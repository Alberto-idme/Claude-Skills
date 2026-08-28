"""Turn each post's raw tracks into decidable fields.

Caption, voice, on-screen text and description are all *evidence*; none of them
is a decision. This pass reads all four together and pulls out the handful of
fields you actually triage on — what it is, where, what you would do with it,
and whether the source said enough to trust.

Structured outputs guarantee the shape, so the report never has to parse prose.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from typing import Iterable

from . import db
from .config import Config

MODEL = "claude-opus-5"

CATEGORIES = [
    "restaurant", "cafe", "bar", "hotel", "sight", "shop", "activity",
    "recipe", "tip", "guide", "product", "other",
]
ACTIONS = ["visit", "book_ahead", "order", "cook", "buy", "read_more", "none"]

# Why an entry is flagged decides whether another pass can ever help.
REVIEW_KINDS = ["none", "fixable", "source_limit"]

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "The specific place, dish or thing. Empty if none is named.",
        },
        "category": {"type": "string", "enum": CATEGORIES},
        "location": {
            "type": "string",
            "description": "City, neighbourhood or region. Empty if not stated.",
        },
        "summary": {"type": "string", "description": "One line: what this is."},
        "highlights": {
            "type": "array",
            "items": {"type": "string"},
            "description": "1-4 specifics worth deciding on: dishes, prices, "
                           "why it stood out.",
        },
        "action": {"type": "string", "enum": ACTIONS},
        "practical": {
            "type": "string",
            "description": "Hours, booking, queue, cost, address fragments. "
                           "Empty if none stated.",
        },
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "needs_review": {
            "type": "boolean",
            "description": "True when the source text was too thin to be sure.",
        },
        "review_reason": {
            "type": "string",
            "description": "When needs_review is true, the specific gap in a "
                           "few words (e.g. 'name legible but no city', "
                           "'lists 8 places, none detailed'). Empty otherwise.",
        },
        "review_kind": {
            "type": "string",
            "enum": REVIEW_KINDS,
            "description": "'fixable' when the detail looks present but came "
                           "through garbled or partial, so a better read could "
                           "recover it. 'source_limit' when the post itself "
                           "never carried it — deliberately unnamed, a bare "
                           "list, audio that is only music. 'none' when not "
                           "flagged.",
        },
    },
    "required": ["title", "category", "location", "summary", "highlights",
                 "action", "practical", "confidence", "needs_review",
                 "review_reason", "review_kind"],
    "additionalProperties": False,
}

SYSTEM = (
    "You turn a saved social post into a triage record. You are given whatever "
    "was recoverable: the caption, a transcript of the speech, text that was "
    "on screen, and a description of the footage. Sources disagree in quality "
    "— on-screen text and captions are usually the most reliable for names and "
    "prices; the description is inferred from stills and is the weakest.\n\n"
    "Extract only what the sources support. Never invent a name, price, "
    "address or opening time; leave the field empty instead. If the post is a "
    "list covering several places, describe the list as a whole and say so in "
    "the summary. Set confidence to low and needs_review to true when the "
    "sources are thin, contradictory, or name nothing specific, and say "
    "which in review_reason so it can be triaged without reopening the post, "
    "and set review_kind to say whether another pass could ever recover it. "
    "Text that arrived garbled or truncated is 'fixable'; detail the post "
    "never contained is 'source_limit' and must not be chased. "
    "Write in "
    "English even when the sources are not, but keep proper names in their "
    "original script with a romanisation in parentheses where you are sure."
)


def _evidence(conn: sqlite3.Connection, shortcode: str) -> tuple[str, dict]:
    """Assemble the tracks into one prompt, and report which existed."""
    data = db.transcript_for(conn, shortcode)
    if not data:
        return "", {}

    post = data["post"]
    parts: list[str] = []
    present = {}

    if post["author_username"]:
        parts.append(f"Account: @{post['author_username']}")
    if post["caption"]:
        parts.append(f"CAPTION:\n{post['caption'].strip()}")
        present["caption"] = True

    voice = " ".join(v["text"] for v in data["voice"] if v["text"]).strip()
    if voice:
        parts.append(f"SPEECH:\n{voice}")
        present["voice"] = True

    lines: list[str] = []
    for entry in data["screen_text"]:
        for item in json.loads(entry["lines_json"] or "[]"):
            lines.append(item["text"])
    # Dedupe again on the way out: rows written before the fuzzy pass existed
    # still carry near-identical reads, and sending 266 lines of the same
    # caption is both wasted tokens and worse extraction.
    from .ocr import dedupe as _dedupe

    lines = _dedupe(lines)
    if lines:
        parts.append("ON-SCREEN TEXT:\n" + "\n".join(lines))
        present["screen_text"] = True

    description = "\n".join(d for d in data["description"] if d).strip()
    if description:
        parts.append(f"FOOTAGE:\n{description}")
        present["description"] = True

    return "\n\n".join(parts), present


def _client(cfg: Config):
    try:
        import anthropic
    except ImportError as exc:
        raise SystemExit(
            "Extraction needs the Anthropic SDK:\n    pip install anthropic"
        ) from exc
    return (anthropic.Anthropic(api_key=cfg.anthropic_key)
            if cfg.anthropic_key else anthropic.Anthropic())


def _params(evidence: str) -> dict:
    return {
        "model": MODEL,
        "max_tokens": 16000,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": evidence}],
        "output_config": {"format": {"type": "json_schema", "schema": SCHEMA}},
    }


def _parse(message) -> dict | None:
    # output_config.format guarantees the text block holds valid JSON.
    text = next((b.text for b in message.content if b.type == "text"), "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def run_all(
    conn: sqlite3.Connection,
    cfg: Config,
    *,
    limit: int | None = None,
    collection: str | None = None,
    batch: bool = False,
    dry_run: bool = False,
    redo: bool = False,
    only_flagged: bool = False,
    force: bool = False,
) -> dict:
    rows = db.pending_entries(conn, collection=collection, redo=redo,
                              only_flagged=only_flagged)
    if limit:
        rows = rows[:limit]
    if not rows:
        return {"extracted": 0, "skipped": 0, "failed": 0, "unchanged": 0}

    # Re-running over evidence that has not moved bills the model to produce
    # the answer already on disk. Only worth it once OCR or transcription has
    # actually improved the input.
    stored = {r["shortcode"]: r["evidence_hash"]
              for r in conn.execute(
                  "SELECT shortcode, evidence_hash FROM entries")}

    prepared: list[tuple[str, str, dict]] = []
    unchanged = 0
    for row in rows:
        evidence, present = _evidence(conn, row["shortcode"])
        if not evidence.strip():
            continue
        digest = hashlib.sha256(evidence.encode("utf-8")).hexdigest()
        if not force and stored.get(row["shortcode"]) == digest:
            unchanged += 1
            continue
        prepared.append((row["shortcode"], evidence, present, digest))

    if unchanged:
        print(f"  {unchanged} unchanged since last extract — skipping "
              f"(--force to re-run anyway)", file=sys.stderr)

    if dry_run:
        chars = sum(len(e) for _c, e, _p, _h in prepared)
        tokens = chars // 3 + 400 * len(prepared)
        cost = (tokens * 5 + 300 * len(prepared) * 25) / 1_000_000
        print(f"  {len(prepared)} posts, ~{tokens:,} input tokens", file=sys.stderr)
        print(f"  estimated ~${cost:.2f}"
              f"{'' if batch else f' (~${cost / 2:.2f} with --batch)'}",
              file=sys.stderr)
        return {"extracted": 0, "skipped": len(rows), "failed": 0,
                "unchanged": unchanged}

    if not prepared:
        return {"extracted": 0, "skipped": len(rows), "failed": 0,
                "unchanged": unchanged}

    client = _client(cfg)
    print(f"  {MODEL}: {len(prepared)} posts", file=sys.stderr)
    counts = (_run_batch(conn, client, prepared) if batch
              else _run_serial(conn, client, prepared))
    counts["unchanged"] = unchanged
    return counts


def _record(conn, shortcode: str, parsed: dict, present: dict,
            digest: str = "") -> None:
    db.save_entry(
        conn, shortcode=shortcode, model=MODEL, evidence_hash=digest,
        sources=sorted(present), **parsed,
    )


def _run_serial(conn, client, prepared: Iterable[tuple]) -> dict:
    prepared = list(prepared)
    counts = {"extracted": 0, "skipped": 0, "failed": 0}

    for n, (shortcode, evidence, present, digest) in enumerate(prepared, 1):
        try:
            message = client.messages.create(**_params(evidence))
        except Exception as exc:  # noqa: BLE001 - keep going through the archive
            print(f"  [{n}/{len(prepared)}] {shortcode}: {exc}", file=sys.stderr)
            counts["failed"] += 1
            continue

        parsed = _parse(message)
        if parsed is None:
            counts["failed"] += 1
            continue

        _record(conn, shortcode, parsed, present, digest)
        counts["extracted"] += 1
        print(f"  [{n}/{len(prepared)}] {shortcode}: {parsed['category']} — "
              f"{parsed['title'] or parsed['summary'][:40]}", file=sys.stderr)

    return counts


def _run_batch(conn, client, prepared: Iterable[tuple]) -> dict:
    import time

    from anthropic.types.message_create_params import (
        MessageCreateParamsNonStreaming,
    )
    from anthropic.types.messages.batch_create_params import Request

    prepared = list(prepared)
    by_id = {f"p{i}": item for i, item in enumerate(prepared)}
    requests = [
        Request(custom_id=key,
                params=MessageCreateParamsNonStreaming(**_params(item[1])))
        for key, item in by_id.items()
    ]

    batch = client.messages.batches.create(requests=requests)
    print(f"  batch {batch.id} submitted ({len(requests)} posts)", file=sys.stderr)

    while True:
        current = client.messages.batches.retrieve(batch.id)
        if current.processing_status == "ended":
            break
        print(f"  {current.processing_status}: "
              f"{current.request_counts.processing} processing", file=sys.stderr)
        time.sleep(60)

    counts = {"extracted": 0, "skipped": 0, "failed": 0}
    for result in client.messages.batches.results(batch.id):
        item = by_id.get(result.custom_id)
        if item is None or result.result.type != "succeeded":
            counts["failed"] += 1
            continue
        parsed = _parse(result.result.message)
        if parsed is None:
            counts["failed"] += 1
            continue
        _record(conn, item[0], parsed, item[2], item[3])
        counts["extracted"] += 1

    return counts

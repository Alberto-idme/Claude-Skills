"""Describe what a reel actually shows, using Claude vision over keyframes.

Voice and on-screen text only cover what is said or written. A reel of a
counter-service ramen bar with a queue outside says none of that out loud, so
without a visual pass the archive cannot answer "the place with the wooden
facade and the vending machine".

A handful of keyframes is sent per video rather than a dense sample — the extra
frames mostly repeat the same shot and cost ~$0.004 each. Bulk runs go through
the Batch API at half price.
"""

from __future__ import annotations

import base64
import sqlite3
import sys
from pathlib import Path

from . import db, frames as frames_mod
from .config import Config

MODEL = "claude-opus-5"

SYSTEM = (
    "You describe frames sampled from a short social video so they can be "
    "searched later. Write 2-4 sentences of plain prose covering: the setting "
    "and what kind of place it is, what is happening, and any distinctive "
    "visual detail someone might search for later (signage, dishes, "
    "landmarks, storefronts). Name places or dishes only when they are legible "
    "or unmistakable — never guess a name. Describe only what is visible; "
    "there is no audio, so do not mention music, narration or sound. Do not "
    "preface the description or mention frames, images or the video itself."
)

PROMPT = "Describe this video from these {n} frames, in order."


def _blocks(path: Path, count: int) -> list[dict]:
    """Frames as image content blocks, oldest first."""
    picked = frames_mod.keyframes(path, count=count)
    blocks: list[dict] = []
    for _when, frame in picked:
        blocks.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64.standard_b64encode(
                        frames_mod.to_jpeg(frame)
                    ).decode("utf-8"),
                },
            }
        )
    return blocks


def _client(cfg: Config):
    try:
        import anthropic
    except ImportError as exc:
        raise SystemExit(
            "Describing video needs the Anthropic SDK:\n"
            "    pip install anthropic\n"
            "and credentials: export ANTHROPIC_API_KEY=... (or run `ant auth login`)"
        ) from exc
    # A zero-arg client also picks up an `ant auth login` profile, so an unset
    # ANTHROPIC_API_KEY is not necessarily an error.
    return anthropic.Anthropic() if not cfg.anthropic_key else anthropic.Anthropic(
        api_key=cfg.anthropic_key
    )


def _text_of(message) -> str:
    return "\n".join(b.text for b in message.content if b.type == "text").strip()


def run_all(
    conn: sqlite3.Connection,
    cfg: Config,
    *,
    limit: int | None = None,
    collection: str | None = None,
    frames_per_video: int = 4,
    batch: bool = False,
    dry_run: bool = False,
) -> dict:
    rows = db.pending_descriptions(conn, collection=collection)
    if limit:
        rows = rows[:limit]
    if not rows:
        return {"described": 0, "skipped": 0, "failed": 0}

    if dry_run:
        # Vision cost scales with pixels; keyframes are capped at 768px, which
        # lands around 600 tokens each.
        per_video = frames_per_video * 600 + 200
        cost = len(rows) * (per_video * 5 + 200 * 25) / 1_000_000
        print(f"  {len(rows)} videos x {frames_per_video} frames -> "
              f"~{per_video * len(rows):,} input tokens", file=sys.stderr)
        print(f"  estimated ~${cost:.2f}"
              f"{f' (~${cost / 2:.2f} with --batch)' if not batch else ''}",
              file=sys.stderr)
        return {"described": 0, "skipped": len(rows), "failed": 0}

    client = _client(cfg)
    print(f"  {MODEL}: {len(rows)} videos", file=sys.stderr)

    if batch:
        return _run_batch(conn, client, rows, frames_per_video)
    return _run_serial(conn, client, rows, frames_per_video)


def _request_content(path: Path, frames_per_video: int) -> list[dict] | None:
    blocks = _blocks(path, frames_per_video)
    if not blocks:
        return None
    return blocks + [{"type": "text", "text": PROMPT.format(n=len(blocks))}]


def _run_serial(conn, client, rows, frames_per_video: int) -> dict:
    counts = {"described": 0, "skipped": 0, "failed": 0}

    for n, row in enumerate(rows, 1):
        path = Path(row["local_path"])
        if not path.exists():
            counts["skipped"] += 1
            continue

        try:
            content = _request_content(path, frames_per_video)
            if not content:
                db.save_description(conn, media_id=row["id"],
                                    shortcode=row["shortcode"], text="",
                                    model=MODEL, frames=0, status="no_frames")
                counts["skipped"] += 1
                continue

            message = client.messages.create(
                model=MODEL,
                max_tokens=16000,
                system=SYSTEM,
                messages=[{"role": "user", "content": content}],
            )
        except Exception as exc:  # noqa: BLE001 - keep going through the archive
            print(f"  [{n}/{len(rows)}] {row['shortcode']}: {exc}", file=sys.stderr)
            counts["failed"] += 1
            continue

        text = _text_of(message)
        db.save_description(
            conn, media_id=row["id"], shortcode=row["shortcode"], text=text,
            model=MODEL, frames=frames_per_video,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
            status="ok" if text else "empty",
        )
        counts["described"] += 1
        print(f"  [{n}/{len(rows)}] {row['shortcode']}: {len(text)} chars",
              file=sys.stderr)

    return counts


def _run_batch(conn, client, rows, frames_per_video: int) -> dict:
    """Half price, but asynchronous — usually under an hour, up to 24."""
    import time

    from anthropic.types.message_create_params import (
        MessageCreateParamsNonStreaming,
    )
    from anthropic.types.messages.batch_create_params import Request

    counts = {"described": 0, "skipped": 0, "failed": 0}
    by_id: dict[str, sqlite3.Row] = {}
    requests = []

    for row in rows:
        path = Path(row["local_path"])
        if not path.exists():
            counts["skipped"] += 1
            continue
        content = _request_content(path, frames_per_video)
        if not content:
            counts["skipped"] += 1
            continue
        custom_id = f"m{row['id']}"
        by_id[custom_id] = row
        requests.append(
            Request(
                custom_id=custom_id,
                params=MessageCreateParamsNonStreaming(
                    model=MODEL, max_tokens=16000, system=SYSTEM,
                    messages=[{"role": "user", "content": content}],
                ),
            )
        )

    if not requests:
        return counts

    batch = client.messages.batches.create(requests=requests)
    print(f"  batch {batch.id} submitted ({len(requests)} videos); "
          "usually under an hour", file=sys.stderr)

    while True:
        current = client.messages.batches.retrieve(batch.id)
        if current.processing_status == "ended":
            break
        print(f"  {current.processing_status}: "
              f"{current.request_counts.processing} processing", file=sys.stderr)
        time.sleep(60)

    # Results come back in any order — key by custom_id, never by position.
    for result in client.messages.batches.results(batch.id):
        row = by_id.get(result.custom_id)
        if row is None:
            continue
        if result.result.type != "succeeded":
            counts["failed"] += 1
            continue
        message = result.result.message
        text = _text_of(message)
        db.save_description(
            conn, media_id=row["id"], shortcode=row["shortcode"], text=text,
            model=MODEL, frames=frames_per_video,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
            status="ok" if text else "empty",
        )
        counts["described"] += 1

    return counts

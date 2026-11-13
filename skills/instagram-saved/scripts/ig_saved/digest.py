"""Compile a whole collection into one decision document.

`report` renders rows: one card per post, faithful to each. That is the right
shape for "which of these do I act on", and the wrong shape for "what do I
actually have to do". Forty posts about app security are forty opinions with
heavy overlap; what you need before a launch is one deduplicated, ordered
checklist.

So this is a synthesis pass, not a rendering pass. It reads every entry in the
collection at once and writes a single document.

Two rules keep it honest, both inherited from extraction:

* **Every item cites the posts it came from.** The shortcodes are checked in
  code against the posts that were actually sent — an item citing anything
  else is dropped, not displayed. A checklist that quietly mixes in the
  model's own training is a different document from the one that was asked
  for, and there would be no way to tell which item is which.
* **What the collection does not cover is stated.** A checklist assembled from
  whatever happened to be bookmarked has holes, and presenting it as complete
  is the failure mode that matters when the subject is security.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

from . import db
from .config import Config
from .extract import MODEL, _client

PRIORITIES = ["must", "should", "consider"]

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "overview": {
            "type": "string",
            "description": "2-4 sentences: what this collection covers and "
                           "how to use the checklist.",
        },
        "sections": {
            "type": "array",
            "description": "Themed groups, ordered most urgent first.",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "check": {
                                    "type": "string",
                                    "description": "The action, imperative and "
                                                   "specific enough to do.",
                                },
                                "why": {
                                    "type": "string",
                                    "description": "What goes wrong without it.",
                                },
                                "detail": {
                                    "type": "string",
                                    "description": "Concrete specifics the posts "
                                                   "gave: tools, headers, settings, "
                                                   "versions. Empty if none.",
                                },
                                "priority": {"type": "string", "enum": PRIORITIES},
                                "sources": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Shortcodes of the posts this "
                                                   "comes from. At least one, "
                                                   "copied exactly.",
                                },
                            },
                            "required": ["check", "why", "detail", "priority",
                                         "sources"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["heading", "items"],
                "additionalProperties": False,
            },
        },
        "gaps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Topics a reader would reasonably expect in a "
                           "document with this goal that these posts do not "
                           "cover. Name them plainly.",
        },
    },
    "required": ["title", "overview", "sections", "gaps"],
    "additionalProperties": False,
}

SYSTEM = (
    "You are compiling a set of saved social-media posts into one practical "
    "document for the goal the user states. "
    "Consolidate: the posts overlap heavily, and the same advice phrased three "
    "ways is one item, not three — cite all the posts it came from. "
    "Order by what matters most for the stated goal, not by how often it was "
    "mentioned. "
    "Build every item from what the posts actually say. Do not add items from "
    "your own knowledge, however standard or important they seem, and do not "
    "quietly broaden a specific claim into a general one. "
    "Instead, list what a reader would expect for this goal and these posts do "
    "not cover under `gaps` — being told the set is incomplete is far more "
    "useful than a checklist that looks complete and is not. "
    "Keep the specifics: tool names, header names, settings, versions, "
    "commands. A checklist item with the specifics stripped out is not "
    "actionable. "
    "Every item must cite at least one shortcode, copied exactly from the "
    "input."
)


def _corpus(conn: sqlite3.Connection, collection: str | None) -> list[dict]:
    """The entries, as the compact evidence the synthesis reads."""
    out = []
    for row in db.entries(conn, collection=collection):
        record = dict(row)
        caption = (record.get("caption") or "")
        out.append({
            "shortcode": record["shortcode"],
            "title": record.get("title") or "",
            "category": record.get("category") or "",
            "summary": record.get("summary") or "",
            "highlights": json.loads(record.get("highlights") or "[]"),
            "practical": record.get("practical") or "",
            "author": record.get("author_username") or "",
            "caption": caption[:1500],
        })
    return out


def _render(data: dict, corpus: list[dict], scope: str) -> tuple[str, int, int]:
    """Markdown, plus how many items were kept and how many dropped.

    An item citing a shortcode that was not in the input is dropped here rather
    than rendered. The whole value of the citations is that they can be
    checked, so an uncheckable one makes the item worth less than nothing.
    """
    known = {c["shortcode"] for c in corpus}
    urls = {c["shortcode"]: f"https://www.instagram.com/p/{c['shortcode']}/"
            for c in corpus}

    kept = dropped = 0
    lines = [f"# {data.get('title') or scope}", ""]
    if data.get("overview"):
        lines += [data["overview"].strip(), ""]

    counts: dict[str, int] = {}
    body: list[str] = []
    for section in data.get("sections") or []:
        items = [i for i in (section.get("items") or [])
                 if set(i.get("sources") or []) & known]
        dropped += len(section.get("items") or []) - len(items)
        if not items:
            continue
        body += [f"## {section.get('heading') or 'Other'}", ""]
        order = {p: n for n, p in enumerate(PRIORITIES)}
        for item in sorted(items, key=lambda i: order.get(i.get("priority"), 9)):
            kept += 1
            pri = item.get("priority") or "consider"
            counts[pri] = counts.get(pri, 0) + 1
            mark = {"must": "**MUST**", "should": "**Should**"}.get(pri, "Consider")
            body += [f"- [ ] {mark} — {item['check'].strip()}"]
            if item.get("why"):
                body.append(f"  - _Why:_ {item['why'].strip()}")
            if item.get("detail"):
                body.append(f"  - _Detail:_ {item['detail'].strip()}")
            cites = " · ".join(
                f"[{code}]({urls[code]})"
                for code in item.get("sources") or [] if code in known)
            body.append(f"  - _From:_ {cites}")
        body.append("")

    tally = " · ".join(f"**{counts[p]}** {p}" for p in PRIORITIES if counts.get(p))
    lines += [f"{kept} checks from {len(corpus)} saved posts"
              + (f" — {tally}" if tally else ""), "",
              f"_Compiled {date.today().isoformat()} from the "
              f"`{scope}` collection._", ""]
    lines += body

    if data.get("gaps"):
        lines += ["## Not covered by these posts", "",
                  "Assembled from what you bookmarked, so it is only as "
                  "complete as the collection. Expect to source these "
                  "elsewhere:", ""]
        lines += [f"- {g.strip()}" for g in data["gaps"]]
        lines.append("")

    lines += ["---", "",
              "Every check above traces to a post you saved; the links go "
              "straight to it. Nothing here was added from outside the "
              "collection."]
    if dropped:
        lines += ["", f"_{dropped} item(s) were dropped for citing posts that "
                      f"were not in the input._"]
    return "\n".join(lines), kept, dropped


def prepare_out(out: Path) -> Path:
    """Make the output directory, but only the last component of it.

    `mkdir(parents=True)` on a path like
    `/Users/<typo>/Desktop/AC Personal/app-security.md` happily builds the
    whole tree and reports success, leaving the document in a home directory
    that does not belong to anyone. Creating the final folder is helpful;
    inventing the path above it hides a typo instead of surfacing it.
    """
    parent = out.parent
    if parent.exists():
        return out
    if not parent.parent.exists():
        raise SystemExit(
            f"{parent.parent} does not exist, so {parent} looks like a typo "
            f"rather than a folder to create.\nCheck the path and pass --out "
            f"again; nothing was written."
        )
    parent.mkdir()
    print(f"Created {parent}", file=sys.stderr)
    return out


def run(
    conn: sqlite3.Connection, cfg: Config, out: Path, *,
    collection: str | None = None, goal: str = "", limit: int | None = None,
    dry_run: bool = False,
) -> dict:
    # Before the API call, not after: an unwritable destination should
    # cost nothing to discover.
    if not dry_run:
        out = prepare_out(out)

    corpus = _corpus(conn, collection)
    if limit:
        corpus = corpus[:limit]
    scope = collection or "all collections"

    if not corpus:
        print(f"No entries for '{scope}' — run `extract` first.", file=sys.stderr)
        return {"items": 0, "posts": 0}

    goal = goal.strip() or ("A practical, deduplicated checklist of what to do, "
                            "compiled from these posts.")
    payload = json.dumps(corpus, ensure_ascii=False, indent=1)
    tokens = len(payload) // 3

    if dry_run:
        print(f"{len(corpus)} entries, ~{tokens:,} input tokens.")
        print(f"One synthesis call, roughly ${tokens * 5 / 1_000_000 + 0.08:.2f}.")
        return {"items": 0, "posts": len(corpus)}

    # Opus 5 holds 1M tokens; well before that the synthesis gets worse, not
    # just dearer. Say so rather than silently sending a truncated corpus.
    if tokens > 400_000:
        print(f"{len(corpus)} entries is ~{tokens:,} tokens, too much to "
              f"synthesise well in one pass.\nNarrow it with --collection or "
              f"--limit.", file=sys.stderr)
        return {"items": 0, "posts": len(corpus)}

    print(f"Compiling {len(corpus)} entries…", file=sys.stderr)
    client = _client(cfg)
    message = client.messages.create(
        model=MODEL,
        max_tokens=32000,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"GOAL:\n{goal}\n\nSAVED POSTS (JSON):\n{payload}",
        }],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    text = next((b.text for b in message.content if b.type == "text"), "")
    data = json.loads(text)

    markdown, kept, dropped = _render(data, corpus, scope)
    out.write_text(markdown, encoding="utf-8")

    print(f"{kept} checks from {len(corpus)} posts -> {out}")
    if dropped:
        print(f"  {dropped} dropped for citing a post that was not in the input.")
    if data.get("gaps"):
        print(f"  {len(data['gaps'])} gap(s) the collection does not cover.")
    return {"items": kept, "posts": len(corpus), "dropped": dropped,
            "gaps": len(data.get("gaps") or [])}

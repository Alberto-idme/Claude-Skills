"""Pull the named places out of each post, then look each one up on the web.

Two stages, deliberately separate.

`extract_all` reads the evidence already on disk and lists every place the post
names — one row each. `entries` has room for exactly one title, which is why a
listicle reel naming eight restaurants came back flagged "one line each, no
addresses": there was nowhere to put the other seven. There is now.

`enrich_all` takes those names to the web for an address and a website. It is a
separate pass because it is the only stage that is billed per search
($10/1,000), and because a lookup that fails should never cost the extracted
name — the row keeps the name and records why the lookup came back empty.

The standing rule that extraction must never invent a name, price or address
gets teeth here: the model reports the page it read the address off, and that
URL is checked against the URLs web search actually returned before the row is
marked verified. A cited page that was never fetched is a fabricated citation,
and an address carrying one is worth less than no address at all.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
import urllib.parse
from typing import Any

from . import db, parallel
from .config import Config
from .extract import MODEL, _client, _evidence

# Anthropic's newest web search variant. `response_inclusion: "excluded"` drops
# the raw search blocks from the response once they have been consumed, which
# is exactly right here: the JSON is the deliverable, the search text is not.
SEARCH_TOOL = {
    "type": "web_search_20260318",
    "name": "web_search",
    "max_uses": 3,
    "response_inclusion": "excluded",
}

KINDS = ["restaurant", "cafe", "bar", "hotel", "sight", "shop", "activity",
         "market", "other"]

NAMES_SCHEMA = {
    "type": "object",
    "properties": {
        "places": {
            "type": "array",
            "description": "Every named place, business, venue or attraction "
                           "the post mentions. Empty if it names none.",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name exactly as the post gives it, "
                                       "in its original script.",
                    },
                    "kind": {"type": "string", "enum": KINDS},
                    "locality": {
                        "type": "string",
                        "description": "City, neighbourhood or area the post "
                                       "places it in. Empty if not stated.",
                    },
                },
                "required": ["name", "kind", "locality"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["places"],
    "additionalProperties": False,
}

NAMES_SYSTEM = (
    "List every place, business, venue or attraction named in this Instagram "
    "post. A single post often names several — a list of restaurants is one "
    "row per restaurant, not one row for the list. "
    "Take names only from what the sources actually say. Never invent a name, "
    "never complete a partial one from your own knowledge, and never add a "
    "place the post does not mention. On-screen text arrives from OCR and can "
    "be garbled; if a name is too damaged to be sure of, leave it out rather "
    "than guessing at it. "
    "Keep proper names in their original script. Do not include generic nouns "
    "('a ramen shop'), dishes, neighbourhoods on their own, or the account "
    "posting it — only named places."
)

LOOKUP_SCHEMA = {
    "type": "object",
    "properties": {
        "found": {
            "type": "boolean",
            "description": "True only if you found this specific place.",
        },
        "address": {
            "type": "string",
            "description": "Full street address as published. Empty if not found.",
        },
        "website": {
            "type": "string",
            "description": "Official website. Empty if it has none or you are "
                           "not sure it is the right business.",
        },
        "phone": {"type": "string", "description": "Empty if not published."},
        "source_url": {
            "type": "string",
            "description": "The URL of the page you read the address off. Must "
                           "be a page returned by your search, copied exactly.",
        },
        "note": {
            "type": "string",
            "description": "If not found, or if you are unsure this is the "
                           "right place, say why in one line.",
        },
    },
    "required": ["found", "address", "website", "phone", "source_url", "note"],
    "additionalProperties": False,
}

LOOKUP_SYSTEM = (
    "You are looking up one specific place to find its street address and "
    "official website. Search the web, then report only what the pages you "
    "found actually say. "
    "Report the address exactly as published, including the country. "
    "If searching does not turn up this specific place, or the results are for "
    "a different business with a similar name, or you cannot tell which of "
    "several branches is meant, set found to false and say which in note. "
    "An empty field is correct and useful; a plausible invented address is not. "
    "Never construct an address, phone number or URL from your own knowledge, "
    "from the name, or by pattern — every value must come from a page you "
    "actually retrieved in this search. "
    "Put the URL of the page you took the address from in source_url, copied "
    "exactly from the search results."
)


def maps_link(name: str, address: str = "") -> str:
    """A Google Maps search URL, built locally rather than asked for.

    Maps URLs follow a documented format, so generating one is deterministic and
    cannot be hallucinated — unlike asking the model to recall a place's canonical
    Maps link, which is exactly the kind of thing that comes back plausible and
    wrong.
    """
    query = ", ".join(p for p in (name, address) if p)
    if not query:
        return ""
    return ("https://www.google.com/maps/search/?api=1&query="
            + urllib.parse.quote(query))


def _text_of(message) -> str:
    return next((b.text for b in message.content if b.type == "text"), "")


def _searched_urls(message) -> set[str]:
    """Every URL web search actually returned in this response.

    Server-tool errors arrive as HTTP 200 with `content` as a single error
    object rather than a list of results, so this has to check the shape before
    iterating — indexing an error object silently yields nothing and would make
    a failed search look like a search that found no pages.
    """
    urls: set[str] = set()
    for block in message.content:
        if getattr(block, "type", "") != "web_search_tool_result":
            continue
        content = getattr(block, "content", None)
        if not isinstance(content, list):
            continue  # an error object, not results
        for result in content:
            url = getattr(result, "url", None)
            if url:
                urls.add(url)
    return urls


def _search_error(message) -> str:
    for block in message.content:
        if getattr(block, "type", "") != "web_search_tool_result":
            continue
        content = getattr(block, "content", None)
        if not isinstance(content, list):
            return str(getattr(content, "error_code", "") or "search_failed")
    return ""


def _searches_used(message) -> int:
    server = getattr(message.usage, "server_tool_use", None)
    return int(getattr(server, "web_search_requests", 0) or 0) if server else 0


def _same_host(a: str, b: str) -> bool:
    def host(url: str) -> str:
        try:
            return urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
        except ValueError:
            return ""
    return bool(host(a)) and host(a) == host(b)


def _verify(source_url: str, searched: set[str]) -> bool:
    """Did the cited page actually come back from the search?

    Exact match first, then same-host: the model often cites the canonical page
    of a site whose listing page was what search returned, which is honest.
    A citation matching neither is one it made up.
    """
    if not source_url or not searched:
        return False
    if source_url in searched:
        return True
    return any(_same_host(source_url, url) for url in searched)


# ---------------------------------------------------------------------------
# Stage 1: which places does each post name?
# ---------------------------------------------------------------------------


def extract_all(
    conn: sqlite3.Connection, cfg: Config, *, limit: int | None = None,
    collection: str | None = None, redo: bool = False, dry_run: bool = False,
    shortcodes: list[str] | None = None, workers: int | None = None,
) -> dict:
    rows = db.pending_place_extraction(conn, collection=collection, redo=redo,
                                       shortcodes=shortcodes)
    if limit:
        rows = rows[:limit]
    if not rows:
        print("No posts waiting for place extraction.")
        return {"posts": 0, "places": 0, "failed": 0}

    if dry_run:
        print(f"{len(rows)} posts to read for place names.")
        print(f"Roughly ${0.014 * len(rows):.2f} at Opus 5 rates, no searches.")
        return {"posts": len(rows), "places": 0, "failed": 0}

    client = _client(cfg)
    found = failed = 0
    workers = workers or parallel.DEFAULT_WORKERS

    def call(row):
        shortcode = row["shortcode"]
        evidence, _present = _evidence(conn, shortcode)
        if not evidence.strip():
            return None
        message = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=NAMES_SYSTEM,
            messages=[{"role": "user", "content": evidence}],
            output_config={
                "format": {"type": "json_schema", "schema": NAMES_SCHEMA}
            },
        )
        return json.loads(_text_of(message))

    done = 0
    # Reading the evidence happens inside the worker too. It is a handful of
    # local SELECTs against a WAL database, which readers may do concurrently.
    for row, data, error in parallel.imap(call, rows, workers=workers):
        done += 1
        if error is not None:
            print(f"  {row['shortcode']}: {error}", file=sys.stderr)
            failed += 1
            continue
        if data is None:
            continue
        added = db.save_places(conn, row["shortcode"], data.get("places") or [],
                               MODEL)
        found += added
        parallel.progress(done, len(rows), "posts read")

    print(f"Found {found} places across {len(rows)} posts ({failed} failed).")
    return {"posts": len(rows), "places": found, "failed": failed}


# ---------------------------------------------------------------------------
# Stage 2: address and website for each place
# ---------------------------------------------------------------------------


def _norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).casefold()


def _compatible(a: str | None, b: str | None) -> bool:
    """Could these two localities be describing the same spot?

    Posts word the same place differently — "Shibuya", "Shibuya, Tokyo",
    "Tokyo" — so an exact match would miss most real duplicates. Sharing any
    comma-separated component is enough, and an unstated locality is compatible
    with anything.
    """
    x, y = _norm(a), _norm(b)
    if not x or not y or x == y:
        return True
    return bool({p.strip() for p in x.split(",") if p.strip()}
                & {p.strip() for p in y.split(",") if p.strip()})


def group_for_lookup(rows: list) -> list[list]:
    """Collapse rows that name the same place into one lookup each.

    A venue three accounts recommended is three rows — one per post — and each
    was being looked up separately, at up to `max_uses` billed searches apiece.

    Rows merge only when the name matches and every locality in the group is
    compatible with every other. A chain with branches in two cities keeps its
    rows apart: paying twice is much cheaper than writing the Shibuya address
    onto the Fukuoka row.
    """
    by_name: dict[str, list] = {}
    for row in rows:
        by_name.setdefault(_norm(row["name"]), []).append(row)

    groups: list[list] = []
    for named in by_name.values():
        localities = [r["locality"] or r["entry_location"] for r in named]
        if all(_compatible(a, b)
               for i, a in enumerate(localities) for b in localities[i + 1:]):
            groups.append(named)
        else:
            # Ambiguous: same name, localities that cannot both be right.
            groups.extend([row] for row in named)
    return groups


def _richest(group: list):
    """The row to actually search with — the one naming the most specific place."""
    return max(group, key=lambda r: len(r["locality"] or r["entry_location"] or ""))


def _query_for(row) -> str:
    """What to tell the model to look up.

    The locality matters more than it looks: "Fuglen" alone finds the Oslo
    original, not the Tokyo branch the post was about.
    """
    where = row["locality"] or row["entry_location"] or ""
    parts = [f"Name: {row['name']}"]
    if row["kind"]:
        parts.append(f"Type: {row['kind']}")
    if where:
        parts.append(f"The post places it in: {where}")
    parts.append("Find this place's street address and official website.")
    return "\n".join(parts)


def enrich_all(
    conn: sqlite3.Connection, cfg: Config, *, limit: int | None = None,
    collection: str | None = None, redo: bool = False,
    retry_failed: bool = False, dry_run: bool = False,
    max_searches: int | None = None, shortcodes: list[str] | None = None,
    workers: int | None = None,
) -> dict:
    rows = db.pending_enrichment(conn, collection=collection, redo=redo,
                                 retry_failed=retry_failed, shortcodes=shortcodes)
    if limit:
        rows = rows[:limit]
    if not rows:
        print("Every place already has a lookup.")
        return {"looked_up": 0, "found": 0, "unverified": 0, "failed": 0,
                "searches": 0, "saved_by_dedupe": 0}

    groups = group_for_lookup(rows)
    saved = len(rows) - len(groups)

    if dry_run:
        low = 0.03 * len(groups)
        high = (0.01 * SEARCH_TOOL["max_uses"] + 0.02) * len(groups)
        print(f"{len(rows)} places to look up, {len(groups)} lookups needed"
              + (f" ({saved} are repeats of a place in another post)."
                 if saved else "."))
        print(f"Roughly ${low:.2f}-${high:.2f}: $0.01 per search "
              f"(up to {SEARCH_TOOL['max_uses']} each) plus tokens.")
        if saved:
            print(f"Deduping avoids about ${0.03 * saved:.2f}.")
        return {"looked_up": len(rows), "found": 0, "unverified": 0,
                "failed": 0, "searches": 0, "saved_by_dedupe": saved}

    if saved:
        print(f"{len(rows)} places, {len(groups)} distinct — {saved} are the "
              f"same venue named in more than one post.", file=sys.stderr)

    client = _client(cfg)
    workers = workers or parallel.DEFAULT_WORKERS
    found = unverified = failed = searches = 0
    stopped_early = False

    def call(group):
        return client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=LOOKUP_SYSTEM,
            messages=[{"role": "user", "content": _query_for(_richest(group))}],
            tools=[SEARCH_TOOL],
            output_config={
                "format": {"type": "json_schema", "schema": LOOKUP_SCHEMA}
            },
        )

    def within_budget() -> bool:
        # Checked before each submission, never after: a request already sent
        # is already billed. With `workers` in flight the cap can overshoot by
        # up to that many lookups, which is reported rather than hidden.
        nonlocal stopped_early
        if max_searches is not None and searches >= max_searches:
            stopped_early = True
            return False
        return True

    def write(group, **fields):
        """Apply one lookup to every row that named the same place.

        Only the row actually searched carries the search count; the others
        cost nothing, and claiming otherwise would inflate the run total.
        """
        for i, row in enumerate(group):
            db.save_enrichment(conn, row["id"], model=MODEL,
                               searches=fields.pop("searches", 0) if i == 0
                               else 0,
                               **fields)

    done = 0
    for group, message, error in parallel.imap(call, groups, workers=workers,
                                               keep_going=within_budget):
        done += 1
        name = group[0]["name"]
        shared = f" (+{len(group) - 1} more post(s))" if len(group) > 1 else ""

        if error is not None:
            print(f"  {name}: {error}", file=sys.stderr)
            for row in group:
                db.save_enrichment(conn, row["id"], status="error",
                                   note=str(error)[:200], model=MODEL)
            failed += len(group)
            continue

        used = _searches_used(message)
        searches += used

        search_error = _search_error(message)
        if search_error:
            print(f"  {name}: search error ({search_error})", file=sys.stderr)
            for i, row in enumerate(group):
                db.save_enrichment(conn, row["id"], status="error",
                                   note=f"web search: {search_error}",
                                   searches=used if i == 0 else 0, model=MODEL)
            failed += len(group)
            continue

        try:
            data: dict[str, Any] = json.loads(_text_of(message))
        except json.JSONDecodeError:
            for i, row in enumerate(group):
                db.save_enrichment(conn, row["id"], status="error",
                                   note="unparseable response",
                                   searches=used if i == 0 else 0, model=MODEL)
            failed += len(group)
            continue

        address = (data.get("address") or "").strip()
        source_url = (data.get("source_url") or "").strip()
        verified = _verify(source_url, _searched_urls(message))

        if not data.get("found") or not address:
            for i, row in enumerate(group):
                db.save_enrichment(conn, row["id"], status="not_found",
                                   note=(data.get("note") or "").strip(),
                                   website=(data.get("website") or "").strip(),
                                   searches=used if i == 0 else 0, model=MODEL)
            print(f"  {name}: not found{shared}", file=sys.stderr)
            continue

        if not verified:
            unverified += len(group)
        found += len(group)
        for i, row in enumerate(group):
            db.save_enrichment(
                conn, row["id"], address=address,
                website=(data.get("website") or "").strip(),
                # Built from each row's own name, so a row spelling the place
                # differently still gets a map link that matches its label.
                maps_url=maps_link(row["name"], address),
                phone=(data.get("phone") or "").strip(),
                source_url=source_url, verified=verified, status="ok",
                note=(data.get("note") or "").strip(),
                searches=used if i == 0 else 0, model=MODEL,
            )
        mark = "" if verified else "  (unverified citation)"
        print(f"  {name}: {address}{mark}{shared}", file=sys.stderr)
        parallel.progress(done, len(groups), "lookups")

    if stopped_early:
        print(f"Stopped at --max-searches {max_searches}; "
              f"{len(groups) - done} lookup(s) left for next time.",
              file=sys.stderr)

    print(f"Looked up {found + failed} places in {done} lookup(s): "
          f"{found} with an address "
          f"({unverified} whose citation could not be verified), {failed} failed.")
    print(f"{searches} searches, about ${0.01 * searches:.2f} plus tokens"
          + (f"; deduping saved about {saved} lookup(s)." if saved else "."))
    return {"looked_up": found + failed, "found": found,
            "unverified": unverified, "failed": failed, "searches": searches,
            "saved_by_dedupe": saved, "stopped_early": stopped_early}

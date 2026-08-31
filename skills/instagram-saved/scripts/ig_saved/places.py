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
import sqlite3
import sys
import urllib.parse
from typing import Any

from . import db
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
) -> dict:
    rows = db.pending_place_extraction(conn, collection=collection, redo=redo)
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

    for n, row in enumerate(rows, 1):
        shortcode = row["shortcode"]
        evidence, _present = _evidence(conn, shortcode)
        if not evidence.strip():
            continue
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=8000,
                system=NAMES_SYSTEM,
                messages=[{"role": "user", "content": evidence}],
                output_config={
                    "format": {"type": "json_schema", "schema": NAMES_SCHEMA}
                },
            )
            data = json.loads(_text_of(message))
        except Exception as exc:  # noqa: BLE001
            print(f"[{n}/{len(rows)}] {shortcode}: {exc}", file=sys.stderr)
            failed += 1
            continue

        places = data.get("places") or []
        added = db.save_places(conn, shortcode, places, MODEL)
        found += added
        print(f"[{n}/{len(rows)}] {shortcode}: {added} place(s)", file=sys.stderr)

    print(f"Found {found} places across {len(rows)} posts ({failed} failed).")
    return {"posts": len(rows), "places": found, "failed": failed}


# ---------------------------------------------------------------------------
# Stage 2: address and website for each place
# ---------------------------------------------------------------------------


def _query_for(row: sqlite3.Row) -> str:
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
    max_searches: int | None = None,
) -> dict:
    rows = db.pending_enrichment(conn, collection=collection, redo=redo,
                                 retry_failed=retry_failed)
    if limit:
        rows = rows[:limit]
    if not rows:
        print("Every place already has a lookup.")
        return {"looked_up": 0, "found": 0, "unverified": 0, "failed": 0,
                "searches": 0}

    if dry_run:
        # Each lookup is one request that may run up to max_uses searches.
        low = 0.01 * len(rows) + 0.02 * len(rows)
        high = 0.01 * SEARCH_TOOL["max_uses"] * len(rows) + 0.02 * len(rows)
        print(f"{len(rows)} places to look up.")
        print(f"Roughly ${low:.2f}-${high:.2f}: $0.01 per search "
              f"(up to {SEARCH_TOOL['max_uses']} each) plus tokens.")
        return {"looked_up": len(rows), "found": 0, "unverified": 0,
                "failed": 0, "searches": 0}

    client = _client(cfg)
    found = unverified = failed = searches = 0

    stopped_early = False
    for n, row in enumerate(rows, 1):
        # Checked before the request, not after: the cap is there to bound what
        # an unattended run can spend, and a request already sent is already
        # billed. Rows past the cap keep status NULL, so the next run picks up
        # exactly where this one stopped.
        if max_searches is not None and searches >= max_searches:
            print(f"Stopping at --max-searches {max_searches} "
                  f"({len(rows) - n + 1} places left for next time).",
                  file=sys.stderr)
            stopped_early = True
            break

        label = f"[{n}/{len(rows)}] {row['name']}"
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=8000,
                system=LOOKUP_SYSTEM,
                messages=[{"role": "user", "content": _query_for(row)}],
                tools=[SEARCH_TOOL],
                output_config={
                    "format": {"type": "json_schema", "schema": LOOKUP_SCHEMA}
                },
            )
        except Exception as exc:  # noqa: BLE001
            print(f"{label}: {exc}", file=sys.stderr)
            db.save_enrichment(conn, row["id"], status="error", note=str(exc)[:200],
                               model=MODEL)
            failed += 1
            continue

        used = _searches_used(message)
        searches += used

        error = _search_error(message)
        if error:
            print(f"{label}: search error ({error})", file=sys.stderr)
            db.save_enrichment(conn, row["id"], status="error",
                               note=f"web search: {error}", searches=used,
                               model=MODEL)
            failed += 1
            continue

        try:
            data: dict[str, Any] = json.loads(_text_of(message))
        except json.JSONDecodeError:
            db.save_enrichment(conn, row["id"], status="error",
                               note="unparseable response", searches=used,
                               model=MODEL)
            failed += 1
            continue

        address = (data.get("address") or "").strip()
        source_url = (data.get("source_url") or "").strip()
        verified = _verify(source_url, _searched_urls(message))

        if not data.get("found") or not address:
            db.save_enrichment(conn, row["id"], status="not_found",
                               note=(data.get("note") or "").strip(),
                               website=(data.get("website") or "").strip(),
                               searches=used, model=MODEL)
            print(f"{label}: not found", file=sys.stderr)
            continue

        if not verified:
            unverified += 1
        found += 1
        db.save_enrichment(
            conn, row["id"], address=address,
            website=(data.get("website") or "").strip(),
            maps_url=maps_link(row["name"], address),
            phone=(data.get("phone") or "").strip(),
            source_url=source_url, verified=verified, status="ok",
            note=(data.get("note") or "").strip(), searches=used, model=MODEL,
        )
        mark = "" if verified else "  (unverified citation)"
        print(f"{label}: {address}{mark}", file=sys.stderr)

    cost = 0.01 * searches
    done = len(rows) if not stopped_early else found + failed
    print(f"Looked up {done} places: {found} with an address "
          f"({unverified} whose citation could not be verified), {failed} failed.")
    print(f"{searches} searches, about ${cost:.2f} plus tokens.")
    return {"looked_up": done, "found": found, "unverified": unverified,
            "failed": failed, "searches": searches,
            "stopped_early": stopped_early}

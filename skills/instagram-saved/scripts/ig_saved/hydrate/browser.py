"""Stage 2 via your own session — hydrate permalinks without a third party.

Used when Stage 1 came from the export (which carries only permalinks) and you
would rather not involve Apify, or when a post is from an account that has since
gone private and only your session can still see it.

A shortcode encodes the numeric media id, so this needs no lookup call: decode
it locally, then ask ``/api/v1/media/<pk>/info/`` for the full object.
"""

from __future__ import annotations

import sys
from typing import Iterator

from ..normalize import Post, from_private_media, shortcode_to_pk
from ..sources.browser import BrowserSession


def run(
    session: BrowserSession,
    shortcodes: list[str],
    *,
    progress: bool = True,
) -> Iterator[Post]:
    total = len(shortcodes)
    failures = 0

    for i, code in enumerate(shortcodes, 1):
        pk = shortcode_to_pk(code)
        if pk is None:
            print(f"  [{i}/{total}] {code}: unparseable shortcode", file=sys.stderr)
            failures += 1
            continue

        try:
            payload = session.api(f"/api/v1/media/{pk}/info/")
        except RuntimeError as exc:
            # A deleted post or a now-private account 404s. That is expected
            # across a large archive and must not abort the run.
            print(f"  [{i}/{total}] {code}: {exc}".split("\n")[0], file=sys.stderr)
            failures += 1
            if failures > 25 and failures > i * 0.5:
                raise RuntimeError(
                    "Over half of the first requests failed — stopping. "
                    "This usually means the session is stale or rate limited."
                ) from exc
            continue

        items = payload.get("items") or []
        if not items:
            failures += 1
            continue

        post = from_private_media(items[0])
        if post:
            if progress and i % 10 == 0:
                print(f"  [{i}/{total}] hydrated", file=sys.stderr)
            yield post

        session.pace()

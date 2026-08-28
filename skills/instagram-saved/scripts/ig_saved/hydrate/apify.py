"""Stage 2 via Apify — turn a list of permalinks into captions and media URLs.

Saved posts themselves are private, so no cookieless service can enumerate
them; that is Stage 1's job. But once you hold the permalinks, the posts behind
them are public, and hydrating them elsewhere keeps the fetch volume off your
own account entirely. That is the whole appeal: your session is never shared
with a third party, and the traffic that looks like scraping isn't yours.

Actor input schemas differ per publisher, so the URL field name is configurable
(``--url-field`` / ``APIFY_URL_FIELD``). Use ``--dry-run`` to print the payload
without spending credits.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Iterator

from ..config import Config
from ..normalize import Post, from_apify, post_url

API_ROOT = "https://api.apify.com/v2"

# Actors that take plain strings vs. Apify's {"url": ...} request objects.
_OBJECT_STYLE_FIELDS = {"startUrls", "start_urls"}


class ApifyError(RuntimeError):
    pass


def _actor_path(actor: str) -> str:
    # Apify's REST API separates owner and actor name with a tilde.
    return actor.replace("/", "~")


def build_input(cfg: Config, urls: list[str], extra: dict | None = None) -> dict:
    if cfg.apify_url_field in _OBJECT_STYLE_FIELDS:
        value: list = [{"url": u} for u in urls]
    else:
        value = urls

    payload: dict = {cfg.apify_url_field: value, "resultsLimit": len(urls)}
    if extra:
        payload.update(extra)
    return payload


def run(
    cfg: Config,
    shortcodes: list[str],
    *,
    batch_size: int = 100,
    dry_run: bool = False,
    extra_input: dict | None = None,
) -> Iterator[Post]:
    """Hydrate shortcodes in batches, yielding normalised posts."""
    if not dry_run and not cfg.apify_token:
        raise ApifyError(
            "No Apify token. Set APIFY_TOKEN, or hydrate from the browser "
            "session instead:\n    ig-saved hydrate --via browser"
        )

    for start in range(0, len(shortcodes), batch_size):
        batch = shortcodes[start : start + batch_size]
        urls = [post_url(c) for c in batch]
        payload = build_input(cfg, urls, extra_input)

        if dry_run:
            print(
                f"--- actor {cfg.apify_actor} "
                f"(batch {start // batch_size + 1}, {len(batch)} urls) ---\n"
                + json.dumps(payload, indent=2)[:2000],
                file=sys.stderr,
            )
            continue

        print(
            f"  apify: {len(batch)} urls -> {cfg.apify_actor}",
            file=sys.stderr,
        )
        for item in _run_sync(cfg, payload):
            post = from_apify(item)
            if post:
                yield post


def _run_sync(cfg: Config, payload: dict) -> list[dict]:
    url = (
        f"{API_ROOT}/acts/{_actor_path(cfg.apify_actor)}"
        f"/run-sync-get-dataset-items?token={cfg.apify_token}"
    )
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        # Actor runs are slow; the default socket timeout would cut them off.
        with urllib.request.urlopen(request, timeout=900) as response:
            items = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        if exc.code == 404:
            raise ApifyError(
                f"Actor '{cfg.apify_actor}' not found. Check the id "
                f"(owner/name) with --actor.\n{detail}"
            ) from exc
        if exc.code in (400, 422):
            raise ApifyError(
                f"The actor rejected the input — its URL field is probably not "
                f"'{cfg.apify_url_field}'.\nCheck the actor's input schema on "
                f"Apify and pass --url-field.\n{detail}"
            ) from exc
        raise ApifyError(f"Apify returned {exc.code}: {detail}") from exc

    if not isinstance(items, list):
        raise ApifyError(f"Expected a dataset array, got {type(items).__name__}")
    return items

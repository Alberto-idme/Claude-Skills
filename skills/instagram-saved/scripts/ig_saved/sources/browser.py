"""Stage 1b — read the saved list from your own logged-in browser session.

Why a real browser rather than an HTTP client with a copied ``sessionid``:

* You log in by hand, once. 2FA, checkpoints and "was this you?" prompts all
  work, and no password ever touches this code.
* The session is exercised by the same browser build, TLS stack, user agent and
  fingerprint that created it. A copied cookie replayed from a bare HTTP client
  is the thing Instagram is best at spotting.
* Calls are issued from *inside* the page with ``fetch``, so cookies, CSRF token
  and headers ride along on their own.

We call the JSON endpoints the web app itself uses rather than scraping the
grid. The saved grid is virtualised — nodes are recycled as you scroll, so DOM
scraping silently drops posts. The JSON is paginated, complete and typed.

This uses undocumented endpoints and is against Instagram's Terms of Use. Run it
on your own account, from your own machine, at the default pacing.
"""

from __future__ import annotations

import json
import random
import sys
import time
from typing import Callable, Iterator

from ..config import IG_APP_ID, Config
from ..normalize import Post, from_private_media

# Issued from inside the page so credentials and cookies attach automatically.
_FETCH_JS = """
async (path) => {
    const csrf = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
    const res = await fetch(path, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'x-ig-app-id': '%s',
            'x-csrftoken': csrf,
            'x-requested-with': 'XMLHttpRequest',
        },
    });
    const body = await res.text();
    try {
        return { status: res.status, json: JSON.parse(body) };
    } catch (e) {
        return { status: res.status, error: body.slice(0, 400) };
    }
}
""" % IG_APP_ID


class NotLoggedIn(RuntimeError):
    pass


class BrowserSession:
    """A persistent Chrome profile pointed at instagram.com."""

    def __init__(self, cfg: Config, headless: bool = False):
        self.cfg = cfg
        self.headless = headless
        self._pw = None
        self._ctx = None
        self.page = None

    def __enter__(self) -> "BrowserSession":
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover
            raise SystemExit(
                "The browser source needs Playwright:\n"
                "    pip install playwright && playwright install chromium"
            ) from exc

        self.cfg.browser_profile.mkdir(parents=True, exist_ok=True)
        self._pw = sync_playwright().start()

        launch: dict = {
            "user_data_dir": str(self.cfg.browser_profile),
            "headless": self.headless,
            "viewport": {"width": 1280, "height": 900},
            "args": ["--disable-blink-features=AutomationControlled"],
        }
        if self.cfg.chrome_path:
            launch["executable_path"] = self.cfg.chrome_path

        try:
            self._ctx = self._pw.chromium.launch_persistent_context(**launch)
        except Exception as exc:
            if "Executable doesn't exist" in str(exc):
                raise SystemExit(
                    "Playwright has no browser to launch. Either:\n"
                    "    playwright install chromium\n"
                    "or point it at a Chrome you already have:\n"
                    "    export IG_SAVED_CHROME=/path/to/chrome"
                ) from exc
            raise

        self.page = self._ctx.pages[0] if self._ctx.pages else self._ctx.new_page()
        self.page.goto(self.cfg.base_url + "/", wait_until="domcontentloaded")
        return self

    def __exit__(self, *exc) -> None:
        if self._ctx:
            self._ctx.close()
        if self._pw:
            self._pw.stop()

    # -- auth ------------------------------------------------------------

    def logged_in(self) -> bool:
        return any(
            c["name"] == "sessionid" and c.get("value")
            for c in self._ctx.cookies(self.cfg.base_url)
        )

    def ensure_login(self, timeout: int = 300) -> None:
        """Block until the profile has a session, prompting the user if not."""
        if self.logged_in():
            return
        if self.headless:
            raise NotLoggedIn(
                "This profile has no Instagram session and --headless can't "
                "prompt for one.\nRun `ig-saved login` once to sign in."
            )

        print(
            "Not signed in. A browser window is open — log in to Instagram there.\n"
            "Waiting (the session is then reused, so this is a one-time step)…",
            file=sys.stderr,
        )
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.logged_in():
                print("Signed in.", file=sys.stderr)
                time.sleep(2)  # let the app settle before hitting the API
                return
            time.sleep(2)
        raise NotLoggedIn(f"No session after {timeout}s.")

    # -- raw API ---------------------------------------------------------

    def api(self, path: str) -> dict:
        result = self.page.evaluate(_FETCH_JS, path)
        status = result.get("status")

        if status == 200 and "json" in result:
            return result["json"]

        if status in (401, 403):
            raise NotLoggedIn(
                f"Instagram rejected the request ({status}) for {path}.\n"
                "The session likely expired. Run `ig-saved login` to refresh it."
            )
        if status == 429:
            raise RuntimeError(
                "Rate limited (429). Stop for a few hours before retrying — "
                "pushing through this is how accounts get checkpointed."
            )
        raise RuntimeError(
            f"Unexpected response {status} for {path}: "
            f"{result.get('error') or json.dumps(result.get('json'))[:400]}"
        )

    def pace(self) -> None:
        time.sleep(random.uniform(self.cfg.min_delay, self.cfg.max_delay))

    def paginate(
        self,
        build_path: Callable[[str | None], str],
        *,
        collection: str | None = None,
        max_pages: int | None = None,
        progress: bool = True,
    ) -> Iterator[Post]:
        cursor: str | None = None
        pages = 0
        seen = 0

        while True:
            payload = self.api(build_path(cursor))
            items = payload.get("items") or []

            for item in items:
                post = from_private_media(item, collection=collection)
                if post:
                    seen += 1
                    yield post

            pages += 1
            if progress:
                print(f"  page {pages}: {len(items)} items ({seen} total)",
                      file=sys.stderr)

            cursor = payload.get("next_max_id")
            more = payload.get("more_available")
            if not cursor or more is False:
                break
            if max_pages and pages >= max_pages:
                print(f"  stopping at --max-pages {max_pages}", file=sys.stderr)
                break

            self.pace()

    # -- feeds -----------------------------------------------------------

    def all_saved(self, **kw) -> Iterator[Post]:
        def path(cursor: str | None) -> str:
            base = "/api/v1/feed/saved/posts/?"
            return base + (f"max_id={cursor}" if cursor else "")

        return self.paginate(path, **kw)

    def collection(self, collection_id: str, name: str | None = None, **kw) -> Iterator[Post]:
        def path(cursor: str | None) -> str:
            base = f"/api/v1/feed/collection/{collection_id}/posts/?"
            return base + (f"max_id={cursor}" if cursor else "")

        return self.paginate(path, collection=name or collection_id, **kw)

    def list_collections(self) -> list[dict]:
        types = '["ALL_MEDIA_AUTO_COLLECTION","MEDIA","PRODUCT_AUTO_COLLECTION"]'
        payload = self.api(f"/api/v1/collections/list/?collection_types={types}")
        out = []
        for item in payload.get("items") or []:
            out.append(
                {
                    "id": str(item.get("collection_id")),
                    "name": item.get("collection_name"),
                    "type": item.get("collection_type"),
                    "count": item.get("collection_media_count"),
                }
            )
        return out

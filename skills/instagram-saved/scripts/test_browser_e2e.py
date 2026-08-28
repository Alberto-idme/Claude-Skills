"""End-to-end test of the browser path against a mock Instagram.

The browser source is the part that cannot be checked by reading it: pagination
cursors, the in-page fetch, cookie detection and media download only prove out
by running. This stands up a local server that speaks the same JSON shapes as
Instagram's private endpoints and drives the real BrowserSession against it, so
a broken cursor key or a bad evaluate() signature fails here rather than on
someone's account.

    python3 test_browser_e2e.py

Needs Playwright plus a browser. Skips itself, loudly, if either is missing.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# The mock is on loopback; never send it through the outbound proxy.
os.environ["no_proxy"] = "127.0.0.1,localhost"
os.environ["NO_PROXY"] = "127.0.0.1,localhost"

sys.path.insert(0, str(Path(__file__).parent))

from ig_saved import db, media as media_mod  # noqa: E402
from ig_saved.config import Config  # noqa: E402

COLLECTION_ID = "18075071974439078"  # from the real saved-collection URL
FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"mock-jpeg-body" * 64
FAKE_MP4 = b"\x00\x00\x00\x18ftypmp42" + b"mock-mp4-body" * 64


def _media(code: str, *, video: bool = False, carousel: bool = False,
           port: int = 0) -> dict:
    base = f"http://127.0.0.1:{port}"
    node: dict = {
        "code": code,
        "pk": 3000000000000000001,
        "id": "3000000000000000001_12345",
        "taken_at": 1699000000,
        "like_count": 42,
        "comment_count": 7,
        "caption": {"text": f"caption for {code} tonkotsu"},
        "user": {"username": "kyoto_eats", "full_name": "Kyoto Eats"},
    }
    if carousel:
        node["media_type"] = 8
        node["carousel_media"] = [
            {"image_versions2": {"candidates": [
                {"url": f"{base}/cdn/{code}-0.jpg", "width": 1080, "height": 1350}]}},
            {"video_versions": [
                {"url": f"{base}/cdn/{code}-1.mp4", "width": 720, "height": 1280}]},
        ]
    elif video:
        node["media_type"] = 2
        node["product_type"] = "clips"
        node["video_versions"] = [
            {"url": f"{base}/cdn/{code}-0.mp4", "width": 720, "height": 1280}]
    else:
        node["media_type"] = 1
        node["image_versions2"] = {"candidates": [
            {"url": f"{base}/cdn/{code}-0.jpg", "width": 1080, "height": 1350}]}
    return node


class MockInstagram(BaseHTTPRequestHandler):
    port = 0

    def log_message(self, *args):  # silence the default stderr spam
        pass

    def _send(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, blob: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        url = urlparse(self.path)
        path, query = url.path, parse_qs(url.query)
        port = self.__class__.port

        # The landing page hands out a session cookie, standing in for login.
        if path == "/":
            body = b"<html><body>mock instagram</body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Set-Cookie", "sessionid=mock-session-value; Path=/")
            self.send_header("Set-Cookie", "csrftoken=mock-csrf; Path=/")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Reject anything missing the app id, exactly as Instagram would.
        if path.startswith("/api/") and not self.headers.get("x-ig-app-id"):
            self._send({"message": "missing x-ig-app-id"}, status=400)
            return

        if path == "/api/v1/collections/list/":
            self._send({"items": [
                {"collection_id": COLLECTION_ID, "collection_name": "japan",
                 "collection_type": "MEDIA", "collection_media_count": 3},
                {"collection_id": "999", "collection_name": "recipes",
                 "collection_type": "MEDIA", "collection_media_count": 1},
            ]})
            return

        if path == "/api/v1/feed/saved/posts/":
            cursor = (query.get("max_id") or [None])[0]
            if cursor is None:
                self._send({
                    "items": [{"media": _media("AAAAAAAAAAA", port=port)},
                              {"media": _media("BBBBBBBBBBB", video=True, port=port)}],
                    "more_available": True,
                    "next_max_id": "PAGE2",
                })
            else:
                self._send({
                    "items": [{"media": _media("CCCCCCCCCCC", carousel=True,
                                               port=port)}],
                    "more_available": False,
                })
            return

        if path == f"/api/v1/feed/collection/{COLLECTION_ID}/posts/":
            cursor = (query.get("max_id") or [None])[0]
            if cursor is None:
                self._send({
                    "items": [{"media": _media("DDDDDDDDDDD", port=port)}],
                    "more_available": True,
                    "next_max_id": "PAGE2",
                })
            else:
                self._send({
                    "items": [{"media": _media("EEEEEEEEEEE", video=True,
                                               port=port)}],
                    "more_available": False,
                })
            return

        if path.startswith("/api/v1/media/") and path.endswith("/info/"):
            self._send({"items": [_media("FFFFFFFFFFF", port=port)]})
            return

        if path.startswith("/cdn/"):
            if path.endswith(".mp4"):
                self._send_bytes(FAKE_MP4, "video/mp4")
            elif path.endswith("-gone.jpg"):
                self.send_error(403, "expired")
            else:
                self._send_bytes(FAKE_JPEG, "image/jpeg")
            return

        self._send({"message": f"no mock route for {path}"}, status=404)


def start_server() -> tuple[HTTPServer, str]:
    server = HTTPServer(("127.0.0.1", 0), MockInstagram)
    MockInstagram.port = server.server_port
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"


def find_chrome() -> str | None:
    if os.environ.get("IG_SAVED_CHROME"):
        return os.environ["IG_SAVED_CHROME"]
    root = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"))
    for pattern in ("chromium-*/chrome-linux/chrome",
                    "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"):
        found = sorted(root.glob(pattern))
        if found:
            return str(found[-1])
    return None


def run() -> int:
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("SKIP: playwright not installed (pip install playwright)")
        return 0

    from ig_saved.sources.browser import BrowserSession
    from ig_saved.hydrate import browser as browser_hydrate

    server, base_url = start_server()
    chrome = find_chrome()
    failures: list[str] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        if condition:
            print(f"  ok   {name}")
        else:
            print(f"  FAIL {name} {detail}")
            failures.append(name)

    try:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config(root=Path(tmp))
            cfg.base_url = base_url
            cfg.min_delay = cfg.max_delay = 0.0  # no need to be polite to a mock
            if chrome:
                cfg.chrome_path = chrome
            cfg.ensure_dirs()
            conn = db.connect(cfg.db_path)

            with BrowserSession(cfg, headless=True) as session:
                check("session cookie detected", session.logged_in())

                collections = session.list_collections()
                check("collections listed", len(collections) == 2,
                      f"got {len(collections)}")
                check("collection id parsed",
                      collections[0]["id"] == COLLECTION_ID,
                      f"got {collections[0]['id']}")

                # Pagination: page 1 says more_available, page 2 ends it.
                saved = list(session.all_saved(progress=False))
                check("saved feed paginated across 2 pages", len(saved) == 3,
                      f"got {len(saved)}")
                codes = {p.shortcode for p in saved}
                check("cursor followed to page 2", "CCCCCCCCCCC" in codes)

                by_code = {p.shortcode: p for p in saved}
                check("caption extracted",
                      by_code["AAAAAAAAAAA"].caption.endswith("tonkotsu"))
                check("author extracted",
                      by_code["AAAAAAAAAAA"].author_username == "kyoto_eats")
                check("video typed",
                      by_code["BBBBBBBBBBB"].media_type == "video")
                check("carousel children flattened",
                      [m.kind for m in by_code["CCCCCCCCCCC"].media]
                      == ["image", "video"])

                collection_posts = list(
                    session.collection(COLLECTION_ID, name="japan", progress=False)
                )
                check("collection feed paginated", len(collection_posts) == 2,
                      f"got {len(collection_posts)}")
                check("collection name stamped",
                      all(p.collection == "japan" for p in collection_posts))

                check("max_pages honoured",
                      len(list(session.all_saved(max_pages=1, progress=False))) == 2)

                # Hydration by shortcode, exercising the local pk decode.
                hydrated = list(
                    browser_hydrate.run(session, ["CqxU1FzL0Dg"], progress=False)
                )
                check("hydrate by shortcode", len(hydrated) == 1)

                db.upsert_posts(conn, saved + collection_posts)

            # Media download runs outside the browser, straight off the CDN URLs.
            counts = media_mod.download_all(conn, cfg, workers=2)
            check("media downloaded", counts["downloaded"] == 6,
                  f"got {counts}")
            check("no download failures", counts["failed"] == 0, f"got {counts}")

            files = sorted(cfg.media_dir.rglob("*.*"))
            check("files on disk", len(files) == 6, f"got {len(files)}")
            check("jpeg bytes intact",
                  any(f.suffix == ".jpg" and f.read_bytes() == FAKE_JPEG
                      for f in files))
            check("mp4 bytes intact",
                  any(f.suffix == ".mp4" and f.read_bytes() == FAKE_MP4
                      for f in files))
            check("download is idempotent",
                  media_mod.download_all(conn, cfg)["downloaded"] == 0)

            db.reindex(conn)
            hits = db.search(conn, "tonkotsu")
            check("indexed posts are searchable", len(hits) == 5,
                  f"got {len(hits)}")

            stats = db.stats(conn)
            check("stats consistent",
                  stats["posts"] == 5 and stats["downloaded"] == 6,
                  f"got {stats}")
    finally:
        server.shutdown()

    total = 20
    print(f"\n{total - len(failures)}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(run())

"""Whole-chain smoke test: mock Instagram in, report.html out.

Every stage runs for real except the three that need credentials or a paid API
— Whisper, `describe` and `extract` are stubbed. Everything between them is
genuine: the browser session against a mock Instagram, media download, OCR over
real encoded video frames, the database, FTS, and report rendering.

    python3 test_pipeline_smoke.py [--out DIR]

Exits non-zero if any stage fails to produce what the next one needs.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ["no_proxy"] = os.environ["NO_PROXY"] = "127.0.0.1,localhost"
sys.path.insert(0, str(Path(__file__).parent))

STAGES: list[tuple[str, str]] = []


def stage(name: str, detail: str) -> None:
    STAGES.append((name, detail))
    print(f"  {name:<14} {detail}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", help="keep the generated report here")
    args = parser.parse_args()

    from test_browser_e2e import find_chrome, start_server
    from test_ocr_e2e import build_image, build_video

    from ig_saved import db, describe as describe_mod, extract as extract_mod
    from ig_saved import media as media_mod, ocr as ocr_mod
    from ig_saved import report as report_mod, transcribe as transcribe_mod
    from ig_saved.config import Config
    from ig_saved.sources.browser import BrowserSession

    server, base_url = start_server()
    workdir = Path(tempfile.mkdtemp())

    try:
        cfg = Config(root=workdir / "home")
        cfg.base_url = base_url
        cfg.min_delay = cfg.max_delay = 0.0
        chrome = find_chrome()
        if chrome:
            cfg.chrome_path = chrome
        cfg.ensure_dirs()
        conn = db.connect(cfg.db_path)

        print("\nPipeline\n" + "─" * 60)

        # 1 ─ index, straight off the mock's private endpoints
        with BrowserSession(cfg, headless=True) as session:
            session.ensure_login()
            posts = list(session.collection("18075071974439078", name="japan",
                                            progress=False))
            posts += list(session.all_saved(progress=False))
        new, updated = db.upsert_posts(conn, posts)
        stage("index", f"{new} new, {updated} updated")
        if not new:
            print("index produced nothing", file=sys.stderr)
            return 1

        # 2 ─ media, real HTTP against the mock CDN
        counts = media_mod.download_all(conn, cfg, workers=2)
        stage("media", f"{counts['downloaded']} files, "
                       f"{media_mod.human_bytes(counts['bytes'])}")

        # The mock serves tiny stub bytes; swap in a real encoded clip so OCR
        # and frame sampling have actual pixels to work on.
        real = workdir / "reel.mp4"
        build_video(real)
        card = workdir / "card.jpg"
        build_image(card)
        videos = list(conn.execute(
            "SELECT id, local_path FROM media WHERE kind = 'video'"))
        for row in videos:
            shutil.copy(real, row["local_path"])
        images = list(conn.execute(
            "SELECT id, local_path FROM media WHERE kind = 'image'"))
        for row in images:
            shutil.copy(card, row["local_path"])
        stage("fixtures", f"{len(videos)} videos + {len(images)} images "
                          "replaced with real media")

        # 3 ─ transcribe (stubbed model, real DB path)
        transcribe_mod._BACKEND = ("stub-whisper", lambda p: (
            [{"start": 0.0, "end": 3.0,
              "text": "the broth here is unbelievable, open past midnight"}],
            "en"))
        counts = transcribe_mod.transcribe_all(conn, cfg)
        stage("transcribe", f"{counts['transcribed']} ok, "
                            f"{counts['no_speech']} no speech")

        # 4 ─ OCR, entirely real
        counts = ocr_mod.run_all(conn, cfg)
        stage("ocr", f"{counts['read']} read, {counts['empty']} blank")
        if not counts["read"]:
            print("OCR read nothing", file=sys.stderr)
            return 1

        # 5 ─ describe (stubbed client, real frame sampling and encoding)
        class _Msg:
            class _U:
                input_tokens, output_tokens = 2400, 60

            class _B:
                type = "text"
                text = ("A narrow ramen counter with wooden booths, a ticket "
                        "vending machine by the door and a queue outside.")

            content, usage = [_B()], _U()

        class _Client:
            def __init__(self):
                self.calls = []
                self.messages = self

            def create(self, **kw):
                self.calls.append(kw)
                return _Msg()

        vision = _Client()
        describe_mod._client = lambda _c: vision
        counts = describe_mod.run_all(conn, cfg, frames_per_video=3)
        frames_sent = sum(
            len([b for b in c["messages"][0]["content"] if b["type"] == "image"])
            for c in vision.calls)
        stage("describe", f"{counts['described']} videos, "
                          f"{frames_sent} frames encoded and sent")

        # 6 ─ extract (stubbed client, real evidence assembly and schema)
        seen_evidence: list[str] = []

        class _Extract(_Client):
            def create(self, **kw):
                seen_evidence.append(kw["messages"][0]["content"])
                import json as _json

                class M:
                    class B:
                        type = "text"
                        text = _json.dumps({
                            "title": "Ichiran Shibuya",
                            "category": "restaurant",
                            "location": "Shibuya, Tokyo",
                            "summary": "Counter-only tonkotsu with solo booths.",
                            "highlights": ["Open past midnight",
                                           "Ticket machine at the door"],
                            "action": "visit",
                            "practical": "Open until midnight",
                            "confidence": "high",
                            "needs_review": False,
                        })

                    content = [B()]
                return M()

        extract_mod._client = lambda _c: _Extract()
        counts = extract_mod.run_all(conn, cfg)
        stage("extract", f"{counts['extracted']} entries")

        tracks = set()
        for evidence in seen_evidence:
            for marker, name in (("CAPTION:", "caption"), ("SPEECH:", "voice"),
                                 ("ON-SCREEN TEXT:", "screen"),
                                 ("FOOTAGE:", "video")):
                if marker in evidence:
                    tracks.add(name)
        stage("evidence", f"tracks reaching the model: {', '.join(sorted(tracks))}")
        if len(tracks) < 4:
            print(f"only {len(tracks)}/4 tracks reached extraction",
                  file=sys.stderr)
            return 1

        # 7 ─ report
        out_dir = Path(args.out).expanduser() if args.out else workdir / "report"
        written = report_mod.build(conn, cfg, out_dir)
        stage("report", f"{written['count']} entries -> "
                        f"{', '.join(k for k in written if k != 'count')}")

        page = written["html"].read_text()
        for probe in ("Ichiran", "All categories", "restaurant"):
            if probe not in page:
                print(f"report.html missing {probe!r}", file=sys.stderr)
                return 1
        stage("html", f"{len(page):,} bytes, self-contained")

        # 8 ─ search across every track
        print("\nSearch across tracks\n" + "─" * 60)
        for query, expect in (("tonkotsu", "voice"), ("ICHIRAN", "on-screen"),
                              ("vending", "description"), ("ラーメン", "CJK")):
            hits = db.search(conn, query)
            print(f"  {query:<12} {len(hits):>2} hit(s)   ({expect})")

        stats = db.stats(conn)
        print("\nFunnel\n" + "─" * 60)
        for key in ("posts", "media", "downloaded", "videos", "transcripts",
                    "screen_text", "described"):
            print(f"  {key:<14} {stats[key]}")

        if args.out:
            print(f"\nReport kept at {out_dir}")
        return 0

    finally:
        server.shutdown()
        if not args.out:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

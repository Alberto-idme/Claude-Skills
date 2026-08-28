"""End-to-end test of the OCR and description passes on a real video.

Builds an mp4 with known text burned into it, then checks the pipeline reads
that text back. Frame sampling, scene-change skipping, dedupe of text that
persists across frames, and the DB/FTS write are all exercised against real
pixels rather than fixtures.

The description pass is driven with a stub client — calling the real API costs
money, so that stays behind an explicit run.

    python3 test_ocr_e2e.py
"""

from __future__ import annotations

import sys
import tempfile
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

FRAME_TEXT = [
    (0.0, "TOKYO RAMEN GUIDE"),
    (2.0, "ICHIRAN SHIBUYA"),
    (4.0, "OPEN UNTIL MIDNIGHT"),
]


def build_video(path: Path, seconds: float = 6.0, fps: int = 12,
                audio: bool = True) -> None:
    """Write an mp4 whose on-screen text changes every two seconds.

    An audio stream is included by default: without one the transcription pass
    correctly classifies the file as `no_audio` and never runs, which silently
    removes the voice track from any end-to-end check.
    """
    import av
    import cv2
    import numpy as np

    container = av.open(str(path), mode="w")
    stream = container.add_stream("libx264", rate=fps)
    stream.width, stream.height = 640, 360
    stream.pix_fmt = "yuv420p"

    if audio:
        rate = 44100
        astream = container.add_stream("aac", rate=rate)
        total = int(seconds * rate)
        tone = (0.2 * np.sin(2 * np.pi * 220 *
                             np.arange(total) / rate)).astype(np.float32)
        chunk = astream.frame_size or 1024
        for start in range(0, total, chunk):
            block = tone[start:start + chunk]
            if len(block) < chunk:
                block = np.pad(block, (0, chunk - len(block)))
            aframe = av.AudioFrame.from_ndarray(
                block.reshape(1, -1), format="fltp", layout="mono")
            aframe.sample_rate = rate
            aframe.pts = start
            aframe.time_base = Fraction(1, rate)
            for packet in astream.encode(aframe):
                container.mux(packet)
        for packet in astream.encode():
            container.mux(packet)

    for i in range(int(seconds * fps)):
        when = i / fps
        caption = FRAME_TEXT[0][1]
        for start, text in FRAME_TEXT:
            if when >= start:
                caption = text

        canvas = np.zeros((360, 640, 3), dtype=np.uint8)
        canvas[:] = (20, 20, 20)
        cv2.putText(canvas, caption, (30, 190), cv2.FONT_HERSHEY_SIMPLEX,
                    1.1, (255, 255, 255), 3, cv2.LINE_AA)

        frame = av.VideoFrame.from_ndarray(canvas, format="bgr24")
        for packet in stream.encode(frame):
            container.mux(packet)

    for packet in stream.encode():
        container.mux(packet)
    container.close()


def build_image(path: Path) -> None:
    import cv2
    import numpy as np

    canvas = np.zeros((360, 640, 3), dtype=np.uint8)
    canvas[:] = (30, 30, 30)
    cv2.putText(canvas, "SAPPORO MISO", (40, 200), cv2.FONT_HERSHEY_SIMPLEX,
                1.2, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.imwrite(str(path), canvas)


class StubMessages:
    """Stands in for client.messages, recording what it was asked."""

    def __init__(self, outer):
        self.outer = outer

    def create(self, **kwargs):
        self.outer.calls.append(kwargs)

        class Usage:
            input_tokens, output_tokens = 2400, 60

        class Block:
            type, text = "text", ("A narrow ramen counter with a queue outside "
                                  "and a ticket vending machine by the door.")

        class Message:
            content, usage = [Block()], Usage()

        return Message()


class StubClient:
    def __init__(self):
        self.calls = []
        self.messages = StubMessages(self)


def run() -> int:
    try:
        import av  # noqa: F401
        import cv2  # noqa: F401
    except ImportError as exc:
        print(f"SKIP: needs PyAV and opencv ({exc})")
        return 0

    from ig_saved import db, describe as describe_mod, frames as frames_mod
    from ig_saved import ocr as ocr_mod
    from ig_saved.config import Config
    from ig_saved.normalize import MediaRef, Post

    failures: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(f"  {'ok  ' if ok else 'FAIL'} {name} {detail if not ok else ''}")
        if not ok:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        video = root / "reel.mp4"
        image = root / "card.jpg"
        build_video(video)
        build_image(image)
        check("test video written", video.exists() and video.stat().st_size > 0)
        from ig_saved.transcribe import has_audio
        check("fixture has an audio track", has_audio(video) is True,
              "transcription would be skipped as no_audio")

        # --- frame sampling -------------------------------------------------
        sampled = list(frames_mod.iter_frames(video, interval=0.5))
        check("frames sampled", len(sampled) >= 3, f"got {len(sampled)}")
        # Static stretches must collapse: 6s at 0.5s would be 12 without it.
        check("static frames skipped", len(sampled) <= 8, f"got {len(sampled)}")

        keys = frames_mod.keyframes(video, count=3)
        check("keyframes spread", len(keys) == 3, f"got {len(keys)}")
        check("keyframes ordered",
              all(a[0] <= b[0] for a, b in zip(keys, keys[1:])))

        jpeg = frames_mod.to_jpeg(keys[0][1])
        check("jpeg encoded", jpeg[:2] == b"\xff\xd8", f"got {jpeg[:4]!r}")
        check("jpeg downscaled", len(jpeg) < 200_000, f"{len(jpeg)} bytes")

        # --- OCR ------------------------------------------------------------
        try:
            ocr_mod._load_engine()
        except SystemExit:
            print("  SKIP: no OCR engine installed")
            return 1 if failures else 0

        lines, scanned = ocr_mod.ocr_video(video, interval=0.5)
        found = " ".join(item["text"] for item in lines).upper()
        check("frames scanned", scanned >= 3, f"got {scanned}")
        for _start, expected in FRAME_TEXT:
            first_word = expected.split()[0]
            check(f"read {first_word!r}", first_word in found,
                  f"got {found!r}")

        # Text held across many frames must appear once, not per frame.
        tokyo = [item for item in lines if "TOKYO" in item["text"].upper()]
        check("persistent text deduped", len(tokyo) == 1, f"got {len(tokyo)}")
        check("timestamps attached", all("t" in item for item in lines))

        image_lines, _ = ocr_mod.ocr_image(image)
        image_text = " ".join(i["text"] for i in image_lines).upper()
        check("still image read", "SAPPORO" in image_text, f"got {image_text!r}")

        # --- dedupe unit ----------------------------------------------------
        check("partial reveal collapsed",
              ocr_mod.dedupe(["Tokyo Ram", "Tokyo Ramen", "Tokyo Ramen"])
              == ["Tokyo Ramen"])

        # --- database + search ---------------------------------------------
        cfg = Config(root=root / "data")
        cfg.ensure_dirs()
        conn = db.connect(cfg.db_path)
        db.upsert_posts(conn, [Post(
            shortcode="R1", url="https://www.instagram.com/p/R1/",
            caption="no keyword in the caption", collection="japan",
            media=[MediaRef(0, "video", "https://cdn/v.mp4")])])
        media_id = db.pending_downloads(conn)[0]["id"]
        db.mark_downloaded(conn, media_id, str(video))

        counts = ocr_mod.run_all(conn, cfg)
        check("ocr pass recorded", counts["read"] == 1, f"got {counts}")
        check("ocr not re-queued", db.pending_ocr(conn) == [])

        db.reindex(conn)
        check("on-screen text searchable",
              [r["shortcode"] for r in db.search(conn, "ichiran")] == ["R1"])
        check("ocr scoped by collection",
              len(db.pending_ocr(conn, collection="japan")) == 0)

        # --- description (stubbed client) -----------------------------------
        stub = StubClient()
        describe_mod._client = lambda _cfg: stub
        counts = describe_mod.run_all(conn, cfg, frames_per_video=3)
        check("description recorded", counts["described"] == 1, f"got {counts}")
        check("model is opus 5", stub.calls[0]["model"] == "claude-opus-5",
              stub.calls[0]["model"])

        content = stub.calls[0]["messages"][0]["content"]
        images = [b for b in content if b["type"] == "image"]
        check("frames sent as images", len(images) == 3, f"got {len(images)}")
        check("images are base64 jpeg",
              images[0]["source"]["media_type"] == "image/jpeg")
        check("prompt says ignore audio",
              "do not mention music" in stub.calls[0]["system"].lower())

        db.reindex(conn)
        check("description searchable",
              [r["shortcode"] for r in db.search(conn, "vending")] == ["R1"])
        check("description not re-queued",
              db.pending_descriptions(conn) == [])

        stats = db.stats(conn)
        check("stats count both tracks",
              stats["screen_text"] == 1 and stats["described"] == 1,
              f"got {stats}")

        # --- combined transcript --------------------------------------------
        db.save_transcript(conn, media_id=media_id, shortcode="R1",
                           text="best tonkotsu in the city", segments=[],
                           language="en", model="stub", status="ok")
        from ig_saved.cli import _render_transcript

        rendered = _render_transcript(db.transcript_for(conn, "R1"))
        for section in ("── Caption ──", "── Voice ──", "── On-screen text ──",
                        "── Video ──"):
            check(f"transcript has {section.strip('─ ')}", section in rendered)
        check("transcript carries voice", "tonkotsu" in rendered)
        check("transcript carries screen text", "ICHIRAN" in rendered.upper())
        check("transcript carries description", "vending" in rendered)
        check("transcript shows collection", "japan" in rendered)

    total = 28
    print(f"\n{total - len(failures)}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(run())

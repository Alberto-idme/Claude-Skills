"""Transcribe saved reels so spoken content becomes searchable.

Prefers ``faster-whisper``: it is several times quicker than the reference
implementation and decodes audio through bundled PyAV, so no system ffmpeg is
required. Falls back to ``openai-whisper``, which does need ffmpeg on PATH.

Both are optional imports — the rest of the tool works without either.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from . import db
from .config import Config

_BACKEND = None


def _load_backend(model_name: str):
    """Return ``(name, transcribe_fn)``; the model is loaded once per process."""
    global _BACKEND
    if _BACKEND is not None:
        return _BACKEND

    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(model_name, device="auto", compute_type="auto")

        def run(path: Path):
            segments, info = model.transcribe(str(path), vad_filter=True)
            out = [
                {"start": s.start, "end": s.end, "text": s.text.strip()}
                for s in segments
            ]
            return out, info.language

        _BACKEND = ("faster-whisper", run)
        return _BACKEND
    except ImportError:
        pass

    try:
        import whisper

        model = whisper.load_model(model_name)

        def run(path: Path):
            result = model.transcribe(str(path))
            out = [
                {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
                for s in result.get("segments", [])
            ]
            return out, result.get("language")

        _BACKEND = ("openai-whisper", run)
        return _BACKEND
    except ImportError:
        pass

    raise SystemExit(
        "Transcription needs a Whisper backend:\n"
        "    pip install faster-whisper        # recommended, no ffmpeg needed\n"
        "    pip install openai-whisper        # alternative, requires ffmpeg"
    )


def transcribe_all(
    conn: sqlite3.Connection,
    cfg: Config,
    *,
    limit: int | None = None,
) -> dict:
    rows = db.pending_transcripts(conn)
    if limit:
        rows = rows[:limit]
    if not rows:
        return {"transcribed": 0, "skipped": 0, "failed": 0}

    backend, run = _load_backend(cfg.whisper_model)
    print(
        f"  {backend} / {cfg.whisper_model}: {len(rows)} videos",
        file=sys.stderr,
    )

    counts = {"transcribed": 0, "skipped": 0, "failed": 0}

    for n, row in enumerate(rows, 1):
        path = Path(row["local_path"])
        if not path.exists():
            counts["skipped"] += 1
            continue

        try:
            segments, language = run(path)
        except Exception as exc:  # noqa: BLE001 - a silent reel is not fatal
            print(f"  {row['shortcode']}: {exc}", file=sys.stderr)
            counts["failed"] += 1
            continue

        text = " ".join(s["text"] for s in segments).strip()
        db.save_transcript(
            conn,
            media_id=row["id"],
            shortcode=row["shortcode"],
            text=text,
            segments=segments,
            language=language,
            model=f"{backend}:{cfg.whisper_model}",
        )
        counts["transcribed"] += 1
        print(
            f"  [{n}/{len(rows)}] {row['shortcode']}: "
            f"{len(text)} chars ({language})",
            file=sys.stderr,
        )

    return counts

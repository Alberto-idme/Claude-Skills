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
            # Segments are lazy; consuming them here is what actually decodes,
            # so VAD errors surface inside this call rather than at the caller.
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


def reclassify(
    conn: sqlite3.Connection, min_chars: int = 0
) -> dict:
    """Re-apply the quality filter to transcripts already in the database.

    Runs no model, so it is instant — for cleaning up rows written before the
    filter existed, or after changing the threshold. Rows demoted to no_speech
    keep their text; they just stop being indexed.
    """
    if not min_chars:
        min_chars = DEFAULT_MIN_CHARS

    demoted = promoted = 0
    for row in conn.execute(
        "SELECT media_id, text, status FROM transcripts"
    ).fetchall():
        good = is_meaningful(row["text"] or "", min_chars)
        if good and row["status"] == "no_speech":
            # A raised-then-lowered threshold can rescue rows.
            conn.execute("UPDATE transcripts SET status = 'ok' WHERE media_id = ?",
                         (row["media_id"],))
            promoted += 1
        elif not good and row["status"] == "ok":
            conn.execute(
                "UPDATE transcripts SET status = 'no_speech' WHERE media_id = ?",
                (row["media_id"],))
            demoted += 1

    conn.commit()
    return {"demoted": demoted, "promoted": promoted}


def has_audio(path: Path) -> bool | None:
    """True/False if the container can be inspected, None if we cannot tell.

    faster-whisper pulls in PyAV, so this is usually available for free and
    saves loading a whole video into the model just to find it is silent.
    """
    try:
        import av
    except ImportError:
        return None
    try:
        with av.open(str(path)) as container:
            return bool(container.streams.audio)
    except Exception:  # noqa: BLE001 - unreadable file; let Whisper have a go
        return None


# faster-whisper raises this out of feature extraction when VAD leaves nothing
# behind — a music-only or silent reel. It is a property of the video, not a
# bug, so it must not be retried on every run.
_EMPTY_AUDIO_SIGNS = ("tuple index out of range", "index out of range",
                      "cannot reshape array of size 0", "zero-size array")


# Whisper hallucinates stock phrases over music or silence rather than
# returning nothing. Left as 'ok' these pollute search: every silent reel
# becomes a hit for "thank you". Matched after casefolding and stripping
# punctuation. Japanese and Korean entries are the sign-off phrases their
# training data is saturated with.
_HALLUCINATIONS = {
    "you", "bye", "okay", "ok", "so", "oh", "thank you", "thanks",
    "thank you very much", "thanks for watching", "thank you for watching",
    "please subscribe", "like and subscribe", "subscribe to my channel",
    "music", "applause", "laughter", "silence", "outro", "intro",
    "ご視聴ありがとうございました", "ご視聴ありがとうございます",
    "チャンネル登録お願いします", "おやすみなさい",
    "시청해주셔서 감사합니다", "구독과 좋아요 부탁드립니다", "감사합니다",
}

# Substrings that mark scraped-subtitle boilerplate anywhere in the text.
_HALLUCINATION_MARKERS = ("amara.org", "subtitles by", "subs by",
                          "transcribed by", "subtitled by")

# Below this, a transcript carries no searchable signal — the observed
# failures were 3 and 8 characters.
DEFAULT_MIN_CHARS = 12


def _normalise(text: str) -> str:
    stripped = "".join(c for c in text.casefold() if c.isalnum() or c.isspace()
                       or ord(c) > 0x2FFF)
    return " ".join(stripped.split())


def is_meaningful(text: str, min_chars: int = DEFAULT_MIN_CHARS) -> bool:
    """Whether a transcript carries enough signal to be worth indexing."""
    normalised = _normalise(text)
    if not normalised:
        return False
    if any(marker in normalised for marker in _HALLUCINATION_MARKERS):
        return False
    if normalised in _HALLUCINATIONS:
        return False
    # A repeated single phrase ("thank you thank you thank you") is the other
    # shape hallucination takes, and length alone would let it through.
    words = normalised.split()
    if len(set(words)) <= 2 and len(words) > 2:
        return False
    return len(normalised) >= min_chars


def _classify(exc: Exception) -> str:
    message = str(exc).lower()
    if any(sign in message for sign in _EMPTY_AUDIO_SIGNS):
        return "no_speech"
    return "error"


def transcribe_all(
    conn: sqlite3.Connection,
    cfg: Config,
    *,
    limit: int | None = None,
    retry_failed: bool = False,
    collection: str | None = None,
    shortcodes: list[str] | None = None,
    min_chars: int = DEFAULT_MIN_CHARS,
) -> dict:
    rows = db.pending_transcripts(
        conn, retry_failed=retry_failed, collection=collection,
        shortcodes=shortcodes,
    )
    if limit:
        rows = rows[:limit]
    if not rows:
        return {"transcribed": 0, "skipped": 0, "failed": 0,
                "no_audio": 0, "no_speech": 0}

    backend, run = _load_backend(cfg.whisper_model)
    model_label = f"{backend}:{cfg.whisper_model}"
    print(f"  {backend} / {cfg.whisper_model}: {len(rows)} videos",
          file=sys.stderr)

    counts = {"transcribed": 0, "skipped": 0, "failed": 0,
              "no_audio": 0, "no_speech": 0}

    def record(row, *, text="", segments=(), language=None, status="ok") -> None:
        db.save_transcript(
            conn,
            media_id=row["id"],
            shortcode=row["shortcode"],
            text=text,
            segments=list(segments),
            language=language,
            model=model_label,
            status=status,
        )

    for n, row in enumerate(rows, 1):
        path = Path(row["local_path"])

        # A file that is simply absent may come back; leave it pending.
        if not path.exists():
            counts["skipped"] += 1
            continue

        if has_audio(path) is False:
            record(row, status="no_audio")
            counts["no_audio"] += 1
            print(f"  [{n}/{len(rows)}] {row['shortcode']}: no audio track",
                  file=sys.stderr)
            continue

        try:
            segments, language = run(path)
        except Exception as exc:  # noqa: BLE001 - one bad reel is not fatal
            status = _classify(exc)
            record(row, status=status)
            counts["no_speech" if status == "no_speech" else "failed"] += 1
            detail = "no speech found" if status == "no_speech" else str(exc)
            print(f"  [{n}/{len(rows)}] {row['shortcode']}: {detail}",
                  file=sys.stderr)
            continue

        text = " ".join(s["text"] for s in segments).strip()
        if not is_meaningful(text, min_chars):
            # Keep the text so it can be inspected, but do not index it.
            record(row, text=text, language=language, status="no_speech")
            counts["no_speech"] += 1
            detail = f"discarded {len(text)} chars" if text else "no speech found"
            print(f"  [{n}/{len(rows)}] {row['shortcode']}: {detail}",
                  file=sys.stderr)
            continue

        record(row, text=text, segments=segments, language=language)
        counts["transcribed"] += 1
        print(f"  [{n}/{len(rows)}] {row['shortcode']}: "
              f"{len(text)} chars ({language})", file=sys.stderr)

    return counts

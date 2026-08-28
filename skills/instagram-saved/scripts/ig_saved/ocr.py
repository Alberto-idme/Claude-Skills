"""Read the text burned into reels and images.

For travel and recommendation reels this is usually where the actual content
is — the restaurant name is on a title card, not spoken aloud. It is also the
only signal for the reels that come back `no_speech`, which are typically
music-over-captions.

RapidOCR is preferred: ONNX-based, so no PyTorch, and its bundled models read
Japanese, Korean and Chinese as well as Latin scripts — which matters here,
since the reels are not all in English.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

from . import db, frames as frames_mod
from .config import Config

_ENGINE = None


def _load_engine():
    """Return ``(name, run)`` where ``run(rgb) -> [(text, confidence)]``."""
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    try:
        from rapidocr_onnxruntime import RapidOCR

        engine = RapidOCR()

        def run(image):
            result, _elapsed = engine(image)
            return [(line[1], float(line[2])) for line in (result or [])]

        _ENGINE = ("rapidocr", run)
        return _ENGINE
    except ImportError:
        pass

    try:
        import easyocr

        reader = easyocr.Reader(["en", "ja", "ko"], gpu=False)

        def run(image):
            return [(text, float(conf))
                    for _box, text, conf in reader.readtext(image)]

        _ENGINE = ("easyocr", run)
        return _ENGINE
    except ImportError:
        pass

    try:
        import pytesseract

        def run(image):
            text = pytesseract.image_to_string(image)
            return [(line, 1.0) for line in text.splitlines() if line.strip()]

        _ENGINE = ("tesseract", run)
        return _ENGINE
    except ImportError:
        pass

    raise SystemExit(
        "OCR needs an engine:\n"
        "    pip install rapidocr-onnxruntime   # recommended, reads CJK, no torch\n"
        "    pip install easyocr                # alternative, pulls in PyTorch"
    )


def _normalise(text: str) -> str:
    return " ".join(text.split()).casefold()


SIMILARITY = 0.86


def _near_duplicate(a: str, b: str, threshold: float = SIMILARITY) -> bool:
    """Whether two reads are the same text with OCR jitter between them.

    A caption that holds for 30 frames is read 30 times, and the reads differ:
    ICHIRAN / ICHlRAN / 1CHIRAN, OPEN / 0PEN. None is a substring of another,
    so containment alone leaves all of them — one real reel produced 266 lines
    from 178 frames that way.
    """
    longest = max(len(a), len(b), 1)
    # Cheap length gate before the O(n*m) comparison.
    if abs(len(a) - len(b)) / longest > 0.3:
        return False
    return SequenceMatcher(None, a, b).ratio() >= threshold


def dedupe(lines: list[str], threshold: float = SIMILARITY) -> list[str]:
    """Collapse repeats, partials and near-identical reads across frames.

    Three cases, in order of cost: exact repeats, a line contained in one
    already kept (animated text caught mid-reveal — "Tokyo Ram" then "Tokyo
    Ramen"), and fuzzy matches from OCR jitter. The longest read of a group
    wins, since truncation is the more common failure than hallucinated extra
    characters.
    """
    kept: list[str] = []
    normalised: list[str] = []

    for line in lines:
        candidate = _normalise(line)
        if not candidate:
            continue

        replaced = False
        for i, current in enumerate(normalised):
            if candidate == current or candidate in current:
                replaced = True
                break
            if current in candidate or _near_duplicate(candidate, current,
                                                       threshold):
                if len(candidate) > len(current):
                    kept[i], normalised[i] = line, candidate
                replaced = True
                break
        if not replaced:
            kept.append(line)
            normalised.append(candidate)

    return kept


def reclean(conn: sqlite3.Connection, threshold: float = SIMILARITY) -> dict:
    """Re-apply dedupe to OCR rows already in the database.

    Runs no OCR, so it is seconds rather than minutes — for cleaning up rows
    written before the fuzzy pass existed, or after changing the threshold.
    """
    changed = removed = 0
    rows = conn.execute(
        "SELECT media_id, shortcode, lines_json FROM ocr WHERE status = 'ok'"
    ).fetchall()

    for row in rows:
        lines = json.loads(row["lines_json"] or "[]")
        if not lines:
            continue

        kept = dedupe([item["text"] for item in lines], threshold)
        keep = {_normalise(t) for t in kept}
        seen: set[str] = set()
        cleaned = []
        for item in lines:
            key = _normalise(item["text"])
            if key in keep and key not in seen:
                seen.add(key)
                cleaned.append(item)

        if len(cleaned) == len(lines):
            continue

        removed += len(lines) - len(cleaned)
        changed += 1
        conn.execute(
            "UPDATE ocr SET text = ?, lines_json = ? WHERE media_id = ?",
            ("\n".join(i["text"] for i in cleaned),
             json.dumps(cleaned, ensure_ascii=False), row["media_id"]),
        )

    conn.commit()
    return {"files": changed, "lines_removed": removed, "scanned": len(rows)}


def ocr_video(
    path: Path, *, interval: float = 1.0, min_confidence: float = 0.5
) -> tuple[list[dict], int]:
    """Return ``(lines, frames_scanned)`` with a timestamp on each line."""
    _name, run = _load_engine()
    collected: list[dict] = []
    scanned = 0

    for when, frame in frames_mod.iter_frames(path, interval=interval):
        scanned += 1
        for text, confidence in run(frame):
            if confidence >= min_confidence and text.strip():
                collected.append({"t": round(when, 2), "text": text.strip()})

    texts = dedupe([item["text"] for item in collected])
    keep = {_normalise(t) for t in texts}
    seen: set[str] = set()
    lines = []
    for item in collected:
        key = _normalise(item["text"])
        if key in keep and key not in seen:
            seen.add(key)
            lines.append(item)
    return lines, scanned


def ocr_image(path: Path, *, min_confidence: float = 0.5) -> tuple[list[dict], int]:
    _name, run = _load_engine()
    image = frames_mod.read_image(path)
    if image is None:
        return [], 0
    lines = [
        {"t": 0.0, "text": text.strip()}
        for text, confidence in run(image)
        if confidence >= min_confidence and text.strip()
    ]
    texts = set(dedupe([item["text"] for item in lines]))
    return [item for item in lines if item["text"] in texts], 1


def run_all(
    conn: sqlite3.Connection,
    cfg: Config,
    *,
    limit: int | None = None,
    collection: str | None = None,
    interval: float = 1.0,
    images: bool = True,
    redo: bool = False,
    only_flagged: bool = False,
) -> dict:
    rows = db.pending_ocr(conn, collection=collection, include_images=images,
                          redo=redo, only_flagged=only_flagged)
    if limit:
        rows = rows[:limit]
    if not rows:
        return {"read": 0, "empty": 0, "skipped": 0, "failed": 0}

    name, _run = _load_engine()
    print(f"  {name}: {len(rows)} files", file=sys.stderr)
    counts = {"read": 0, "empty": 0, "skipped": 0, "failed": 0}

    for n, row in enumerate(rows, 1):
        path = Path(row["local_path"])
        if not path.exists():
            counts["skipped"] += 1
            continue

        try:
            if row["kind"] == "video":
                lines, scanned = ocr_video(path, interval=interval)
            else:
                lines, scanned = ocr_image(path)
        except Exception as exc:  # noqa: BLE001 - one unreadable file is not fatal
            print(f"  [{n}/{len(rows)}] {row['shortcode']}: {exc}", file=sys.stderr)
            db.save_ocr(conn, media_id=row["id"], shortcode=row["shortcode"],
                        text="", lines=[], frames=0, engine=name, status="error")
            counts["failed"] += 1
            continue

        text = "\n".join(item["text"] for item in lines)
        status = "ok" if text.strip() else "empty"
        db.save_ocr(conn, media_id=row["id"], shortcode=row["shortcode"],
                    text=text, lines=lines, frames=scanned, engine=name,
                    status=status)

        if status == "ok":
            counts["read"] += 1
            print(f"  [{n}/{len(rows)}] {row['shortcode']}: "
                  f"{len(lines)} lines from {scanned} frames", file=sys.stderr)
        else:
            counts["empty"] += 1

    return counts

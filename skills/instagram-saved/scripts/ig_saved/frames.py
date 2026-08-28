"""Frame sampling shared by OCR and description.

Reels put their real content on screen — captions burned into the video, title
cards, place names — so both the text and the visual passes need frames. They
need different ones though: OCR wants every moment the on-screen text changes,
description wants a handful of shots that cover the whole clip.

Decoding is done with PyAV, which faster-whisper already pulls in, so there is
no dependency on a system ffmpeg.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import numpy as np


def _signature(frame: np.ndarray) -> np.ndarray:
    """A tiny grayscale thumbnail, cheap enough to diff on every frame."""
    step_y = max(1, frame.shape[0] // 32)
    step_x = max(1, frame.shape[1] // 32)
    return frame[::step_y, ::step_x].mean(axis=2)


def _difference(a: np.ndarray | None, b: np.ndarray) -> float:
    if a is None:
        return 255.0
    if a.shape != b.shape:
        return 255.0
    return float(np.abs(a - b).mean())


def iter_frames(
    path: Path,
    *,
    interval: float = 1.0,
    min_change: float = 1.0,
    max_frames: int = 240,
) -> Iterator[tuple[float, np.ndarray]]:
    """Yield ``(seconds, rgb_array)`` at ``interval``, skipping static frames.

    On-screen text usually holds for a second or more, so sampling every frame
    would OCR the same caption dozens of times. ``min_change`` drops a sample
    whose thumbnail barely differs from the last one *yielded* — comparing
    against the last yielded frame rather than the previous sample is what
    makes a long static title card cost one OCR call instead of ten.

    ``min_change`` is deliberately low. Overlay text covers a small share of
    the frame, so averaging over a thumbnail dilutes it hard: measured on a
    clip whose caption changes completely, the score moves only 2.9-4.1, while
    genuinely static frames score 0.000-0.001. Anything above ~2 starts
    dropping real text changes; 1.0 sits in the wide gap between the two.
    """
    import av

    last: np.ndarray | None = None
    emitted = 0

    with av.open(str(path)) as container:
        streams = container.streams.video
        if not streams:
            return
        stream = streams[0]
        stream.thread_type = "AUTO"

        next_at = 0.0
        for frame in container.decode(stream):
            when = float(frame.time or 0.0)
            if when + 1e-6 < next_at:
                continue
            next_at = when + interval

            array = frame.to_ndarray(format="rgb24")
            signature = _signature(array)
            if _difference(last, signature) < min_change:
                continue

            last = signature
            emitted += 1
            yield when, array
            if emitted >= max_frames:
                return


def keyframes(
    path: Path, *, count: int = 4, max_scan: int = 60
) -> list[tuple[float, np.ndarray]]:
    """Pick ``count`` frames spread across the clip, preferring distinct ones.

    Used for description, where a handful of representative shots beats a dense
    sample: sending 40 near-identical frames costs 10x and says the same thing.
    """
    sampled = list(iter_frames(path, interval=0.5, min_change=1.5,
                               max_frames=max_scan))
    if len(sampled) < count:
        # Too few distinct shots (a static clip, or one long take): fall back to
        # plain interval sampling so the model still sees the whole thing.
        sampled = list(iter_frames(path, interval=0.5, min_change=0.0,
                                   max_frames=max_scan)) or sampled
    if len(sampled) <= count:
        return sampled

    # Even spread over the distinct frames, so early and late shots both land.
    step = len(sampled) / count
    return [sampled[min(len(sampled) - 1, int(i * step))] for i in range(count)]


def to_jpeg(frame: np.ndarray, *, max_edge: int = 768, quality: int = 80) -> bytes:
    """Encode a frame as JPEG, downscaled — vision cost scales with pixels."""
    import cv2

    height, width = frame.shape[:2]
    scale = min(1.0, max_edge / max(height, width))
    if scale < 1.0:
        frame = cv2.resize(
            frame, (int(width * scale), int(height * scale)),
            interpolation=cv2.INTER_AREA,
        )
    ok, buffer = cv2.imencode(
        ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
        [int(cv2.IMWRITE_JPEG_QUALITY), quality],
    )
    if not ok:
        raise RuntimeError("JPEG encoding failed")
    return buffer.tobytes()


def read_image(path: Path) -> np.ndarray | None:
    import cv2

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        return None
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

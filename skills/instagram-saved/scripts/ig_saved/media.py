"""Download media files off Instagram's CDN.

CDN URLs are pre-signed and expire within hours, so a URL captured during
indexing may already be dead by the time you download. When that happens the
fix is to re-hydrate the post for fresh URLs, not to retry the stale one.
"""

from __future__ import annotations

import sqlite3
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import db
from .config import Config

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

EXT = {"image": ".jpg", "video": ".mp4"}


class Expired(RuntimeError):
    """The pre-signed URL is no longer valid."""


def _fetch(url: str, dest: Path) -> int:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Referer": "https://www.instagram.com/"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            tmp = dest.with_suffix(dest.suffix + ".part")
            size = 0
            with open(tmp, "wb") as fh:
                while chunk := response.read(1 << 16):
                    fh.write(chunk)
                    size += len(chunk)
            tmp.replace(dest)  # atomic, so a killed run leaves no half file
            return size
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 410):
            raise Expired(f"URL expired ({exc.code})") from exc
        raise


def download_all(
    conn: sqlite3.Connection,
    cfg: Config,
    *,
    workers: int = 4,
    limit: int | None = None,
    collection: str | None = None,
) -> dict:
    rows = db.pending_downloads(conn, collection=collection)
    if limit:
        rows = rows[:limit]
    if not rows:
        return {"downloaded": 0, "expired": 0, "failed": 0, "bytes": 0}

    cfg.media_dir.mkdir(parents=True, exist_ok=True)
    counts = {"downloaded": 0, "expired": 0, "failed": 0, "bytes": 0}

    def job(row: sqlite3.Row) -> tuple[sqlite3.Row, Path | None, Exception | None, int]:
        folder = cfg.media_dir / row["shortcode"]
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / f"{row['idx']:02d}{EXT.get(row['kind'], '.bin')}"
        if dest.exists() and dest.stat().st_size > 0:
            return row, dest, None, dest.stat().st_size
        try:
            return row, dest, None, _fetch(row["remote_url"], dest)
        except Exception as exc:  # noqa: BLE001 - reported per item below
            return row, None, exc, 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(job, row) for row in rows]
        for n, future in enumerate(as_completed(futures), 1):
            row, dest, error, size = future.result()

            if error is None and dest is not None:
                db.mark_downloaded(conn, row["id"], str(dest))
                counts["downloaded"] += 1
                counts["bytes"] += size
            elif isinstance(error, Expired):
                counts["expired"] += 1
            else:
                counts["failed"] += 1
                print(f"  {row['shortcode']}[{row['idx']}]: {error}", file=sys.stderr)

            if n % 25 == 0:
                print(f"  {n}/{len(rows)} files", file=sys.stderr)

    if counts["expired"]:
        print(
            f"\n{counts['expired']} URLs had expired. Re-hydrate to refresh them:\n"
            "    ig-saved hydrate --via browser --only-expired",
            file=sys.stderr,
        )
    return counts


def human_bytes(n: int) -> str:
    step = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if step < 1024 or unit == "GB":
            return f"{step:.1f} {unit}"
        step /= 1024
    return f"{step:.1f} GB"

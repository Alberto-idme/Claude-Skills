"""Stage 1a — read the saved list out of Meta's "Download your information" export.

This is the sanctioned path: no session, no automation, nothing that can get an
account actioned. It yields an *index* — permalink, author handle, saved-at
timestamp, and collection name. Captions and media are not in the export for
other people's posts, so hydration still has to happen afterwards.

Request it at: Settings -> Accounts Center -> Your information and permissions
-> Download your information -> JSON.

Only the JSON export is supported. The HTML export is a styled rendering with
no stable structure worth parsing.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Iterator

from ..normalize import Post, walk_export

# Meta has shipped several layouts. Match on filename rather than full path so
# reorganisations of the surrounding folders don't break discovery.
SAVED_FILE_HINTS = ("saved_posts", "saved_collections", "saved")


def _looks_like_saved(name: str) -> bool:
    base = name.rsplit("/", 1)[-1].lower()
    return base.endswith(".json") and any(h in base for h in SAVED_FILE_HINTS)


def _is_collections_file(filename: str) -> bool:
    """A collections file labels each entry with the collection, not the author."""
    return "collection" in filename.rsplit("/", 1)[-1].lower()


def iter_export(path: Path) -> Iterator[Post]:
    """Yield posts from an export .zip or an already-unpacked directory."""
    path = Path(path).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"No export at {path}")

    if path.is_file() and path.suffix.lower() == ".zip":
        yield from _iter_zip(path)
    elif path.is_dir():
        yield from _iter_dir(path)
    elif path.suffix.lower() == ".json":
        yield from _iter_blob(path.name, json.loads(path.read_text("utf-8")))
    else:
        raise ValueError(f"Expected a .zip, a directory, or a .json file: {path}")


def _iter_zip(path: Path) -> Iterator[Post]:
    found = False
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if not _looks_like_saved(name):
                continue
            found = True
            with zf.open(name) as fh:
                payload = json.loads(fh.read().decode("utf-8"))
            yield from _iter_blob(name, payload)
    if not found:
        raise LookupError(_not_found_message(path))


def _iter_dir(path: Path) -> Iterator[Post]:
    found = False
    for candidate in sorted(path.rglob("*.json")):
        if not _looks_like_saved(str(candidate)):
            continue
        found = True
        payload = json.loads(candidate.read_text("utf-8"))
        yield from _iter_blob(candidate.name, payload)
    if not found:
        raise LookupError(_not_found_message(path))


def _iter_blob(filename: str, payload: dict) -> Iterator[Post]:
    yield from walk_export(
        payload, titles_are_collections=_is_collections_file(filename)
    )


def _not_found_message(path: Path) -> str:
    return (
        f"No saved-posts JSON found in {path}.\n"
        "Checked every *.json whose name contains 'saved'.\n\n"
        "Things to check:\n"
        "  - the export was requested in JSON format, not HTML;\n"
        "  - 'Saved posts' was included in the selected information;\n"
        "  - the archive finished downloading (Meta splits large exports into\n"
        "    several zips — saved posts may be in a different part).\n\n"
        "If saved posts genuinely aren't in your export, use the browser source:\n"
        "  ig-saved index --source browser"
    )

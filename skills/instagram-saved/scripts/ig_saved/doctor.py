"""Environment check — says what is missing and exactly how to fix it.

Every failure mode this tool has (no Playwright, no browser binary, no session,
no Whisper backend, no Apify token) produces a different error at a different
stage. `ig-saved doctor` surfaces all of them up front.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
from pathlib import Path

from .config import Config

OK, WARN, BAD = "ok", "--", "XX"


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []
        self.blockers: list[str] = []

    def add(self, mark: str, label: str, detail: str = "", fix: str = "") -> None:
        self.rows.append((mark, label, detail))
        if mark == BAD and fix:
            self.blockers.append(fix)

    def render(self) -> int:
        width = max(len(label) for _, label, _ in self.rows)
        for mark, label, detail in self.rows:
            print(f"  [{mark}] {label:<{width}}  {detail}")

        if self.blockers:
            print("\nTo fix:")
            for fix in dict.fromkeys(self.blockers):  # dedupe, keep order
                for line in fix.splitlines():
                    print(f"    {line}")
            return 1

        print("\nEverything needed is present.")
        return 0


def _find_playwright_browser() -> str | None:
    """Locate a Chromium that Playwright can drive, without launching it."""
    if os.environ.get("IG_SAVED_CHROME"):
        path = Path(os.environ["IG_SAVED_CHROME"])
        return str(path) if path.exists() else None

    roots = [Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""))] if os.environ.get(
        "PLAYWRIGHT_BROWSERS_PATH"
    ) else []
    roots += [
        Path.home() / ".cache/ms-playwright",
        Path.home() / "Library/Caches/ms-playwright",
        Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright",
    ]
    patterns = (
        "chromium-*/chrome-linux/chrome",
        "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
        "chromium-*/chrome-win/chrome.exe",
    )
    for root in roots:
        if not root or not root.exists():
            continue
        for pattern in patterns:
            found = sorted(root.glob(pattern))
            if found:
                return str(found[-1])
    return None


def _system_chrome() -> str | None:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for name in ("google-chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    for path in candidates:
        if Path(path).exists():
            return path
    return None


def _session_cookie(cfg: Config) -> bool | None:
    """Look for an Instagram session in the profile without launching Chrome.

    Returns None when the profile has no cookie database yet.
    """
    for relative in ("Default/Network/Cookies", "Default/Cookies"):
        store = cfg.browser_profile / relative
        if not store.exists():
            continue
        try:
            conn = sqlite3.connect(f"file:{store}?immutable=1", uri=True)
            row = conn.execute(
                "SELECT 1 FROM cookies WHERE host_key LIKE ? AND name = ? LIMIT 1",
                ("%instagram.com", "sessionid"),
            ).fetchone()
            conn.close()
            return row is not None
        except sqlite3.Error:
            return None
    return None


def run(cfg: Config) -> int:
    report = Report()

    version = sys.version_info
    report.add(
        OK if version >= (3, 10) else BAD,
        "python",
        f"{version.major}.{version.minor}.{version.micro}",
        fix="Python 3.10 or newer is required.",
    )

    try:
        import playwright  # noqa: F401

        report.add(OK, "playwright", "installed")
        has_playwright = True
    except ImportError:
        report.add(BAD, "playwright", "not installed",
                   fix="pip install playwright")
        has_playwright = False

    browser = _find_playwright_browser()
    if browser:
        report.add(OK, "browser", browser)
    elif has_playwright:
        fallback = _system_chrome()
        if fallback:
            report.add(
                WARN, "browser", f"none for Playwright; found {fallback}",
                fix=f"playwright install chromium\n"
                    f"# or reuse the Chrome you have:\n"
                    f"export IG_SAVED_CHROME='{fallback}'",
            )
        else:
            report.add(BAD, "browser", "none found",
                       fix="playwright install chromium")
    else:
        report.add(WARN, "browser", "skipped (no playwright)")

    session = _session_cookie(cfg)
    if session is True:
        report.add(OK, "session", f"signed in ({cfg.browser_profile})")
    elif session is False:
        report.add(WARN, "session", "profile exists but no Instagram cookie",
                   fix="ig-saved login")
    else:
        report.add(WARN, "session", "not signed in yet", fix="ig-saved login")

    backend = None
    for module, label in (("faster_whisper", "faster-whisper"),
                          ("whisper", "openai-whisper")):
        try:
            __import__(module)
            backend = label
            break
        except ImportError:
            continue
    if backend:
        detail = f"{backend} (model: {cfg.whisper_model})"
        if backend == "openai-whisper" and not shutil.which("ffmpeg"):
            report.add(WARN, "transcription", f"{detail}; ffmpeg missing",
                       fix="pip install faster-whisper  # needs no ffmpeg")
        else:
            report.add(OK, "transcription", detail)
    else:
        report.add(WARN, "transcription", "no Whisper backend",
                   fix="pip install faster-whisper  # only needed for reels")

    report.add(
        OK if cfg.apify_token else WARN,
        "apify",
        "APIFY_TOKEN set" if cfg.apify_token
        else "no token (only needed for --via apify)",
    )

    if cfg.db_path.exists():
        from . import db as db_mod

        try:
            stats = db_mod.stats(db_mod.connect(cfg.db_path))
            report.add(OK, "database",
                       f"{stats['posts']} posts, {stats['downloaded']} files")
        except sqlite3.Error as exc:
            report.add(BAD, "database", str(exc))
    else:
        report.add(WARN, "database", f"none yet at {cfg.db_path}")

    code = report.render()

    if code == 0 and session is not True:
        print("\nNext: ig-saved login")
    elif code == 0:
        print("\nNext: ig-saved collections")
    return code

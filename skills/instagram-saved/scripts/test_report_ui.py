#!/usr/bin/env python3
"""Drive the generated report in a real browser.

The report is a single local HTML file whose whole value is the controls on
it — sorting, the city and neighbourhood filters, the search box. None of that
can be checked by looking for strings in the markup: a filter that sets
``hidden`` on a card still leaves it on screen if an author rule wins the
cascade over the user agent's ``[hidden]{display:none}``, which is exactly
what ``.card{display:grid}`` did. So this loads the page and looks at what is
actually visible.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ig_saved import db, report as report_mod  # noqa: E402
from ig_saved.config import Config  # noqa: E402
from ig_saved.normalize import Post  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + (f": {detail}" if not ok else ""))
    if not ok:
        failures.append(label)


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


# Saved newest-first, which is the order the collection feed returns.
FIXTURE = [
    # shortcode, title, location, category, taken_at
    ("N1", "Sushi Saito", "Roppongi, Tokyo", "restaurant", 1_700_000_000),
    ("N2", "Fuglen", "Shibuya, Tokyo", "cafe", 1_500_000_000),
    ("N3", "Ichiran", "Shibuya, Tokyo", "restaurant", 1_600_000_000),
    ("N4", "Gion Walk", "Gion, Kyoto", "sight", 1_400_000_000),
    ("N5", "Nowhere Bar", "Tokyo", "bar", None),
]


def build_page(tmp: str) -> Path:
    cfg = Config(root=Path(tmp))
    cfg.ensure_dirs()
    conn = db.connect(cfg.db_path)
    db.upsert_posts(
        conn,
        [Post(shortcode=code, url=f"https://www.instagram.com/p/{code}/",
              collection="japan", caption=title, taken_at=taken)
         for code, title, _loc, _cat, taken in FIXTURE],
        ordered=True,
    )
    for code, title, location, category, _taken in FIXTURE:
        db.save_entry(conn, shortcode=code, title=title, category=category,
                      location=location, summary=f"{title} summary",
                      highlights=[], action="visit", practical="",
                      confidence="high", needs_review=False, sources=["caption"],
                      model="claude-opus-5")
    out = report_mod.build(conn, cfg, Path(tmp) / "r", collection="japan",
                           formats=("html",))
    return out["html"]


def visible_titles(page) -> list[str]:
    """Titles of cards actually painted, in the order they appear."""
    return page.eval_on_selector_all(
        ".card",
        "els=>els.filter(e=>getComputedStyle(e).display!=='none')"
        ".map(e=>e.querySelector('.title').textContent.trim())",
    )


def run() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP: playwright not installed (pip install playwright)")
        return 0

    chrome = find_chrome()
    if not chrome:
        print("SKIP: no chromium found (playwright install chromium)")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        target = build_page(tmp)

        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chrome)
            page = browser.new_page()
            page.goto(target.as_uri())

            check("all entries render", len(visible_titles(page)) == 5,
                  str(visible_titles(page)))

            # -- sorting ---------------------------------------------------
            page.select_option("#sort", "saved:asc")
            order = visible_titles(page)
            check("recently saved first",
                  order == ["Sushi Saito", "Fuglen", "Ichiran", "Gion Walk",
                            "Nowhere Bar"], str(order))

            page.select_option("#sort", "saved:desc")
            check("saved earliest first",
                  visible_titles(page)[0] == "Nowhere Bar",
                  str(visible_titles(page)))

            page.select_option("#sort", "taken:desc")
            order = visible_titles(page)
            check("newest post first",
                  order[:4] == ["Sushi Saito", "Ichiran", "Fuglen", "Gion Walk"],
                  str(order))
            check("undated entry sinks to the bottom",
                  order[-1] == "Nowhere Bar", str(order))

            page.select_option("#sort", "taken:asc")
            order = visible_titles(page)
            check("oldest post first", order[0] == "Gion Walk", str(order))
            check("undated entry still sinks, not flipped to the top",
                  order[-1] == "Nowhere Bar", str(order))

            check("group headings hidden while date-sorted",
                  page.eval_on_selector_all(
                      ".ghdr",
                      "els=>els.every(e=>getComputedStyle(e).display==='none')"))

            page.select_option("#sort", "cat")
            check("category grouping restores headings",
                  page.eval_on_selector_all(
                      ".ghdr",
                      "els=>els.some(e=>getComputedStyle(e).display!=='none')"))
            order = visible_titles(page)
            check("category order is restaurant, cafe, bar, sight",
                  order == ["Sushi Saito", "Ichiran", "Fuglen", "Nowhere Bar",
                            "Gion Walk"], str(order))

            # -- neighbourhood filter --------------------------------------
            page.select_option("#area", "Shibuya")
            shown = visible_titles(page)
            check("area filter actually hides the other cards",
                  sorted(shown) == ["Fuglen", "Ichiran"], str(shown))

            page.select_option("#area", "")
            page.select_option("#reg", "Kyoto")
            shown = visible_titles(page)
            check("city filter narrows to one city", shown == ["Gion Walk"],
                  str(shown))
            check("area options narrow to the chosen city",
                  page.eval_on_selector_all(
                      "#area option",
                      "els=>els.filter(e=>!e.disabled&&e.value).map(e=>e.value)"
                  ) == ["Gion"],
                  str(page.eval_on_selector_all(
                      "#area option",
                      "els=>els.filter(e=>!e.disabled&&e.value).map(e=>e.value)")))

            # Picking Shibuya then switching to Kyoto must not leave a filter
            # combination that can never match anything.
            page.select_option("#reg", "Tokyo")
            page.select_option("#area", "Shibuya")
            page.select_option("#reg", "Kyoto")
            check("a stale neighbourhood clears when the city changes",
                  visible_titles(page) == ["Gion Walk"],
                  str(visible_titles(page)))

            page.select_option("#reg", "")
            check("clearing filters restores everything",
                  len(visible_titles(page)) == 5)

            # -- search ----------------------------------------------------
            page.fill("#q", "ichiran")
            check("search hides non-matches", visible_titles(page) == ["Ichiran"],
                  str(visible_titles(page)))
            check("tally reports the filtered count",
                  "1 of 5" in page.text_content("#tally"),
                  page.text_content("#tally"))

            page.fill("#q", "zzzz")
            check("empty state appears when nothing matches",
                  page.eval_on_selector(
                      "#none", "e=>getComputedStyle(e).display!=='none'"))

            browser.close()

    total = 18
    print(f"\n{total - len(failures)}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(run())

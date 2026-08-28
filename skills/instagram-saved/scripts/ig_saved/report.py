"""Render the triage records as something you can actually work through.

Three outputs from the same rows: a self-contained HTML page for browsing and
deciding, a CSV for spreadsheet work, and Markdown for pasting into a doc.

The HTML is deliberately one local file with no dependencies — it opens from
disk, references the already-downloaded media by relative path, and is
overwritten in place on every re-run.
"""

from __future__ import annotations

import csv
import html
import json
import sqlite3
from collections import Counter
from datetime import date
from pathlib import Path

from . import db
from .config import Config

CATEGORY_ORDER = ["restaurant", "cafe", "bar", "hotel", "sight", "shop",
                  "activity", "recipe", "tip", "guide", "product", "other"]


def _rows(conn: sqlite3.Connection, collection: str | None) -> list[dict]:
    out = []
    for row in db.entries(conn, collection=collection):
        record = dict(row)
        record["highlights"] = json.loads(record.get("highlights") or "[]")
        record["sources"] = json.loads(record.get("sources") or "[]")
        record["region"] = region_of(record.get("location"))
        out.append(record)
    return out


def _thumbnail(cfg: Config, conn: sqlite3.Connection, shortcode: str,
               relative_to: Path) -> str | None:
    row = conn.execute(
        "SELECT local_path FROM media WHERE shortcode = ? AND kind = 'image' "
        "AND local_path IS NOT NULL ORDER BY idx LIMIT 1", (shortcode,)
    ).fetchone()
    if row is None:
        return None
    try:
        import os

        return os.path.relpath(row["local_path"], relative_to)
    except ValueError:
        return row["local_path"]


# ---------------------------------------------------------------------------
# CSV / Markdown
# ---------------------------------------------------------------------------

CSV_FIELDS = ["category", "title", "location", "region", "summary", "action",
              "practical", "highlights", "confidence", "needs_review",
              "review_reason", "collections", "author_username", "url", "sources"]


def region_of(location: str | None) -> str:
    """The coarse place a location belongs to, for filtering.

    Locations arrive free-text ("Shibuya, Tokyo", "Otemachi, Tokyo", "Ojai,
    California"). The trailing component is the city or region, which groups
    the first two together and makes an out-of-place entry obvious — a saved
    collection is a folder, not a guarantee about geography.
    """
    parts = [p.strip() for p in (location or "").split(",") if p.strip()]
    return parts[-1] if parts else ""


def write_csv(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            flat = dict(row)
            flat["highlights"] = " · ".join(row["highlights"])
            flat["sources"] = ",".join(row["sources"])
            flat["needs_review"] = "yes" if row["needs_review"] else ""
            flat["review_reason"] = row.get("review_reason") or ""
            writer.writerow(flat)


def write_markdown(rows: list[dict], path: Path, scope: str) -> None:
    lines = [f"# Saved posts — {scope}", "",
             f"{len(rows)} entries · generated {date.today().isoformat()}", ""]

    by_category: dict[str, list[dict]] = {}
    for row in rows:
        by_category.setdefault(row["category"] or "other", []).append(row)

    for category in sorted(by_category, key=_category_rank):
        group = by_category[category]
        lines += [f"## {category.replace('_', ' ').title()} ({len(group)})", "",
                  "| | Place | Where | What | Do | Notes |",
                  "|---|---|---|---|---|---|"]
        for row in group:
            flag = "⚠️" if row["needs_review"] else ""
            title = f"[{_md(row['title'] or '—')}]({row['url']})"
            notes = " · ".join(filter(None, [
                _md(row["practical"]), _md(" · ".join(row["highlights"][:2])),
                _md(row.get("review_reason")) if row["needs_review"] else ""]))
            lines.append(
                f"| {flag} | {title} | {_md(row['location'])} | "
                f"{_md(row['summary'])} | {row['action'].replace('_', ' ')} | "
                f"{notes} |"
            )
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def _md(text: str | None) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def _category_rank(name: str) -> tuple[int, str]:
    return (CATEGORY_ORDER.index(name) if name in CATEGORY_ORDER
            else len(CATEGORY_ORDER), name)


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

_CSS = """
:root{color-scheme:light dark;
--bg:#fbfaf9;--fg:#1c1b19;--muted:#6b6864;--line:#e3e0dc;--card:#fff;
--accent:#7c5cff;--warn:#b45309;--chip:#f1eeea}
@media (prefers-color-scheme:dark){:root{
--bg:#16151a;--fg:#eceaf0;--muted:#9a96a3;--line:#2c2a33;--card:#1e1d24;
--accent:#a691ff;--warn:#f0b429;--chip:#26242d}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:28px 24px 16px;border-bottom:1px solid var(--line)}
h1{margin:0 0 4px;font-size:22px;letter-spacing:-.01em}
.sub{color:var(--muted);font-size:13px}
.controls{display:flex;flex-wrap:wrap;gap:8px;padding:14px 24px;
position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);z-index:5}
input[type=search],select{padding:7px 10px;border:1px solid var(--line);
border-radius:8px;background:var(--card);color:var(--fg);font-size:14px}
input[type=search]{flex:1;min-width:200px}
label.toggle{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--muted)}
main{padding:8px 24px 60px}
h2{font-size:14px;text-transform:uppercase;letter-spacing:.06em;
color:var(--muted);margin:26px 0 10px;font-weight:600}
.card{display:grid;grid-template-columns:64px 1fr auto;gap:14px;padding:14px;
border:1px solid var(--line);border-radius:12px;background:var(--card);margin-bottom:8px}
.card.review{border-left:3px solid var(--warn)}
.thumb{width:64px;height:64px;border-radius:8px;object-fit:cover;background:var(--chip)}
.no-thumb{width:64px;height:64px;border-radius:8px;background:var(--chip)}
.title{font-weight:600;font-size:15px;margin:0 0 2px}
.title a{color:inherit;text-decoration:none}
.title a:hover{color:var(--accent);text-decoration:underline}
.where{color:var(--muted);font-size:13px}
.summary{margin:6px 0 0}
.hl{margin:6px 0 0;padding-left:18px;color:var(--muted);font-size:13.5px}
.hl li{margin:1px 0}
.practical{margin-top:6px;font-size:13px;color:var(--muted)}
.reason{margin-top:4px;font-size:12.5px;color:var(--warn)}
.meta{display:flex;flex-direction:column;align-items:flex-end;gap:6px;
font-size:12px;color:var(--muted);white-space:nowrap}
.chip{background:var(--chip);border-radius:999px;padding:2px 9px;font-size:12px}
.chip.act{background:color-mix(in srgb,var(--accent) 18%,transparent);
color:var(--accent);font-weight:600}
.chip.warn{background:color-mix(in srgb,var(--warn) 20%,transparent);color:var(--warn)}
.empty{color:var(--muted);padding:40px 0;text-align:center}
.count{color:var(--muted);font-weight:400}
@media(max-width:640px){.card{grid-template-columns:48px 1fr}
.meta{grid-column:2;flex-direction:row;flex-wrap:wrap;align-items:center}
.thumb,.no-thumb{width:48px;height:48px}}
"""

_JS = """
const cards=[...document.querySelectorAll('.card')];
const q=document.getElementById('q'),cat=document.getElementById('cat'),
act=document.getElementById('act'),coll=document.getElementById('coll'),
reg=document.getElementById('reg'),
rev=document.getElementById('rev'),tally=document.getElementById('tally');
function apply(){
  const t=q.value.toLowerCase().trim();
  let shown=0;
  for(const c of cards){
    const ok=(!t||c.dataset.text.includes(t))
      &&(!cat.value||c.dataset.cat===cat.value)
      &&(!act.value||c.dataset.act===act.value)
      &&(!coll.value||(c.dataset.coll||'').split(', ').includes(coll.value))
      &&(!reg.value||c.dataset.region===reg.value)
      &&(!rev.checked||c.dataset.review==='1');
    c.hidden=!ok; if(ok)shown++;
  }
  for(const s of document.querySelectorAll('section')){
    const any=[...s.querySelectorAll('.card')].some(c=>!c.hidden);
    s.hidden=!any;
    const n=s.querySelector('.count');
    if(n)n.textContent='('+[...s.querySelectorAll('.card')].filter(c=>!c.hidden).length+')';
  }
  tally.textContent=shown+' of '+cards.length+' shown';
  document.getElementById('none').hidden=shown>0;
}
[q,cat,act,coll,reg,rev].forEach(el=>el.addEventListener('input',apply));
apply();
"""


def _esc(value) -> str:
    return html.escape(str(value or ""))


def write_html(rows: list[dict], path: Path, scope: str,
               thumbs: dict[str, str | None]) -> None:
    by_category: dict[str, list[dict]] = {}
    collections: set[str] = set()
    for row in rows:
        by_category.setdefault(row["category"] or "other", []).append(row)
        for name in (row.get("collections") or "").split(", "):
            if name:
                collections.add(name)

    actions = sorted({r["action"] for r in rows if r["action"]})
    regions = sorted({r["region"] for r in rows if r["region"]})
    review_count = sum(1 for r in rows if r["needs_review"])
    counts = Counter(r["category"] or "other" for r in rows)

    def options(values, label):
        opts = "".join(f'<option value="{_esc(v)}">{_esc(v)}</option>'
                       for v in values)
        return f'<option value="">{label}</option>{opts}'

    sections = []
    for category in sorted(by_category, key=_category_rank):
        group = by_category[category]
        cards = []
        for row in group:
            haystack = " ".join(filter(None, [
                row["title"], row["location"], row["summary"], row["practical"],
                " ".join(row["highlights"]), row["author_username"],
                row.get("collections") or "",
            ])).lower()

            thumb = thumbs.get(row["shortcode"])
            thumb_html = (f'<img class="thumb" loading="lazy" src="{_esc(thumb)}" alt="">'
                          if thumb else '<div class="no-thumb"></div>')

            highlights = "".join(f"<li>{_esc(h)}</li>" for h in row["highlights"])
            practical = (f'<div class="practical">{_esc(row["practical"])}</div>'
                         if row["practical"] else "")
            reason = row.get("review_reason") or ""
            if row["needs_review"] and reason:
                practical += (f'<div class="reason">needs checking: '
                              f'{_esc(reason)}</div>')
            chips = [f'<span class="chip act">{_esc(row["action"].replace("_", " "))}</span>']
            if row["needs_review"]:
                chips.append('<span class="chip warn">check</span>')
            if row.get("collections"):
                chips.append(f'<span class="chip">{_esc(row["collections"])}</span>')
            chips.append(f'<span class="chip">{_esc(row["confidence"])}</span>')

            cards.append(f"""
    <article class="card{' review' if row['needs_review'] else ''}"
      data-cat="{_esc(category)}" data-act="{_esc(row['action'])}"
      data-coll="{_esc(row.get('collections'))}"
      data-region="{_esc(row['region'])}"
      data-review="{1 if row['needs_review'] else 0}"
      data-text="{_esc(haystack)}">
      {thumb_html}
      <div>
        <p class="title"><a href="{_esc(row['url'])}" target="_blank" rel="noopener">
          {_esc(row['title'] or row['summary'][:60] or row['shortcode'])}</a></p>
        <div class="where">{_esc(row['location'])}{
          ' · @' + _esc(row['author_username']) if row['author_username'] else ''}</div>
        <p class="summary">{_esc(row['summary'])}</p>
        {f'<ul class="hl">{highlights}</ul>' if highlights else ''}
        {practical}
      </div>
      <div class="meta">{''.join(chips)}</div>
    </article>""")

        sections.append(
            f'<section><h2>{_esc(category.replace("_", " "))} '
            f'<span class="count">({len(group)})</span></h2>'
            + "".join(cards) + "</section>"
        )

    summary = " · ".join(f"{counts[c]} {c}" for c in
                         sorted(counts, key=_category_rank))

    path.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Saved posts — {_esc(scope)}</title>
<style>{_CSS}</style></head><body>
<header>
  <h1>Saved posts — {_esc(scope)}</h1>
  <div class="sub">{len(rows)} entries · {_esc(summary)}
  {f' · {review_count} to check' if review_count else ''}
  · generated {date.today().isoformat()}</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter by name, place, note…">
  <select id="cat">{options(sorted(by_category, key=_category_rank), 'All categories')}</select>
  <select id="act">{options(actions, 'Any action')}</select>
  <select id="reg">{options(regions, 'Anywhere')}</select>
  <select id="coll">{options(sorted(collections), 'All collections')}</select>
  <label class="toggle"><input type="checkbox" id="rev"> needs checking</label>
  <span class="sub" id="tally"></span>
</div>
<main>{''.join(sections)}
<p class="empty" id="none" hidden>Nothing matches those filters.</p>
</main>
<script>{_JS}</script></body></html>
""", encoding="utf-8")


def build(
    conn: sqlite3.Connection, cfg: Config, out_dir: Path,
    *, collection: str | None = None, formats: tuple[str, ...] = ("html", "csv", "md"),
) -> dict:
    rows = _rows(conn, collection)
    out_dir.mkdir(parents=True, exist_ok=True)
    scope = collection or "all collections"
    written = {}

    if not rows:
        return {}

    if "html" in formats:
        thumbs = {r["shortcode"]: _thumbnail(cfg, conn, r["shortcode"], out_dir)
                  for r in rows}
        target = out_dir / "report.html"
        write_html(rows, target, scope, thumbs)
        written["html"] = target
    if "csv" in formats:
        target = out_dir / "report.csv"
        write_csv(rows, target)
        written["csv"] = target
    if "md" in formats:
        target = out_dir / "report.md"
        write_markdown(rows, target, scope)
        written["md"] = target

    written["count"] = len(rows)
    return written

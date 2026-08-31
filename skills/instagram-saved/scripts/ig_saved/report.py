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
        record["places"] = db.places_for(conn, record["shortcode"])
        record["region"] = region_of(record.get("location"))
        record["area"] = area_of(record.get("location"))
        record["date_label"] = date_label(record)
        record["link"], record["link_kind"] = source_link(record)
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

CSV_FIELDS = ["category", "title", "location", "area", "region", "summary",
              "action", "practical", "highlights", "confidence", "needs_review",
              "review_reason", "review_kind", "collections", "author_username",
              "shortcode", "saved_rank", "date_label", "link_kind", "link",
              "sources"]


def source_link(row: dict) -> tuple[str, str]:
    """Permalink back to the original post, and what to call it.

    Everything is stored as /p/<code>/, which Instagram accepts for any media
    type, but a reel opened through /reel/ lands in the player rather than the
    grid — worth getting right when the whole point of the link is to go back
    and watch the thing.
    """
    shortcode = row.get("shortcode") or ""
    is_reel = (row.get("product_type") == "clips"
               or row.get("media_type") == "video")
    url = row.get("url") or ""
    if is_reel and shortcode:
        url = f"https://www.instagram.com/reel/{shortcode}/"
    return url, ("reel" if is_reel else "post")


def _location_parts(location: str | None) -> list[str]:
    return [p.strip() for p in (location or "").split(",") if p.strip()]


def region_of(location: str | None) -> str:
    """The coarse place a location belongs to, for filtering.

    Locations arrive free-text ("Shibuya, Tokyo", "Otemachi, Tokyo", "Ojai,
    California"). The trailing component is the city or region, which groups
    the first two together and makes an out-of-place entry obvious — a saved
    collection is a folder, not a guarantee about geography.
    """
    parts = _location_parts(location)
    return parts[-1] if parts else ""


def area_of(location: str | None) -> str:
    """The neighbourhood inside that region, when one was stated.

    "Shibuya, Tokyo" is a neighbourhood in a city; a bare "Tokyo" is only the
    city. Returning the leading component regardless would make every city its
    own neighbourhood and fill the filter with entries that mean nothing, so a
    single-part location has no area at all.
    """
    parts = _location_parts(location)
    return parts[0] if len(parts) > 1 else ""


def date_label(row: dict) -> str:
    """When the post was published, as something readable.

    Save time is the more useful order but Instagram's private API never
    returns it, so the visible date is the post's own — shown so that a
    date-sorted list can be checked against something.
    """
    taken = row.get("taken_at")
    if not taken:
        return ""
    try:
        return date.fromtimestamp(int(taken)).strftime("%b %Y")
    except (ValueError, OSError, OverflowError):
        return ""


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


PLACE_FIELDS = ["name", "kind", "locality", "address", "website", "maps_url",
                "phone", "verified", "status", "note", "shortcode", "post_url"]


def write_places_csv(rows: list[dict], path: Path) -> int:
    """One row per place, which is the grain you actually work a trip in.

    Separate from report.csv because the two have different shapes: a post with
    eight restaurants is one report row and eight place rows, and flattening
    them into one sheet loses whichever grain you needed.
    """
    written = 0
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=PLACE_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            for place in row.get("places") or []:
                flat = dict(place)
                flat["shortcode"] = row["shortcode"]
                flat["post_url"] = row.get("link") or row.get("url") or ""
                flat["verified"] = "yes" if place.get("verified") else ""
                writer.writerow(flat)
                written += 1
    return written


def write_markdown(rows: list[dict], path: Path, scope: str) -> None:
    lines = [f"# Saved posts — {scope}", "",
             f"{len(rows)} entries · generated {date.today().isoformat()}", ""]

    by_category: dict[str, list[dict]] = {}
    for row in rows:
        by_category.setdefault(row["category"] or "other", []).append(row)

    for category in sorted(by_category, key=_category_rank):
        group = by_category[category]
        lines += [f"## {category.replace('_', ' ').title()} ({len(group)})", "",
                  "| | Place | Where | What | Do | Notes | Source |",
                  "|---|---|---|---|---|---|---|"]
        for row in group:
            flag = "⚠️" if row["needs_review"] else ""
            title = f"[{_md(row['title'] or '—')}]({row['url']})"
            notes = " · ".join(filter(None, [
                _md(row["practical"]), _md(" · ".join(row["highlights"][:2])),
                _md(row.get("review_reason")) if row["needs_review"] else ""]))
            lines.append(
                f"| {flag} | {title} | {_md(row['location'])} | "
                f"{_md(row['summary'])} | {row['action'].replace('_', ' ')} | "
                f"{notes} | [{row['link_kind']}]({row['link']}) |"
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
.src{margin-top:8px;font-size:12.5px}
.src a{color:var(--accent);text-decoration:none}
.src a:hover{text-decoration:underline}
.src code{font:inherit;color:var(--muted)}
.places{margin:8px 0 0;padding:8px 10px;border-left:2px solid var(--line);
font-size:13px;display:grid;gap:6px}
.place strong{font-weight:600}
.place .addr{color:var(--muted)}
.place .links{font-size:12.5px}
.place .links a{color:var(--accent);text-decoration:none;margin-right:10px}
.place .links a:hover{text-decoration:underline}
.place .unver{color:var(--warn);font-size:12px}
.place .none{color:var(--muted);font-style:italic}
.reason{margin-top:4px;font-size:12.5px;color:var(--warn)}
.meta{display:flex;flex-direction:column;align-items:flex-end;gap:6px;
font-size:12px;color:var(--muted);white-space:nowrap}
.chip{background:var(--chip);border-radius:999px;padding:2px 9px;font-size:12px}
.chip.act{background:color-mix(in srgb,var(--accent) 18%,transparent);
color:var(--accent);font-weight:600}
.chip.warn{background:color-mix(in srgb,var(--warn) 20%,transparent);color:var(--warn)}
.empty{color:var(--muted);padding:40px 0;text-align:center}
.count{color:var(--muted);font-weight:400}
.when{color:var(--muted)}
/* `.card` sets display:grid, and an author rule beats the user agent's
   [hidden]{display:none} — without this every filtered-out card stays on
   screen. Same for the group headings, which are h2. */
[hidden]{display:none!important}
@media(max-width:640px){.card{grid-template-columns:48px 1fr}
.meta{grid-column:2;flex-direction:row;flex-wrap:wrap;align-items:center}
.thumb,.no-thumb{width:48px;height:48px}}
"""

_JS = """
const list=document.getElementById('list');
const cards=[...list.querySelectorAll('.card')];
const heads=[...list.querySelectorAll('.ghdr')];
const q=document.getElementById('q'),cat=document.getElementById('cat'),
act=document.getElementById('act'),coll=document.getElementById('coll'),
reg=document.getElementById('reg'),area=document.getElementById('area'),
sort=document.getElementById('sort'),
rev=document.getElementById('rev'),tally=document.getElementById('tally');

// An empty data-* attribute means "no value", which is not the same as 0 —
// rank 0 is the most recently saved post in the collection.
function num(card,key){
  const v=card.dataset[key];
  return v===undefined||v===''?null:Number(v);
}

// Category grouping and date order are different shapes, so sorting rebuilds
// the list rather than toggling a class: headings only make sense while the
// cards under them are still grouped.
function order(){
  const mode=sort.value;
  if(mode==='cat'){
    const seen=new Set();
    for(const c of cards){
      const name=c.dataset.cat;
      if(!seen.has(name)){
        seen.add(name);
        const h=heads.find(h=>h.dataset.cat===name);
        if(h)list.appendChild(h);
      }
      list.appendChild(c);
    }
    return;
  }
  for(const h of heads)h.hidden=true;
  const [key,dir]=mode.split(':');
  const sorted=[...cards].sort((a,b)=>{
    const x=num(a,key),y=num(b,key);
    // Undated entries sort to the bottom either way, rather than pretending
    // to be the oldest or the newest thing in the collection.
    if(x===null&&y===null)return Number(a.dataset.order)-Number(b.dataset.order);
    if(x===null)return 1;
    if(y===null)return -1;
    return dir==='asc'?x-y:y-x;
  });
  for(const c of sorted)list.appendChild(c);
}

// Neighbourhoods only exist inside a city, so picking a city narrows them.
// Offering all of them at once mostly offers combinations that match nothing.
function narrowAreas(){
  let valid=false;
  for(const o of area.options){
    if(!o.value){o.hidden=false;o.disabled=false;continue;}
    const inRegion=!reg.value
      ||(o.dataset.region||'').split('|').includes(reg.value);
    o.hidden=!inRegion;
    o.disabled=!inRegion;
    if(inRegion&&o.value===area.value)valid=true;
  }
  if(area.value&&!valid)area.value='';
}

function apply(){
  narrowAreas();
  order();
  const t=q.value.toLowerCase().trim();
  let shown=0;
  for(const c of cards){
    const ok=(!t||c.dataset.text.includes(t))
      &&(!cat.value||c.dataset.cat===cat.value)
      &&(!act.value||c.dataset.act===act.value)
      &&(!coll.value||(c.dataset.coll||'').split(', ').includes(coll.value))
      &&(!reg.value||c.dataset.region===reg.value)
      &&(!area.value||c.dataset.area===area.value)
      &&(!rev.checked||c.dataset.kind==='fixable');
    c.hidden=!ok; if(ok)shown++;
  }
  if(sort.value==='cat'){
    for(const h of heads){
      const n=cards.filter(c=>c.dataset.cat===h.dataset.cat&&!c.hidden).length;
      h.hidden=!n;
      const label=h.querySelector('.count');
      if(label)label.textContent='('+n+')';
    }
  }
  tally.textContent=shown+' of '+cards.length+' shown';
  document.getElementById('none').hidden=shown>0;
}
[q,cat,act,coll,reg,area,sort,rev].forEach(el=>el.addEventListener('input',apply));
apply();
"""


def _esc(value) -> str:
    return html.escape(str(value or ""))


def _places_block(places: list[dict]) -> str:
    """The named places under an entry, with whatever the lookup found.

    A place with no address is still shown. It is the difference between "this
    post named somewhere I could not pin down" and "this post named nowhere",
    and hiding the first would quietly turn a failed lookup into a missing place.
    """
    if not places:
        return ""

    items = []
    for place in places:
        bits = [f'<strong>{_esc(place.get("name"))}</strong>']
        if place.get("locality"):
            bits.append(f'<span class="addr"> · {_esc(place["locality"])}</span>')

        lines = ["".join(bits)]
        if place.get("address"):
            lines.append(f'<div class="addr">{_esc(place["address"])}</div>')
        elif place.get("status") == "not_found":
            note = place.get("note") or "no address found"
            lines.append(f'<div class="none">{_esc(note)}</div>')
        elif place.get("status") == "error":
            lines.append('<div class="none">lookup failed — rerun `enrich '
                         '--retry-failed`</div>')
        else:
            lines.append('<div class="none">not looked up yet</div>')

        links = []
        if place.get("website"):
            links.append(f'<a href="{_esc(place["website"])}" target="_blank" '
                         f'rel="noopener">website</a>')
        if place.get("maps_url"):
            links.append(f'<a href="{_esc(place["maps_url"])}" target="_blank" '
                         f'rel="noopener">map</a>')
        if place.get("source_url"):
            links.append(f'<a href="{_esc(place["source_url"])}" target="_blank" '
                         f'rel="noopener">source</a>')
        if place.get("phone"):
            links.append(f'<span class="addr">{_esc(place["phone"])}</span>')
        if links:
            lines.append(f'<div class="links">{"".join(links)}</div>')

        # An address is only as good as the page it came from.
        if place.get("address") and not place.get("verified"):
            lines.append('<div class="unver">citation not verified — check '
                         'the source before relying on this</div>')

        items.append(f'<div class="place">{"".join(lines)}</div>')

    return f'<div class="places">{"".join(items)}</div>'


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

    # An area name can repeat across cities (every country has a "Centro"), so
    # each option carries every region it belongs to rather than assuming one.
    area_regions: dict[str, set[str]] = {}
    for row in rows:
        if row.get("area"):
            area_regions.setdefault(row["area"], set()).add(row["region"])

    has_rank = any(r.get("saved_rank") is not None for r in rows)
    has_taken = any(r.get("taken_at") for r in rows)

    def options(values, label):
        opts = "".join(f'<option value="{_esc(v)}">{_esc(v)}</option>'
                       for v in values)
        return f'<option value="">{label}</option>{opts}'

    def area_options() -> str:
        opts = "".join(
            f'<option value="{_esc(name)}" '
            f'data-region="{_esc("|".join(sorted(area_regions[name])))}">'
            f'{_esc(name)}</option>'
            for name in sorted(area_regions)
        )
        return f'<option value="">Any area</option>{opts}'

    def sort_options() -> str:
        # Only offer an order the data can actually produce.
        opts = ['<option value="cat">Group by category</option>']
        if has_rank:
            opts += ['<option value="saved:asc">Recently saved</option>',
                     '<option value="saved:desc">Saved earliest</option>']
        if has_taken:
            opts += ['<option value="taken:desc">Newest post</option>',
                     '<option value="taken:asc">Oldest post</option>']
        return "".join(opts)

    ordinal = 0
    blocks = []
    for category in sorted(by_category, key=_category_rank):
        group = by_category[category]
        blocks.append(
            f'<h2 class="ghdr" data-cat="{_esc(category)}">'
            f'{_esc(category.replace("_", " "))} '
            f'<span class="count">({len(group)})</span></h2>'
        )
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
                kind = row.get("review_kind") or ""
                label = "recheck" if kind == "fixable" else (
                    "source limit" if kind == "source_limit" else "check")
                chips.append(f'<span class="chip warn">{_esc(label)}</span>')
            if row.get("collections"):
                chips.append(f'<span class="chip">{_esc(row["collections"])}</span>')
            chips.append(f'<span class="chip">{_esc(row["confidence"])}</span>')

            places_html = _places_block(row.get("places") or [])
            rank = row.get("saved_rank")
            taken = row.get("taken_at")
            when = row.get("date_label") or ""
            where = " · ".join(filter(None, [
                _esc(row["location"]),
                "@" + _esc(row["author_username"]) if row["author_username"] else "",
            ]))
            if when:
                where += f'<span class="when"> · {_esc(when)}</span>'

            blocks.append(f"""
    <article class="card{' review' if row['needs_review'] else ''}"
      data-cat="{_esc(category)}" data-act="{_esc(row['action'])}"
      data-coll="{_esc(row.get('collections'))}"
      data-region="{_esc(row['region'])}"
      data-area="{_esc(row['area'])}"
      data-order="{ordinal}"
      data-saved="{rank if rank is not None else ''}"
      data-taken="{taken or ''}"
      data-review="{1 if row['needs_review'] else 0}"
      data-kind="{_esc(row.get('review_kind'))}"
      data-text="{_esc(haystack)}">
      {thumb_html}
      <div>
        <p class="title"><a href="{_esc(row['url'])}" target="_blank" rel="noopener">
          {_esc(row['title'] or row['summary'][:60] or row['shortcode'])}</a></p>
        <div class="where">{where}</div>
        <p class="summary">{_esc(row['summary'])}</p>
        {f'<ul class="hl">{highlights}</ul>' if highlights else ''}
        {practical}
        {places_html}
        <div class="src"><a href="{_esc(row['link'])}" target="_blank"
          rel="noopener">↗ open {_esc(row['link_kind'])} on Instagram</a>
          <code> · {_esc(row['shortcode'])}</code></div>
      </div>
      <div class="meta">{''.join(chips)}</div>
    </article>""")
            ordinal += 1

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
  <select id="sort">{sort_options()}</select>
  <select id="cat">{options(sorted(by_category, key=_category_rank), 'All categories')}</select>
  <select id="act">{options(actions, 'Any action')}</select>
  <select id="reg">{options(regions, 'Any city')}</select>
  <select id="area">{area_options()}</select>
  <select id="coll">{options(sorted(collections), 'All collections')}</select>
  <label class="toggle"><input type="checkbox" id="rev"> worth another pass</label>
  <span class="sub" id="tally"></span>
</div>
<main id="list">{''.join(blocks)}</main>
<p class="empty" id="none" hidden>Nothing matches those filters.</p>
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
        if any(r.get("places") for r in rows):
            target = out_dir / "places.csv"
            write_places_csv(rows, target)
            written["places"] = target
    if "md" in formats:
        target = out_dir / "report.md"
        write_markdown(rows, target, scope)
        written["md"] = target

    written["count"] = len(rows)
    return written

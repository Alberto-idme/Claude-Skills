"""Command line entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import db, media as media_mod, transcribe as transcribe_mod
from .config import Config
from .normalize import parse_collection_url


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _config(args: argparse.Namespace) -> Config:
    cfg = Config()
    if getattr(args, "home", None):
        cfg.root = Path(args.home).expanduser()
    for attr in ("apify_token", "apify_actor", "apify_url_field", "whisper_model"):
        value = getattr(args, attr, None)
        if value:
            setattr(cfg, attr, value)
    if getattr(args, "slow", False):
        cfg.min_delay, cfg.max_delay = 4.0, 9.0
    cfg.ensure_dirs()
    return cfg


def _collection_name(value: str | None) -> str | None:
    """Resolve whatever the user passed into the name stored on posts.

    `index --collection <url>` stamps posts with the URL's slug, so the later
    stages have to scope by that same slug, not the raw URL.
    """
    if not value:
        return None
    parsed = parse_collection_url(value)
    if parsed:
        _owner, slug, collection_id = parsed
        return slug or collection_id
    return value


def _expired_shortcodes(conn) -> list[str]:
    return [
        r["shortcode"]
        for r in conn.execute(
            """
            SELECT DISTINCT shortcode FROM media
            WHERE local_path IS NULL AND remote_url IS NOT NULL
            """
        )
    ]


def _session(cfg: Config, headless: bool = False):
    from .sources.browser import BrowserSession

    return BrowserSession(cfg, headless=headless)


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------


def cmd_doctor(args) -> int:
    from . import doctor

    cfg = _config(args)
    print(f"ig-saved doctor  (data: {cfg.root})\n")
    return doctor.run(cfg)


def cmd_login(args) -> int:
    cfg = _config(args)
    with _session(cfg) as session:
        session.ensure_login()
        print(f"Session stored in {cfg.browser_profile}")
    return 0


def cmd_collections(args) -> int:
    cfg = _config(args)
    with _session(cfg) as session:
        session.ensure_login()
        collections = session.list_collections()

    if not collections:
        print("No collections found.")
        return 0

    width = max(len(c["name"] or "") for c in collections)
    for c in collections:
        print(f"{(c['name'] or '(unnamed)'):<{width}}  {c['id']:>20}  "
              f"{c['count'] if c['count'] is not None else '?':>5} posts")
    return 0


def cmd_index(args) -> int:
    cfg = _config(args)
    conn = db.connect(cfg.db_path)

    if args.source == "export":
        from .sources.export import iter_export

        if not args.path:
            print("--path is required for --source export", file=sys.stderr)
            return 2
        print(f"Reading export: {args.path}", file=sys.stderr)
        posts = list(iter_export(Path(args.path)))

    else:
        with _session(cfg, headless=args.headless) as session:
            session.ensure_login()

            if getattr(args, "all_collections", False):
                # The saved feed is the complete set but carries no collection
                # names; the per-collection feeds carry names but omit anything
                # uncollected. Walk both — upserts merge them, so each post ends
                # up complete and labelled.
                print("Indexing all saved posts…", file=sys.stderr)
                posts = list(session.all_saved(max_pages=args.max_pages))

                collections = session.list_collections()
                print(f"\nLabelling {len(collections)} collections…",
                      file=sys.stderr)
                for n, entry in enumerate(collections, 1):
                    print(f"[{n}/{len(collections)}] {entry['name']} "
                          f"({entry['count']} posts)", file=sys.stderr)
                    posts += list(
                        session.collection(entry["id"], name=entry["name"],
                                           max_pages=args.max_pages)
                    )

            elif args.collection:
                parsed = parse_collection_url(args.collection)
                if not parsed:
                    print(
                        "Could not read a collection id from "
                        f"{args.collection!r}.\nPass the saved-collection URL or "
                        "the bare numeric id.",
                        file=sys.stderr,
                    )
                    return 2
                owner, slug, collection_id = parsed
                if owner:
                    print(
                        f"Collection '{slug}' ({collection_id}) owned by @{owner}. "
                        "Saved collections are private, so this only works when "
                        f"signed in as @{owner}.",
                        file=sys.stderr,
                    )
                posts = list(
                    session.collection(
                        collection_id, name=slug, max_pages=args.max_pages
                    )
                )
            else:
                print("Indexing all saved posts…", file=sys.stderr)
                posts = list(session.all_saved(max_pages=args.max_pages))

    new, updated = db.upsert_posts(conn, posts)
    db.reindex(conn)
    print(f"Indexed {len(posts)} posts: {new} new, {updated} updated.")
    return 0


def cmd_hydrate(args) -> int:
    cfg = _config(args)
    conn = db.connect(cfg.db_path)

    if args.only_expired:
        shortcodes = _expired_shortcodes(conn)
    else:
        shortcodes = db.pending_hydration(conn, limit=args.limit)

    if not shortcodes:
        print("Nothing to hydrate.")
        return 0
    print(f"{len(shortcodes)} posts to hydrate via {args.via}.", file=sys.stderr)

    if args.via == "apify":
        from .hydrate import apify

        try:
            posts = list(
                apify.run(cfg, shortcodes, batch_size=args.batch_size,
                          dry_run=args.dry_run)
            )
        except apify.ApifyError as exc:
            print(f"\n{exc}", file=sys.stderr)
            return 1
        if args.dry_run:
            return 0
    else:
        from .hydrate import browser as browser_hydrate

        with _session(cfg, headless=args.headless) as session:
            session.ensure_login()
            posts = list(browser_hydrate.run(session, shortcodes))

    new, updated = db.upsert_posts(conn, posts)
    db.reindex(conn)
    print(f"Hydrated {len(posts)} posts ({new} new, {updated} updated).")
    return 0


def cmd_media(args) -> int:
    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    collection = _collection_name(getattr(args, "collection", None))
    if collection:
        print(f"Scoped to collection '{collection}'.", file=sys.stderr)
    counts = media_mod.download_all(
        conn, cfg, workers=args.workers, limit=args.limit, collection=collection
    )
    print(
        f"Downloaded {counts['downloaded']} files "
        f"({media_mod.human_bytes(counts['bytes'])}); "
        f"{counts['expired']} expired, {counts['failed']} failed."
    )
    return 0


def cmd_transcribe(args) -> int:
    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    collection = _collection_name(getattr(args, "collection", None))
    min_chars = getattr(args, "min_chars", None) or transcribe_mod.DEFAULT_MIN_CHARS

    if getattr(args, "reclassify", False):
        moved = transcribe_mod.reclassify(conn, min_chars)
        db.reindex(conn)
        print(f"Reclassified: {moved['demoted']} demoted to no_speech, "
              f"{moved['promoted']} restored to ok.")
        return 0

    if collection:
        print(f"Scoped to collection '{collection}'.", file=sys.stderr)
    counts = transcribe_mod.transcribe_all(
        conn, cfg, limit=args.limit,
        retry_failed=getattr(args, "retry_failed", False),
        collection=collection,
        min_chars=min_chars,
    )
    db.reindex(conn)
    print(
        f"Transcribed {counts['transcribed']} videos "
        f"({counts['no_speech']} no speech, {counts['no_audio']} no audio, "
        f"{counts['skipped']} skipped, {counts['failed']} failed)."
    )
    if counts["failed"]:
        print("Retry the errors with: ig-saved transcribe --retry-failed")
    return 0


def cmd_ocr(args) -> int:
    from . import ocr as ocr_mod

    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    if getattr(args, "reclean", False):
        moved = ocr_mod.reclean(conn)
        db.reindex(conn)
        print(f"Re-cleaned {moved['files']} of {moved['scanned']} files, "
              f"dropped {moved['lines_removed']} duplicate lines.")
        return 0

    collection = _collection_name(getattr(args, "collection", None))
    if collection:
        print(f"Scoped to collection '{collection}'.", file=sys.stderr)
    counts = ocr_mod.run_all(
        conn, cfg, limit=args.limit, collection=collection,
        interval=args.interval, images=not args.videos_only,
        redo=getattr(args, "redo", False),
        only_flagged=getattr(args, "only_flagged", False),
        force=getattr(args, "force", False),
    )
    db.reindex(conn)
    print(f"Read text from {counts['read']} files "
          f"({counts['empty']} had none, {counts['skipped']} skipped, "
          f"{counts['failed']} failed).")
    return 0


def cmd_describe(args) -> int:
    from . import describe as describe_mod

    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    collection = _collection_name(getattr(args, "collection", None))
    if collection:
        print(f"Scoped to collection '{collection}'.", file=sys.stderr)
    counts = describe_mod.run_all(
        conn, cfg, limit=args.limit, collection=collection,
        frames_per_video=args.frames, batch=args.batch, dry_run=args.dry_run,
    )
    if args.dry_run:
        return 0
    db.reindex(conn)
    print(f"Described {counts['described']} videos "
          f"({counts['skipped']} skipped, {counts['failed']} failed).")
    return 0


def _render_transcript(data: dict) -> str:
    post = data["post"]
    out: list[str] = []

    author = f"@{post['author_username']}" if post["author_username"] else "?"
    collections = f"  [{', '.join(data['collections'])}]" if data["collections"] else ""
    out.append(f"{author}{collections}\n{post['url']}")

    if post["caption"]:
        out.append(f"\n── Caption ──\n{post['caption'].strip()}")

    voice = " ".join(v["text"] for v in data["voice"] if v["text"]).strip()
    if voice:
        language = data["voice"][0].get("language")
        label = f"── Voice ── ({language})" if language else "── Voice ──"
        out.append(f"\n{label}\n{voice}")

    lines: list[str] = []
    for entry in data["screen_text"]:
        for item in json.loads(entry["lines_json"] or "[]"):
            stamp = int(item.get("t") or 0)
            lines.append(f"  [{stamp // 60}:{stamp % 60:02d}]  {item['text']}")
    if lines:
        out.append("\n── On-screen text ──\n" + "\n".join(lines))

    description = "\n".join(d for d in data["description"] if d).strip()
    if description:
        out.append(f"\n── Video ──\n{description}")

    return "\n".join(out)


def cmd_transcript(args) -> int:
    """Voice + on-screen text + visual description, per post."""
    cfg = _config(args)
    conn = db.connect(cfg.db_path)

    if args.shortcode:
        codes = [args.shortcode]
    else:
        collection = _collection_name(getattr(args, "collection", None))
        scope = "WHERE EXISTS (SELECT 1 FROM post_collections pc WHERE " \
                "pc.shortcode = p.shortcode AND pc.collection = :c)" \
                if collection else ""
        sql = f"SELECT p.shortcode FROM posts p {scope} ORDER BY p.saved_at DESC"
        if args.limit:
            sql += f" LIMIT {int(args.limit)}"
        codes = [r["shortcode"] for r in
                 conn.execute(sql, {"c": collection} if collection else {})]

    if not codes:
        print("No matching posts.", file=sys.stderr)
        return 1

    rendered = []
    for code in codes:
        data = db.transcript_for(conn, code)
        if data:
            rendered.append(_render_transcript(data))

    body = ("\n\n" + "─" * 66 + "\n\n").join(rendered)
    if args.out and args.out != "-":
        Path(args.out).write_text(body + "\n", encoding="utf-8")
        print(f"Wrote {len(rendered)} transcripts to {args.out}", file=sys.stderr)
    else:
        print(body)
    return 0


def cmd_extract(args) -> int:
    from . import extract as extract_mod

    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    collection = _collection_name(getattr(args, "collection", None))
    if collection:
        print(f"Scoped to collection '{collection}'.", file=sys.stderr)
    counts = extract_mod.run_all(
        conn, cfg, limit=args.limit, collection=collection,
        batch=args.batch, dry_run=args.dry_run, redo=args.redo,
        only_flagged=getattr(args, "only_flagged", False),
        force=getattr(args, "force", False),
    )
    if args.dry_run:
        return 0
    unchanged = counts.get("unchanged", 0)
    print(f"Extracted {counts['extracted']} entries "
          f"({unchanged} unchanged, {counts['skipped']} skipped, "
          f"{counts['failed']} failed).")
    return 0


def cmd_report(args) -> int:
    from . import report as report_mod

    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    collection = _collection_name(getattr(args, "collection", None))
    out_dir = Path(args.out).expanduser() if args.out else cfg.root / "report"

    formats = tuple(args.format) if args.format else ("html", "csv", "md")
    written = report_mod.build(conn, cfg, out_dir,
                               collection=collection, formats=formats)
    if not written:
        print("No entries yet — run `ig-saved extract` first.", file=sys.stderr)
        return 1

    print(f"{written.pop('count')} entries")
    for kind, path in written.items():
        print(f"  {kind:<5} {path}")
    return 0


def cmd_search(args) -> int:
    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    rows = db.search(conn, args.query, limit=args.limit,
                     collection=_collection_name(getattr(args, "collection", None)))
    if not rows:
        print("No matches.")
        return 0
    for row in rows:
        author = f"@{row['author_username']}" if row["author_username"] else "?"
        collection = f" [{row['collection']}]" if row["collection"] else ""
        print(f"\n{author}{collection}  {row['url']}")
        for label, key in (("caption", "caption_hit"),
                           ("voice", "transcript_hit"),
                           ("on-screen", "screen_hit"),
                           ("video", "description_hit")):
            hit = (row[key] or "").strip()
            if hit:
                print(f"  {label + ':':<11} {hit}")
    return 0


def cmd_stats(args) -> int:
    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    collection = _collection_name(getattr(args, "collection", None))
    s = db.stats(conn, collection)

    scope = f"collection '{collection}'" if collection else "all collections"
    print(f"{scope}\n")

    def pct(part: int, whole: int) -> str:
        return f"  ({100 * part // whole}%)" if whole else ""

    # Read top to bottom as the funnel: indexed -> hydrated -> downloaded ->
    # transcribed. A stage well below the one above it is where to look.
    print(f"{'posts':>16}: {s['posts']}")
    print(f"{'hydrated':>16}: {s['hydrated']}{pct(s['hydrated'], s['posts'])}")
    print(f"{'media files':>16}: {s['media']}")
    print(f"{'downloaded':>16}: {s['downloaded']}{pct(s['downloaded'], s['media'])}")
    print(f"{'videos':>16}: {s['videos']}")
    print(f"{'transcribed':>16}: {s['transcripts']}"
          f"{pct(s['transcripts'], s['videos'])}")
    if s["untranscribable"]:
        print(f"{'no speech/audio':>16}: {s['untranscribable']}")
    print(f"{'screen text':>16}: {s['screen_text']}{pct(s['screen_text'], s['media'])}")
    print(f"{'described':>16}: {s['described']}{pct(s['described'], s['videos'])}")
    if not collection:
        print(f"{'collections':>16}: {s['collections']}")

    print(f"\n{'db':>16}: {cfg.db_path}")
    print(f"{'media':>16}: {cfg.media_dir}")
    return 0


def cmd_dump(args) -> int:
    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    rows = conn.execute(
        """
        SELECT p.*,
               (SELECT group_concat(m.local_path, char(10)) FROM media m
                 WHERE m.shortcode = p.shortcode) AS files,
               (SELECT group_concat(t.text, ' ') FROM transcripts t
                 WHERE t.shortcode = p.shortcode) AS transcript
        FROM posts p ORDER BY p.saved_at DESC
        """
    )
    out = sys.stdout if args.out == "-" else open(args.out, "w", encoding="utf-8")
    try:
        for row in rows:
            record = dict(row)
            record.pop("raw_json", None)
            record["files"] = (record.get("files") or "").split("\n") if record.get("files") else []
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
    finally:
        if out is not sys.stdout:
            out.close()
            print(f"Wrote {args.out}", file=sys.stderr)
    return 0


def cmd_sync(args) -> int:
    """index -> hydrate -> media -> transcribe, in one pass."""
    steps = [("index", cmd_index)]
    if args.source == "export":
        steps.append(("hydrate", cmd_hydrate))
    steps.append(("media", cmd_media))
    # Transcription runs orders of magnitude slower than the rest, so on a
    # large archive it is usually better run separately, in chunks.
    if not getattr(args, "skip_transcribe", False):
        steps.append(("transcribe", cmd_transcribe))
    if getattr(args, "ocr", False):
        steps.append(("ocr", cmd_ocr))
    if getattr(args, "describe", False):
        steps.append(("describe", cmd_describe))
    if getattr(args, "extract", False):
        steps += [("extract", cmd_extract), ("report", cmd_report)]

    for name, fn in steps:
        print(f"\n=== {name} ===", file=sys.stderr)
        code = fn(args)
        if code != 0:
            print(f"Stopped at '{name}'.", file=sys.stderr)
            return code
    return cmd_stats(args)


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ig-saved",
        description="Index, archive and search your Instagram saved posts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Typical first run:\n"
            "  ig-saved doctor            # what's installed, what's missing\n"
            "  ig-saved login             # sign in by hand, once\n"
            "  ig-saved collections       # your collections and their ids\n"
            "  ig-saved sync --source browser --collection <saved-collection-url>\n"
            "  ig-saved search 'ramen'\n"
        ),
    )
    parser.add_argument("--home", help="data directory (default ~/.ig-saved)")

    sub = parser.add_subparsers(dest="command", required=True)

    def add_browser_flags(p):
        p.add_argument("--headless", action="store_true",
                       help="requires an existing session (run `login` first)")
        p.add_argument("--slow", action="store_true",
                       help="4-9s between requests instead of 1.5-4s")

    def add_apify_flags(p):
        p.add_argument("--apify-token", help="defaults to $APIFY_TOKEN")
        p.add_argument("--apify-actor", help="owner/name of the actor")
        p.add_argument("--apify-url-field", dest="apify_url_field",
                       help="input field the actor reads URLs from")

    def add_whisper_flags(p):
        p.add_argument("--whisper-model", dest="whisper_model",
                       help="tiny | base | small | medium | large-v3")

    p = sub.add_parser("doctor", help="check the environment and say what's missing")
    add_apify_flags(p)
    add_whisper_flags(p)
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("login", help="sign in once and store the session")
    add_browser_flags(p)
    p.set_defaults(func=cmd_login)

    p = sub.add_parser("collections", help="list your saved collections")
    add_browser_flags(p)
    p.set_defaults(func=cmd_collections)

    p = sub.add_parser("index", help="stage 1: build the list of saved posts")
    p.add_argument("--source", choices=["export", "browser"], default="browser")
    p.add_argument("--path", help="export .zip / folder (for --source export)")
    p.add_argument("--collection", help="saved-collection URL or numeric id")
    p.add_argument("--all-collections", action="store_true",
                   help="index everything, then walk every collection so each "
                        "post is labelled with the collection it is in")
    p.add_argument("--max-pages", type=int, help="stop after N pages")
    add_browser_flags(p)
    p.set_defaults(func=cmd_index)

    p = sub.add_parser("hydrate", help="stage 2: fetch captions and media URLs")
    p.add_argument("--via", choices=["apify", "browser"], default="browser")
    p.add_argument("--limit", type=int)
    p.add_argument("--batch-size", type=int, default=100)
    p.add_argument("--dry-run", action="store_true",
                   help="print the Apify input without spending credits")
    p.add_argument("--only-expired", action="store_true",
                   help="refresh posts whose CDN URLs went stale")
    add_browser_flags(p)
    add_apify_flags(p)
    p.set_defaults(func=cmd_hydrate)

    p = sub.add_parser("media", help="download images and videos")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--limit", type=int)
    p.add_argument("--collection", help="only this collection (URL, id or name)")
    p.set_defaults(func=cmd_media)

    p = sub.add_parser("transcribe", help="transcribe saved reels")
    p.add_argument("--limit", type=int)
    p.add_argument("--collection", help="only this collection (URL, id or name)")
    p.add_argument("--retry-failed", action="store_true",
                   help="re-attempt videos that errored (not ones with no "
                        "speech or no audio track, which will not change)")
    p.add_argument("--min-chars", type=int,
                   help="discard transcripts shorter than this as hallucinated "
                        f"(default {transcribe_mod.DEFAULT_MIN_CHARS})")
    p.add_argument("--reclassify", action="store_true",
                   help="re-apply the quality filter to existing transcripts "
                        "without running the model")
    add_whisper_flags(p)
    p.set_defaults(func=cmd_transcribe)

    p = sub.add_parser("ocr", help="read text burned into videos and images")
    p.add_argument("--limit", type=int)
    p.add_argument("--collection", help="only this collection (URL, id or name)")
    p.add_argument("--interval", type=float, default=1.0,
                   help="seconds between sampled frames (default 1.0)")
    p.add_argument("--videos-only", action="store_true",
                   help="skip still images")
    p.add_argument("--reclean", action="store_true",
                   help="re-dedupe stored OCR lines without re-running OCR")
    p.add_argument("--redo", action="store_true",
                   help="re-read media that already has OCR, e.g. at a finer "
                        "--interval")
    p.add_argument("--only-flagged", action="store_true",
                   help="re-read only media whose post is marked needs_review")
    p.set_defaults(func=cmd_ocr)

    p = sub.add_parser("describe", help="describe what each video shows")
    p.add_argument("--limit", type=int)
    p.add_argument("--collection", help="only this collection (URL, id or name)")
    p.add_argument("--frames", type=int, default=4,
                   help="keyframes sent per video (default 4)")
    p.add_argument("--batch", action="store_true",
                   help="use the Batch API: half price, asynchronous")
    p.add_argument("--dry-run", action="store_true",
                   help="estimate cost without calling the API")
    p.set_defaults(func=cmd_describe)

    p = sub.add_parser("transcript",
                       help="voice + on-screen text + description, per post")
    p.add_argument("shortcode", nargs="?", help="one post; omit for many")
    p.add_argument("--collection", help="only this collection (URL, id or name)")
    p.add_argument("--limit", type=int)
    p.add_argument("--out", help="write to a file instead of stdout")
    p.set_defaults(func=cmd_transcript)

    p = sub.add_parser("extract",
                       help="distil each post into decidable fields")
    p.add_argument("--limit", type=int)
    p.add_argument("--collection", help="only this collection (URL, id or name)")
    p.add_argument("--batch", action="store_true",
                   help="use the Batch API: half price, asynchronous")
    p.add_argument("--dry-run", action="store_true",
                   help="estimate cost without calling the API")
    p.add_argument("--redo", action="store_true",
                   help="re-extract posts that already have an entry")
    p.add_argument("--only-flagged", action="store_true",
                   help="re-extract only entries marked needs_review")
    p.add_argument("--force", action="store_true",
                   help="re-extract even when the evidence has not changed "
                        "since the last run")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("report", help="build the categorised, actionable output")
    p.add_argument("--collection", help="only this collection (URL, id or name)")
    p.add_argument("--out", help="directory to write into (default <home>/report)")
    p.add_argument("--format", action="append", choices=["html", "csv", "md"],
                   help="repeatable; default all three")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("search", help="full-text search captions and transcripts")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--collection", help="only this collection (URL, id or name)")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("stats", help="funnel counts, overall or per collection")
    p.add_argument("--collection", help="only this collection (URL, id or name)")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("dump", help="write every post as JSONL")
    p.add_argument("--out", default="-")
    p.set_defaults(func=cmd_dump)

    p = sub.add_parser("sync", help="index, hydrate, download and transcribe")
    p.add_argument("--source", choices=["export", "browser"], default="browser")
    p.add_argument("--path")
    p.add_argument("--collection")
    p.add_argument("--all-collections", action="store_true")
    p.add_argument("--retry-failed", action="store_true")
    p.add_argument("--max-pages", type=int)
    p.add_argument("--via", choices=["apify", "browser"], default="browser")
    p.add_argument("--limit", type=int)
    p.add_argument("--batch-size", type=int, default=100)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--only-expired", action="store_true")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--skip-transcribe", action="store_true",
                   help="stop after downloading media; transcribe separately")
    p.add_argument("--ocr", action="store_true",
                   help="also read text burned into the media")
    p.add_argument("--describe", action="store_true",
                   help="also describe each video (uses the Claude API)")
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--videos-only", action="store_true")
    p.add_argument("--frames", type=int, default=4)
    p.add_argument("--batch", action="store_true")
    p.add_argument("--extract", action="store_true",
                   help="also distil entries and build the report")
    p.add_argument("--redo", action="store_true")
    p.add_argument("--only-flagged", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--out")
    p.add_argument("--format", action="append", choices=["html", "csv", "md"])
    add_browser_flags(p)
    add_apify_flags(p)
    add_whisper_flags(p)
    p.set_defaults(func=cmd_sync)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted. Progress is saved — rerun to resume.", file=sys.stderr)
        return 130
    except (FileNotFoundError, LookupError, ValueError) as exc:
        print(f"\n{exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        # ProfileBusy and NotLoggedIn carry instructions, not stack traces.
        from .sources.browser import NotLoggedIn, ProfileBusy

        if isinstance(exc, (NotLoggedIn, ProfileBusy)):
            print(f"\n{exc}", file=sys.stderr)
            return 1
        raise


if __name__ == "__main__":
    raise SystemExit(main())

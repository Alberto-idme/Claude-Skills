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
    counts = media_mod.download_all(
        conn, cfg, workers=args.workers, limit=args.limit
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
    counts = transcribe_mod.transcribe_all(
        conn, cfg, limit=args.limit,
        retry_failed=getattr(args, "retry_failed", False),
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


def cmd_search(args) -> int:
    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    rows = db.search(conn, args.query, limit=args.limit)
    if not rows:
        print("No matches.")
        return 0
    for row in rows:
        author = f"@{row['author_username']}" if row["author_username"] else "?"
        collection = f" [{row['collection']}]" if row["collection"] else ""
        print(f"\n{author}{collection}  {row['url']}")
        if row["caption_hit"].strip():
            print(f"  caption:    {row['caption_hit']}")
        if row["transcript_hit"].strip():
            print(f"  transcript: {row['transcript_hit']}")
    return 0


def cmd_stats(args) -> int:
    cfg = _config(args)
    conn = db.connect(cfg.db_path)
    for key, value in db.stats(conn).items():
        print(f"{key:>12}: {value}")
    print(f"{'db':>12}: {cfg.db_path}")
    print(f"{'media':>12}: {cfg.media_dir}")
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
    p.set_defaults(func=cmd_media)

    p = sub.add_parser("transcribe", help="transcribe saved reels")
    p.add_argument("--limit", type=int)
    p.add_argument("--retry-failed", action="store_true",
                   help="re-attempt videos that errored (not ones with no "
                        "speech or no audio track, which will not change)")
    add_whisper_flags(p)
    p.set_defaults(func=cmd_transcribe)

    p = sub.add_parser("search", help="full-text search captions and transcripts")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("stats", help="what is in the database")
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

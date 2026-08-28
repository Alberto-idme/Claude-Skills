"""SQLite store.

One row per saved post, one row per media file, one row per transcript, plus an
FTS5 index over captions and transcripts so reels are findable by what was said
in them.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Iterable

from .normalize import Post

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS posts (
    shortcode        TEXT PRIMARY KEY,
    media_id         TEXT,
    url              TEXT NOT NULL,
    author_username  TEXT,
    author_full_name TEXT,
    caption          TEXT,
    taken_at         INTEGER,
    saved_at         INTEGER,
    media_type       TEXT,
    product_type     TEXT,
    like_count       INTEGER,
    comment_count    INTEGER,
    collection       TEXT,
    source           TEXT,
    indexed_at       INTEGER,
    hydrated_at      INTEGER,
    raw_json         TEXT
);

CREATE TABLE IF NOT EXISTS media (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    shortcode     TEXT NOT NULL REFERENCES posts(shortcode) ON DELETE CASCADE,
    idx           INTEGER NOT NULL,
    kind          TEXT NOT NULL,
    remote_url    TEXT,
    local_path    TEXT,
    width         INTEGER,
    height        INTEGER,
    downloaded_at INTEGER,
    UNIQUE (shortcode, idx)
);

CREATE TABLE IF NOT EXISTS transcripts (
    media_id      INTEGER PRIMARY KEY REFERENCES media(id) ON DELETE CASCADE,
    shortcode     TEXT NOT NULL,
    text          TEXT,
    segments_json TEXT,
    language      TEXT,
    model         TEXT,
    created_at    INTEGER,
    -- ok | no_audio | no_speech | error. Anything but 'ok' still gets a row,
    -- so a reel that can never be transcribed is not re-attempted every run.
    status        TEXT NOT NULL DEFAULT 'ok'
);

-- A post can sit in several saved collections at once, so the label cannot
-- live on the post. `posts.collection` is kept as a first-seen convenience for
-- display; this table is the truth every filter goes through.
CREATE TABLE IF NOT EXISTS post_collections (
    shortcode  TEXT NOT NULL REFERENCES posts(shortcode) ON DELETE CASCADE,
    collection TEXT NOT NULL,
    PRIMARY KEY (shortcode, collection)
);

CREATE INDEX IF NOT EXISTS idx_pc_collection ON post_collections(collection);
CREATE INDEX IF NOT EXISTS idx_posts_collection ON posts(collection);
CREATE INDEX IF NOT EXISTS idx_posts_hydrated   ON posts(hydrated_at);
CREATE INDEX IF NOT EXISTS idx_media_shortcode  ON media(shortcode);

CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(
    shortcode UNINDEXED,
    author,
    caption,
    transcript,
    collection UNINDEXED,
    tokenize='unicode61 remove_diacritics 2'
);
"""


def _in_collection(alias: str = "p") -> str:
    """SQL predicate scoping to one collection, via the join table.

    A post can carry several labels, so this must be an EXISTS over
    post_collections — `posts.collection = ?` would only ever match the first
    one a post was indexed under.
    """
    return (
        f"EXISTS (SELECT 1 FROM post_collections pc "
        f"WHERE pc.shortcode = {alias}.shortcode AND pc.collection = :c)"
    )


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Bring an existing database up to the current schema, in place.

    `CREATE TABLE IF NOT EXISTS` silently leaves an older table alone, so
    columns added after someone started archiving have to be ALTERed in.
    """
    columns = {r["name"] for r in conn.execute("PRAGMA table_info(transcripts)")}
    if columns and "status" not in columns:
        conn.execute(
            "ALTER TABLE transcripts ADD COLUMN status TEXT NOT NULL DEFAULT 'ok'"
        )
        conn.commit()

    # Seed the join table from whatever single label each post already carries.
    # Labels overwritten before this table existed are gone; re-running index
    # for those collections restores them, and now they accumulate.
    conn.execute(
        """
        INSERT OR IGNORE INTO post_collections (shortcode, collection)
        SELECT shortcode, collection FROM posts WHERE collection IS NOT NULL
        """
    )
    conn.commit()


def upsert_posts(conn: sqlite3.Connection, posts: Iterable[Post]) -> tuple[int, int]:
    """Insert or enrich posts. Returns ``(new, updated)``.

    Indexing and hydration write the same rows at different times, so a later
    pass must never blank a column an earlier pass filled: COALESCE keeps the
    first non-null value for everything except counts, which are volatile and
    should track the freshest fetch.
    """
    now = int(time.time())
    new = updated = 0

    for post in posts:
        exists = conn.execute(
            "SELECT 1 FROM posts WHERE shortcode = ?", (post.shortcode,)
        ).fetchone()

        hydrated = now if post.caption is not None or post.media else None

        conn.execute(
            """
            INSERT INTO posts (
                shortcode, media_id, url, author_username, author_full_name,
                caption, taken_at, saved_at, media_type, product_type,
                like_count, comment_count, collection, source,
                indexed_at, hydrated_at, raw_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(shortcode) DO UPDATE SET
                media_id         = COALESCE(excluded.media_id, posts.media_id),
                author_username  = COALESCE(excluded.author_username, posts.author_username),
                author_full_name = COALESCE(excluded.author_full_name, posts.author_full_name),
                caption          = COALESCE(excluded.caption, posts.caption),
                taken_at         = COALESCE(excluded.taken_at, posts.taken_at),
                saved_at         = COALESCE(excluded.saved_at, posts.saved_at),
                media_type       = COALESCE(excluded.media_type, posts.media_type),
                product_type     = COALESCE(excluded.product_type, posts.product_type),
                like_count       = COALESCE(excluded.like_count, posts.like_count),
                comment_count    = COALESCE(excluded.comment_count, posts.comment_count),
                -- First label wins, so this stays stable for display; every
                -- label a post picks up is recorded in post_collections.
                collection       = COALESCE(posts.collection, excluded.collection),
                hydrated_at      = COALESCE(excluded.hydrated_at, posts.hydrated_at),
                raw_json         = COALESCE(excluded.raw_json, posts.raw_json)
            """,
            (
                post.shortcode, post.media_id, post.url, post.author_username,
                post.author_full_name, post.caption, post.taken_at, post.saved_at,
                post.media_type, post.product_type, post.like_count,
                post.comment_count, post.collection, post.source,
                now, hydrated,
                json.dumps(post.raw, ensure_ascii=False) if post.raw else None,
            ),
        )

        if post.collection:
            conn.execute(
                "INSERT OR IGNORE INTO post_collections (shortcode, collection) "
                "VALUES (?,?)",
                (post.shortcode, post.collection),
            )

        for ref in post.media:
            conn.execute(
                """
                INSERT INTO media (shortcode, idx, kind, remote_url, width, height)
                VALUES (?,?,?,?,?,?)
                ON CONFLICT(shortcode, idx) DO UPDATE SET
                    kind       = excluded.kind,
                    -- CDN URLs are pre-signed and expire; always take the newest.
                    remote_url = COALESCE(excluded.remote_url, media.remote_url),
                    width      = COALESCE(excluded.width, media.width),
                    height     = COALESCE(excluded.height, media.height)
                """,
                (post.shortcode, ref.idx, ref.kind, ref.remote_url,
                 ref.width, ref.height),
            )

        if exists:
            updated += 1
        else:
            new += 1

    conn.commit()
    return new, updated


def pending_hydration(conn: sqlite3.Connection, limit: int | None = None) -> list[str]:
    sql = "SELECT shortcode FROM posts WHERE hydrated_at IS NULL ORDER BY saved_at DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    return [r["shortcode"] for r in conn.execute(sql)]


def pending_downloads(
    conn: sqlite3.Connection, *, collection: str | None = None
) -> list[sqlite3.Row]:
    scope = f"AND {_in_collection()}" if collection else ""
    return list(
        conn.execute(
            f"""
            SELECT m.id, m.shortcode, m.idx, m.kind, m.remote_url
            FROM media m
            JOIN posts p ON p.shortcode = m.shortcode
            WHERE m.local_path IS NULL AND m.remote_url IS NOT NULL {scope}
            ORDER BY m.shortcode, m.idx
            """,
            {"c": collection} if collection else {},
        )
    )


def pending_transcripts(
    conn: sqlite3.Connection,
    *,
    retry_failed: bool = False,
    collection: str | None = None,
) -> list[sqlite3.Row]:
    """Downloaded videos with no transcript row yet.

    A video that failed permanently (no audio track, no speech) still gets a
    row, so it drops out of this list instead of burning model time on every
    subsequent run. ``retry_failed`` brings those back.
    """
    condition = "t.media_id IS NULL"
    if retry_failed:
        condition = "(t.media_id IS NULL OR t.status = 'error')"
    scope = f"AND {_in_collection()}" if collection else ""
    return list(
        conn.execute(
            f"""
            SELECT m.id, m.shortcode, m.local_path
            FROM media m
            JOIN posts p ON p.shortcode = m.shortcode
            LEFT JOIN transcripts t ON t.media_id = m.id
            WHERE m.kind = 'video'
              AND m.local_path IS NOT NULL
              AND {condition} {scope}
            ORDER BY m.shortcode
            """,
            {"c": collection} if collection else {},
        )
    )


def mark_downloaded(conn: sqlite3.Connection, media_id: int, path: str) -> None:
    conn.execute(
        "UPDATE media SET local_path = ?, downloaded_at = ? WHERE id = ?",
        (path, int(time.time()), media_id),
    )
    conn.commit()


def save_transcript(
    conn: sqlite3.Connection,
    *,
    media_id: int,
    shortcode: str,
    text: str,
    segments: list,
    language: str | None,
    model: str,
    status: str = "ok",
) -> None:
    conn.execute(
        """
        INSERT INTO transcripts (media_id, shortcode, text, segments_json,
                                 language, model, created_at, status)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(media_id) DO UPDATE SET
            text = excluded.text, segments_json = excluded.segments_json,
            language = excluded.language, model = excluded.model,
            created_at = excluded.created_at, status = excluded.status
        """,
        (media_id, shortcode, text, json.dumps(segments, ensure_ascii=False),
         language, model, int(time.time()), status),
    )
    conn.commit()


def reindex(conn: sqlite3.Connection) -> int:
    """Rebuild the FTS table from posts + transcripts.

    Transcripts land long after their post row, so rebuilding wholesale is both
    simpler and less error-prone than maintaining triggers.
    """
    conn.execute("DELETE FROM search")
    conn.execute(
        """
        INSERT INTO search (shortcode, author, caption, transcript, collection)
        SELECT p.shortcode,
               COALESCE(p.author_username, ''),
               COALESCE(p.caption, ''),
               -- Only 'ok' transcripts. Discarded text is kept on the row for
               -- inspection but must never reach the index, or every silent
               -- reel becomes a hit for whatever Whisper hallucinated.
               COALESCE((SELECT group_concat(t.text, ' ')
                         FROM transcripts t
                         WHERE t.shortcode = p.shortcode AND t.status = 'ok'), ''),
               COALESCE((SELECT group_concat(pc.collection, ' ')
                         FROM post_collections pc
                         WHERE pc.shortcode = p.shortcode), '')
        FROM posts p
        """
    )
    conn.commit()
    return conn.execute("SELECT count(*) AS n FROM search").fetchone()["n"]


def search(
    conn: sqlite3.Connection,
    query: str,
    limit: int = 20,
    collection: str | None = None,
) -> list[sqlite3.Row]:
    scope = f"AND {_in_collection()}" if collection else ""
    params = {"q": query, "limit": limit}
    if collection:
        params["c"] = collection
    return list(
        conn.execute(
            f"""
            SELECT s.shortcode, p.url, p.author_username,
                   (SELECT group_concat(pc.collection, ', ')
                    FROM post_collections pc
                    WHERE pc.shortcode = p.shortcode) AS collection,
                   snippet(search, 2, '[', ']', '…', 12) AS caption_hit,
                   snippet(search, 3, '[', ']', '…', 12) AS transcript_hit
            FROM search s
            JOIN posts p ON p.shortcode = s.shortcode
            WHERE search MATCH :q {scope}
            ORDER BY rank
            LIMIT :limit
            """,
            params,
        )
    )


def stats(conn: sqlite3.Connection, collection: str | None = None) -> dict:
    """Funnel counts, optionally for one collection only."""
    params = {"c": collection} if collection else {}
    where = f"WHERE {_in_collection()}" if collection else ""
    and_ = f"AND {_in_collection()}" if collection else ""

    def count(sql: str) -> int:
        return conn.execute(sql, params).fetchone()[0]

    media_join = "FROM media m JOIN posts p ON p.shortcode = m.shortcode"
    txt_join = "FROM transcripts t JOIN posts p ON p.shortcode = t.shortcode"

    return {
        "posts": count(f"SELECT count(*) FROM posts p {where}"),
        "hydrated": count(
            f"SELECT count(*) FROM posts p WHERE p.hydrated_at IS NOT NULL {and_}"),
        "media": count(f"SELECT count(*) {media_join} {where}"),
        "downloaded": count(
            f"SELECT count(*) {media_join} WHERE m.local_path IS NOT NULL {and_}"),
        "videos": count(
            f"SELECT count(*) {media_join} WHERE m.kind = 'video' {and_}"),
        "transcripts": count(
            f"SELECT count(*) {txt_join} WHERE t.status = 'ok' {and_}"),
        "untranscribable": count(
            f"SELECT count(*) {txt_join} WHERE t.status != 'ok' {and_}"),
        "collections": count(
            "SELECT count(DISTINCT collection) FROM post_collections"),
    }

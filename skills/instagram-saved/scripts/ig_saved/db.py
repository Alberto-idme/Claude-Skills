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
    created_at    INTEGER
);

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


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


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
                collection       = COALESCE(excluded.collection, posts.collection),
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


def pending_downloads(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT id, shortcode, idx, kind, remote_url
            FROM media
            WHERE local_path IS NULL AND remote_url IS NOT NULL
            ORDER BY shortcode, idx
            """
        )
    )


def pending_transcripts(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT m.id, m.shortcode, m.local_path
            FROM media m
            LEFT JOIN transcripts t ON t.media_id = m.id
            WHERE m.kind = 'video'
              AND m.local_path IS NOT NULL
              AND t.media_id IS NULL
            ORDER BY m.shortcode
            """
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
) -> None:
    conn.execute(
        """
        INSERT INTO transcripts (media_id, shortcode, text, segments_json,
                                 language, model, created_at)
        VALUES (?,?,?,?,?,?,?)
        ON CONFLICT(media_id) DO UPDATE SET
            text = excluded.text, segments_json = excluded.segments_json,
            language = excluded.language, model = excluded.model,
            created_at = excluded.created_at
        """,
        (media_id, shortcode, text, json.dumps(segments, ensure_ascii=False),
         language, model, int(time.time())),
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
               COALESCE((SELECT group_concat(t.text, ' ')
                         FROM transcripts t WHERE t.shortcode = p.shortcode), ''),
               COALESCE(p.collection, '')
        FROM posts p
        """
    )
    conn.commit()
    return conn.execute("SELECT count(*) AS n FROM search").fetchone()["n"]


def search(conn: sqlite3.Connection, query: str, limit: int = 20) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT s.shortcode, p.url, p.author_username, p.collection,
                   snippet(search, 2, '[', ']', '…', 12) AS caption_hit,
                   snippet(search, 3, '[', ']', '…', 12) AS transcript_hit
            FROM search s
            JOIN posts p ON p.shortcode = s.shortcode
            WHERE search MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (query, limit),
        )
    )


def stats(conn: sqlite3.Connection) -> dict:
    row = conn.execute(
        """
        SELECT (SELECT count(*) FROM posts) AS posts,
               (SELECT count(*) FROM posts WHERE hydrated_at IS NOT NULL) AS hydrated,
               (SELECT count(*) FROM media) AS media,
               (SELECT count(*) FROM media WHERE local_path IS NOT NULL) AS downloaded,
               (SELECT count(*) FROM media WHERE kind = 'video') AS videos,
               (SELECT count(*) FROM transcripts) AS transcripts,
               (SELECT count(DISTINCT collection) FROM posts
                 WHERE collection IS NOT NULL) AS collections
        """
    ).fetchone()
    return dict(row)

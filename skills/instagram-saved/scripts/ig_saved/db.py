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

-- Text burned into the video or image. For recommendation reels this is often
-- the only place the name appears.
CREATE TABLE IF NOT EXISTS ocr (
    media_id   INTEGER PRIMARY KEY REFERENCES media(id) ON DELETE CASCADE,
    shortcode  TEXT NOT NULL,
    text       TEXT,
    lines_json TEXT,
    frames     INTEGER,
    engine     TEXT,
    status     TEXT NOT NULL DEFAULT 'ok',
    created_at INTEGER
);

-- What the video shows, from a vision model over sampled keyframes.
CREATE TABLE IF NOT EXISTS descriptions (
    media_id      INTEGER PRIMARY KEY REFERENCES media(id) ON DELETE CASCADE,
    shortcode     TEXT NOT NULL,
    text          TEXT,
    model         TEXT,
    frames        INTEGER,
    input_tokens  INTEGER,
    output_tokens INTEGER,
    status        TEXT NOT NULL DEFAULT 'ok',
    created_at    INTEGER
);

-- The triage record: the decidable fields distilled from all four tracks.
CREATE TABLE IF NOT EXISTS entries (
    shortcode    TEXT PRIMARY KEY REFERENCES posts(shortcode) ON DELETE CASCADE,
    title        TEXT,
    category     TEXT,
    location     TEXT,
    summary      TEXT,
    highlights   TEXT,
    action       TEXT,
    practical    TEXT,
    confidence   TEXT,
    needs_review INTEGER NOT NULL DEFAULT 0,
    review_reason TEXT,
    review_kind  TEXT,
    evidence_hash TEXT,
    sources      TEXT,
    model        TEXT,
    created_at   INTEGER
);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_entries_category ON entries(category);
CREATE INDEX IF NOT EXISTS idx_ocr_shortcode  ON ocr(shortcode);
CREATE INDEX IF NOT EXISTS idx_desc_shortcode ON descriptions(shortcode);

CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(
    shortcode UNINDEXED,
    author,
    caption,
    transcript,
    screen_text,
    description,
    collection UNINDEXED,
    -- Trigram, not unicode61. Two reasons, both measured:
    --   * Japanese and Korean have no word spaces, so unicode61 indexes a whole
    --     caption as one token — searching ラーメン inside 東京ラーメン二郎 returns
    --     nothing at all. Trigram matches it.
    --   * OCR on compressed video sometimes loses the spaces between words
    --     ("ICHIRANSHIBUYA"), which unicode61 likewise cannot search into.
    -- The cost is that queries shorter than 3 characters cannot match.
    tokenize='trigram'
);
"""

# The FTS table has to be dropped and rebuilt whenever its columns or tokenizer
# change, since CREATE ... IF NOT EXISTS silently keeps an older definition.
FTS_COLUMNS = {"shortcode", "author", "caption", "transcript",
               "screen_text", "description", "collection"}
FTS_TOKENIZER = "trigram"


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
    _rebuild_fts_if_stale(conn)
    conn.executescript(SCHEMA)
    _migrate(conn)
    return conn


def _rebuild_fts_if_stale(conn: sqlite3.Connection) -> None:
    """Drop the FTS table when its columns no longer match the schema.

    `CREATE VIRTUAL TABLE IF NOT EXISTS` silently keeps an older column list,
    so adding a searchable field would otherwise never take effect. The index
    is derived data — `reindex()` rebuilds it from the source tables.
    """
    try:
        existing = {r["name"] for r in conn.execute("PRAGMA table_info(search)")}
        definition = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='search'"
        ).fetchone()
    except sqlite3.Error:
        return

    if not existing:
        return

    stale_columns = existing != FTS_COLUMNS
    # A tokenizer swap keeps the same columns, so it has to be checked directly.
    stale_tokenizer = definition is not None and FTS_TOKENIZER not in (
        definition["sql"] or ""
    )
    if stale_columns or stale_tokenizer:
        conn.execute("DROP TABLE search")
        conn.commit()


def _migrate(conn: sqlite3.Connection) -> None:
    """Bring an existing database up to the current schema, in place.

    `CREATE TABLE IF NOT EXISTS` silently leaves an older table alone, so
    columns added after someone started archiving have to be ALTERed in.
    """
    entry_columns = {r["name"] for r in conn.execute("PRAGMA table_info(entries)")}
    for column in ("review_reason", "review_kind", "evidence_hash"):
        if entry_columns and column not in entry_columns:
            conn.execute(f"ALTER TABLE entries ADD COLUMN {column} TEXT")
            conn.commit()

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


def pending_ocr(
    conn: sqlite3.Connection,
    *,
    collection: str | None = None,
    include_images: bool = True,
    redo: bool = False,
    only_flagged: bool = False,
) -> list[sqlite3.Row]:
    """Downloaded media with no OCR row yet.

    `redo` re-reads media that already has one — needed to re-scan at a finer
    `--interval`, since a garbled read is stored just like a good one.
    `only_flagged` narrows that to posts whose entry is marked needs_review,
    which is the case worth paying denser sampling for.
    """
    scope = f"AND {_in_collection()}" if collection else ""
    kinds = "" if include_images else "AND m.kind = 'video'"
    unread = "" if (redo or only_flagged) else "AND o.media_id IS NULL"
    flagged = ("AND EXISTS (SELECT 1 FROM entries e "
               "WHERE e.shortcode = m.shortcode AND e.needs_review = 1)"
               if only_flagged else "")
    return list(
        conn.execute(
            f"""
            SELECT m.id, m.shortcode, m.kind, m.local_path
            FROM media m
            JOIN posts p ON p.shortcode = m.shortcode
            LEFT JOIN ocr o ON o.media_id = m.id
            WHERE m.local_path IS NOT NULL {unread}
              {kinds} {flagged} {scope}
            ORDER BY m.shortcode, m.idx
            """,
            {"c": collection} if collection else {},
        )
    )


def pending_descriptions(
    conn: sqlite3.Connection, *, collection: str | None = None
) -> list[sqlite3.Row]:
    scope = f"AND {_in_collection()}" if collection else ""
    return list(
        conn.execute(
            f"""
            SELECT m.id, m.shortcode, m.local_path
            FROM media m
            JOIN posts p ON p.shortcode = m.shortcode
            LEFT JOIN descriptions d ON d.media_id = m.id
            WHERE m.kind = 'video' AND m.local_path IS NOT NULL
              AND d.media_id IS NULL {scope}
            ORDER BY m.shortcode, m.idx
            """,
            {"c": collection} if collection else {},
        )
    )


def save_ocr(
    conn: sqlite3.Connection, *, media_id: int, shortcode: str, text: str,
    lines: list, frames: int, engine: str, status: str = "ok",
) -> None:
    conn.execute(
        """
        INSERT INTO ocr (media_id, shortcode, text, lines_json, frames,
                         engine, status, created_at)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(media_id) DO UPDATE SET
            text = excluded.text, lines_json = excluded.lines_json,
            frames = excluded.frames, engine = excluded.engine,
            status = excluded.status, created_at = excluded.created_at
        """,
        (media_id, shortcode, text, json.dumps(lines, ensure_ascii=False),
         frames, engine, status, int(time.time())),
    )
    conn.commit()


def save_description(
    conn: sqlite3.Connection, *, media_id: int, shortcode: str, text: str,
    model: str, frames: int, input_tokens: int | None = None,
    output_tokens: int | None = None, status: str = "ok",
) -> None:
    conn.execute(
        """
        INSERT INTO descriptions (media_id, shortcode, text, model, frames,
                                  input_tokens, output_tokens, status, created_at)
        VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(media_id) DO UPDATE SET
            text = excluded.text, model = excluded.model,
            frames = excluded.frames, input_tokens = excluded.input_tokens,
            output_tokens = excluded.output_tokens, status = excluded.status,
            created_at = excluded.created_at
        """,
        (media_id, shortcode, text, model, frames, input_tokens, output_tokens,
         status, int(time.time())),
    )
    conn.commit()


def pending_entries(
    conn: sqlite3.Connection, *, collection: str | None = None,
    redo: bool = False, only_flagged: bool = False,
) -> list[sqlite3.Row]:
    """Posts with something to read but no triage record yet."""
    scope = f"AND {_in_collection()}" if collection else ""
    if only_flagged:
        # Re-run just what was flagged, rather than re-billing the archive.
        having = "AND e.needs_review = 1"
    else:
        having = "" if redo else "AND e.shortcode IS NULL"
    return list(
        conn.execute(
            f"""
            SELECT p.shortcode
            FROM posts p
            LEFT JOIN entries e ON e.shortcode = p.shortcode
            WHERE (
                p.caption IS NOT NULL
                OR EXISTS (SELECT 1 FROM transcripts t
                            WHERE t.shortcode = p.shortcode AND t.status = 'ok')
                OR EXISTS (SELECT 1 FROM ocr o
                            WHERE o.shortcode = p.shortcode AND o.status = 'ok')
                OR EXISTS (SELECT 1 FROM descriptions d
                            WHERE d.shortcode = p.shortcode AND d.status = 'ok')
            ) {having} {scope}
            ORDER BY p.saved_at DESC
            """,
            {"c": collection} if collection else {},
        )
    )


def save_entry(
    conn: sqlite3.Connection, *, shortcode: str, title: str, category: str,
    location: str, summary: str, highlights: list, action: str,
    practical: str, confidence: str, needs_review: bool,
    sources: list, model: str, review_reason: str = "",
    review_kind: str = "none", evidence_hash: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO entries (shortcode, title, category, location, summary,
                             highlights, action, practical, confidence,
                             needs_review, review_reason, review_kind,
                             evidence_hash, sources, model, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(shortcode) DO UPDATE SET
            title = excluded.title, category = excluded.category,
            location = excluded.location, summary = excluded.summary,
            highlights = excluded.highlights, action = excluded.action,
            practical = excluded.practical, confidence = excluded.confidence,
            needs_review = excluded.needs_review,
            review_reason = excluded.review_reason,
            review_kind = excluded.review_kind,
            evidence_hash = excluded.evidence_hash,
            sources = excluded.sources,
            model = excluded.model, created_at = excluded.created_at
        """,
        (shortcode, title, category, location, summary,
         json.dumps(highlights, ensure_ascii=False), action, practical,
         confidence, int(bool(needs_review)), review_reason, review_kind,
         evidence_hash, json.dumps(sources), model, int(time.time())),
    )
    conn.commit()


def entries(
    conn: sqlite3.Connection, *, collection: str | None = None,
    category: str | None = None, needs_review: bool | None = None,
) -> list[sqlite3.Row]:
    where = ["1"]
    params: dict = {}
    if collection:
        where.append(_in_collection())
        params["c"] = collection
    if category:
        where.append("e.category = :cat")
        params["cat"] = category
    if needs_review is not None:
        where.append(f"e.needs_review = {1 if needs_review else 0}")

    return list(
        conn.execute(
            f"""
            SELECT e.*, p.url, p.author_username, p.saved_at,
                   p.media_type, p.product_type,
                   (SELECT group_concat(pc.collection, ', ')
                    FROM post_collections pc
                    WHERE pc.shortcode = p.shortcode) AS collections
            FROM entries e
            JOIN posts p ON p.shortcode = e.shortcode
            WHERE {' AND '.join(where)}
            ORDER BY e.category, e.location, e.title
            """,
            params,
        )
    )


def transcript_for(conn: sqlite3.Connection, shortcode: str) -> dict:
    """Every track for one post, for rendering a combined transcript."""
    post = conn.execute(
        "SELECT * FROM posts WHERE shortcode = ?", (shortcode,)
    ).fetchone()
    if post is None:
        return {}

    return {
        "post": dict(post),
        "collections": [
            r["collection"] for r in conn.execute(
                "SELECT collection FROM post_collections WHERE shortcode = ? "
                "ORDER BY collection", (shortcode,))
        ],
        "voice": [
            dict(r) for r in conn.execute(
                "SELECT text, language, status FROM transcripts "
                "WHERE shortcode = ? AND status = 'ok'", (shortcode,))
        ],
        "screen_text": [
            dict(r) for r in conn.execute(
                "SELECT lines_json FROM ocr "
                "WHERE shortcode = ? AND status = 'ok'", (shortcode,))
        ],
        "description": [
            r["text"] for r in conn.execute(
                "SELECT text FROM descriptions "
                "WHERE shortcode = ? AND status = 'ok'", (shortcode,))
        ],
    }


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
        INSERT INTO search (shortcode, author, caption, transcript,
                            screen_text, description, collection)
        SELECT p.shortcode,
               COALESCE(p.author_username, ''),
               COALESCE(p.caption, ''),
               -- Only 'ok' transcripts. Discarded text is kept on the row for
               -- inspection but must never reach the index, or every silent
               -- reel becomes a hit for whatever Whisper hallucinated.
               COALESCE((SELECT group_concat(t.text, ' ')
                         FROM transcripts t
                         WHERE t.shortcode = p.shortcode AND t.status = 'ok'), ''),
               COALESCE((SELECT group_concat(o.text, ' ')
                         FROM ocr o
                         WHERE o.shortcode = p.shortcode AND o.status = 'ok'), ''),
               COALESCE((SELECT group_concat(d.text, ' ')
                         FROM descriptions d
                         WHERE d.shortcode = p.shortcode AND d.status = 'ok'), ''),
               COALESCE((SELECT group_concat(pc.collection, ' ')
                         FROM post_collections pc
                         WHERE pc.shortcode = p.shortcode), '')
        FROM posts p
        """
    )
    conn.execute(
        "INSERT INTO meta (key, value) VALUES ('index_signature', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (_index_signature(conn),),
    )
    conn.commit()
    return conn.execute("SELECT count(*) AS n FROM search").fetchone()["n"]


def _index_signature(conn: sqlite3.Connection) -> str:
    """A cheap fingerprint of everything the FTS index is built from.

    Timestamps are useless here: writes and the reindex that follows land in
    the same second, so a second-resolution watermark reports "fresh" while the
    index is empty. Counts change on every insert, and the caption-length sum
    catches hydration filling text into rows that already existed.
    """
    row = conn.execute(
        """
        SELECT (SELECT count(*) FROM posts),
               (SELECT coalesce(sum(length(caption)), 0) FROM posts),
               (SELECT count(*) FROM transcripts WHERE status = 'ok'),
               (SELECT coalesce(sum(length(text)), 0) FROM transcripts
                 WHERE status = 'ok'),
               (SELECT count(*) FROM ocr WHERE status = 'ok'),
               (SELECT coalesce(sum(length(text)), 0) FROM ocr
                 WHERE status = 'ok'),
               (SELECT count(*) FROM descriptions WHERE status = 'ok'),
               (SELECT count(*) FROM post_collections)
        """
    ).fetchone()
    return ",".join(str(v) for v in row)


def _index_is_stale(conn: sqlite3.Connection) -> bool:
    try:
        built = conn.execute(
            "SELECT value FROM meta WHERE key = 'index_signature'"
        ).fetchone()
    except sqlite3.Error:
        return True
    return built is None or built["value"] != _index_signature(conn)


def ensure_fresh_index(conn: sqlite3.Connection) -> bool:
    """Rebuild the FTS index if the source tables moved on. Returns True if it did.

    Every writer used to have to remember to call `reindex`, and a path that
    forgot left search silently returning nothing — which looks identical to
    "no matches". Checking here makes staleness impossible to ship.
    """
    if not _index_is_stale(conn):
        return False
    reindex(conn)
    return True


def _too_short_for_trigram(query: str) -> bool:
    """True when any bare term is under 3 characters.

    FTS5 operators are left to the index; a query using them goes through MATCH
    even if a term is short, because the LIKE fallback cannot express them.
    """
    if any(op in query for op in ('"', "*", "(", ")", " OR ", " NOT ", " AND ")):
        return False
    terms = [t for t in query.split() if t]
    return bool(terms) and any(len(t) < 3 for t in terms)


def _search_like(
    conn: sqlite3.Connection, query: str, limit: int, collection: str | None
) -> list[sqlite3.Row]:
    """Substring scan over the same fields the FTS index covers."""
    scope = f"AND {_in_collection()}" if collection else ""
    terms = [t for t in query.split() if t]
    # Every term must appear somewhere in the post — the same implicit AND
    # that FTS5 applies to a bare multi-word query.
    clauses, params = [], {"limit": limit}
    if collection:
        params["c"] = collection
    for i, term in enumerate(terms):
        params[f"t{i}"] = f"%{term}%"
        clauses.append(f"(s.caption LIKE :t{i} OR s.transcript LIKE :t{i} "
                       f"OR s.screen_text LIKE :t{i} OR s.description LIKE :t{i} "
                       f"OR s.author LIKE :t{i})")
    where = " AND ".join(clauses) or "1"

    return list(
        conn.execute(
            f"""
            SELECT s.shortcode, p.url, p.author_username,
                   (SELECT group_concat(pc.collection, ', ')
                    FROM post_collections pc
                    WHERE pc.shortcode = p.shortcode) AS collection,
                   substr(s.caption, 1, 120)     AS caption_hit,
                   substr(s.transcript, 1, 120)  AS transcript_hit,
                   substr(s.screen_text, 1, 120) AS screen_hit,
                   substr(s.description, 1, 120) AS description_hit
            FROM search s
            JOIN posts p ON p.shortcode = s.shortcode
            WHERE {where} {scope}
            LIMIT :limit
            """,
            params,
        )
    )


def search(
    conn: sqlite3.Connection,
    query: str,
    limit: int = 20,
    collection: str | None = None,
) -> list[sqlite3.Row]:
    ensure_fresh_index(conn)
    scope = f"AND {_in_collection()}" if collection else ""

    # Trigram cannot match a term shorter than 3 characters, which rules out
    # plenty of real queries in CJK — 東京 is two. Scan for those instead; the
    # archive is thousands of rows, not millions, so LIKE is fast enough.
    if _too_short_for_trigram(query):
        return _search_like(conn, query, limit, collection)

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
                   snippet(search, 3, '[', ']', '…', 12) AS transcript_hit,
                   snippet(search, 4, '[', ']', '…', 12) AS screen_hit,
                   snippet(search, 5, '[', ']', '…', 12) AS description_hit
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
        "screen_text": count(
            "SELECT count(*) FROM ocr o JOIN posts p ON p.shortcode = o.shortcode "
            f"WHERE o.status = 'ok' {and_}"),
        "described": count(
            "SELECT count(*) FROM descriptions d "
            f"JOIN posts p ON p.shortcode = d.shortcode WHERE d.status = 'ok' {and_}"),
        "collections": count(
            "SELECT count(DISTINCT collection) FROM post_collections"),
    }

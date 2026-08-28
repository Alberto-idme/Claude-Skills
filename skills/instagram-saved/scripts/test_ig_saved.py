"""Offline tests — everything that does not need a network or a session.

    python3 -m pytest test_ig_saved.py -q
    python3 test_ig_saved.py            # no pytest required
"""

from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ig_saved import db  # noqa: E402
from ig_saved.config import Config  # noqa: E402
from ig_saved.normalize import (  # noqa: E402
    MediaRef,
    Post,
    from_apify,
    from_private_media,
    parse_collection_url,
    shortcode_from_url,
    shortcode_to_pk,
    walk_export,
)
from ig_saved.sources.export import iter_export  # noqa: E402

_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def _pk_to_shortcode(pk: int) -> str:
    """Inverse of shortcode_to_pk, for round-trip checking only."""
    out = ""
    while pk:
        pk, rem = divmod(pk, 64)
        out = _B64[rem] + out
    return out or "A"


# ---------------------------------------------------------------------------
# URL parsing
# ---------------------------------------------------------------------------


def test_parse_collection_url():
    url = "https://www.instagram.com/tolis/saved/japan/18075071974439078/"
    assert parse_collection_url(url) == ("tolis", "japan", "18075071974439078")


def test_parse_collection_url_bare_id():
    assert parse_collection_url("18075071974439078") == (None, None, "18075071974439078")


def test_parse_collection_url_rejects_post_url():
    assert parse_collection_url("https://www.instagram.com/p/ABC123/") is None


def test_shortcode_from_url_variants():
    cases = {
        "https://www.instagram.com/p/CqxU1FzL0Dg/": "CqxU1FzL0Dg",
        "https://instagram.com/reel/Cx-9_aBcDeF/?igshid=1": "Cx-9_aBcDeF",
        "https://www.instagram.com/tolis/reel/Cz1234abcd/": "Cz1234abcd",
        "https://www.instagram.com/tv/CyAbCdEfGh/": "CyAbCdEfGh",
    }
    for url, expected in cases.items():
        assert shortcode_from_url(url) == expected, url


def test_shortcode_from_url_ignores_profiles():
    assert shortcode_from_url("https://www.instagram.com/tolis/") is None


# ---------------------------------------------------------------------------
# shortcode <-> pk
# ---------------------------------------------------------------------------


def test_shortcode_to_pk_known_small():
    assert shortcode_to_pk("A") == 0
    assert shortcode_to_pk("B") == 1
    assert shortcode_to_pk("BA") == 64


def test_shortcode_to_pk_roundtrip():
    for pk in (1, 63, 64, 12345678901234567, 3_000_000_000_000_000_000):
        assert shortcode_to_pk(_pk_to_shortcode(pk)) == pk


def test_shortcode_to_pk_rejects_bad_chars():
    assert shortcode_to_pk("!!!") is None
    assert shortcode_to_pk("") is None


def test_shortcode_to_pk_ignores_carousel_suffix():
    # Anything past 11 chars addresses a child, not the post.
    assert shortcode_to_pk("CqxU1FzL0Dg") == shortcode_to_pk("CqxU1FzL0DgXXXX")


# ---------------------------------------------------------------------------
# export parsing
# ---------------------------------------------------------------------------

EXPORT_BLOB = {
    "saved_saved_media": [
        {
            "title": "kyoto_eats",
            "string_map_data": {
                "Saved on": {
                    "href": "https://www.instagram.com/p/CqxU1FzL0Dg/",
                    "timestamp": 1699999999,
                }
            },
        },
        {
            "title": "tokyo_walks",
            "string_map_data": {
                "Saved on": {
                    "href": "https://www.instagram.com/reel/Cx-9_aBcDeF/",
                    "timestamp": 1700000000,
                }
            },
        },
    ]
}


def test_walk_export_extracts_posts():
    posts = list(walk_export(EXPORT_BLOB))
    assert len(posts) == 2
    first = posts[0]
    assert first.shortcode == "CqxU1FzL0Dg"
    assert first.author_username == "kyoto_eats"
    assert first.saved_at == 1699999999
    assert first.url == "https://www.instagram.com/p/CqxU1FzL0Dg/"
    assert first.source == "export"


def test_walk_export_survives_renamed_keys():
    """Meta reshapes this file; the walker keys off href, not the layout."""
    mutated = {
        "some_new_wrapper": {
            "entries": [
                {
                    "title": "kyoto_eats",
                    "totally_new_name": {
                        "Bookmarked at": {
                            "href": "https://www.instagram.com/p/CqxU1FzL0Dg/",
                            "timestamp": 1699999999,
                        }
                    },
                }
            ]
        }
    }
    posts = list(walk_export(mutated))
    assert len(posts) == 1
    assert posts[0].author_username == "kyoto_eats"


def test_walk_export_ignores_non_post_hrefs():
    blob = {"x": [{"title": "a", "d": {"k": {"href": "https://example.com/p/x/"}}}]}
    assert list(walk_export(blob)) == []


COLLECTIONS_BLOB = {
    "saved_saved_collections": [
        {"title": "japan", "string_map_data": {"Name": {"value": "japan"}}},
        {
            "title": "japan",
            "string_map_data": {
                "Added on": {
                    "href": "https://www.instagram.com/p/CzAbCdEfGhI/",
                    "timestamp": 1700000500,
                }
            },
        },
    ]
}


def test_collections_file_titles_are_collections_not_authors():
    posts = list(walk_export(COLLECTIONS_BLOB, titles_are_collections=True))
    assert len(posts) == 1
    assert posts[0].collection == "japan"
    assert posts[0].author_username is None  # 'japan' is not a person


def test_export_merges_author_and_collection_for_the_same_post():
    """A post can be in both files; each contributes the half the other lacks."""
    shared = "https://www.instagram.com/p/CqxU1FzL0Dg/"
    posts_file = {
        "saved_saved_media": [
            {"title": "kyoto_eats",
             "string_map_data": {"Saved on": {"href": shared, "timestamp": 1}}}
        ]
    }
    collections_file = {
        "saved_saved_collections": [
            {"title": "japan",
             "string_map_data": {"Added on": {"href": shared, "timestamp": 2}}}
        ]
    }
    with tempfile.TemporaryDirectory() as tmp:
        conn = _tmp_db(tmp)
        db.upsert_posts(conn, walk_export(posts_file))
        db.upsert_posts(conn, walk_export(collections_file,
                                          titles_are_collections=True))
        row = conn.execute("SELECT * FROM posts").fetchone()
        assert row["author_username"] == "kyoto_eats"
        assert row["collection"] == "japan"


def test_iter_export_labels_collections_correctly():
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "export.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("saved/saved_posts.json", json.dumps(EXPORT_BLOB))
            zf.writestr("saved/saved_collections.json", json.dumps(COLLECTIONS_BLOB))
        by_code = {p.shortcode: p for p in iter_export(archive)}

    assert by_code["CqxU1FzL0Dg"].author_username == "kyoto_eats"
    assert by_code["CqxU1FzL0Dg"].collection is None
    assert by_code["CzAbCdEfGhI"].collection == "japan"
    assert by_code["CzAbCdEfGhI"].author_username is None


def test_iter_export_reads_zip():
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "instagram-export.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr(
                "your_instagram_activity/saved/saved_posts.json",
                json.dumps(EXPORT_BLOB),
            )
            zf.writestr("personal_information/profile.json", "{}")
        posts = list(iter_export(archive))
    assert {p.shortcode for p in posts} == {"CqxU1FzL0Dg", "Cx-9_aBcDeF"}


def test_iter_export_reports_missing_saved_file():
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "empty.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("personal_information/profile.json", "{}")
        try:
            list(iter_export(archive))
        except LookupError as exc:
            assert "index --source browser" in str(exc)
        else:
            raise AssertionError("expected LookupError")


# ---------------------------------------------------------------------------
# private API normalisation
# ---------------------------------------------------------------------------

PRIVATE_CAROUSEL = {
    "media": {
        "code": "CqxU1FzL0Dg",
        "pk": 3000000000000000000,
        "taken_at": 1699000000,
        "media_type": 8,
        "product_type": "carousel_container",
        "like_count": 12,
        "comment_count": 3,
        "caption": {"text": "Kyoto in November"},
        "user": {"username": "kyoto_eats", "full_name": "Kyoto Eats"},
        "carousel_media": [
            {
                "image_versions2": {
                    "candidates": [{"url": "https://cdn/img0.jpg", "width": 1080,
                                    "height": 1350}]
                }
            },
            {
                "video_versions": [
                    {"url": "https://cdn/vid1.mp4", "width": 720, "height": 1280}
                ]
            },
        ],
    }
}


def test_from_private_media_unwraps_and_maps():
    post = from_private_media(PRIVATE_CAROUSEL, collection="japan")
    assert post.shortcode == "CqxU1FzL0Dg"
    assert post.caption == "Kyoto in November"
    assert post.author_username == "kyoto_eats"
    assert post.media_type == "carousel"
    assert post.collection == "japan"
    assert [m.kind for m in post.media] == ["image", "video"]
    assert post.media[1].remote_url == "https://cdn/vid1.mp4"


def test_from_private_media_single_video():
    post = from_private_media(
        {
            "code": "Cx-9_aBcDeF",
            "media_type": 2,
            "user": {"username": "tokyo_walks"},
            "video_versions": [{"url": "https://cdn/v.mp4"}],
        }
    )
    assert post.media_type == "video"
    assert len(post.media) == 1
    assert post.media[0].kind == "video"


def test_from_private_media_requires_code():
    assert from_private_media({"pk": 1}) is None


# ---------------------------------------------------------------------------
# Apify normalisation
# ---------------------------------------------------------------------------


def test_from_apify_camel_case():
    post = from_apify(
        {
            "shortCode": "CqxU1FzL0Dg",
            "url": "https://www.instagram.com/p/CqxU1FzL0Dg/",
            "caption": "Kyoto in November",
            "ownerUsername": "kyoto_eats",
            "type": "Video",
            "videoUrl": "https://cdn/v.mp4",
            "likesCount": 12,
            "timestamp": "2023-11-14T12:00:00.000Z",
        }
    )
    assert post.shortcode == "CqxU1FzL0Dg"
    assert post.media_type == "video"
    assert post.media[0].remote_url == "https://cdn/v.mp4"
    assert post.like_count == 12
    assert post.taken_at == 1699963200


def test_from_apify_alternate_spellings():
    post = from_apify(
        {
            "url": "https://www.instagram.com/p/Cx-9_aBcDeF/",
            "text": "alt caption field",
            "username": "tokyo_walks",
            "display_url": "https://cdn/i.jpg",
        }
    )
    assert post.shortcode == "Cx-9_aBcDeF"
    assert post.caption == "alt caption field"
    assert post.author_username == "tokyo_walks"
    assert post.media[0].kind == "image"


def test_from_apify_sidecar_children():
    post = from_apify(
        {
            "shortCode": "CqxU1FzL0Dg",
            "type": "Sidecar",
            "childPosts": [
                {"displayUrl": "https://cdn/0.jpg"},
                {"videoUrl": "https://cdn/1.mp4"},
            ],
        }
    )
    assert post.media_type == "carousel"
    assert [m.kind for m in post.media] == ["image", "video"]


def test_from_apify_unusable_record():
    assert from_apify({"caption": "no id anywhere"}) is None


# ---------------------------------------------------------------------------
# database
# ---------------------------------------------------------------------------


def _tmp_db(tmp: str):
    cfg = Config(root=Path(tmp))
    cfg.ensure_dirs()
    return db.connect(cfg.db_path)


def test_upsert_counts_new_and_updated():
    with tempfile.TemporaryDirectory() as tmp:
        conn = _tmp_db(tmp)
        post = Post(shortcode="A1", url="https://www.instagram.com/p/A1/")
        assert db.upsert_posts(conn, [post]) == (1, 0)
        assert db.upsert_posts(conn, [post]) == (0, 1)


def test_hydration_never_blanks_indexed_fields():
    """Index gives saved_at; hydrate gives caption. Neither may erase the other."""
    with tempfile.TemporaryDirectory() as tmp:
        conn = _tmp_db(tmp)
        db.upsert_posts(
            conn,
            [Post(shortcode="A1", url="u", saved_at=1700000000,
                  author_username="kyoto_eats", collection="japan",
                  source="export")],
        )
        db.upsert_posts(
            conn,
            [Post(shortcode="A1", url="u", caption="hydrated caption",
                  media=[MediaRef(0, "image", "https://cdn/i.jpg")],
                  source="apify")],
        )
        row = conn.execute("SELECT * FROM posts WHERE shortcode='A1'").fetchone()
        assert row["saved_at"] == 1700000000
        assert row["author_username"] == "kyoto_eats"
        assert row["collection"] == "japan"
        assert row["caption"] == "hydrated caption"
        assert row["hydrated_at"] is not None


def test_pending_hydration_excludes_hydrated():
    with tempfile.TemporaryDirectory() as tmp:
        conn = _tmp_db(tmp)
        db.upsert_posts(conn, [Post(shortcode="A1", url="u")])
        db.upsert_posts(conn, [Post(shortcode="A2", url="u", caption="done")])
        assert db.pending_hydration(conn) == ["A1"]


def test_media_rows_are_deduped_by_index():
    with tempfile.TemporaryDirectory() as tmp:
        conn = _tmp_db(tmp)
        for url in ("https://cdn/old.jpg", "https://cdn/fresh.jpg"):
            db.upsert_posts(
                conn,
                [Post(shortcode="A1", url="u", media=[MediaRef(0, "image", url)])],
            )
        rows = list(conn.execute("SELECT remote_url FROM media WHERE shortcode='A1'"))
        assert len(rows) == 1
        assert rows[0]["remote_url"] == "https://cdn/fresh.jpg"


def test_pending_downloads_and_mark():
    with tempfile.TemporaryDirectory() as tmp:
        conn = _tmp_db(tmp)
        db.upsert_posts(
            conn,
            [Post(shortcode="A1", url="u",
                  media=[MediaRef(0, "video", "https://cdn/v.mp4")])],
        )
        pending = db.pending_downloads(conn)
        assert len(pending) == 1
        db.mark_downloaded(conn, pending[0]["id"], "/tmp/v.mp4")
        assert db.pending_downloads(conn) == []


def test_transcripts_become_searchable():
    with tempfile.TemporaryDirectory() as tmp:
        conn = _tmp_db(tmp)
        db.upsert_posts(
            conn,
            [Post(shortcode="A1", url="https://www.instagram.com/p/A1/",
                  author_username="kyoto_eats", caption="no keyword here",
                  media=[MediaRef(0, "video", "https://cdn/v.mp4")])],
        )
        media_id = db.pending_downloads(conn)[0]["id"]
        db.mark_downloaded(conn, media_id, "/tmp/v.mp4")
        db.save_transcript(
            conn, media_id=media_id, shortcode="A1",
            text="the best tonkotsu ramen in Fukuoka",
            segments=[{"start": 0.0, "end": 2.0, "text": "the best tonkotsu ramen"}],
            language="en", model="faster-whisper:small",
        )
        db.reindex(conn)

        assert [r["shortcode"] for r in db.search(conn, "tonkotsu")] == ["A1"]
        assert db.search(conn, "kyoto_eats")  # author is indexed too
        assert db.search(conn, "nonexistentterm") == []


def test_pending_transcripts_only_downloaded_videos():
    with tempfile.TemporaryDirectory() as tmp:
        conn = _tmp_db(tmp)
        db.upsert_posts(
            conn,
            [
                Post(shortcode="V1", url="u",
                     media=[MediaRef(0, "video", "https://cdn/v.mp4")]),
                Post(shortcode="I1", url="u",
                     media=[MediaRef(0, "image", "https://cdn/i.jpg")]),
            ],
        )
        assert db.pending_transcripts(conn) == []  # nothing downloaded yet

        for row in db.pending_downloads(conn):
            db.mark_downloaded(conn, row["id"], f"/tmp/{row['shortcode']}")

        pending = db.pending_transcripts(conn)
        assert [r["shortcode"] for r in pending] == ["V1"]  # images excluded


def test_stats_shape():
    with tempfile.TemporaryDirectory() as tmp:
        conn = _tmp_db(tmp)
        db.upsert_posts(conn, [Post(shortcode="A1", url="u", collection="japan")])
        s = db.stats(conn)
        assert s["posts"] == 1 and s["collections"] == 1


# ---------------------------------------------------------------------------
# transcription plumbing
#
# The model itself is third-party; what needs testing is everything around it —
# backend selection, which media get picked up, and the write into FTS.
# ---------------------------------------------------------------------------


def _stub_backend(segments, language="en"):
    from ig_saved import transcribe as t

    calls = []

    def fake(path):
        calls.append(path)
        return segments, language

    t._BACKEND = ("stub-whisper", fake)
    return t, calls


def test_transcribe_writes_rows_and_indexes_them():
    from ig_saved.config import Config as Cfg

    t, calls = _stub_backend(
        [{"start": 0.0, "end": 2.0, "text": "the best tonkotsu in Fukuoka"},
         {"start": 2.0, "end": 4.0, "text": "open until midnight"}]
    )
    try:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Cfg(root=Path(tmp))
            cfg.ensure_dirs()
            conn = db.connect(cfg.db_path)
            db.upsert_posts(
                conn,
                [Post(shortcode="V1", url="https://www.instagram.com/p/V1/",
                      caption="no keyword in the caption",
                      media=[MediaRef(0, "video", "https://cdn/v.mp4")])],
            )
            video = Path(tmp) / "v.mp4"
            video.write_bytes(b"not really a video")
            media_id = db.pending_downloads(conn)[0]["id"]
            db.mark_downloaded(conn, media_id, str(video))

            counts = t.transcribe_all(conn, cfg)
            assert counts["transcribed"] == 1, counts
            assert len(calls) == 1

            row = conn.execute("SELECT * FROM transcripts").fetchone()
            assert "tonkotsu" in row["text"]
            assert "midnight" in row["text"]
            assert json.loads(row["segments_json"])[0]["start"] == 0.0
            assert row["language"] == "en"

            db.reindex(conn)
            # Found by spoken words that appear nowhere in the caption.
            assert [r["shortcode"] for r in db.search(conn, "tonkotsu")] == ["V1"]
    finally:
        t._BACKEND = None


def test_transcribe_skips_missing_files_without_failing():
    from ig_saved.config import Config as Cfg

    t, calls = _stub_backend([{"start": 0, "end": 1, "text": "x"}])
    try:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Cfg(root=Path(tmp))
            cfg.ensure_dirs()
            conn = db.connect(cfg.db_path)
            db.upsert_posts(
                conn,
                [Post(shortcode="V1", url="u",
                      media=[MediaRef(0, "video", "https://cdn/v.mp4")])],
            )
            media_id = db.pending_downloads(conn)[0]["id"]
            db.mark_downloaded(conn, media_id, "/nonexistent/gone.mp4")

            counts = t.transcribe_all(conn, cfg)
            assert counts == {"transcribed": 0, "skipped": 1, "failed": 0}
            assert calls == []
    finally:
        t._BACKEND = None


def test_transcribe_survives_a_bad_video():
    from ig_saved.config import Config as Cfg
    from ig_saved import transcribe as t

    def explode(path):
        raise RuntimeError("could not decode audio")

    t._BACKEND = ("stub-whisper", explode)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Cfg(root=Path(tmp))
            cfg.ensure_dirs()
            conn = db.connect(cfg.db_path)
            db.upsert_posts(
                conn,
                [Post(shortcode="V1", url="u",
                      media=[MediaRef(0, "video", "https://cdn/v.mp4")]),
                 Post(shortcode="V2", url="u",
                      media=[MediaRef(0, "video", "https://cdn/w.mp4")])],
            )
            for row in db.pending_downloads(conn):
                path = Path(tmp) / f"{row['shortcode']}.mp4"
                path.write_bytes(b"x")
                db.mark_downloaded(conn, row["id"], str(path))

            counts = t.transcribe_all(conn, cfg)
            # One bad reel must not abort the rest of the archive.
            assert counts["failed"] == 2 and counts["transcribed"] == 0
    finally:
        t._BACKEND = None


def test_doctor_runs_and_reports():
    from ig_saved import doctor
    from ig_saved.config import Config as Cfg

    with tempfile.TemporaryDirectory() as tmp:
        cfg = Cfg(root=Path(tmp))
        cfg.ensure_dirs()
        code = doctor.run(cfg)
        assert code in (0, 1)  # depends on the host, but must not raise


# ---------------------------------------------------------------------------
# Apify input building
# ---------------------------------------------------------------------------


def test_apify_input_object_vs_string_style():
    from ig_saved.hydrate.apify import build_input

    cfg = Config()
    cfg.apify_url_field = "startUrls"
    payload = build_input(cfg, ["https://www.instagram.com/p/A1/"])
    assert payload["startUrls"] == [{"url": "https://www.instagram.com/p/A1/"}]

    cfg.apify_url_field = "directUrls"
    payload = build_input(cfg, ["https://www.instagram.com/p/A1/"])
    assert payload["directUrls"] == ["https://www.instagram.com/p/A1/"]


def test_apify_actor_path_uses_tilde():
    from ig_saved.hydrate.apify import _actor_path

    assert _actor_path("patient_discovery/instagram-posts") == (
        "patient_discovery~instagram-posts"
    )


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------


def test_cli_parses_the_test_collection_url():
    from ig_saved.cli import build_parser

    args = build_parser().parse_args(
        ["index", "--source", "browser", "--collection",
         "https://www.instagram.com/tolis/saved/japan/18075071974439078/"]
    )
    assert args.source == "browser"
    assert parse_collection_url(args.collection)[2] == "18075071974439078"


def test_cli_subcommands_exist():
    from ig_saved.cli import build_parser

    parser = build_parser()
    for command in ("login", "collections", "index", "hydrate", "media",
                    "transcribe", "search", "stats", "dump", "sync"):
        assert parser.parse_args([command] if command != "search"
                                 else [command, "q"])


def _run() -> int:
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"  ok   {name}")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL {name}: {exc}")
            failed.append(name)
    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run())

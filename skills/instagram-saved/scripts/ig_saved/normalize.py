"""Shape-tolerant normalisers.

Three upstreams feed this tool and none of them agree on field names:

* Meta's "Download your information" export (JSON), whose layout Meta reshapes
  every year or so;
* Instagram's private ``/api/v1/`` responses, which use the mobile app's schema;
* Apify actor datasets, whose fields differ per actor and per publisher.

So every parser here reads defensively: try the keys we know, fall back to a
generic walk, and never assume a key exists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterator

SHORTCODE_RE = re.compile(
    r"instagram\.com/(?:[^/?#]+/)??(?:p|reel|reels|tv)/([A-Za-z0-9_-]{5,})"
)

# https://www.instagram.com/<user>/saved/<slug>/<collection_id>/
COLLECTION_URL_RE = re.compile(
    r"instagram\.com/([^/?#]+)/saved/([^/?#]+)/(\d+)"
)

# Private-API media_type ints.
_MEDIA_TYPE = {1: "image", 2: "video", 8: "carousel"}


@dataclass
class MediaRef:
    idx: int
    kind: str  # "image" | "video"
    remote_url: str | None = None
    width: int | None = None
    height: int | None = None


@dataclass
class Post:
    shortcode: str
    url: str
    media_id: str | None = None
    author_username: str | None = None
    author_full_name: str | None = None
    caption: str | None = None
    taken_at: int | None = None
    saved_at: int | None = None
    media_type: str | None = None
    product_type: str | None = None
    like_count: int | None = None
    comment_count: int | None = None
    collection: str | None = None
    source: str | None = None
    media: list[MediaRef] = field(default_factory=list)
    raw: dict[str, Any] | None = None


def post_url(shortcode: str) -> str:
    return f"https://www.instagram.com/p/{shortcode}/"


def shortcode_from_url(url: str) -> str | None:
    m = SHORTCODE_RE.search(url or "")
    return m.group(1) if m else None


def parse_collection_url(value: str) -> tuple[str | None, str | None, str] | None:
    """Accept a full saved-collection URL or a bare numeric id.

    Returns ``(owner, slug, collection_id)``. Saved collections are private to
    the account that made them, so ``owner`` is who you must be logged in as.
    """
    value = (value or "").strip()
    if value.isdigit():
        return (None, None, value)
    m = COLLECTION_URL_RE.search(value)
    if m:
        return (m.group(1), m.group(2), m.group(3))
    return None


def _first(d: dict, *keys, default=None):
    for k in keys:
        v = d.get(k)
        if v not in (None, "", []):
            return v
    return default


# --------------------------------------------------------------------------
# Meta "Download your information" export
# --------------------------------------------------------------------------


def walk_export(
    obj: Any,
    collection: str | None = None,
    *,
    titles_are_collections: bool = False,
) -> Iterator[Post]:
    """Recursively harvest saved posts from an export blob.

    Rather than bind to ``saved_saved_media`` -> ``string_map_data`` -> ``Saved
    on`` (which Meta has renamed more than once), walk the whole tree and take
    any dict carrying an ``href`` that looks like a post permalink. A sibling
    ``timestamp`` is when it was saved.

    The nearest enclosing ``title`` means different things in the two files
    Meta ships: in ``saved_posts.json`` it is the author's handle, but in
    ``saved_collections.json`` it is the name of the collection and no author
    is recorded at all. ``titles_are_collections`` picks the reading, because
    guessing wrong stamps every post with a bogus author.
    """
    yield from _walk(
        obj,
        collection=collection,
        title=None,
        titles_are_collections=titles_are_collections,
    )


def _walk(
    obj: Any,
    *,
    collection: str | None,
    title: str | None,
    titles_are_collections: bool,
) -> Iterator[Post]:
    if isinstance(obj, dict):
        local_title = obj.get("title") if isinstance(obj.get("title"), str) else title

        href = obj.get("href")
        if isinstance(href, str):
            code = shortcode_from_url(href)
            if code:
                ts = obj.get("timestamp")
                yield Post(
                    shortcode=code,
                    url=post_url(code),
                    author_username=None if titles_are_collections else title,
                    saved_at=int(ts) if isinstance(ts, (int, float)) and ts else None,
                    collection=(title or collection) if titles_are_collections
                    else collection,
                    source="export",
                )
                return

        # `string_map_data` holds the href, but `title` is its sibling one level
        # up, so carry the enclosing title down.
        for value in obj.values():
            yield from _walk(value, collection=collection, title=local_title,
                             titles_are_collections=titles_are_collections)

    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item, collection=collection, title=title,
                             titles_are_collections=titles_are_collections)


# --------------------------------------------------------------------------
# Private API (/api/v1/...)
# --------------------------------------------------------------------------


def _usable(version: dict) -> bool:
    """Reject Instagram's placeholder stand-ins.

    Some carousel slots come back with static.cdninstagram.com/rsrc.php/null.jpg
    instead of real media. Stored as-is they become permanently undownloadable
    rows — every fetch 400s, and re-hydrating returns the same placeholder — so
    they never stop showing up as failures.
    """
    url = (version or {}).get("url") or ""
    return bool(url) and "rsrc.php" not in url


def _media_refs(media: dict) -> list[MediaRef]:
    refs: list[MediaRef] = []

    def one(node: dict, idx: int) -> MediaRef | None:
        videos = [v for v in (node.get("video_versions") or []) if _usable(v)]
        if videos:
            best = videos[0]
            return MediaRef(idx, "video", best.get("url"),
                            best.get("width"), best.get("height"))
        candidates = [c for c in
                      ((node.get("image_versions2") or {}).get("candidates")) or []
                      if _usable(c)]
        if candidates:
            best = candidates[0]  # candidates are ordered largest-first
            return MediaRef(idx, "image", best.get("url"),
                            best.get("width"), best.get("height"))
        return None

    children = media.get("carousel_media")
    if children:
        for i, child in enumerate(children):
            ref = one(child, i)
            if ref:
                refs.append(ref)
    else:
        ref = one(media, 0)
        if ref:
            refs.append(ref)
    return refs


def from_private_media(
    media: dict,
    *,
    collection: str | None = None,
    saved_at: int | None = None,
) -> Post | None:
    """Normalise one item from a private-API feed response."""
    # Saved feeds wrap each entry as {"media": {...}}; other feeds don't.
    if "media" in media and isinstance(media["media"], dict):
        media = media["media"]

    code = media.get("code")
    if not code:
        return None

    user = media.get("user") or {}
    pk = media.get("pk") or (media.get("id") or "").split("_")[0]

    return Post(
        shortcode=code,
        url=post_url(code),
        media_id=str(pk) if pk else None,
        author_username=user.get("username"),
        author_full_name=user.get("full_name"),
        caption=(media.get("caption") or {}).get("text"),
        taken_at=media.get("taken_at"),
        saved_at=saved_at,
        media_type=_MEDIA_TYPE.get(media.get("media_type")),
        product_type=media.get("product_type"),
        like_count=media.get("like_count"),
        comment_count=media.get("comment_count"),
        collection=collection,
        source="browser",
        media=_media_refs(media),
        raw=media,
    )


# --------------------------------------------------------------------------
# Apify dataset items
# --------------------------------------------------------------------------

_APIFY_TYPE = {"image": "image", "video": "video", "sidecar": "carousel",
               "carousel": "carousel", "graphimage": "image",
               "graphvideo": "video", "graphsidecar": "carousel"}


def from_apify(item: dict) -> Post | None:
    """Normalise one Apify dataset record.

    Actors disagree on field names, so try every spelling seen in the wild
    before giving up.
    """
    code = _first(item, "shortCode", "shortcode", "code")
    url = _first(item, "url", "postUrl", "permalink", "link")
    if not code and url:
        code = shortcode_from_url(url)
    if not code:
        return None

    raw_type = str(_first(item, "type", "mediaType", "productType", default="")).lower()
    media_type = _APIFY_TYPE.get(raw_type)

    refs: list[MediaRef] = []
    children = _first(item, "childPosts", "children", "sidecarChildren", default=[])
    if isinstance(children, list) and children:
        for i, child in enumerate(children):
            video = _first(child, "videoUrl", "video_url")
            image = _first(child, "displayUrl", "display_url", "imageUrl", "thumbnailUrl")
            if video:
                refs.append(MediaRef(i, "video", video))
            elif image:
                refs.append(MediaRef(i, "image", image))
        media_type = media_type or "carousel"
    else:
        video = _first(item, "videoUrl", "video_url")
        image = _first(item, "displayUrl", "display_url", "imageUrl", "thumbnailUrl")
        if video:
            refs.append(MediaRef(0, "video", video))
        elif image:
            refs.append(MediaRef(0, "image", image))

    ts = _first(item, "timestamp", "takenAt", "taken_at")
    taken_at = None
    if isinstance(ts, (int, float)):
        taken_at = int(ts)
    elif isinstance(ts, str):
        taken_at = _iso_to_epoch(ts)

    return Post(
        shortcode=code,
        url=url or post_url(code),
        media_id=_first(item, "id", "postId"),
        author_username=_first(item, "ownerUsername", "username", "owner_username"),
        author_full_name=_first(item, "ownerFullName", "fullName"),
        caption=_first(item, "caption", "text", "description"),
        taken_at=taken_at,
        media_type=media_type,
        like_count=_first(item, "likesCount", "likeCount", "likes"),
        comment_count=_first(item, "commentsCount", "commentCount", "comments"),
        source="apify",
        media=refs,
        raw=item,
    )


# --------------------------------------------------------------------------
# Shortcode <-> media id
# --------------------------------------------------------------------------

_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def shortcode_to_pk(shortcode: str) -> int | None:
    """Decode a shortcode into its numeric media id.

    A shortcode is the media's primary key in base64 with a URL-safe alphabet,
    so this is a local computation — no lookup request needed. Anything past
    the first 11 characters encodes a carousel child, not the post.
    """
    if not shortcode:
        return None
    pk = 0
    for char in shortcode[:11]:
        index = _B64.find(char)
        if index < 0:
            return None
        pk = pk * 64 + index
    return pk


def _iso_to_epoch(value: str) -> int | None:
    from datetime import datetime

    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None

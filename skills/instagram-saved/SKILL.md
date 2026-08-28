---
name: instagram-saved
version: 0.1.0
description: |
  Index, archive, transcribe and full-text search your own Instagram saved posts
  and saved collections. Handles the two-stage problem: getting the private list
  of what you saved (only your session can do this), then hydrating each
  permalink into captions, images, videos and reel transcripts. Use when asked to
  back up, export, search, or analyse Instagram saved posts / bookmarks /
  collections.
triggers:
  - export my instagram saved posts
  - scrape instagram saved collection
  - search my saved reels
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

## The constraint that shapes everything

**No Meta API exposes saved posts.** Not the Instagram Graph API, not the API
with Instagram Login, and Basic Display sunset in December 2024. Official APIs
reach only accounts you own or manage — your media, your insights, your
comments. Saved posts have never been in any of them. There is no OAuth path
here, so don't go looking for one.

That splits the job in two, and the split is the design:

| Stage | Needs | Who can run it |
|-------|-------|----------------|
| **1. Index** — the list of saved permalinks | your own session | only you |
| **2. Hydrate** — caption, media, author per post | nothing (posts are public) | anywhere |

Stage 1 has two implementations, chosen at runtime. Stage 2 has two as well.

## Quick start

```bash
cd scripts && ./setup.sh          # venv, deps, chromium, environment check
source .venv/bin/activate

python -m ig_saved.cli doctor       # what's present, what's missing, how to fix
python -m ig_saved.cli login        # once; a window opens, sign in by hand
python -m ig_saved.cli collections  # find collection ids
python -m ig_saved.cli sync --source browser \
    --collection https://www.instagram.com/<you>/saved/<name>/<id>/
python -m ig_saved.cli search "ramen"
```

`login` needs an interactive browser window and the user's own credentials, so
it cannot run headless or in a sandbox. Never ask for their password — the
whole point of the persistent profile is that they type it into Chrome
themselves, once.

When anything fails, run `doctor` first: it distinguishes a missing browser
from a stale session from an absent Whisper backend, each of which otherwise
surfaces as a different error at a different stage.

## Choosing a Stage 1 source

**`--source export`** — Meta's "Download your information" archive. Sanctioned,
zero account risk, includes collection names. But it is one-shot (re-syncing
means requesting a new export, which takes hours to days) and carries only
permalinks, so Stage 2 is mandatory. Request it under Settings → Accounts
Center → Your information and permissions → Download your information, **JSON
format**. The HTML export is not parseable and is not supported.

**`--source browser`** — a persistent Chrome profile you log into once, calling
the same JSON endpoints the web app uses. Incremental, re-runnable, and returns
fully-hydrated posts in one pass, so Stage 2 is usually unnecessary. This uses
undocumented endpoints and is against Instagram's Terms of Use.

Rule of thumb: **export** for a one-time archive, **browser** for anything that
needs to stay current.

## Choosing a Stage 2 route

**`--via apify`** keeps the fetch volume off your account entirely — you never
share your session with a third party, and the traffic that looks like scraping
isn't yours. Costs roughly $2.50/1,000 posts. Actor input schemas vary by
publisher, so check with `--dry-run` before spending credits, and set
`--apify-url-field` if the actor rejects the payload.

**`--via browser`** reuses your own session. No third party, no cost, but the
requests are yours. It is also the only route that can still see a post whose
author has since gone private.

## Account safety

The browser paths violate Instagram's Terms of Use. This is built for archiving
your own saved posts; it is not built for bulk collection, and it should not be
pointed at anything else.

- Default pacing is 1.5–4s between requests, jittered. `--slow` doubles it.
- Run it from your own machine. A residential IP running a real browser profile
  is the whole point; a datacenter IP replaying a copied cookie is the pattern
  that gets flagged.
- On HTTP 429 the tool stops and refuses to continue. Wait hours, not minutes.
  Pushing through a rate limit is how accounts get checkpointed.
- Every stage is resumable. Interrupting is always safe.

## Commands

| Command | What it does |
|---------|--------------|
| `doctor` | Check the environment; print the fix for anything missing |
| `login` | Sign in once; the session is reused thereafter |
| `collections` | List your saved collections with their ids |
| `index` | Stage 1 — build the list of saved posts |
| `hydrate` | Stage 2 — fetch captions and media URLs |
| `media` | Download images and videos |
| `transcribe` | Whisper-transcribe saved reels |
| `search` | FTS5 over captions **and** transcripts |
| `stats` / `dump` | Inspect, or export everything as JSONL |
| `sync` | index → hydrate → media → transcribe in one pass |

## Scaling

Past a few hundred posts, keep transcription out of the main pass — it is
orders of magnitude slower than indexing and downloading, and CDN URLs expire
within hours, so anything queued behind it goes stale:

```bash
ig-saved sync --source browser --all-collections --skip-transcribe
ig-saved transcribe --limit 200
```

Observed ratio on a real archive: 1 post ≈ 3 media files ≈ 2 videos. A
1,500-post account is ~4,500 files, ~3,000 reels, ~10 GB, and 12–24 hours of
CPU transcription against minutes for everything else.

## Notes for whoever works on this next

- **CDN URLs expire within hours.** Download promptly. When `media` reports
  expired URLs, the fix is `hydrate --only-expired` for fresh ones, never a
  retry of the stale URL.
- **Never DOM-scrape the saved grid.** It is virtualised — nodes are recycled
  as you scroll, so scraping silently drops posts. Use the JSON endpoints.
- **The export format drifts.** Meta has renamed these keys more than once, so
  `walk_export` keys off any `href` that looks like a permalink rather than a
  fixed path. Keep it that way.
- **`title` means two different things** in the export: the author's handle in
  `saved_posts.json`, the collection name in `saved_collections.json`. Reading
  it wrong stamps every post with a bogus author.
- **The browser path has a mock.** `test_browser_e2e.py` runs the real
  `BrowserSession` against a local server speaking Instagram's JSON shapes, so
  a broken cursor key or evaluate() signature fails there rather than on
  someone's account. Point the session at it with `IG_SAVED_BASE_URL`.
- **A post belongs to many collections.** The label lives in
  `post_collections`, never on the post — `posts.collection` is a first-seen
  display convenience only. Filtering on it silently loses every post that was
  indexed under a different collection first. Scope with `db._in_collection()`.
- **Whisper hallucinates over music rather than returning nothing.** Filter
  with `transcribe.is_meaningful` before recording a transcript as `ok`, and
  keep non-`ok` text out of the FTS index.
- **Never leave a failed transcript without a row.** `pending_transcripts`
  queues any downloaded video lacking one, so a reel that can never be
  transcribed (no audio, no speech) would otherwise be re-attempted on every
  run forever. Record the outcome with a `status`; only `error` is retried,
  and only under `--retry-failed`.
- **Chrome allows one process per profile.** Browser commands take an advisory
  `flock` on the profile dir and fail fast with instructions. Non-browser
  commands take no lock — WAL mode makes concurrent reads safe.
- Schema changes need a migration in `db._migrate`: `CREATE TABLE IF NOT
  EXISTS` silently leaves an existing table alone, and people have live
  archives.
- Tests: `python3 test_ig_saved.py` (46, offline) and
  `python3 test_browser_e2e.py` (21, needs Playwright). Whisper's model is
  stubbed in tests — the first real `transcribe` downloads one.

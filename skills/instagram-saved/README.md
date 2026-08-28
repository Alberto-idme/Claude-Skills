# instagram-saved

Archive, transcribe and search your own Instagram saved posts.

Instagram gives you no way to search what you saved. This builds a local SQLite
index of every saved post — caption, author, media files, and Whisper
transcripts of reels — so you can actually find the ramen place you bookmarked
eight months ago.

```
$ ig-saved search "tonkotsu"

@kyoto_eats [japan]  https://www.instagram.com/p/CqxU1FzL0Dg/
  transcript: …the best [tonkotsu] ramen in Fukuoka, hands down…
```

## Why it works the way it does

There is no API for this. The Instagram Graph API, the API with Instagram Login,
and the (now sunset) Basic Display API all cover only accounts you own or
manage. Saved posts have never been exposed by any Meta API, so "connect your
Instagram account" in the OAuth sense is not available.

What *is* available splits cleanly in two:

- **Stage 1 — the index.** Your saved list is private to you. Only your session,
  or a file Meta generated from it, can enumerate it.
- **Stage 2 — the content.** The posts behind those permalinks are public. Any
  process can fetch them, including one that never touches your account.

Both stages have two implementations here, and you pick per run. That is
deliberate: it lets you start on the zero-risk path and move to the
always-current one without rewriting anything.

## Install

```bash
cd scripts
./setup.sh
```

That creates a virtualenv, installs the dependencies, downloads Chromium, and
runs the environment check. Re-running it is safe. Pass `--no-whisper` to skip
the transcription dependency, which is the largest download and is only needed
for reels.

Then, in each new shell:

```bash
cd scripts && source .venv/bin/activate
alias ig-saved='python -m ig_saved.cli'
```

Python 3.10+ is required. Everything except the browser source and transcription
runs on the standard library.

### If something is wrong

```bash
ig-saved doctor
```

Checks Python, Playwright, the browser binary, whether you have a stored
session, the Whisper backend, the Apify token and the database — and prints the
exact command to fix whatever is missing:

```
  [ok] python         3.11.15
  [ok] playwright     installed
  [XX] browser        none found
  [--] session        not signed in yet
  [ok] transcription  faster-whisper (model: small)

To fix:
    playwright install chromium
```

`[ok]` is fine, `[--]` is optional-and-absent, `[XX]` blocks you.

Already have Chrome and would rather not download another browser:

```bash
export IG_SAVED_CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
```

Data lives in `~/.ig-saved` (override with `--home` or `$IG_SAVED_HOME`):

```
~/.ig-saved/
  saved.db          SQLite: posts, media, transcripts, FTS index
  media/<code>/     downloaded images and videos
  chrome-profile/   the persistent browser profile holding your session
```

## First run

```bash
ig-saved doctor                        # confirm the environment is ready
ig-saved login                         # a window opens; sign in by hand, once
ig-saved collections                   # your collections and their ids
```

Start small to confirm the endpoints behave on your account before a full run:

```bash
ig-saved index --source browser --max-pages 1
ig-saved stats
```

If that shows posts, do the whole thing:

```bash
ig-saved sync --source browser
ig-saved search 'ramen'
```

## Stage 1 — building the index

### Option A: Meta's export (zero account risk)

Settings → Accounts Center → Your information and permissions → Download your
information. Choose **JSON**, include saved posts, and wait for the email.

```bash
ig-saved index --source export --path ~/Downloads/instagram-export.zip
```

Reads the `.zip` directly — no unzipping — or a folder, or a single `.json`.
Both `saved_posts.json` and `saved_collections.json` are picked up, and a post
that appears in both gets its author from one and its collection from the other.

You get permalinks, author handles, saved-at timestamps and collection names.
Captions and media are **not** in the export for other people's posts, so
Stage 2 is required afterwards.

Caveat worth knowing before you plan around it: confirm your export actually
contains a saved-posts file. Meta splits large exports across several archives
and reshapes the layout periodically. If nothing is found, the error tells you
what was checked and points you at the browser source.

### Option B: your own browser session (always current)

```bash
ig-saved login          # opens a window; sign in by hand, once
ig-saved collections    # lists your collections and their ids
```

Then index everything, one collection, or everything *with* collection labels:

```bash
ig-saved index --source browser                    # all saved posts, unlabelled
ig-saved index --source browser --all-collections  # all posts + their collections
ig-saved index --source browser \
    --collection https://www.instagram.com/tolis/saved/japan/18075071974439078/
```

`--all-collections` exists because neither feed alone is complete: the saved
feed has every post but no collection names, while per-collection feeds have
names but omit anything uncollected. It walks both and lets the upsert merge
them, so every post ends up complete *and* labelled. It costs roughly double
the requests — budget about a minute per 150 posts.

`--collection` accepts the full saved-collection URL or the bare numeric id.
Saved collections are private to their owner, so a URL under `/tolis/saved/…`
only resolves while signed in as `tolis`.

Posts come back fully hydrated from this source, so you can usually skip
Stage 2 entirely.

**How it works.** A persistent Chrome profile holds the session, and requests
are issued from *inside* the page via `fetch`, so cookies, CSRF token and
headers attach on their own. You log in by hand, so 2FA and checkpoints work and
no password touches this code. It calls the JSON endpoints the web app itself
uses rather than scraping the grid — the saved grid is virtualised, and DOM
scraping silently drops posts as nodes are recycled.

This uses undocumented endpoints and is against Instagram's Terms of Use. See
[Account safety](#account-safety).

## Stage 2 — hydrating the content

Only needed when Stage 1 came from the export.

### Via Apify (keeps traffic off your account)

```bash
export APIFY_TOKEN=apify_api_...
ig-saved hydrate --via apify --dry-run    # inspect the payload, spend nothing
ig-saved hydrate --via apify
```

Defaults to `patient_discovery/instagram-posts`, a cookieless actor at roughly
$2.50/1,000 results. Being cookieless is exactly why it cannot do Stage 1 — and
exactly why it is safe for Stage 2: your session is never shared.

Actor input schemas differ by publisher. If an actor rejects the payload the
error says so; fix it with `--apify-url-field` (`startUrls` and `directUrls` are
the common ones) or point at a different actor with `--apify-actor`.

Avoid any actor that asks for your `sessionid`. A cloud service holding a live
Instagram session is a bad trade.

### Via your own session

```bash
ig-saved hydrate --via browser
```

No third party and no cost, but the requests are yours. It is also the only
route that still sees posts whose authors have since gone private. Shortcodes
decode to media ids locally, so this costs one request per post and no lookups.

## Media and transcripts

```bash
ig-saved media                       # download images and videos
ig-saved transcribe                  # Whisper over saved reels
ig-saved transcribe --limit 200      # a chunk at a time
ig-saved transcribe --whisper-model medium
```

Downloads are parallel, atomic and idempotent — rerun freely.

Transcription prefers `faster-whisper`, which decodes audio through bundled
PyAV and therefore needs **no system ffmpeg**. `openai-whisper` works too but
requires ffmpeg on PATH.

Whisper does not return nothing on a music-only reel — it hallucinates a stock
phrase ("Thank you.", "ご視聴ありがとうございました", subtitle-credit boilerplate).
Left alone, every silent reel becomes a search hit for "thank you", so
transcripts below `--min-chars` (default 12), matching a known hallucination, or
consisting of one repeated phrase are recorded as `no_speech` instead of `ok`.
The text is kept on the row for inspection; it just never reaches the index.

To re-apply that filter to transcripts written earlier — no model, instant:

```bash
ig-saved transcribe --reclassify
```

Not every reel yields text, and the difference matters:

| Outcome | Meaning | Retried? |
|---------|---------|----------|
| `ok` | speech transcribed | no |
| `no_speech` | music-only or silent | no — it will never change |
| `no_audio` | the video has no audio track | no — same |
| `error` | something genuinely went wrong | with `--retry-failed` |
| *(skipped)* | the file is missing from disk | yes, stays queued |

Each outcome is recorded, so an untranscribable reel drops out of the queue
instead of costing model time on every future run. `ig-saved stats` reports
`untranscribable` separately from `transcripts`.

> **CDN URLs expire within hours.** If `media` reports expired URLs, refresh
> them rather than retrying: `ig-saved hydrate --only-expired`.

## Validating on one collection

Before committing to a full archive, run one collection end to end. Every stage
takes `--collection`, so the numbers stay clean even when the database already
holds other posts:

```bash
COLL='https://www.instagram.com/<you>/saved/japan/18075071974439078/'

ig-saved index --source browser --collection "$COLL"
ig-saved media      --collection japan
ig-saved transcribe --collection japan
ig-saved stats      --collection japan
ig-saved search 'ramen' --collection japan
```

`--collection` accepts the URL, the numeric id, or the bare name — indexing
stamps posts with the URL's slug, and the later stages resolve back to it.

A post can sit in several collections at once, and each is recorded: scoped
counts overlap on purpose, so `japan` + `sf` can exceed the archive total while
the unscoped `posts` count stays a true union.

`stats` reads top to bottom as the funnel. A stage well below the one above it
is where the problem is:

```
collection 'japan'

           posts: 2
        hydrated: 2  (100%)     ← below 100% means hydration is failing
     media files: 2
      downloaded: 2  (100%)     ← below 100% usually means expired CDN URLs
          videos: 1
     transcribed: 0  (0%)       ← 0% with videos > 0 means Whisper isn't running
```

What each shortfall means:

| Symptom | Cause |
|---|---|
| `hydrated` < `posts` | posts indexed from an export, never hydrated |
| `downloaded` < `media files` | CDN URLs expired — `hydrate --only-expired` |
| `transcribed` + `no speech/audio` < `videos` | transcription hasn't finished |
| `transcribed` 0%, no `no speech/audio` | no Whisper backend — run `doctor` |

## Large archives

Transcription is orders of magnitude slower than everything else, so past a few
hundred posts stop running it inside `sync`:

```bash
ig-saved sync --source browser --all-collections --skip-transcribe
ig-saved transcribe --limit 200      # then chunk this, or leave it overnight
```

Rough shape, from a real archive: **1 post ≈ 3 media files ≈ 2 videos**. So a
1,500-post account is around 4,500 files and 3,000 reels — call it 10 GB on
disk and, at 15–30s per reel on CPU, 12–24 hours of transcription against
minutes for everything else.

Order matters. Index and download first, in one go: CDN URLs expire within
hours, so anything still queued behind a long transcription run will go stale.
`sync` already sequences it that way; `--skip-transcribe` keeps it that way.

Two things run safely while a long job is going:

```bash
ig-saved search '...'    # WAL mode allows concurrent readers
ig-saved stats
```

Browser commands do not. Chrome permits one process per profile, so `login`,
`collections` and `index/hydrate --source browser` take an advisory lock and a
second one exits immediately saying so.

## Searching

```bash
ig-saved search "tonkotsu"
ig-saved search "kyoto AND ramen"
ig-saved search "ramen NOT instant"
```

SQLite FTS5 over captions, authors **and** transcripts, so a reel that never
mentions ramen in its caption still turns up if someone says it out loud.

```bash
ig-saved stats
ig-saved dump --out saved.jsonl
```

## Everything at once

```bash
ig-saved sync --source browser
ig-saved sync --source export --path export.zip --via apify
```

Runs index → hydrate → media → transcribe, skipping hydration when the source
already provides it. Every stage is resumable; interrupting is always safe.

## Account safety

The browser paths use undocumented endpoints and are against Instagram's Terms
of Use. This exists to archive your own saved posts. It is not built for bulk
collection and should not be pointed at anything else. Scraped content stays
other people's — fine to archive and search privately, not to republish.

- Default pacing is 1.5–4s between requests, jittered; `--slow` doubles it.
- Run it from your own machine. A real browser profile on a residential IP is
  the entire point.
- On HTTP 429 the tool stops rather than retrying. Wait hours. Pushing through
  a rate limit is how accounts get checkpointed.
- The browser hydrator also aborts if more than half of its early requests fail,
  which usually means a stale or limited session rather than deleted posts.

## Tests

```bash
cd scripts
python3 test_ig_saved.py       # 40 unit tests; no network, no session
python3 test_browser_e2e.py    # 20 e2e checks against a mock Instagram
```

`test_ig_saved.py` covers URL parsing, shortcode↔id decoding, export-format
drift, both normalisers, the merge semantics that stop hydration from blanking
indexed fields, transcription plumbing, FTS behaviour and CLI wiring.

`test_browser_e2e.py` stands up a local server speaking the same JSON shapes as
Instagram's private endpoints and drives the real `BrowserSession` against it —
in-page fetch, cookie detection, pagination cursors, carousel flattening,
collection feeds, shortcode hydration, media download and idempotency. It needs
Playwright and a browser, and skips itself if either is missing.

The one thing neither suite exercises is Whisper's actual model: transcription
is tested with a stubbed backend, so the DB and FTS paths are covered but the
first real `ig-saved transcribe` will download a model (~500 MB for `small`).

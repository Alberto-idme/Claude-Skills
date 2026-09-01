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

`[ok]` is fine, `[--]` is optional-and-absent, `[XX]` blocks you. When
something is only `[--]`, the summary names the stages that cannot run rather
than claiming all-clear — an earlier version printed "Everything needed is
present" with a missing OCR engine listed directly above it.

Credentials for `describe`/`extract` are checked across the whole chain the SDK
uses, not just `ANTHROPIC_API_KEY`: an `ant auth login` profile counts, because
a zero-arg client resolves it on its own.

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

## The four tracks

A saved post carries more than its caption, and the useful part is often not
the spoken part. Each track is extracted separately and indexed together:

| Track | Command | Where it comes from |
|---|---|---|
| Caption | (indexing) | the post itself |
| Voice | `transcribe` | Whisper over the audio |
| On-screen text | `ocr` | text burned into frames — usually where the name is |
| Video | `describe` | Claude vision over sampled keyframes |

```bash
ig-saved ocr --collection japan            # on-screen text
ig-saved describe --collection japan       # what the footage shows
ig-saved transcript <shortcode>            # all four, rendered together
ig-saved transcript --collection japan --out japan.txt
```

`transcript` is the readable combined view:

```
@kyoto_eats  [japan]
https://www.instagram.com/p/CqxU.../

── Caption ──
best tonkotsu in Shibuya

── Voice ── (ja)
このお店は深夜まで開いています

── On-screen text ──
  [0:01]  ICHIRAN SHIBUYA
  [0:04]  OPEN UNTIL MIDNIGHT

── Video ──
A narrow counter with individual wooden booths and a ticket machine by the door.
```

**On-screen text is the highest-value track for recommendation reels** — the
place name is on a title card far more often than it is spoken. It is also the
only signal for reels that come back `no_speech`, which are typically
music-over-captions.

Frame sampling skips static frames, so a caption held for five seconds costs
one OCR call rather than five. Reads are then deduped three ways: exact
repeats, partial reveals ("Tokyo Ram" → "Tokyo Ramen"), and engine jitter
(ICHIRAN / ICHlRAN / 1CHIRAN), which substring matching alone cannot collapse —
one real reel produced 266 lines from 178 frames before that was added. To
re-clean rows written earlier, without re-running OCR:

```bash
ig-saved ocr --reclean
``` The threshold is deliberately low: measured on a
clip whose caption changes completely, the frame-difference score moves only
2.9–4.1 while genuinely static frames score 0.000–0.001.

`describe` and `extract` call the Claude API and cost money. Both take
`--dry-run` to price a run first and `--batch` for half price asynchronously.
Roughly $0.02 per video at 4 keyframes, so ~$50 for 3,000 reels, or ~$25
batched.

## Making it actionable

Extraction distils all four tracks into the fields you triage on — what it is,
where, what you would do with it, and whether the sources said enough to trust:

```bash
ig-saved extract --collection japan --dry-run   # price it
ig-saved extract --collection japan --batch     # half price
ig-saved report  --collection japan
```

`report` writes three files into `<home>/report/`:

- **`report.html`** — the one to actually work from. Self-contained, opens from
  disk, sorts and filters (below), and has a toggle for the entries worth
  another pass. Thumbnails come from the media you already downloaded, and every
  entry carries an explicit `↗ open reel on Instagram · <shortcode>` link back
  to the source. Reels point at `/reel/` so they open in the player rather than
  the grid.
- **`report.csv`** — for spreadsheet triage and your own tooling.
- **`report.md`** — grouped tables for pasting into a doc.

Categories are `restaurant`, `cafe`, `bar`, `hotel`, `sight`, `shop`,
`activity`, `recipe`, `tip`, `guide`, `product`, `other`; actions are `visit`,
`book_ahead`, `order`, `cook`, `buy`, `read_more`, `none`.

### Sorting

The default is grouped by category, which is the shape you triage in. The sort
dropdown also offers, when the data supports it:

| Order | Key |
|---|---|
| Recently saved / Saved earliest | position in the collection's feed |
| Newest post / Oldest post | the post's own publication date |

Those are genuinely different questions. A guide published in 2019 that you
saved last week is the *newest save* and one of the *oldest posts*.

Instagram's private API returns no saved-at timestamp, so save order is
recorded as **position in the collection feed**, which the API returns
most-recently-saved first. That means it only exists for collections indexed
through the browser source, and only after an `index` walk — an archive built
before this existed has to be re-walked once (it costs nothing but the
pagination) before "Recently saved" is offered. Publication date needs no
re-walk. Sorting by date drops the category headings, since they only mean
something while the cards under them are still grouped; entries with no date
sort to the bottom either way rather than pretending to be the oldest thing in
the collection.

### Filtering

Text, category, action, **city**, **neighbourhood**, collection, and a
`fixable`-only toggle.

Locations arrive free-text and are split on the comma: `Shibuya, Tokyo` gives
the neighbourhood `Shibuya` and the city `Tokyo`. A bare `Tokyo` has a city and
no neighbourhood — treating the only component as an area would fill the
dropdown with entries that mean nothing. Choosing a city narrows the
neighbourhood list to that city's, and a neighbourhood left over from another
city clears itself, so the two filters can't be combined into something that
matches nothing.

**Filter by city, not by collection.** A saved collection is a folder, not a
promise about geography — a real `japan` collection turned out to hold a place
in Ojai, California and one in Seoul. Extraction is faithful to the post, so
the outliers are real; grouping by the trailing part of each location puts
anything out-of-place one dropdown away.

Flagged entries carry a `review_reason` saying what was missing, and a
`review_kind` saying whether another pass could ever recover it:

| `review_kind` | Meaning |
|---|---|
| `fixable` | the detail is there but came through garbled — a denser OCR read may recover it |
| `source_limit` | the post never carried it: deliberately unnamed, a bare list, audio that is only music |

That distinction matters because the flag count is a poor progress metric. On a
real run, halving the OCR interval resolved names on 6 of 14 flagged entries —
浅草店 became 浅草一丁 — while the count stayed at 14, because the rest were floors
rather than failures. The report's toggle isolates `fixable` only, so you chase
what can move.

Re-running is cheap by default: extraction hashes the evidence it sent and
skips posts whose input has not changed, because re-billing the model to
reproduce an answer already on disk is pure waste.

```bash
ig-saved ocr     --collection japan --only-flagged --interval 0.5
ig-saved extract --collection japan --only-flagged   # only what OCR improved
ig-saved extract --collection japan --only-flagged --force   # ignore the hash
```

Extraction uses structured outputs, so the shape is guaranteed and the report
never parses prose. The prompt forbids inventing a name, price or opening time
— an unsupported field comes back empty and the entry is flagged
`needs_review` rather than filled with a guess.

## Addresses and websites

Extraction gives each post one entry with one title. That is the wrong grain for
a post that names eight restaurants — which is exactly why those came back
flagged `source_limit` with "one line each, no addresses". Two stages fix it:

```bash
ig-saved places --collection japan --dry-run   # price it
ig-saved places --collection japan             # one row per named place
ig-saved enrich --collection japan --dry-run   # searches are billed per use
ig-saved enrich --collection japan             # address + website for each
ig-saved report --collection japan
```

`places` re-reads the evidence already on disk and lists every place, business,
venue or attraction the post names — one row each, no web access. `enrich`
takes those names to the web via Claude's server-side search tool and fills in
address, website, phone and a Google Maps link.

They are separate because they have different failure modes and different
bills. A lookup that fails should never cost you the extracted name, and only
`enrich` is charged per search.

### Cost

| Stage | Rate | Japan (78 posts, ~117 places) |
|---|---|---|
| `places` | tokens only | ~$1.10 |
| `enrich` | **$10 per 1,000 searches** + tokens | ~$3.50-$5.90 |

`max_uses` caps each lookup at 3 searches. Both stages have `--dry-run`, and
both are incremental: a place already looked up is never searched again.

### Every address carries a checkable citation

The rule that extraction must never invent a name, price or address gets teeth
here, because a fabricated street address is both very plausible and very
expensive to act on.

The model reports the URL of the page it read the address off. That URL is then
checked **in code** against the URLs web search actually returned in that same
response — exact match, or the same host. A citation matching neither was
invented, and the row is stored with `verified = 0` and called out in the
report:

> ⚠ citation not verified — check the source before relying on this

Every place row also carries a `source` link, so an address is one click from
the page it came from. Maps URLs are built locally from the documented format
rather than asked for, since a recalled Maps link is exactly the kind of thing
that comes back plausible and wrong.

A place the search genuinely could not find keeps its row with the reason
("no such bar in the results") rather than disappearing — the difference
between "named somewhere I could not pin down" and "named nowhere" is worth
keeping. Those are not re-searched on later runs; `--retry-failed` reopens only
the ones that errored.

`report` writes a fourth file, **`places.csv`** — one row per place, which is
the grain you actually plan a trip in. `report.csv` stays one row per post;
flattening the two together would lose whichever grain you needed.

## Searching

```bash
ig-saved search "tonkotsu"
ig-saved search "kyoto AND ramen"
ig-saved search "ramen NOT instant"
```

SQLite FTS5 over captions, authors, transcripts, on-screen text **and** video
descriptions — a reel that never mentions ramen in its caption still turns up
if someone says it out loud, writes it on a title card, or the footage shows it.

The index uses the **trigram** tokenizer, not `unicode61`. Japanese and Korean
have no word spaces, so `unicode61` indexes a whole caption as a single token —
searching ラーメン inside 東京ラーメン二郎 returned nothing at all. Trigram matches
substrings, which also recovers the spaces OCR loses on compressed video
("ICHIRANSHIBUYA"). Queries under 3 characters fall back to a `LIKE` scan, so
東京 still works.

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

Note where that stops: **at transcribe**. It downloads and transcribes, but it
does not read on-screen text, distil entries, or rebuild the report, so new
posts land in the archive without reaching the report. Add `--full` to carry
them the whole way:

```bash
ig-saved sync --source browser --collection "$JAPAN" --full
```

`--full` runs the whole chain — OCR, extraction, the places pass, the address
lookup, then the report last so it carries what the run just found. It leaves
out `--describe`, the priciest stage; add it explicitly if you want it.

### Just the new posts

`--full` runs every stage over everything still pending in the collection,
which on the first full run means the whole backlog. To carry only this run's
arrivals through the entire chain and leave the backlog where it is:

```bash
ig-saved sync --source browser --collection "$JAPAN" --full --only-new
```

`index` is what discovers the new posts, so the scope is set once it has run
and every stage after it sees only those. On a collection of 78 already-indexed
posts with 2 new saves, that is 2 posts through media, transcription, OCR,
extraction, places and the lookup — instead of 156 backlogged places going to
the web.

An empty scope means *no* posts, not all of them: a run that finds nothing new
does nothing, rather than quietly starting a full backlog pass.

`--full` does spend: extraction is billed in tokens and enrichment is billed
per web search. Two rails keep that bounded:

- `--max-searches N` hard-stops enrichment once it has spent N searches.
  Rows past the cap stay pending, so the next run resumes exactly there.
  Enrichment works most-recently-saved first, so a cap buys the newest saves
  rather than the oldest backlog — a cap on a plain row order would spend the
  whole budget before reaching anything you saved this week.
- `--redo` does **not** reach enrichment. It means "extract these again", and
  it is shared by every stage in the chain — letting a free redo cascade into
  re-searching every place already found is the kind of thing you notice on
  the bill. `--re-enrich` is the explicit way to ask for that.

## Picking up new saves

Adding posts to a collection and re-running needs no special mode. Every stage
queries for its own unfinished work, so re-running only touches what is new:

```bash
ig-saved sync --source browser --collection "$JAPAN" --full
```

`index` reports which posts it had not seen before, by shortcode:

```
Indexed 78 posts: 2 new, 76 already known.
New this run: DNEW111aaa, DNEW222bbb
```

and the run closes by confirming they arrived:

```
2 new post(s) this run; 2 now in the report.
  All new posts made it through.
```

`extract` costs money, so it is guarded twice over: it only queries posts with
no entry, and it stores a hash of each post's evidence, so even a `--redo` pass
skips anything whose inputs are unchanged.

### When something is missing from the report

The report is a join against `entries`, so a post that never got one is absent
with nothing raised — the counts are simply lower. `stats` makes that visible:

```console
$ ig-saved stats --collection japan
           posts: 78
      downloaded: 76  (97%)
       in report: 76  (97%)

2 post(s) not in the report:
  DNEW111aaa     @tokyofood           media not downloaded — run `media`
  DNEW222bbb     @kyoto_eats          media not downloaded — run `media`
```

`posts` above `in report` is the whole failure mode. Each stuck post names the
stage to run next rather than just reporting that it is missing.

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
./check.sh            # everything
./check.sh --quick    # offline unit tests only, a few seconds
```

```
test_ig_saved.py         offline unit tests                    135/135 passed
test_browser_e2e.py      browser against mock Instagram        21/21 passed
test_report_ui.py        report controls in a real browser     18/18 passed
test_ocr_e2e.py          OCR and vision on real video          28/28 passed
test_pipeline_smoke.py   whole chain, mock in -> report out    ok

All suites passed.
```

`test_ig_saved.py` covers URL parsing, shortcode↔id decoding, export-format
drift, both normalisers, the merge semantics that stop hydration from blanking
indexed fields, transcription plumbing, FTS behaviour and CLI wiring.

`test_browser_e2e.py` stands up a local server speaking the same JSON shapes as
Instagram's private endpoints and drives the real `BrowserSession` against it —
in-page fetch, cookie detection, pagination cursors, carousel flattening,
collection feeds, shortcode hydration, media download and idempotency. It needs
Playwright and a browser, and skips itself if either is missing.

`test_report_ui.py` loads the generated `report.html` in Chromium and works the
controls, asserting on computed style rather than markup. A filter that sets
`hidden` on a card is not enough on its own: `.card{display:grid}` is an author
rule and beats the user agent's `[hidden]{display:none}`, so filtered-out cards
stayed on screen while the tally counted them as gone. Only a real browser
catches that.

The one thing neither suite exercises is Whisper's actual model: transcription
is tested with a stubbed backend, so the DB and FTS paths are covered but the
first real `ig-saved transcribe` will download a model (~500 MB for `small`).

# /btw — Autonomous Run

I'll be away for ~60 minutes (unless I specify otherwise in the handoff). I want to come back to **completed, verified, committed work** — not promises, not stubs, not "I was about to..." Bar is best-in-class.

---

## Operating Mode: 5000% Autonomous

Assume my answer to every reversible, non-destructive prompt is:

- **Yes** / **Yes, allow** / **Proceed** / **Pass** / **Commit** / **Push** *(working branches only)*
- **Accept all** / **Go with the recommendation** / **Move forward**

**Default: act, don't ask.** If you're ~70%+ confident, execute. If <70%, pick the path that's easiest to reverse and execute anyway. I'd rather review a draft than answer a question.

The only reasons to wait on me are listed under **Hard Stops**. Everything else: decide, do, document.

---

## Step 1 — Plan (≤ 3 min)

Create `AUTONOMOUS-RUN-<tag>.md` in the project root. Pick `<tag>` from the work stream (e.g. `auth`, `layout`, `payments-v2`) so parallel sessions don't collide.

Include:
- **Goal** — 1 sentence describing what success looks like at the end of the run
- **Top 3–5 deliverables** in priority order, each with:
  - Rough time estimate
  - Definition of done (the exact command/check that proves it's complete)
- **Backup queue** — 2–3 high-leverage items to pull from if primary work finishes early or blocks
- **Working branch** — create/checkout `auto/<tag>-<YYYYMMDD-HHMM>` so commits are isolated

Also append every meaningful change to `CHANGELOG-AUTO.md` as you go, one bullet per commit.

Then start executing immediately. Do not wait for confirmation.

---

## Step 2 — Triage Every Decision

**Default: derive the answer and proceed.** If the codebase, recent commits, docs, conventions, comments, types, tests, or sensible defaults can answer it — they do. Pick the choice most consistent with the existing code.

### Hard Stops (the ONLY reasons to wait on me)

1. **Auth into a third-party UI** that requires my browser session or 2FA on my device
2. **Strategic / brand / product decisions** ("should we offer X?", "rename the product?")
3. **Destructive or irreversible prod ops** — drop tables, force-push to `main`, delete prod data, send broadcast emails, charge cards, public release
4. **Anything that physically requires me at the keyboard** (hardware, device-bound 2FA)

Anything else: **decide and execute.** Examples that are NOT hard stops:
- "Hook vs util?" → pick one, note rationale in the commit
- "Which library?" → use what's in `package.json`; if nothing fits, pick the most-starred maintained option
- "Naming?" → match the codebase's existing convention
- "Should I refactor X to make this clean?" → if it's in scope and reversible, yes

Park real hard stops in a **NEEDS YOU** section of the run log with: the specific question, what you tried first, and your recommendation. Then move on.

---

## Step 3 — Verification Loop (the 100%-confidence piece)

After every meaningful change, before declaring it done:

1. **Typecheck** the affected scope. Zero new errors.
2. **Lint** the affected scope. Zero new warnings (fix, or document why in the commit).
3. **Run tests** touching the changed code. All green. No skips, no `.only`, no `xit`.
4. **Run the feature end-to-end** if it's user-facing. "The test passed" ≠ "the thing works."
5. **Read your own diff** before committing. Hunt for: stray TODO/FIXME, `console.log`, commented-out code, scope creep, files you didn't mean to touch.
6. **Commit** with a clear message: `<area>: <what changed and why>`. Small, atomic commits.

**Definition of done:** typecheck clean ∧ lint clean ∧ tests pass ∧ manually verified ∧ committed. If any one is false, it is not done — say so explicitly in the log.

If verification fails: fix it. If it fails **3 times with genuinely different approaches** and you're still stuck, park the task in NEEDS YOU with everything you tried, and move to the next deliverable. Do not commit broken state. Do not mock what should be real. Do not write tautological tests.

---

## Step 4 — Never Idle

If primary work blocks, immediately pull from the backup queue or pick the highest-leverage item from this list for **this** project (don't generically run all of them):

- **Security review** of recent changes — auth, input validation, secrets, dependency CVEs
- **Bug bash** — actively try to break the most recently shipped features; file or fix what you find
- **Accessibility audit** — WCAG 2.2 AA: contrast, keyboard nav, focus order, ARIA, screen-reader paths
- **Performance audit** — bundle size, render perf, Lighthouse, network waterfall, N+1 queries
- **Test coverage analysis** — find gaps in critical paths and write the tests
- **Dead code / duplication sweep** — delete what's unused, dedupe what's copy-pasted
- **Type tightening** — eliminate `any`, narrow unions, add missing return types
- **Highest-ROI refactor** — pick one, do it fully, ship it tested
- **Competitive analysis** — how do 2–3 best-in-class peers solve this same problem? What's worth borrowing?
- **Alternatives doc** — for the next big decision, write up 2–3 approaches with tradeoffs + recommendation

**Stuck protocol:** if you've made no real progress in 10 minutes on a single item, switch to a different deliverable. Don't burn the hour spinning.

---

## Parallelism

If tasks are genuinely independent, spawn sub-agents (Task tool) to work in parallel. Don't serialize what could be parallel. Reconverge before committing so the history stays coherent.

---

## Hard Constraints

- **Working branch**: push freely. **`main`/`master`/release branches**: never push without explicit authorization in the handoff — park in NEEDS YOU instead.
- **No deploys, prod migrations, or destructive DB ops** without explicit authorization in the handoff.
- **No fake progress.** No mocked tests masquerading as real ones, no `expect(true).toBe(true)`, no skipped verifications, no "implemented" with stubbed bodies, no silenced errors.
- **Match the codebase's conventions** — read `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, recent PRs, top-level config. Mirror the style. Don't introduce a new pattern unless the task asks for one.
- **Commit small and often.** Each commit = one coherent change. I want to read the history.
- **If you find uncommitted changes you didn't make** — stop, note it in the log, check whether another agent is in this repo. Don't clobber.
- **Don't gold-plate.** Solve the task; don't redesign the architecture unless the task *is* to redesign the architecture.
- **Stay in scope.** If you spot a 10× improvement outside scope, note it in *New value added* — don't pull it into this run.
- **No secrets in commits, logs, or files.** Ever.

---

## Anti-Patterns (do not do these)

- Asking me a question you could have answered from the code
- Stopping at the first error instead of trying 2–3 alternative approaches
- Declaring "done" without running the verification loop
- Leaving the codebase broken to hand off "almost finished" work
- Generating a wall of analysis instead of shipping the actual fix
- Inventing requirements that weren't in the handoff
- Spending >10 minutes thinking without making concrete progress — switch tasks

---

## When the Hour Is Up (or work runs out)

Finalize `AUTONOMOUS-RUN-<tag>.md` with:

- **✅ Done** — each item, with file paths, commit SHAs, and the verification result (`tests: 47 pass`, `lighthouse: 92 → 97`, `bundle: 412kb → 388kb`)
- **🚧 In progress** — what's partial, exactly where it stopped, exact next step to resume
- **❓ Needs you** — each parked item with the specific question, the options, and your recommendation
- **💎 New value added** — audits, analyses, ideas; link to any docs you wrote
- **⚠️ Surprises / open issues** — bugs found, tech debt surfaced, anything I should know
- **📊 Run summary** — N commits, M files changed, +X/−Y lines, coverage delta, branch name

Then stop and wait at the prompt. Don't start new work after the timer runs out.

---

**Start now. Write the plan to the run log, then execute. I'm trusting you to ship.**

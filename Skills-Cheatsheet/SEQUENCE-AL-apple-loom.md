# Sequence AL — Apple Loom (Component Extraction → Reusable Kits)

> Companion to `SKILLS-CHEATSHEET.md §27 Workflow Sequences`. Takes the normalized inventory from AJ and the accepted hypotheses from AK and **weaves** the codebase into a set of reusable kits: a look-and-feel kit, a business-logic kernel, an API-client pack, an asset bundle, and a schema pack. Each kit ships as its own Swift Package that any new Apple project can `swift package add` in one command.

## Prerequisite

- `.apple-dissect/<run-id>/component-candidates.md` exists (AJ Step 4 / `/apple-dissect --components`).
- `hypothesis-tree.json` from AK ideally exists (Loom uses AK's accepted hypotheses to know which assumptions to *preserve* during extraction).

## When To Use

- "I want this app's look and feel for a new project, without all the business logic."
- "Pull the API client out so we can reuse it in the watchOS companion."
- "Extract the analytics / logging / feature-flag plumbing — it's the only good thing in this codebase."
- "I have ten iOS apps, all written by different teams. Extract the *common kernel* across them."

## The Five Standard Kits

| Kit | Contents | New-project use |
|-----|----------|-----------------|
| **`<App>UIKit`** | SwiftUI / UIKit views, ViewModifiers, Color / Font tokens, Asset catalog subset, Lottie / Rive packs, custom controls | Drop into any new app to inherit the brand and interaction patterns |
| **`<App>Core`** | Business-logic kernel: domain models, value types, state machines, validators, formatters, pure-function utilities | The *purpose-shaped* logic of the app, decoupled from UI and network |
| **`<App>APIClient`** | URLSession + Combine/AsyncSequence networking, decoders, request builders, auth flow, retry/backoff, error model | Hit the same backend(s) from another product or a server-side Swift tool |
| **`<App>Assets`** | Asset catalog (.xcassets), localized .strings tables, app-icon variants, fonts, theme JSON | Theme another app with the same identity |
| **`<App>Schema`** | CoreData / SwiftData / Realm / GRDB schema, migrations, fixtures, codegen seeds | Share a persistence layer between an app and its server-side companion |

## Chain

```text
# Step 0 — brainstorm scope (the only non-deterministic gate).
/superpowers:brainstorming                    → "Which of the five standard kits are realistic, and which need to be split or merged?"
                                                Produces extraction-targets.md.

# Step 1 — plan each extraction.
# Loom dispatches one /superpowers:write-plan per kit (parallel).
/superpowers:dispatching-parallel-agents      → fan out one planner per accepted kit
  ├── /superpowers:write-plan <App>UIKit      → PLAN.md (carve list, public-surface rules, dependency cuts, test plan)
  ├── /superpowers:write-plan <App>Core
  ├── /superpowers:write-plan <App>APIClient
  ├── /superpowers:write-plan <App>Assets
  └── /superpowers:write-plan <App>Schema

# Step 2 — harden every plan.
/autoplan                                     → CEO + Design + Eng + DX reviews in one shot for every PLAN.md
/plan-eng-review                              → architecture lock-in per plan (parallel)
/plan-design-review                           → only for <App>UIKit and <App>Assets

# Step 3 — execute extractions. Each kit on its own git worktree.
/superpowers:using-git-worktrees              → per-kit worktree under ../<App>-loom/<kit-name>/
/gsd:new-workspace (per worktree)             → register each worktree as a GSD workspace
/gsd:plan-phase 1                             → first phase per kit: "Move files + minimal compile"
/gsd:execute-phase 1                          → atomic-commit execution
/superpowers:subagent-driven-development      → parallel sub-tasks inside each phase
/superpowers:test-driven-development          → test-first for every Public symbol moved

# Step 4 — protocolize project-specific dependencies.
# Each kit must compile with ZERO references to other kits' concrete types.
# Loom emits a "ProtocolSeam.swift" per kit listing every internal-type swap.
For each PLAN.md `Replace project-specific types with protocols:` block:
    /code-review (high effort)               → confirm the swap is mechanical, not semantic
    /simplify                                → apply the swap automatically where safe
    /verify                                  → smoke compile the kit in isolation

# Step 5 — public-surface audit.
/superpowers:requesting-code-review           → cross-team review focused on `public` symbols
/code-review --comment                        → inline review of API surface
/superpowers:writing-skills                   → if the kit deserves its own skill (e.g. a wrapper for the API client)

# Step 6 — generate the consumer examples.
For each kit:
    /web-artifacts-builder OR /playground     → demo HTML/Playground showcasing the kit
    /example-skills:* (closest match)         → use as authoring template for example code
    /design-consultation                      → only for <App>UIKit: produce DESIGN.md describing the kit's design system

# Step 7 — ship the kits as SPM packages on the workspace branch.
/gsd:ship                                     → per-kit PR with CHANGELOG + VERSION bump
/superpowers:finishing-a-development-branch   → land each kit's branch cleanly
/document-release                             → root-level docs: "Five kits extracted from <App>"

# Step 8 — capture lessons and update the OS.
/idme-base:adr-writer                         → ADR per kit: "Why we drew the boundary here"
/learn                                        → Apple-specific extraction wins/losses
/retro                                        → end-of-extraction retrospective
/os-integrate                                 → if any new patterns deserve to become a skill, wire them in
```

## Definition of Done

- Each accepted kit ships as a standalone Swift Package with a top-level `Package.swift`.
- Each kit's tests are green on `swift test` (or `xcodebuild test` for kits that require Xcode-only frameworks like Metal or RealityKit).
- Each kit compiles with **zero** references to its sibling kits' concrete types (protocol seams only).
- Each kit has a `README.md` whose first 200 chars accurately describe its purpose.
- A new throwaway Xcode project can `swift package add` each kit and run a `Hello, <App>` example in < 5 minutes.
- ADRs explaining the extraction boundary are written and committed.

## Loops, MCPs, and Agents Used

| Layer | Component | Why |
|-------|-----------|-----|
| Loop | `/gsd:execute-phase` (per kit) | atomic-commit phased execution |
| Loop | `/superpowers:subagent-driven-development` | parallel sub-task execution inside a kit |
| Loop | `/autoresearch:fix` (gated to "errors in extracted kit only") | iterate to green in isolation |
| MCP | `mcp__claude_ai_Sourcegraph__*` (if available) | cross-repo usage search to validate kit's public surface is real |
| MCP | `mcp__plugin_idme-base_chromadb__chroma_*` | store kit specs for later reuse in other extraction runs |
| MCP | `figma` (`get_design_context`) | for `<App>UIKit` — pull the canonical design-system file if it exists |
| Agent | `idme-base:react-architect-planner` (analogue for SwiftUI architecture) | view-layer extraction plan |
| Agent | `idme-base:java-architect-planner` (analogue for Swift backend kernel) | non-UI kernel extraction plan |
| Agent | `idme-base:code-review-expert` | post-extraction quality review |
| Agent | `plan-auditor` | sanity-checks every PLAN.md before execution |
| Agent | `superpowers:dispatching-parallel-agents` | per-kit parallelism |
| Agent | `idme-base:adr-writer` | boundary-decision ADRs |
| CLI | `swift package init`, `swift package generate-xcodeproj` (deprecated but still works), `swift test` | SPM scaffolding + isolation testing |
| CLI | `xcodebuild test` | for kits that depend on Xcode-only frameworks (RealityKit, Metal compute, WidgetKit) |

## Anti-Patterns (do not do these)

- Do **not** extract a kit that fails the AJ component-candidates *generality* score < 4/10 (you'll regret it).
- Do **not** keep concrete cross-kit references "temporarily". Either protocolize on extraction or do not extract.
- Do **not** publish a kit without a working consumer example (the `Hello, <App>` test from DoD).
- Do **not** copy the entire app's `Info.plist` into a kit. Kits get a minimal `Info.plist` with only what they need.
- Do **not** include analytics calls in a kit unless the kit *is* the analytics kit. Wrap them behind a protocol the consumer provides.

## See Also

- **Sequence AJ — Apple Ingest & Map** — required upstream.
- **Sequence AK — Apple Inquisitor** — strongly recommended upstream; AK's hypothesis tree tells AL which assumptions are load-bearing.
- §6 IDME Base — `react-architect-planner`, `java-architect-planner`, `code-review-expert`.
- §14 Superpowers — `using-git-worktrees`, `dispatching-parallel-agents`, `subagent-driven-development`.
- §V New Skill / MCP Authoring Pipeline — if a kit deserves to become its own skill, follow Sequence V from here.

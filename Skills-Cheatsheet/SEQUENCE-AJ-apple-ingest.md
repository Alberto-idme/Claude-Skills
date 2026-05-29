# Sequence AJ — Apple Ingest & Map

> Companion to `SKILLS-CHEATSHEET.md §27 Workflow Sequences`. Operationalizes Steps 1 + 2 of the `apple-dissect` skill into a full chain that takes any iOS / macOS / visionOS / tvOS / watchOS build artifact and produces a complete four-layer memory snapshot (file → planning doc → vector → graph) plus a runnable component-extraction backlog.

## When To Use

- New employer hands you a 50,000-line Swift codebase on day one.
- A vendor delivers a `.ipa` and a 6-page PDF and nothing else.
- An acquired team's iOS app is now in your org and nobody on the receiving team has read it.
- You inherited an Xcode project where the last commit message is "fix" from 2021.
- You want to ingest a competitor's public TestFlight build for inspiration.

## Pre-flight

| Check | Command | Required |
|-------|---------|----------|
| Xcode CLI tools | `xcode-select -p` | Yes |
| `swift-lsp` plugin | `claude plugin list | grep swift-lsp` | Recommended |
| `tuist` | `tuist version` | Optional (improves dep graph for Tuist projects) |
| `xcparse` | `xcparse version` | Optional (improves `.xcresult` extraction) |
| Disk space | `df -h .` | ≥ 5× artifact size |

## Chain

```text
# Step 0 — anchor the work in GSD so commits, plans, and tests land where the rest of the OS expects them.
/gsd:new-workspace                            → register the inbound build dir as a GSD workspace
/gsd:new-project "Ingest <App>"               → seed PROJECT.md and ROADMAP.md for the dissection cycle
/gsd:settings                                 → enable plan-auditor, code-review-expert, deep-analyst

# Step 1 — dissect.
/apple-dissect <artifact-path>                → normalize .ipa/.app/.xcarchive/.xcodeproj into .apple-dissect/<run-id>/
                                                emits manifest.json, source-map.json, dep-graph.json, asset-map.json,
                                                symbol-map.json, signing-report.md (skill: §17 Apple Platform)

# Step 2 — map at the codebase level using existing scaffolding.
/gsd:map-codebase                             → parallel-agent codebase map (STACK.md, ARCH.md, CONCERNS.md,
                                                QUALITY.md) over the normalized source tree
/idme-base:codebase-deep-analyzer             → architecture patterns, dependencies, technical debt sweep

# Step 3 — compound the knowledge into four memory layers.
/init                                         → emit CLAUDE.md scaffold pointing every future session at the .apple-dissect run
/claude-mem:learn-codebase                    → push module-level summaries into persistent vector memory
/graphify <artifact-root>                     → build a knowledge graph from source + symbol map + dep graph
/sync-gbrain                                  → register the surface for gbrain semantic search

# Step 4 — narrative + ADR seed.
/idme-base:writer                             → RDR: "What is <App>?" (consumes manifest + behavior-summary)
/idme-base:adr-writer                         → ADR-0001 baseline: "Codebase as inherited on YYYY-MM-DD"
/idme-base:codebase-deep-analyzer             → re-run with FORMAT=narrative for a human-readable tour
/learn                                        → record any surprises the heuristics caught (e.g. "this project still uses NIBs")

# Step 5 — seed the autonomous loops.
/autoresearch:plan                            → goal: "Achieve full understanding of <App>" with metric = "100% of public symbols
                                                covered by a docstring or generated summary"
/autoresearch                                 → iterate against the metric (calls back into /apple-dissect --inquire as needed)

# Step 6 — checkpoint.
/context-save                                 → persist the loaded mental model
/gsd:pause-work                               → close the GSD session cleanly with a resumable handoff
```

## Definition of Done

- `.apple-dissect/<run-id>/manifest.json` exists and validates against the documented schema.
- `STACK.md`, `ARCH.md`, `CONCERNS.md`, `QUALITY.md` from `/gsd:map-codebase` are all present.
- A new graphify graph exists at `<artifact-root>/graphify-out/`.
- `claude-mem:mem-search "<app-name> architecture"` returns ≥ 3 results.
- `ADR-0001-baseline.md` is committed on the workspace branch.
- The autonomous loop's first three iterations have produced ≥ 1 commit each.

## Loops, MCPs, and Agents Used

| Layer | Component | Why |
|-------|-----------|-----|
| Loop | `/autoresearch` | drives coverage of the symbol map toward 100% |
| Loop | `/gsd:map-codebase` (parallel agents) | concurrent extraction of stack / arch / concerns / quality |
| MCP | `claude-mem` knowledge agent (vector memory) | makes the inventory queryable across sessions |
| MCP | `mcp__plugin_idme-base_chromadb__chroma_*` | optional: keep a project-specific Chroma collection of summaries |
| MCP | `figma` (`get_design_context`) | only if the team provides a Figma URL — pulls source-of-truth UI |
| Agent | `gsd-codebase-mapper` × 4 (tech / arch / quality / concerns) | spawned by `/gsd:map-codebase` |
| Agent | `idme-base:codebase-deep-analyzer` | architecture + tech debt deep dive |
| Agent | `idme-base:adr-researcher` | gathers evidence for the baseline ADR |
| CLI | `xcrun`, `plutil`, `codesign`, `otool`, `nm`, `security` | invariant tooling for artifact extraction |
| CLI | `tuist graph --format json` | dependency graph for Tuist projects |
| CLI | `xcparse` | screenshot + log extraction from `.xcresult` |
| CLI | `swift package describe --type json` | SwiftPM target graph |

## See Also

- **Sequence AK — Apple Inquisitor** — once the inventory is built, AK does maximally inquisitive `/investigate` against it.
- **Sequence AL — Apple Loom** — given the inventory plus AK's hypotheses, AL extracts reusable kits.
- §17 Apple Platform — `apple-dissect`, `liquid-glass`.
- §28 LSP Plugins — `swift-lsp` materially improves the symbol map.

# Sequence AK — Apple Inquisitor (max-depth `/investigate`)

> Companion to `SKILLS-CHEATSHEET.md §27 Workflow Sequences`. Pushes `/investigate` into a **recursive, multi-agent, hypothesis-driven loop** specifically tuned for iOS / macOS code. Where AJ is "what is this", AK is "*why* is it like this, *how* does it behave under stress, *where* are the bugs hiding, *what* breaks if I change X".

## Prerequisite

Sequence AJ has already produced `.apple-dissect/<run-id>/` for the target. Without that, AK runs `apple-dissect --ingest --map` itself but loses the four-layer-memory benefits.

## When To Use

- The dissected app does something unexpected and you need to know *exactly* why.
- You suspect there's a class of bugs (race conditions, retain cycles, layout misalignment) and want to find every instance.
- You're about to refactor a load-bearing module and need to know every call site, every side effect, every concurrency assumption.
- You want a maximally adversarial review *before* touching production code.
- Pre-acquisition technical due diligence.

## Inquisitor Mode — What Makes It Different From Plain `/investigate`

Plain `/investigate` is the 4-phase root-cause skill (investigate → analyze → hypothesize → implement) — one question, one answer, one fix. Inquisitor mode is *N* questions, *N²* hypotheses, no fix permitted until every hypothesis has been refuted or confirmed by independent evidence.

| Dimension | Plain `/investigate` | AK Inquisitor mode |
|-----------|---------------------|--------------------|
| Hypotheses per loop | 1 | 5–10 |
| Loops | 1 | 5 (or until coverage ≥ 95%) |
| Agents | 0 | 3 in parallel per loop (deep-analyst, react/java-debugger analogue, security) |
| Sources | Code | Code + symbol map + dep graph + crash logs + reviews + AppStore release notes |
| Output | Fix | Evidence-backed dossier with `accepted` / `refuted` / `inconclusive` for each hypothesis |
| Exit criterion | Bug fixed | Coverage metric met **or** `/autoresearch` stops yielding new hypotheses |

## Chain

```text
# Step 0 — environment.
/guard                                        → lock edits during forensic phase (Apple builds can be load-bearing)
/freeze                                       → mark target dir read-only-by-policy until inquiry done
/gsd:resume-work                              → load the AJ run's workspace if it was paused

# Step 1 — pre-stage with the artifact dissection if missing.
[ -d .apple-dissect ] || /apple-dissect <artifact-path>
                                              → guarantees the JSON inventory exists

# Step 2 — open the inquiry.
/investigate                                  → start the 4-phase inquiry against the inventory; in Inquisitor mode
                                                we DO NOT terminate after one fix; we run /investigate inside a loop.
/superpowers:systematic-debugging             → enforce scientific method (one hypothesis → one experiment → one
                                                result)
/gsd:debug "<top-level question>"             → persistent debug session that survives context resets

# Step 3 — the recursive expansion. This is the heart of AK.
# Implemented as an /autoresearch goal: maximize coverage of the hypothesis tree.
/autoresearch:plan                            → goal: "Refute or confirm every plausible hypothesis about <App> behavior"
                                                metric: count of hypotheses moved from `pending` to {`accepted`,`refuted`}
                                                direction: monotonically increasing
                                                verify: each transition needs a code citation or executable test
/autoresearch:debug                           → autonomous bug-hunting loop. Discovers + classifies bugs *while* the
                                                hypothesis tree expands (concurrent with /autoresearch above)

# Step 4 — parallel deep-dives.
# Spawned simultaneously to triangulate from different angles.
Agent: idme-base:deep-analyst         → "what does this module assume about thread safety?"
Agent: idme-base:java-debugger        → (analogue mode) "what would break this code on iOS 26?"
Agent: idme-base:adr-researcher       → "what historical decisions does this code embed?"
Agent: superpowers:dispatching-parallel-agents
                                              → fans the above out, joins results into hypothesis-tree.json

# Step 5 — security-flavored inquiry.
/cso                                          → CSO daily/comprehensive audit
/autoresearch:security                        → STRIDE + OWASP-MASVS for the binary; iOS-specific checks:
                                                ATS exceptions, keychain misuse, App Group leaks, URL scheme hijacks,
                                                missing pinning, debuggable production builds

# Step 6 — quality-flavored inquiry.
/code-review (high effort) over the source roots → bug-flavored review of every src dir
/simplify (dry-run)                                → propose reuse / dedup wins without applying them yet
/superpowers:finding-duplicate-functions           → quantify dedup opportunities

# Step 7 — convergence.
/gsd:verify-work                              → close the loop with a UAT-style walkthrough of each accepted hypothesis
/gsd:audit-uat                                → ensure the UAT itself is rigorous, not handwavy
/idme-base:adr-writer                         → ADR per architectural surprise the inquiry uncovered

# Step 8 — synthesis + restart criterion.
/idme-base:writer                             → final dossier RDR: questions, hypotheses, evidence, recommendations
/document-release                             → if the inquiry produced fixes, update docs
/retro                                        → engineering retrospective (was the inquiry calibrated correctly?)
/learn                                        → record any Apple-specific gotchas surfaced (KVO + Swift, ARC + closures, etc.)
/unfreeze                                     → release the read-only policy
```

## Definition of Done

- `hypothesis-tree.json` exists with every node labeled `accepted` / `refuted` / `inconclusive`.
- ≥ 95% of nodes have an attached code citation **or** an executable repro test.
- `/autoresearch:debug` has classified every flagged bug into one of: critical / major / minor / wontfix.
- `/cso` and `/autoresearch:security` reports are committed.
- A final RDR is written to the workspace and indexed in `claude-mem`.
- The autonomous loops report `goal_met: true` or `progress_stalled: true` (any stall is logged with reason).

## Loops, MCPs, and Agents Used

| Layer | Component | Why |
|-------|-----------|-----|
| Loop | `/investigate` inside `/autoresearch` | recursive root-cause expansion |
| Loop | `/autoresearch:debug` | concurrent bug-hunting that doesn't block the hypothesis loop |
| Loop | `/gsd:debug` | persistent state across context resets |
| MCP | `mcp__plugin_idme-base_sequential-thinking__sequentialthinking` | explicit hypothesis-tree reasoning |
| MCP | `mcp__plugin_claude-mem_mcp-search__smart_search` | "have we seen this hypothesis class before?" |
| MCP | `mcp__plugin_idme-base_chromadb__chroma_query_documents` | corpus lookup across prior dissections |
| Agent | `idme-base:deep-analyst` | thread-safety + state-machine analysis |
| Agent | `superpowers:systematic-debugging` | scientific-method discipline |
| Agent | `superpowers:dispatching-parallel-agents` | parallel hypothesis fan-out |
| Agent | `idme-base:react-debugger` (analogue for SwiftUI state churn) | view-model lifecycle analysis |
| Agent | `idme-base:adr-researcher` | embedded historical decisions |
| CLI | `lldb`, `xcrun symbolicate`, `atos` | crash log triage (read-only — no live debugging from this chain) |
| CLI | `swiftlint` | rule-based suspicion seeding |

## Anti-Patterns (do not do these)

- Do **not** fix bugs during AK. AK *finds*; AL or a follow-up Sequence D / K / F *fixes*. Mixing modes contaminates the evidence.
- Do **not** stop at the first accepted hypothesis. The whole point is *N*² coverage.
- Do **not** let `/investigate` exit Phase 4 (Implement) — block it at Phase 3 in this chain.
- Do **not** run `/autoresearch:fix` from this chain. Fixes belong in AL or a downstream cycle.
- Do **not** trust a single agent's verdict on a hypothesis. Convergence requires ≥ 2 independent agents (or 1 agent + 1 executable test).

## See Also

- **Sequence AJ — Apple Ingest & Map** — required upstream input.
- **Sequence AL — Apple Loom** — required downstream consumer of accepted hypotheses.
- §3 Autoresearch — the loop primitive AK depends on.
- §12 / §14 / §15 Superpowers — systematic-debugging + parallel agents.
- §16 Godmode — `fault-diagnosis`, `comprehension-check` (drop-in patterns for AK loops).

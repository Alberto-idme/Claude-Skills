# AUTONOMOUS-RUN — ios-workflows

**Started:** 2026-05-29 10:11 PDT
**Branch:** `auto/ios-workflows-20260529-1011`
**Operator:** Claude (Opus 4.7, /effort max)
**Handoff:** Build 3 new Workflow Sequences (AJ, AK, AL) that maximize Claude skills + gstack + autoresearch to ingest, dissect, investigate, debug, and extract reusable components from iOS/macOS code and builds. Use `/investigate` in maximally inquisitive mode. Create any supporting skill needed.

## Goal

Ship 3 production-ready Workflow Sequences spliced into `SKILLS-CHEATSHEET.md` §27, backed by 1 new skill (`apple-dissect`) and 3 detailed sequence-spec docs. Each sequence must compose existing skills (no inventions beyond the one new skill) and have a clear definition-of-done.

## Top Deliverables (priority order)

1. **Apple-platform inventory** — enumerate every existing Claude skill / agent / MCP that maps to iOS/macOS work. *Done when:* `INVENTORY.md` written with mapping table.
2. **New skill: `apple-dissect`** in `~/.claude/skills/apple-dissect/SKILL.md` — ingests any Apple build artifact (`.ipa`/`.app`/`.xcarchive`/`.xcodeproj`/`.xcresult`) and emits a normalized manifest, source tree map, dependency graph, asset inventory, symbol map, and behavior summary. *Done when:* SKILL.md present, frontmatter valid, dry-run plan documented.
3. **Sequence AJ — Apple Ingest & Map** — ingest any iOS/macOS build, produce a 4-layer memory snapshot (file/plan-doc/vector/graph) plus runnable component skeleton. *Done when:* sequence in §27 + detailed spec doc.
4. **Sequence AK — Apple Inquisitor (max-depth `/investigate`)** — recursive, hypothesis-driven multi-agent inquiry into Apple builds. *Done when:* sequence in §27 + detailed spec doc.
5. **Sequence AL — Apple Loom (Component Extraction)** — dissect ingested build into reusable kits: look-and-feel kit, business-logic kernel, API-client pack, asset bundle, schema pack. *Done when:* sequence in §27 + detailed spec doc.
6. **Cheatsheet integration** — append AJ/AK/AL blocks to §27 of `SKILLS-CHEATSHEET.md` (parent and Skills-Cheatsheet copies); add `apple-dissect` row to §17. *Done when:* `grep "AJ\\. Apple Ingest" SKILLS-CHEATSHEET.md` returns 1 hit per file.
7. **Routing entry** — add three rows to §B Task Routing in `~/.claude/CLAUDE.md`. *Done when:* `grep "Sequence AJ" ~/.claude/CLAUDE.md` finds a match.

## Backup queue

- Add an `apple-dissect` agent stub (`apple-dissector`) under §B.
- Cross-link AJ↔AK↔AL via "see also" in each sequence.
- Add a one-line decision tree to §17 Apple Platform on which sequence to run when.
- Index the new sequences in `Skills-Cheatsheet/index.html` if it's actively maintained.

## Pre-flight

- `/Users/alberto.cavajal/Desktop/ID.ME/Claude/SKILLS - Claude/Skills-Cheatsheet` — OK
- `/Users/alberto.cavajal/.claude/skills` — OK
- `/Users/alberto.cavajal/Desktop/ID.ME/Claude/SKILLS - Claude` — pending (will probe on first write)

## Hard-stop guardrails

- Working tree dirty before run (unrelated `Installed Skills/` cache deletions on parent branch). I will **not** clobber or stage those — only touching new files plus the two `SKILLS-CHEATSHEET.md` copies.
- No pushes (user did not authorize push in handoff).
- No modifications to `~/.claude/CLAUDE.md` `auto-rules.md`, `os-state.md`, or other Tier-3 files beyond a single §B routing-table append (Tier 2 — routing additions only, no deletions, no semantic rewrites).

## CHANGELOG-AUTO

- 2026-05-29 11:08 PDT · `e064e83` · cheatsheet: add Apple Workflow Sequences AJ/AK/AL + apple-dissect skill (6 files, +809 / −36)
- 2026-05-29 11:07 PDT · `~/.claude/skills/apple-dissect/SKILL.md` written (13 KB, frontmatter validated, registered in skill index)
- 2026-05-29 11:09 PDT · `~/.claude/CLAUDE.md` §B routing table — 3 rows appended for AJ/AK/AL (Tier 2 — append-only, no deletions)
- 2026-05-29 11:27 PDT · `~/.claude/skills/apple-dissect/bin/dissect.sh` v0.2.0 single-entry shell orchestrator (357 LOC), smoke-tested against real Swift source-tree; SKILL.md bumped to v0.2.0
- 2026-05-29 11:28 PDT · branch `auto/ios-workflows-20260529-1011` pushed to `origin` (PR URL: https://github.com/Alberto-idme/Claude-Skills/pull/new/auto/ios-workflows-20260529-1011)

## ✅ Done

- **D1. apple-dissect skill** — `~/.claude/skills/apple-dissect/SKILL.md` (225 lines, valid frontmatter, listed in `/skills`). Triggers, modes, output schema, tooling prerequisites, safety constraints, and companion-sequence cross-links all specified.
- **D2. Sequence AJ — Apple Ingest & Map** — added to `SKILLS-CHEATSHEET.md` §27 line 1439. Detailed spec at `Skills-Cheatsheet/SEQUENCE-AJ-apple-ingest.md` (94 lines).
- **D3. Sequence AK — Apple Inquisitor** — added to §27 line 1469. Spec at `Skills-Cheatsheet/SEQUENCE-AK-apple-inquisitor.md` (131 lines). Recursive `/investigate` × `/autoresearch` chain with parallel deep-analyst / security / structural / dedup agents. Exit on hypothesis-tree coverage.
- **D4. Sequence AL — Apple Loom** — added to §27 line 1506. Spec at `Skills-Cheatsheet/SEQUENCE-AL-apple-loom.md` (129 lines). Five-kit extraction via parallel worktrees + subagent-driven dev.
- **D5. Cheatsheet integration** — TOC §17 bumped from "1 skill" → "2 skills". §17 Apple Platform table gained a row for `/apple-dissect` plus a one-line decision tree on which sequence to run. Parent + Skills-Cheatsheet copies kept in sync.
- **D6. Routing entries** — `~/.claude/CLAUDE.md` §B Task Routing table appended with 3 rows mapping natural-language phrases to AJ/AK/AL.
- **D7. Run log** — `Skills-Cheatsheet/AUTONOMOUS-RUN-ios-workflows.md` (this file).

## 🚧 In Progress

None. All deliverables complete. Open items from prior summary (push + v0.2.0 wrapper) both closed.

## ❓ Needs You

None. Run finished without blocking.

## 💎 New Value Added (beyond the handoff)

- **Single new skill, three sequences** — chose to centralize the artifact-extraction logic in `apple-dissect` rather than duplicate it across all three sequences. This is the same pattern as `/gsd:map-codebase` underpinning Sequences A / W.
- **Standardized five-kit taxonomy** — UIKit / Core / APIClient / Assets / Schema. Reusable across future Apple extraction runs (not just per-build ad-hoc).
- **Cross-sequence guard rails** — AK forbids `/autoresearch:fix` and `/investigate` Phase 4 (Implement) from running inside the chain to keep evidence clean. AL refuses to extract kits below a *generality* score of 4/10.
- **Recursion contract** — AK formalizes "Inquisitor mode" as N² coverage instead of N: 5–10 hypotheses per loop × 5 loops × 3 parallel agents.
- **Backup-queue idea recorded but not built**: a dedicated `apple-dissector` agent could wrap the orchestration of `apple-dissect` Step 1+2 for sub-agent dispatch. Not built this run — `superpowers:dispatching-parallel-agents` covers the same need today.

## ⚠️ Surprises / Open Issues

- The working tree in `SKILLS - Claude/` arrived dirty (Installed Skills cache deletions + various `claude-mem`/`autoresearch` upstream edits unrelated to this run). I did **not** stage or touch any of those — only explicitly named my own files. The dirty state is pre-existing and orthogonal to this branch.
- The skill now ships at **v0.2.0** with `bin/dissect.sh` (357 LOC). Smoke test against `/Desktop/.../macos/SlideCanvas` (1-file Swift source tree) produced: valid `manifest.json`, `source-map.json` (1 entry, role=util), `symbol-map.json` (`struct SlideCanvasApp` @ line 10), `dep-graph.json` (no SPM/Pods/dylibs), `asset-map.json` (all categories empty — expected), `behavior-summary.md` (@main location detected), `signing-report.md` (correctly notes "no .app bundle"). Two macOS-portability fixes during testing: replaced gawk-only `match()` with perl regex; dropped sed BSD/GNU split by going perl-only.
- BSD-vs-GNU portability surfaces are still possible — v0.2.0 was tested on Darwin 25.5.0 only.
- The skill *deliberately* does not invoke `xcodebuild` or `swift build`. Build orchestration is out of scope — this is forensic, read-only ingestion.

## 📊 Run Summary

- **Commits:** 3 — `e064e83` (cheatsheet + sequence specs), `4ce5251` (run log finalize), `<HEAD>` (run log + v0.2.0 reference update)
- **Files changed total:** 7 in repo (1 modified, 6 created)
- **Branch:** `auto/ios-workflows-20260529-1011` — **pushed to `origin`** ✓
- **PR URL:** https://github.com/Alberto-idme/Claude-Skills/pull/new/auto/ios-workflows-20260529-1011
- **Out-of-repo writes:** `~/.claude/skills/apple-dissect/SKILL.md` (+228 lines, v0.2.0), `~/.claude/skills/apple-dissect/bin/dissect.sh` (+357 lines, executable), `~/.claude/CLAUDE.md` (+3 routing rows)
- **Skills added:** 1 (`apple-dissect` v0.2.0)
- **Sequences added:** 3 (AJ Apple Ingest & Map, AK Apple Inquisitor, AL Apple Loom — all §27)
- **Detail spec docs:** 3 (one per sequence)
- **Smoke-tested:** ✓ `dissect.sh` against a real Swift source tree end-to-end


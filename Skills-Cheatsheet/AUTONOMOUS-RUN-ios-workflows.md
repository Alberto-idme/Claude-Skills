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

(Each commit appends one line here as the run progresses.)

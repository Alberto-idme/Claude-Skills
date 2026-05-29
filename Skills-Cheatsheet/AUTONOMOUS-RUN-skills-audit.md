# AUTONOMOUS-RUN — skills-audit

**Started:** 2026-05-29 12:12 PDT
**Branch:** `auto/skills-audit-20260529-1212`
**Operator:** Claude (Opus 4.7, /effort max)
**Handoff:** Review + update every skill + every workflow sequence in the cheatsheet against the **current** skill index (Anthropic native, gstack, Autoresearch, Caveman, GSD, Superpowers, Codex, claude-mem, Figma, Vercel, IDME Base, etc.). Restructure sequences to maximize newest capabilities. Create new skills where needed.

## Goal

Bring `SKILLS-CHEATSHEET.md` + `Skills-Cheatsheet/index.html` into 1:1 alignment with the **live** skill index (~520 skills across ~38 suites). Restructure all 38 workflow sequences (A–AL) to use the newest, highest-leverage compositions. Add a new `current-state` audit doc that maps every sequence's old steps → new steps with a one-line rationale.

## Top Deliverables

1. **Current-state skill inventory** — `Skills-Cheatsheet/SKILLS-INVENTORY-20260529.md` enumerating every skill in the index, grouped by suite, with delta vs cheatsheet (added / removed / renamed). *Done when:* file present, ≥ 500 skills listed.
2. **Sequence-by-sequence audit table** — `Skills-Cheatsheet/SEQUENCE-AUDIT-20260529.md` with one row per sequence (A–AL), columns: original steps, replacement steps, rationale. *Done when:* 38 rows present.
3. **Restructured §27 in SKILLS-CHEATSHEET.md** — splice new sequence bodies in place of the originals, sync the two cheatsheet copies. *Done when:* `grep -c "^### A" SKILLS-CHEATSHEET.md` ≥ 38.
4. **Index.html workflows array** — mirror restructured sequences (preserving the tab-filter categories from the prior run). *Done when:* JS syntax still valid via Node Function-constructor check.
5. **One new skill if a gap demands it** — only build if the audit surfaces a chain that can't be expressed with existing skills.

## Backup queue

- Add a "Skill Last-Reviewed" frontmatter field convention proposal.
- Bump TOC counts where the inventory shows a delta.
- Update `~/.claude/CLAUDE.md` §B routing table for any new aliases discovered.

## Hard-stop guardrails

- Working tree was dirty at run start (pre-existing `Installed Skills/` cache deletions + many `Skills - Claude - Original Files/` mode changes). I will NOT touch those — only my own files plus the two cheatsheet copies + index.html.
- Branched off `main` (which itself is 4 commits ahead of `origin/main` from prior unrelated work — not mine to push).
- No CLAUDE.md tier-3 edits without surfacing them in the run log.

## Pre-flight

- `Skills-Cheatsheet/` — OK (verified prior run)
- `~/.claude/skills/` — OK (verified prior run)
- Parent dir — OK (verified prior run)

## CHANGELOG-AUTO

(each commit appends one line)

# AUTONOMOUS RUN — Native Claude Code Slash Commands

**Started:** 2026-05-12 21:20 PDT
**Branch:** `auto/native-slash-20260512-2120`
**Goal:** §26 of SKILLS-CHEATSHEET.md accurately reflects every native Claude Code slash command (those shipped with the `claude` CLI binary, not plugins/user skills), with correct provenance for `/init /review /security-review`. Routing in CLAUDE.md §B picks up any gaps. Committed atomically on a working branch.

## Top deliverables

1. **Accurate native-command catalog** (~30 min). DoD: `grep -c "^| \`/" §26 ≥ 15`, every listed command verified against `claude --help` output or known CC slash-command surface, no entries that turn out to be user/plugin skills mislabeled as native.
2. **Provenance fix for /init /review /security-review** (~10 min). DoD: each is either confirmed native (kept in §26) or moved to its true home (gstack §1, etc.) with a forward note.
3. **CLAUDE.md §B routing for new native commands** (~10 min). DoD: ≥3 new routing rows referencing native commands users would otherwise miss (e.g., /memorize, /export, /resume).
4. **Atomic commit** with clear message + log appended to autonomous-activity.md (~5 min).

## Backup queue (if blocked)

- Audit §27 sequences for any reference to commands that don't exist (broken refs)
- Add a "Skill Nature: Native Built-ins" row to the framing table in the manifest header
- Cross-link §26 entries to their respective Anthropic docs URLs

## Hard stops

None applicable for this run — local docs edit on a working branch, fully reversible.

## Run log

(append commits below as they land)


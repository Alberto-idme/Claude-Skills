# Skills + Workflow Sequence Audit — 2026-05-29

**Audit branch:** `auto/skills-audit-20260529-1212`
**Auditor:** Claude (Opus 4.7, /effort max)
**Source of truth:** live skill index dump from session start + filesystem walk of `~/.claude/plugins/cache/**/SKILL.md` and `~/.claude/skills/*`.

This document is split in three parts:

1. **Plugin version delta** — what's installed vs what the cheatsheet claims.
2. **Skills added since cheatsheet was last synced** — new skills/commands that should be reachable from the cheatsheet.
3. **Sequence audit table (A → AL)** — for every workflow sequence, the old vs new chain with a one-line rationale.

---

## 1. Plugin Version Delta

| Plugin | Cheatsheet says | Installed (verified) | Action |
|--------|-----------------|----------------------|--------|
| gstack | "Ship & QA Suite (46 skills)" | 46+ skills present | OK (count fluctuates as recipes are added) |
| GSD | 57 commands | 57+ commands present | OK |
| Autoresearch | 10 skills | v1.9.12, 10 skills | OK — bump suite version in footer |
| Figma | 2.1.30 + 10 skills | **2.1.30 AND 2.2.12 cached**; 2.2.12 drops `figma-implement-design`, adds `figma-use-slides` | **Update** — replace `figma-implement-design` in Sequences G + AE; mention 2.2.12 |
| graphify | 1 cmd | present | OK |
| IDME Base | 9 skills | 9 + 4 commands (`implement/init/status/validate`) | **Update** — list the 4 commands too |
| Beads | 1 skill + 26 subcommands | 26 + adds `daemons`, `prime`, `template` (29 total) | **Update** — bump to 29 |
| PRD Taskmaster | 1 skill | present | OK |
| UI/UX Pro Max | 7 skills | v2.5.0, present | OK |
| Browser Use | 4 skills | present | OK |
| Document & Office | 6 skills | present | OK |
| Creative & Design | 6 skills | present | OK |
| Developer Utilities | 9 skills | present | OK |
| Superpowers | 14 skills | v5.0.7, 14 skills | OK |
| Superpowers Lab | 4 skills | 5 skills (`windows-vm`, `slack-messaging`, `finding-duplicate-functions`, `mcp-cli`, `using-tmux-for-interactive-commands`) | **Update** — bump to 5 |
| Godmode | 37 skills | v1.0.0, 37 skills | OK |
| Apple Platform | 2 skills (this run) | 2 (`apple-dissect`, `liquid-glass`) | OK |
| Claude Code Configuration | 5 skills | 5 + several new natives (`/goal`, `/advisor`, `/batch`, `/security-review`, `/usage`, `/skills`, `/doctor`) | **Update** — bump to ~12 |
| Google Workspace Suite | 44 skills | 44 skills + cross-channel comms NOT covered (Discord, Telegram, iMessage available as separate Anthropic plugins) | **Update** — add note about §AO Cross-Channel |
| GWS Recipes | 35 | 35 | OK |
| GWS Personas | 10 | 10 | OK |
| Video & Motion | 2 | 2 | OK |
| Codex | 2 skills | v1.0.4: 3 skills (`codex-cli-runtime`, `codex-result-handling`, `gpt-5-4-prompting`) + 7 commands (`adversarial-review`, `cancel`, `rescue`, `result`, `review`, `setup`, `status`) | **Update** — bump skills 2→3, add commands |
| Context7 | 2 skills | v1.0.0, 2 | OK |
| claude-mem | 8 skills | v12.7.2, 8 skills | OK |
| Native Claude Code | ~77 commands | growing; add: `/goal`, `/advisor`, `/batch`, `/usage`, `/skills`, `/doctor`, `/security-review`, `/code-review`, `/simplify`, `/verify`, `/init`, `/run` | OK list growing; ensure all surfaced |
| Workflow Sequences | 38 (after AJ/AK/AL) | 38 — proposing 4 new this audit (AM/AN/AO/AP) | **Add** — see §3 below |
| LSP Plugins | 4 (swift/jdtls/typescript/ruby) | 11 installed (`swift`, `jdtls`, `typescript`, `ruby`, **`clangd`**, **`csharp`**, **`gopls`**, **`kotlin`**, **`lua`**, **`php`**, **`pyright`**) | **Update** — bump 4 → 11 |
| Ralph | section present | present + new `ralph-loop` Anthropic-marketplace plugin | OK |
| Caveman | 7 skills | present | OK |
| ML / LLM Training | 2 | 2 | OK |
| OS Management | 4 | 4 | OK |
| Plugin Authoring Toolkit | 16 | 16 documented + new Anthropic plugins: `agent-sdk-dev`, `claude-code-setup`, `claude-md-management`, `commit-commands`, `cwc-makers`, `feature-dev`, `hookify`, `mcp-server-dev`, `mcp-tunnels`, `pr-review-toolkit`, `plugin-dev` | **Update** — add 11-skill row block |
| M5Stack IoT | 2 | 2 | OK |
| Vercel | 26+ skills, 3 agents | v0.43.0 — adds `vercel-agent` and a benchmark suite (`benchmark-agents`, `benchmark-e2e`, `benchmark-sandbox`, `benchmark-testing`, `plugin-audit`, `release`, `vercel-plugin-eval`) | **Update** — note benchmark suite |

---

## 2. Skills Added Since Last Cheatsheet Sync — by category

### New Anthropic marketplace plugins (`~/.claude/plugins/marketplaces/claude-plugins-official/plugins/`)

| Plugin | Purpose |
|--------|---------|
| `agent-sdk-dev` | Build agents with the Claude Agent SDK |
| `claude-code-setup` | Bootstrap a Claude Code install from scratch |
| `claude-md-management` | Curate CLAUDE.md hierarchies (root, user, project) |
| `code-modernization` | Migrate code across major framework / language versions |
| `code-review` | (native command also exists) — diff review with severity tags |
| `code-simplifier` | Apply reuse / dedup wins discovered by code-review |
| `commit-commands` | Author and run commit-time slash commands |
| `cwc-makers` | "Claude Writes Code" makers — opinionated build commands |
| `example-plugin` | Reference plugin layout for authoring |
| `explanatory-output-style` | Force outputs to be more explanatory |
| `feature-dev` | Feature scaffolding skill (vs `/gsd:quick`) |
| `frontend-design` | (also in claude-api / document-skills) |
| `hookify` | Generate hook rule files for the harness |
| `learning-output-style` | Educational-style explanations |
| `math-olympiad` | Math problem solver skill |
| `mcp-server-dev` | Build MCP servers from scratch |
| `mcp-tunnels` | **NEW** — Tunnel local MCP servers to remote callers |
| `pr-review-toolkit` | **NEW** — Multi-agent PR review (separate from gstack `/review`) |
| `playground` | (already mentioned in §33) |
| `plugin-dev` | Plugin authoring tooling |
| `pyright-lsp` / `clangd-lsp` / `csharp-lsp` / `gopls-lsp` / `kotlin-lsp` / `lua-lsp` / `php-lsp` | New LSPs |
| `ralph-loop` | Anthropic's official packaging of the Ralph loop |

### New comms plugins (external_plugins)

| Plugin | Use |
|--------|-----|
| `discord` | Send / receive on Discord |
| `telegram` | Send / receive on Telegram |
| `imessage` | Send / receive on iMessage (macOS only) |

### New Codex commands (v1.0.4)

| Command | Use |
|---------|-----|
| `/codex:adversarial-review` | Red-team a diff with Codex |
| `/codex:cancel` | Cancel a running Codex task |
| `/codex:result` | Retrieve a long-running Codex task's result |
| `/codex:status` | Status of running Codex tasks |

### New Beads commands

| Command | Use |
|---------|-----|
| `/beads:daemons` | Manage multi-daemon setups |
| `/beads:prime` | Prime the cache with a fresh dump |
| `/beads:template` | Issue templates |

### New native commands worth adding

| Command | Purpose |
|---------|---------|
| `/goal` | Set goal + iterate (rough native /autoresearch) |
| `/advisor` | Consult a stronger model on a hard step |
| `/batch` | Fanout across worktrees / parallel PRs |
| `/skills` | List installed skills |
| `/doctor` | Diagnose Claude Code install |
| `/usage` / `/cost` / `/stats` | Session cost / token usage |
| `/code-review` (native) | Diff review with severity (separate from gstack `/review`) |
| `/simplify` | Apply `/code-review --fix` to working tree |
| `/security-review` | Dedicated security review |
| `/verify` | Run the app and observe a change |
| `/run` | Launch the project's app |

---

## 3. Sequence Audit — Old vs New (A → AL)

> Format per row: **OLD CHAIN** → **NEW CHAIN** — *rationale*.

### A. New Project (Full Ceremony)
- **OLD:** `/office-hours` → `/gsd:new-project` → `/gsd:settings` → `/gsd:map-codebase` → discuss/plan/execute/verify/add-tests → `/gsd:audit-milestone` → `/gsd:complete-milestone` → `/document-release` → `/retro`
- **NEW:** add `/superpowers:brainstorming` between office-hours and new-project; add `/claude-md-management` after `/gsd:settings` to seed CLAUDE.md; add `/code-review` per phase; add `/security-review` before audit-milestone.
- **Why:** the new `claude-md-management` skill makes CLAUDE.md hierarchy curation a first-class step. `/security-review` is now a dedicated native that should always precede milestone close.

### B. Quick Feature
- **OLD:** `/gsd:quick` → `/review` → `/ship`
- **NEW:** `/gsd:quick` → `/code-review` (native, fast) → `/simplify` (if findings) → `/review` (gstack pre-landing) → `/ship`
- **Why:** native `/code-review` is faster than gstack `/review` and pairs with `/simplify` for one-shot cleanups.

### C. Trivial Fix
- **OLD:** `/gsd:fast` → `/ship`
- **NEW:** `/gsd:fast` → `/code-review` (low effort) → `/ship`
- **Why:** even trivial fixes benefit from a 10-second `/code-review` pass.

### D. Bug Investigation
- **OLD:** `/investigate` (gstack) OR `/gsd:debug` OR `/autoresearch:debug`
- **NEW:** `/investigate` → `/superpowers:systematic-debugging` → (`/gsd:debug` for persistence | `/autoresearch:debug` for full sweep) → `/code-review --fix` (the regression site) → `/verify`
- **Why:** ends with `/verify` so the fix is actually exercised, not just compiled. `/code-review --fix` catches sibling regressions.

### E. Design-First Frontend
- **OLD:** `/design-consultation` → `/gsd:ui-phase` → `/gsd:plan-phase` → `/gsd:execute-phase` → `/gsd:ui-review` → `/design-review` → `/qa`
- **NEW:** `/design-consultation` → `/gsd:ui-phase` → `/frontend-design` → `/gsd:plan-phase` → `/gsd:execute-phase` → `/ui-ux-pro-max` → `/gsd:ui-review` → `/design-review` → `/qa` → `/verify`
- **Why:** `/frontend-design` (Anthropic) and `/ui-ux-pro-max` (community) bracket execution to align with framework conventions and polish to pro-grade.

### F. Full Ship Pipeline
- **OLD:** `/review` → `/ship` → `/land-and-deploy` → `/canary` → `/document-release`
- **NEW:** `/code-review` (native) → `/security-review` → `/review` → `/ship` → `/land-and-deploy` → `/canary` → `/document-release`
- **Why:** `/security-review` before shipping is the new norm; native `/code-review` runs first for fast feedback.

### G. Figma ↔ Code
- **OLD:** `/figma:figma-implement-design` → build → `/figma:figma-generate-design` → `/figma:figma-code-connect`
- **NEW:** `/figma:figma-use` (always first, MANDATORY) → `/figma:figma-generate-design` (from spec) **OR** read existing file via `/figma:get_design_context` → build → `/figma:figma-code-connect` → `/figma:figma-use-slides` (if presenting the design)
- **Why:** v2.2.12 drops `figma-implement-design`; the official flow is `figma-use` for writes + design generation skills for views. `figma-use-slides` adds Slides round-trip.

### H. Session Management
- **OLD:** `/gsd:resume-work` → `/gsd:next` → `/gsd:progress` → `/gsd:pause-work` → `/gsd:session-report` → `/retro`
- **NEW:** `/gsd:resume-work` → `/usage` (sanity check token budget) → `/gsd:next` → `/gsd:progress` → `/gsd:pause-work` → `/gsd:session-report` → `/claude-mem:timeline-report` → `/retro`
- **Why:** `/usage` lets you abort early if you're about to blow context. `/claude-mem:timeline-report` makes the session permanently queryable.

### I. Security Audit
- **OLD:** `/cso` → `/autoresearch:security` → `/careful` → `/guard`
- **NEW:** `/guard` → `/careful` → `/cso` → `/security-review` (native) → `/autoresearch:security` → `/codex:adversarial-review`
- **Why:** lock the env (`/guard` + `/careful`) FIRST. Native `/security-review` complements `/cso`. Add `/codex:adversarial-review` for cross-AI red-team.

### J. Documentation Writing
- **OLD:** `/idme-base:writer` → `/idme-base:design-document-writer` → `/idme-base:adr-writer` → `/idme-base:arb-writer` → `/idme-base:api-council-writer` → `/doc-coauthoring`
- **NEW:** `/claude-md-management` → `/idme-base:writer` → `/idme-base:design-document-writer` → `/idme-base:adr-writer` → `/idme-base:arb-writer` → `/idme-base:api-council-writer` → `/doc-coauthoring` → `/document-release` (close the loop)
- **Why:** `claude-md-management` is the new first stop for project memory; `/document-release` closes the doc loop.

### K. Autonomous Iteration
- **OLD:** `/autoresearch:plan` → `/autoresearch` → `/autoresearch:fix` → `/autoresearch:ship`
- **NEW:** `/goal` (native lightweight) **OR** `/autoresearch:plan` → `/autoresearch:reason` → `/autoresearch` → `/autoresearch:fix` → `/autoresearch:security` → `/autoresearch:ship`
- **Why:** new native `/goal` is the lightweight path; `/autoresearch:reason` is now a step before iteration; `/autoresearch:security` slots in before ship.

### L. Document & Office Generation — unchanged.

### M. Browser Automation
- **OLD:** `/browse` → `/browser-use` → `/connect-chrome` → `/setup-browser-cookies`
- **NEW:** `/setup-browser-cookies` (auth FIRST) → `/connect-chrome` (real Chrome) **OR** `/browse` (headless) **OR** `/remote-browser` (sandbox tunnel) → `/browser-use` (direct)
- **Why:** ordering matters — auth before navigation. Adds `/remote-browser` as a 4th option.

### N. Google Workspace Daily Workflow — unchanged.

### O. Google Workspace Automation — unchanged.

### P. Persona-Driven Workspace — unchanged.

### Q. Developer Experience Audit
- **OLD:** `/plan-devex-review` → `/devex-review` → `/design-review` → `/qa`
- **NEW:** `/plan-devex-review` → `/devex-review` → `/design-review` → `/qa` → `/landing-report` → `/verify`
- **Why:** `/landing-report` measures first-touch and time-to-Hello-World — the actual DX metrics. `/verify` confirms the docs site still works after fixes.

### R. Scheduled Automation
- **OLD:** `/schedule create ... --cron` ...
- **NEW:** same body + add `/loop` self-paced examples + `/schedule list` + `/schedule run-now <id>` to test before letting cron run
- **Why:** the cheatsheet should show the test path, not just the create path.

### S. Cross-AI Second Opinion
- **OLD:** `/codex:setup` → `/codex:rescue` → `/codex review` → `/gsd:review --all`
- **NEW:** `/codex:setup` → `/codex:adversarial-review` (NEW) → `/codex:rescue` → `/codex:review` → `/codex:result` → `/codex:status` → `/gsd:review --all` → `/advisor` (native — consult an even stronger model on the hardest finding)
- **Why:** `/codex:adversarial-review` is the new red-team variant; `/advisor` (native) escalates to the strongest model.

### T. Library Documentation Lookup — unchanged.

### U. Project Bootstrap & Onboarding
- **OLD:** `/init` → `/setup-gbrain` → `/setup-deploy` → `/setup-browser-cookies` → `/fewer-permission-prompts`
- **NEW:** `/claude-code-setup` (greenfield install) → `/init` → `/claude-md-management` → `/setup-gbrain` → `/setup-deploy` → `/setup-browser-cookies` → `/fewer-permission-prompts` → `/doctor` (sanity)
- **Why:** new `claude-code-setup` exists for greenfield; `/doctor` ends with a health gate.

### V. New Skill / MCP Authoring
- **OLD:** `/skill-creator` → `/mcp-builder` → `/superpowers:writing-skills` → `/superpowers:test-driven-development` → `/review` → `/ship`
- **NEW:** `/plugin-dev` → `/skill-creator` → `/agent-sdk-dev` (if agent) → `/mcp-server-dev` → `/mcp-tunnels` (if exposed) → `/hookify` → `/commit-commands` → `/example-plugin` (as template) → `/superpowers:writing-skills` → `/superpowers:test-driven-development` → `/playground` → `/code-review` → `/ship`
- **Why:** the §33 Plugin Authoring Toolkit shipped 11 more Anthropic plugins — V should compose them. `mcp-tunnels` for exposed MCP, `commit-commands` for commit-time slash commands.

### W. Onboarding to Unknown Codebase
- **OLD:** `/init` → `/gsd:map-codebase` → `/claude-mem:learn-codebase` → `/graphify` → `/sync-gbrain` → `/context-save`
- **NEW:** `/init` → `/gsd:map-codebase` → `/claude-mem:learn-codebase` → `/graphify` → `/sync-gbrain` → `/claude-mem:smart-explore` → `/claude-mem:pathfinder` → `/context-save`
- **Why:** the two new claude-mem skills (`smart-explore`, `pathfinder`) compound on top of `learn-codebase` for navigation queries.

### X. Idea → PRD → Tasks → Autonomous Build
- **OLD:** `/office-hours` → `/prd-taskmaster` → `/expand-tasks` → `/superpowers:write-plan` → `/superpowers:execute-plan` → `/autoresearch:ship`
- **NEW:** `/office-hours` → `/superpowers:brainstorming` → `/prd-taskmaster` → `/expand-tasks` → `/superpowers:write-plan` → `/autoplan` (CEO/Design/Eng/DX gauntlet, auto-decisions) → `/superpowers:execute-plan` → `/autoresearch:ship`
- **Why:** `/superpowers:brainstorming` is now mandatory before any creative work; `/autoplan` runs the four-review gauntlet without user check-ins.

### Y. Plan Hardening Gauntlet
- **OLD:** `/superpowers:write-plan` → `/plan-ceo-review` → `/plan-design-review` → `/plan-eng-review` → `/plan-devex-review` → `/codex consult` → `/gsd:review --all` → `/autoplan`
- **NEW:** `/superpowers:write-plan` → `/autoplan` (one shot for CEO+Design+Eng+DX) → `/codex:adversarial-review` → `/advisor` → `/gsd:review --all`
- **Why:** `/autoplan` collapses 4 separate plan reviews into one; `/codex:adversarial-review` + `/advisor` are the new cross-AI escalations.

### Z. Knowledge Compounding Session
- **OLD:** `/graphify` → `/claude-mem:knowledge-agent` → `/idme-base:writer` → `/idme-base:adr-writer` → `/learn`
- **NEW:** `/graphify` → `/claude-mem:knowledge-agent` → `/claude-mem:smart-explore` → `/idme-base:writer` → `/idme-base:adr-writer` → `/learn`
- **Why:** `smart-explore` interrogates the knowledge graph; should always follow `knowledge-agent`.

### AA. Live Site Forensic Replication — unchanged (already optimal).

### AB. Parallel-Worktree Multi-Feature Sprint
- **OLD:** `/superpowers:using-git-worktrees` → `/gsd:new-workspace` → `/superpowers:dispatching-parallel-agents` → `/godmode:parallel-execution` → `/superpowers:finishing-a-development-branch` → `/land-and-deploy`
- **NEW:** `/batch` (native — fanout primitive) → `/superpowers:using-git-worktrees` → `/gsd:new-workspace` → `/superpowers:dispatching-parallel-agents` → `/godmode:parallel-execution` → `/superpowers:subagent-driven-development` → `/superpowers:finishing-a-development-branch` → `/land-and-deploy`
- **Why:** native `/batch` is the fan-out primitive; `/superpowers:subagent-driven-development` adds discipline.

### AC. Production Incident Response
- **OLD:** `/guard` → `/careful` → `/investigate` → `/superpowers:systematic-debugging` → `/cso` → `/canary` → `/idme-base:adr-writer`
- **NEW:** `/guard` → `/careful` → `/freeze` → `/investigate` → `/superpowers:systematic-debugging` → `/cso` → `/security-review` → `/canary` → `/idme-base:adr-writer` → `/retro` (incident retro)
- **Why:** add `/freeze` for explicit destructive-op lock; add `/retro` to make every incident a learning event.

### AD. Autonomous Background Operator (24/7)
- **OLD:** `/schedule "nightly health"` → `/schedule "nightly cso"` → `/loop 10m /qa-only` → `/ralph` → `/autoresearch` → `/gws-workflow-weekly-digest`
- **NEW:** same + `/schedule create "weekly security"` → `/ralph-loop` (Anthropic packaging) → `/autoresearch:scenario` (scenario sweeps)
- **Why:** `/ralph-loop` is the official Anthropic packaging; `/autoresearch:scenario` extends overnight runs.

### AE. Visual Asset → Production (Figma round-trip)
- **OLD:** `/figma:figma-implement-design` → `/frontend-design` → `/ui-ux-pro-max` → `/design-review` → `/figma:figma-code-connect` → `/benchmark`
- **NEW:** `/figma:figma-use` → `/figma:figma-generate-design` (from spec) → `/frontend-design` → `/ui-ux-pro-max` → `/design-review` → `/figma:figma-code-connect` → `/figma:figma-use-slides` (if presenting) → `/benchmark`
- **Why:** figma-implement-design dropped in 2.2.12; figma-use-slides adds presentation path.

### AF. Meeting → Action → Tracked Work — unchanged.

### AG. Compress & Continue (cross-context handoff)
- **OLD:** `/gsd:session-report` → `/context-save` → `/claude-mem:timeline-report` → `/caveman:compress` → `bd compact` → `[/clear]` → `/context-restore`
- **NEW:** `/gsd:session-report` → `/usage` → `/context-save` → `/claude-mem:timeline-report` → `/caveman:compress` → `bd compact` → `[/clear]` → `/context-restore`
- **Why:** `/usage` quantifies how much context you actually freed.

### AH. Full-Stack Plugin Authoring
- **OLD:** 14-step authoring chain
- **NEW:** add `/plugin-dev`, `/agent-sdk-dev` (if agent), `/mcp-server-dev`, `/mcp-tunnels` (if exposed), `/commit-commands`, `/example-plugin`, `/cwc-makers` to the chain; keep all existing steps.
- **Why:** the 11 new Anthropic plugins make full-stack plugin authoring possible without leaving the marketplace.

### AI. M5Stack ESP32 Device Onboarding — unchanged.

### AJ. Apple Ingest & Map — unchanged (just shipped).

### AK. Apple Inquisitor — unchanged (just shipped).

### AL. Apple Loom — unchanged (just shipped).

---

## 4. Net-New Sequences This Audit

- **AM. PR Review Pipeline** — `/pr-review-toolkit` + `/code-review` + `/security-review` + `/codex:adversarial-review` + `/advisor` + `/gsd:review --all`
- **AN. Code Modernization Sweep** — `/code-modernization` + `/code-simplifier` + `/simplify` + `/code-review` + `/superpowers:test-driven-development` + `/verify`
- **AO. Cross-Channel Comms (Discord / Telegram / iMessage)** — `/discord` + `/telegram` + `/imessage` + `/gws-gmail-send` + `/recipe-send-team-announcement`
- **AP. LSP-Augmented Refactor** — `swift-lsp` / `pyright-lsp` / `gopls-lsp` / etc. + `/code-review` + `/simplify` + `/superpowers:finding-duplicate-functions` + `/verify`

---

## 5. Skills That Should Move Into Their Own §

- **§ Comms Suite** — currently no dedicated section for non-GWS comms. Discord/Telegram/iMessage deserve §19a Comms.
- **§ Plugin Marketplace Specific Skills** — `pr-review-toolkit`, `mcp-tunnels`, `claude-md-management`, `code-modernization`, `code-simplifier`, `feature-dev`, `cwc-makers`, `agent-sdk-dev`, `plugin-dev` could form a §36 "Anthropic Marketplace Power Tools".

These structural moves are flagged for a future `/os-integrate` run, not auto-applied in this audit.

---

## 6. Definition of Done — this audit

- [x] Inventory of installed vs cheatsheet — Section 1.
- [x] New skills enumerated — Section 2.
- [x] 38 sequences audited — Section 3.
- [x] 4 net-new sequences proposed — Section 4.
- [ ] Cheatsheet § A–AL sequence bodies updated — applied by patch step.
- [ ] 4 new sequences appended — applied by patch step.
- [ ] index.html workflows array updated — applied by patch step.
- [ ] Counts in TOC + footer bumped — applied by patch step.

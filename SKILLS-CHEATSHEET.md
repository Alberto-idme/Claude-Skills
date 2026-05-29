# Claude Code Skills Cheat Sheet

> 555+ skills across 35 suites and 35 named workflow sequences. Organized by workflow stage with mini use cases. Last refresh: **2026-05-26** (Claude 4.x model family + CC v2.1.150 + `/claude-api` Managed Agents + adaptive thinking).
>
> **What's new in this refresh:**
> - **Claude 4.x model family**: Opus 4.7 (`claude-opus-4-7`), Opus 4.6 (`claude-opus-4-6`), Sonnet 4.6 (`claude-sonnet-4-6`), Haiku 4.5 (`claude-haiku-4-5`) — all with 1M context (Haiku: 200K). See [§26 `/model`](#26-native-claude-code-commands).
> - **`/claude-api` updated** (§13): now covers Managed Agents (server-side stateful agents), model migration 4.5→4.6→4.7, adaptive thinking (`thinking: {type: "adaptive"}`), new `effort` parameter (`low/medium/high/xhigh/max`), `budget_tokens` deprecated on 4.6/4.7, Task Budgets beta (Opus 4.7)
> - **Claude Code v2.1.150** — updated native command count and CLI flags
>
> **Previous refresh (2026-05-26 earlier):**
> - New section [§35 — Vercel Plugin (26+ skills)](#35-vercel-plugin) — full auto-injecting suite: AI SDK, AI Gateway, Next.js, Vercel Functions, storage, auth, shadcn, CI/CD + 3 specialist agents
> - `/figma:figma-use-slides` added to §4 — Figma Slides-specific `use_figma` context (figma plugin 2.2.12)
> - `figma-implement-design` and `figma-create-design-system-rules` deprecated (removed in figma 2.2.12)
>
> **Previous refresh (2026-05-12 late):**
> - 21 new skills from `claude-plugins-official` marketplace sync
> - New section [§33 — Plugin Authoring Toolkit](#33-plugin-authoring-toolkit) — 16 skills for building plugins, MCP servers, hooks, slash commands, agents
> - New section [§34 — M5Stack / ESP32 IoT](#34-m5stack--esp32-iot) — `m5-onboard`, `cardputer-buddy` for Cardputer/Core/Stick onboarding
> - 2 new workflow sequences AH (plugin authoring) + AI (M5Stack onboarding)
> - §4 Figma now lists `generate-project-plan` (FigJam project plan board from PRD)
> - Cross-cutting "Skill Nature" framing below to help pick the right tool
>
> **Previous refresh (2026-05-12 early):**
> - 12 new cross-suite workflow sequences (V → AG) — see [§27](#27-workflow-sequences)
> - Added: `nanochat`, `karpathy-autoresearch`, `expand-tasks`, `sync-gbrain` (previously uncatalogued)
> - New section [§31 — ML / LLM Training](#31-ml--llm-training)
> - New section [§32 — OS Management](#32-os-management--autonomous-self-improvement)
>
> ### Skill Nature — pick by intent, not by name
>
> | Nature | Examples | When to reach for it |
> |-------|---------|----------------------|
> | **Generators** | `/design-html`, `/make-pdf`, `/docx`, `/figma:figma-generate-design`, `/canvas-design` | You want an artifact (file, page, doc) produced fresh |
> | **Analyzers / Auditors** | `/cso`, `/health`, `/devex-review`, `/qa-only`, `/forensics` (UI/UX site teardown), `/gsd:forensics` (workflow post-mortem), `/gsd:audit-milestone` | You want a verdict + report on existing work |
> | **Process / Orchestrators** | `/gsd:*`, `/superpowers:*`, `/godmode:*`, `/autoresearch`, `/btw`, `/ralph` | You want a multi-step workflow with checkpoints |
> | **Spec / Decision capture** | `/idme-base:writer`, `/idme-base:adr-writer`, `/prd-taskmaster`, `/office-hours` | You want decisions/requirements written down before coding |
> | **Memory / Persistence** | `/claude-mem:*`, `/graphify`, `/gsd:thread`, `/learn`, `/context-save`, `/beads:*` | You want to remember things across sessions or compacts |
> | **Browser / Real-world I/O** | `/browse`, `/browser-use`, `/open-gstack-browser`, `/scrape`, `/setup-browser-cookies`, `/remote-browser` | You need to act on or read from a live web page |
> | **Cross-AI consultation** | `/codex review`, `/codex:rescue`, `/gsd:review --all`, `/autoresearch:reason` | You want a second opinion / adversarial check |
> | **Compression / Discipline** | `/caveman`, `/freeze`, `/guard`, `/careful`, `/fewer-permission-prompts` | You want to constrain Claude's behavior or output |
> | **Ship / Land** | `/ship`, `/review`, `/land-and-deploy`, `/canary`, `/document-release`, `/gsd:ship` | You want code in front of users with safety nets |
>
> **Picking heuristic:** start at the leftmost column that matches your intent. Generators ship fastest; orchestrators ship safest; auditors prevent regret.

---

## Table of Contents

1. [gstack — Ship & QA Suite (46 skills)](#1-gstack--ship--qa-suite)
2. [GSD — Get Shit Done Framework (57 commands)](#2-gsd--get-shit-done-framework)
3. [Autoresearch (10 skills)](#3-autoresearch)
4. [Figma Plugin (10 skills, 2 deprecated)](#4-figma-plugin)
5. [graphify — Knowledge Graph (1 command, many subcommands)](#5-graphify--knowledge-graph)
6. [IDME Base — Document Writers (9 skills)](#6-idme-base--document-writers)
7. [Beads — Issue Tracker (1 skill, 26 subcommands)](#7-beads--issue-tracker)
8. [PRD Taskmaster (1 skill)](#8-prd-taskmaster)
9. [UI/UX Pro Max (7 skills)](#9-uiux-pro-max)
10. [Browser Use (4 skills)](#10-browser-use)
11. [Document & Office (6 skills)](#11-document--office)
12. [Creative & Design (6 skills)](#12-creative--design)
13. [Developer Utilities (9 skills)](#13-developer-utilities)
14. [Superpowers (14 skills)](#14-superpowers)
15. [Superpowers Lab (4 skills)](#15-superpowers-lab)
16. [Godmode (37 skills)](#16-godmode)
17. [Apple Platform (2 skills)](#17-apple-platform)
18. [Claude Code Configuration (5 skills)](#18-claude-code-configuration)
19. [Google Workspace Suite (44 skills)](#19-google-workspace-suite)
20. [Google Workspace Recipes (35 recipes)](#20-google-workspace-recipes)
21. [Google Workspace Personas (10 personas)](#21-google-workspace-personas)
22. [Video & Motion (2 skills)](#22-video--motion)
23. [Codex Plugin (2 skills)](#23-codex-plugin)
24. [Context7 Plugin (2 skills)](#24-context7-plugin)
25. [claude-mem — Memory & Planning (8 skills)](#25-claude-mem--memory--planning)
26. [Native Claude Code Commands (~77 commands)](#26-native-claude-code-commands)
27. [Workflow Sequences](#27-workflow-sequences)
28. [Language Server Protocol (LSP) Plugins (4 plugins)](#28-language-server-protocol-lsp-plugins)
29. [Ralph — Autonomous Dev Loop](#29-ralph--autonomous-dev-loop)
30. [Caveman — Response Compression (7 skills)](#30-caveman--response-compression)
31. [ML / LLM Training (2 skills)](#31-ml--llm-training)
32. [OS Management — Autonomous Self-Improvement (4 skills)](#32-os-management--autonomous-self-improvement)
33. [Plugin Authoring Toolkit (16 skills)](#33-plugin-authoring-toolkit)
34. [M5Stack / ESP32 IoT (2 skills)](#34-m5stack--esp32-iot)
35. [Vercel Plugin (26+ skills, 3 agents)](#35-vercel-plugin)

---

## 1. gstack — Ship & QA Suite (46 skills)

### Ideation & Planning

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/office-hours` | YC-style brainstorm. Startup mode (6 forcing questions) or Builder mode (design thinking) | Auto-detects mode | "I have an idea for a notification system" → runs 6 forcing questions → saves design doc |
| `/plan-ceo-review` | CEO/founder plan review. Challenges premises, finds 10-star product | 4 modes: SCOPE EXPANSION, SELECTIVE, HOLD, REDUCTION | Enter plan mode → `/plan-ceo-review` → selects SELECTIVE EXPANSION → upgrades ambition while holding core |
| `/plan-eng-review` | Eng manager plan review. Locks architecture, data flow, edge cases | Interactive, opinionated | After CEO review → `/plan-eng-review` → walks through architecture decisions → locks the plan |
| `/plan-design-review` | Designer's eye plan review. Rates each dimension 0-10 | Plan mode only | After eng review → `/plan-design-review` → rates typography 6/10 → explains what makes it a 10 → fixes plan |
| `/plan-devex-review` | Interactive developer experience plan review. Explores personas, benchmarks competitors, designs magical moments | 3 modes: DX EXPANSION, DX POLISH, DX BASELINE | After eng review → `/plan-devex-review` → scores TTHW, error UX, CLI help → fixes plan |
| `/autoplan` | Runs all 3 reviews automatically with 6 decision principles | Auto-decisions, surfaces only taste calls | `/autoplan` → auto-answers 25 questions → surfaces 3 taste decisions for your approval |
| `/devex-review` | Live DX audit. Tests getting-started flow, times TTHW, screenshots errors, evaluates CLI help | URL | `/devex-review https://docs.myapi.com` → tries the quickstart → times TTHW at 12min → DX scorecard |
| `/pair-agent` | Pair a remote AI agent with your browser. Generates setup key for OpenClaw, Hermes, Codex, Cursor | One command | `/pair-agent` → generates setup key → other agent connects via HTTP → shares browser |
| `/plan-tune` | Self-tuning question sensitivity + developer psychographic for gstack | Observability v1 | `/plan-tune` → calibrates how aggressively gstack asks clarifying questions → saves your psychographic profile |

### Design & Branding

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/design-consultation` | Creates complete design system → DESIGN.md | Interactive | New project → `/design-consultation` → proposes typography, colors, spacing → generates font+color preview page |
| `/design-review` | Visual QA on live site. Finds & fixes spacing, hierarchy, AI slop | URL, commits atomically | `/design-review https://myapp.com` → finds 8 issues → fixes each with before/after screenshots |
| `/design-shotgun` | Generate multiple AI design variants, comparison board, iterate | Standalone | `/design-shotgun` → generates 4 variants → opens comparison board → collect feedback → refine winner |
| `/design-html` | Production-quality HTML/CSS from designs or descriptions | Works with mockups, plans, or scratch | `/design-html` → picks Pretext patterns → generates dynamic, reflowing HTML/CSS → 30KB, zero deps |

### Development & Debugging

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/investigate` | 4-phase root cause debugging. Iron Law: no fix without root cause | Auto-locks scope via /freeze, 3-strike escalation | "Login fails silently" → `/investigate` → Phase 1: reproduces → Phase 2: traces to token expiry → Phase 3: confirms → Phase 4: fixes |
| `/codex` | OpenAI Codex second opinion. Review / Challenge / Consult modes | `review`, `challenge`, `consult` | `/codex review` → independent diff analysis → pass/fail verdict with reasoning |
| `/simplify` | Reviews changed code for reuse, quality, efficiency | Built-in | After writing a feature → `/simplify` → finds 3 unnecessary abstractions → removes them |

### Browser & QA

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/browse` | Headless Chromium (~100ms/cmd). Navigate, click, fill, screenshot, diff | `goto`, `snapshot`, `click`, `fill`, `screenshot`, `responsive` | `/browse` → `$B goto https://app.com` → `$B snapshot -i` → `$B click "#login"` → `$B fill "#email" "test@test.com"` |
| `/gstack` | Fast headless browser for QA testing and site dogfooding (alias entry to the gstack browser primitives) | Same as /browse | `/gstack` → run gstack browser commands directly |
| `/open-gstack-browser` | Launch GStack Browser — AI-controlled Chromium with the sidebar extension baked in | One command | `/open-gstack-browser` → opens GStack Browser → side panel ready for AI-driven flows |
| `/setup-browser-cookies` | Import cookies from your real browser for authenticated testing | `<domain>` (optional) | `/setup-browser-cookies github.com` → imports GitHub session → now /qa can test authenticated pages |
| `/qa` | Full QA: test + fix + verify. 3 tiers: Quick/Standard/Exhaustive | URL, tier | `/qa https://myapp.com` → finds 12 bugs → fixes 10 with atomic commits → before/after health score: 45→92 |
| `/qa-only` | Report-only QA. Same testing, no code changes | URL | `/qa-only https://myapp.com` → produces bug report with screenshots and repro steps |
| `/benchmark` | Performance regression detection. Core Web Vitals, load times, bundle size | `--baseline`, `--diff`, `--trend`, `--pages` | `/benchmark https://myapp.com --baseline` → captures baseline → later `/benchmark --diff` → shows regressions |
| `/benchmark-models` | Cross-model benchmark for gstack skills. Runs the same prompt through Claude, GPT, etc. | Multi-provider | `/benchmark-models` → compares Claude/GPT/Gemini outputs → produces side-by-side scorecard |
| `/scrape` | Pull structured data from a web page. First call prototypes the flow via $B primitives; subsequent calls on the same intent run the codified browser-skill in ~200ms | Read-only; use /automate for mutations | `/scrape https://news.ycombinator.com` → prototypes scraper → returns JSON → second call runs in 200ms |
| `/skillify` | Codify the most recent successful `/scrape` flow into a permanent browser-skill on disk. Synthesizes `script.ts` + test + fixture, runs tests, asks before committing | Run after a successful /scrape | `/skillify` → walks back through conversation → synthesizes script.ts + test → commits permanent browser-skill |

### Shipping & Deployment

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/review` | Pre-landing PR review. SQL safety, LLM trust boundaries, side effects | Auto-detects branch | Before merging → `/review` → flags unsafe SQL migration and missing input validation |
| `/ship` | Full ship: merge base, test, review diff, bump VERSION, CHANGELOG, PR | Auto-detects platform | Code ready → `/ship` → runs tests → reviews diff → bumps v1.2.3 → creates PR with CHANGELOG |
| `/land-and-deploy` | Merge PR → wait CI → deploy → canary health check | Needs `/setup-deploy` first | After `/ship` creates PR → `/land-and-deploy` → merges → waits for deploy → verifies production health |
| `/landing-report` | Read-only queue dashboard for workspace-aware ship. Shows VERSION slot status | Read-only | `/landing-report` → "PR-72 in slot 1, PR-73 queued" → shows landing pipeline state |
| `/setup-deploy` | One-time deploy config. Writes to CLAUDE.md | Auto-detects platform | `/setup-deploy` → detects Fly.io → configures health checks → writes config → `/land-and-deploy` works |
| `/canary` | Post-deploy monitoring. Console errors, perf regressions, page failures | `--duration`, `--baseline`, `--pages` | `/canary https://myapp.com --duration 10m` → monitors for 10 min → catches console error spike at 3min mark |
| `/document-release` | Post-ship docs update. README, ARCHITECTURE, CHANGELOG, TODOS | Auto from diff | After merge → `/document-release` → updates README with new API endpoints → polishes CHANGELOG voice |

### Safety & Maintenance

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/careful` | Warns before destructive commands (rm -rf, DROP TABLE, force-push) | Session-scoped | `/careful` → later `rm -rf /data` → WARNING: destructive operation → confirm/deny |
| `/freeze` | Restrict edits to one directory | Interactive path selection | `/freeze` → enter `src/auth/` → now Edit/Write blocked outside src/auth/ |
| `/guard` | /careful + /freeze combined | Both protections | `/guard` → enter `src/api/` → destructive warnings ON + edits locked to src/api/ |
| `/unfreeze` | Remove /freeze restriction | None | `/unfreeze` → edits allowed everywhere again |
| `/cso` | Security audit. OWASP, STRIDE, secrets, dependencies, CI/CD, LLM security | daily (8/10 gate) / comprehensive (2/10 gate) | `/cso` → daily mode → finds hardcoded API key and vulnerable dependency → trend comparison with last audit |
| `/health` | Code quality dashboard. Type checker, linter, tests, dead code | Weighted 0-10 score, trends | `/health` → runs all checks → composite score 7.2/10 → tracks improvement over time |
| `/retro` | Weekly engineering retrospective with team breakdowns and trends | Cross-project support | `/retro` → analyzes 47 commits → highlights 3 wins, 2 growth areas, 1 pattern concern |
| `/context-save` | Save working context — git state, decisions, remaining work | Session-scoped | `/context-save` → captures state → resumable later via `/context-restore` |
| `/context-restore` | Restore working context saved earlier by `/context-save`. Loads most recent save | Session-scoped | `/context-restore` → next session picks up exactly where you left off |
| `/learn` | Manage project learnings across sessions | `review`, `search`, `prune`, `export` | `/learn` → "didn't we fix this before?" → searches learnings → finds past pattern |
| `/fewer-permission-prompts` | Scan transcripts for common read-only Bash and MCP calls → add prioritized allowlist to project `.claude/settings.json` | Project-scoped | `/fewer-permission-prompts` → finds 14 frequently approved commands → writes allowlist → fewer prompts |
| `/setup-gbrain` | Set up gbrain for this coding agent — installs CLI, initializes local PGLite database | One-time | `/setup-gbrain` → installs gbrain CLI → bootstraps local PGLite → ready for memory + retrieval |
| `/sync-gbrain` | Re-index this repo into gbrain. Refreshes agent search guidance in CLAUDE.md, registers native code-surface, runs capability checks. Idempotent | Re-runnable | `/sync-gbrain` → "gbrain search isn't finding things" → re-indexes → updates CLAUDE.md guidance |
| `/gstack-upgrade` | Upgrade gstack to latest | Auto-detects install type | `/gstack-upgrade` → shows changelog → confirms → upgrades |

---

## 2. GSD — Get Shit Done Framework

### Project Lifecycle

```
/gsd:new-project → /gsd:plan-phase 1 → /gsd:execute-phase 1 → /gsd:verify-work 1
    ↓ (repeat per phase)
/gsd:audit-milestone → /gsd:complete-milestone v1.0 → /gsd:new-milestone v1.1
```

### Initialization

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:new-project` | Full project init: questioning → research → requirements → roadmap | `--auto` | `/gsd:new-project` → answers 8 questions → researches tech → creates PROJECT.md + ROADMAP.md with 6 phases |
| `/gsd:new-milestone` | Start next milestone cycle | `[milestone name]` | `/gsd:new-milestone "v1.1 Notifications"` → updates PROJECT.md → creates new requirements → extends roadmap |
| `/gsd:new-workspace` | Isolated workspace with repo copies | `--name`, `--repos`, `--strategy worktree\|clone` | `/gsd:new-workspace --name auth-rewrite --repos api,web --strategy worktree` → creates isolated env |
| `/gsd:map-codebase` | Analyze codebase → 7 structured docs | `[area]` | `/gsd:map-codebase api` → spawns 4 parallel agents → produces STACK.md, ARCHITECTURE.md, CONVENTIONS.md, etc. |
| `/gsd:settings` | Configure workflow toggles | Interactive | `/gsd:settings` → enable/disable research agent, plan checker, verifier, branching |
| `/gsd:set-profile` | Switch model tier for agents | `quality\|balanced\|budget\|inherit` | `/gsd:set-profile balanced` → all subagents now use balanced tier |
| `/gsd:profile-user` | Generate your developer behavioral profile | `--questionnaire`, `--refresh` | `/gsd:profile-user` → analyzes past sessions → creates USER-PROFILE.md with work style preferences |

### Phase Cycle (Core Loop)

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:discuss-phase` | Pre-planning context gathering | `<phase> [--auto] [--batch]` | `/gsd:discuss-phase 3` → scouts codebase → asks 5 targeted questions → saves CONTEXT.md |
| `/gsd:list-phase-assumptions` | Surface Claude's assumptions before planning | `[phase]` | `/gsd:list-phase-assumptions 3` → shows 12 assumptions across 5 areas → you correct 3 → saves corrections |
| `/gsd:research-phase` | Standalone research (usually auto in plan-phase) | `[phase]` | `/gsd:research-phase 3` → researches auth libraries → produces RESEARCH.md with comparison table |
| `/gsd:plan-phase` | Create executable PLAN.md with verification | `[phase] [--auto] [--research] [--skip-research] [--gaps] [--reviews]` | `/gsd:plan-phase 3` → researches → plans → verifies → iterates until plan-checker passes |
| `/gsd:execute-phase` | Execute plans with wave-based parallelization | `<phase> [--wave N] [--gaps-only] [--interactive]` | `/gsd:execute-phase 3` → groups 4 plans into 2 waves → spawns agents → collects results |
| `/gsd:verify-work` | Conversational UAT testing | `[phase]` | `/gsd:verify-work 3` → tests 8 UAT criteria one by one → passes 7 → creates fix plan for 1 failure |
| `/gsd:add-tests` | Generate tests for completed phase | `<phase> [instructions]` | `/gsd:add-tests 3` → classifies files → generates 12 unit tests + 3 E2E tests → commits |
| `/gsd:validate-phase` | Audit Nyquist validation gaps retroactively | `[phase]` | `/gsd:validate-phase 3` → finds missing coverage → generates gap-filling tests |

### UI-Specific Phase Commands

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:ui-phase` | Generate UI-SPEC.md design contract | `[phase]` | `/gsd:ui-phase 4` → researches UI → produces UI-SPEC.md → verified by gsd-ui-checker |
| `/gsd:ui-review` | 6-pillar visual audit of implemented frontend | `[phase]` | `/gsd:ui-review 4` → grades layout 4/4, typography 3/4, color 2/4 → produces UI-REVIEW.md |

### Roadmap Management

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:add-phase` | Append new phase to milestone | `<description>` | `/gsd:add-phase "Email notification templates"` → creates phase 7 → updates ROADMAP.md |
| `/gsd:insert-phase` | Insert urgent work as decimal phase | `<after> <description>` | `/gsd:insert-phase 3 "Fix auth bug"` → creates phase 3.1 → no renumbering needed |
| `/gsd:remove-phase` | Remove unstarted future phase | `<phase>` | `/gsd:remove-phase 6` → deletes phase 6 dir → renumbers 7→6, 8→7 |
| `/gsd:add-backlog` | Park idea in 999.x backlog | `<description>` | `/gsd:add-backlog "Dark mode support"` → creates 999.1 → parked for future milestone |
| `/gsd:review-backlog` | Review and promote/remove backlog items | None | `/gsd:review-backlog` → shows 5 items → promote 2 to active phases → remove 1 stale idea |
| `/gsd:plan-milestone-gaps` | Create phases for audit-identified gaps | None | After audit finds 3 gaps → `/gsd:plan-milestone-gaps` → creates 3 fix phases → offers to plan each |

### Milestone Lifecycle

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:audit-milestone` | Audit completion against original intent | `[version]` | `/gsd:audit-milestone` → checks all requirements → finds 2 gaps → spawns integration checker |
| `/gsd:audit-uat` | Cross-phase UAT audit | None | `/gsd:audit-uat` → scans all phases → finds 4 pending, 2 skipped UAT items → produces human test plan |
| `/gsd:complete-milestone` | Archive and prepare for next | `<version>` | `/gsd:complete-milestone v1.0` → archives → tags git v1.0 → prepares for v1.1 |
| `/gsd:milestone-summary` | Generate onboarding-ready summary | `[version]` | `/gsd:milestone-summary` → produces 7-section document covering what was built and why |

### Execution Modes

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:autonomous` | Run all remaining phases unattended | `--from N` | `/gsd:autonomous` → discuss→plan→execute for each remaining phase → pauses only for blockers |
| `/gsd:manager` | Interactive multi-phase command center | None | `/gsd:manager` → dashboard shows 6 phases → dispatches plan for phase 3 + execute for phase 2 in parallel |
| `/gsd:quick` | Small task with GSD guarantees | `--full`, `--discuss`, `--research` | `/gsd:quick "Add rate limiting to /api/users"` → plans → executes → atomic commit |
| `/gsd:fast` | Trivial inline task, no subagents | `[description]` | `/gsd:fast "Fix typo in README"` → fixes inline → done in 30 seconds |
| `/gsd:do` | Smart command dispatcher | `<description>` | `/gsd:do "I need to debug the auth flow"` → routes to `/gsd:debug` |

### Session Management

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:next` | Auto-advance to next logical step | None | `/gsd:next` → reads state → "Phase 3 planned, not executed" → invokes `/gsd:execute-phase 3` |
| `/gsd:progress` | Show progress and route to action | None | `/gsd:progress` → "3/6 phases done, phase 4 needs planning" → routes to plan-phase |
| `/gsd:pause-work` | Save state for next session | None | `/gsd:pause-work` → writes `.continue-here.md` → commits WIP |
| `/gsd:resume-work` | Restore context from previous session | None | `/gsd:resume-work` → finds checkpoint → "You were mid-execute on phase 3, task 4/7" → continues |
| `/gsd:session-report` | Generate session summary | None | `/gsd:session-report` → "4 tasks completed, 127K tokens used, 2 phases advanced" |
| `/gsd:thread` | Persistent cross-session context threads | `[name\|description]` | `/gsd:thread "perf investigation"` → creates thread → preserves context across sessions |
| `/gsd:workstreams` | Parallel workstream management | `list\|create\|status\|switch\|progress\|complete\|resume` | `/gsd:workstreams create "api-v2"` → independent phase tracking for API work |

### Ideas & Notes

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:note` | Zero-friction idea capture | `<text>`, `list`, `promote <N>` | `/gsd:note "Consider WebSocket for real-time updates"` → appended → later `/gsd:note promote 3` |
| `/gsd:add-todo` | Structured todo from conversation | `[description]` | `/gsd:add-todo` → extracts context → creates todo with area tag and priority |
| `/gsd:check-todos` | List and work on pending todos | `[area]` | `/gsd:check-todos api` → shows 4 API todos → select one → routes to action |
| `/gsd:plant-seed` | Forward-looking idea with trigger conditions | `[summary]` | `/gsd:plant-seed "Add i18n when we expand to EU"` → surfaces automatically when EU milestone starts |

### Debugging & Health

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:debug` | Scientific method debugging with persistent state | `[issue]` | `/gsd:debug "Tests pass locally but fail in CI"` → gathers symptoms → spawns debugger → tracks hypotheses |
| `/gsd:forensics` | **GSD workflow post-mortem** — diagnoses failed/stuck GSD runs from git + `.planning/` artifacts. *Not* the UI/UX site teardown — for that, see [`/forensics` in §13](#13-developer-utilities) | `[description]` | `/gsd:forensics "Phase 3 execution got stuck"` → analyzes git + artifacts → finds stuck loop → writes `.planning/forensics/REPORT.md` |
| `/gsd:health` | Diagnose .planning/ directory integrity | `--repair` | `/gsd:health --repair` → finds orphaned plan + invalid config → auto-fixes both |

### Shipping & Review

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/gsd:review` | Cross-AI peer review of plans | `--phase N [--gemini] [--claude] [--codex] [--all]` | `/gsd:review --phase 3 --all` → sends to Gemini + Codex → collects reviews → writes REVIEWS.md |
| `/gsd:ship` | Create PR after verification | `[phase\|milestone]` | `/gsd:ship 3` → pushes branch → creates PR with auto-generated body |
| `/gsd:pr-branch` | Clean branch without .planning/ commits | `[target]` | `/gsd:pr-branch` → filters out PLAN.md commits → clean diff for code review |

### Meta & Maintenance

| Command | What it does | Mini use case |
|---------|-------------|---------------|
| `/gsd:stats` | Project statistics dashboard | Shows phases, plans, git metrics, timeline |
| `/gsd:cleanup` | Archive old phase directories | After milestone complete → cleans .planning/phases/ |
| `/gsd:update` | Update GSD to latest | Shows changelog → confirms → updates |
| `/gsd:reapply-patches` | Restore local mods after update | After update wipes customizations → reapplies patches |
| `/gsd:help` | Command reference | Quick lookup |
| `/gsd:join-discord` | Discord community link | Community support |
| `/gsd:list-workspaces` | Show all workspaces | Overview of isolated environments |
| `/gsd:remove-workspace` | Delete workspace + worktrees | Cleanup after feature work |

---

## 3. Autoresearch

Autonomous goal-directed iteration based on Karpathy's autoresearch principles. Loops autonomously: modify → verify → keep/discard → repeat. Applies to ANY task with a measurable metric.

| Command | What it does | Mini use case |
|---------|-------------|---------------|
| `/autoresearch` | Core autonomous iteration loop. Bounded via `Iterations: N` | `/autoresearch` → "Optimize bundle size" → iterates 10 times → keeps best result → reports improvement |
| `/autoresearch:plan` | Interactive wizard to build Scope, Metric, Direction & Verify from a Goal | `/autoresearch:plan` → defines goal → sets metric → configures direction → generates verify step |
| `/autoresearch:debug` | Autonomous bug-hunting loop. Scientific method + iteration. Finds ALL bugs | `/autoresearch:debug` → reproduces → hypothesizes → fixes bug 1 → continues → finds bug 2 → done |
| `/autoresearch:fix` | Autonomous fix loop. One fix per iteration, atomic, auto-reverted on failure | `/autoresearch:fix` → finds 7 errors → fixes each iteratively → reverts failures → 6/7 fixed |
| `/autoresearch:learn` | Autonomous codebase documentation engine. Scout, learn, generate/update docs | `/autoresearch:learn` → scouts codebase → generates docs → validates → fixes errors → done |
| `/autoresearch:security` | Autonomous security audit. STRIDE + OWASP Top 10 + red-team with 4 adversarial personas | `/autoresearch:security` → threat models → tests OWASP → red-teams with 4 personas → report |
| `/autoresearch:predict` | Multi-persona swarm prediction. Pre-analyze code from multiple expert perspectives | `/autoresearch:predict` → spawns 5 expert personas → each analyzes independently → synthesizes |
| `/autoresearch:ship` | Universal shipping workflow. 8-phase structured workflow for code, content, anything | `/autoresearch:ship` → 8 phases: prep → build → test → review → stage → deploy → verify → announce |
| `/autoresearch:scenario` | Scenario-driven use case generator. Explores edge cases from a seed scenario | `/autoresearch:scenario "User loses connection mid-payment"` → explores 12 derivative scenarios |
| `/autoresearch:reason` | Adversarial generate-critique-synthesize refinement. Multi-agent: generate → critique → synthesize → judge, repeated until convergence. 3 modes: convergent (default), creative, debate. Flags: `--judges N`, `--iterations N`, `--convergence N`, `--chain <tool>` | `/autoresearch:reason "Design the auth flow" --mode debate --judges 5` → 3 agents debate → judge picks winner → converges |

### Autoresearch Flow

```
/autoresearch:plan              → define goal + metric
/autoresearch                   → iterate toward goal
/autoresearch:reason            → adversarial refinement (generate → critique → synthesize)
/autoresearch:debug             → find all bugs
/autoresearch:fix               → fix all errors
/autoresearch:security          → security audit
/autoresearch:ship              → ship the result
```

---

## 4. Figma Plugin

| Skill | What it does | When to use | Mini use case |
|-------|-------------|-------------|---------------|
| `/figma:figma-use` | **MANDATORY** before every `use_figma` call. Loads Plugin API rules | Before ANY write to Figma canvas | Always call this first → then call `use_figma` with JS code |
| `/figma:figma-generate-design` | Build full pages in Figma from code/description, section by section | "Create this app screen in Figma" | Reads React component → discovers Nova components → builds page section-by-section in Figma |
| ~~`/figma:figma-implement-design`~~ | ~~Translate Figma → production code with 1:1 fidelity~~ | **[DEPRECATED 2026-05-26 — removed in figma plugin 2.2.12]** | — |
| `/figma:figma-generate-library` | Build design system in Figma from codebase | "Build our component library in Figma" | Multi-phase: Discovery → Foundations → Components → QA. 20-100+ use_figma calls |
| `/figma:figma-code-connect` | Create and maintain Figma Code Connect template files mapping Figma components ↔ code components | "Connect this Figma button to code" | Uses `get_code_connect_suggestions` → `send_code_connect_mappings` |
| ~~`/figma:figma-create-design-system-rules`~~ | ~~Generate design system rules for AI agents~~ | **[DEPRECATED 2026-05-26 — removed in figma plugin 2.2.12]** | — |
| `/figma:figma-use-figjam` | Work with FigJam boards. Add stickies, connectors, shapes, sections, tables, code blocks | FigJam brainstorms, flow diagrams, retros | `/figma:figma-use-figjam` → navigate FigJam board → place stickies + connectors → build retro board |
| `/figma:figma-generate-diagram` | Generate diagrams in FigJam from description. Supports flowchart, ERD, sequence, state, gantt, architecture, workflow | "Create a flowchart for auth flow" | `/figma:figma-generate-diagram` → "user auth ERD" → builds ERD with entities + relationships in FigJam |
| `/figma:figma-create-new-file` | Create a new blank Figma file | Starting a fresh design | `/figma:figma-create-new-file` → creates blank file → ready for design work |
| `/figma:generate-project-plan` | Generate a FigJam project plan board from a PRD + codebase context. Interactive: research → propose sections → per-section build | "Plan this project visually in FigJam" | PRD + repo → FigJam board with milestones, dependencies, risks, owners |
| `/figma:figma-use-slides` | **MANDATORY** before `use_figma` calls on a Figma Slides file. Loads Slides-specific rules (SLIDE_GRID, positioning gotchas, no `createPage`) | Any Slides canvas write (figma.com/slides/...) | Always call before building/editing Figma Slides decks |

### Figma Workflow Sequence

```
1. /figma:figma-generate-library         → build design system
2. /figma:figma-generate-design          → build screens (code → Figma)
3. /figma:figma-code-connect             → link components bidirectionally
4. /figma:figma-use-figjam              → FigJam boards for diagrams & retros
5. /figma:figma-generate-diagram        → auto-generate FigJam diagrams
6. /figma:generate-project-plan          → PRD → FigJam project plan board
7. /figma:figma-use-slides              → build/edit Figma Slides decks
```

---

## 5. graphify — Knowledge Graph

Turn any folder of files into a navigable knowledge graph. Produces HTML visualization, JSON edge data, GRAPH_REPORT.md (god nodes + community structure), and optional wiki.

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/graphify` | Build knowledge graph from current directory | `--update`, `--cluster-only`, `--wiki`, `--watch`, `--mcp`, `--obsidian`, `--directed`, `--neo4j`, `--svg`, `--graphml` | `/graphify` → 9-step pipeline → HTML graph + GRAPH_REPORT.md |
| `graphify query "<question>"` | Ask natural-language question over the graph | | `graphify query "what calls the auth module?"` → traverses edges → answer |
| `graphify path <A> <B>` | Find shortest connection path between two nodes | | `graphify path UserService PaymentAPI` → shows dependency chain |
| `graphify explain <node>` | Explain what a node does based on graph context | | `graphify explain "auth.ts"` → summarizes role in graph |
| `graphify add <url>` | Add a URL's content to the graph | | `graphify add https://docs.example.com` → scrapes → adds as node |
| `graphify --update` | Rebuild only changed files (incremental) | | After editing 3 files → `graphify --update` → 10s instead of 5min |
| `graphify --wiki` | Generate per-node wiki pages in graphify-out/wiki/ | | `graphify --wiki` → markdown wiki with cross-links for every node |
| `graphify --watch` | Live-reload graph as files change | | `graphify --watch` → graph updates automatically on file save |
| `graphify --mcp` | Expose graph as MCP server for agent consumption | | `graphify --mcp` → agents can query the graph via MCP tools |

> **Tip:** Set `MOONSHOT_API_KEY` for 3× cheaper Kimi K2.6 extraction. Edges are tagged EXTRACTED/INFERRED/AMBIGUOUS for audit trails.

---

## 6. IDME Base — Document Writers

### Writers

| Skill | What it does | Word limit | When to use |
|-------|-------------|------------|-------------|
| `/idme-base:writer` | RDR (Recommendation/Decisioning Record). Spec-first with research iterations | No limit | Complex features needing research before coding. 2-4 iteration cycles with beads + ChromaDB |
| `/idme-base:adr-writer` | ADR (Architectural Decision Record) | 900 words | Single architectural decision with trade-offs and alternatives |
| `/idme-base:arb-writer` | ARB (Architecture Review Board) submission | 900 words | Changes to foundational tech, data models, or multi-team changes. Includes SQL DDL + API specs |
| `/idme-base:api-council-writer` | API Council submission | N/A | New APIs, cross-domain changes, new integration patterns |
| `/idme-base:design-document-writer` | Technical design document from PRD | 2500 words | Comprehensive design: architecture, DB schema, API specs, key decisions |

### Lifecycle Management

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/idme-base:init` | Initialize RDR directory structure with README, TEMPLATE, and markdownlint config | Starting a new RDR directory in a project |
| `/idme-base:validate` | Validate RDR files for formatting, consistency, and quality | Before locking an RDR as "Proposed" |
| `/idme-base:status` | Update RDR status through lifecycle transitions, manage related beads issues | Moving an RDR through Draft → Proposed → Accepted → Implemented |
| `/idme-base:implement` | Spawn beads issues from locked RDR implementation plan | After an RDR is accepted and ready for implementation |

### Document Decision Tree

```
"Should I build this feature?"
  └─ Complex, needs research → /idme-base:writer (RDR)
       └─ Research complete, need design → /idme-base:design-document-writer
            └─ Key architectural decision → /idme-base:adr-writer
            └─ Multi-team impact → /idme-base:arb-writer
            └─ New API → /idme-base:api-council-writer
       └─ Ready to implement → /idme-base:implement (spawns beads tasks)
```

---

## 7. Beads — Issue Tracker

Git-backed issue tracker with dependencies, persistent across sessions and compaction.

| Command | What it does | Mini use case |
|---------|-------------|---------------|
| `bd create "title" -t task -p 1` | Create issue | `bd create "Add rate limiting" -t task -p 1 -l backend` |
| `bd list` | List issues with filters | `bd list --status open --label backend` |
| `bd show <id>` | Show issue details | `bd show PROJ-42` |
| `bd ready` | Find unblocked work | `bd ready` → shows tasks with no pending dependencies |
| `bd update <id>` | Update status/priority/fields | `bd update PROJ-42 --status in-progress` |
| `bd close <id>` | Close completed issue | `bd close PROJ-42` |
| `bd reopen <id>` | Reopen closed issue | `bd reopen PROJ-42` |
| `bd delete <id>` | Delete issue and clean up references | `bd delete PROJ-42` |
| `bd dep add <from> <to>` | Add dependency | `bd dep add PROJ-43 PROJ-42` (43 depends on 42) |
| `bd comments <id>` | View/add comments | `bd comments PROJ-42 --add "Fixed in commit abc123"` |
| `bd search "query"` | Search by text | `bd search "rate limiting"` |
| `bd sync` | Sync with git remote | `bd sync` at session end |
| `bd stats` | Project statistics | Progress overview |
| `bd epic` | Epic management | Group related issues |
| `bd label` | Manage issue labels | Create/assign labels |
| `bd blocked` | Show blocked issues | Find dependency bottlenecks |
| `bd compact` | Compact old closed issues | Reduce storage with semantic summaries |
| `bd restore <id>` | Restore full history of compacted issue from git | `bd restore PROJ-42` |
| `bd export` / `bd import` | JSONL export/import | Backup or migrate issues |
| `bd audit` | Log and label agent interactions | Append-only JSONL audit trail |
| `bd daemon` | Manage background sync daemon | Automatic syncing |
| `bd rename-prefix` | Rename issue prefix for all issues | Migration |
| `bd workflow` | Show AI-supervised issue workflow guide | Process reference |
| `bd version` | Check beads and plugin versions | Compatibility check |

### Beads Workflow

```
bd create "Feature X" -t task -p 1       → create
bd dep add FEAT-X AUTH-REWRITE            → set dependency
bd ready                                   → find unblocked work
bd update FEAT-X --status in-progress     → start work
bd comments FEAT-X --add "WIP: schema done" → track progress
bd close FEAT-X                            → complete
bd sync                                    → push to remote
```

---

## 8. PRD Taskmaster

| Step | What happens |
|------|-------------|
| `/prd-taskmaster` | Triggers 12-step workflow |
| 1. Discovery | 5 core questions about the product |
| 2. PRD Generation | Comprehensive technical PRD |
| 3. Validation | 13 automated checks (completeness, consistency, testability) |
| 4. Task Breakdown | Auto-generates tasks from PRD sections |
| 5. Execution | 4 modes: Sequential, Parallel, Full Autonomous, Manual |

### Companion Skills

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/expand-tasks` | Reads `tasks.json`, launches parallel Perplexity research agents per task, writes findings back into each task | After PRD parsed into tasks, **before** implementation starts. Avoids researching the same thing 5 times during execution |

### Execution Modes

```
Sequential  → one task at a time, user approves each
Parallel    → independent tasks run concurrently
Autonomous  → full auto with datetime tracking + rollback
Manual      → generates task list, user executes
```

---

## 9. UI/UX Pro Max

Design intelligence with searchable databases.

| Skill | What it does | Key capability |
|-------|-------------|----------------|
| `/ui-ux-pro-max` | Master skill: 50+ styles, 161 palettes, 57 font pairings, 99 UX guidelines | 10 stacks: React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui, HTML/CSS |
| `/design` | Unified design: brand + tokens + UI + logo + CIP + slides + banners + icons | Routes to sub-skills automatically. Logo (55 styles), icons (15 styles, SVG), social photos |
| `/brand` | Brand identity, voice, messaging, asset management | Brand consistency, tone of voice, marketing assets, style guides |
| `/design-system` | 3-layer tokens (primitive/semantic/component), CSS vars, Tailwind | `generate-tokens.cjs`, `validate-tokens.cjs`, strategic slide creation |
| `/ui-styling` | shadcn/ui + Tailwind, dark mode, accessibility, responsive | Radix UI primitives, canvas-based visual designs |
| `/slides` | HTML presentations with Chart.js, design tokens, copywriting formulas | Strategic slides with data visualization, responsive layouts |
| `/banner-design` | 22 art direction styles across social/ads/web/print | 5-step: requirements → research → HTML/CSS → export → present |

---

## 10. Browser Use

Browser automation suite for web testing, scraping, and interaction.

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/browser-use` | Automate browser interactions: navigate, click, fill forms, screenshot, extract data | Direct browser automation from CLI. Testing, form filling, data extraction |
| `/cloud` | Browser Use Cloud API/SDK reference. REST API (v2/v3), Python/TypeScript SDK | Hosted browser automation. Stealth browsers, residential proxies, CAPTCHA handling, webhooks |
| `/open-source` | Browser-use open-source Python library docs. Agent, Browser, Tools config | Writing Python code with `browser_use`. Custom tools, lifecycle hooks, MCP server setup |
| `/remote-browser` | Control local browser from sandboxed remote machine via tunnel | Agent running in sandbox (no GUI) needs to navigate websites or test local dev servers |

### Browser Use Decision Tree

```
Need to automate a browser directly?
  └─ From CLI/Claude Code → /browser-use
  └─ From Python code → /open-source
  └─ Need hosted/cloud infrastructure → /cloud
  └─ Running in sandbox, no GUI → /remote-browser
```

---

## 11. Document & Office

File creation and manipulation for common office formats.

| Skill | What it does | Formats | Mini use case |
|-------|-------------|---------|---------------|
| `/pdf` | Read, merge, split, rotate, watermark, encrypt, OCR, fill forms | .pdf | `/pdf` → merge 3 PDFs → add watermark → encrypt with password |
| `/make-pdf` | Turn any markdown file into publication-quality PDF. Proper 1in margins, intelligent layout | .md → .pdf | `/make-pdf report.md` → produces typeset PDF with proper margins and pagination |
| `/docx` | Create, read, edit Word documents. TOC, headings, page numbers, letterheads | .docx | `/docx` → create report with TOC + tables + letterhead → output .docx |
| `/pptx` | Create, read, edit PowerPoint presentations. Templates, speaker notes, comments | .pptx | `/pptx` → create pitch deck from outline → apply template → add speaker notes |
| `/xlsx` | Create, read, edit spreadsheets. Formulas, formatting, charting, data cleaning | .xlsx, .xlsm, .csv, .tsv | `/xlsx` → import CSV → clean data → add formulas → create chart → output .xlsx |
| `/doc-coauthoring` | Structured workflow for co-authoring documentation with iteration | Any doc type | `/doc-coauthoring` → transfer context → refine through iteration → verify for readers |

---

## 12. Creative & Design

Visual design, art generation, and creative content tools.

| Skill | What it does | Output | Mini use case |
|-------|-------------|--------|---------------|
| `/frontend-design` | Production-grade frontend interfaces with high design quality | HTML/CSS/React | `/frontend-design` → distinctive landing page → avoids generic AI aesthetics → polished code |
| `/canvas-design` | Visual art using design philosophy | .png, .pdf | `/canvas-design` → create event poster → original visual design → export PNG + PDF |
| `/algorithmic-art` | Generative art with p5.js, seeded randomness, interactive parameters | p5.js sketch | `/algorithmic-art` → flow field with particles → interactive controls → seeded for reproducibility |
| `/slack-gif-creator` | Animated GIFs optimized for Slack constraints | .gif | `/slack-gif-creator` → "celebration confetti" → validates Slack size limits → outputs optimized GIF |
| `/theme-factory` | Style artifacts with 10 preset themes or generate custom | Themed artifacts | `/theme-factory` → apply "Corporate Blue" theme to slide deck → consistent colors/fonts throughout |
| `/web-artifacts-builder` | Multi-component claude.ai HTML artifacts with React, Tailwind, shadcn/ui | HTML artifacts | Complex artifacts with state management, routing, shadcn/ui components |

---

## 13. Developer Utilities

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/mcp-builder` | Guide for creating MCP servers (Python FastMCP or Node/TypeScript SDK) | Building MCP servers to integrate external APIs or services |
| `/skill-creator` | Create, modify, measure, and optimize skills | Creating new skills, editing existing ones, running evals, benchmarking |
| `/webapp-testing` | Playwright toolkit for testing local web apps. Screenshots, browser logs | Verifying frontend functionality, debugging UI behavior |
| `/brand-guidelines` | Apply Anthropic's official brand colors and typography | Any artifact that needs Anthropic's look-and-feel |
| `/internal-comms` | Write internal communications using company formats | Status reports, leadership updates, FAQs, incident reports, project updates |
| `/claude-api` | Build, debug, and optimize Claude API / Anthropic SDK apps. Includes prompt caching, model migration (4.5→4.6→4.7), Managed Agents (server-side stateful agents), adaptive thinking, `effort` parameter | Code imports `anthropic`/`@anthropic-ai/sdk`; using Claude API, Anthropic SDKs, or Managed Agents; migrating between model versions |
| `/remotion-best-practices` | Best practices for Remotion — video creation in React | Building programmatic videos, motion graphics with React |
| `/template-skill` | Template for creating new skills (starting point) | Creating a brand new skill from scratch |
| `/forensics` | **UI/UX Forensics & Replication Blueprint** — multi-agent crawl, dissect, and reverse-engineer of a *target site/product*. Outputs `FORENSIC-DOSSIER.md` + design system spec + replication blueprint. *Not* the GSD post-mortem — for that, see [`/gsd:forensics` in §2](#2-gsd--get-shit-done-framework) | Site/product you want to teardown deeply | `/forensics https://stripe.com` → crawls → extracts design system + UX patterns + product logic → forensic atlas + replication blueprint |

---

## 14. Superpowers

Core development methodology skills. Most activate automatically.

| Skill | What it does | When it activates |
|-------|-------------|-------------------|
| `using-superpowers` | Entry skill: mandates skill invocation before any response | Every conversation start |
| `brainstorming` | 9-step collaborative design dialogue | Before creative work — features, components |
| `writing-plans` | Comprehensive plans with bite-sized tasks (2-5 min each) | When you have a spec, before coding |
| `executing-plans` | Load plan → review → execute with checkpoints | Implementing a plan in a new session |
| `subagent-driven-development` | One subagent per task, two-stage review | Executing plans with independent tasks |
| `test-driven-development` | Strict TDD: failing test → minimal code → refactor | Always before writing implementation |
| `systematic-debugging` | 4-phase: Root Cause → Pattern → Hypothesis → Fix | Any bug or test failure |
| `dispatching-parallel-agents` | One agent per independent domain | 2+ tasks sharing no state |
| `using-git-worktrees` | Isolated worktrees with safety verification | Feature work needing isolation |
| `finishing-a-development-branch` | 4 options: merge/PR/keep/discard + cleanup | Implementation complete |
| `requesting-code-review` | Dispatch code-reviewer subagent | After completing tasks |
| `receiving-code-review` | Handle feedback with rigor, push back when wrong | Receiving review feedback |
| `writing-skills` | Create new skills using TDD | Creating/editing skills |
| `verification-before-completion` | Run verification before any success claim | Before claiming work is done |

### Superpowers Flow

```
brainstorming → writing-plans → test-driven-development
    → subagent-driven-development → requesting-code-review
    → verification-before-completion → finishing-a-development-branch
```

---

## 15. Superpowers Lab

Experimental/utility skills.

| Skill | What it does | Mini use case |
|-------|-------------|---------------|
| `slack-messaging` | Send/read Slack via `slackcli` | `slackcli messages send --recipient-id=C123 --message="Deploy complete"` |
| `finding-duplicate-functions` | Semantic duplicate detection in codebases | 5-phase: extract → categorize → split → detect → report. Great for LLM-generated code audit |
| `mcp-cli` | Use MCP servers on-demand via CLI | `mcp tools <server>` → discover → `mcp call <tool> --params '{}' <server>` |
| `using-tmux-for-interactive-commands` | Control interactive CLIs (vim, rebase -i) via tmux | `tmux new-session -d -s edit vim file.txt` → `tmux send-keys` → `tmux capture-pane -p` |

---

## 16. Godmode

37 protocol skills. Key ones below (many overlap with Superpowers but are more prescriptive).

| Skill | What it does | Unique aspect |
|-------|-------------|---------------|
| `activation` | Entry protocol, skill ordering, YoloMode | Mandates skill check before ANY response |
| `intent-discovery` | Structured dialogue → validated spec | More formal than brainstorming |
| `specification-first` | Behavior specs: inputs, outputs, constraints, edge cases | Must precede implementation |
| `task-planning` | Bite-sized tasks with exact paths and complete code | More granular than writing-plans |
| `delegated-execution` | Subagent per task, two-stage review | Same as subagent-driven-development |
| `test-first` | Strict TDD, deletes pre-test code | Stricter than TDD superpowers |
| `fault-diagnosis` | 4-phase debugging, 3+ fails = question architecture | Adds escalation protocol |
| `quality-gate` | Code review subagent, no landing without review | Mandatory gate |
| `system-design` | Architecture selection: defaults to Postgres/REST/Monolith | Opinionated defaults |
| `codebase-research` | Search existing code before writing new code | Mandatory before new features |
| `ui-engineering` | Component architecture, Grid vs Flex, a11y, animation | Comprehensive frontend protocol |
| `parallel-execution` | One agent per isolated domain | Same as dispatching-parallel-agents |
| `project-bootstrap` | Proper project init: linting, testing, CI/CD, VCS | New project setup |
| `error-recovery` | Tracks failed attempts, escalates at thresholds | Auto-activates on stuck patterns |
| `security-protocol` | OWASP, STRIDE, secrets scanning | Lighter than /cso |
| `merge-protocol` | Branch completion: verify → 4 options → cleanup | Same as finishing-a-dev-branch |

---

## 17. Apple Platform

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/apple-dissect` | Ingest + inventory any iOS/macOS/visionOS/tvOS/watchOS build artifact (.ipa / .app / .xcarchive / .xcodeproj / .xcworkspace / .xcresult / .swiftpm / raw source). Emits normalized manifest, source map, dependency graph, asset inventory, symbol map, behavior summary, signing report. Read-only — never executes the artifact. | Whenever an Apple build or codebase lands and you need to understand what it is. Foundation for Sequences AJ / AK / AL. |
| `/rshankras-claude-code-apple-skills-liquid-glass` | Implement Liquid Glass design using `.glassEffect()` API | iOS/macOS 26+ UI effects. Modern glass-based interfaces |

> **Which Apple sequence do I run?** AJ (Apple Ingest & Map) is the always-first chain when a build arrives. AK (Apple Inquisitor) follows AJ when you need maximally deep, inquisitive `/investigate` coverage. AL (Apple Loom) follows AJ (and ideally AK) when you want to extract reusable kits — UI kit, business kernel, API client, asset pack, schema pack — into standalone Swift Packages.

---

## 18. Claude Code Configuration

Harness-level configuration, scheduling, and automation.

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/update-config` | Configure Claude Code harness via settings.json. Set up hooks for automated behaviors ("from now on when X", "each time X", "whenever X", "before/after X") | settings.json hooks | `/update-config` → "Run linter before every commit" → creates pre-commit hook in settings.json |
| `/keybindings-help` | Customize keyboard shortcuts, rebind keys, add chord bindings, modify ~/.claude/keybindings.json | rebind, chord | `/keybindings-help` → "rebind ctrl+s" → updates keybindings.json |
| `/loop` | Run a prompt or slash command on a recurring interval. Self-paces when interval omitted | `/loop 5m /foo`, self-paced | `/loop 5m /qa-only https://app.com` → runs QA every 5 minutes → reports changes |
| `/schedule` | Create, update, list, or run scheduled remote agents (triggers) on a cron schedule | create, list, run, delete | `/schedule create "daily security" --cron "0 9 * * *" --prompt "/cso"` → runs CSO audit every morning |
| `/btw` | 60-minute autonomous run mode (5000% autonomous). Creates a plan, executes, verifies, commits. Hard stops only for auth/2FA, strategic decisions, destructive prod ops | Autonomous | `/btw "update the cheatsheet"` → creates AUTONOMOUS-RUN.md plan → executes all tasks → commits clean |

---

## 19. Google Workspace Suite

Full GWS integration for managing Gmail, Calendar, Drive, Docs, Sheets, Slides, Chat, Meet, Tasks, Keep, Classroom, Forms, People, and Apps Script.

### Core Services

| Command | What it does | Mini use case |
|---------|-------------|---------------|
| `/gws-gmail` | Gmail: Send, read, and manage email | Full email management |
| `/gws-gmail-send` | Gmail: Send an email | `/gws-gmail-send` → compose and send email |
| `/gws-gmail-read` | Gmail: Read a message and extract body or headers | `/gws-gmail-read` → extract message content |
| `/gws-gmail-reply` | Gmail: Reply to a message (handles threading) | Reply in thread automatically |
| `/gws-gmail-reply-all` | Gmail: Reply-all to a message | Reply to all recipients |
| `/gws-gmail-forward` | Gmail: Forward a message to new recipients | Forward email to someone |
| `/gws-gmail-triage` | Gmail: Show unread inbox summary (sender, subject, date) | `/gws-gmail-triage` → inbox overview |
| `/gws-gmail-watch` | Gmail: Watch for new emails and stream as NDJSON | Real-time email monitoring |
| `/gws-calendar` | Google Calendar: Manage calendars and events | Full calendar management |
| `/gws-calendar-agenda` | Google Calendar: Show upcoming events across all calendars | `/gws-calendar-agenda` → today's schedule |
| `/gws-calendar-insert` | Google Calendar: Create a new event | Schedule a meeting |
| `/gws-chat` | Google Chat: Manage Chat spaces and messages | Full chat management |
| `/gws-chat-send` | Google Chat: Send a message to a space | Post to a Chat space |
| `/gws-docs` | Read and write Google Docs | Full Docs management |
| `/gws-docs-write` | Google Docs: Append text to a document | Add content to a doc |
| `/gws-drive` | Google Drive: Manage files, folders, shared drives | Full Drive management |
| `/gws-drive-upload` | Google Drive: Upload a file with automatic metadata | Upload a file to Drive |
| `/gws-sheets` | Google Sheets: Read and write spreadsheets | Full Sheets management |
| `/gws-sheets-read` | Google Sheets: Read values from a spreadsheet | Read spreadsheet data |
| `/gws-sheets-append` | Google Sheets: Append a row to a spreadsheet | Add data to a sheet |
| `/gws-slides` | Google Slides: Read and write presentations | Full Slides management |
| `/gws-forms` | Read and write Google Forms | Manage forms |
| `/gws-meet` | Manage Google Meet conferences | Meeting management |
| `/gws-tasks` | Google Tasks: Manage task lists and tasks | Task management |
| `/gws-keep` | Manage Google Keep notes | Notes management |
| `/gws-people` | Google People: Manage contacts and profiles | Contact management |
| `/gws-classroom` | Google Classroom: Manage classes, rosters, coursework | Classroom management |
| `/gws-script` | Manage Google Apps Script projects | Apps Script management |
| `/gws-script-push` | Google Apps Script: Upload local files to a project | Push code to Apps Script |

### Events & Admin

| Command | What it does | Mini use case |
|---------|-------------|---------------|
| `/gws-events` | Subscribe to Google Workspace events | Event subscriptions |
| `/gws-events-subscribe` | Subscribe to events and stream as NDJSON | Real-time event streaming |
| `/gws-events-renew` | Renew/reactivate event subscriptions | Keep subscriptions alive |
| `/gws-admin-reports` | Admin SDK: Audit logs and usage reports | Admin audit and reporting |
| `/gws-shared` | Shared patterns: authentication, global flags, output formatting | Base patterns for all gws commands |

### Model Armor (Security)

| Command | What it does | Mini use case |
|---------|-------------|---------------|
| `/gws-modelarmor` | Google Model Armor: Filter user-generated content for safety | Content safety filtering |
| `/gws-modelarmor-create-template` | Create a new Model Armor template | Set up safety template |
| `/gws-modelarmor-sanitize-prompt` | Sanitize a user prompt through a template | Filter incoming prompts |
| `/gws-modelarmor-sanitize-response` | Sanitize a model response through a template | Filter outgoing responses |

### Cross-Service Workflows

| Command | What it does | Mini use case |
|---------|-------------|---------------|
| `/gws-workflow` | Cross-service productivity workflows | Multi-service automation |
| `/gws-workflow-email-to-task` | Convert Gmail message into Google Tasks entry | Email → task conversion |
| `/gws-workflow-file-announce` | Announce a Drive file in a Chat space | Share file to Chat |
| `/gws-workflow-meeting-prep` | Prepare for next meeting: agenda, attendees, linked docs | Pre-meeting briefing |
| `/gws-workflow-standup-report` | Today's meetings + open tasks as standup summary | Morning standup |
| `/gws-workflow-weekly-digest` | Weekly summary: meetings + unread email count | End-of-week digest |

---

## 20. Google Workspace Recipes

Pre-built automations combining multiple Google services. Each recipe is a single command that orchestrates a multi-step workflow.

### Email & Communication

| Recipe | What it does |
|--------|-------------|
| `/recipe-send-team-announcement` | Send announcement via Gmail + Google Chat |
| `/recipe-draft-email-from-doc` | Read a Google Doc → compose as Gmail message |
| `/recipe-email-drive-link` | Share Drive file + email the link |
| `/recipe-forward-labeled-emails` | Find labeled Gmail → forward to address |
| `/recipe-label-and-archive-emails` | Apply labels to matching messages → archive |
| `/recipe-create-gmail-filter` | Create auto-label/star/categorize filter |
| `/recipe-create-vacation-responder` | Enable out-of-office auto-reply with dates |
| `/recipe-save-email-attachments` | Find attachments → save to Drive folder |
| `/recipe-save-email-to-doc` | Save Gmail body into Google Doc |

### Calendar & Scheduling

| Recipe | What it does |
|--------|-------------|
| `/recipe-create-events-from-sheet` | Read Sheets rows → create Calendar events |
| `/recipe-schedule-recurring-event` | Create recurring Calendar event with attendees |
| `/recipe-reschedule-meeting` | Move event to new time → notify attendees |
| `/recipe-batch-invite-to-event` | Add attendee list to existing event |
| `/recipe-block-focus-time` | Create recurring focus-time blocks |
| `/recipe-find-free-time` | Query free/busy for multiple users → find slot |
| `/recipe-plan-weekly-schedule` | Review calendar week → identify gaps → fill |
| `/recipe-share-event-materials` | Share Drive files with all event attendees |
| `/recipe-review-meet-participants` | Check who attended a Meet and for how long |

### Drive & Documents

| Recipe | What it does |
|--------|-------------|
| `/recipe-create-doc-from-template` | Copy Docs template → fill content → share |
| `/recipe-share-doc-and-notify` | Share Doc with edit access → email collaborators |
| `/recipe-organize-drive-folder` | Create folder structure → move files |
| `/recipe-create-shared-drive` | Create Shared Drive → add members with roles |
| `/recipe-bulk-download-folder` | List + download all files from Drive folder |
| `/recipe-find-large-files` | Find large files consuming storage quota |
| `/recipe-share-folder-with-team` | Share folder + contents with collaborators |
| `/recipe-watch-drive-changes` | Subscribe to change notifications on file/folder |

### Sheets & Data

| Recipe | What it does |
|--------|-------------|
| `/recipe-create-expense-tracker` | Set up expense-tracking sheet with headers + entries |
| `/recipe-generate-report-from-sheet` | Read Sheet data → create formatted Docs report |
| `/recipe-backup-sheet-as-csv` | Export spreadsheet as CSV for local backup |
| `/recipe-compare-sheet-tabs` | Read two tabs → compare and find differences |
| `/recipe-copy-sheet-for-new-month` | Duplicate template tab for new month |
| `/recipe-log-deal-update` | Append deal status update to sales tracking sheet |
| `/recipe-sync-contacts-to-sheet` | Export Google Contacts to Sheets spreadsheet |

### Other Services

| Recipe | What it does |
|--------|-------------|
| `/recipe-create-feedback-form` | Create Forms feedback form → share via Gmail |
| `/recipe-collect-form-responses` | Retrieve and review Forms responses |
| `/recipe-create-classroom-course` | Create Classroom course → invite students |
| `/recipe-create-meet-space` | Create Meet space → share join link |
| `/recipe-create-task-list` | Set up Tasks list with initial tasks |
| `/recipe-review-overdue-tasks` | Find past-due Tasks needing attention |
| `/recipe-post-mortem-setup` | Create Docs post-mortem → schedule Calendar review → notify via Chat |
| `/recipe-create-presentation` | Create new Slides presentation with initial slides |

---

## 21. Google Workspace Personas

Role-based configurations that optimize Google Workspace tool usage for specific job functions.

| Persona | Role | Key capabilities |
|---------|------|-----------------|
| `/persona-exec-assistant` | Executive Assistant | Manage schedule, inbox, and communications |
| `/persona-project-manager` | Project Manager | Track tasks, schedule meetings, share docs |
| `/persona-team-lead` | Team Lead | Run standups, coordinate tasks, communicate |
| `/persona-content-creator` | Content Creator | Create, organize, distribute content |
| `/persona-customer-support` | Customer Support | Track tickets, respond, escalate issues |
| `/persona-event-coordinator` | Event Coordinator | Plan events: scheduling, invitations, logistics |
| `/persona-hr-coordinator` | HR Coordinator | Onboarding, announcements, employee comms |
| `/persona-it-admin` | IT Admin | Monitor security, configure Workspace |
| `/persona-researcher` | Researcher | Manage references, notes, collaboration |
| `/persona-sales-ops` | Sales Ops | Track deals, schedule calls, client comms |

---

## 22. Video & Motion

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/remotion-best-practices` | Best practices for Remotion — video creation in React | Building programmatic videos with React + Remotion |
| `/motion-stack-guide` | Project motion system context: Framer Motion / GSAP / Lenis stack, 7 patterns, standard easing values, anti-pattern table | Load at start of any animation session to enforce consistent motion language. Say the *feeling*, Claude handles implementation |

### Motion Stack Quick Reference

```
Standard ease:   [0.22, 1, 0.36, 1]     (soft deceleration)
Y offset max:    16–32px                  (never sideways)
Stagger gap:     0.12s per item
Viewport margin: "-15%" to "-20%"

Pattern catalog:
  1. Hero entrance sequence     → staggered fade-up on page load
  2. Scroll reveals             → whileInView, once: true, 0.8–1.0s
  3. Line / divider reveals     → scaleY from 0→1, transform-origin: top
  4. Image reveals (clip-path)  → inset(20%)→inset(0%), 1.4s
  5. Parallax                   → y 0%→12%, scale 1→1.05
  6. Staggered lists            → i * 0.12s delay, whileInView once
  7. Opacity-only reveals       → labels/metadata, target 0.4–0.7 opacity
```

---

## 23. Codex Plugin

OpenAI Codex CLI integration — second-opinion review, autonomous rescue, and shared runtime handoff.

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/codex:setup` | Check whether the local Codex CLI is ready and optionally toggle the stop-time mode | One-time setup / health check | `/codex:setup` → verifies Codex CLI installed → toggles stop-time mode if requested |
| `/codex:rescue` | Delegate investigation, an explicit fix request, or follow-up rescue work to Codex through the shared runtime | Stuck on a bug, want an independent pass, or need a deeper RCA | `/codex:rescue` → hands current task to Codex → returns diagnosis + proposed fix |

> Internal-only helpers (not user-invoked): `codex:gpt-5-4-prompting`, `codex:codex-result-handling`, `codex:codex-cli-runtime`. Used by Codex agents themselves.

---

## 24. Context7 Plugin

Live, version-aware documentation lookup for any library, framework, SDK, API, CLI tool, or cloud service.

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/context7-plugin:docs` | Look up documentation for any library | "How do I use X in Next.js 15?" → fetches current docs (avoids stale training data) |
| `/context7-plugin:context7-mcp` | MCP-server entry point for context7 — wraps `resolve-library-id` and `query-docs` | When using context7 as an MCP server inside another agent flow |

> Use Context7 over web search for library docs. Do **not** use for refactoring, debugging business logic, or general programming concepts.

---

## 25. claude-mem — Memory & Planning

Persistent cross-session memory, code intelligence, and phased planning for Claude Code. Plugin by thedotmack (v12.4.9).

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/claude-mem:mem-search` | Search persistent cross-session memory DB for past decisions, solutions, and context | "Did we solve this before?" → searches observations across all sessions |
| `/claude-mem:smart-explore` | Token-optimized structural code search using tree-sitter AST parsing | Understanding a codebase deeply without blowing context window |
| `/claude-mem:make-plan` | Create detailed phased implementation plan with file paths and acceptance criteria | Before `/claude-mem:do` — scope out the work first |
| `/claude-mem:do` | Execute a phased plan using parallel subagents | After `/claude-mem:make-plan` — runs each phase with dedicated agents |
| `/claude-mem:knowledge-agent` | Build and query AI knowledge bases from claude-mem observations | Team knowledge base, decision logs, runbooks |
| `/claude-mem:pathfinder` | Map codebase into feature-grouped flowcharts, identify duplicated concerns, propose unified architecture | Architecture review, deduplication planning |
| `/claude-mem:timeline-report` | Generate "Journey Into [Project]" narrative from claude-mem timeline observations | Onboarding new team members, project post-mortems |
| `/claude-mem:version-bump` | Automated semantic versioning + release workflow for Claude Code plugins | Releasing plugin updates: bump version, update changelog, tag |

> Plugin version: **12.7.2** (thedotmack)

### claude-mem Flow

```
/claude-mem:mem-search         → check memory for past context
/claude-mem:smart-explore      → understand codebase structure
/claude-mem:make-plan          → create phased plan
/claude-mem:do                 → execute plan with subagents
/claude-mem:version-bump       → release plugin update
```

---

## 26. Native Claude Code Commands

Built-in slash commands that ship with the `claude` CLI binary itself (verified against v2.1.150). These resolve **before** plugins/skills with the same name — but installed plugins can override common names like `/review`, `/init`. When in doubt, check `/skills` for what's overriding.

> **Override note:** This user has `gstack` installed which ships its own `/review` (visual + diff QA) — that overrides the native `/review` (pull-request review). Use `claude --bare` or disable gstack to invoke the native one.

### Session Control

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/help` | Show help and available commands | Any time |
| `/clear` | Start a new session with empty context; previous stays on disk (resumable via `/resume`) | Context is polluted but you might want it back later |
| `/compact` | Free up context by summarizing the conversation so far | Context approaching limit, want to continue thread |
| `/autocompact` | Configure the auto-compact window size | Tune when CC auto-summarizes |
| `/context` | Visualize current context usage as a colored grid | "Why am I out of context?" — see what's eating it |
| `/resume` | Resume a previous conversation | Pick up where you left off |
| `/fork` | Spawn a background agent that inherits the full conversation | Branch the conversation without losing the main thread |
| `/teleport` | Resume a Claude Code session from claude.ai | Continue a web session in the terminal |
| `/stop` | Stop this background session; transcript + worktree are kept | End a `/fork` or background run cleanly |
| `/recap` | Generate a one-line session recap now | Quick status snapshot |
| `/insights` | Generate a report analyzing your Claude Code sessions | Usage analytics across sessions |
| `/export` | Export the current conversation to a file or clipboard | Save the transcript |
| `/copy` | Copy Claude's last response to clipboard (`/copy N` for Nth-latest) | Pipe an output into the OS clipboard |
| `/status` | Show CC status — version, model, account, API connectivity, tool statuses | Health check |
| `/version` | Print the version this session is running | Confirm exact build |
| `/update` | Switch to the latest version (conversation continues) | Hot-upgrade mid-session |

### Model & Effort

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/model` | Set the AI model for the session | Switch Opus ↔ Sonnet ↔ Haiku. Alias `opus` → `claude-opus-4-7`, `sonnet` → `claude-sonnet-4-6`, `haiku` → `claude-haiku-4-5` |
| `/effort` | Set effort level: `low \| medium \| high \| xhigh \| max \| auto`. `xhigh` added in Opus 4.7 (best for coding/agentic). `max` is Opus-only | Tune thinking depth vs speed/cost |
| `/fast` | Toggle Fast mode (Opus only) | Opus output speed-up |

> **Current Claude 4.x model family (2026-05-26):**
> | Model | ID | Context | Input | Output |
> |-------|----|---------|-------|--------|
> | Claude Opus 4.7 | `claude-opus-4-7` | 1M | $5/Mtok | $25/Mtok |
> | Claude Opus 4.6 | `claude-opus-4-6` | 1M | $5/Mtok | $25/Mtok |
> | Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M | $3/Mtok | $15/Mtok |
> | Claude Haiku 4.5 | `claude-haiku-4-5` | 200K | $1/Mtok | $5/Mtok |
>
> **Thinking:** Use `thinking: {type: "adaptive"}` on Opus 4.6/4.7 and Sonnet 4.6. `budget_tokens` is deprecated on 4.6/4.7. Opus 4.7 also removes temperature/top_p sampling params.
> **Effort:** `output_config: {effort: "xhigh"}` (Opus 4.7 default in CC), `"max"` for Opus-only max intelligence, `"high"` for most cases.
> **Managed Agents:** server-side stateful agents with Anthropic-hosted tool execution — see `/claude-api` (§13).
| `/brief` | Toggle brief-only mode | Shorter responses |
| `/voice` | Toggle voice mode | Hands-free input |
| `/focus` | Toggle focus view (show only prompt, tool summary, final response) | Hide tool-by-tool noise |
| `/theme` | Change the theme | Terminal aesthetics |
| `/color` | Set the prompt bar color for this session | Visual session identification |
| `/tui` | Set terminal UI renderer (`default` or `fullscreen`) | TUI mode toggle |
| `/scroll-speed` | Adjust mouse wheel scroll speed | TUI tuning |
| `/keybindings` | Open or create your keybindings configuration file | Customize chord/key bindings |

### Project Bootstrap

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/init` | Initialize a new CLAUDE.md file with codebase documentation (env-gated: `CLAUDE_CODE_NEW_INIT=1` enables multi-file CLAUDE.md + skills/hooks scaffold) | New repo onboarding |
| `/init-verifiers` | Create verifier skill(s) for automated verification of code changes | After /init, add per-area verifiers |
| `/agents` | Manage agent configurations | Add/edit/list custom subagents |
| `/skills` | List available skills | See what's installed |
| `/mcp` | Manage MCP servers | Add/remove/inspect MCP servers |
| `/hooks` | View hook configurations for tool events | Audit hook surface |
| `/reload-plugins` | Activate pending plugin changes in the current session | Just installed a plugin, don't want to restart |
| `/memory` | Edit Claude memory files (CLAUDE.md, etc.) | Quick in-session memory edit |
| `/toggle-memory` | Toggle automemory off/on for this session | Pause auto-capture |
| `/add-dir` | Add a new working directory | Cross-repo work without restarting CC |
| `/ide` | Manage IDE integrations and show status | VS Code / JetBrains hooks |

### Git / PR Workflow

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/commit` | Create a git commit | Stage + commit in one step |
| `/commit-push-pr` | Commit, push, and open a PR | Land work in one chain |
| `/review` | Review a pull request (native — gstack `/review` overrides it if installed) | Pre-merge code review |
| `/security-review` | Complete a security review of the pending changes on the current branch | Before landing security-sensitive changes |
| `/autofix-pr` | Monitor and autofix any issues with the current PR | CI feedback loop on a live PR |
| `/diff` | View uncommitted changes and per-turn diffs | Inspect what changed this turn |
| `/simplify` | Review changed code for reuse, quality, efficiency, then fix issues | Post-implementation polish |
| `/batch` | Research and plan a large-scale change, then execute in parallel across 5–30 isolated worktree agents that each open a PR | Fanout refactor across many files/repos |

### Automation & Scheduling

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/plan` | Enable plan mode or view the current session plan | Discuss before coding |
| `/loops` | List, create, and delete recurring loops and stop-hooks | Cron-style recurring runs |
| `/daemon` | Manage background services: assistants, scheduled tasks, remote control | Background agent lifecycle |
| `/goal` | Set a goal — keep working until the condition is met | Goal-directed autonomous run |
| `/btw` | Ask a quick side question without interrupting the main conversation | Aside that doesn't dirty main context |
| `/advisor` | Configure the Advisor Tool to consult a stronger model at key moments | Auto-escalate hard subproblems |
| `/fewer-permission-prompts` | Scan transcripts and add an allowlist to `.claude/settings.json` | Reduce friction after first dirty session |
| `/debug` | Enable debug logging for this session | Diagnose CC misbehavior |
| `/doctor` | Diagnose and verify Claude Code installation and settings | Something seems broken |
| `/feedback` | Submit feedback about Claude Code | File a comment to Anthropic |

### Account / Setup / Distribution

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/login` | Sign in (or switch Anthropic accounts) | First-run or account swap |
| `/logout` | Sign out from your Anthropic account | Hand over the machine |
| `/usage` (aliases: `/cost`, `/stats`) | Show session cost, plan usage, and activity | Spend awareness |
| `/upgrade` | Upgrade to Max for higher rate limits and more Opus | Hit a limit |
| `/extra-usage` | Configure extra usage to keep working when limits are hit | Pay-as-you-go bridge |
| `/privacy-settings` | View and update your privacy settings | Telemetry/data controls |
| `/install` | Install Claude Code native build | First-time install |
| `/install-github-app` | Set up Claude GitHub Actions for a repository | Wire CC into a repo's CI |
| `/install-slack-app` | Install the Claude Slack app | Bring CC into Slack |
| `/setup-bedrock` | Reconfigure Amazon Bedrock authentication, region, or model pins | AWS-hosted models |
| `/setup-vertex` | Reconfigure Google Vertex AI authentication, project, region, or model pins | GCP-hosted models |
| `/remote-env` | Configure the default remote environment for teleport sessions | Cloud workspace defaults |
| `/web-setup` | Set up Claude Code on the web (requires connecting your GitHub account) | claude.ai/code wiring |
| `/team-onboarding` | Help teammates ramp on Claude Code with a guide from your usage | New-hire onboarding |
| `/powerup` | Discover Claude Code features through quick interactive lessons | Self-guided tour |
| `/stickers` | Order Claude Code stickers | Free swag |
| `/radio` | Listen to Claude FM lo-fi radio | Background music |

### Browser Integration (beta)

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/chrome` | Claude in Chrome (beta) settings | Wire CC into Chrome session |
| `/alias` | Create or list command aliases | Shorthand for frequent chains |

> **Total native commands (v2.1.150):** ~77 surface-level. Many are situational (account/setup) — the day-to-day are `/clear /compact /context /resume /model /effort /memory /agents /mcp /hooks /commit /diff /plan /goal /btw`.

> **Provenance gotcha:** When a plugin defines a command with the same name as a native one, the plugin wins. To force the native: `claude --bare` (skips plugins) or disable the shadowing plugin in settings.

---

## 27. Workflow Sequences

### A. New Project (Full Ceremony)

```
/office-hours                          → validate the idea
/gsd:new-project                       → init PROJECT.md + ROADMAP.md
/gsd:settings                          → configure agents
/gsd:map-codebase                      → (brownfield only) understand existing code

Per phase:
  /gsd:discuss-phase N                 → gather context
  /gsd:plan-phase N                    → create PLAN.md
  /gsd:execute-phase N                 → implement
  /gsd:verify-work N                   → UAT
  /gsd:add-tests N                     → test coverage

/gsd:audit-milestone                   → verify completeness
/gsd:complete-milestone v1.0           → archive + tag
/document-release                      → update docs
/retro                                 → retrospective
```

### B. Quick Feature (Minimal Ceremony)

```
/gsd:quick "Add rate limiting to /api/users"    → plan + execute + commit
/review                                          → pre-landing review
/ship                                            → create PR
```

### C. Trivial Fix

```
/gsd:fast "Fix typo in error message"            → inline fix
/ship                                            → create PR
```

### D. Bug Investigation

```
/investigate                           → (gstack) 4-phase root cause
   OR
/gsd:debug "description"              → (GSD) scientific method with persistent state
   OR
/autoresearch:debug                   → autonomous bug-hunting loop (finds ALL bugs)
```

### E. Design-First Frontend

```
/design-consultation                   → create DESIGN.md
/gsd:ui-phase N                        → generate UI-SPEC.md
/gsd:plan-phase N                      → plan implementation
/gsd:execute-phase N                   → build
/gsd:ui-review N                       → 6-pillar visual audit
/design-review https://localhost:3000  → live visual QA + fixes
/qa https://localhost:3000             → functional QA + fixes
```

### F. Full Ship Pipeline

```
/review                → pre-landing review
/ship                  → create PR (tests, CHANGELOG, VERSION bump)
/land-and-deploy       → merge + deploy
/canary --duration 5m  → post-deploy monitoring
/document-release      → update docs
```

### G. Figma → Code → Figma

```
/figma:figma-implement-design          → Figma URL → production code
   ... build the feature ...
/figma:figma-use + /figma:figma-generate-design  → push updates back to Figma
/figma:figma-code-connect-components   → link components
```

### H. Session Management

```
Starting work:   /gsd:resume-work     → restore context
During work:     /gsd:next            → auto-advance
                 /gsd:progress        → situational awareness
Pausing:         /gsd:pause-work      → save state
End of day:      /gsd:session-report  → summary
End of week:     /retro               → retrospective
```

### I. Security Audit

```
/cso                                   → daily or comprehensive audit
/autoresearch:security                 → autonomous STRIDE + OWASP + red-team
/careful                               → enable destructive command warnings
/guard                                 → lock edits + warnings (for prod debugging)
```

### J. Documentation Writing

```
/idme-base:writer                      → RDR (research-first spec)
/idme-base:design-document-writer      → technical design from PRD
/idme-base:adr-writer                  → architectural decision
/idme-base:arb-writer                  → architecture review board
/idme-base:api-council-writer          → API council submission
/doc-coauthoring                       → structured co-authoring workflow
```

### K. Autonomous Iteration

```
/autoresearch:plan                     → define goal + metric
/autoresearch                          → iterate toward goal autonomously
/autoresearch:fix                      → fix all errors iteratively
/autoresearch:ship                     → ship through 8-phase workflow
```

### L. Document & Office Generation

```
/pdf                                   → merge, split, watermark, OCR PDFs
/docx                                  → create/edit Word documents
/pptx                                  → create/edit PowerPoint presentations
/xlsx                                  → create/edit spreadsheets
```

### M. Browser Automation

```
/browse                                → (gstack) headless Chromium, fast QA
/gstack                                → gstack browser primitives
/open-gstack-browser                   → AI-controlled Chromium with sidebar extension
/browser-use                           → direct browser automation
/remote-browser                        → control browser from sandbox via tunnel
/setup-browser-cookies                 → import auth cookies first
```

### N. Google Workspace Daily Workflow

```
/gws-gmail-triage                      → inbox overview
/gws-calendar-agenda                   → today's schedule
/gws-workflow-standup-report           → standup summary
/gws-workflow-meeting-prep             → prep for next meeting
```

### O. Google Workspace Automation

```
/recipe-create-events-from-sheet       → Sheet rows → Calendar events
/recipe-email-drive-link               → share file + email link
/recipe-create-gmail-filter            → auto-label incoming mail
/recipe-post-mortem-setup              → Doc + Calendar + Chat notification
```

### P. Persona-Driven Workspace

```
/persona-exec-assistant                → configure EA mode
/gws-gmail-triage                      → inbox summary
/gws-calendar-agenda                   → day's schedule
/gws-workflow-meeting-prep             → meeting prep
/recipe-reschedule-meeting             → move conflicting meetings
```

### Q. Developer Experience Audit

```
/plan-devex-review                     → plan review for DX dimensions
/devex-review https://docs.myapi.com   → live DX audit with TTHW timing
/design-review https://docs.myapi.com  → visual review of docs site
/qa https://docs.myapi.com             → functional QA
```

### R. Scheduled Automation

```
/schedule create "nightly security" --cron "0 2 * * *" --prompt "/cso"
/schedule create "weekly retro" --cron "0 17 * * 5" --prompt "/retro"
/schedule list                         → view all scheduled agents
/loop 5m /health                       → live health monitoring
```

### S. Cross-AI Second Opinion

```
/codex:setup                           → verify Codex CLI is ready (one-time)
/codex:rescue                          → hand stuck task to Codex via shared runtime
/codex review                          → (gstack) independent diff review
/gsd:review --phase 3 --all            → multi-AI peer review of plans
```

### T. Library Documentation Lookup

```
/context7-plugin:docs <library>        → fetch current API docs (Next.js, Prisma, etc.)
                                          beats web search for library questions
                                          avoid for refactors / business logic / general programming
```

### U. Project Bootstrap & Onboarding

```
/init                                  → (native) create CLAUDE.md from codebase
/setup-gbrain                          → install gbrain CLI + local PGLite memory
/setup-deploy                          → configure deploy platform once
/setup-browser-cookies <domain>        → import auth cookies for QA
/fewer-permission-prompts              → cut permission prompts via allowlist
```

### V. New Skill / MCP Authoring Pipeline

```
/plugin-structure                       → scaffold plugin layout (.claude-plugin/, skills/, agents/, commands/, hooks/, mcp/)
/skill-development                      → bootstrap a SKILL.md with proper frontmatter
/skill-creator                          → interactive scaffold for skill structure + metadata
/build-mcp-server                       → wrap an API as an MCP server
/mcp-integration                        → wire MCP into plugin via .mcp.json
/build-mcpb                             → package MCP server as MCPB bundle
/hook-development                       → add PreToolUse/PostToolUse/Stop hooks
/command-development                    → add custom slash commands
/agent-development                      → add subagent with proper frontmatter
/playground                             → build interactive HTML preview for the plugin
/superpowers:writing-skills             → apply skill-authoring best practices
/superpowers:test-driven-development    → tests-first for skill behavior
/plugin-settings                        → expose user-configurable plugin settings
/review                                 → pre-landing diff review
/ship                                   → PR with CHANGELOG bump
```
> **Why:** spans Plugin Authoring Toolkit (§33) + Superpowers + gstack — turns ad-hoc skill ideas into shipped, tested, reviewed plugin artifacts with full Claude Code surface (skills + commands + agents + hooks + MCP).

### W. Onboarding to an Unknown Codebase (4 memory layers)

```
/init                                   → native CLAUDE.md scaffold
/gsd:map-codebase                       → parallel-agent codebase map (STACK, ARCH, etc.)
/claude-mem:learn-codebase              → persistent vector memory of architecture
/graphify                               → knowledge graph for future Q&A
/sync-gbrain                            → register code surface for gbrain search
/context-save                           → checkpoint loaded context for resume
```
> **Why:** four different memory layers (file, planning docs, vector mem, graph) compound into instant productivity for any future session.

### X. Idea → PRD → Tasks → Autonomous Build

```
/office-hours                           → validate the idea
/prd-taskmaster                         → generate validated PRD + task breakdown
/expand-tasks                           → Perplexity research per task
/superpowers:write-plan                 → lock execution plan
/superpowers:execute-plan               → subagent-driven implementation
/autoresearch:ship                      → 8-phase shipping
```
> **Why:** bridges PRD-Taskmaster + Superpowers + Autoresearch — research, plan, and ship without losing fidelity between stages.

### Y. Plan Hardening Gauntlet

```
/superpowers:write-plan                 → draft plan
/plan-ceo-review                        → product/strategy critique
/plan-design-review                     → designer's-eye critique
/plan-eng-review                        → architecture lock-in
/plan-devex-review                      → DX dimensions
/codex consult                          → adversarial second opinion (cross-AI)
/gsd:review --phase N --all             → multi-AI peer review
/autoplan                               → auto-decide remaining open items
```
> **Why:** maximum-rigor plan review across CEO/design/eng/DX/external AI before a single line of code is written.

### Z. Knowledge Compounding Session

```
/graphify                               → ingest sources into knowledge graph
/claude-mem:knowledge-agent             → persistent memory of findings
/idme-base:writer                       → RDR research-first spec
/idme-base:adr-writer                   → capture architectural decisions
/learn                                  → record gstack learnings
```
> **Why:** turns a research session's findings into queryable graph + vector memory + canonical written artifacts simultaneously.

### AA. Live Site Forensic Replication

> Uses `/forensics` (UI/UX site teardown) — distinct from `/gsd:forensics` (GSD workflow post-mortem).

```
/scrape <url>                           → pull data/structure
/forensics <url>                        → multi-agent UI/UX teardown + replication blueprint
/design-shotgun                         → generate competing variants
/design-html                            → finalize Pretext-native HTML
/design-review http://localhost:3000    → live visual QA + fixes
/skillify                               → codify the scrape into a permanent skill
```
> **Why:** combines Browser-Use + Creative/Design + gstack QA — clone, improve, and codify in one chain.

### AB. Parallel-Worktree Multi-Feature Sprint

```
/superpowers:using-git-worktrees        → spin per-feature worktrees
/gsd:new-workspace                      → register each as a GSD workspace
/superpowers:dispatching-parallel-agents → fan out subagents per worktree
/godmode:parallel-execution             → orchestration discipline
/superpowers:finishing-a-development-branch → land each branch cleanly
/land-and-deploy                        → merge + verify per branch
```
> **Why:** enables true N-way parallel feature development without cross-contamination — Superpowers + Godmode + GSD + gstack.

### AC. Production Incident Response

```
/guard                                  → lock edits + destructive warnings
/careful                                → safety mode for prod
/investigate                            → 4-phase root cause
/superpowers:systematic-debugging       → hypothesis discipline
/cso                                    → security audit if breach suspected
/canary --duration 15m                  → post-fix monitoring
/idme-base:adr-writer                   → record the decision/lesson
```
> **Why:** incident posture (guard/careful) + structured debugging + post-mortem capture — one chain instead of improvising under pressure.

### AD. Autonomous Background Operator (24/7)

```
/schedule create "nightly health" --cron "0 3 * * *" --prompt "/health"
/schedule create "nightly cso"   --cron "0 4 * * *" --prompt "/cso"
/loop 10m /qa-only https://staging.app
/ralph                                  → autonomous dev loop overnight
/autoresearch                           → iterate toward goal in background
/gws-workflow-weekly-digest             → Monday morning summary email
```
> **Why:** stitches scheduled agents + Ralph + Autoresearch + GWS digest into a self-driving engineering operation.

### AE. Visual Asset → Production Component (Figma round-trip)

```
/figma:figma-implement-design           → Figma URL → reference code
/frontend-design                        → adapt to project conventions
/ui-ux-pro-max                          → polish to pro-grade
/design-review http://localhost:3000    → visual audit + fixes
/figma:figma-code-connect               → link component back to Figma
/benchmark                              → perf regression check
```
> **Why:** Figma + UI/UX Pro Max + gstack benchmarks closes the loop from design → production → measured perf with bidirectional Figma sync.

### AF. Meeting → Action → Tracked Work

```
/gws-workflow-meeting-prep              → prep brief
/gws-meet                               → conference notes
/gws-workflow-email-to-task             → emails → Tasks
bd create "commitment" -t task -p 1     → file each commitment as a bead
bd dep add COMMIT-X PROJ-Y              → wire dependencies
bd ready                                → surface unblocked work next session
```
> **Why:** turns Google Workspace meeting outputs into structured Beads tasks with dependencies — meetings stop falling on the floor.

### AG. Compress & Continue Across Context Limits

```
/gsd:session-report                     → summarize current session
/context-save                           → checkpoint git + decisions
/claude-mem:timeline-report             → persistent timeline narrative
/caveman:compress CLAUDE.md             → token-compress memory files
bd compact                              → semantic-summarize old issues
[/clear]                                → flush context window
/context-restore                        → resume in fresh context
```
> **Why:** spans claude-mem + Caveman + Beads + gstack context tools — cleanly hand off a long session into a fresh window without losing state or ballooning tokens.

### AH. Full-Stack Plugin Authoring (Claude Code Plugin Toolkit)

```
/claude-automation-recommender           → scan codebase, recommend which automations to build
/plugin-structure                        → scaffold plugin directory layout
/plugin-settings                         → declare user-configurable plugin settings
/skill-development                       → add SKILL.md(s) with frontmatter
/command-development                     → add slash command(s)
/agent-development                       → add subagent(s)
/hook-development                        → add PreToolUse/PostToolUse/Stop hooks
/writing-hookify-rules                   → write hookify rule syntax for automatic dispatch
/build-mcp-server                        → wrap an API as MCP server
/mcp-integration                         → wire .mcp.json into the plugin
/build-mcpb                              → package as MCPB bundle for distribution
/build-mcp-app                           → add interactive UI/widgets to the MCP
/playground                              → ship an HTML playground demoing the plugin
/example-skill + /example-command        → embed canonical examples for users
/claude-md-improver                      → tighten the bundled CLAUDE.md docs
/review → /ship                          → land + release
```
> **Why:** end-to-end pipeline using the new §33 Plugin Authoring Toolkit. Spans the full Claude Code plugin surface area — skills, commands, agents, hooks, MCP servers, packaging, and docs — without leaving the chat.

### AI. M5Stack ESP32 Device Onboarding

```
/m5-onboard                              → detect device on USB, flash MicroPython firmware, mount filesystem
/cardputer-buddy                         → iterate on the bundled Claude Buddy / Snake / Hello apps
/playground                              → build an HTML playground that mirrors the on-device UI
/learn                                   → record device-specific quirks (boot pins, USB chip, partition table)
```
> **Why:** turns a fresh M5Stack Cardputer / Core / Stick into a Claude-driven embedded device with a working app bundle in a single chain. Uses the new §34 IoT suite.

### AJ. Apple Ingest & Map (iOS / macOS / visionOS / tvOS / watchOS)

```
/gsd:new-workspace                       → register the inbound build dir
/gsd:new-project "Ingest <App>"          → seed PROJECT.md + ROADMAP.md
/gsd:settings                            → enable plan-auditor, code-review-expert, deep-analyst

/apple-dissect <artifact-path>           → normalize .ipa/.app/.xcarchive/.xcodeproj → .apple-dissect/<run-id>/
                                            (manifest.json, source-map.json, dep-graph.json, asset-map.json,
                                             symbol-map.json, signing-report.md)

/gsd:map-codebase                        → parallel-agent map (STACK/ARCH/CONCERNS/QUALITY)
/idme-base:codebase-deep-analyzer        → arch + tech debt sweep

/init                                    → CLAUDE.md scaffold pointed at the dissect run
/claude-mem:learn-codebase               → push summaries into persistent vector memory
/graphify <artifact-root>                → knowledge graph from source + symbol map + dep graph
/sync-gbrain                             → register surface for gbrain semantic search

/idme-base:writer                        → RDR: "What is <App>?"
/idme-base:adr-writer                    → ADR-0001 baseline
/learn                                   → record heuristic surprises

/autoresearch:plan                       → goal = 100% symbol coverage; metric = coverage%
/autoresearch                            → iterate (calls /apple-dissect --inquire as needed)

/context-save && /gsd:pause-work         → checkpoint + resumable handoff
```
> **Why:** turns any Apple build artifact into a four-layer-memory inventory (file / planning doc / vector / graph) plus a runnable extraction backlog. Built on the new `apple-dissect` skill (§17). Spec: `Skills-Cheatsheet/SEQUENCE-AJ-apple-ingest.md`.

### AK. Apple Inquisitor — Max-Depth `/investigate` for Apple Builds

```
/guard && /freeze                        → lock edits during forensic phase
/gsd:resume-work                         → continue AJ's workspace if paused

[ -d .apple-dissect ] || /apple-dissect <path>   → ensure inventory exists

/investigate                             → open 4-phase inquiry (do NOT exit Phase 3 in this chain)
/superpowers:systematic-debugging        → scientific-method discipline
/gsd:debug "<top-level question>"        → persistent debug session across resets

/autoresearch:plan                       → goal: refute or confirm every plausible hypothesis
                                            metric: hypotheses moved from `pending` → {accepted|refuted}
/autoresearch:debug                      → concurrent autonomous bug-hunting

# Parallel deep-dives (spawn together):
Agent: idme-base:deep-analyst            → thread-safety + state-machine analysis
Agent: idme-base:java-debugger           → iOS-26 behavior analysis (analogue)
Agent: idme-base:adr-researcher          → embedded historical decisions
/superpowers:dispatching-parallel-agents → fan out + join into hypothesis-tree.json

/cso                                     → security audit
/autoresearch:security                   → STRIDE + OWASP-MASVS, ATS / keychain / app-group checks
/code-review (high effort)               → bug-flavored review of every src dir
/simplify (dry-run)                      → propose reuse / dedup wins (do not apply yet)
/superpowers:finding-duplicate-functions → quantify dedup opportunities

/gsd:verify-work && /gsd:audit-uat       → close the loop with rigorous UAT
/idme-base:adr-writer                    → ADR per architectural surprise

/idme-base:writer                        → final dossier RDR
/document-release                        → docs for any fixes that landed
/retro && /learn && /unfreeze            → retrospective + capture + release lock
```
> **Why:** runs `/investigate` recursively inside `/autoresearch`, with parallel deep-analyst / security / structural / dedup agents. Exit criterion is hypothesis-tree coverage, not "first fix landed". Spec: `Skills-Cheatsheet/SEQUENCE-AK-apple-inquisitor.md`.

### AL. Apple Loom — Component Extraction into Reusable Kits

```
# Five standard kits: <App>UIKit · <App>Core · <App>APIClient · <App>Assets · <App>Schema

/superpowers:brainstorming               → confirm which kits are realistic (gate)

/superpowers:dispatching-parallel-agents → one /superpowers:write-plan per kit (parallel)
  ├── <App>UIKit · <App>Core · <App>APIClient · <App>Assets · <App>Schema

/autoplan                                → CEO+Design+Eng+DX review every PLAN.md in one shot
/plan-eng-review                         → architecture lock-in per kit
/plan-design-review                      → only for UIKit + Assets

/superpowers:using-git-worktrees         → per-kit worktree ../<App>-loom/<kit>/
/gsd:new-workspace                       → per worktree
/gsd:plan-phase 1 → /gsd:execute-phase 1 → atomic commits for "move + minimal compile"
/superpowers:subagent-driven-development → parallel sub-tasks per phase
/superpowers:test-driven-development     → test-first for every Public symbol moved

# Protocolize project-specific deps (must reach zero cross-kit concrete refs):
/code-review (high effort) → /simplify → /verify

/superpowers:requesting-code-review      → cross-team `public` surface review
/code-review --comment                   → inline API surface review

/web-artifacts-builder | /playground     → demo per kit
/design-consultation                     → DESIGN.md for the UIKit kit

/gsd:ship (per kit)                      → PR + CHANGELOG + VERSION bump
/superpowers:finishing-a-development-branch → land each branch
/document-release                        → "Five kits extracted from <App>"

/idme-base:adr-writer (per kit)          → "Why we drew the boundary here"
/learn && /retro && /os-integrate        → capture and wire new patterns into the OS
```
> **Why:** consumes AJ's `component-candidates.md` + AK's `hypothesis-tree.json` and ships five reusable Swift Packages (UI kit / business kernel / API client / asset pack / schema pack). Maximum parallelism via worktrees + subagent fan-out. Spec: `Skills-Cheatsheet/SEQUENCE-AL-apple-loom.md`.

---

## 28. Language Server Protocol (LSP) Plugins

Background plugins that give Claude Code IDE-grade code intelligence — go-to-definition, find references, error checking, and refactoring. Not slash commands; they activate automatically when working in the relevant language.

| Plugin | Language | File extensions | Prerequisites |
|--------|----------|-----------------|---------------|
| `swift-lsp` | Swift | `.swift` | Xcode or `brew install swift` (SourceKit-LSP bundled) |
| `jdtls-lsp` | Java | `.java` | Java 17+ JDK, `brew install jdtls` on macOS |
| `typescript-lsp` | TypeScript / JavaScript | `.ts`, `.tsx`, `.js`, `.jsx`, `.mts`, `.cts`, `.mjs`, `.cjs` | `npm install -g typescript-language-server typescript` |
| `ruby-lsp` | Ruby | `.rb`, `.rake`, `.gemspec`, `.ru`, `.erb` | `gem install ruby-lsp` (Ruby 3.0+) |

> **How they work:** Once installed, Claude Code automatically connects to the language server when editing files in those languages. Provides real-time diagnostics, symbol navigation, and intelligent completions without any explicit invocation.

---

## 29. Ralph — Autonomous Dev Loop

Ralph (v0.11.5) is an implementation of Geoffrey Huntley's technique that wraps Claude Code in a continuous autonomous development loop — iterate until done with built-in safeguards. Install once globally via `ralph_enable.sh`.

### Core Scripts

| Command | What it does | Mini use case |
|---------|-------------|---------------|
| `ralph_loop.sh` | Main autonomous loop. Calls Claude Code repeatedly with dual-condition exit gate (completion indicators + explicit EXIT_SIGNAL). Rate-limited to 100 calls/hour. | `ralph_loop.sh` → Claude works autonomously → exits when done or circuit breaker trips |
| `ralph_enable.sh` | Interactive wizard — detects environment, sets up `.ralphrc`, imports tasks from beads / GitHub Issues / PRD | `ralph_enable.sh` → answers setup questions → creates `.ralphrc` → writes PROMPT.md, AGENT.md |
| `ralph_enable_ci.sh` | Non-interactive version for CI/automation. Same wizard, CLI flags only | `ralph_enable_ci.sh --task-source beads --project-name MyApp` |
| `ralph_import.sh` | Import a PRD or spec doc into Ralph's task format | `ralph_import.sh prd.md` → converts PRD sections → creates Ralph task files |
| `ralph_monitor.sh` | Live monitoring dashboard via tmux — shows loop status, circuit breaker state, iteration count | `ralph_monitor.sh` → tmux pane → real-time loop health |

### Key Safeguards

```
Circuit breaker  → halts runaway loops (3 states: CLOSED / HALF_OPEN / OPEN)
Rate limiter     → 100 calls/hour, resets on the hour
Session continuity → --resume <session_id> for context preservation (24h TTL)
--live flag      → stream Claude Code output in real time
```

### Ralph vs /btw

| | `/btw` | Ralph |
|-|--------|-------|
| Invocation | Claude Code slash command | Shell script (`ralph_loop.sh`) |
| Duration | ~60 min autonomous run | Unbounded (until completion) |
| Config | Inline conversation | `.ralphrc` project file |
| Rate limiting | No | Yes (100 calls/hour) |
| Circuit breaker | No | Yes |
| Session resume | No | Yes (`--resume`) |

---

## 30. Caveman — Response Compression

Compresses Claude's output to terse, information-dense responses. Drops articles, filler, pleasantries, and hedging. All technical substance stays intact. Code, commits, and security warnings are always written normally.

Plugin: **caveman@caveman** (version ef6050c5e184)

### Modes

| Level | Behavior |
|-------|---------|
| `full` | Drop articles, fragments OK, short synonyms. Classic caveman. *(default)* |
| `lite` | Lighter compression — drop filler, keep articles |
| `ultra` | Maximum compression |

Switch with `/caveman lite`, `/caveman full`, or `/caveman ultra`.
Stop with "stop caveman" or "normal mode".

### Skills

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/caveman:caveman` | Activate caveman mode (terse responses) | "stop wasting tokens, be direct" |
| `/caveman:caveman-help` | Show caveman mode reference | Check current level and rules |
| `/caveman:caveman-review` | Code review in caveman style — one line per finding, severity-tagged, no praise | `caveman:cavecrew-reviewer` agent wrapper |
| `/caveman:caveman-commit` | Generate terse commit messages | After code changes |
| `/caveman:caveman-stats` | Session stats: tokens saved, compression ratio | Measure compression impact |
| `/caveman:compress` | Compress a block of text in caveman style | Paste verbose text → get terse version |
| `/caveman:cavecrew` | Launch cavecrew subagents (investigator, builder, reviewer) | Delegate surgical tasks to specialized terse agents |

### Cavecrew Agents

| Agent | Role | Scope |
|-------|------|-------|
| `caveman:cavecrew-investigator` | Read-only code locator. Returns file:line table for symbol definitions, callers, usages | "where is X", "what calls Y" |
| `caveman:cavecrew-builder` | Surgical 1-2 file edits. Typo fixes, single-function rewrites, mechanical renames | Hard refuses 3+ file scope |
| `caveman:cavecrew-reviewer` | Diff/branch/file reviewer. One line per finding, severity-tagged | "review this PR", "audit this file" |

### Auto-Clarity

Caveman mode drops automatically for: security warnings, irreversible action confirmations, multi-step sequences where fragment order risks misread, technical ambiguity. Resumes after the clear part.

```
Response pattern:  [thing] [action] [reason]. [next step].
Not:  "Sure! I'd be happy to help you with that. The issue you're experiencing is likely..."
Yes:  "Bug in auth middleware. Token expiry check use < not <=. Fix:"
```

---

## 31. ML / LLM Training

Specialized wrappers for hands-on language-model training experiments. Both built around Karpathy's nanochat / autoresearch repos. **Require an NVIDIA GPU with CUDA** — these do not run on macOS or CPU.

| Skill | What it does | When to use | Mini use case |
|-------|-------------|-------------|---------------|
| `/nanochat` | Wrapper for Karpathy's `nanochat` — minimal hackable LLM training harness covering tokenization, pretraining, SFT, RL, evaluation, inference, and chat UI | "Train a small LM from scratch" / educational deep-dive into the full training pipeline | `/nanochat` → "start nanochat speedrun" → tokenizes → pretrains base → SFT → RL → ships chat UI |
| `/karpathy-autoresearch` | Autonomous LLM-pretraining experiment loop. Edits `train.py`, runs 5-min training budgets, tracks `val_bpb` in `results.tsv`, **keeps wins / reverts losses on a dedicated git branch** | "Iterate on a training recipe overnight" — Karpathy's auto-experiment loop | `/karpathy-autoresearch` → reads `program.md` → runs experiment → improves val_bpb → commits → repeats |

### ML Training Workflow

```
/nanochat                               → set up training harness (one-time)
/karpathy-autoresearch                  → autonomous experiment loop on train.py
/learn                                  → record successful training tweaks
/idme-base:adr-writer                   → capture the architectural decision (e.g. "switched to RoPE")
```

> **Caveat:** these target language-model research, **not** Claude API consumption. For building apps that *use* Claude, see `/claude-api` in §13.

---

## 32. OS Management — Autonomous Self-Improvement

Skills that run the autonomous OS layer. Auto-invoked by hooks, cron, and thresholds — rarely called manually. Lives in `~/.claude/skills/os-*/`.

| Skill | Trigger | What it does | When to invoke manually |
|-------|---------|-------------|------------------------|
| `/os-sync` | Cron Mon 9am; SessionStart if >7 days stale; file watcher on skills/ | Scans all skill paths, diffs against SKILLS-CHEATSHEET.md, adds new skills, marks removed | "New plugin just installed, sync now" |
| `/os-evolve` | Cron Fri 5pm; evolution-log ≥5 pending entries | Synthesizes evolution-log.md into Tier 1/2/3 changes, generates weekly digest | "I want to process pending learnings now" |
| `/os-audit` | Cron 1st Mon 9am; 35+ days since last audit | Monthly health check: skill usage, sequence pass rates, capability gaps, growth metrics | "Audit the OS health manually" |
| `/os-integrate` | After /os-sync detects new skills | Wires new skills into routing table §B and precedence §C (Tier 2 — queued for review) | "I just added several skills, integrate them" |

### Auto-Sync Rules

| Tier | What changes | Approval |
|------|-------------|---------|
| 1 | Manifests, timestamps, health reports, digests | Auto-applied, logged |
| 2 | Routing table §B, precedence §C, sequence updates | 7-day review window |
| 3 | Hard rules §F, session protocol §D, auto-rules.md | Always manual |

### OS Self-Improvement Cycle

```
Mon 9am:  /os-sync      → detect + catalog new skills
Fri 5pm:  /os-evolve    → synthesize learnings → digest
1st Mon:  /os-audit     → health report + growth metrics
          /os-integrate → wire new skills (queued, 7-day review)
```

---

## 33. Plugin Authoring Toolkit

Skills for building, packaging, and shipping Claude Code plugins. Synced 2026-05-12 from `claude-plugins-official` marketplace. Covers the full plugin surface area: structure, skills, commands, agents, hooks, MCP servers, packaging, and demos.

### Plugin Structure & Settings

| Skill | What it does | When to use | Mini use case |
|-------|-------------|-------------|---------------|
| `/plugin-structure` | Scaffold plugin directory layout — `.claude-plugin/`, `skills/`, `agents/`, `commands/`, `hooks/`, `mcp/` | "Create a plugin", "scaffold a plugin", "organize plugin files" | New plugin → `/plugin-structure` → produces canonical directory tree with manifest stubs |
| `/plugin-settings` | Declare user-configurable plugin settings (env vars, defaults, validation) | "Store plugin configuration", ".user-configurable plugin" | Plugin needs an API key → `/plugin-settings` → adds settings.json schema + reader helper |
| `/example-skill` | Canonical example skill demonstrating frontmatter + layout | Reference when teaching skill format | Show new contributors what a SKILL.md should look like |
| `/example-command` | Canonical example user-invoked slash command | Reference for command authoring | Demonstrates frontmatter options + `skills/<name>/SKILL.md` layout |

### Skill / Command / Agent / Hook Development

| Skill | What it does | When to use | Mini use case |
|-------|-------------|-------------|---------------|
| `/skill-development` | Bootstrap a SKILL.md with proper frontmatter (name, description, trigger guidance) | "Create a skill", "add a skill to plugin", "improve skill description" | Plugin needs a new behavior → `/skill-development` → emits SKILL.md with idiomatic trigger phrasing |
| `/command-development` | Create a custom slash command (`commands/<name>.md`) with frontmatter | "Create a slash command", "add a command", "define command parameters" | Plugin exposes a new `/foo` → `/command-development` → produces commands/foo.md |
| `/agent-development` | Write a subagent (`agents/<name>.md`) with role + tool scoping | "Create an agent", "add a subagent", "agent frontmatter" | Plugin needs a specialized reviewer agent → `/agent-development` → produces agents/reviewer.md |
| `/hook-development` | Add PreToolUse / PostToolUse / Stop / SessionStart hooks | "Create a hook", "validate tool use", "intercept Stop event" | Plugin needs to block dangerous bash → `/hook-development` → emits hooks.json + script |
| `/writing-hookify-rules` | Author hookify rule syntax for declarative hook dispatch | "Create a hookify rule", "configure hookify", "add a hookify rule" | Plugin uses hookify → `/writing-hookify-rules` → emits rule with matcher + action |

### MCP & Packaging

| Skill | What it does | When to use | Mini use case |
|-------|-------------|-------------|---------------|
| `/build-mcp-server` | Wrap an API as an MCP server (tools, resources, prompts) | "Build an MCP server", "wrap an API for Claude", "create an MCP" | Internal API → `/build-mcp-server` → emits TS/Python MCP server with tool defs |
| `/mcp-integration` | Wire MCP into plugin via `.mcp.json` | "Add MCP server", "integrate MCP", "use .mcp.json" | Plugin needs MCP → `/mcp-integration` → updates .mcp.json + plugin manifest |
| `/build-mcp-app` | Add interactive UI / widgets / "rendered components" to an MCP server | "MCP app", "interactive UI for MCP", "widgets" | MCP returns a chart → `/build-mcp-app` → adds rendered widget descriptor |
| `/build-mcpb` | Package an MCP server as a distributable MCPB bundle | "Package an MCP", "ship a local MCP server", "MCPB" | Internal MCP → `/build-mcpb` → emits .mcpb archive for distribution |

### Discovery & Polish

| Skill | What it does | When to use | Mini use case |
|-------|-------------|-------------|---------------|
| `/claude-automation-recommender` | Scan a codebase and recommend which automations (hooks, subagents, skills, plugins, MCPs) to build | "Recommend Claude Code automations", "what should I automate" | Existing repo → `/claude-automation-recommender` → ranked list of automation opportunities |
| `/claude-md-improver` | Audit & improve CLAUDE.md files — scope, signal-to-noise, missing sections | "Check, audit, update, or fix CLAUDE.md" | Old CLAUDE.md → `/claude-md-improver` → tightened version with rationale per change |
| `/playground` | Generate an interactive single-file HTML playground that demos the plugin / skill / MCP | "Make a playground", "demo this skill in a browser" | Plugin needs a demo page → `/playground` → emits self-contained HTML explorer |

### Plugin Authoring Workflow

```
1. /claude-automation-recommender  → identify what to build
2. /plugin-structure               → scaffold directory tree
3. /plugin-settings                → declare user-configurable settings
4. /skill-development              → add skills
5. /command-development            → add slash commands
6. /agent-development              → add agents
7. /hook-development               → add hooks (+/writing-hookify-rules if using hookify)
8. /build-mcp-server               → wrap APIs as MCP
9. /mcp-integration                → wire .mcp.json
10. /build-mcpb / /build-mcp-app   → package + add UI
11. /playground                    → ship interactive demo
12. /claude-md-improver            → polish docs
13. /review → /ship                → land & release
```

> See **Sequence AH** in §27 for the full Plugin Authoring chain.
> Related: `/skill-creator` (§13) is the interactive single-skill scaffolder; this suite covers the entire plugin.

---

## 34. M5Stack / ESP32 IoT

End-to-end onboarding for M5Stack ESP32 devices (Cardputer, Cardputer-Adv, Core, CoreS3, Stick). Provisioning + bundled apps + iterative dev — designed for Claude Buddy / Snake / Hello starter apps. From `cwc-makers` plugin.

| Skill | What it does | When to use | Mini use case |
|-------|-------------|-------------|---------------|
| `/m5-onboard` | Detect a freshly-plugged-in M5Stack ESP32 over USB, identify model + USB chip, flash MicroPython firmware, mount filesystem, deploy starter bundle | First-time setup of a Cardputer / Core / Stick | Plug in Cardputer → `/m5-onboard` → autoflashed MicroPython + Claude Buddy bundle ready in <5 min |
| `/cardputer-buddy` | Iterate on the bundled MicroPython apps (Claude Buddy chat client, Snake, Hello) post-onboarding | After `m5-onboard` succeeded — edit / debug / deploy app changes | `/cardputer-buddy` → tweak Claude Buddy prompt → redeploy to device → live test |

### IoT Workflow

```
1. /m5-onboard                  → provision device (one-time per device)
2. /cardputer-buddy             → iterate on the app bundle
3. /playground (§33)            → optional — mirror device UI in browser for design iteration
4. /learn                       → record device-specific quirks (boot pins, partition layout)
```

> **Prerequisites:** USB cable, `esptool.py`, USB serial driver for the device's chip (CH340/CP210x/native). The skill auto-detects and prompts for the driver if missing.
> See **Sequence AI** in §27 for the IoT onboarding chain.

---

## 35. Vercel Plugin

Auto-injecting skill suite from the official `vercel` Claude plugin (v0.43.0). Skills activate automatically based on file patterns, imports, and bash commands — no manual invocation needed. Three specialist **agents** are also available for complex tasks.

> **How it works:** SessionStart hook profiles the project → `VERCEL_PLUGIN_LIKELY_SKILLS` set → skills auto-inject on tool use (file edits, bash commands, imports) and prompt submit. Up to 3 skills per tool call within 18KB budget.

### Auto-Injecting Skills (context-aware, no `/` command needed)

| Skill | Triggers on | What it does |
|-------|------------|-------------|
| `ai-sdk` | `app/api/chat/**`, `@ai-sdk/*` imports, "build AI chat" | Vercel AI SDK — chat, streaming, tool calling, agents, embeddings, MCP |
| `ai-gateway` | `@ai-sdk/gateway` imports, `vercel env pull` | AI Gateway — model routing, provider failover, cost tracking |
| `nextjs` | `next.config.*`, `app/**`, `.next/` | Next.js App Router guidance — layouts, server components, RSC patterns |
| `vercel-functions` | `api/**`, `app/api/**`, Vercel function patterns | Serverless + Edge functions, streaming responses |
| `vercel-cli` | `vercel` bash commands | Vercel CLI — deploy, env, domains, logs, inspect |
| `vercel-storage` | `@vercel/kv`, `@vercel/postgres`, `@vercel/blob` imports | KV, Postgres, Blob storage patterns |
| `auth` | `auth.ts`, `next-auth`, `authjs` patterns | Auth.js / NextAuth configuration |
| `shadcn` | `components/ui/**`, `@/components/ui` | shadcn/ui component installation and usage |
| `chat-sdk` | Chat SDK imports | Vercel Chat SDK — multi-turn, persistence, tool UX |
| `react-best-practices` | After 3+ `.tsx` file edits | React patterns — hooks, performance, composition, accessibility |
| `bootstrap` | Empty/greenfield project detection | Greenfield Next.js setup from scratch |
| `deployments-cicd` | `.github/workflows/**` with vercel patterns | CI/CD pipeline configuration |
| `env-vars` | `vercel env` commands | Environment variable management and `.env` patterns |
| `marketplace` | Marketplace integration patterns | Vercel Marketplace product integrations |
| `turbopack` | `--turbopack` flag, turbopack config | Turbopack configuration and migration |
| `routing-middleware` | `middleware.ts`, matcher patterns | Next.js middleware and routing |
| `runtime-cache` | Cache headers, `revalidate`, `unstable_cache` | Runtime caching strategies |
| `next-cache-components` | Next.js cache imports | Next.js data caching and `use cache` directive |
| `next-forge` | `next-forge` config patterns | next-forge monorepo setup |
| `next-upgrade` | Version upgrade contexts | Next.js version migration guidance |
| `vercel-firewall` | Firewall config patterns | Vercel WAF and DDoS protection |
| `vercel-sandbox` | Sandbox API patterns | Vercel Sandboxes — ephemeral microVMs for code execution |
| `workflow` | Workflow DevKit imports | Durable workflow orchestration (Workflow DevKit) |
| `verification` | Test file patterns | Testing and verification best practices |
| `knowledge-update` | Prompt: "update docs", "knowledge update" | Vercel platform knowledge refresh guidance |

### Specialist Agents (via Agent tool)

| Agent | What it does | When to use |
|-------|-------------|-------------|
| `vercel:ai-architect` | Architect AI apps — AI SDK patterns, provider config, agents, MCP, durable workflows | Designing AI features, chatbots, agentic apps |
| `vercel:deployment-expert` | Deployment strategy, CI/CD, preview URLs, rollbacks, env vars, domains | Troubleshooting deploys, setting up pipelines |
| `vercel:performance-optimizer` | Core Web Vitals, rendering strategies, caching, image/font optimization, bundle size | Slow pages, Lighthouse scores, loading perf |

### Benchmark / Eval Skills (internal, invokable)

| Skill | What it does |
|-------|-------------|
| `/benchmark-agents` | Advanced AI agent scenarios stressing AI Gateway, MCP, Queues, Flags, Sandbox |
| `/benchmark-e2e` | E2E suite: inject skills → dev server → analyze logs → improvement report |
| `/benchmark-sandbox` | Run eval scenarios in Vercel Sandboxes (ephemeral microVMs) |
| `/benchmark-testing` | Create/launch benchmark test projects in isolated dirs with WezTerm panes |
| `/vercel-plugin-eval` | Live eval: verify hook behavior, skill injection, dedup, coverage report |
| `/plugin-audit` | Audit plugin perf on real projects — extract tool calls, test pattern coverage, check cache staleness |

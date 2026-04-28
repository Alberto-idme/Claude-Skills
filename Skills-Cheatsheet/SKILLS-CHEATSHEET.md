# Claude Code Skills Cheat Sheet

> 380+ skills across 24 suites. Organized by workflow stage with mini use cases. Last updated: 2026-04-27.

---

## Table of Contents

1. [gstack — Ship & QA Suite (44 skills)](#1-gstack--ship--qa-suite)
2. [GSD — Get Shit Done Framework (57 commands)](#2-gsd--get-shit-done-framework)
3. [Autoresearch (9 skills)](#3-autoresearch)
4. [Figma Plugin (6 skills)](#4-figma-plugin)
5. [IDME Base — Document Writers (9 skills)](#5-idme-base--document-writers)
6. [Beads — Issue Tracker (1 skill, 26 subcommands)](#6-beads--issue-tracker)
7. [PRD Taskmaster (1 skill)](#7-prd-taskmaster)
8. [UI/UX Pro Max (7 skills)](#8-uiux-pro-max)
9. [Browser Use (4 skills)](#9-browser-use)
10. [Document & Office (6 skills)](#10-document--office)
11. [Creative & Design (6 skills)](#11-creative--design)
12. [Developer Utilities (8 skills)](#12-developer-utilities)
13. [Superpowers (14 skills)](#13-superpowers)
14. [Superpowers Lab (4 skills)](#14-superpowers-lab)
15. [Godmode (37 skills)](#15-godmode)
16. [Apple Platform (1 skill)](#16-apple-platform)
17. [Claude Code Configuration (4 skills)](#17-claude-code-configuration)
18. [Google Workspace Suite (44 skills)](#18-google-workspace-suite)
19. [Google Workspace Recipes (35 recipes)](#19-google-workspace-recipes)
20. [Google Workspace Personas (10 personas)](#20-google-workspace-personas)
21. [Video & Motion (1 skill)](#21-video--motion)
22. [Codex Plugin (2 skills)](#22-codex-plugin)
23. [Context7 Plugin (2 skills)](#23-context7-plugin)
24. [Native Claude Code Commands (3 commands)](#24-native-claude-code-commands)
25. [Workflow Sequences](#25-workflow-sequences)

---

## 1. gstack — Ship & QA Suite

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
| `/gsd:forensics` | Post-mortem for failed GSD workflows | `[description]` | `/gsd:forensics "Phase 3 execution got stuck"` → analyzes git + artifacts → finds stuck loop → writes report |
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

### Autoresearch Flow

```
/autoresearch:plan              → define goal + metric
/autoresearch                   → iterate toward goal
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
| `/figma:figma-implement-design` | Translate Figma → production code with 1:1 fidelity | User shares Figma URL + "implement this" | Reads `get_design_context` → adapts to project stack → outputs production React code |
| `/figma:figma-generate-library` | Build design system in Figma from codebase | "Build our component library in Figma" | Multi-phase: Discovery → Foundations → Components → QA. 20-100+ use_figma calls |
| `/figma:figma-code-connect` | Create and maintain Figma Code Connect template files mapping Figma components ↔ code components | "Connect this Figma button to code" | Uses `get_code_connect_suggestions` → `send_code_connect_mappings` |
| `/figma:figma-create-design-system-rules` | Generate design system rules for AI agents | "Set up design rules for my project" | Outputs CLAUDE.md / AGENTS.md / Cursor rules for consistent Figma→code |

### Figma Workflow Sequence

```
1. /figma:figma-generate-library         → build design system
2. /figma:figma-create-design-system-rules → generate AI rules
3. /figma:figma-generate-design          → build screens (code → Figma)
4. /figma:figma-implement-design         → implement screens (Figma → code)
5. /figma:figma-code-connect             → link components bidirectionally
```

---

## 5. IDME Base — Document Writers

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

## 6. Beads — Issue Tracker

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

## 7. PRD Taskmaster

| Step | What happens |
|------|-------------|
| `/prd-taskmaster` | Triggers 12-step workflow |
| 1. Discovery | 5 core questions about the product |
| 2. PRD Generation | Comprehensive technical PRD |
| 3. Validation | 13 automated checks (completeness, consistency, testability) |
| 4. Task Breakdown | Auto-generates tasks from PRD sections |
| 5. Execution | 4 modes: Sequential, Parallel, Full Autonomous, Manual |

### Execution Modes

```
Sequential  → one task at a time, user approves each
Parallel    → independent tasks run concurrently
Autonomous  → full auto with datetime tracking + rollback
Manual      → generates task list, user executes
```

---

## 8. UI/UX Pro Max

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

## 9. Browser Use

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

## 10. Document & Office

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

## 11. Creative & Design

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

## 12. Developer Utilities

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/mcp-builder` | Guide for creating MCP servers (Python FastMCP or Node/TypeScript SDK) | Building MCP servers to integrate external APIs or services |
| `/skill-creator` | Create, modify, measure, and optimize skills | Creating new skills, editing existing ones, running evals, benchmarking |
| `/webapp-testing` | Playwright toolkit for testing local web apps. Screenshots, browser logs | Verifying frontend functionality, debugging UI behavior |
| `/brand-guidelines` | Apply Anthropic's official brand colors and typography | Any artifact that needs Anthropic's look-and-feel |
| `/internal-comms` | Write internal communications using company formats | Status reports, leadership updates, FAQs, incident reports, project updates |
| `/claude-api` | Build, debug, and optimize Claude API / Anthropic SDK apps. Includes prompt caching | Code imports `anthropic`/`@anthropic-ai/sdk`, using Claude API or Anthropic SDKs |
| `/remotion-best-practices` | Best practices for Remotion — video creation in React | Building programmatic videos, motion graphics with React |
| `/template-skill` | Template for creating new skills (starting point) | Creating a brand new skill from scratch |

---

## 13. Superpowers

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

## 14. Superpowers Lab

Experimental/utility skills.

| Skill | What it does | Mini use case |
|-------|-------------|---------------|
| `slack-messaging` | Send/read Slack via `slackcli` | `slackcli messages send --recipient-id=C123 --message="Deploy complete"` |
| `finding-duplicate-functions` | Semantic duplicate detection in codebases | 5-phase: extract → categorize → split → detect → report. Great for LLM-generated code audit |
| `mcp-cli` | Use MCP servers on-demand via CLI | `mcp tools <server>` → discover → `mcp call <tool> --params '{}' <server>` |
| `using-tmux-for-interactive-commands` | Control interactive CLIs (vim, rebase -i) via tmux | `tmux new-session -d -s edit vim file.txt` → `tmux send-keys` → `tmux capture-pane -p` |

---

## 15. Godmode

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

## 16. Apple Platform

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/rshankras-claude-code-apple-skills-liquid-glass` | Implement Liquid Glass design using `.glassEffect()` API | iOS/macOS 26+ UI effects. Modern glass-based interfaces |

---

## 17. Claude Code Configuration

Harness-level configuration, scheduling, and automation.

| Command | What it does | Key flags | Mini use case |
|---------|-------------|-----------|---------------|
| `/update-config` | Configure Claude Code harness via settings.json. Set up hooks for automated behaviors ("from now on when X", "each time X", "whenever X", "before/after X") | settings.json hooks | `/update-config` → "Run linter before every commit" → creates pre-commit hook in settings.json |
| `/keybindings-help` | Customize keyboard shortcuts, rebind keys, add chord bindings, modify ~/.claude/keybindings.json | rebind, chord | `/keybindings-help` → "rebind ctrl+s" → updates keybindings.json |
| `/loop` | Run a prompt or slash command on a recurring interval. Self-paces when interval omitted | `/loop 5m /foo`, self-paced | `/loop 5m /qa-only https://app.com` → runs QA every 5 minutes → reports changes |
| `/schedule` | Create, update, list, or run scheduled remote agents (triggers) on a cron schedule | create, list, run, delete | `/schedule create "daily security" --cron "0 9 * * *" --prompt "/cso"` → runs CSO audit every morning |

---

## 18. Google Workspace Suite

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

## 19. Google Workspace Recipes

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

## 20. Google Workspace Personas

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

## 21. Video & Motion

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/remotion-best-practices` | Best practices for Remotion — video creation in React | Building programmatic videos with React + Remotion |

---

## 22. Codex Plugin

OpenAI Codex CLI integration — second-opinion review, autonomous rescue, and shared runtime handoff.

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/codex:setup` | Check whether the local Codex CLI is ready and optionally toggle the stop-time mode | One-time setup / health check | `/codex:setup` → verifies Codex CLI installed → toggles stop-time mode if requested |
| `/codex:rescue` | Delegate investigation, an explicit fix request, or follow-up rescue work to Codex through the shared runtime | Stuck on a bug, want an independent pass, or need a deeper RCA | `/codex:rescue` → hands current task to Codex → returns diagnosis + proposed fix |

> Internal-only helpers (not user-invoked): `codex:gpt-5-4-prompting`, `codex:codex-result-handling`, `codex:codex-cli-runtime`. Used by Codex agents themselves.

---

## 23. Context7 Plugin

Live, version-aware documentation lookup for any library, framework, SDK, API, CLI tool, or cloud service.

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/context7-plugin:docs` | Look up documentation for any library | "How do I use X in Next.js 15?" → fetches current docs (avoids stale training data) |
| `/context7-plugin:context7-mcp` | MCP-server entry point for context7 — wraps `resolve-library-id` and `query-docs` | When using context7 as an MCP server inside another agent flow |

> Use Context7 over web search for library docs. Do **not** use for refactoring, debugging business logic, or general programming concepts.

---

## 24. Native Claude Code Commands

Built-in slash commands that ship with Claude Code itself (not part of any plugin).

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/init` | Initialize a new CLAUDE.md file with codebase documentation | New project / first time onboarding Claude to the repo |
| `/review` | Review a pull request | Before merging a PR — runs structured code review |
| `/security-review` | Complete a security review of the pending changes on the current branch | Before landing security-sensitive changes |

---

## 25. Workflow Sequences

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

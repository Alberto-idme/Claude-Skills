# Deep UI/UX Forensics & Replication Blueprint — Multi-Agent Prompt

## Mission

Crawl, dissect, and reverse-engineer the UI, interaction model, design system, and product logic that powers **`<TARGET_URL>`**. Produce:

1. A **forensic atlas** — every screen, component, interaction, microcopy line, and design token, captured at granular detail.
2. A **frame-of-reference map** — the design lineages, mental models, and product philosophies this tool inherits from.
3. A **replication blueprint** — how to build something **measurably better** ("34× better" operationalized as concrete dimensions, see §Targets).
4. A **design system & component spec** for the new product (codename: **Marketing Tool**).
5. A **validated final synthesis** that has survived a hostile multi-perspective review board and a Validator's tests.

No hedging. No excuses. No watered-down "it depends." Go deep, name names, take positions. The point is to come back with the kind of analysis an ultra senior product team would pay $250k for.

> **Practical note on what to clone:** Patterns, structures, interaction models, design principles, and information architectures are fair game — that's how the design industry works. **Verbatim code, copy, branded assets, and copyrighted media are not** — they create real legal exposure for you. All agents should extract *principles* and *patterns*, not paste blobs of source.

---

## Inputs

```yaml
target_url: <fill in>
product_category: <e.g. "AI marketing copy generator">
our_wedge: <optional — what we think our edge is>
budget_for_replication: <optional — small team / well-funded / etc.>
```

---

## Operating Principles

- **Structured outputs only.** Every agent emits the schema specified in its spec, so the next phase can consume it without re-parsing prose.
- **One shared artifact** — `FORENSIC-DOSSIER.md` — grows through the run. Each agent appends its section, never overwrites another's.
- **Cite the source.** Every claim about the target product points to a specific URL, screenshot, DOM selector, or quote.
- **Speculation is allowed but labeled.** Mark inferred claims as `[INFERRED]` and load-bearing observations as `[OBSERVED]`.
- **Best-in-class bar.** "Adequate" gets rejected by the Validator. Ship analysis you'd be proud to present.

---

## Targets — Operationalizing "34× Better"

The Replication Blueprint must demonstrate measurable improvement on **at least 6 of these 10 dimensions**. The Validator tests against this list.

| # | Dimension | How it's measured |
|---|---|---|
| 1 | **Time-to-first-value** | Seconds from signup → user has a useful artifact |
| 2 | **Activation depth** | % of core capabilities surfaced in first session |
| 3 | **Error recovery** | Can the user undo / fix / re-roll without restarting? |
| 4 | **Personalization** | Does the tool adapt to the user, or treat everyone identically? |
| 5 | **Output quality ceiling** | Best-case output vs. target's best-case output |
| 6 | **Output quality floor** | Worst-case output vs. target's worst-case output |
| 7 | **Cognitive load** | Decisions per task; can be measured by counting required inputs |
| 8 | **Agentic leverage** | What the tool does autonomously vs. requires user labor |
| 9 | **Trust & explainability** | Does the user understand *why* the tool did what it did? |
| 10 | **Compounding value** | Does using it more make the next use better? (memory, learning) |

---

# Agent Roster

Each agent runs as a sub-task with a specific mandate, tooling, output schema, and done-criteria. The **Conductor** (below) orchestrates phases.

---

## Phase 0 — Conductor

### `agent.conductor`

- **Role:** Orchestrator. Runs the show end-to-end.
- **Mandate:**
  - Each agent in this prompt is a sub-task. Dispatch each `agent.*` block via the Task tool, passing that agent's mandate as the sub-agent prompt and the dossier path as context.
  - Initialize `FORENSIC-DOSSIER.md` with the section skeleton.
  - Dispatch Phase 1 agents in parallel. Wait for all to complete.
  - Dispatch Phase 2, then 3, then 4 (Validation Board in parallel), then 5 (Validator).
  - **Honor Validator status:** on `REVISIONS_REQUIRED`, re-dispatch the named Phase 1–3 agents with the gaps. On `RESOLUTION_REJECTED_BY_VALIDATOR`, run the **Board Re-deliberation Protocol** (see Phase 5) — re-dispatch the named personas for Round 2 (or Round 3) with the Validator's rebuttal in their context. On `STALEMATE` or `REJECTED`, halt and surface to the human.
  - Detect failed/incomplete agent outputs and re-dispatch with explicit fixes.
  - Maintain a `RUN-LOG.md` with phase timings, agent statuses, board round count, and reconvergence points.
- **Done when:** Validator emits `STATUS: APPROVED` and the final synthesis is written.

---

## Phase 1 — Reconnaissance (run in parallel)

These agents extract **raw, observed** data. No synthesis yet.

### `agent.ui_cartographer`

- **Role:** Map every screen, route, and surface.
- **Mandate:**
  - Enumerate all reachable URLs / routes (public, authed if creds provided).
  - For each: screen name, purpose, primary CTA, secondary actions, layout type (single-column, split, dashboard, modal, etc.), responsive behavior.
  - Note states: empty, loading, populated, error, success.
  - Capture screenshots or DOM snapshots; file under `dossier/ui-cartography/`.
- **Tools:** web crawler, headless browser, screenshot tool, sitemap.xml.
- **Output schema:**
  ```yaml
  screens:
    - id: <slug>
      url: <path>
      purpose: <1 sentence>
      layout_type: <enum>
      primary_cta: <label + action>
      secondary_actions: [...]
      states_observed: [empty, loading, populated, error, ...]
      screenshot_path: <file>
      notes: <free text>
  ```
- **Done when:** ≥95% of reachable surfaces are documented with at least one state captured each.

### `agent.interaction_archaeologist`

- **Role:** Catalog every interaction primitive.
- **Mandate:**
  - Every clickable, hoverable, draggable, keyboard-shortcuttable element.
  - Transitions: timing, easing, directionality.
  - Gestures, drag-and-drop targets, multi-select behavior, undo/redo paths.
  - Keyboard map (`?` menu, command palette, modifier keys).
  - Loading patterns (skeletons vs. spinners vs. optimistic).
  - Feedback mechanisms (toasts, inline, modal, sound, haptic).
- **Output schema:**
  ```yaml
  interactions:
    - element: <selector or description>
      trigger: <click | hover | keyboard | drag | ...>
      response: <description>
      timing_ms: <observed>
      surprise_factor: <low | med | high>
      pattern_lineage: <e.g. "Linear-style command palette">
  keyboard_map: { ... }
  motion_signature: <description of overall motion language>
  ```
- **Done when:** Every distinct interaction class has at least one documented exemplar.

### `agent.design_system_forensics`

- **Role:** Reverse-engineer the design tokens.
- **Mandate:**
  - **Color:** primary palette, semantic colors (success/warn/error/info), surface levels, dark/light mode handling, contrast ratios.
  - **Typography:** font families, scale, line heights, letter-spacing, weights used per role.
  - **Spacing:** observed spacing scale (4px / 8px / custom).
  - **Radii, borders, shadows, blur** — full elevation system.
  - **Iconography:** library used (Lucide, Phosphor, custom?), sizes, stroke weights.
  - **Motion tokens:** standard durations and easings.
  - **Component inventory:** every reusable component (buttons, inputs, cards, chips, modals, drawers, tables, etc.) with all variants.
- **Tools:** DevTools, computed-style inspection, CSS extraction, font-network audit.
- **Output schema:** standard design-token JSON (Style Dictionary / W3C Design Tokens format) + a component inventory table.
- **Done when:** A designer could rebuild the visual language from the tokens alone.

### `agent.ia_analyst`

- **Role:** Information architecture and navigation.
- **Mandate:**
  - Top-level nav model (sidebar / topnav / hybrid / contextual).
  - Hierarchy depth, breadcrumbs, back-stack behavior.
  - Search: scope, ranking, filters, recency.
  - Content taxonomy and labeling conventions.
  - Cross-linking density (does the product encourage exploration or focus?).
- **Output schema:** sitemap tree + nav-pattern description + IA principles inferred.

### `agent.copy_voice_analyst`

- **Role:** Microcopy, voice, tone, and persuasive language.
- **Mandate:**
  - Headlines and value props on the marketing site.
  - In-product microcopy: button labels, empty states, error messages, tooltips, onboarding hints, loading messages.
  - Tone register (formal / casual / playful / authoritative).
  - Use of jargon vs. plain language.
  - Persuasive devices: social proof, scarcity, authority, reciprocity, loss-aversion.
  - Capitalize lessons in a **voice rulebook** the new product can adopt or deliberately diverge from.
- **Output schema:** voice charter (10–15 rules) + microcopy library categorized by surface.

### `agent.onboarding_tracker`

- **Role:** First-run experience and activation.
- **Mandate:**
  - Sign-up flow: steps, friction, social auth, email verification timing.
  - First-session: tour? sample data? blank canvas? template gallery?
  - Time-to-first-meaningful-output (stopwatch the actual experience).
  - Aha-moment design: what does the product do to manufacture one?
  - Drop-off risks: where would a confused user bail?
- **Output schema:** onboarding flowchart + activation funnel + aha-moment hypothesis + measured TTV in seconds.

### `agent.conversion_monetization_analyst`

- **Role:** Pricing, paywalls, and conversion mechanics.
- **Mandate:**
  - Pricing structure (freemium / trial / per-seat / usage / hybrid).
  - Paywall placement: what triggers it, how it's framed.
  - Upgrade prompts: frequency, framing, dismissibility.
  - Free-tier scope: generous-enough-to-share or deliberately throttled?
  - Anti-churn mechanics: cancellation flow, win-back offers.
  - Referral / virality loops if any.
- **Output schema:** pricing-page audit + conversion-touchpoint map + extracted monetization principles.

### `agent.tech_performance_investigator`

- **Role:** Stack, performance, and infrastructure inferences.
- **Mandate:**
  - Frontend framework signature (React / Next / Svelte / etc. — visible from build artifacts).
  - State-management style (URL-driven / client store / server-driven).
  - Realtime mechanisms (websockets, SSE, polling).
  - Page-load metrics (LCP, INP, CLS) on key surfaces.
  - Asset strategy (CDN, image formats, lazy loading).
  - Telemetry visible in network tab (analytics, feature flags, A/B framework).
- **Tools:** DevTools network/performance, Lighthouse, Wappalyzer-style detection.
- **Output schema:** stack hypothesis + perf metrics table + infra inferences.

---

## Phase 2 — Synthesis

These agents read all of Phase 1's outputs and produce higher-order pattern claims.

### `agent.pattern_synthesizer`

- **Role:** Distill the recon data into named patterns.
- **Mandate:**
  - Identify recurring interaction patterns and give each a name + canonical example.
  - Map each pattern to the user need it serves.
  - Flag patterns that are unique vs. those borrowed from elsewhere.
- **Output schema:** pattern library (10–25 entries), each with name, description, exemplar, why-it-works, replication notes.

### `agent.frame_of_reference_mapper`

- **Role:** Identify the design lineages this product inherits from.
- **Mandate:**
  - Which products/companies' DNA shows up here? (Linear, Notion, Stripe, Figma, Superhuman, Apple HIG, Material, Arc, etc.)
  - For each lineage: what specifically was borrowed and how it was adapted.
  - What's *not* borrowed from anyone — the genuine originality.
  - Cultural/aesthetic frames (Bauhaus minimalism, Y2K maximalism, brutalist web, etc.).
- **Output schema:** lineage map with attributed influences and originality assessment.

### `agent.mental_model_reconstructor`

- **Role:** Reverse-engineer the user's mental model the product teaches.
- **Mandate:**
  - What metaphors does the UI use? (canvas / inbox / pipeline / library / ...)
  - What does it assume the user knows?
  - What new vocabulary does it teach?
  - What does the user's "happy path internal narrative" sound like?
- **Output schema:** mental-model description + metaphor inventory + assumed-knowledge audit.

---

## Phase 3 — Strategic

### `agent.differentiator_strategist`

- **Role:** Decide what to keep, change, and improve.
- **Mandate:**
  - For each major pattern from Phase 2: keep / adapt / discard / invert. Justify each.
  - Identify the target's load-bearing strengths (don't break these).
  - Identify the target's actual weaknesses (these are your wedges).
  - Position the Marketing Tool against the target on each Target dimension (§Targets).
- **Output schema:** keep/change/discard table + wedge list + positioning matrix.

### `agent.agentic_architecture_designer`

- **Role:** Design the AI/agent layer that delivers the 34× claim.
- **Mandate:**
  - For each Target dimension where the new product wins, specify the agentic mechanism enabling it.
  - Agent roster for the Marketing Tool itself: each agent's role, inputs, outputs, tools, escalation rules.
  - Memory architecture: per-user, per-workspace, per-task. What's remembered, what's forgotten, how it's surfaced.
  - Model routing: which tasks go to which model class and why.
  - Human-in-the-loop touchpoints: where does the user *want* control, where do they want autonomy?
  - Failure handling and graceful degradation.
- **Output schema:** agent system diagram + per-agent specs + memory model + routing table + HITL map.

### `agent.implementation_architect`

- **Role:** Translate strategy into a buildable plan.
- **Mandate:**
  - Tech stack recommendation (with reasoning vs. alternatives).
  - Repo structure, deployment topology, data model sketch.
  - MVP scope vs. v1 vs. v2 — phased delivery.
  - Risk register: top 5 build risks and mitigations.
  - 90-day roadmap.
- **Output schema:** stack decision-doc + phased roadmap + risk register.

---

## Phase 4 — Validation Board (run in parallel)

Each persona reads the full dossier through Phase 3 and produces a structured critique. **Personas are not vibes — each has a specific evaluative lens and required output.**

**Isolation rule:** Each persona writes its output to `dossier/board/<persona>.md` — *not* to the main dossier. Personas must not see each other's critiques mid-flight; each verdict has to be independent. The Validator merges them in Phase 5.

All personas use the same output schema:

```yaml
persona: <name>
verdict: <STRONG_APPROVE | APPROVE | CONCERNS | REJECT>
strengths: [3 items]
concerns: [3 items, ranked by severity]
specific_changes_requested: [list]
one_question_for_the_team: <single sharpest question>
```

### `agent.persona.optimist`
- **Lens:** Upside ceiling. If everything goes right, how big does this get?
- **Asks:** What's the 10× outcome? What underrated trend does this ride? Where's the compounding moat?

### `agent.persona.pessimist`
- **Lens:** Failure modes and pre-mortem.
- **Asks:** What kills this in 18 months? Which assumption is most fragile? What does the worst-case launch look like?

### `agent.persona.nihilist`
- **Lens:** Strip away the theater. What's actually load-bearing?
- **Asks:** If you removed the brand, the aesthetic, and the marketing copy, is there a real wedge? What's pure performance? What's the smallest version that delivers the actual value?

### `agent.persona.marketing_expert`
- **Lens:** Narrative, positioning, GTM.
- **Asks:** What's the one-sentence story? Who is the wedge customer? What's the channel-product fit? Does the homepage convert?

### `agent.persona.sales_closer`
- **Lens:** Can this close in a 30-second pitch?
- **Asks:** What's the demo moment? What objection will I get most? Who's the economic buyer vs. user? What's the urgency hook?

### `agent.persona.domain_expert`
- **Lens:** Practitioner scrutiny.
- **Asks:** Does this actually solve the workflow problem, or a cartoon version of it? What does a real power user need that's missing? Where does it embarrass itself in front of someone who knows the domain?

### `agent.persona.psychoanalyst`
- **Lens:** Projected vs. real user beliefs.
- **Asks:** What unspoken anxiety is this product feeding? What does the founder unconsciously believe about the user? Where is the product solving the founder's problem instead of the user's?

### `agent.persona.researcher`
- **Lens:** Evidence and rigor.
- **Asks:** Which claims here are load-bearing and unevidenced? What study/test/interview would falsify the strategy? What do we actually know vs. assume?

### `agent.persona.pragmatist`
- **Lens:** Can a real team actually ship this?
- **Asks:** Given a 4-person team and 6 months, what's cuttable? Where will the build slip? What's the smallest valuable thing you could ship in 4 weeks?

### `agent.persona.user_advocate`
- **Lens:** Whose interest does the product serve?
- **Asks:** Where does the design serve the company at the user's expense (dark patterns, attention traps, lock-in)? Where could it be more honest? Would you recommend it to your sister?

---

## Phase 5 — The Validator

### `agent.validator`

- **Role:** Reconcile the board, run tests, ship the final synthesis.
- **Inputs:** Full dossier through Phase 4.
- **Mandate:**

  **A. Reconciliation**
  - Cluster overlapping concerns from the board. Promote any concern raised by ≥3 personas to **Must-Address**.
  - Surface the sharpest single objection across all personas — name it explicitly.
  - Where personas disagree, take a position with reasoning. Don't average.

  **B. Tests against the Targets (§Targets)**
  - For each of the 10 dimensions, score the Replication Blueprint as: **Wins / Parity / Loses** vs. target, with justification.
  - Require a Win on **≥6/10**. If fewer, send the blueprint back to `agent.agentic_architecture_designer` with specific gaps.

  **C. Internal-consistency tests**
  - Does the Design System spec cover every component the Implementation Architect's roadmap requires?
  - Does the agentic architecture have memory primitives sufficient for the "compounding value" target?
  - Does the onboarding plan deliver the claimed time-to-first-value?
  - Are all `[INFERRED]` claims either downgraded to assumptions in the risk register or upgraded with evidence?

  **D. Resolution quality — 75% pass threshold**

  Score the board's resolution against these 8 criteria. Each is **PASS** or **FAIL**. The resolution must score **≥6/8 (75%)** to be accepted.

  | # | Criterion | PASS means |
  |---|---|---|
  | 1 | **Coverage** | Every Must-Address concern (raised by ≥3 personas) has an explicit response in the resolution |
  | 2 | **Sharpest-objection rebuttal** | The single sharpest objection is named *and* rebutted with reasoning, not deflected |
  | 3 | **Disagreement adjudication** | Where personas disagreed, the resolution takes a position with reasoning (no averaging, no "both sides have a point") |
  | 4 | **Evidence-claim ratio** | Load-bearing claims cite a source from the dossier; `[INFERRED]` claims are flagged as such |
  | 5 | **Targets coherence** | The resolution is consistent with the Targets scoring in §B (doesn't claim wins where §B shows parity/loss) |
  | 6 | **Falsifiability** | At least one concrete test, metric, or observation is named that *would* falsify the strategy |
  | 7 | **No new contradictions** | The resolution doesn't introduce claims that conflict with the Forensic Atlas or earlier strategy phases |
  | 8 | **Actionability** | A reader could turn the resolution into a build plan without asking clarifying questions |

  **If <6/8:** emit `RESOLUTION_REJECTED_BY_VALIDATOR` with a structured rebuttal (see status spec below) and send back to the board for **Round 2**. Do not produce final output yet.

  **E. Final output** *(only when resolution passes ≥6/8)*
  - Executive summary (1 page max).
  - Forensic atlas (deliverable 1).
  - Frame-of-reference map (deliverable 2).
  - Replication blueprint with agentic architecture (deliverable 3).
  - Design system spec (deliverable 4).
  - Validation board verdict + Validator's reconciliation (deliverable 5).
  - 90-day roadmap with the top 5 risks called out.

- **Status emitted (one of):**
  - `APPROVED` — resolution scored ≥6/8, Targets ≥6/10, internal-consistency clean. Final output written.
  - `REVISIONS_REQUIRED: <specific agent list + gaps>` — Phase 1–3 issue. Conductor re-dispatches the named agents.
  - `RESOLUTION_REJECTED_BY_VALIDATOR` — board's resolution failed the 75% bar. Must include:
    - Score per criterion (which of the 8 passed/failed)
    - Specific unreconciled concerns (quoted from persona reports)
    - Specific questions the next round must answer
    - Personas to re-engage (default: all 10; if the failure is narrow, name a subset)
  - `STALEMATE` — only after **3 board rounds**. Includes the strongest version of the resolution, the unresolved disagreements, and a recommendation to the human on how to break the tie.
  - `REJECTED: <reason>` — fundamental flaw upstream that re-dispatching can't fix; escalate to human.

- **Done when:** Status is `APPROVED` and all six final-output deliverables are present in the dossier.

---

### Board Re-deliberation Protocol (Round 2 and Round 3)

Triggered when the Validator emits `RESOLUTION_REJECTED_BY_VALIDATOR`.

- **Conductor re-dispatches the named personas** with three additions to their original mandate:
  1. The prior resolution (Round N−1 output).
  2. The Validator's structured rebuttal (which criteria failed, which concerns weren't reconciled, the specific questions to answer).
  3. An instruction to **address the Validator's rebuttal directly** in their new critique — not just restate their prior position.
- **Isolation rule still holds.** Personas write to `dossier/board/round-<N>/<persona>.md`. They see the Validator's rebuttal and the prior resolution, but **not** each other's new critiques.
- **A persona may converge** (update verdict from `CONCERNS` to `APPROVE`) if the rebuttal addresses their concern. They must say so explicitly.
- **A persona may dig in** (hold their objection). They must explain why the rebuttal didn't satisfy them.
- **Round cap: 3.** If Round 3 still scores <6/8, the Validator emits `STALEMATE` rather than looping further. Genuinely irreconcilable disagreements deserve human judgment, not infinite agent churn.
- **Cumulative log:** The dossier preserves all rounds (`board/round-1/`, `board/round-2/`, `board/round-3/`) so the human can audit what shifted and what didn't.

---

## Final Output Spec

```
FORENSIC-DOSSIER.md
├── 0. Executive Summary (Validator-authored, 1 page)
├── 1. Forensic Atlas
│    ├── 1.1 UI Cartography (screens + screenshots)
│    ├── 1.2 Interaction Archaeology
│    ├── 1.3 Design Tokens (JSON)
│    ├── 1.4 Component Inventory
│    ├── 1.5 IA & Navigation
│    ├── 1.6 Voice & Microcopy Library
│    ├── 1.7 Onboarding & Activation Audit
│    ├── 1.8 Conversion & Monetization Audit
│    └── 1.9 Tech Stack & Performance
├── 2. Frame-of-Reference Map
├── 3. Pattern Library
├── 4. Mental Model Analysis
├── 5. Differentiation Strategy (keep/change/discard + wedges)
├── 6. Agentic Architecture for the Marketing Tool
├── 7. Design System Spec for the Marketing Tool
├── 8. Implementation Plan & 90-day Roadmap
├── 9. Validation Board Reports (10 personas × N rounds, structured)
│    ├── board/round-1/<persona>.md
│    ├── board/round-2/<persona>.md  (only if Validator rejected Round 1)
│    └── board/round-3/<persona>.md  (only if Validator rejected Round 2)
├── 10. Validator Reconciliation & Test Results (incl. 8-criterion scoring per round)
└── 11. Open Questions & Risk Register
```

---

## Run Instructions

1. Fill in `target_url` and any optional context.
2. Conductor initializes the dossier skeleton.
3. Phase 1 agents run in parallel. Conductor blocks on completion.
4. Phase 2 agents run in parallel. Conductor blocks.
5. Phase 3 agents run sequentially (each depends on prior).
6. Phase 4 personas run in parallel (Round 1).
7. Validator runs, produces a status.
8. **Loopbacks:**
   - `REVISIONS_REQUIRED` → Conductor re-dispatches the named Phase 1–3 agents with the Validator's gaps; resume from Phase 4 once they complete.
   - `RESOLUTION_REJECTED_BY_VALIDATOR` → Conductor runs the Board Re-deliberation Protocol (next round of Phase 4) with the Validator's rebuttal injected into persona contexts; then re-runs the Validator. Max 3 board rounds.
   - `STALEMATE` (after Round 3) or `REJECTED` → halt and surface to the human with the strongest version + unresolved disagreements.
9. Loop until `APPROVED`.

**Begin.**

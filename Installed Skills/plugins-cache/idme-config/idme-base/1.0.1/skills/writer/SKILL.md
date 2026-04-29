---
name: writer
description: Create Recommendation Data/Decisioning Records (RDRs) - specification-first development documents for complex features requiring detailed research, alternatives analysis, and validation before coding. Supports Fast/Standard/Deep research tracks with 2-4 iteration cycles. Integrates with beads for research tracking and ChromaDB for knowledge management. Use when implementation needs iteration on approach before committing to code.
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - WebSearch
  - WebFetch
  - mcp__plugin_beads_beads__create
  - mcp__plugin_beads_beads__update
  - mcp__plugin_beads_beads__list
  - mcp__plugin_beads_beads__show
  - mcp__plugin_beads_beads__close
  - mcp__plugin_infrastructure-setup_chromadb__chroma_query_documents
  - mcp__plugin_infrastructure-setup_chromadb__chroma_add_documents
---

# RDR (Recommendation Data/Decisioning Record) Writer

## **CRITICAL CONSTRAINTS**

1. **USE BEADS TO TRACK ALL RESEARCH THREADS** - Most important pattern for preventing context loss
2. Document targets ~2000 words (soft limit, excluding appendix)
3. RDRs must be immutable once status is "Proposed" - never edit after locking
4. All assertions must be verified through web/code search
5. Expect 5-15 back-and-forth exchanges with 2-4 complete iteration cycles

## What Are RDRs?

**RDRs (Recommendation Data/Decisioning Records)** are specification-first development documents that enable iteration on design before implementation.

### Key Benefits
- **Iterate on specifications before code** - Saves implementation rework
- **Capture technical decisions with provenance** - Research tracked in beads
- **Cross-validate multiple RDRs** - Catches inconsistencies early
- **Use as immutable specs** - Drive development with minimal intervention
- **Avoid sunk-cost fallacy** - Change direction easily before emotional investment in code

### RDRs vs Other Documentation

**RDR vs ADR (Architectural Decision Record)**:
- ADRs document **why** a decision was made (justification)
- RDRs document **what** and **how** before implementation (planning)
- ADRs are written after decisions are finalized
- RDRs are written before coding begins as executable blueprints

**RDR vs Design Document**:
- Design docs are comprehensive system architecture documents
- RDRs are focused, implementation-ready specifications for specific features
- RDRs emphasize iterative research and explicit locking phases

## When to Use RDRs

### Use RDRs When:

1. **Making technical decisions** that affect multiple components
   - Which library to use for a specific feature
   - How to structure a complex data flow
   - Performance optimization approaches

2. **Documenting research findings** from deep investigation
   - After using deep-research-synthesizer or adr-researcher agents
   - When consolidating information from multiple sources
   - After debugging complex issues

3. **Planning significant implementations**
   - Before starting epic-level work in beads
   - When multiple approaches exist and trade-offs need documenting
   - For decisions that future agents will need to reference

### Don't Use RDRs For:

- **Simple bug fixes**: Use beads task notes instead
- **Obvious choices**: No need to document standard patterns
- **Transient session notes**: Use memory bank for temporary information
- **Code comments**: Keep inline documentation in source files

## RDR Effort Levels

RDRs are classified by scope and complexity:

### Fast Track (1-2 hours)
- Simple features following clear existing patterns
- Minimal research needed (can reference similar RDR)
- Low cross-RDR dependency impact
- Streamlined: trigger → draft → validate → implement → close
- **Example**: Add new CLI flag following established patterns

### Standard Track (3-6 hours)
- Complex features requiring original research
- Multiple validation rounds needed
- Cross-RDR consistency checks required
- 2-4 iteration cycles with refinement passes
- **Example**: New integration requiring architecture decisions

### Deep Research Track (6-12 hours)
- Very complex features or major architectural decisions
- Multi-source research (web + semantic db + agent analysis)
- Multiple research threads tracked in beads
- Comprehensive verification across all existing RDRs
- **Example**: Performance optimization requiring system-wide analysis

## RDR Lifecycle

Every RDR follows this lifecycle from creation to implementation:

### 1. Create
- Start from RDR template
- Document problem statement and context
- Initial research and solution exploration
- Status: "Recommendation" or "Draft"

### 2. Iterate (2-4 cycles typical)
- Each cycle: Draft → Verify → Refine → Validate
- Conduct focused research (5-7 research tasks per cycle)
- **Track ALL research threads in beads** (prevents context loss)
- Evaluate alternatives and capture rationale with evidence
- Validate against existing RDRs
- Verify assertions through code/web search
- Expect 5-15 back-and-forth exchanges
- Keep RDR concise but complete

### 3. Think Time
- Let design sink in
- Gather informal feedback
- Identify gaps or concerns
- Final refinement pass

### 4. Lock Design
- Mark RDR as "Proposed" status
- **RDR becomes IMMUTABLE - DO NOT edit after this point**
- Can commit to feature branch alongside implementation
- Immutability preserves design rationale and decision history
- Document deviations during implementation in Track Errata phase

### 5. Implement
- Create beads issues from RDR sections
- Work iteratively through implementation tasks
- Use RDR as authoritative design reference
- Status: "In Progress" → "Implemented"

### 6. Track Errata
- Document issues discovered during implementation
- Capture lessons learned
- Note deviations from design
- Do NOT edit original RDR retroactively

## Core Practices

### 1. Parallel Research Before Writing (REQUIRED: Track in Beads)

- Conduct 5-7 focused research tasks before synthesizing RDR
- **Track each research task as beads issue** - essential for preventing context loss
- Extended RDR sessions will lose research findings without explicit tracking
- Research areas:
  - Library/framework capabilities and APIs
  - Opensource project implementations
  - Technical constraints (performance, scaling, limits)
- Ensures evidence-based decisions with clear provenance

### 2. Cross-Validation After Writing (5-7 verification tasks)

Execute these validation methods:

- **Assertion Verification**: Web search or code search to confirm all technical claims
  - Prompt: "review whole rdr. confirm assertions through code/web search"

- **Cross-RDR Consistency**: Check terminology, patterns, and approaches align
  - Prompt: "review @doc/rdr/ documents. ensure [TERM] usage consistent across RDR-X, RDR-Y"

- **Implementation Readiness**: Verify RDR has sufficient detail to implement
  - Prompt: "review [RDR] and make implementation plan. check dependent rdrs"

- **Format Compliance**: Run markdownlint to catch structural issues
  - Prompt: "ensure rdr properly formatted via markdownlint"

- **Internal Consistency**: Verify scope, priorities, and design decisions align throughout

### 3. Iterative Refinement

- Expect 2-4 complete iteration cycles
- Within each cycle: draft → verify → refine → validate
- Track significant updates as beads tasks
- Common refinements:
  - Adding capabilities discovered during research
  - Adjusting designs for consistency with prior RDRs
  - Simplifying by removing unnecessary complexity
  - Correcting assumptions invalidated by research

### 4. Research Escalation Pattern

Escalate research complexity based on needs:

- **Level 1 - Direct Research**: Web search and code grep for straightforward questions
  - When: Answering specific factual questions
  - Prompt: "search web for [TOPIC] and review code for [PATTERN]"

- **Level 2 - Collection Search**: Index repositories into ChromaDB for semantic analysis
  - When: Need to understand patterns across large codebases
  - Prompt: "i've added [REPO] to arc:[COLLECTION]. search for [QUESTIONS]"

- **Level 3 - Agent Spawn**: Use specialized agents for comprehensive analysis
  - When: Complex multi-source research or deep architectural investigation
  - Prompt: "use deep-analyst/adr-researcher to analyze [SYSTEM] including [DETAILS]"

## RDR Template Structure

Every RDR follows this structure:

```markdown
# Recommendation [NUMBER]: [TITLE]

## Metadata
- **Date**: YYYY-MM-DD
- **Status**: Recommendation | Draft | Proposed | In Progress | Implemented | Superseded
- **Type**: Feature | Bug Fix | Technical Debt | Framework Workaround | Architecture
- **Priority**: High | Medium | Low
- **Related Issues**: [Links to beads issues]
- **Related Tests**: [Test classes or scenarios]

## Problem Statement
[Clear, concise description of the problem or need]

## Context

### Background
[Provide relevant background:
- How the issue was discovered
- Current system behavior
- Impact on users or system
- Any constraints or requirements]

### Technical Environment
[Describe relevant technical context:
- Framework versions
- Dependencies
- System architecture
- Related components]

## Research Findings

### Investigation Process
[Document the research approach:
- Code analysis performed
- Documentation reviewed
- Experiments conducted
- External resources consulted]

### Key Discoveries
[List important findings:
- Root causes identified
- Framework limitations discovered
- Performance implications
- Security considerations]

## Proposed Solution

### Approach
[Detailed description of the recommended solution]

### Technical Design
[Include relevant technical details:
- Architecture diagrams (in appendix)
- Code structure
- API changes
- Data model changes]

### Implementation Example
```[language]
// Example code demonstrating key aspects
```

## Alternatives Considered

### Alternative 1: [Name]
**Description**: [Brief description]
**Pros**:
- [Advantage 1]
- [Advantage 2]
**Cons**:
- [Disadvantage 1]
- [Disadvantage 2]
**Reason for rejection**: [Why not chosen]

### Alternative 2: [Name]
[Same structure...]

## Trade-offs and Consequences

### Positive Consequences
- [Benefit 1]
- [Benefit 2]

### Negative Consequences
- [Drawback 1]
- [Drawback 2]

### Risks and Mitigations
- **Risk**: [Description]
  **Mitigation**: [How to address]

## Implementation Plan

### Prerequisites
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]

### Step-by-Step Implementation

#### Step 1: [Title]
[Detailed instructions]

#### Step 2: [Title]
[Detailed instructions]

### Files to Modify
- `path/to/file1` - [Description of changes]
- `path/to/file2` - [Description of changes]

### Dependencies
- [New dependencies to add]
- [Dependencies to update]

## Validation

### Testing Approach
[How to verify solution works correctly]

### Test Scenarios
1. **Scenario**: [Description]
   **Expected Result**: [What should happen]

2. **Scenario**: [Description]
   **Expected Result**: [What should happen]

### Performance Validation
[How to verify performance requirements]

### Security Validation
[How to verify security requirements]

## References
- [Links to documentation]
- [Links to related issues]
- [Links to research resources]

## Notes
[Additional notes, considerations, future improvements]

## Appendix
[ASCII diagrams, schemas, detailed technical specifications]
```

## Workflow Prompts by Phase

### Trigger/Suggestion Phase

**Pattern: Issue-to-RDR Conversion**
```
create rdr for [FEATURE]. there will be [N] modes: [MODE_1], [MODE_2].
[CONSTRAINTS]
```

**Pattern: Check Existing RDRs First**
```
reviewing prior rdrs, do we need a new rdr for [FEATURE] or extend [EXISTING_RDR]?
```

### Creation/Drafting Phase

**Pattern: Research-Driven Creation** (Most Important)
```
let's create/implement rdr for [ISSUE_ID]. review relevant rdrs for [RELATED_TOPICS].
use beads to track lines of research. ensure we are complimentary to prior rdrs.
if we need to modify a prior rdr, open a beads issue to address. use [AGENT_NAME]
to review [TARGET_SOURCE]. we are only writing one rdr document, no code or summaries.
```

**Key Elements**:
- Explicitly state "only writing RDR, no code"
- Use beads to track ALL research threads
- Reference related RDRs by number
- Use specialized agents for investigation
- Plan for 2-4 hours of iterative work

**Pattern: Multi-Source Research**
```
Review [TECHNOLOGY] ([GITHUB_URL]) architecture and [ASPECT] patterns.

Focus on:
1. **[ASPECT_1]** - [KEY_QUESTION_1]
2. **[ASPECT_2]** - [KEY_QUESTION_2]
[... 5-8 aspects total]
7. **Comparison to [EXISTING_SOLUTION]** - How similar/different?
```

### Research/Investigation Phase

**Pattern: Codebase Research with Tracking**
```
i've added [SOURCE_CODE/DOCS] to [COLLECTION_NAME] chroma collection.
use beads to track all todo and research items so they are not forgotten
as the rdr is being created
```

**Pattern: Assertion Verification**
```
review the whole rdr. confirm assertions through code or web search.
ensure the document is consistent with itself and priorities are
consistently applied across the doc
```

### Validation/Review Phase

**Pattern: Cross-RDR Consistency Check**
```
review @doc/rdr/ documents. in [RDR_NUM] we [DECISION_MADE].
[OTHER_RDR_NUM] has [CONFLICTING_CONTENT]. let's align them by
[ALIGNMENT_ACTION] so that [RATIONALE]
```

**Pattern: Implementation Readiness Check**
```
review @doc/rdr/[RDR_FILE] and make a plan for implementation.
review completed rdrs and ensure there are no changes that need
to be accounted for
```

**Pattern: Format Check**
```
ensure rdr properly formatted via markdownlint
```

### Implementation Phase

**Pattern: Standard Implementation**
```
implement @doc/rdr/[RDR_FILE]
```

**Pattern: Implementation with Review**
```
implement @doc/rdr/[RDR_FILE]. review all other rdrs to first ensure
the proposal will satisfy [DEPENDENCY_CONCERN]. propose deviations
from the rdr plan after reviewing the rdrs
```

**Pattern: Post-Implementation Update**
```
mark rdr [NUMBER] as [STATUS] and update any related issues.
update @doc/rdr/README.md
```

## Anti-Patterns to Avoid

### 1. "Implement Then Document" Trap
**Bad**: Writing RDR after code is already written
**Why Bad**: RDRs are planning documents that enable iteration before coding
**Fix**: Always create RDR before implementation, treat as immutable spec

### 2. "No Research" RDR
**Bad**: Drafting from general knowledge without verification
**Why Bad**: Assertions become outdated/wrong, implementation fails
**Good Evidence**: Empirical data, benchmarks, actual API behaviors, concrete examples
**Bad Evidence**: Hearsay ("everybody does it"), vague claims without verification
**Fix**: Always verify through web/code search, track research in beads

### 3. "Mega RDR" Problem
**Bad**: Single RDR covering 5+ distinct concerns
**Why Bad**: Hard to review, implement, and maintain; creates dependencies
**Fix**: Split into focused RDRs that reference each other

### 4. "Orphan RDR"
**Bad**: No links to beads issues or other RDRs
**Why Bad**: Lost context, unclear dependencies, forgotten implementations
**Fix**: Link RDRs to beads epics via `external_ref`, reference related RDRs by number

### 5. "Stale Assertions" Problem
**Bad**: Copying claims without verification
**Why Bad**: Outdated versions, changed APIs, incompatible patterns
**Fix**: Run "review whole rdr. confirm assertions" before locking

## Word Count Management

- Target: ~2000 words (soft limit, excluding appendix)
- Move technical details to appendix (diagrams, schemas, detailed specs)
- Focus on essential information for implementation
- Use concise language and bullet points where appropriate
- Continuously monitor word count during writing

## Validation Checklist

Before marking RDR as "Proposed", verify:

- [ ] All assertions verified through web/code search
- [ ] Cross-RDR consistency checked (terminology, patterns)
- [ ] Format validated via markdownlint
- [ ] Implementation plan is detailed and actionable
- [ ] All research threads tracked in beads
- [ ] Alternatives documented with pros/cons
- [ ] Trade-offs and consequences captured
- [ ] Related RDRs referenced by number
- [ ] Beads issues linked via related issues field

## Your Approach as RDR Writer Skill

1. **Assess Effort Level**: Determine Fast/Standard/Deep track based on complexity
2. **Create Beads Issues**: Track 5-7 research areas before starting
3. **Conduct Research**: Use web search, code analysis, ChromaDB queries, or spawn agents
4. **Draft RDR**: Follow template structure, document all findings
5. **Verify Assertions**: Confirm all technical claims through search
6. **Check Consistency**: Review against existing RDRs in doc/rdr/
7. **Format Check**: Run markdownlint validation
8. **Iterate**: Refine 2-4 times based on validation findings
9. **Lock Design**: Mark as "Proposed" when ready (becomes immutable)
10. **Update Index**: Update doc/rdr/README.md with new RDR entry

## Critical Success Factors

1. **Beads Integration**: ABSOLUTELY CRITICAL - track ALL research threads
   - Most important pattern: "use beads to track research. only write rdr, no code"
   - Extended sessions WILL lose context without beads tracking

2. **Iterative Process**: Embrace 5-15 exchanges with 2-4 complete cycles
   - Don't rush to implementation
   - Refine based on validation findings
   - Allow time for research and verification

3. **Evidence-Based**: All assertions must be verified
   - Web search for library versions and capabilities
   - Code search for existing patterns
   - Empirical testing for performance claims

4. **Immutability Discipline**: Once "Proposed", RDRs are frozen
   - Track deviations in errata, not in original RDR
   - Create new RDRs to supersede if major changes needed

5. **Cross-RDR Awareness**: Maintain consistency across related RDRs
   - Check terminology alignment
   - Verify pattern consistency
   - Update dependent RDRs via beads issues

## Example Fast Track Workflow (1-2 hours)

```bash
# 1. Trigger
"create rdr for [SIMPLE_FEATURE]. review [SIMILAR_RDR] for patterns"

# 2. Draft
[Create RDR-NNN-title.md following template]

# 3. Validate
"review rdr for consistency. run markdownlint"

# 4. Implement
"implement @doc/rdr/RDR-NNN-title.md"

# 5. Close
"mark rdr NNN as implemented. update @doc/rdr/README.md"
```

## Example Standard Track Workflow (3-6 hours)

```bash
# 1. Trigger with scope question
"reviewing prior rdrs, do we need new rdr for [FEATURE] or extend [EXISTING]?"

# 2. Research phase
"use beads to track research. review [TECHNOLOGY] focusing on:
1. [ASPECT_1]
2. [ASPECT_2]
[... 5-7 aspects total]"

# 3. Draft with cross-references
"create rdr. ensure complimentary to [RDR_A] and [RDR_B].
track research in beads. only write rdr, no code"

# 4. Verify assertions
"review whole rdr. confirm assertions through code/web search"

# 5. Cross-RDR consistency
"review @doc/rdr/ to align [TERM] usage across RDR-X, RDR-Y"

# 6. Format check
"ensure rdr properly formatted via markdownlint"

# 7. Implementation planning
"review [RDR] and make implementation plan. check for dependent rdrs"

# 8. Implement
"implement @doc/rdr/[RDR]. propose deviations after reviewing rdrs"

# 9. Close loop
"mark rdr [NUM] implemented. close related issues. update readme"
```

## Example Deep Research Track Workflow (6-12 hours)

```bash
# 1. Scope with dependency analysis
"create rdr for [COMPLEX_FEATURE]. review rdrs [A, B, C] for related patterns.
identify if new rdr or should extend existing"

# 2. Multi-source research with beads tracking
"i've added [REPO_1], [REPO_2] to arc collections.
use beads to track these research threads:
- [THREAD_1]
- [THREAD_2]
- [THREAD_3]"

# 3. Spawn specialized agent for analysis
"use [AGENT] to conduct VERY THOROUGH analysis of [SYSTEM].
focus on [DETAILED_QUESTIONS]. provide file paths and line numbers"

# 4. Iterative drafting (repeat 2-3 times)
"create rdr draft. only rdr, no code"
"update rdr with [RESEARCH_FINDINGS]"
"ensure rdr consistent with itself regarding [ASPECT]"

# 5. Comprehensive verification
"review whole rdr. confirm assertions. check cross-rdr consistency"

# 6. Alternatives analysis
"compare [APPROACH_A] vs [APPROACH_B] for [RDR].
provide trade-offs and recommendation"

# 7. Pre-implementation validation
"review [RDR] for implementation readiness.
ensure no changes from completed rdrs need accounting"

# 8. Staged implementation
"implement [RDR]. focus on [SUBSET] before [DEPENDENT_PART].
propose deviations with justification"

# 9. Close with documentation
"mark rdr [NUM] implemented. update readme.
document deviations in [BEADS_ISSUE]"
```

## Integration with Other Agents

- **java-architect-planner**: Can automatically create RDRs for epics
- **deep-research-synthesizer**: Use for Deep track multi-source research
- **adr-researcher**: Use for ADR-style decision research within RDRs
- **java-developer**: Implements RDRs following test-first methodology
- **code-review-expert**: Reviews RDR implementation for quality

## Pro Tips

1. **Start with beads**: Create research tracking issues BEFORE drafting
2. **Use ChromaDB**: Index relevant repos for semantic search during research
3. **Reference by number**: Always cite related RDRs by number (RDR-005, RDR-010)
4. **Verify everything**: Don't trust memory - web search and code search all claims
5. **Iterate fearlessly**: 2-4 cycles is normal - embrace refinement
6. **Lock deliberately**: Mark "Proposed" only when truly ready (becomes immutable)
7. **Track deviations**: Use errata section or beads issues, never edit locked RDRs

Remember: RDRs are about capturing the **why** behind decisions and **how** to implement them in a concise, evidence-based way. Focus on iteration before implementation to avoid the sunk-cost fallacy of premature coding.

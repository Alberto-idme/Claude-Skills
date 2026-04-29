---
name: adr-writer
description: Write Architectural Decision Records (ADRs) under 900 words with validation, evidence-based decision capture following structured template
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - mcp__plugin_beads_beads__create
  - mcp__plugin_beads_beads__update
  - mcp__plugin_beads_beads__list
---

# Architectural Decision Record (ADR) Writer

## **CRITICAL CONSTRAINTS**

1. The document MUST be under 900 words (excluding appendix with ASCII diagrams and SQL DDL)
2. After writing the ADR, you MUST validate the word count using bash
3. If word count exceeds 900, immediately revise to condense content

## Memory Management

Use the `bd` tool to track progress through the ADR creation process. Create issues for each major section. Fall back to chromadb MCP server or standard Claude memory if `bd` is unavailable.

Example workflow:
```bash
bd create "ADR: Summary section" -t task -p 1
bd create "ADR: Context section" -t task -p 1
bd create "ADR: Decision section" -t task -p 1
bd create "ADR: Consequences section" -t task -p 1
bd create "ADR: Alternatives section" -t task -p 1
bd create "ADR: Word count validation" -t task -p 1
```

## About ADRs

Architectural Decision Records (ADRs) are concise documents that capture a single significant technical or architectural decision in context. They help you understand the reasons for a chosen architectural decision, along with its trade-offs and consequences.

### Goals
- **Primary**: Enable prioritized technical decision making
- **Secondary**:
  - Preserve institutional knowledge and rationales
  - Improve transparency and stakeholder participation
  - Support future-proofing, auditing, and AI-driven knowledge mining
  - Ensure consistent documentation in production-readiness processes

### ADRs vs RFCs and ARB
- ADRs focus on the **why** over the **how**
- Do NOT require a full ARB meeting
- Usually finalized with a smaller audience
- Often related to an RFC discussed in ARB
- Separate from execution plans for clarity

## Tenets

1. **Single decision focus**: Each ADR records ONE architecturally significant decision, concise and clear
2. **Immutable**: Approved ADRs are immutable. New insights lead to new ADRs that supersede prior ones
3. **Evidence backed**: Include alternatives, pros/cons, trade-offs - grounded in context, not opinion
4. **Shared ownership**: Anyone may author; owners maintain and shepherd to acceptance
5. **Structured lifecycle**: draft → proposed → accepted/rejected → superseded

## Process

### Step 1: Gather Research
Take the output from the **ADR Researcher Skill** (if used) to understand:
- The problem space
- Alternatives considered
- Trade-offs and consequences
- Relevant standards and context

### Step 2: Map to Template
Think through how the research applies to each ADR section:
- What goes in Summary vs Context?
- What are the 3 most important problem impacts?
- What are the 3 most important solution impacts?
- What is the core Decision statement?
- What are the key Consequences?
- What are the top 2 Alternatives?

### Step 3: Write the ADR
Follow the template structure precisely. Keep to 2-3 pages.

### Step 4: Add Appendix
Include ASCII diagrams and SQL DDL in appendix (doesn't count toward word limit).

### Step 5: Validate Word Count
**CRITICAL**: After writing, use bash to count words:
```bash
awk '/^---$/,/^## Appendix:/{if(/^## Appendix:/)exit}1' <file> | wc -w
```
If over 900 words, immediately revise to condense.

## Template Structure

```markdown
# [Title of Decision]

**ADR**: [Date in YYYYMMDD format]-[Sequential number, e.g., 001]
**Authors**: @AuthorName
**Date**: [Full date]
**Status**: draft

---

# Summary

[2-3 paragraphs clearly stating the problem space, background context, and proposed direction. Keep it high-level but informative. Explain WHAT the decision is and WHY it matters. Assume reader has some context but may not know technical details.]

## Context

[Provide all necessary background that led to this ADR. Describe the ecosystem, current practices, relevant standards or constraints. Explain the landscape in which the decision is being made. Keep tone descriptive and factual.]

### Problem Statement

[Define the core problem in a focused, concrete way. Write as if explaining to someone technical who isn't deeply familiar with your system. Emphasize the key challenge this ADR resolves.]

### Problem Impact

[Why does the problem matter? Describe risks, limitations, or pain points caused by current approach or lack of one. Use circular bullets, max 3 items:]

• [Impact 1: Technical or operational consequence]
• [Impact 2: Risk or limitation]
• [Impact 3: Pain point or constraint]

### Solution

[Explain the proposed approach and how it solves the problem. Be specific about how it works and how it will be implemented. Avoid overly abstract descriptions. Use plain language. Include standards or protocols being adopted or extended.]

### Solution Impact

[How does the solution change the system's security posture, architecture, or development processes? Use circular bullets, max 3 items:]

• [Impact 1: Improvement or risk reduction]
• [Impact 2: Benefit or capability gained]
• [Impact 3: Long-term benefit or operational improvement]

## Decision

[Capture the formal choice being made. Explain WHAT will be done, HOW it will be enforced, and WHO is expected to follow this guidance. Reference related standards or practices. Provide precise expectations for implementers and consumers. This is the heart of the ADR - be precise and detailed but concise.]

## Consequences

[Highlight downstream effects, both positive and negative. Use **bolded** words with explanations. Keep very short.]

**[Positive consequence]**: [Brief explanation]
**[Negative consequence or trade-off]**: [Brief explanation]
**[New responsibility or requirement]**: [Brief explanation]

## Alternatives

[List other options considered and why they were not chosen. Describe merits and limitations. Max 2 alternatives. Use **bolded** words with explanations.]

**[Alternative 1 name]**: [Why it was considered, why it wasn't chosen, link to RFC/standard if applicable]

**[Alternative 2 name]**: [Why it was considered, why it wasn't chosen, link to RFC/standard if applicable]

---

## Appendix

[ASCII diagrams for clarity]

```
[Diagram 1]
```

[SQL DDL schemas if applicable]

```sql
-- Schema designs
```

[Sequence diagrams if applicable]

```
[Sequence diagram]
```
```

## Writing Guidelines

### DO:
- Write in full paragraphs for Summary, Context, Problem Statement, Solution, and Decision
- Use circular bullets (•) for Problem Impact and Solution Impact (max 3 each)
- Use **bolded** words with explanations for Consequences and Alternatives
- Be specific and concrete
- Use plain language
- Reference standards and protocols
- Include links to RFCs or related documents
- Keep Decision section very short but precise
- Keep Consequences list very short
- Include max 2 alternatives

### DON'T:
- Use rhetorical questions
- Create excessive subheaders beyond the template structure
- Include more than 3 bullets in Problem/Solution Impact
- Include more than 2 alternatives
- Add a Mitigations section
- Make Decision section too long
- Make Consequences list too long

## Word Count Management Strategy

### Target Word Counts by Section:
- **Summary**: 100-150 words
- **Context**: 100-150 words
- **Problem Statement**: 75-100 words
- **Problem Impact**: 30-50 words (3 bullets)
- **Solution**: 150-200 words
- **Solution Impact**: 30-50 words (3 bullets)
- **Decision**: 100-150 words (very concise but precise)
- **Consequences**: 50-75 words (very short)
- **Alternatives**: 100-150 words (max 2 alternatives)

**Total Target**: 750-900 words

### Condensing Strategies:
1. Remove redundant explanations
2. Combine related points
3. Use more concise language
4. Move technical details to appendix
5. Reduce alternatives from 3 to 2
6. Shorten Consequences list
7. Tighten Decision section

## Validation Process

After writing the ADR to disk, you MUST:

1. Run word count command:
```bash
awk '/^---$/,/^## Appendix:/{if(/^## Appendix:/)exit}1' <filepath> | wc -w
```

2. Report the actual word count to the user:
   - "ADR written successfully. Word count: [X]/900 words"

3. If word count exceeds 900:
   - "Word count exceeds limit: [X]/900 words. Revising to condense content..."
   - Immediately revise the document
   - Re-run word count validation
   - Repeat until under 900 words

## Output Format

When creating an ADR, generate this exact structure:

```markdown
# [Decision Title]

**ADR**: 20250130-001
**Authors**: @[Author]
**Date**: January 30, 2025
**Status**: draft

---

# Summary

[2-3 paragraphs]

## Context

[Background and landscape]

### Problem Statement

[Core problem definition]

### Problem Impact

• [Impact 1]
• [Impact 2]
• [Impact 3]

### Solution

[Proposed approach]

### Solution Impact

• [Impact 1]
• [Impact 2]
• [Impact 3]

## Decision

[Formal choice and expectations]

## Consequences

**[Consequence 1]**: [Explanation]
**[Consequence 2]**: [Explanation]
**[Consequence 3]**: [Explanation]

## Alternatives

**[Alternative 1]**: [Description and why not chosen]

**[Alternative 2]**: [Description and why not chosen]

---

## Appendix

[ASCII diagrams]

```
[Diagrams here]
```

[SQL DDL if applicable]

```sql
-- SQL here
```
```

## Your Approach

1. **Initialize tracking**: Create bd issues for each section
2. **Gather research**: Review any ADR Researcher output or user input
3. **Map content**: Think through how information applies to each section
4. **Write systematically**: Complete sections in order
5. **Monitor word count**: Track as you write
6. **Add appendix**: Move diagrams and SQL to appendix
7. **Validate word count**: Run bash command to verify < 900 words
8. **Revise if needed**: Condense if over limit
9. **Report**: Tell user final word count
10. **Update bd**: Mark all sections complete

## Example bd Workflow

```bash
# Initialize
bd create "ADR: Gather research and understand context" -t task -p 1
bd create "ADR: Write Summary section" -t task -p 1
bd create "ADR: Write Context section" -t task -p 1
bd create "ADR: Write Problem Statement" -t task -p 1
bd create "ADR: Write Problem Impact (3 bullets)" -t task -p 1
bd create "ADR: Write Solution" -t task -p 1
bd create "ADR: Write Solution Impact (3 bullets)" -t task -p 1
bd create "ADR: Write Decision section" -t task -p 1
bd create "ADR: Write Consequences (keep short)" -t task -p 1
bd create "ADR: Write Alternatives (max 2)" -t task -p 1
bd create "ADR: Create appendix with diagrams" -t task -p 1
bd create "ADR: Validate word count" -t task -p 0

# As you work
bd update [id] --status in_progress
bd update [id] --status done --reason "Section complete"

# After validation
bd update [validation-id] --status done --reason "Word count: 850/900 words"
```

## Status Lifecycle

- **draft**: Initial creation, work in progress
- **proposed**: Ready for review, seeking approval
- **accepted**: Decision approved and active
- **rejected**: Decision not adopted
- **superseded**: Replaced by newer ADR

## Critical Reminders

1. **Single decision per ADR**: Don't try to capture multiple decisions
2. **Immutability**: Once accepted, ADRs don't change - create new ones to supersede
3. **Evidence-based**: Always ground in context, not just opinion
4. **Word count validation**: ALWAYS run the bash command after writing
5. **Immediate revision**: If over 900 words, revise immediately before presenting to user
6. **Appendix doesn't count**: Liberally use appendix for diagrams and SQL
7. **Max 3 bullets**: Problem Impact and Solution Impact each get exactly 3
8. **Max 2 alternatives**: Never include more than 2 alternatives
9. **Keep Decision short**: Very concise but precise
10. **Keep Consequences short**: Very short list

## Pro Tips

1. **Start with research**: Use ADR Researcher Skill or gather context first
2. **Outline first**: Map content to sections before writing
3. **Write iteratively**: Draft, count, revise
4. **Use appendix**: Move all diagrams and SQL there
5. **Be ruthless**: Cut anything not essential to the decision
6. **Focus on why**: This is about rationale, not implementation
7. **Validate early**: Check word count after each major section
8. **Bold for scanning**: Use **bolded** words in Consequences and Alternatives for easy scanning

## Common Pitfalls to Avoid

- ❌ Including too many alternatives (max 2)
- ❌ Making Decision section too long (keep very short)
- ❌ Creating excessive subheaders
- ❌ Using rhetorical questions
- ❌ Forgetting to validate word count
- ❌ Not using appendix for diagrams/SQL
- ❌ More than 3 bullets in Impact sections
- ❌ Adding a Mitigations section
- ❌ Making Consequences list too long

Remember: ADRs are about capturing the **why** behind decisions in a concise, evidence-based way. Focus on the decision itself, not the implementation details. Keep it under 900 words and validate with bash.

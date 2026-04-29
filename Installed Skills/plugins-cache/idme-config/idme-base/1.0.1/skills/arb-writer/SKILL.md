---
name: arb-writer
description: Create Architecture Review Board (ARB) submissions under 900 words with required sections, SQL DDL, API specs, and comprehensive review checklist
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

# Architecture Review Board (ARB) Writer

## **CRITICAL CONSTRAINT**

The document MUST be under 900 words (excluding ASCII diagrams and SQL DDL). Put all ASCII diagrams and SQL DDL schemas in an Appendix section that doesn't count toward the word limit.

## Memory Management

Use the `bd` tool to track progress through the ARB document creation process. Create issues for each major section and track completion. Fall back to chromadb MCP server or standard Claude memory if `bd` is unavailable.

Example workflow:
```bash
bd create "ARB Doc: What/Why section" -t task -p 1
bd create "ARB Doc: Background section" -t task -p 1
bd create "ARB Doc: Data Structures in SQL" -t task -p 1
bd create "ARB Doc: API Spec" -t task -p 1
bd create "ARB Doc: Key Questions" -t task -p 1
```

## About ARB

The Architecture Review Board provides:
- Transparency around proposed changes and timing
- Adherence to best practices
- Alignment with future goals, not just feature goals
- Deep technical feedback from subject matter experts across the org

## When ARB Review Is Required

Review is REQUIRED for:
- Changes to foundational tech stack (new 3rd party software/services, new language)
- Changes requiring multiple teams to "do work"
- Any change to data models or data flows
- Anything that substantially changes user behavior
- **If in doubt, use ARB**

## Process Overview

### Step 0: Get an ARB Shepherd
You CANNOT proceed without a shepherd. Contact one of:
- Chris Wensel (chris.wensel@id.me)
- Hal Hildebrand (hal.hildebrand@id.me)
- Lee Horner (lee.horner@id.me)
- Scott Meyer (scott.meyer@id.me)
- Tanel Suurhans (tanel@id.me)

### Step 1: Sign Up
Contact Jennifer Varela (jennifer.varela@id.me) and add to the [calendar](https://docs.google.com/spreadsheets/d/1jSYCMzmwsMBhfwhP-L44rut2yj5sHTePIgjphKNFtrw/edit?gid=1006034087#gid=1006034087). Maximum 2 proposals per week.

### Step 2: Submit Pre-Read Materials
Materials must be submitted **at least 48 hours before** the review. Document should be 3-5 pages maximum with required sections.

## Your Task

Guide the user through creating the ARB document section by section. Track progress with `bd` tool. Continuously monitor word count and warn when approaching 900 words (excluding appendix content).

## Required Sections

### 1. What/Why - The Core Problem and Solution

Ask and document:
- **What is the problem?** (Be specific and concrete)
- **Why is this problem important to solve?** (Business impact, user impact, technical debt)
- **What is the solution?** (High-level approach)
- **What is the predicted impact?** (Measurable outcomes)

**Word count target**: 150-200 words

### 2. Background and Relationship to Other Work

Gather and cite:
- **Blake's vision**: How does this align? Link to relevant Blake communications
- **PRD reference**: Note any changes from the PRD
- **Related documents**: How does this differ from other related work?
- **Standards/conventions**: How does this relate to NIST, industry standards, etc.?
- **AI assistance**: Document where ChatGPT or AI was used to prepare/critique
  - Example prompts used
  - Link to conversations
  - The expectation is AI was used to accelerate and improve accuracy
- **Vocabulary consistency**: Use Secoda as source of truth for terminology

**Important**: Use ChatGPT to:
- Explain how to model concepts on the trust chain
- Show SQL implementations
- Describe use cases and data schemas
- Review best practices for security, API design, etc.
- Suggest diagrams for architecture and data flows

**Word count target**: 200-250 words

### 3. Data Structures in SQL

**IMPORTANT**: This goes in the APPENDIX (doesn't count toward 900 words)

Guide the user to:
- Write SQL DDL (CREATE TABLE, etc.) expressing key data structures
- Copy necessary parts of tables being modified
- Generate physical ERD from source code if needed
- Estimate data size and growth
- Write SQL DML (views) implementing key queries
- Create test data and "Evals" demonstrating correctness
- Check all SQL into [architecture-design](https://github.com/IDme/architecture-design) in sequentially numbered subdirectory

Key questions to address:
- How does this relate to the 4 primary nodes (people, organizations, places, things)?
- What structural compatibility are you exploiting?
- Is a logical ERD needed? (e.g., "person who is doctor" → "organization which is hospital")

### 4. API Spec

**Key principle**: All interfaces must be an API. No other data movement methods.

Document:
- **New APIs**: Describe and check in Swagger spec
- **API Council**: Must consult and get sign-off BEFORE ARB
  - Post in #api-council Slack channel
  - Complete API Council review process first
- **Dependencies**: What APIs are you dependent on? Do they exist?
- **AI-generated docs**: Use AI to write API spec documentation

**Word count target**: 150-200 words (spec details go in appendix)

### 5. Answer Key Questions

Address each of these:

1. **Completeness expectations**: What parts are "done forever" vs. tentative/incomplete?

2. **API longevity**: Is the API general and congruent with team charter? Anticipated future changes?

3. **Team dependencies**: What other teams must prioritize work for 100% completion?

4. **Scale-out expectations**:
   - Services are stateless and scale linearly (8 boxes = 2x QPS of 4 boxes)
   - Database writes are single-table transactions only
   - Database reads require eventual consistency only

**Word count target**: 150-200 words

### 6. Design Quality Checklist

Ensure the document includes:

- **Prioritization**: What are the THREE most important things to know?
- **Vision alignment**: How does this align to company vision?
- **Comprehensiveness**: Don't assume high context
- **Terminology accuracy**: Use most up-to-date industry standard definitions (check Secoda)
- **Security review**: If needed, request threat modeling via [established process](https://idmeinc.atlassian.net/wiki/spaces/APSEC/pages/2512158864/Threat+Modeling)

**Word count target**: 50-100 words

## Output Format

Generate a complete markdown document with this structure:

```markdown
# ARB Submission: [Project Name]

**Submitted by**: [Team/Name]
**Date**: [Current Date]
**ARB Shepherd**: [Shepherd Name]
**Scheduled Review**: [Date/Time]
**Status**: Draft

**Word Count**: [X]/900 words (excluding appendix)

---

## 1. What Are We Doing and Why?

### The Problem
[Specific, concrete problem description]

### Why This Matters
[Business/user/technical impact]

### The Solution
[High-level approach]

### Predicted Impact
[Measurable outcomes]

---

## 2. Background and Related Work

### Alignment with Blake's Vision
[How this aligns with company vision - cite specific communications]

### Product Requirements Document
**PRD Link**: [URL]
**Changes from PRD**: [Any deviations]

### Related Documents
- [Doc 1]: [How this differs]
- [Doc 2]: [How this differs]

### Standards and Conventions
**Relevant Standards**: [NIST 800-63-3, etc.]
[How design relates to standards]

### AI Assistance Used
**ChatGPT Conversations**: [Links to conversations]
**Key Questions Asked**:
- [Question 1]
- [Question 2]
- [Question 3]

**Secoda Terminology**: [Confirm usage of standard vocabulary]

---

## 3. Relationship to Trust Chain

[How this relates to the 4 primary nodes: people, organizations, places, things]

[What structural compatibility is being exploited]

[Logical ERD explanation if needed]

**Detailed SQL DDL**: See Appendix A
**SQL Views/Queries**: See Appendix B
**Test Data/Evals**: See Appendix C

**GitHub Repository**: [Link to architecture-design subdirectory]

---

## 4. API Specifications

### New APIs Introduced
[Description of new APIs]

**Swagger Spec**: See Appendix D (or link to GitHub)

### API Council Review
**Status**: [Completed/Scheduled]
**Outcome**: [Approved/Comments]
**Link**: [#api-council thread]

### API Dependencies
| Dependency API | Status | Owner Team |
|---------------|--------|------------|
| [API Name] | [Exists/Planned] | [Team] |

---

## 5. Key Architecture Questions

### Completeness Expectations
**Done Forever**:
- [Component 1]
- [Component 2]

**Tentative/Incomplete**:
- [Component 3]
- [Component 4]

### API Longevity and Generality
[Is API general? Congruent with team charter? Future changes anticipated?]

### Team Dependencies
**Teams Required for 100% Completion**:
- [Team 1]: [What work]
- [Team 2]: [What work]

### Scale-Out Design
- ✓ Services are stateless and scale linearly
- ✓ Database writes are single-table transactions only
- ✓ Database reads require eventual consistency only

[Details on how design meets each requirement]

---

## 6. Design Priorities and Alignment

### Three Most Important Things
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

### Company Vision Alignment
[How design aligns with and advances company vision]

### Security Review
**Threat Modeling**: [Completed/Scheduled/Not Required]
**Link**: [If applicable]

---

## Appendix A: SQL DDL (Data Structures)

**Data Size Estimates**: [Rows at launch, growth rate]

```sql
-- Core tables
CREATE TABLE [table_name] (
    -- DDL here
);

-- Modified tables (relevant parts)
CREATE TABLE [existing_table] (
    -- existing columns
    -- new columns
);
```

## Appendix B: SQL DML (Views and Queries)

```sql
-- Key views
CREATE VIEW [view_name] AS
SELECT ...;

-- Important queries
SELECT ...;
```

## Appendix C: Test Data and Evals

```sql
-- Test data
INSERT INTO [table] VALUES (...);

-- Eval queries demonstrating correctness
SELECT ... -- Expected result: [description]
```

## Appendix D: API Specifications

[ASCII diagrams of architecture]

```
[Architecture diagram]
```

[Swagger spec or detailed API documentation]

```yaml
openapi: 3.0.0
...
```

## Appendix E: Architecture Diagrams

```
[ASCII diagrams of data flows, system architecture, etc.]
```

---

## Submission Checklist

- [ ] ARB Shepherd assigned
- [ ] Scheduled on ARB calendar (via Jennifer Varela)
- [ ] Word count under 900 (excluding appendix): [X]/900
- [ ] All SQL checked into architecture-design repo
- [ ] API Council review completed (if applicable)
- [ ] Threat modeling completed (if applicable)
- [ ] All sections complete
- [ ] Submitted 48+ hours before review
- [ ] AI assistance documented
- [ ] Terminology verified against Secoda

```

## Your Approach

1. **Initialize tracking**: Create bd issues for each section
2. **Work section by section**: Don't overwhelm the user
3. **Monitor word count**: Continuously track and warn at 700, 800, 850 words
4. **Manage appendix**: Move SQL DDL, diagrams, and specs to appendix
5. **Verify completeness**: Check all required elements before finalizing
6. **Update bd issues**: Mark sections complete as you go
7. **Final review**: Ensure word count compliance and all checkboxes met

## Word Count Management Strategy

- Keep main sections concise and focused
- Use bullet points and tables for efficiency
- Move all technical details (SQL, API specs, diagrams) to appendix
- Continuously count words and alert user:
  - **700 words**: "Approaching limit, recommend being concise in remaining sections"
  - **800 words**: "Warning: Only 100 words remaining"
  - **850 words**: "Critical: Only 50 words remaining, prioritize essential content"

## Important Reminders

1. **SQL is communication**: Don't worry about efficiency or practicality. No commitment to use verbatim in product.
2. **API Council first**: Must get API Council approval BEFORE ARB review
3. **Use AI**: Expected to use ChatGPT/AI for acceleration and accuracy - document it!
4. **Check everything in**: SQL goes to architecture-design repo in numbered subdirectory
5. **48-hour rule**: Materials must be submitted 48+ hours before review
6. **Shepherd required**: Cannot proceed without a shepherd assigned

## Example bd Workflow

```bash
# Initialize
bd create "ARB: Get shepherd assigned" -t task -p 0
bd create "ARB: Schedule review session" -t task -p 0
bd create "ARB: Section 1 - What/Why" -t task -p 1
bd create "ARB: Section 2 - Background" -t task -p 1
bd create "ARB: Section 3 - SQL DDL" -t task -p 1
bd create "ARB: Section 4 - API Spec" -t task -p 1
bd create "ARB: Section 5 - Key Questions" -t task -p 1
bd create "ARB: Section 6 - Design Quality" -t task -p 1
bd create "ARB: Check SQL into repo" -t task -p 1
bd create "ARB: Word count verification" -t task -p 1
bd create "ARB: Final review and submission" -t task -p 1

# As you work
bd update [id] --status in_progress
bd update [id] --status done --reason "Section complete, 150 words"

# Track word count
bd create "Word count check" -t task -p 1 -d "Current: 650/900 words"
```

## Pro Tips

1. **Start with outline**: Get user agreement on structure before writing
2. **Use AI heavily**: Document all ChatGPT usage as required
3. **Secoda first**: Always check terminology against Secoda glossary
4. **API Council sync**: Coordinate timing so API Council completes before ARB
5. **Shepherd early**: Get shepherd involved early for guidance
6. **Appendix liberally**: When in doubt, move technical details to appendix
7. **Prioritize ruthlessly**: 900 words isn't much - focus on what matters most

Remember: The goal is to get multiple perspectives and ensure alignment with best practices and company vision. Be comprehensive but concise.

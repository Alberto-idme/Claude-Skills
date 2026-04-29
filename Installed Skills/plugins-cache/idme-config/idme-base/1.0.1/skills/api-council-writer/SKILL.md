---
name: api-council-writer
description: Create API Council submissions with customer problem description, system context maps, integration impact, alternatives, and API design summary
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

# API Council Document Writer

Leverage the `bd` tool to manage memory.

## About API Council

The API Council ensures system-wide thinking when building APIs. It prevents teams from painting themselves into corners, avoids baking business logic into application code that should be modular, ensures awareness of what other teams are building, maintains consistency in system integration, and identifies opportunities to reuse existing capabilities.

## Your Task

Guide the user through creating a complete API Council submission. Use the template below and help them fill in each section systematically.

## Process

1. **Understand the scope**: Ask clarifying questions about what they're building
2. **Gather information**: Work through each required section, asking specific questions
3. **Create artifacts**: Help generate the required diagrams and documentation
4. **Review completeness**: Ensure all sections are addressed before finalizing

## Required Sections

### 1. Customer Problem Description

Ask the user to describe:
- What customer problem are they solving?
- What does the current experience look like? (Request visuals/screenshots if available)
- What will the experience look like after this change?
- Who is the first customer? (Should always be ID.me flows, apps, or internal processes)

### 2. System Context Map

Help the user create a diagram showing:
- The new/changed API and behavior (and old API for comparison)
- What services/systems will call it
- What it calls or depends on
- Any data stores it touches
- Which teams own each dependency and their status (pending or completed)

Ask if they prefer to create this in: Lucidchart, Miro, draw.io, excalidraw, or a whiteboard photo.

### 3. Integration Impact Statement

Create a table or document listing:
- Which teams are affected by the changes
- What changes for them (new dependencies, breaking changes, new capabilities)
- Whether they've consulted with affected teams and what concerns were raised
- How they're addressing those concerns

### 4. Alternatives Considered

Document:
- What existing APIs, services, or patterns were evaluated
- Why they didn't meet the needs
- If extending existing vs. creating new, why that approach was chosen

This prevents duplicating existing capabilities.

### 5. API Design Summary

Guide them to post to: https://github.com/IDme/restful-api-schema

Include:
- Key endpoints/resources
- Payload examples and data model documentation
- Authentication/authorization approach

This should be enough for reviewers to understand system implications without implementation details.

## Review Process Reminder

Once complete, remind them to:
1. Post artifacts to **#api-council** Slack channel
2. Tag required reviewers:
   - Always: @Eric Karlinsky @Tanel Suurhans
   - If security/compliance: @Arnold Abernathy
   - Tag leads/architects for affected domains/teams
3. Wait for 48-hour review window
4. Outcomes:
   - ✅ Approved → Proceed
   - 💬 Comments → Address feedback
   - ⚠️ Discussion needed → Attend Thursday meeting

## When API Council Review Is Required

Council review is REQUIRED when:
- Creating a new API or service
- Changes affect multiple teams/services (breaking changes, new dependencies)
- Crossing domain boundaries
- Introducing new patterns or technologies
- Uncertain whether review is needed (when in doubt, bring it)

Council review is NOT required for:
- Internal changes to existing APIs that don't affect consumers (additive/backward compatible)
- Changes entirely within team's bounded context

## Output Format

Generate a complete markdown document with all sections filled in, using this structure:

```markdown
# API Council Submission: [Project Name]

**Submitted by**: [Team Name]
**Date**: [Current Date]
**Status**: Draft

---

## 1. Customer Problem Description

### Current State
[Description of current customer experience]

[Visuals/screenshots of current UX]

### Proposed State
[Description of improved customer experience]

[Visuals/mockups of new UX]

### First Customer
[Which ID.me flows, apps, or internal processes will use this first]

---

## 2. System Context Map

[Diagram or detailed description showing:
- New/changed API and behavior (+ old API for comparison)
- Calling services/systems
- Dependencies and data stores
- Team ownership and status]

**Tool used**: [Lucidchart/Miro/draw.io/excalidraw/other]
**Diagram link**: [URL]

---

## 3. Integration Impact Statement

| Affected Team | Impact Description | Consultation Status | Concerns Raised | Resolution |
|---------------|-------------------|---------------------|-----------------|------------|
| [Team name] | [What changes] | [Yes/No/Pending] | [Concerns] | [How addressed] |

---

## 4. Alternatives Considered

### Existing APIs/Services Evaluated

1. **[Option 1]**
   - Description: [What it is]
   - Why not suitable: [Reason]

2. **[Option 2]**
   - Description: [What it is]
   - Why not suitable: [Reason]

### Decision Rationale
[Why the chosen approach (extend existing vs. create new) was selected]

---

## 5. API Design Summary

**GitHub Schema Location**: https://github.com/IDme/restful-api-schema/[path-to-schema]

### Key Endpoints

#### [Endpoint 1]
- **Method**: [GET/POST/PUT/DELETE]
- **Path**: [/api/v1/resource]
- **Description**: [What it does]

#### [Endpoint 2]
- **Method**: [GET/POST/PUT/DELETE]
- **Path**: [/api/v1/resource]
- **Description**: [What it does]

### Payload Examples

```json
{
  "example": "request payload"
}
```

```json
{
  "example": "response payload"
}
```

### Data Model
[Brief description or diagram of key data entities]

### Authentication/Authorization
[Approach used: OAuth, JWT, API keys, etc.]

---

## Next Steps

- [ ] Post to #api-council Slack channel
- [ ] Tag required reviewers (@Eric Karlinsky @Tanel Suurhans + others as needed)
- [ ] Wait for 48-hour review window
- [ ] Address feedback or attend Thursday meeting if discussion requested

---

## Additional Context

[Any other relevant information, links to PRDs, design docs, etc.]
```

## Important Notes

- Keep the document concise but complete
- Focus on system implications, not implementation details
- Always demonstrate systems thinking
- Show how the work fits into the broader system
- Be clear about affected teams and consultation efforts
- Link to full specs/designs for reference rather than including everything

## Your Approach

1. Ask questions section by section
2. Don't overwhelm the user - work incrementally
3. If information is missing, help them identify who to consult
4. Offer to help create diagrams or tables
5. Review for completeness before finalizing
6. Ensure they understand the next steps for submission

Remember: The goal is alignment and quality, not slowing teams down. If they've done the work and there are no major concerns, they should move forward quickly.

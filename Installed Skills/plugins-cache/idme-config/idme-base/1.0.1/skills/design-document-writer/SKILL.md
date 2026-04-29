---
name: design-document-writer
description: Write technical design documents under 2500 words from PRDs or research documents, with comprehensive structure covering summary, scope, architecture, database schema, API specs, and key decisions
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

# Design Document Writer

**CRITICAL**: You MUST keep the document under 2500 words. ASCII diagrams and SQL schemas do not count towards the 2500 words.

Leverage the `bd` tool for memory management. Fall back to the chromadb mcp server or Claude.

## Instructions
1. Write a document based on the template below using the given PRD or research documents
2. Put all ASCII diagrams and SQL DDL schemas in an Appendix section

## Template for Writing Design Documents

Based on the Email Send API design document, here are detailed instructions for writing each section:

### Document Header

What to include:
- Authors: List all primary contributors
- Date: Document creation or last major update date
- Status: Current state (e.g., "Under Review", "Approved", "Draft", "Implemented")

How to write it:
Keep it simple and factual. This helps readers quickly understand who owns the document, when it was written, and whether it's still being refined.

---

### Summary

What to include:
- What the system does (1-2 sentences describing the core functionality)
- How it works (high-level approach in 1-2 sentences)
- Why it matters (2-4 bullet points covering business value, technical benefits, and strategic alignment)

How to write it:
Start with a clear statement of purpose. Then explain the approach in plain language—avoid jargon. End with the "so what?"—why should stakeholders
care? Focus on outcomes like consistency, reliability, visibility, and future readiness.

Example structure:
[System name] does [core function] by [high-level approach].

This design matters because it:
- Ensures [benefit 1]
- Provides [benefit 2]
- Gives [benefit 3]
- Is future-ready for [future capability]

---

### Scope

What to include:
- In Scope: Bulleted list of what this design covers
- Non-Scope (or "Out of Scope"): Bulleted list of what is explicitly excluded

How to write it:
Be specific and concrete. In-scope items should map directly to components, APIs, or features you'll describe later. Non-scope items prevent scope
creep and set clear boundaries—include related features that might be expected but aren't included.

Tips:
- Use parallel structure (all items start similarly)
- Group related items together
- For in-scope: mention specific APIs, database structures, integrations, workers, observability features
- For non-scope: mention related but excluded features, adjacent systems, advanced capabilities deferred to future phases

---

### Design Overview

#### System Overview

What to include:
- Architecture diagram (visual representation of components and data flow)
- Component descriptions (brief explanation of each major piece)
- High-level data flow (how requests move through the system)
- Design philosophy (2-3 sentences explaining the architectural approach and its alignment with existing systems)

How to write it:
Start with a diagram showing all major components and their relationships. Then walk through each component in the order data flows through them. Use
present tense and active voice. End with a paragraph that ties the architecture to broader system principles or existing patterns.

Example structure:
[Component 1] orchestrates [responsibility]
[Component 2] enqueues [what data]
[Component 3] consumes from [source], [processes], and [updates]
[Component 4] manages [responsibility]
[Database] is the system's source of truth for [data types]

The [system name] is designed as [architecture type] that [core purpose].
It introduces [key pattern] with [number] core layers: [layer 1] ([purpose]),
[layer 2] ([purpose]), and [layer 3] ([purpose]). This structure mirrors
[existing pattern], ensuring consistency with [related systems].

---

### DB Schema Overview

What to include:
- Summary of tables and their purposes
- Critical tables/columns explained in detail
- Relationships between tables (foreign keys)
- Reference to detailed schema (appendix or separate section)

How to write it:
List each table with a brief purpose statement, then detail the most important columns. Focus on:
- Primary keys and their significance
- Foreign key relationships
- Critical business logic columns
- Any non-obvious design choices (e.g., why a certain column exists)

Example format per table:
table_name: [One sentence purpose]
Columns: id (pk), foreign_key_id (fk→other_table.id), [key columns]
[Bullet points explaining critical columns or design decisions]

---

### Alignment with Existing Architecture

What to include:
- Table mapping existing concepts to your design
- Detailed explanations of how each architectural principle is satisfied
- Benefits of maintaining consistency

How to write it:
Create a comparison table showing how your design maps to existing patterns. Then expand on each row with:
1. The existing architecture's concept
2. How your design implements it
3. The benefit/outcome of this alignment

Table format:
| Existing Concept | Your Design Element | Purpose/Benefit |

Detailed format per concept:
**[Concept name]**
Existing approach: [How it works in current system]
Your design: [How you implement the same principle]
Outcome: [What this consistency achieves]

---

### API Specifications

What to include for each endpoint:
- API path and method
- Description (one sentence)
- Request type (content type)
- Request structure (format/standard used)
- Request body schema with data types and descriptions
- Success response with status code and body
- Error responses with status codes and descriptions

How to write it:
Use a structured format for clarity. Show actual JSON examples. For each field in the request/response, include:
- Field name
- Data type
- Whether required/optional
- Purpose or constraint
- Example value if helpful

Example format:
API: [METHOD] [path]
Description: [One sentence purpose]
Request Type: [Content-Type]
Request Payload: [Format description]

Request Body:
{
  "field_name": "TYPE (constraints)", // required/optional - purpose
  "another_field": "TYPE"             // description
}

Success Response - [status code]
{
  [response body]
}

Error Responses:
[status code] [name] — [when this occurs]
[status code] [name] — [when this occurs]

---

### Key Design Decisions

What to include:
- One section per major decision
- Background/Context explaining why the decision is needed
- Proposed solution with clear recommendation
- Alternatives considered in a comparison table
- Justification for the recommended approach

How to write it:
For each major design decision:

1. Background: Explain the problem or constraint (2-3 sentences)
2. Solution: State your recommendation clearly
3. Alternatives: Create a comparison table evaluating options across relevant dimensions
4. Recommendation: Restate your choice and list 3-5 concrete reasons why

Comparison table format:
| Aspect | Option A | Option B | Option C |
|--------|----------|----------|----------|
| [Criterion 1] | [Rating/description] | [Rating/description] | [Rating/description] |
| [Criterion 2] | [Rating/description] | [Rating/description] | [Rating/description] |

Selection criteria to consider:
- Durability/reliability
- Infrastructure requirements
- Setup complexity
- Performance/latency
- Scalability
- Operational cost
- Code changes needed
- Debugging/observability
- Transaction safety
- Best use case

Recommendation format:
**Recommendation: [Option name]**
- [Reason 1] - [brief explanation]
- [Reason 2] - [brief explanation]
- [Reason 3] - [brief explanation]

---

## General Writing Guidelines

1. Use present tense for describing the design ("The API handles...", not "The API will handle...")
2. Be specific: Use concrete examples, actual table names, real field names, specific technologies
3. Show, don't just tell: Include code snippets, JSON examples, SQL schemas, diagrams
4. Think in layers: Move from high-level (architecture) to mid-level (components) to detailed (schemas, APIs)
5. Maintain traceability: Scope items should map to Design Overview sections, which should map to API specs and schemas
6. Justify decisions: Every non-obvious choice should have a "why" explanation
7. Consider your audience: Balance technical detail with readability—include both summaries for executives and details for engineers
8. Use consistent terminology: Pick one term for each concept and stick with it throughout
9. Include appendices: Move detailed schemas, full API contracts, or extensive examples to appendices to keep the main document readable
10. Version thoughtfully: Update the date and status when making significant changes; consider keeping a changelog for living documents

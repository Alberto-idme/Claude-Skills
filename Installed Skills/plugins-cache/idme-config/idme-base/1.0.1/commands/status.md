---
description: Update RDR status through lifecycle transitions and manage related beads issues
---

# RDR Status Command

Update RDR lifecycle status, manage related beads issues, and maintain the RDR index.

## What This Command Does

Manages RDR status transitions through the lifecycle:
1. Update RDR metadata status field
2. Validate status transition is legal
3. Update doc/rdr/README.md index table
4. Close/update related beads issues based on status
5. Optionally archive completed RDRs

## Your Task

### 1. Parse Command

Determine what user wants to do:

```
/rdr:status doc/rdr/RDR-005-feature.md Implemented
/rdr:status RDR-005 Proposed
/rdr:status doc/rdr/RDR-010-*.md Superseded --reason "Replaced by RDR-015"
```

Extract:
- RDR file path or number
- New status
- Optional reason/comment

### 2. Validate Status Transition

Check current status and validate transition:

**Valid Status Values**:
- Recommendation (initial state)
- Draft (early development)
- Proposed (locked design, immutable)
- In Progress (being implemented)
- Implemented (complete)
- Superseded (replaced by newer RDR)

**Valid Transitions**:
```
Recommendation → Draft → Proposed → In Progress → Implemented
                                                    ↓
                                                Superseded ← (any status)
```

**Invalid Transitions** (warn user):
- Implemented → Draft (RDRs are immutable after implementation)
- Implemented → Proposed (can't go backward)
- Proposed → Recommendation (can't unlock)
- Draft → Implemented (must go through Proposed status)

If invalid transition:
```
❌ Invalid status transition for RDR-005

Current status: Implemented
Requested status: Draft

This transition is not allowed because:
- RDRs are immutable once Implemented
- Cannot revert to earlier lifecycle stages

Valid options:
1. Create new RDR and mark this as Superseded
2. Document changes in errata section (don't change status)

Suggested:
  /rdr:create RDR-015 "Updated approach based on RDR-005 learnings"
  /rdr:status RDR-005 Superseded --reason "Replaced by RDR-015"
```

### 3. Update RDR File

Modify the RDR file metadata section:

```markdown
## Metadata
- **Date**: [original date]
- **Status**: [NEW_STATUS]  ← Update this line
- **Type**: Feature
...
```

If status is Implemented, optionally add implementation date:
```markdown
- **Status**: Implemented
- **Implemented**: 2025-01-15
```

If status is Superseded, add reason:
```markdown
- **Status**: Superseded
- **Superseded By**: RDR-015
- **Reason**: [user-provided reason]
```

### 4. Update README.md Index

Update the index table in `doc/rdr/README.md`:

Find the row for this RDR:
```markdown
| 005 | [Semantic Search Implementation](RDR-005-semantic-search.md) | Draft    | High     |
```

Update status column:
```markdown
| 005 | [Semantic Search Implementation](RDR-005-semantic-search.md) | Implemented | High  |
```

If Superseded, add note:
```markdown
| 005 | [~~Semantic Search~~](RDR-005-semantic-search.md) | Superseded | High  |
```

### 5. Manage Related Beads Issues

Based on new status, take appropriate beads actions:

**Status: Proposed (Locked)**
- No beads action needed (ready for implementation)
- Suggest: `/rdr:implement doc/rdr/RDR-NNN-*.md`

**Status: In Progress**
- Verify beads epic exists (from `/rdr:implement`)
- Update epic status to "in_progress"
- Remind user to track progress in beads

**Status: Implemented**
- Find related beads issues (via external_ref or labels)
- Close all related tasks if all complete:
  ```bash
  bd close [task-id] --reason "RDR-005 implementation complete"
  ```
- If some tasks still open, warn user:
  ```
  ⚠️  Warning: 2 beads tasks still open for RDR-005
    - impl-459: Step 2: Implement query builder
    - test-462: Validation and testing

  Complete these tasks before marking RDR as Implemented, or close manually:
    bd close impl-459 --reason "Completed as part of final implementation"
  ```

**Status: Superseded**
- Find related beads issues
- Close all with reference to replacement RDR:
  ```bash
  bd close [task-id] --reason "Superseded by RDR-015"
  ```
- Update epic description with superseded notice

### 6. Optional: Archive Completed RDRs

If user requests archiving (`/rdr:status --archive`):
```bash
mkdir -p doc/rdr/archive
mv doc/rdr/RDR-005-feature.md doc/rdr/archive/
```

Update README.md to reflect archived location.

### 7. Display Status Update

Show confirmation of changes:
```
✅ RDR-005 Status Updated

Previous status: Draft
New status: Proposed

Changes made:
✓ Updated doc/rdr/RDR-005-semantic-search.md metadata
✓ Updated doc/rdr/README.md index
✓ Design is now locked (immutable)

Next steps:
1. Review design one final time
2. Create implementation tasks: /rdr:implement doc/rdr/RDR-005-semantic-search.md
3. Begin development following RDR as specification
```

## Batch Status Updates

Handle multiple RDRs at once:
```
/rdr:status doc/rdr/RDR-00{5,6,7}-*.md Implemented
```

Update each RDR, show summary:
```
✅ Batch Status Update Complete

Updated 3 RDRs to Implemented:
  ✓ RDR-005: Semantic Search
  ✓ RDR-006: Claude Integration
  ✓ RDR-007: Performance Optimization

Closed 12 beads tasks across all RDRs
Updated doc/rdr/README.md index
```

## Status Report Mode

If no status provided, show current status:
```
/rdr:status doc/rdr/RDR-005-feature.md
```

Display:
```
📋 RDR-005 Status Report

Title: Semantic Search Implementation
Current Status: In Progress
Priority: High
Type: Feature

Lifecycle:
  ✓ Recommendation (2025-01-10)
  ✓ Draft (2025-01-12)
  ✓ Proposed (2025-01-14) ← Design locked
  → In Progress (2025-01-15) ← Current
  ☐ Implemented
  ☐ Superseded

Related Beads Issues: 7 tasks
  ✓ Completed: 4
  → In Progress: 2
  ☐ Open: 1

Implementation Progress: 71% (5 of 7 tasks complete)

Next milestone: Complete remaining 2 tasks
Estimated completion: Based on task complexity
```

## Success Criteria

- Status updated in RDR file metadata
- Status transition validated
- README.md index updated
- Related beads issues managed appropriately
- Clear next steps provided
- No invalid state transitions allowed

## Usage Examples

```
# Update single RDR status
/rdr:status doc/rdr/RDR-005-feature.md Proposed

# Update by number
/rdr:status RDR-005 Implemented

# Mark as superseded with reason
/rdr:status RDR-005 Superseded --reason "Replaced by RDR-015 with improved approach"

# Batch update
/rdr:status doc/rdr/RDR-0{10,11,12}-*.md Implemented

# Check current status
/rdr:status RDR-005

# Archive after completion
/rdr:status RDR-005 Implemented --archive
```

## Integration with Beads

Uses beads MCP server to:
- Query issues via `external_ref` field matching RDR path
- Query issues via labels (e.g., "rdr-005")
- Close tasks when RDR is Implemented or Superseded
- Update epic status when RDR transitions

Gracefully handles missing beads integration (warns but continues).

## Notes

- Status transitions enforce RDR lifecycle discipline
- Immutability after "Proposed" prevents design drift
- Beads integration maintains traceability
- Archive option keeps doc/rdr/ focused on active RDRs
- Status report mode useful for checking progress

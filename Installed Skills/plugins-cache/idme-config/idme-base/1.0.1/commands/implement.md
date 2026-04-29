---
description: Spawn beads issues from locked RDR implementation plan with external_ref links and dependency tracking
---

# RDR Implement Command

Generate beads issues from a locked RDR (status: Proposed) to bridge planning to execution.

## What This Command Does

Parses a locked RDR and creates structured beads issues for implementation:
1. Create beads epic for the overall RDR
2. Parse Implementation Plan section for step-by-step tasks
3. Extract Prerequisites as blocking dependencies
4. Create beads task for each implementation step
5. Link all tasks to RDR via `external_ref` field
6. Set task dependencies based on Prerequisites section
7. Update RDR status to "In Progress"

## Your Task

### 1. Verify RDR is Ready

Check preconditions:
- RDR status must be "Proposed" (locked and immutable)
- Implementation Plan section must exist
- Implementation Plan must have Step-by-Step Implementation subsection

If not ready, provide feedback:
```
❌ RDR-005 cannot be implemented yet.

Current status: Draft
Required status: Proposed

Action needed:
1. Complete validation: /rdr:validate doc/rdr/RDR-005-feature.md
2. Lock design by updating status to "Proposed"
3. Then run: /rdr:implement doc/rdr/RDR-005-feature.md
```

### 2. Parse RDR Structure

Extract key information:
- RDR Number (e.g., 005 from RDR-005-semantic-search.md)
- Title from filename or H1 heading
- Priority from metadata
- Prerequisites from Implementation Plan section
- Steps from Step-by-Step Implementation section
- Files to Modify list
- Related Issues already listed in metadata

### 3. Create Beads Epic

```bash
# Create epic for the RDR
bd create "RDR-005: Semantic Search Implementation" \
  --type epic \
  --priority [from RDR metadata] \
  --description "Implementation of doc/rdr/RDR-005-semantic-search.md" \
  --external-ref "doc/rdr/RDR-005-semantic-search.md"
```

Capture epic ID for linking subtasks.

### 4. Create Prerequisite Tasks

For each item in Prerequisites section:
```bash
bd create "Prerequisite: [prerequisite description]" \
  --type task \
  --priority 0 \  # Highest priority for prereqs
  --assignee [from RDR or ask user] \
  --labels "rdr-005,prerequisite"
```

Capture prerequisite task IDs for dependency linking.

### 5. Create Implementation Step Tasks

For each step in Step-by-Step Implementation:
```bash
bd create "RDR-005 Step [N]: [step title]" \
  --type task \
  --priority [from RDR] \
  --description "[detailed instructions from step]" \
  --deps [prerequisite task IDs if step 1, previous step ID otherwise] \
  --labels "rdr-005,implementation" \
  --external-ref "doc/rdr/RDR-005-semantic-search.md#step-[N]"
```

### 6. Create File Modification Tasks (Optional)

If Files to Modify section has many files, create grouped tasks:
```bash
bd create "RDR-005: Modify core files" \
  --type task \
  --priority [from RDR] \
  --description "Modify:\n- path/to/file1.java\n- path/to/file2.java" \
  --deps [final implementation step ID] \
  --labels "rdr-005,files"
```

### 7. Create Testing Task

If Validation section exists:
```bash
bd create "RDR-005: Validation and testing" \
  --type task \
  --priority [from RDR] \
  --description "Test scenarios from RDR:\n[paste test scenarios]" \
  --deps [all implementation step IDs] \
  --labels "rdr-005,testing"
```

### 8. Link Epic to Subtasks

```bash
# Link all created tasks to epic
bd dep [epic-id] [prereq-task-1-id] --type parent-child
bd dep [epic-id] [impl-task-1-id] --type parent-child
bd dep [epic-id] [impl-task-2-id] --type parent-child
# ... for all tasks
```

### 9. Update RDR Status

Update RDR file metadata:
```markdown
- **Status**: In Progress
```

Update doc/rdr/README.md index table with new status.

### 10. Display Implementation Plan

Show created issues with dependencies:
```
✅ RDR-005 Implementation Plan Created

Epic: RDR-005: Semantic Search Implementation
      ID: epic-123
      External Ref: doc/rdr/RDR-005-semantic-search.md

Prerequisites (must complete first):
  ☐ prereq-456: Install ChromaDB dependencies
  ☐ prereq-457: Set up test environment

Implementation Steps:
  ☐ impl-458: Step 1: Create search interface
      Depends on: prereq-456, prereq-457

  ☐ impl-459: Step 2: Implement query builder
      Depends on: impl-458

  ☐ impl-460: Step 3: Add result formatting
      Depends on: impl-459

  ☐ impl-461: Step 4: Integration with CLI
      Depends on: impl-460

Testing:
  ☐ test-462: Validation and testing
      Depends on: impl-458, impl-459, impl-460, impl-461

Total: 7 tasks created
Next: bd list --label rdr-005

Start implementation:
1. Complete prerequisites first: bd show prereq-456
2. Then work through steps: bd show impl-458
3. Track progress: bd list --label rdr-005 --status in_progress
```

## Handling Edge Cases

### Partial Implementation

If user wants to implement only specific steps:
```
/rdr:implement doc/rdr/RDR-005-feature.md --steps 1,2,4
```

Create tasks only for specified steps, adjust dependencies accordingly.

### Reimplement After Changes

If RDR was already implemented but needs rework:
```
/rdr:implement doc/rdr/RDR-005-feature.md --force
```

- Check if beads issues already exist for this RDR
- Ask user if they want to:
  - Create new issues (default)
  - Reopen existing closed issues
  - Skip and show existing issues

### Link to Existing Issues

If user has already created some beads issues manually:
```
/rdr:implement doc/rdr/RDR-005-feature.md --link-to existing-123
```

Create remaining tasks and link all to specified epic.

## Success Criteria

- Beads epic created and linked to RDR via `external_ref`
- All prerequisite tasks created with priority 0
- All implementation step tasks created with dependencies
- Testing task created depending on all implementation steps
- RDR status updated to "In Progress"
- README.md index updated
- Clear next steps provided to user

## Usage Examples

```
# Standard implementation
/rdr:implement doc/rdr/RDR-005-semantic-search.md

# Partial implementation
/rdr:implement doc/rdr/RDR-005-semantic-search.md --steps 1,2,3

# Force reimplementation
/rdr:implement doc/rdr/RDR-005-semantic-search.md --force

# Link to existing epic
/rdr:implement doc/rdr/RDR-005-semantic-search.md --link-to epic-999
```

## Integration with Beads

This command heavily integrates with beads MCP server:
- Uses `mcp__plugin_beads_beads__create` to create issues
- Uses `mcp__plugin_beads_beads__dep` to set dependencies
- Uses `mcp__plugin_beads_beads__update` to modify existing issues
- Uses `mcp__plugin_beads_beads__list` to check for existing issues

Ensure beads is initialized in the project before running this command.

## Notes

- This command bridges RDR planning to actual execution
- Maintains traceability: each beads task links back to RDR
- Dependency tracking ensures proper implementation order
- Beads issues become the execution tracking mechanism
- RDR remains immutable specification during implementation

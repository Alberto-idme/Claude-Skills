---
description: Initialize RDR directory structure with README, TEMPLATE, and markdownlint configuration
---

# RDR Init Command

Initialize the `doc/rdr/` directory structure for Recommendation Data Records (RDRs) in the current project.

## What This Command Does

Creates a complete RDR directory structure with:
1. `doc/rdr/` directory
2. `README.md` with index table and RDR overview
3. `TEMPLATE.md` with complete RDR structure
4. `.markdownlint.json` with formatting rules

## Your Task

1. **Check if doc/rdr/ already exists**:
   - If it exists, ask user if they want to reinitialize (will preserve existing RDR files)
   - If new, proceed with setup

2. **Create directory structure**:
```bash
mkdir -p doc/rdr
```

3. **Create README.md**:
   - Include index table with columns: ID, Title, Status, Priority
   - Add "What are RDRs?" section explaining the concept
   - Add "When to Create an RDR" decision criteria
   - Add "RDR Workflow" summary
   - Link to TEMPLATE.md

4. **Create TEMPLATE.md**:
   - Copy complete template structure with all sections
   - Include inline guidance for each section
   - Show metadata format
   - Include appendix structure

5. **Create .markdownlint.json**:
```json
{
  "default": true,
  "MD013": false,
  "MD033": {
    "allowed_elements": ["details", "summary", "br"]
  },
  "MD041": false
}
```

## Success Criteria

Return a message confirming:
- Directory created at `doc/rdr/`
- Files created: README.md, TEMPLATE.md, .markdownlint.json
- Next steps: "Use the writer skill to create your first RDR"

## Example Output

```
✅ RDR directory initialized successfully!

Created:
- doc/rdr/README.md (index and overview)
- doc/rdr/TEMPLATE.md (RDR template structure)
- doc/rdr/.markdownlint.json (formatting rules)

Next steps:
1. Review doc/rdr/README.md to understand RDRs
2. Use the writer skill to create your first RDR
3. Example: "use writer skill to create rdr for [feature]"
```

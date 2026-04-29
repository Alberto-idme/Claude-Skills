---
description: Validate RDR files for formatting, consistency, and quality before locking as "Proposed"
---

# RDR Validate Command

Perform comprehensive validation checks on RDR files to ensure quality, consistency, and implementation readiness.

## What This Command Does

Runs 5-7 validation checks on RDR files:
1. **Format Compliance**: Markdown formatting via markdownlint
2. **Cross-RDR Consistency**: Check terminology and patterns across related RDRs
3. **Status Transitions**: Verify status changes are valid
4. **Word Count**: Warn if exceeds 2500 words (excluding appendix)
5. **Assertion Verification** (optional): Verify technical claims via web/code search
6. **Implementation Readiness**: Check for sufficient detail
7. **Metadata Completeness**: Ensure required fields present

## Your Task

### 1. Determine Scope
Ask user what to validate:
- Single RDR file: `/rdr:validate doc/rdr/RDR-005-feature.md`
- All RDRs: `/rdr:validate` or `/rdr:validate doc/rdr/`
- Specific set: `/rdr:validate doc/rdr/RDR-00{5,6,7}-*.md`

### 2. Run Format Check
```bash
# If markdownlint is available
npx markdownlint-cli2 doc/rdr/*.md

# Report any formatting issues with line numbers
```

### 3. Check Cross-RDR Consistency

For each RDR being validated:
- Extract key terms (technologies, patterns, approaches)
- Search other RDRs in `doc/rdr/` for same terms
- Flag inconsistencies:
  - Same technology with different versions
  - Conflicting architectural decisions
  - Inconsistent terminology (e.g., "collection" vs "corpus")
  - Duplicate implementations

Example check:
```bash
# Extract technologies mentioned
grep -E "(version|library|framework)" doc/rdr/RDR-*.md

# Look for conflicting decisions
grep -i "alternative.*rejected" doc/rdr/RDR-*.md
```

### 4. Verify Status Transitions

Check status field in metadata:
- Valid statuses: Recommendation | Draft | Proposed | In Progress | Implemented | Superseded
- Valid transitions:
  - Recommendation → Draft → Proposed → In Progress → Implemented
  - Any → Superseded (when replaced by newer RDR)
- Invalid transitions:
  - Implemented → Draft (RDRs are immutable once Implemented)
  - Proposed → Recommendation (can't un-lock)

### 5. Word Count Check

Count words excluding appendix:
```bash
# Count words up to "## Appendix" section
awk '/^## Appendix/,0 {next} {print}' doc/rdr/RDR-NNN-*.md | wc -w
```

Warnings:
- < 500 words: "RDR may lack sufficient detail"
- 500-2000 words: "Optimal word count"
- 2000-2500 words: "Consider moving details to appendix"
- \> 2500 words: "Warning: Exceeds recommended length. Move technical details to appendix."

### 6. Assertion Verification (Optional - Deep Check)

If user requests deep validation (`/rdr:validate --deep`):
- Extract technical assertions (version numbers, API signatures, performance claims)
- Verify via web search or code search
- Flag unverified or outdated claims

Example assertions to check:
- Library versions: "uses ChromaDB 1.2.0" → verify latest stable version
- API signatures: "calls `collection.add()`" → verify method exists
- Performance claims: "processes 1000 docs/sec" → ask for benchmark evidence

### 7. Implementation Readiness Check

For RDRs with status "Proposed":
- Verify Implementation Plan section exists and has steps
- Check Prerequisites section is complete
- Verify Files to Modify lists actual file paths
- Ensure Validation section has test scenarios

### 8. Metadata Completeness

Check required metadata fields:
- Date (YYYY-MM-DD format)
- Status (valid value)
- Type (Feature | Bug Fix | Technical Debt | Framework Workaround | Architecture)
- Priority (High | Medium | Low)
- Related Issues (can be empty but field should exist)

## Output Format

Provide structured validation report:

```
🔍 RDR Validation Report

Files validated: 3
✅ Passed: 2
⚠️  Warnings: 1
❌ Errors: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 doc/rdr/RDR-005-semantic-search.md
Status: Proposed | Words: 1,847 | Priority: High

✅ Format: Pass (markdownlint clean)
✅ Metadata: Complete
✅ Cross-RDR: Consistent with RDR-004, RDR-006
✅ Status transition: Valid (Draft → Proposed)
✅ Word count: Optimal (1,847 words)
✅ Implementation plan: Detailed and actionable

Ready for implementation ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 doc/rdr/RDR-006-claude-integration.md
Status: Draft | Words: 2,342 | Priority: High

✅ Format: Pass
✅ Metadata: Complete
⚠️  Cross-RDR: Uses "collection" vs "corpus" in RDR-005 (align terminology)
✅ Status transition: Valid
⚠️  Word count: 2,342 words (consider moving details to appendix)
❌ Implementation plan: Missing Prerequisites section

Action needed:
1. Align "collection" terminology with RDR-005
2. Move technical specifications to appendix to reduce word count
3. Add Prerequisites section to Implementation Plan

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
- 1 RDR ready for implementation (RDR-005)
- 1 RDR needs revision (RDR-006)
- Common issues: terminology consistency, word count management

Recommendations:
1. Run: align-terminology doc/rdr/ "collection"
2. Review RDR-006 and move technical specs to appendix
3. Complete Implementation Plan prerequisites
```

## Success Criteria

- Validation report generated for all requested RDRs
- Format issues identified with line numbers
- Cross-RDR inconsistencies flagged
- Word count warnings provided
- Clear action items listed for any issues found
- Ready/Not Ready determination for each RDR

## Usage Examples

```
# Validate single RDR
/rdr:validate doc/rdr/RDR-005-feature.md

# Validate all RDRs
/rdr:validate

# Deep validation with assertion checking
/rdr:validate --deep doc/rdr/RDR-010-performance.md

# Validate RDRs ready for implementation (status: Proposed)
/rdr:validate --status=Proposed
```

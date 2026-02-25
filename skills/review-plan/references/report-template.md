# Report Template

Output format for runbook review reports.

---

## Report Structure

```markdown
# Runbook Review: {name}

**Artifact**: [path]
**Date**: [ISO timestamp]
**Mode**: review + fix-all
**Phase types**: [TDD | General | Inline | Mixed (N TDD, M general, K inline)]

## Summary
- Total items: N (cycles: X, steps: Y)
- Issues found: N critical, N major, N minor
- Issues fixed: N
- Unfixable (escalation required): N
- Overall assessment: Ready | Needs Escalation

## Critical Issues

### Issue 1: [description]
**Location**: [cycle/step, line range]
**Problem**: [what's wrong]
**Fix**: [what was done]
**Status**: FIXED | UNFIXABLE (reason)

## Major Issues
[same format]

## Minor Issues
[same format]

## Fixes Applied
- [list of all fixes applied]

## Unfixable Issues (Escalation Required)
[numbered list with rationale, or "None — all issues fixed"]
```

## Report File Location

`plans/<feature-name>/reports/runbook-review.md` (or `phase-N-review.md` for phase files)

## Return Format

**On success (all issues fixed):**
```
plans/<feature>/reports/runbook-review.md
```

**On success with unfixable issues:**
```
plans/<feature>/reports/runbook-review.md
ESCALATION: 2 unfixable issues require attention (see report)
```

**On failure:**
```
Error: [What failed]
Details: [Error message]
Context: [What was being attempted]
Recommendation: [What to do]
```

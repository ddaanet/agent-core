---
name: review
description: Review in-progress changes for quality and correctness
allowed-tools: Read, Bash(git:*, diff:*)
user-invocable: true
---

# Review Changes for Quality

Review in-progress work for quality, correctness, and adherence to project standards. This skill examines uncommitted changes, recent commits, or partial branch work to identify issues and suggest improvements.

**Distinction:** This skill reviews work-in-progress. The built-in `/review` is for PR-focused reviews.

## Review Process

### 1. Determine Scope

**Ask user what to review:**

Use AskUserQuestion tool:

```
What should I review?

Options:
1. "Uncommitted changes" - Review git diff (staged + unstaged)
2. "Recent commits" - Review last N commits on current branch
3. "Current branch" - Review all commits since branched from main
4. "Specific files" - Review only specified files
5. "Everything" - Uncommitted + recent commits
6. "Design conformity" - Review changes against design document
```

**Common patterns:**
- After runbook execution: "Uncommitted changes"
- After series of commits: "Recent commits" (ask how many)
- Before creating PR: "Current branch"
- Targeted review: "Specific files"

### 2. Gather Changes

**For uncommitted changes:**
```bash
git status
git diff HEAD  # Shows both staged and unstaged
```

**For recent commits:**
```bash
git log -N --oneline  # List recent commits
git diff HEAD~N..HEAD  # Show changes in last N commits
git log -N -p  # Show commits with diffs
```

**For current branch:**
```bash
git log main..HEAD --oneline  # Commits on branch
git diff main...HEAD  # Changes since branch point
```

**For specific files:**
```bash
git diff HEAD <file1> <file2> ...
```

### 3. Analyze Changes

**Review axes:** Read `references/review-axes.md` for the full 10-category checklist (code quality, design conformity, functional completeness, project standards, runbook file references, self-referential modification, security, testing, documentation, completeness).

### 4. Provide Feedback

**Feedback structure:**

```markdown
# Review Report: [scope description]

**Scope**: [What was reviewed]
**Date**: [timestamp]

## Summary

[2-3 sentence overview of changes and overall assessment]

**Overall Assessment**: [Ready / Needs Minor Changes / Needs Significant Changes]

## Issues Found

### Critical Issues

[Issues that must be fixed before commit/merge]

1. **[Issue title]**
   - Location: [file:line or commit hash]
   - Problem: [What's wrong]
   - Fix: [What to do]

### Major Issues

[Issues that should be fixed, strongly recommended]

1. **[Issue title]**
   - Location: [file:line or commit hash]
   - Problem: [What's wrong]
   - Suggestion: [Recommended fix]

### Minor Issues

[Nice-to-have improvements, optional]

1. **[Issue title]**
   - Location: [file:line or commit hash]
   - Note: [Improvement idea]

## Positive Observations

[What was done well - be specific]

- [Good practice 1]
- [Good pattern 2]

## Recommendations

[High-level suggestions if applicable]

1. [Recommendation 1]
2. [Recommendation 2]

## Next Steps

[Clear action items]

1. [Action 1]
2. [Action 2]
```

**Assessment criteria:**

**Ready:**
- No critical issues
- Minor issues only or no issues
- Follows project standards
- Tests adequate
- Documentation complete

**Needs Minor Changes:**
- No critical issues
- 1-2 major issues
- Quick fixes needed
- Can proceed after addressing major issues

**Needs Significant Changes:**
- Critical issues present, or
- Multiple major issues, or
- Design problems requiring rework

### 5. Output Review

**Write review to file:**
- Path: `scratch/reviews/review-report-[timestamp].md` or
- Path: `plans/[plan-name]/reports/review-report.md` (if part of runbook)

**Return summary to user:**
- Overall assessment
- Count of issues (critical/major/minor)
- Key action items
- Path to full review

## Constraints

- **Bash** for git commands only, **Read** for examining files, **Write** for review output
- Do NOT use Edit to fix issues (review only)
- Review exactly what user requested — do not expand scope
- Be specific, actionable, constructive
- Flag secrets as CRITICAL — never log or output secret values

**Example execution:** Read `references/example-execution.md` for a complete review interaction flow.

**Common scenarios:** Read `references/common-scenarios.md` for handling secrets, multi-concern changes, pattern violations, already-committed work, and large changesets.

## Integration with General Workflow

**This skill is the protocol used by review/correction agents.** In workflow contexts, prefer agent delegation over direct skill invocation:

- `corrector` — review + apply fixes (Tier 3 orchestration)

**Direct `/review` invocation** is still valid when the user explicitly requests a review in conversation.

**Workflow stages:**
1. `/design` — Opus creates design document
2. `/runbook` — Sonnet creates runbook (per-phase typing: TDD + general)
3. `/orchestrate` — Executes runbook
4. corrector — Review and fix changes before commit
5. `/commit` — Commit changes
6. Complete job

## Execution Context for Review Delegations

When delegating to corrector, include scope context per `agent-core/fragments/review-requirement.md`:

**Required:** Scope IN, Scope OUT, Changed files, Requirements summary
**Optional:** Prior state, Design reference

See `agent-core/fragments/review-requirement.md` for full template and rationale.


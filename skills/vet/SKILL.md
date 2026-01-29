---
description: Review in-progress changes for quality and correctness
allowed-tools: Read, Bash(git:*, diff:*)
user-invocable: true
---

# Vet Skill

Review in-progress work for quality, correctness, and adherence to project standards. This skill examines uncommitted changes, recent commits, or partial branch work to identify issues and suggest improvements.

**Distinction:** This skill reviews work-in-progress. The built-in `/review` is for PR-focused reviews.

## When to Use

**Use this skill when:**
- Ready to review changes before committing
- Want to check recent commits for issues
- Need quality check on partial branch work
- Unsure if changes are ready for commit
- After completing runbook execution (oneshot workflow)

**Do NOT use when:**
- Reviewing a pull request (use built-in `/review`)
- Changes already committed and pushed
- Need code exploration (use explore agent)

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

**Review for:**

**Code Quality:**
- Logic correctness
- Edge case handling
- Error handling
- Code clarity and readability
- Appropriate abstractions (not over/under-engineered)

**Project Standards:**
- Follows existing patterns and conventions
- Consistent with codebase style
- Proper file locations
- Appropriate dependencies

**Security:**
- No hardcoded secrets or credentials
- Input validation where needed
- No obvious vulnerabilities
- Proper authentication/authorization

**Testing:**
- Tests included where appropriate
- Tests cover main cases
- Tests are clear and maintainable

**Documentation:**
- Code comments where logic isn't obvious
- Updated relevant documentation
- Clear commit messages (if reviewing commits)

**Completeness:**
- All TODOs addressed or documented
- No debug code left behind
- No commented-out code (unless explained)
- Related changes included

### 4. Provide Feedback

**Feedback structure:**

```markdown
# Vet Review: [scope description]

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
- Path: `scratch/reviews/vet-review-[timestamp].md` or
- Path: `plans/[plan-name]/reports/vet-review.md` (if part of runbook)

**Return summary to user:**
- Overall assessment
- Count of issues (critical/major/minor)
- Key action items
- Path to full review

## Critical Constraints

**Tool Usage:**
- Use **Bash** for git commands only
- Use **Read** for examining specific files
- Do NOT use Edit or Write to fix issues (review only)
- Output review to file with Write

**Scope:**
- Review exactly what user requested
- Don't expand scope without asking
- Focus on concrete issues, not abstract principles

**Tone:**
- Be specific and actionable
- Focus on "what" and "why", not just "this is wrong"
- Acknowledge good practices
- Be constructive, not critical

**Security:**
- Never log or output secrets/credentials
- Flag secrets immediately as critical issue
- Don't suggest specific values for secrets

## Example Execution

**User:** `/vet`

**Agent:** "What should I review?

1. Uncommitted changes
2. Recent commits
3. Current branch
4. Specific files
5. Everything"

**User:** "Uncommitted changes"

**Agent:** "Reviewing uncommitted changes...

*Runs git status and git diff HEAD*

Found changes in 5 files:
- agent-core/agents/quiet-task.md (new file)
- agent-core/bin/prepare-runbook.py (new file)
- CLAUDE.md (modified)
- plans/oneshot-workflow/design.md (modified)
- .claude/agents/unification-task.md (new file)

Analyzing changes...

*Reviews each file for quality, standards, security*

Review complete.

**Overall Assessment**: Ready

**Issues found:**
- Critical: 0
- Major: 0
- Minor: 2

Full review written to: scratch/reviews/vet-review-2026-01-19-142530.md

**Minor issues:**
1. prepare-runbook.py: Consider adding --help flag example to docstring
2. quiet-task.md: Typo in line 87 \"specificed\" → \"specified\"

**Recommendations:**
- All files follow project conventions
- Good documentation in script
- Comprehensive error handling

**Next steps:**
1. Fix minor typo if desired (optional)
2. Ready to commit"

## Common Scenarios

**Scenario: Review finds secrets in code**
- Mark as CRITICAL issue
- Don't show the secret value in review
- Recommend using environment variables or secure config
- Suggest tools like `git-secrets` if not already used

**Scenario: Changes span multiple concerns**
- Note in review if changes should be split into multiple commits
- Group issues by concern
- Suggest commit organization

**Scenario: Code works but doesn't follow project patterns**
- Mark as MAJOR issue if pattern is important
- Explain the project pattern
- Show example of correct pattern from codebase

**Scenario: Review requested for already-committed work**
- Still provide review
- Note in summary that changes are already committed
- Recommendations can be addressed in follow-up commit

**Scenario: Large changeset (1000+ lines)**
- Focus on high-level patterns and critical issues
- Don't nitpick every line
- Suggest breaking into smaller reviewable chunks if not committed yet

## Integration with Oneshot Workflow

**Workflow stages:**
1. `/design` - Opus creates design document
2. `/plan-adhoc` - Sonnet creates runbook
3. `/orchestrate` - Haiku executes runbook
4. `/vet` - Review changes before commit (THIS SKILL)
5. `/commit` - Commit changes
6. Complete job

**Typical invocation:**
After `/orchestrate` completes, user runs `/vet` to review all changes before committing.

**Handoff:**
- Input: Uncommitted changes from runbook execution
- Output: Review report with issues and recommendations
- Next: User fixes critical/major issues, then commits

## References

**Example reviews:**
- Look for patterns in existing PR reviews
- Check project conventions in CLAUDE.md
- Reference agents/design-decisions.md for architectural patterns

**Related skills:**
- Built-in `/review` - For PR reviews
- `/commit` - After vet review passes
- `/remember` - To document discovered patterns

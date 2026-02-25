# Progress Tracking

Track execution state during orchestration.

## Simple Approach
- Log each step completion to stdout
- Format: "check Step N: [step name] - completed"
- On error: "cross Step N: [step name] - failed: [error]"

## Detailed Approach (optional)
- Maintain progress file: `plans/<runbook-name>/progress.md`
- Update after each step with status and timestamp
- Include report file references

## Progress File Format

```markdown
# Runbook Execution Progress

**Runbook**: [name]
**Started**: [timestamp]
**Status**: [In Progress / Completed / Blocked]

## Step Execution

- check Step 1: [name] - Completed at [timestamp]
  - Report: plans/<runbook-name>/reports/step-1-execution.md
- check Step 2: [name] - Completed at [timestamp]
  - Report: plans/<runbook-name>/reports/step-2-execution.md
- cross Step 3: [name] - Failed at [timestamp]
  - Report: plans/<runbook-name>/reports/step-3-execution.md
  - Error: [brief error description]
  - Escalated to: [sonnet / user]

## Summary

Steps completed: 2/5
Steps failed: 1
Current status: Blocked on Step 3
```

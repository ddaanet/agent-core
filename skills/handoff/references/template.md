# Session Handoff Template

Use this structure when updating session.md for agent handoff:

```markdown
# Session Handoff: [Date]

**Status:** [Brief 1-line summary]

## Completed This Session

**[Category/Feature]:**
- Item with specifics (commit: abc123f, file: plans/x/report.md)
- Item with context (metrics, root cause, why decisions made)

**[Another Category]:**
- Item with traceability

## Pending Tasks

- [ ] **Task name** (PRIORITY)
  - Specific requirement or detail
  - Reference: file/path.md:line-numbers

- [ ] **Another task** (AFTER X)
  - Dependencies or prerequisites
  - Context needed for execution

## Blockers / Gotchas

**[Issue description]:**
- Root cause: [why it happened]
- Impact: [what's affected]
- Resolution: [how to fix or work around]

**Key learning:** [Important pattern or anti-pattern discovered]

## Next Steps

[1-2 sentences on immediate next action with file references]

---
*Handoff by [Model]. [Brief status note.]*
```

## Formatting Guidelines

**Use sub-headers to group related work:**
- Group completed work by feature/category
- Use bold headers for visual scanning
- Keep related bullets together

**Use sub-bullets for complex tasks:**
- Main bullet: Task name with priority
- Sub-bullets: Specific steps, file references, prerequisites
- Checkboxes `- [ ]` for pending tasks

## Retention Guidelines

**Completed tasks are trimmed on handoff if BOTH:**
1. From a previous conversation (not current)
2. AND already committed

**Always preserved:**
- Tasks completed in current conversation
- Uncommitted tasks from any conversation

**Note:** Learnings are written to separate `agents/learnings.md` file (not session.md)

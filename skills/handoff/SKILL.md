---
name: handoff
description: Update session.md with completed tasks, pending tasks, and blockers for agent handoff.
---

# Skill: handoff

Update session.md for agent handoff according to AGENTS.md protocol.

## Target Model
Haiku (simple file update)

## Protocol

When invoked, immediately update `session.md` with:

### 1. Gather Context
- Review conversation to identify completed tasks
- Identify any pending/remaining tasks
- Note any blockers or gotchas discovered

### 2. Update session.md

Write a concise handoff note with this structure:

```markdown
# Session Handoff: [Date]

**Status:** [Brief 1-line summary]

## Completed This Session
- [Task 1]
- [Task 2]
...

## Pending Tasks
- [Task 1] - [brief context if needed]
- [Task 2]
...

## Blockers / Gotchas
- [Any blockers or important notes for next agent]
- [None if no blockers]

## Next Steps
[1-2 lines on what the next agent should do first]
```

### 3. Size Discipline
- Keep session.md under ~100 lines
- If content would exceed, compact by summarizing (git history preserves details)
- Only preserve what the next agent needs to know

## Rules (from AGENTS.md)
- session.md is for current work state, NOT persistent documentation
- Focus on "what does the next agent need to know?"
- Be concise - completed work summarized in 1-2 lines, not full details
- Delete details after summarizing outcomes
- Git history is the archive - no separate archive files needed

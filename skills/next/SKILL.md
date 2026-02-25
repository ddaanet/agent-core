---
name: next
description: This skill should be used when the user asks "what's next?" or "any pending work?" and no pending work exists in already-loaded context. Checks secondary locations (shelf, todo.md, ROADMAP.md).
version: 0.1.0
---

# Find Pending Work

Check secondary locations (shelf, todo.md, ROADMAP.md) for pending work after confirming no work exists in primary context.

## How It Works

By the time this skill loads, the agent has already checked context (CLAUDE.md, session.md) and found no pending work. This skill checks additional locations:

### 1. Check agents/shelf/

List and read files in `agents/shelf/`:
- Look for frontmatter with `status: incomplete`
- Check "Pending Tasks" or "Next Steps" sections with actual work items (NOT "None")
- Report most recent incomplete shelved work

If actual pending work found: Report it and STOP.
If no pending work: Continue to step 2.

### 2. Check agents/todo.md

Read `agents/todo.md`:
- Look for actual items in "Backlog" section
- Check priority markers (High/Medium/Low)
- Report highest priority uncompleted items

If actual pending work found: Report it and STOP.
If no pending work: Continue to step 3.

### 3. Check agents/ROADMAP.md

Read `agents/ROADMAP.md`:
- Look for actual items marked "(Priority)"
- Report future enhancement ideas

If actual pending work found: Report it and STOP.
If no pending work: Continue to step 4.

### 4. No Work Found

If all checks complete with no pending work found:
- Report: "No pending work found. All tracked locations are clear."
- Suggest: "Ready for new tasks."

## Response Format

When pending work is found, provide:
- **Location**: Where the work was found
- **Summary**: Brief description of the work
- **Context**: Any relevant blockers or dependencies
- **Next action**: What should be done first

**Example response:**
```
Found pending work in agents/shelf/auth-refactor-session.md:

**Auth middleware migration** (status: incomplete):
- Convert session-based auth to JWT
- Update 3 route handlers

Next action: Resume auth refactor from shelved session.
```

## Constraints

- Stop once actual pending work is found ("None" or "No pending tasks" means continue checking)
- Report location where work was found
- Respect handoff warnings ("⚠️ STOP" → remind user explicit approval needed)
- Check order: shelf → todo → roadmap (session already checked by caller)

---
name: next
description: This skill should be used ONLY when the user asks "what's next?" and there is NO pending work in already-loaded context (CLAUDE.md, session.md). Check context first before loading this skill. If pending work exists in context, report it directly without invoking this skill.
version: 0.1.0
---

# Next Work Finder

This skill systematically checks for pending work across multiple project locations, stopping as soon as work is found.

## Purpose

Find pending work in secondary locations (shelf, todo.md, ROADMAP.md) after confirming no work exists in primary context (session.md, CLAUDE.md). This skill should only be invoked when context is empty.

## When to Use

**Check context first, THEN decide:**

1. User asks: "what's next?", "next?", "what should I work on?", "any pending work?"
2. Check already-loaded context (CLAUDE.md, session.md) for pending work
3. **If work found in context**: Report it directly, DO NOT load this skill
4. **If no work in context**: THEN invoke this skill to check other locations

## When NOT to Use

**Do NOT invoke this skill if:**
- Pending work exists in session.md (report it directly)
- In-progress tasks exist in context (report them directly)
- You can see specific tasks in already-loaded files (report them directly)

**The skill is for finding work in OTHER locations** (shelf, todo.md, ROADMAP.md) when context is empty.

## How It Works

**Important**: By the time this skill is loaded, the agent has already checked context (CLAUDE.md, session.md) and found no pending work. This skill checks additional locations:

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
Found pending work in agents/session.md:

**Pre-edit rule files** (3 files to create):
- .claude/rules/skill-development.md
- .claude/rules/hook-development.md
- .claude/rules/agent-development.md

Each ~10 lines with paths frontmatter and skill loading reminder.

Next action: Create the three rule files as specified in the designs.
```

## Important Notes

**Check context before loading**: Agent must check session.md BEFORE invoking this skill. Most sessions have pending work in context, so this skill should rarely be needed.

**Stop early**: Do not continue checking once actual pending work is found. "None", "No pending tasks", or "Ready for new work" are NOT pending work - continue checking when you see these. The goal is efficiency.

**Report location**: Always tell the user where the work was found so they understand the project's organization.

**Respect handoff warnings**: If session.md contains "⚠️ STOP: Do not execute tasks below unless user explicitly requests it", report the work but remind the user that explicit approval is needed.

**Prioritize correctly**: The check order reflects priority - active session work comes before shelved work, which comes before backlog items.

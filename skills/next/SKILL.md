---
name: next
description: This skill should be used when the user asks "what's next?", "next?", "what should I work on?", "any pending work?", or similar questions about what to do next. Provides a systematic check of all work tracking locations, stopping as soon as pending work is found.
version: 0.1.0
---

# Next Work Finder

This skill systematically checks for pending work across multiple project locations, stopping as soon as work is found.

## Purpose

Find the next pending work item by checking project tracking locations in order of priority. Most of the time, pending work exists in session.md, requiring zero tool calls.

## When to Use

Invoke this skill when the user asks about what to do next:
- "what's next?"
- "next?"
- "what should I work on?"
- "any pending work?"
- "what's the status?"

## How It Works

Check locations in order, stopping immediately when pending work is found:

### 1. Check Initial Context (Zero tool calls)

Look for pending work in files already loaded via @file directives (CLAUDE.md, session.md):
- Look for "Pending Tasks" sections with actual tasks (NOT "None" or "No pending tasks")
- Look for task list items marked `- [ ]` (pending) or `- [>]` (in-progress)
- Check "Next Steps", "Handoff", or "Ready for Implementation" sections with actual work items
- Check "Blockers" that might need attention

**What qualifies as pending work:**
- Specific tasks or work items listed
- In-progress tasks needing completion
- NOT: "None", "No pending tasks", "Ready for new work", or similar empty states

If actual pending work found: Report it and STOP.
If no pending work (empty/none): Continue to step 2.

### 2. Check agents/shelf/

List and read files in `agents/shelf/`:
- Look for frontmatter with `status: incomplete`
- Check "Pending Tasks" or "Next Steps" sections with actual work items (NOT "None")
- Report most recent incomplete shelved work

If actual pending work found: Report it and STOP.
If no pending work: Continue to step 3.

### 3. Check agents/todo.md

Read `agents/todo.md`:
- Look for actual items in "Backlog" section
- Check priority markers (High/Medium/Low)
- Report highest priority uncompleted items

If actual pending work found: Report it and STOP.
If no pending work: Continue to step 4.

### 4. Check agents/ROADMAP.md

Read `agents/ROADMAP.md`:
- Look for actual items marked "(Priority)"
- Report future enhancement ideas

If actual pending work found: Report it and STOP.
If no pending work: Continue to step 5.

### 5. No Work Found

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

**Stop early**: Do not continue checking once actual pending work is found. "None", "No pending tasks", or "Ready for new work" are NOT pending work - continue checking when you see these. The goal is efficiency.

**Zero tool calls when possible**: Most sessions have work in CLAUDE.md or session.md, which are loaded via @file directives. Check these first without any tool calls.

**Report location**: Always tell the user where the work was found so they understand the project's organization.

**Respect handoff warnings**: If session.md contains "⚠️ STOP: Do not execute tasks below unless user explicitly requests it", report the work but remind the user that explicit approval is needed.

**Prioritize correctly**: The check order reflects priority - active session work comes before shelved work, which comes before backlog items.

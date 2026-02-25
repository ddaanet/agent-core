---
name: handoff-haiku
description: Internal skill for Haiku model orchestrators only. Not for Sonnet or Opus — use /handoff instead. Mechanical session context preservation without learnings judgment.
user-invocable: false
---

# Haiku Orchestrator Handoff

Mechanical session handoff for Haiku models. Preserves context without judgment calls. For full handoff protocol with learnings processing, use `/handoff` skill (Sonnet/Opus).

**Target Model:** Haiku (mechanical preservation)

## Protocol

When invoked, update session.md mechanically:

### 1. Review Conversation
- Identify completed tasks (with commit hashes/file refs)
- Identify pending/remaining tasks
- Note any blockers or gotchas

### 2. Update session.md

**Merge rules — read current session.md first, then apply:**
- **REPLACE** these sections with fresh content: "Completed This Session", "Next Steps"
- **MERGE** these sections (carry forward unresolved items + add new): "Pending Tasks", "Blockers / Gotchas"
- **ADD** "Session Notes" section if new observations to record
- **PRESERVE UNCHANGED** all other existing sections (especially "Recent Learnings", "Reference Files", any "Prior Session" content)

**How to apply:**
1. Read current session.md
2. Update header (date, status line)
3. Replace sections listed under REPLACE with fresh content
4. For MERGE sections: preserve unresolved items from previous session, add new items, mark completed items with [x]
5. Add Session Notes section if new observations exist
6. Keep everything else exactly as-is

**MERGE semantics for Pending Tasks:**
- Review all pending tasks from previous session.md
- Keep all unresolved tasks (mark with [ ] or carry forward as-is)
- Add new pending tasks from current session
- Mark completed tasks with [x] if they were completed in current session

**Task metadata format:** Follow the format defined in `execute-rule.md` (always loaded). Preserve metadata format verbatim when carrying forward unresolved items.

**MERGE semantics for Blockers / Gotchas:**
- Review all blockers/gotchas from previous session.md
- Keep items that are still relevant (unresolved blockers, active gotchas)
- Add new blockers/gotchas discovered in current session
- Drop items that were resolved in current session (document resolution in Completed or Session Notes if significant)

**Template for sections being replaced/added:**

## Completed This Session
[Bullet list of completed work with commit hashes/file refs]

## Pending Tasks
[Bullet list with checkboxes]

## Session Notes
[Raw observations, discoveries, issues encountered - NO FILTERING]
[Preserve verbatim what happened, let standard model judge later]

## Blockers / Gotchas
[Any blockers or warnings for next agent]

## Next Steps
[Immediate next action]

**CRITICAL:** Do NOT delete existing sections not shown above. session.md may contain
sections from prior handoffs (Recent Learnings, Reference Files, etc.) that MUST be preserved.

### 3. Report Completion
Report line count: "Session handoff complete. [X] lines."

## Key Differences from Full Handoff

- **"Session Notes" not "Recent Learnings"** — no judgment about learnings, dump raw observations
- **No learnings staging** — do not call add-learning.py
- **No size advice** — report completion with line count only
- **Preserve everything mechanically** — commit hashes, file paths, line numbers, metrics. Do not filter or judge importance

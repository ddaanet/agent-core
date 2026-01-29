---
name: handoff-haiku
description: Internal skill for Haiku model orchestrators only. Not for Sonnet or Opus — use /handoff instead. Mechanical session context preservation without learnings judgment.
user-invocable: false
---

# Skill: handoff-haiku

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
- **REPLACE** these sections with fresh content: "Completed This Session", "Pending Tasks", "Blockers / Gotchas", "Next Steps"
- **ADD** "Session Notes" section if new observations to record
- **PRESERVE UNCHANGED** all other existing sections (especially "Recent Learnings", "Reference Files", any "Prior Session" content)

**How to apply:**
1. Read current session.md
2. Update header (date, status line)
3. Replace ONLY the sections listed under REPLACE with fresh content
4. Add Session Notes section if new observations exist
5. Keep everything else exactly as-is

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

**"Session Notes" not "Recent Learnings":**
- No judgment about what qualifies as a learning
- Dump raw observations for standard model to process later
- Preserve verbatim what happened

**No learnings staging:**
- Don't call add-learning.py
- Let standard model handle learnings judgment

**No size advice:**
- Just report completion with line count
- Let user decide on session continuity

## Principles

**Preserve everything mechanically:**
- Don't filter or judge importance
- Include specifics: commit hashes, file paths, line numbers, metrics
- Document what happened and why

**Trust the next agent:**
- Standard model will review Session Notes for learnings
- Standard model will decide on consolidation needs
- Preserve context completely without filtering

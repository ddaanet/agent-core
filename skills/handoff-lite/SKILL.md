---
name: handoff-lite
description: This skill should be used when efficient models (Haiku) need to "end session", "handoff", or "update session context" without learnings judgment. Mechanical preservation for quick orchestrator handoffs.
---

# Skill: handoff-lite

Mechanical session handoff for efficient models (Haiku). Preserves context without judgment calls. For full handoff protocol with learnings processing, use `/handoff` skill with Sonnet.

**Target Model:** Haiku (mechanical preservation)

## Protocol

When invoked, update session.md mechanically:

### 1. Review Conversation
- Identify completed tasks (with commit hashes/file refs)
- Identify pending/remaining tasks
- Note any blockers or gotchas

### 2. Write session.md
Use this embedded template:

```markdown
# Session Handoff: [DATE]

**Status**: [Brief status]

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

---
*Handoff by efficient model. Session notes preserved for learnings review.*
```

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

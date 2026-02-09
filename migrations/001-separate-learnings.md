# Migration 001: Separate Learnings from Session

**Date:** 2026-01-30
**Reason:** Agents delete learnings during handoff by conflating them with trimmable session content. Structural separation eliminates this failure mode.

## What Changed

- Learnings moved from `agents/session.md` to dedicated `agents/learnings.md`
- Handoff skill writes learnings to separate file, never trims them
- `/remember` skill consolidates old learnings into permanent docs
- Soft limit (80 lines) with user-directed consolidation guidance

## Migration Checklist

**Execution:** Project agents execute Steps 1-3 in project repo. Agent-core maintainers execute Step 4 in agent-core repo (can execute in parallel).

Execute project steps sequentially:

- [ ] **Step 1:** Create `agents/learnings.md` with standard header (see below) + extract existing learnings from `agents/session.md` (locate `## Recent Learnings` section, copy all learnings verbatim into new file after header)
- [ ] **Step 2:** Remove `## Recent Learnings` section from `agents/session.md`
- [ ] **Step 3:** Add `@agents/learnings.md` reference to project CLAUDE.md under `### Current Work` section

After completing project migration (steps 1-3):

- [ ] **Step 4:** Update handoff skill in agent-core repo - modify "Include Recent Learnings" section to append learnings to `agents/learnings.md` instead of `session.md`

## Verification Checklist

After completing all steps:

- [ ] `agents/learnings.md` exists with standard header
- [ ] `agents/learnings.md` contains all learnings from old `session.md`
- [ ] `agents/session.md` has no `## Recent Learnings` section
- [ ] CLAUDE.md `### Current Work` section includes `@agents/learnings.md` reference
- [ ] Handoff skill SKILL.md (agent-core repo) updated to write learnings to `agents/learnings.md`
- [ ] Git status shows 3 modified files + 1 new file in project repo (session.md, CLAUDE.md, learnings.md new); handoff skill modified in agent-core repo

## Standard Header for `agents/learnings.md`

```markdown
# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
```

## Notes

- Projects without existing learnings (no `## Recent Learnings` in session.md): create `agents/learnings.md` with header only
- Projects with learnings in other locations (e.g., CLAUDE.md inline): migrate those too
- Git history preserves old session.md content if needed for reference
- Step 4 modifies handoff skill behavior - after this migration, handoff will write learnings to separate file instead of inline in session.md

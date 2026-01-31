# Handoff Skill Learnings

Accumulated patterns and best practices for session handoff workflow.

## Handoff Must Preserve Design Decision Detail

**Anti-pattern:** Abbreviating design decisions during handoff, losing rationale.

**Correct pattern:** Write design decisions with rationale to learnings.md (staging for /remember).

**Rationale:** session.md allowed sections are limited (Completed, Pending, Blockers, References only). Design decisions don't fit these categories. learnings.md is staging area → /remember consolidates to permanent locations (fragments/, decisions/, skill references/).

**Impact:** Prevents loss of architectural context across sessions.

## Don't Track "Commit This" as Pending Task

**Anti-pattern:** `- [ ] Commit changes` in session.md pending tasks.

**Problem:** Commits don't update session.md, so task is never marked done.

**Correct pattern:** Commits happen organically; only track substantive work in pending tasks.

**Impact:** Cleaner pending task list, avoids stale "commit" tasks.

## Handoff-Haiku: MERGE Semantics for Pending/Blockers

**Anti-pattern:** REPLACE semantics for Pending Tasks and Blockers/Gotchas drops unresolved items from prior sessions.

**Root cause:** Haiku follows literal "replace with fresh content" instruction, doesn't infer "carry forward unresolved".

**Correct pattern:** MERGE semantics (carry forward unresolved + add new items).

**Implementation:** Updated handoff-haiku skill to explicitly merge Pending Tasks and Blockers/Gotchas sections.

**Impact:** Prevents loss of long-term pending work and active gotchas across handoffs.

# Design: Handoff Anti-Pattern Rules at Point of Violation

**Problem**: Agent violated "no commit tasks" rule despite it being documented in two places:
- learnings.md line 108-111
- handoff SKILL.md line 154

**Root cause**: Rule placement mismatch. The rule lives in Phase 6 (Trim Completed Tasks) — a section about *deleting old tasks*. The violation occurs in Phase 2/3 (writing Pending Tasks and Next Steps). The agent never mentally consulted Phase 6 while populating new content.

This is a **rule location** problem, not a **rule existence** problem.

## Analysis

### Current state

The handoff skill has two locations where content rules could live:

- **Phase 3 (Context Preservation)** — has "NEVER create other sections" and content guidelines for what to preserve/omit. This is where the agent looks when *writing* session.md sections.

- **Phase 6 (Trim Completed Tasks)** — has a "Do NOT list" block at lines 150-154 that includes the commit-task anti-pattern. This phase runs *after* the session is already written.

The agent follows phases sequentially. By the time it reaches Phase 6, the damage is done.

### Why it failed

Phase 3 guidance is entirely *positive* (what TO include). It lacks *negative* rules (what NOT to include). The "Do NOT list" in Phase 6 is a cleanup checklist, not a writing guideline.

Template (references/template.md) line 38-40 gives minimal guidance for Next Steps: `[1-2 sentences on immediate next action with file references]`. No constraints.

## Design

### Approach: Add anti-pattern block to Phase 3

Add a negative constraint block in Phase 3 (Context Preservation), after the "The goal: Complete context without bloat" summary (after line 67, before Phase 4). This places the constraint where the agent is actively making content decisions.

Use `**NEVER**` emphasis to match the existing strong-signal pattern at line 38 (`NEVER create other sections`).

Remove the commit-specific line from Phase 6 (line 154) to avoid rule scatter.

### Changes

**File: `skills/handoff/SKILL.md`**

**Addition** — In Phase 3, after line 67 ("Next agent should NOT need to..."), before Phase 4:

```markdown
**NEVER include in Pending Tasks or Next Steps:**
- Commit tasks ("commit changes", "commit fix") — commits don't update session.md, so task can never be marked done
- Obvious mechanical steps (restart, paste command) — only track substantive work
```

**Removal** — In Phase 6 "Do NOT list" block (lines 150-154), remove line 154:
```
- Create "commit this" or "commit changes" as a pending task (commits don't update session.md to mark done)
```

Lines 150-153 remain unchanged (they are trimming-specific rules):
```
- Create "Previous Session" headers
- Delete tasks completed in the current conversation
- Archive to separate files
```

### Scope

- **In scope**: Move the commit-task anti-pattern from Phase 6 to Phase 3
- **Out of scope**: Systematic extraction of all learnings.md rules into skills (that's `/remember`'s job)
- **Out of scope**: Adding validation scripts or hooks for handoff content

### Rationale for minimal approach

The broader problem (learnings.md rules not integrated into skills) is already addressed by the `/remember` consolidation workflow. This fix targets the specific high-frequency violation by placing the rule where it's consulted during writing.

Two items from the vet review draft were dropped:
- "Tasks already completed in this conversation" — overlaps with Phase 6 line 152 which handles *deleting* already-written completed tasks. Different semantic (don't write vs. delete after writing). Not adding a net-new rule here; Phase 6 already covers this.
- The broader "obvious mechanical steps" was kept but narrowed with examples for clarity.

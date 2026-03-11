---
name: handoff
description: Save session state for the next agent. Triggers on "handoff", "h", "hc", session update, or agent switch requests. Writes session.md with completed tasks, pending work, blockers, and learnings. Not for Haiku orchestrators — use /handoff-haiku instead.
allowed-tools: Read, Write, Edit, Bash(wc:*), Task, Skill
user-invocable: true
continuation:
  cooperative: true
  default-exit: []
---

# Update Session Context

Update session.md for agent handoff, preserving critical context for the next agent.

## Target Model

Standard (Sonnet)

**CRITICAL:** If you are a Haiku orchestrator, use `/handoff-haiku` instead.

## Protocol

### 1. Gather Context

- Review conversation for completed tasks, pending/remaining tasks, blockers
- If reviewing a handoff-haiku session, process Session Notes for learnings
- **Uncommitted prior handoff:** Read `agents/session.md`. If it contains a `# Session Handoff:` header with a date different from today, prior uncommitted handoff content exists — preserve as base state in Step 2

### 2. Update session.md

Write session.md following this structure:

```
# Session Handoff: [Date]

**Status:** [Brief 1-line summary]

## Completed This Session

**[Category/Feature]:**
- Item with specifics (file: path/to/report.md)
- Item with context (metrics, root cause, decisions)

## In-tree Tasks

- [ ] **Task name** — description | model
- [ ] **Another task** — description | model | restart

## Worktree Tasks

- [ ] **Task name** — description | model

## Blockers / Gotchas

**[Issue]:**
- Root cause, impact, resolution/workaround

## Next Steps

[1-2 sentences on immediate next action]

## Reference Files

- `path/to/file` — description
```

**Allowed sections only.** NEVER create "Learnings", "Key Decisions", or other sections. Learnings go to learnings.md.

**Carry-forward rule:** In-tree Tasks and Worktree Tasks are accumulated data. Read current sections, carry forward verbatim. Only mutate: mark completed `[x]`, mark blocked `[!]` with reason (see `task-failure-lifecycle.md`), mark failed `[†]` with error summary, mark canceled `[–]` with reason, append new tasks, update metadata changed this session. Do NOT rewrite, compress, or de-duplicate existing sub-items. Blocked/failed/canceled tasks persist across handoffs — do NOT trim them.

**Task classification (D-9):** When creating new tasks, classify into the correct section:
- **In-tree Tasks:** No plan directory, mechanical edits, no restart needed. Quick work done directly on current branch.
- **Worktree Tasks:** Has plan directory with behavioral changes, opus model tier, restart flag, or explicitly parallel scope. Tasks pre-classified as needing isolation.
- Default to In-tree when uncertain. Classification is static — set at creation, no moves between sections.

**Command derivation:** Run `Bash: claudeutils _worktree ls` to load current plan statuses. For tasks with a plan directory, derive the backtick command from the plan's lifecycle status:
- `requirements` → `/design plans/{name}/requirements.md`
- `outlined` → `/runbook plans/{name}/outline.md`
- `designed` → `/runbook plans/{name}/design.md`
- `planned` → `agent-core/bin/prepare-runbook.py plans/{name}`
- `ready` → `/orchestrate {name}`
- `review-pending` → `/deliverable-review plans/{name}`
- Unmapped statuses (`rework`, `reviewed`, `delivered`) → preserve existing command
- **Note override:** If existing command differs from derived AND task Note explains routing (e.g. "Route to /inline not /runbook"), preserve existing command

Non-plan tasks keep their static command. This prevents stale commands from persisting across handoffs.

**Multiple handoffs before commit:** Merge incrementally via Edit (append to Completed, mutate In-tree/Worktree, append Blockers, replace Next Steps). Do NOT Write a fresh file discarding prior content.

**NEVER reference commits as pending** in session.md — no "ready to commit" language.

**Worktree-terminal state:** If no `[ ]` pending tasks AND in a worktree (`git rev-parse --git-dir` ≠ `.git`), Next Steps = "Branch work complete." No merge-to-main instructions — the merge is tracked on main's session.md and performed from main.

**Haiku tasks** require execution criteria (acceptance criteria, test commands, or plan references):

```markdown
- [ ] **Enhance prepare-runbook.py** — Add phase file assembly | haiku
  - Accept directory input, detect runbook-phase-*.md files
  - Verify: `prepare-runbook.py plans/statusline-parity/` succeeds
```

Without criteria, haiku cannot verify alignment and quality surfaces only at commit time.

### 3. Context Preservation

**Target: 75-150 lines.**

**Preserve:** file paths, line numbers, metrics, root causes, failed approaches, decision rationale, rejected tradeoffs.

**No commit hashes in session.md.** They change on amend and rebase. Use file paths and plan names as stable references.

**Omit:** execution logs (git history), obvious outcomes, dead-end debugging, info already in referenced files.

**Discussion substance:** When a session included design debate or trade-off analysis, preserve conclusions and rejected alternatives — not the conversation flow.

### 4. Write Learnings

Append to `agents/learnings.md` (not session.md). Format: H2 title → Anti-pattern → Correct pattern → Rationale. No blank line after title.

**Title format (enforced by precommit):**
- Must start with `When ` or `How to `
- Min 2 content words after prefix
- Name after the activity at the decision point — not jargon or root-cause nouns
- Examples: ❌ "transformation table" → ✅ "When choosing review gate"; ❌ "prose gates" → ✅ "How to prevent skill steps from being skipped"

Titles become `/when` and `/how` triggers mechanically. Design decisions are learnings; learnings.md is a staging area for `/codify` consolidation.

**Append-only.** Never overwrite or trim.

### 4b. Check for Invalidated Learnings

**Trigger:** Session modified enforcement (validators, scripts) or behavioral rules (fragments, skills).

Review loaded learnings.md (already in memory — no Read needed). Remove any learning claiming something now false. Changes and cleanup must be atomic.

### 5. Update plan-archive.md

When a plan completed this session, append to `agents/plan-archive.md`: H2 heading + paragraph (2-4 sentences: deliverable, modules, decisions).

### 6. Trim Completed Tasks

Delete completed tasks only if BOTH: (1) completed before this conversation, AND (2) committed. Extract learnings before deleting.

Do NOT delete tasks completed in the current conversation, even if just committed.

### 7. Display STATUS

Display STATUS per execute-rule.md MODE 1.

## Continuation

Read continuation from `additionalContext` or `[CONTINUATION: ...]` suffix. If skill needs a subroutine: prepend entries (existing entries stay in original order — append-only invariant). Peel first entry from (possibly modified) continuation, tail-call: `Skill(skill: "<target>", args: "<target-args> [CONTINUATION: <remainder>]")`. If empty: stop.

Do NOT include continuation metadata in Task tool prompts.

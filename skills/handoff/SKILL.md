---
name: handoff
description: This skill should be used when the user asks to "handoff", "update session", "end session", or mentions switching agents. Updates session.md with completed tasks, pending work, blockers, and learnings for seamless agent continuation. NOT for Haiku model orchestrators - use /handoff-haiku instead.
allowed-tools: Read, Write, Edit, Bash(wc:*), Task, Skill
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/commit"]
---

# Update Session Context

Update session.md for agent handoff, preserving critical context for the next agent.

## Target Model

Standard (Sonnet)

**CRITICAL:** If you are a Haiku orchestrator, use `/handoff-haiku` instead.

## Flags

- `--commit` — After completing handoff, tail-call `/commit`.

**Flag parsing:** Flags are exact tokens, not substrings. `/handoff --commit` has the flag. `/handoff describe the commit process` does NOT.

## Protocol

### 1. Gather Context

- Review conversation for completed tasks, pending/remaining tasks, blockers
- If reviewing a handoff-haiku session, process Session Notes for learnings
- **Uncommitted prior handoff:** Read `agents/session.md`. If it contains prior uncommitted handoff content (`# Session Handoff:` header, Completed section, pending tasks not from this conversation), preserve as base state in Step 2

### 2. Update session.md

Write session.md following this structure:

```
# Session Handoff: [Date]

**Status:** [Brief 1-line summary]

## Completed This Session

**[Category/Feature]:**
- Item with specifics (commit: abc123f, file: path/to/report.md)
- Item with context (metrics, root cause, decisions)

## Pending Tasks

- [ ] **Task name** — description | model
- [ ] **Another task** — description | model | restart

## Worktree Tasks

- [ ] **Task name** → `<slug>` — description | model

## Blockers / Gotchas

**[Issue]:**
- Root cause, impact, resolution/workaround

## Next Steps

[1-2 sentences on immediate next action]

## Reference Files

- `path/to/file` — description
```

**Allowed sections only.** NEVER create "Learnings", "Key Decisions", or other sections. Learnings go to learnings.md.

**Carry-forward rule:** Pending Tasks and Worktree Tasks are accumulated data. Read current sections, carry forward verbatim. Only mutate: mark completed `[x]`, mark blocked `[!]` with reason (see `task-failure-lifecycle.md`), mark failed `[✗]` with error summary, mark canceled `[–]` with reason, append new tasks, update metadata changed this session. Do NOT rewrite, compress, or de-duplicate existing sub-items. Blocked/failed/canceled tasks persist across handoffs — do NOT trim them.

**Multiple handoffs before commit:** Merge incrementally via Edit (append to Completed, mutate Pending, append Blockers, replace Next Steps). Do NOT Write a fresh file discarding prior content.

**NEVER reference commits as pending** in session.md — no "ready to commit" language. With `--commit`, write status assuming commit succeeds.

**Haiku tasks** require execution criteria (acceptance criteria, test commands, or plan references):

```markdown
- [ ] **Enhance prepare-runbook.py** — Add phase file assembly | haiku
  - Accept directory input, detect runbook-phase-*.md files
  - Verify: `prepare-runbook.py plans/statusline-parity/` succeeds
```

Without criteria, haiku cannot verify alignment and quality surfaces only at commit time.

### 3. Context Preservation

**Target: 75-150 lines.**

**Preserve:** commit hashes, file paths, line numbers, metrics, root causes, failed approaches, decision rationale, rejected tradeoffs.

**Omit:** execution logs (git history), obvious outcomes, dead-end debugging, info already in referenced files.

**Discussion substance:** When a session included design debate or trade-off analysis, preserve conclusions and rejected alternatives — not the conversation flow.

### 4. Write Learnings

Append to `agents/learnings.md` (not session.md). Format: H2 title → Anti-pattern → Correct pattern → Rationale. No blank line after title.

**Title format (enforced by precommit):**
- Must start with `When ` or `How to `
- Min 2 content words after prefix
- Name after the activity at the decision point — not jargon or root-cause nouns
- Examples: ❌ "transformation table" → ✅ "When choosing review gate"; ❌ "prose gates" → ✅ "How to prevent skill steps from being skipped"

Titles become `/when` and `/how` triggers mechanically. Design decisions are learnings; learnings.md is a staging area for `/remember` consolidation.

**Append-only.** Never overwrite or trim.

### 4b. Check for Invalidated Learnings

**Trigger:** Session modified enforcement (validators, scripts) or behavioral rules (fragments, skills).

Review loaded learnings.md (already in memory — no Read needed). Remove any learning claiming something now false. Changes and cleanup must be atomic.

### 5. Update plan-archive.md

When a plan completed this session, append to `agents/plan-archive.md`: H2 heading + paragraph (2-4 sentences: deliverable, modules, decisions).

### 6. Trim Completed Tasks

Delete completed tasks only if BOTH: (1) completed before this conversation, AND (2) committed. Extract learnings before deleting.

Do NOT delete tasks completed in the current conversation, even if just committed.

### 7. Display STATUS (unless --commit)

**Without `--commit`:** Display STATUS per execute-rule.md MODE 1.

**With `--commit`:** Skip — `/commit` displays it after committing.

## Principles

- **session.md = working memory.** Next agent context without bloat. Specifics > logs.
- **learnings.md = semantic memory.** Anti-patterns, correct patterns. Append-only, consolidated via `/remember`.
- **git = archive.** Plan summaries → plan-archive.md. Commit history injected at session start.
- **Efficient-model review:** Process haiku Session Notes for learnings; apply judgment the efficient model skipped.

## Continuation

Read continuation from `additionalContext` or `[CONTINUATION: ...]` suffix. If empty: stop. Otherwise tail-call first entry: `Skill(skill: "<target>", args: "<target-args> [CONTINUATION: <remainder>]")`.

Do NOT include continuation metadata in Task tool prompts.

## Reference

- **`examples/good-handoff.md`** — Real-world best practice example
- **`references/learnings.md`** — Handoff-specific patterns and anti-patterns

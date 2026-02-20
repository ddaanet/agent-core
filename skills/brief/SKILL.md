---
name: brief
description: >-
  Transfer context (scope changes, decisions, conclusions) to a worktree task
  via plans/<plan>/brief.md. Triggers: "brief a worktree", "write a brief",
  "/brief <slug>", "transfer context to worktree".
allowed-tools:
  - Read
  - Write
  - Edit
user-invocable: true
---

# /brief — Cross-Tree Context Transfer

Write a context brief for a task in another worktree. Captures scope changes, design decisions, and discussion conclusions that the worktree agent needs before starting work.

## Usage

`/brief <slug-or-plan-name>`

## Process

1. **Resolve argument to plan directory.** Check `plans/<arg>/` exists. If not, match against worktree slugs in session.md Worktree Tasks section (`→ <slug>`) and derive the plan name from the task's metadata.

2. **Compose brief from conversation context.** Extract scope changes, design decisions, and discussion conclusions relevant to the target task. Dense, essential facts only — the consumer agent is intelligent.

3. **Append timestamped H2 entry to `plans/<plan>/brief.md`** (create file if needed). Do not overwrite existing content — briefs accumulate.

4. **No auto-commit.** The brief is included in the next `hc` cycle.

## Brief Format

```markdown
## YYYY-MM-DD: <topic summary>

<context — scope changes, decisions, conclusions>
```

## Consumer

Worktree agents read `plans/<plan>/brief.md` during task pickup (see execute-rule.md "Task Pickup" section). No manual action needed — the brief is automatically surfaced when the target task starts.

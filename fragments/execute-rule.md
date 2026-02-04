## Session Modes

Four session modes define agent behavior on startup or when prompted with workflow commands.

### MODE 1: STATUS (default)

**Triggers:**
- `#status` or `s`
- Ambiguous prompts: "next?", "what's next?", startup without explicit command
- Any prompt that doesn't clearly match EXECUTE or RESUME semantics

**Behavior:**
Display pending tasks with metadata, then wait for instruction.

**STATUS display format:**

```
Next: <first pending task name>
  `<command to start it>`
  Model: <recommended model> | Restart: <yes/no>

Pending:
- <task 2 name> (<model if non-default>)
  - Plan: <plan-directory> | Status: <status> | Notes: <notes>
- <task 3 name>
  - Plan: <plan-directory> | Status: <status>
- ...

Unscheduled Plans:
- <plan-name> — <status>
- ...
```

**Pending list format:**
- First line: task name with model if non-default
- Nested line: plan directory, status from jobs.md, notes if present
- Omit nested line if task has no associated plan

**Unscheduled Plans:** Plans in jobs.md that have no associated pending task.
- Read `agents/jobs.md` for all plans
- Exclude plans that appear in any pending task's plan directory
- **Format:** `<plan-name> — <status>`
- **Status values:** `complete`, `planned`, `designed`, `requirements`
- **Sorting:** Alphabetical by plan name

**Status source:** Read `agents/jobs.md` as authoritative source for plan status and notes.

**Special handling for `plans/claude/`:**
- List individual `.md` files within `plans/claude/` as separate entries
- **Format:** `claude/<filename> — plan` (without .md extension)
- Excludes `.gitkeep` and other non-plan files
- These are Claude Code built-in plan mode files

**Graceful degradation:**
- Missing session.md or no Pending Tasks → "No pending tasks."
- Old format (no metadata) → use defaults (sonnet, no restart)
- No unscheduled plans → omit Unscheduled Plans section entirely

### MODE 2: EXECUTE

**Triggers:**
- `#execute` or `x`

**Behavior:**
Smart execute: resume in-progress task if exists, otherwise start first pending task. Drive to completion, then stop.

### MODE 3: EXECUTE+COMMIT

**Triggers:**
- `#execute --commit` or `xc`

**Behavior:**
Execute task to completion, then chain:
1. `/handoff` updates session.md
2. Tail-calls `/commit` which commits changes
3. `/commit` displays STATUS showing next pending task

### MODE 4: RESUME

**Triggers:**
- `#resume` or `r`

**Behavior:**
Strict resume: continue in-progress task only. Error if no in-progress task exists.

### Task Pickup: Context Recovery

**Rule:** Before starting a pending task, run `agent-core/bin/task-context.sh '<task-name>'` to recover the session.md where it was introduced.

The task name serves as the lookup key. The script uses `git log -S` to find the commit where the task was first introduced and outputs the full session.md from that commit.

---

## `x` vs `r` Behavior Matrix

| State | `x` (#execute) | `r` (#resume) |
|-------|----------------|---------------|
| In-progress task exists | Resume it | Resume it |
| No in-progress, pending exists | Start first pending | Error: "Nothing in progress" |
| No tasks | "No pending tasks" | Error: "Nothing in progress" |

**When to use:**
- `x` — General-purpose "do the next thing"
- `r` — Strict resume-only (prefer error over accidentally starting new work)

---

## Shortcut Vocabulary

### Tier 1 - Commands (exact match)

| Shortcut | Expansion | Semantics |
|----------|-----------|-----------|
| `s` | #status | List tasks with metadata, wait |
| `x` | #execute | Smart: resume OR start pending |
| `xc` | #execute --commit | Execute → handoff → commit → status |
| `r` | #resume | Strict: resume only (error if none) |
| `h` | /handoff | Update session.md → status |
| `hc` | /handoff --commit | Handoff → commit → status |
| `ci` | /commit | Commit → status |
| `?` | #help | List shortcuts, keywords, entry skills |

### Tier 2 - Directives (colon prefix)

| Shortcut | Semantics |
|----------|-----------|
| `d: <text>` | Discussion mode — analyze, don't execute |
| `p: <text>` | Pending task — append to session.md, don't execute |

---

## Task Status Notation

**In session.md:**
- `- [ ]` = Pending task
- `- [x]` = Completed task
- `- [>]` = In-progress task (optional, or use bold/italics)

**Task metadata format:**

```markdown
- [ ] **Task Name** — `command` | model | restart?
```

**Examples:**
```markdown
- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` | sonnet
- [ ] **Design runbook identifiers** — `/design plans/runbook-identifiers/problem.md` | opus | restart
```

**Field rules:**
- Task Name: Prose key serving as identifier (must be unique across session.md and disjoint from learning keys)
- Command: Backtick-wrapped command to start the task
- Model: `haiku`, `sonnet`, or `opus` (default: sonnet if omitted)
- Restart: Optional flag — only include if restart needed (omit = no restart)

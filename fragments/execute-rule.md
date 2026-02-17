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

Worktree:
- <task name> → <slug>
- <task name 2> → <slug2>

Unscheduled Plans:
- <plan-name> — <status>
- ...
```

**Pending list format:**
- First line: task name with model if non-default
- Nested line: plan directory, status from jobs.md, notes if present
- Omit nested line if task has no associated plan

**Worktree section:**
- Only shown when worktree tasks exist in session.md
- Tasks in Worktree section are NOT shown in Pending
- Format shows task name and worktree slug for `wt-rm` reference

**Unscheduled Plans:** Plans in jobs.md that have no associated pending task.
- Read `agents/jobs.md` for all plans
- Exclude plans that appear in any pending task's plan directory
- **Format:** `<plan-name> — <status>`
- **Status values:** `complete`, `planned`, `designed`, `requirements`
- **Sorting:** Alphabetical by plan name

**Status source:** Read `agents/jobs.md` as authoritative source for plan status and notes.

**Parallel task detection:**

After listing pending tasks, analyze for parallelizable groups:
- No shared plan directory between tasks
- No logical dependency (check Blockers/Gotchas section)
- Compatible model tier (all sonnet, or all same)
- No restart requirement

If a group of 2+ independent tasks exists, append:

```
Parallel (N tasks, independent):
  - task name 1
  - task name 2
  `wt` to set up worktrees
```

Show largest independent group only. Omit section if no parallelism detected.

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

### MODE 5: WORKTREE SETUP

**Triggers:**
- `wt` (no args) — set up parallel group
- `wt <task-name>` — branch off single named task

**Behavior:**
Set up worktrees for parallel or single-task execution. See `agent-core/skills/worktree/SKILL.md` for implementation details.

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

Shortcuts are mechanical expansions — invoke the expansion directly. Do not pre-evaluate whether the expansion has work to do.

| Shortcut | Expansion | Semantics |
|----------|-----------|-----------|
| `s` | #status | List tasks with metadata, wait |
| `x` | #execute | Smart: resume OR start pending |
| `xc` | #execute --commit | Execute → handoff → commit → status |
| `r` | #resume | Strict: resume only (error if none) |
| `h` | /handoff | Update session.md → status |
| `hc` | /handoff --commit | Handoff → commit → status |
| `ci` | /commit | Commit → status |
| `wt` | #worktree | Set up worktrees for parallel tasks |
| `?` | #help | List shortcuts, keywords, entry skills |

### Tier 2 - Directives (colon prefix)

| Shortcut | Semantics |
|----------|-----------|
| `d: <text>` | Discussion mode — analyze, don't execute |
| `p: <text>` | Pending task — assess model, defer write to handoff |
| `learn: <text>` | Add to session learnings (agents/learnings.md) |
| `q: <text>` | Quick question — terse response, no ceremony |

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
- [ ] **Implement ambient awareness** — `/runbook plans/ambient-awareness/design.md` | sonnet
- [ ] **Design runbook identifiers** — `/design plans/runbook-identifiers/problem.md` | opus | restart
```

**Field rules:**
- Task Name: Prose key serving as identifier (must be unique across session.md and disjoint from learning keys)
- Command: Backtick-wrapped command to start the task
- Model: `haiku`, `sonnet`, or `opus` (default: sonnet if omitted)
- Restart: Optional flag — only include if restart needed (omit = no restart)

**Worktree Tasks section:**

Tasks branched off to worktrees move from Pending Tasks to Worktree Tasks:

```markdown
## Worktree Tasks

- [ ] **Task Name** → `<slug>` — original metadata
```

**Rules:**
- Tasks move from Pending Tasks to Worktree Tasks when `wt` creates their worktree
- `→ <slug>` tracks which worktree holds the task
- After merge + `wt-rm`, remove the task from Worktree Tasks (move to Completed or delete)
- Handoff preserves Worktree Tasks section as-is (not trimmed)

**Restart triggers:** Session restart is required for structural changes that load at startup:
- Sub-agent definitions (`.claude/agents/`)
- Hook configuration (`.claude/hooks/`, `settings.json` hooks)
- Plugin changes (`.claude/plugins/`)
- MCP server configuration (`.mcp.json`)
- API/provider configuration

**NOT restart triggers:** Model changes (use `/model` command at runtime)

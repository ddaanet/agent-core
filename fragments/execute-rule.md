## Session Modes

Four session modes define agent behavior on startup or when prompted with workflow commands.

### MODE 1: STATUS (default)

**Triggers:**
- `#status` or `s`
- Ambiguous prompts: "next?", "what's next?", startup without explicit command
- Any prompt that doesn't clearly match EXECUTE or RESUME semantics

**Behavior:**
Display pending tasks with metadata, then wait for instruction.

**Rendering:** Output `Status.` as final line — Stop hook renders via `_status` CLI.

**Planstate-derived commands:**
- For tasks with an associated plan directory, derive the command from planstate (shown in CLI output as `→ <command>`)
- Use the CLI-derived command instead of the static session.md command
- Session.md command is fallback only for tasks without plans

**Session continuation:**
- Shown only when git tree is dirty (uncommitted changes from skill execution or manual edits)
- Shows the natural next steps: `` `/handoff`, `/commit` ``
- If any plan-associated task has status `review-pending`, append: `` `/deliverable-review plans/<name>` ``
- Omit entirely when tree is clean

**Next task when in-tree blocked:**
When all in-tree tasks are blocked and the first actionable work is a worktree task, "Next" should point to worktree setup (`wt <task-name>` or `wt` for parallel group), not the worktree task's execution command. The execution command belongs inside the worktree session.

**Graceful degradation:**
- Missing session.md or no In-tree Tasks → "No in-tree tasks." In a worktree (`git rev-parse --git-dir` ≠ `.git`), append: "Branch complete."
- Old format (no metadata) → use defaults (sonnet, no restart)
- Old section name ("Pending Tasks") → treat as "In-tree Tasks"
- No unscheduled plans → omit Unscheduled Plans section entirely

### MODE 2: EXECUTE

**Triggers:**
- `#execute` or `x`

**Behavior:**
Smart execute: resume in-progress task if exists, otherwise start first in-tree task. Invoke the task's backtick command — via Skill tool for `/skill` commands, or Bash for script commands. Do not reinterpret the command or implement the work directly. Skips blocked (`[!]`), failed (`[†]`), and canceled (`[-]`) tasks. Worktree tasks require `wt` setup — `x` does not pick them up. Drive to completion, then stop.

### MODE 3: EXECUTE+COMMIT

**Triggers:**
- `#execute --commit` or `xc`

**Behavior:**
Execute task to completion, then chain:
1. `/handoff` updates session.md
2. Tail-calls `/commit` which commits changes
3. `/commit` outputs `Status.`

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

**Brief check:** If the task has an associated plan directory, check for `plans/<plan>/brief.md`. If it exists, read it — contains cross-tree context (scope changes, decisions) from other sessions. In worktrees where the plan directory only exists on main: `git show main:plans/<plan>/brief.md 2>/dev/null`.

---

## `x` vs `r` Behavior Matrix

| State | `x` (#execute) | `r` (#resume) |
|-------|----------------|---------------|
| In-progress task exists | Resume it | Resume it |
| No in-progress, in-tree exists | Start first in-tree | Error: "Nothing in progress" |
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
| `hc` | /handoff, /commit | Handoff → commit → status |
| `ci` | /commit | Commit → status |
| `wt` | #worktree | Set up worktrees for parallel tasks |
| `?` | #help | List shortcuts, keywords, entry skills |

### Tier 2 - Directives (colon prefix)

| Shortcut | Semantics |
|----------|-----------|
| `d: <text>` | Discussion mode — analyze, don't execute |
| `bd: <text>` | Brainstorm divergence — generate 3+ framings (one must reframe problem, not vary solution) then `d:` core protocol |
| `p: <text>` | Pending task — assess model, defer write to handoff |
| `learn: <text>` | Add to session learnings (agents/learnings.md) |
| `q: <text>` | Quick question — terse response, no ceremony |

---

## Task Status Notation

**In session.md:**
- `- [ ]` = Pending task
- `- [x]` = Completed task
- `- [>]` = In-progress task (optional, or use bold/italics)
- `- [!]` = Blocked (waiting on signal — see `task-failure-lifecycle.md`)
- `- [†]` = Failed (terminal, system-detected — requires user decision)
- `- [-]` = Canceled (terminal, user-initiated)

**Task metadata format:**

```markdown
- [ ] **Task Name** — `command` | model | restart?
```

**Examples:**
```markdown
- [ ] **Implement ambient awareness** — `/runbook plans/ambient-awareness/design.md` | sonnet
- [ ] **Design runbook identifiers** — `/design plans/runbook-identifiers/brief.md` | opus | restart
```

**Field rules:**
- Task Name: Prose key serving as identifier (must be unique across session.md and disjoint from learning keys)
- Command: Backtick-wrapped command to start the task
- Model: `haiku`, `sonnet`, or `opus` (default: sonnet if omitted)
- Restart: Optional flag — only include if restart needed (omit = no restart)

**Plan-backed tasks (mandatory):**

Every pending task must reference a plan directory (`plans/<slug>/`) containing at least one artifact: requirements.md, brief.md, or design.md. Inline-described tasks are forbidden — inline descriptions lack context, references, and produce results that miss unstated requirements.

Task commands must include a plan path argument (e.g., `/design plans/foo/requirements.md`, not bare `/design`). The plan path is the validator's primary extraction source.

Applies to: `p:` directive (must create plan artifact before or during handoff), `/handoff` (must not write tasks without plan backing).

**Discussion conclusions must survive session boundaries.** When `d:` mode decisions or agreed refinements produce pending work, capture conclusions as task notes in session.md. The handoff is the recovery mechanism — if it's not in session.md, it doesn't survive. `task-context.sh` recovers the introducing commit, but only if the handoff captured the context.

**Worktree Tasks section:**

Tasks pre-classified as needing worktree isolation. Classification is static — set at creation by handoff or `p:` directive. No move semantics between sections.

```markdown
## Worktree Tasks

- [ ] **Task Name** — metadata (not yet dispatched)
- [ ] **Task Name** → `<slug>` — metadata (active worktree)
```

**Rules:**
- Tasks placed in Worktree Tasks at creation based on classification heuristic (D-9)
- `→ <slug>` added by `_worktree new [TASK_NAME]` when worktree created, removed by `_worktree rm`
- `#status` annotates with `→ slug` from `_worktree ls` (filesystem state, not session.md)
- `x` does not pick up worktree tasks — use `wt` to dispatch
- Handoff preserves Worktree Tasks section as-is (not trimmed)
- Main is worktree-tasks-only — only trivial fixes belong in In-tree. Plan absence does not qualify for in-tree

**Worktree-tasks-only scope:** This rule governs task classification (pending tasks in session.md), not interactive skill execution. Maintenance skills (`/codify`, `/commit`, `/handoff`) run on main regardless.

**Restart triggers:** Session restart is required for structural changes that load at startup:
- Sub-agent definitions (`.claude/agents/`)
- Hook configuration (`.claude/hooks/`, `settings.json` hooks)
- Plugin changes (`.claude/plugins/`)
- MCP server configuration (`.mcp.json`)
- API/provider configuration

**NOT restart triggers:** Model changes (use `/model` command at runtime)

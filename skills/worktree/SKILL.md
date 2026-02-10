---
name: worktree
description: >-
  This skill should be used when the user asks to "create a worktree",
  "set up parallel work", "merge a worktree", "branch off a task",
  or uses the `wt` shortcut. Handles worktree lifecycle: creation with
  focused sessions, merge with ceremony, and parallel task setup.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(claudeutils _worktree:*)
  - Bash(just precommit)
  - Bash(git status:*)
  - Bash(git worktree:*)
  - Skill
user-invocable: true
continuation:
  cooperative: true
  default-exit: []
---

# Worktree Skill

Manage git worktree lifecycle for parallel task execution and focused work.

## Mode A: Single Task

Used when the user specifies a single task name: `wt <task-name>`. This mode branches off one task from the main session to a dedicated worktree, enabling focused work in isolation.

1. **Read `agents/session.md`** to locate the task by name in the Pending Tasks section. Extract the full task block including name, command, model, and any metadata (continuation lines).

2. **Derive slug** from the task name using deterministic transformation: lowercase, replace spaces with hyphens, remove special characters, truncate to 30 characters maximum. Examples: "Implement foo bar" → "implement-foo-bar", "Task: X/Y" → "task-x-y". The slug serves as the worktree directory name and must be unique within the repository.

3. **Generate focused session.md content** with minimal scope. Create a session file containing only the selected task's metadata and blockers/references relevant to that task. The focused session acts as the worktree-local view of work: same format as main session.md but filtered to single task.

4. **Write to `tmp/wt-<slug>-session.md`** using the generated focused session content. Template structure:

       # Session: Worktree — <task name>

       **Status:** Focused worktree for parallel execution.

       ## Pending Tasks

       - [ ] **<task name>** — <full metadata from original>

       ## Blockers / Gotchas

       <only blockers relevant to this task>

       ## Reference Files

       <only references relevant to this task>

5. **Invoke: `claudeutils _worktree new <slug> --session tmp/wt-<slug>-session.md`** to create the git worktree with its own branch and initialize the focused session context. This command handles branch naming, worktree setup, and session.md placement.

6. **Edit `agents/session.md`** to move the task from Pending Tasks to Worktree Tasks section. Locate the task in Pending Tasks, extract the full task block (including continuation lines with indented metadata), create a Worktree Tasks section if it doesn't exist, and append the task with the marker `→ wt/<slug>` indicating which worktree contains it. Example:

       ## Worktree Tasks

       - [ ] **Task Name** → `wt/task-slug` — `command` | model

7. **Print launch command** for the user: `cd wt/<slug> && claude    # <task name>`. This tells the user how to enter the worktree and start the task in a new Claude Code session.

## Mode B: Parallel Group

## Mode C: Merge Ceremony

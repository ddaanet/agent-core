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

Used when the user invokes `wt` with no arguments. This mode detects a group of independent parallel tasks and creates multiple worktrees simultaneously, enabling concurrent work on independent tasks.

1. **Read `agents/session.md` and `agents/jobs.md`** to identify all pending tasks and their properties. Extract task names, plan directories, model tiers, restart flags, and any blockers that might create dependencies.

2. **Analyze Pending Tasks for parallel group candidates.** Examine each pending task to determine which tasks can run in parallel. Apply these criteria to identify an independent group:

   - **Plan directory independence:** Examine each pending task's plan directory (if specified). Tasks with different plan directories OR no plan directory specified are potentially independent. Tasks with no plan property are independent from each other. A task without a plan and another task with a plan share no dependency. Skip tasks that belong to the same plan directory.

   - **Logical dependencies:** Check the Blockers/Gotchas section for mentions of other tasks. If Task B's blockers mention Task A, they cannot run parallel. Similarly, examine the Pending Tasks section for explicit ordering hints (e.g., "Task X blocks Task Y"). Build a dependency graph and exclude tasks that depend on each other.

   - **Model tier compatibility:** Verify model tiers match for all tasks in the candidate group. Tasks requiring different model tiers (e.g., one haiku and one opus) cannot be batched together. Tasks with no model specified default to sonnet. A valid group has all tasks with the same tier OR all tasks without a specified tier (defaulting to sonnet).

   - **Restart requirement check:** Examine the restart flag for each task. Any task marked with "Restart: yes" cannot be batched with others. Tasks must all have restart=no (or no restart flag) to be grouped.

   Select the **largest independent group** that satisfies all four criteria. If multiple groups of different sizes exist, prefer the larger group (e.g., batch 3 tasks over batching 2 if both groups are valid).

3. **If no parallel group found** (all tasks have dependencies, different tiers, or restart requirements), output the message: "No independent parallel group detected. All pending tasks have dependencies or incompatible requirements." Stop execution. Do not create any worktrees.

4. **If group found, for each task in the parallel group, execute Mode A steps 2-7.** Derive slug, generate focused session, write to tmp, invoke CLI creation, edit session.md to move task to Worktree Tasks, and print launch command. Process tasks sequentially within this loop (one task at a time, in order).

5. **Print consolidated launch commands** after all worktrees are created:

       Worktrees ready:
         cd wt/<slug1> && claude    # <task name 1>
         cd wt/<slug2> && claude    # <task name 2>
         ...

       After each completes: `hc` to handoff+commit, then return here.
       Merge back: `wt merge <slug>` (uses skill)

## Mode C: Merge Ceremony

Used when the user invokes `wt merge <slug>`. This mode orchestrates the merge ceremony that returns worktree commits to the main branch, handling the handoff, commit, merge, and cleanup sequence.

1. **Read `agents/session.md`** to verify current session state. Then **invoke `/handoff --commit`** to ensure clean tree and session context committed. This ceremony step is mandatory: merge operations require a clean working tree, and handoff ensures that `agents/session.md` and related context files reflect the current state and are committed as a sync point. If handoff or commit fails, STOP. Merge requires clean tree. Resolve handoff/commit issues before retrying merge.

2. **Use Bash to invoke: `claudeutils _worktree merge <slug>`** to perform the three-phase merge: submodule resolution, parent repo merge, and precommit validation. The tool call captures exit code and stderr automatically.

3. **Exit code 0 (success):** The merge completed successfully. Use Edit tool on `agents/session.md`: Remove task from Worktree Tasks section. If Worktree Tasks section is missing, note that no cleanup is needed (task may have been removed already). Locate the line matching the pattern `→ wt/<slug>` marker and remove the entire task entry (and any continuation lines). Then use Bash to invoke: `claudeutils _worktree rm <slug>` to clean up the worktree branch and directory. Output: "Merged and cleaned up wt/<slug>. Task complete."

4. **Exit code 1 (conflicts or precommit failure):** The merge encountered conflicts or failed precommit validation. Read stderr from the merge command and parse for conflict indicators or precommit failure messages.

   - **If conflicts:** List the conflicted files. Note that session files (`agents/session.md`, `agents/learnings.md`, `agents/jobs.md`) should resolve automatically using deterministic strategies — report as a bug if these files appear in the conflict list. For source files: resolve manually (edit to fix conflicts), stage with `git add`, then re-run `claudeutils _worktree merge <slug>` (merge is idempotent and can resume after resolution).

   - **If precommit failure:** Show which checks failed. Explain that the merge commit already exists (do not re-merge). Fix the reported issues in the working tree, stage the fixes with `git add`, amend the merge commit with `git commit --amend --no-edit`, verify with `just precommit`, and then re-run `claudeutils _worktree merge <slug>` to continue cleanup.

5. **Exit code 2 (error):** Output: "Merge error: " followed by the stderr content from the failed command. Generic error handling: review the error output and resolve before retrying.

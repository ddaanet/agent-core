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

Used when user specifies `wt <task-name>`.

1. **Read `agents/session.md`** to locate task in Pending Tasks. Extract full task block including name, command, model, and metadata.

2. **Invoke: `claudeutils _worktree new --task "<task name>"`** to create the worktree with focused session. The command derives the slug, generates a focused session.md (filtered to just this task's context), creates the worktree in the sibling container, and cleans up temp files. Output is tab-separated: `<slug>\t<path>`.

3. **Parse output** to extract slug and worktree path from the tab-separated line.

4. **Edit `agents/session.md`** to move the task from Pending Tasks to Worktree Tasks section. Locate the task in Pending Tasks, extract the full task block (including continuation lines with indented metadata), create a Worktree Tasks section if it doesn't exist, and append the task with the marker `→ <slug>` indicating which worktree contains it. Example:

       ## Worktree Tasks

       - [ ] **Task Name** → `task-slug` — `command` | model

5. **Output launch command** using the path from step 3: `cd <path> && claude    # <task name>`.

## Mode B: Parallel Group

Used when the user invokes `wt` with no arguments. This mode detects a group of independent parallel tasks and creates multiple worktrees simultaneously, enabling concurrent work on independent tasks.

1. **Read `agents/session.md` and `agents/jobs.md`** to identify all pending tasks and their properties. Extract task names, plan directories, model tiers, restart flags, and any blockers that might create dependencies.

2. **Check for shared plan directories and dependencies.** For each pending task, extract the plan directory (if specified). Build a dependency map:

   - **Plan directory independence:** Tasks with different plan directories OR no plan directory can run parallel. Tasks with no plan property are independent from each other. Skip any task that shares a plan directory with another.

   - **Logical dependencies:** Scan the Blockers/Gotchas section for mentions of other tasks. If Task B's blockers mention Task A, exclude both from parallel group. Check Pending Tasks section for explicit ordering hints (e.g., "Task X blocks Task Y").

   - **Model tier compatibility:** Extract model tier for each candidate task (haiku/sonnet/opus, default sonnet). All tasks in the group must have the same tier.

   - **Restart requirement check:** Check restart flag for each task. Any task marked "Restart: yes" disqualifies from parallel grouping.

   Select the **largest independent group** satisfying all four criteria. If multiple group sizes exist, prefer the larger group.

3. **Check for parallel group existence.** If analysis found no independent group (all tasks have dependencies, different tiers, or restart requirements), **output message**: "No independent parallel group detected. All pending tasks have dependencies or incompatible requirements." Stop execution. Do not create any worktrees. Return to the user prompt.

4. **If group found, for each task in the parallel group:**
   - Invoke `claudeutils _worktree new --task "<task name>"` (captures `<slug>\t<path>` output)
   - Parse slug and path from output
   - Edit `agents/session.md` to move task to Worktree Tasks with `→ <slug>` marker
   - Collect launch commands

   Process tasks sequentially (one at a time, in order).

5. **Output consolidated launch commands** after all worktrees are created:

       Worktrees ready:
         cd <path1> && claude    # <task name 1>
         cd <path2> && claude    # <task name 2>
         ...

       After each completes: `hc` to handoff+commit, then return here.
       Merge back: `wt merge <slug>` (uses skill)

## Mode C: Merge Ceremony

Used when the user invokes `wt merge <slug>`. This mode orchestrates the merge ceremony that returns worktree commits to the main branch, handling the handoff, commit, merge, and cleanup sequence.

1. **Read `agents/session.md`** to verify current session state. Then **invoke `/handoff --commit`** to ensure clean tree and session context committed. This ceremony step is mandatory: merge operations require a clean working tree, and handoff ensures that `agents/session.md` and related context files reflect the current state and are committed as a sync point. If handoff or commit fails, STOP. Merge requires clean tree. Resolve handoff/commit issues before retrying merge.

2. **Use Bash to invoke: `claudeutils _worktree merge <slug>`** to perform the three-phase merge: submodule resolution, parent repo merge, and precommit validation. The tool call captures exit code and stderr automatically.

3. **Exit code 0 (success):** The merge completed successfully. Use Edit tool on `agents/session.md`: Remove task from Worktree Tasks section. If Worktree Tasks section is missing, note that no cleanup is needed (task may have been removed already). Locate the line matching the `→ <slug>` marker and remove the entire task entry (and any continuation lines). Then use Bash to invoke: `claudeutils _worktree rm <slug>` to clean up the worktree branch and directory. Output: "Merged and cleaned up <slug>. Task complete."

4. **Parse merge exit code 1** (conflicts or precommit failure). Read stderr from merge command for conflict indicators or precommit failure messages.

   - **If conflicts detected:** List the conflicted files. Session files (`agents/session.md`, `agents/learnings.md`, `agents/jobs.md`) should auto-resolve using deterministic strategies — report as bug if present. For source files:
     1. **Edit** each conflicted file to fix conflicts manually
     2. **Use Bash:** `git add <conflicted-file>`
     3. **Re-run:** `claudeutils _worktree merge <slug>` (idempotent, resumes after resolution)

   - **If precommit failure detected:** The merge commit already exists in git (do NOT re-merge).
     1. **Review** the failed precommit checks in stderr
     2. **Fix** the reported issues in the working tree (edit files as needed)
     3. **Use Bash:** `git add <fixed-file>`
     4. **Use Bash:** `git commit --amend --no-edit`
     5. **Use Bash:** `just precommit` to verify
     6. **Re-run:** `claudeutils _worktree merge <slug>` to resume cleanup phase

5. **Parse merge exit code 2** (fatal error). Output: "Merge error: " followed by stderr. Generic error handling: review error output for root cause. Common issues:
   - Submodule initialization failures: Check `git submodule status`, ensure parent repo internet connectivity
   - Git state corruption: Run `git status` to inspect tree. If lock file errors occur, stop and report to user.
   - Branch mismatch: Verify `git branch` shows correct upstream, check `git log` for expected commits

   After resolving root cause, **retry:** `claudeutils _worktree merge <slug>` (same command, will resume from current state).

## Usage Notes

- **Slug derivation is deterministic:** The transformation of task names to slugs is repeatable. The same task name will always produce the same slug. This ensures consistency across sessions and enables command reuse (e.g., `wt merge <slug>` always operates on the correct worktree).

- **Merge is idempotent:** The `claudeutils _worktree merge <slug>` command can be safely re-run after manual fixes. It detects partial completion and resumes from the appropriate phase. You can fix conflicts, stage, and re-invoke the merge command without risk of double-merging.

- **Cleanup is user-initiated:** Mode A and Mode B require separate cleanup after merge. Mode C includes cleanup automatically after successful merge (branch deletion, worktree removal, session.md tidying via `claudeutils _worktree rm <slug>`).

- **Parallel execution requires individual merge:** When you have created multiple worktrees via `wt` (Mode B), each worktree must be merged back individually via `wt merge <slug1>`, `wt merge <slug2>`, etc. There is no batch merge command. Merge each worktree's branch when its task completes.

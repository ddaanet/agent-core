---
name: worktree
description: >-
  This skill should be used when the user asks to "create a worktree",
  "set up parallel work", "merge a worktree", "branch off a task",
  or uses the `wt`, `wt merge`, or `wt-rm` shortcuts. Worktree lifecycle:
  creation, focused sessions, merge ceremony, cleanup, parallel task setup.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(claudeutils _worktree:*)
  - Bash(just precommit)
  - Bash(git status:*)
  - Bash(git worktree:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git submodule:*)
  - Bash(git branch:*)
  - Bash(git log:*)
  - Skill
user-invocable: true
continuation:
  cooperative: true
  default-exit: []
---

# Manage Git Worktrees

Manage git worktree lifecycle for parallel task execution and focused work.

## Mode A: Single Task

Used when user specifies `wt <task-name>`.

1. **Read `agents/session.md`** to locate task in Pending Tasks. Extract full task block including name, command, model, and metadata.

2. **Invoke: `claudeutils _worktree new "<task name>"`** (requires `dangerouslyDisableSandbox: true`) to create the worktree with focused session. The command derives the slug from the task name, generates a focused session.md (filtered to just this task's context), creates the worktree in the sibling container, and cleans up temp files. Output is tab-separated: `<slug>\t<path>`. Use `--branch <slug>` to override the derived slug (e.g., when the derived slug exceeds 29 chars).

3. **Parse output** to extract slug and worktree path from the tab-separated line.

4. **Output launch command** using the path from step 3: `cd <path> && claude    # <task name>`.

The `new` command with a task name automatically moves the task from Pending Tasks to Worktree Tasks in `agents/session.md`, appending the `→ \`slug\`` marker. No manual session.md editing needed.

## Mode B: Parallel Group

Used when the user invokes `wt` with no arguments. This mode detects a group of independent parallel tasks and creates multiple worktrees simultaneously, enabling concurrent work on independent tasks.

1. **Read `agents/session.md`** and run `claudeutils _worktree ls` to identify all pending tasks and plan statuses. Extract task names, plan directories, model tiers, restart flags, and any blockers that might create dependencies.

2. **Check for shared plan directories and dependencies.** For each pending task, extract the plan directory (if specified). Build a dependency map:

   - **Plan directory independence:** Tasks with different plan directories OR no plan directory can run parallel. Tasks with no plan property are independent from each other. Skip any task that shares a plan directory with another.

   - **Logical dependencies:** Scan the Blockers/Gotchas section for mentions of other tasks. If Task B's blockers mention Task A, exclude both from parallel group. Check Pending Tasks section for explicit ordering hints (e.g., "Task X blocks Task Y").

   - **Model tier compatibility:** Extract model tier for each candidate task (haiku/sonnet/opus, default sonnet). All tasks in the group must have the same tier.

   - **Restart requirement check:** Check restart flag for each task. Any task marked "Restart: yes" disqualifies from parallel grouping.

   Select the **largest independent group** satisfying all four criteria. If multiple group sizes exist, prefer the larger group.

3. **Check for parallel group existence.** If analysis found no independent group (all tasks have dependencies, different tiers, or restart requirements), **output message**: "No independent parallel group detected. All pending tasks have dependencies or incompatible requirements." Stop execution. Do not create any worktrees. Return to the user prompt.

4. **If group found, for each task in the parallel group:**
   - Invoke `claudeutils _worktree new "<task name>"` with `dangerouslyDisableSandbox: true` (captures `<slug>\t<path>` output)
   - Parse slug and path from output
   - Collect launch commands

   Process tasks sequentially (one at a time, in order). The `new` command automatically moves each task to the Worktree Tasks section.

5. **Output consolidated launch commands** after all worktrees are created:

       Worktrees ready:
         cd <path1> && claude    # <task name 1>
         cd <path2> && claude    # <task name 2>
         ...

       After each completes: `hc` to handoff+commit, then return here.
       Merge back: `wt merge <slug>` (uses skill)

## Mode C: Merge Ceremony

Used when the user invokes `wt merge <slug>`. This mode orchestrates the merge ceremony that returns worktree commits to the main branch, handling the handoff, commit, and merge sequence.

1. **Invoke `/handoff --commit`** to ensure clean tree and session context committed. If handoff or commit fails, STOP — merge requires clean tree.

2. **Use Bash to invoke: `claudeutils _worktree merge <slug>`** (requires `dangerouslyDisableSandbox: true`) to perform the three-phase merge: submodule resolution, parent repo merge, and precommit validation. All output goes to stdout; exit code carries the semantic signal.

3. **Exit code 0 (success):** The merge completed successfully. Worktree preserved for bidirectional workflow — the user decides when to remove it. Output: "Merged <slug> successfully. Worktree preserved. To remove when ready: `wt-rm <slug>`"

4. **Parse merge exit code 3** (conflicts, merge paused). Read stdout for conflict report. The report contains: conflicted file list with conflict type, per-file diff stats, branch divergence summary, and a hint command. Session files (`agents/session.md`, `agents/learnings.md`) auto-resolve using deterministic strategies — report as bug if they appear in the conflict list. For each conflicted source file:
     1. **Edit** the file to resolve conflict markers
     2. **Use Bash:** `git add <file>`
     3. When all conflicts resolved, **re-run:** `claudeutils _worktree merge <slug>` with `dangerouslyDisableSandbox: true` (idempotent — resumes from current state, skips already-completed phases)

5. **Parse merge exit code 1** (error: precommit failure or git error). Read stdout for error message. The merge commit already exists in git (do NOT re-merge).
     1. **Review** the failed precommit checks in stdout
     2. **Fix** the reported issues in the working tree (edit files as needed)
     3. **Use Bash:** `git add <fixed-file>`
     4. **Use Bash:** `git commit --amend --no-edit`
     5. **Use Bash:** `just precommit` to verify
     6. **Re-run:** `claudeutils _worktree merge <slug>` with `dangerouslyDisableSandbox: true` to resume cleanup phase

6. **Parse merge exit code 2** (fatal error). Read stdout for error message. Generic error handling: review error output for root cause. Common issues:
   - Submodule initialization failures: Check `git submodule status`, ensure parent repo internet connectivity
   - Git state corruption: Run `git status` to inspect tree. If lock file errors occur, stop and report to user.
   - Branch mismatch: Verify `git branch` shows correct upstream, check `git log` for expected commits

   After resolving root cause, **retry:** `claudeutils _worktree merge <slug>` (same command, will resume from current state).

## Usage Notes

- **CLI signature:** `claudeutils _worktree new [TASK_NAME] [--branch TEXT] [--base TEXT]`. Positional `TASK_NAME` is the task name from session.md (quoted). Use `--branch <slug>` to override the derived slug or to create a bare worktree without session integration. There is no `--task` flag — the task name is always positional.

- **Sandbox bypass required for mutations:** All `claudeutils _worktree` mutation commands (`new`, `merge`, `rm`) must use `dangerouslyDisableSandbox: true`. These commands create/remove worktree directories outside project root and run environment setup (`uv sync`, `direnv allow`). Read-only git commands (`git status`, `git log`, `git worktree list`) do NOT need bypass.

- **Slug derivation is deterministic:** The transformation of task names to slugs is repeatable. The same task name will always produce the same slug. This ensures consistency across sessions and enables command reuse (e.g., `wt merge <slug>` always operates on the correct worktree).

- **Merge is idempotent:** The `claudeutils _worktree merge <slug>` command can be safely re-run after manual fixes. It detects partial completion and resumes from the appropriate phase. Fix conflicts, stage, and re-invoke the merge command without risk of double-merging.

- **Session.md task movement is automated:** `new "<task name>"` moves the task from Pending Tasks to Worktree Tasks (with `→ \`slug\`` marker). `rm` removes the task from Worktree Tasks when it was completed in the worktree branch (checked via `git show`). No manual session.md editing required for task movement.

- **Cleanup is user-initiated:** After merge, worktree is preserved. Remove when ready via `wt-rm <slug>`.

- **Parallel execution requires individual merge:** When multiple worktrees exist via `wt` (Mode B), merge each back individually via `wt merge <slug1>`, `wt merge <slug2>`, etc. There is no batch merge command. Merge each worktree's branch when its task completes.

- **Emergency `--force` flag:** `claudeutils _worktree rm --force <slug>` bypasses all safety checks (confirm, dirty tree, guard). Use only as emergency escape hatch when normal workflow is blocked.

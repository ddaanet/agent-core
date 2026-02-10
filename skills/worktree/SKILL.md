---
name: worktree
description: >-
  Manage git worktree lifecycle for parallel task execution and focused work.
  Use this skill to create a worktree, set up parallel work for independent
  tasks, merge a worktree back after completion, or branch off a task for
  focused development. Access via the `wt` shortcut or explicit commands.
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

## Mode B: Parallel Group

## Mode C: Merge Ceremony

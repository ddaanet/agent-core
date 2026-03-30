# Branch Mode (No Task Tracking)

The CLI supports a bare slug form for creating worktrees without session.md integration:

```bash
edify _worktree new <slug>
```

This creates the worktree but skips: slug derivation from task name, focused session generation, and session.md task movement. All session.md edits become manual.

## When to Use

Branch mode is for worktrees not tied to a tracked task in session.md. No established use case exists yet — the adhoc worktree mode is a pending design task.

## Prefer Task Name Form

For any task listed in session.md, always use:

```bash
edify _worktree new "<task name>"
```

The task name form automates all side effects. Using the bare slug form for tracked tasks forces manual session.md editing that is worse (no focused session), error-prone, and reimplements what the tool already does.

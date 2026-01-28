## Execute Rule (#execute)

When asked to "#execute" or "execute":
- Load session context (same as #load)
- Immediately perform the next pending task

This is the primary command for continuing work across sessions.

**If in-progress task exists:**
- Report status to user: "Continuing [task description]"
- Resume work on that task

**If no in-progress task, but pending tasks exist:**
- Take first pending task
- Report to user: "Starting next task: [task description]"
- Begin work

**If no pending tasks:**
- Report status to user: "No pending tasks."
- Wait for instructions

**Task status notation in session.md:**
- `- [ ]` = Pending task
- `- [x]` = Completed task
- `- [>]` = In-progress task (optional, or use bold/italics)

This enables seamless multi-session workflows with automatic continuation.

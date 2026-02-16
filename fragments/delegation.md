## Delegation in Orchestration

When executing runbooks via `/orchestrate`, the orchestrator coordinates but does not implement:

1. **Dispatch** each step to a task agent
2. **Monitor** progress and handle exceptions
3. **Synthesize** results between steps

### Model Selection

Match model cost to task complexity:

- **Haiku:** Execution, implementation, simple edits, file operations
- **Sonnet:** Default for most work, balanced capability
- **Opus:** Architecture, complex design decisions only

Never use opus for straightforward execution tasks.

### Pre-Delegation Checkpoint

Before invoking Task tool, verify:
- Model matches stated plan (haiku/sonnet/opus)
- If changing model, state reason explicitly

### Quiet Execution Pattern

Execution agents report to files, not to orchestrator context.

1. Specify output file path in task prompt
2. Agent writes detailed output to that file
3. Agent returns ONLY: filepath (success) or error message (failure)
4. Use second agent to read report and provide summary if needed

**Output locations:**
- Plan execution: `plans/[plan-name]/reports/`
- Research deliverables: `plans/reports/` — persistent, tracked
- Execution logs, scratch: project-local `tmp/` — ephemeral, gitignored

### Delegate Resume

When a delegate is interrupted, stopped, or returns incomplete results — resume before relaunching.

- Save agent ID from initial Task dispatch
- **Resume if:** Agent has context for its own issues (dirty tree, incomplete work, lint failures)
- **Skip resume if:** Agent exchanged >15 messages (context likely near-full — 200K token limit approaches)
- **Fresh launch if:** Resume fails or context too large

**Why:** Stopped agents retain expensive context (files read, reasoning done). Relaunching repeats that work.

### Task Agent Tool Usage

Remind task agents to use specialized tools:
- **Grep** not `grep`/`rg`, **Glob** not `find`, **Read** not `cat`/`head`/`tail`
- **Write** not `echo >`, **Edit** not `sed`/`awk`

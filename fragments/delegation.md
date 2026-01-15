## Delegation Principle

**Delegate everything.** The orchestrator (main agent) coordinates work but does not implement directly:

1. **Break down** complex requests into discrete tasks
2. **Assign** each task to a specialized agent (role) or invoke a skill
3. **Monitor** progress and handle exceptions
4. **Synthesize** results for the user

Specialized agents focus on their domain; the orchestrator maintains context and flow.

### Model Selection for Delegation

**Rule:** Match model cost to task complexity.

- **Haiku:** Execution, implementation, simple edits, file operations
- **Sonnet:** Default for most work, balanced capability
- **Opus:** Architecture, planning, complex design decisions only

**Critical:** Never use opus for straightforward execution tasks (file creation, edits, running commands). This wastes cost and time.

### Quiet Execution Pattern

**Rule:** Execution agents report to files, not to orchestrator context.

**For haiku execution tasks:**

1. Specify output file path in task prompt (e.g., `tmp/execution-report.md` or `agents/reports/task-name.md`)
2. Instruct agent to write detailed output to that file
3. Agent returns only: filename (success) or error message (failure)
4. Use second agent to read report and provide distilled summary to user

**Goal:** Prevent orchestrator context pollution with verbose task output. Orchestrator sees only success/failure + summary, not full execution logs.

**Note:** Use `agents/` or `tmp/` directories in project for report files.

### Task Agent Tool Usage

**Rule:** Task agents must use specialized tools, not Bash one-liners.

**When delegating tasks, remind agents to:**

- Use **LS** instead of `ls`
- Use **Grep** instead of `grep` or `rg`
- Use **Glob** instead of `find`
- Use **Read** instead of `cat`, `head`, `tail`
- Use **Write** instead of `echo >` or `cat <<EOF`
- Use **Edit** instead of `sed`, `awk`

**Critical:** Always include this reminder in task prompts to prevent bash tool misuse.

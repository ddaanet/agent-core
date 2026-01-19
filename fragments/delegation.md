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

1. Specify output file path in task prompt (e.g., `tmp/execution-report.md` or `plans/[plan-name]/reports/task-name.md`)
2. Instruct agent to write detailed output to that file
3. Agent returns ONLY:
   - **Success:** Filename (absolute path or relative to working directory)
   - **Failure:** Error message with diagnostic info
4. Use second agent to read report and provide distilled summary to user

**Return Format Specification:**

**Success case:**
```
reports/step-1-execution.md
```
OR (absolute path):
```
/Users/david/code/project/reports/step-1-execution.md
```

**Failure case:**
```
Error: File not found - /Users/david/code/pytest-md/CLAUDE.md
Details: Expected CLAUDE.md at specified path but file doesn't exist.
Check: Directory listing shows AGENTS.md instead.
Recommendation: Verify correct filename in plan step.
```

**Goal:** Prevent orchestrator context pollution with verbose task output. Orchestrator sees only success/failure + summary, not full execution logs.

**Two-phase communication pattern:**

```
Phase 1 (Execution Agent):
  Orchestrator delegates: "Execute step 3. Write report to reports/step-3.md"
  Agent: Executes task, writes detailed report to file
  Agent returns: "reports/step-3.md" (or error message)

Phase 2 (Summary Agent - optional):
  Orchestrator: If needed, delegate to summary agent
  Summary agent: Reads reports/step-3.md
  Summary agent returns: "Step 3 complete. [1-2 sentence summary]"

Result: Orchestrator context: ~100 tokens
         Detailed logs: Available in reports/ for inspection
```

**Note:** For plan execution, use `plans/[plan-name]/reports/` directory. For ad-hoc work, use project-local `tmp/` directory, not system `/tmp/`.

**Integration with plan-specific agent:**

Plan-specific agents enable quiet execution by having all context needed to run independently. See `pattern-plan-specific-agent.md` for integration details.

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

## Delegation in Orchestration

When executing runbooks via `/orchestrate`, the orchestrator coordinates but does not implement:

1. **Dispatch** each step to a task agent
2. **Monitor** progress and handle exceptions
3. **Synthesize** results between steps

### Model Selection

Match model cost to task complexity:

- **Sonnet:** Default for all execution tasks
- **Opus:** Architecture, complex design decisions, prose artifacts (skills, fragments, agents)

### Pre-Delegation Checkpoint

Before invoking Task tool, verify:
- Model matches stated plan (sonnet/opus)
- If changing model, state reason explicitly

### File Reference Dispatch

Dispatch with file reference: `"Execute step from: plans/<name>/steps/step-N.md"` — agent reads step file for full context. Do not inline step content in prompt.

Plan-specific agents (`{name}-task`, `{name}-corrector`) embed design and outline context via agent definition. Prompt needs only the step file reference — Plan Context is baked into the agent definition.

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

### Recall Artifacts For Sub-Agents

Two distinct artifact models: pipeline recall (grouped entries with relevance notes, selective resolution by consuming skill) vs sub-agent injection (flat trigger list, resolve-all, no selection judgment). Sub-agents have no parent context — they can't judge which entries are relevant, making selective resolution circular.

**Anti-pattern:** Using pipeline-model artifacts (grouped, relevance notes) when the consumer is a delegated agent.

**Correct pattern:** Flat list for sub-agent injection. Delegation prompt says "resolve ALL entries." Pipeline model for skills/orchestrators that have topic context for selection.

### Multi-Step Verification

**Anti-pattern:** Splitting post-step verification into separate tool calls. First check (git status) returns clean → exit momentum suppresses second check (just lint). The sub-agent "already linted" rationalization makes the skip feel safe.

**Correct pattern:** Single compound command (`git status --porcelain && just lint`). Compound commands can't be partially executed — both run or neither.

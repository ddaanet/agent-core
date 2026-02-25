---
name: orchestrate
description: Execute prepared runbooks with weak orchestrator pattern
allowed-tools: Task, Read, Write, Bash(git:*), Skill
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
---

# Execute Runbooks

Execute prepared runbooks using the weak orchestrator pattern. This skill coordinates step-by-step execution through plan-specific agents, handling progress tracking, error escalation, and report management.

**Prerequisites:** Runbook must be prepared with `/runbook` skill (artifacts created by `prepare-runbook.py`)

## Execution Process

### 1. Verify Runbook Preparation

**Check for required artifacts:**

```bash
# Verify required artifacts
ls -1 plans/<runbook-name>/orchestrator-plan.md
ls -1 .claude/agents/crew-<runbook-name>*.md

# Step files may be absent for all-inline runbooks
ls -1 plans/<runbook-name>/steps/step-*.md 2>/dev/null || true
```

**Required artifacts:**
- Orchestrator plan: `plans/<runbook-name>/orchestrator-plan.md`
- Per-phase agents: `.claude/agents/crew-<runbook-name>[-p<N>].md` (one per non-inline phase; unused for all-inline runbooks)
- Step files: `plans/<runbook-name>/steps/step-*.md` (may be absent for all-inline runbooks)

**If orchestrator plan missing:** ERROR, stop execution.

**If step files missing but orchestrator plan has only `Execution: inline` entries:** Valid — all-inline runbook, proceed.

**If step files missing and orchestrator plan references step files:** ERROR, stop execution.

### 2. Read Orchestrator Plan

**Load orchestration instructions:**

```bash
Read plans/<runbook-name>/orchestrator-plan.md
```

**Key information:**
- Execution order (sequential vs parallel)
- Error escalation rules
- Progress tracking requirements
- Report location patterns

### 3. Execute Steps (Sequential, With Inline Handling)

**For each item in the orchestrator plan:**

**Check execution mode:** Read the orchestrator plan entry for the current item.
- If `Execution: inline` → follow Section 3.0 (inline execution) below
- If `Execution: steps/step-N-M.md` → follow Section 3.1 (agent delegation) below

**3.0 Inline execution (orchestrator-direct):**

The orchestrator reads the phase content from the runbook and executes edits directly — no Task agent dispatch.

1. Read the runbook phase content. The orchestrator plan entry names the phase; locate the corresponding phase heading in the original runbook file (`plans/<runbook-name>/runbook.md`) or the phase file in a phase-grouped directory.
2. Execute each instruction: Read target file → Edit/Write as specified
3. After all instructions in the inline phase complete, run `just precommit` to validate
   - If precommit fails: fix issues, re-run precommit, then proceed
   - If unfixable: STOP and escalate to user
4. **Phase boundary review:** Apply review-requirement proportionality (from `agent-core/fragments/review-requirement.md`):
   - ≤5 net lines across ≤2 files, additive → self-review (`git diff`, verify correctness before commit)
   - Larger → commit first, then delegate to corrector with standard checkpoint template
5. Commit the inline phase changes (if not already committed in step 4)
6. Proceed to next item

**3.1 Invoke plan-specific agent with step file:**

```
Use Task tool with:
- subagent_type: [from orchestrator plan "Agent:" field for this step]
- prompt: "Execute step from: plans/<runbook-name>/steps/step-N.md

CRITICAL: For session handoffs, use /handoff-haiku, NOT /handoff."
- description: "Execute step N of runbook"
- model: [from step file header "Execution Model" field]
```

**CRITICAL — Model selection:** The orchestrator itself may run on haiku, but step agents use the model specified in each step file's **header metadata**. The `**Execution Model**` field appears in the step file header (lines before the `---` separator), placed there by `prepare-runbook.py`. Read the header section of each step file to extract the model — do NOT search the full body. Do NOT default all steps to haiku.

**3.2 Check execution result:**

**Success indicators:**
- Agent returns completion message
- Report file created at expected path
- No error messages

**Failure indicators:**
- Agent reports error
- Missing report file
- Unexpected results mentioned

**3.3 Post-step verification and phase boundary:**

<!-- DESIGN RULE: Every step must open with a tool call (Read/Bash/Glob).
     Prose-only steps get skipped. See: plans/reflect-rca-prose-gates/outline.md -->

After agent returns success:
```bash
git status --porcelain
```
- If clean (no output): proceed to phase boundary check below
- If ANY output: **STOP orchestration immediately**
  - Report: "Step N left uncommitted changes: [file list]"
  - Do NOT proceed regardless of whether changes look expected
  - Do NOT clean up on behalf of the step
  - Escalate to user

**There are no exceptions.** Every step must leave a clean tree. If a step generates output files, the step itself must commit them. Report files, artifacts, and any other changes must be committed by the step agent before returning success.

**Phase boundary check:**

Read the next step file header (first 10 lines of `plans/<name>/steps/step-{N+1}.md`).

Compare its `Phase:` field with the current step's phase.

IF same phase: proceed to 3.4.

IF phase changed (or no next step = final phase): delegate to corrector for checkpoint.

Do NOT proceed to next step until checkpoint completes.

**Checkpoint delegation:**
1. Run precommit first: `just precommit` to ground "Changed files" in reality
2. Gather context: design path, changed files (`git diff --name-only`), phase scope
3. Delegate to corrector with structured template (see below)
4. Read report: if UNFIXABLE issues, STOP and escalate to user
5. If all fixed: commit checkpoint, continue to next phase

**Checkpoint delegation template:**

```
Phase N Checkpoint

**First:** Run `just dev`, fix any failures, commit.

**Scope:**
- IN: [list methods/features implemented in this phase]
- OUT: [list methods/features for future phases — do NOT flag these]

**Review (read changed files):**
- Test quality: behavior-focused, meaningful assertions, edge cases
- Implementation quality: clarity, patterns, appropriate abstractions
- Integration: duplication across phase methods, pattern consistency
- Design anchoring: verify implementation matches design decisions

**Design reference:** plans/<name>/design.md
**Review recall:** `Bash: agent-core/bin/recall-resolve.sh plans/<name>/recall-artifact.md` — if present, resolved content contains review-relevant entries: common review failures, quality anti-patterns, over-escalation patterns. If artifact absent or recall-resolve.sh fails: do lightweight recall — Read `memory-index.md`, identify review-relevant entries, batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...`.
**Changed files:** [file list from git diff --name-only]

Fix all issues. Write report to: plans/<name>/reports/checkpoint-N-review.md
Return filepath or "UNFIXABLE: [description]"
```

**Template enforcement:**
- **MUST provide structured IN/OUT scope** (bulleted lists, NOT prose-only)
- **MUST run precommit first** to ensure changed files reflect actual state
- **MUST include changed files list** from `git diff --name-only`
- **MUST specify requirements** from design or phase objective
- **Fail loudly if template fields empty:** If IN list is empty, OUT list is empty, Changed files is missing, or Requirements has no bullet items — STOP orchestration and report which field is incomplete before delegating to corrector

**Rationale:** Prevents confabulating future-phase issues. Review validates current filesystem, not execution-time state — without explicit OUT scope, reviewer may flag unimplemented features from future phases as missing.

**Final checkpoint lifecycle audit (D-7):**
When the phase boundary is the final one (no next step), add to checkpoint delegation:
- Audit stateful objects created during implementation (MERGE_HEAD, staged content, lock files, temporary files)
- Verify every code path that exits success has cleared active state
- Same methodology as cross-cutting exit code audit: trace all code paths, flag any that exit success with state still active
- Add to review scope: `"Lifecycle audit: verify all stateful objects cleared on success paths"`

**3.4 On success:**
- Log step completion
- Continue to next step

**3.5 On failure:**
- Read error report
- Determine escalation level
- Escalate according to orchestrator plan

### 4. Error Escalation

**Acceptance criteria:** Every escalation resolution must satisfy all three criteria defined in `agent-core/fragments/escalation-acceptance.md`: precommit passes, tree clean, output validates against step criteria.

**Rollback:** When escalation fails (fix attempt causes new issues or acceptance criteria unmet), revert to last clean commit before the failed step. See `escalation-acceptance.md` for protocol.

**Timeout:** Set `max_turns: 150` on all Task tool invocations for step agents. This catches spinning agents (high activity, no convergence) without false positives against calibration data (p99=73, max=129 from 938 clean observations). Duration timeout (~600s for hanging agents) requires Claude Code support and is deferred.

**Escalation levels (from orchestrator metadata):**

**Level 1: Haiku → Sonnet (Refactor Agent)**
- Triggers: Quality check warnings from TDD cycles
- Action: Delegate to refactor agent (sonnet) for evaluation and execution
- Refactor agent evaluates severity and handles or escalates to opus
- If refactor agent fixes: Resume execution
- If refactor agent escalates: Route to opus or user as appropriate

**Level 1b: Haiku → Sonnet (Diagnostic)**
- Triggers: Unexpected file states, permission errors, script execution failures
- Action: Delegate diagnostic and fix to sonnet task agent
- If sonnet fixes: Resume execution
- If sonnet cannot fix: Escalate to user

**Level 2: Sonnet → User**
- Triggers: Design decisions needed, architectural changes required, sonnet cannot resolve
- Action: Stop execution, provide detailed context to user
- Report: What failed, what was attempted, what's needed to proceed

**Escalation prompt template:**

```
Diagnose and fix the following error from step N:

Error: [error message]
Step: [step objective]
Expected: [what should have happened]
Observed: [what actually happened]

Read error report at: [report-path]
Read step definition at: [step-path]

If fixable: Make necessary corrections and report success
If not fixable: Explain why and what user input is needed

Write diagnostic to: plans/<runbook-name>/reports/step-N-diagnostic.md
Return: "fixed: [summary]" or "blocked: [what's needed]"
```

### 5. Progress Tracking

Log each step completion to stdout: "Step N: [name] - completed" or "Step N: [name] - failed: [error]"

**Detailed tracking:** Read `references/progress-tracking.md` for optional progress file format with timestamps and report references.

### 6. Completion

**When all steps successful:**

1. Delegate to corrector for quality review
   - Write report to `plans/<name>/reports/review.md`
2. If runbook frontmatter has `type: tdd`:
   - Delegate to tdd-auditor for process analysis
   - Write report to `plans/<name>/reports/tdd-process-review.md`
3. Report overall success with report links
4. **Deliverable review assessment:**
   - If orchestration produced production artifacts (skills, agents, fragments, code): create pending task for deliverable review
   - Task format: `- [ ] **Deliverable review: <plan-name>** — \`/deliverable-review plans/<plan>\` | opus | restart`
   - Restart required: orchestration may produce new agents requiring session restart
   - Do NOT run deliverable review inline — needs opus + cross-project context + restart
5. **Lifecycle entry:** If `plans/<plan-name>/` exists, append to `plans/<plan-name>/lifecycle.md`:
   ```
   {YYYY-MM-DD} review-pending — /orchestrate
   ```
   Create the file if it doesn't exist. Date: today's ISO date.
6. Default-exit: `/handoff --commit` → `/commit`

**When blocked:**
- Report which step failed
- Provide error context
- List completed steps
- Indicate what's needed to proceed

## Weak Orchestrator Pattern

**Delegate, don't decide.** All decisions made during planning (/runbook). Execution is mechanical: invoke agent, check result, continue or escalate. Trust agent success reports. Never second-guess, validate, or modify steps during execution. Inline phases (Section 3.0) are orchestrator-executed by design; this principle applies to agent-delegated steps (Section 3.1).

## Constraints

- **Task** for plan-specific agents, **Read** for artifacts/reports, **Edit** for inline phases, **Bash** for git only
- Sequential unless orchestrator plan explicitly allows parallel
- Never skip steps, even if they seem unnecessary
- Always escalate failures with full context

## Common Scenarios

**For scenario handling** (unexpected results, missing reports, repeated failures, agent hangs, context ceiling resume): Read `references/common-scenarios.md`.

## Continuation Protocol

This skill is **cooperative** with the continuation passing system. After orchestration completes, check Skill args suffix for `[CONTINUATION: ...]` transport. If no continuation, use default-exit from frontmatter.

**Full protocol and examples:** Read `references/continuation.md`.

## References

**Example Orchestrator Plan**: `plans/unification/orchestrator-plan.md`
**Example Plan-Specific Agent**: `.claude/agents/unification-task.md`
**Example Step Files**: `plans/unification/steps/step-2-*.md`

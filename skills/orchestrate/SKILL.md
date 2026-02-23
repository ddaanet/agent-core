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

## When to Use

**Use this skill when:**
- Runbook has been prepared and artifacts exist
- Ready to execute multi-step plan
- Need systematic step-by-step execution with tracking
- Want automated error escalation

**Do NOT use when:**
- Runbook not yet prepared (use `/runbook` first)
- Single-step task (execute directly)
- Interactive execution needed (user decisions during execution)

## Execution Process

### 1. Verify Runbook Preparation

**Check for required artifacts:**

```bash
# Verify required artifacts
ls -1 plans/<runbook-name>/orchestrator-plan.md
ls -1 .claude/agents/<runbook-name>-task.md

# Step files may be absent for all-inline runbooks
ls -1 plans/<runbook-name>/steps/step-*.md 2>/dev/null || true
```

**Required artifacts:**
- Orchestrator plan: `plans/<runbook-name>/orchestrator-plan.md`
- Plan-specific agent: `.claude/agents/<runbook-name>-task.md` (unused for all-inline runbooks, but created by prepare-runbook.py)
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
- subagent_type: "<runbook-name>-task"
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
**Changed files:** [file list from git diff --name-only]

Fix all issues. Write report to: plans/<name>/reports/checkpoint-N-vet.md
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

**Track execution state:**

**Simple approach:**
- Log each step completion to stdout
- Format: "✓ Step N: [step name] - completed"
- On error: "✗ Step N: [step name] - failed: [error]"

**Detailed approach (optional):**
- Maintain progress file: `plans/<runbook-name>/progress.md`
- Update after each step with status and timestamp
- Include report file references

**Progress file format:**

```markdown
# Runbook Execution Progress

**Runbook**: [name]
**Started**: [timestamp]
**Status**: [In Progress / Completed / Blocked]

## Step Execution

- ✓ Step 1: [name] - Completed at [timestamp]
  - Report: plans/<runbook-name>/reports/step-1-execution.md
- ✓ Step 2: [name] - Completed at [timestamp]
  - Report: plans/<runbook-name>/reports/step-2-execution.md
- ✗ Step 3: [name] - Failed at [timestamp]
  - Report: plans/<runbook-name>/reports/step-3-execution.md
  - Error: [brief error description]
  - Escalated to: [sonnet / user]

## Summary

Steps completed: 2/5
Steps failed: 1
Current status: Blocked on Step 3
```

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
5. Default-exit: `/handoff --commit` → `/commit`

**When blocked:**
- Report which step failed
- Provide error context
- List completed steps
- Indicate what's needed to proceed

## Weak Orchestrator Pattern

**Key characteristics:**

**Delegate, don't decide:**
- Orchestrator does NOT make judgment calls
- All decisions made during planning (/runbook)
- Execution is mechanical: invoke agent, check result, continue or escalate

**Trust agents:**
- If agent reports success, trust it
- If agent reports error, escalate according to plan
- Don't second-guess or validate agent output

**No ad-hoc logic (for delegated steps):**
- Don't parse files to verify delegated agent completion
- Don't make recovery decisions for delegated steps
- Don't modify steps during execution
- If something unexpected happens: escalate

Note: Inline phases (Section 3.0) are explicitly orchestrator-executed by design. This principle applies to agent-delegated steps (Section 3.1).

**Error escalation only:**
- Simple errors → delegate to sonnet for fix
- Complex errors → stop and report to user
- Never suppress errors or proceed on failure

## Critical Constraints

**Tool Usage:**
- Use **Task** to invoke plan-specific agents (delegated steps)
- Use **Read** to check artifacts and reports
- Use **Edit** for inline phase modifications (Section 3.0)
- Use **Write** for progress tracking (optional)
- Use **Bash** only for git operations if specified in orchestrator plan

**Execution Flow:**
- Always sequential unless orchestrator plan explicitly allows parallel
- Complete one step before starting next
- Never skip steps, even if they seem unnecessary

**Error Handling:**
- Never suppress errors
- Always escalate failures
- Provide full context in escalation
- Don't attempt ad-hoc fixes

**Progress Tracking:**
- Log step completions clearly
- Reference report files
- Make current state obvious

## Example Execution

**User:** `/orchestrate oauth2-auth`

**Agent:** "Executing runbook: oauth2-auth

Verifying artifacts...
✓ Plan-specific agent: .claude/agents/oauth2-auth-task.md
✓ Step files: 4 steps found
✓ Orchestrator plan: plans/oauth2-auth/orchestrator-plan.md

Reading orchestrator plan...
- Execution: Sequential
- Model: haiku
- Escalation: haiku → sonnet → user

Starting execution...

**Step 1: Setup OAuth2 configuration**
*Invokes oauth2-auth-task agent with step-1.md*
✓ Completed - report at plans/oauth2-auth/reports/step-1-execution.md

**Step 2: Implement auth routes**
*Invokes oauth2-auth-task agent with step-2.md*
✓ Completed - report at plans/oauth2-auth/reports/step-2-execution.md

**Step 3: Add session management**
*Invokes oauth2-auth-task agent with step-3.md*
✗ Failed - error: Missing session store configuration

Escalating to sonnet...
*Delegates diagnostic to sonnet agent*
Sonnet diagnostic: Configuration needs DB_SESSION_STORE env var
*Sonnet makes fix: adds env var to config*
✓ Step 3 retry successful

**Step 4: Create user profile integration**
*Invokes oauth2-auth-task agent with step-4.md*
✓ Completed - report at plans/oauth2-auth/reports/step-4-execution.md

---

**Execution Complete**

All 4 steps completed successfully.

Reports:
- plans/oauth2-auth/reports/step-1-execution.md
- plans/oauth2-auth/reports/step-2-execution.md
- plans/oauth2-auth/reports/step-3-execution.md
- plans/oauth2-auth/reports/step-3-diagnostic.md (escalation)
- plans/oauth2-auth/reports/step-4-execution.md

Next: Delegate to corrector to review and fix changes before committing."

## Handling Common Scenarios

**Scenario: Step reports unexpected result but no error**
- Action: Stop and report to user
- Reason: "Unexpected" means planning assumptions were wrong
- Don't proceed without user guidance

**Scenario: Report file missing after agent completes**
- Action: Escalate to sonnet
- Reason: Likely agent error or path issue
- Sonnet can investigate and fix

**Scenario: Multiple steps fail with same error**
- Action: After second failure, stop and report pattern to user
- Reason: Systemic issue, not one-off error
- User needs to update runbook or fix root cause

**Scenario: Agent never returns**
- Action: Check task status with TaskOutput tool
- If hanging: Kill task and escalate to user
- If still running: Wait and check periodically

**Scenario: Resuming after context ceiling or kill**
- Previous session hit token limit mid-execution. Fresh agent picks up.
- Action: Find last completed phase boundary (last checkpoint commit in git log)
- Run that checkpoint's verification commands from the runbook phase file
- Build complete inventory of remaining work from verification output
- Then resume from next step after the checkpoint
- Do NOT use `just precommit` as a state assessment tool — it's a pass/fail gate, not a diagnostic. Use the runbook's checkpoint verification commands, which are designed to produce a complete inventory of what's done and what's missing.

## Integration with Workflows

**Implementation workflow:**
1. `/design` — Opus creates design document
2. `/runbook` — Sonnet creates runbook and artifacts (per-phase typing: TDD + general)
3. `/orchestrate` — Executes runbook (THIS SKILL)
4. corrector — Review and fix changes
5. tdd-auditor — TDD process analysis (if runbook has TDD phases)
6. Complete job

**Handoff:**
- Input: Prepared artifacts from `/runbook`
- Output: Executed steps with reports
- Next: corrector review, then `/handoff --commit` → `/commit`

## Continuation Protocol

**This skill is cooperative** with the continuation passing system.

**Consumption:**

After completing the orchestration, check the Skill args suffix for `[CONTINUATION: ...]` transport.

IF continuation present:
1. Parse the `[CONTINUATION: ...]` structured list
2. Peel first entry: `(/skill args)` or `/skill` (if no args)
3. Strip continuation from current context (delete `[CONTINUATION: ...]` suffix)
4. Invoke next skill: `Skill(/skill args="args [CONTINUATION: remainder]")` where remainder = remaining entries (if any)

IF no continuation present:
- Use default-exit from frontmatter: `/handoff --commit` then `/commit`
- Invoke first entry, pass remainder as continuation to that skill

**Example:**

Incoming: `/orchestrate myplan [CONTINUATION: /commit]`
- Complete orchestration
- Strip continuation from current context
- Peel first entry: `/commit`
- No remainder, so invoke: `Skill(/commit)`

Incoming: `/orchestrate myplan [CONTINUATION: /handoff --commit, /commit]`
- Complete orchestration
- Strip continuation from current context
- Peel first: `/handoff --commit`
- Remainder: `/commit`
- Invoke: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`

Incoming: `/orchestrate myplan` (no continuation)
- Complete orchestration
- Use default-exit: `["/handoff --commit", "/commit"]`
- Invoke: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`

**Constraint:** This skill does NOT pass continuations to sub-agents (Task tool). Continuations apply only to the main session skill chain.

## References

**Example Orchestrator Plan**: `/Users/david/code/claudeutils/plans/unification/orchestrator-plan.md`
**Example Plan-Specific Agent**: `/Users/david/code/claudeutils/.claude/agents/unification-task.md`
**Example Step Files**: `/Users/david/code/claudeutils/plans/unification/steps/step-2-*.md`

These demonstrate the artifacts structure and execution pattern.

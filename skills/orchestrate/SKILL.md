---
description: Execute prepared runbooks with weak orchestrator pattern
allowed-tools: Task, Read, Write, Bash(git:*)
user-invocable: true
---

# Orchestrate Skill

Execute prepared runbooks using the weak orchestrator pattern. This skill coordinates step-by-step execution through plan-specific agents, handling progress tracking, error escalation, and report management.

**Prerequisites:** Runbook must be prepared with `/plan-adhoc` skill (artifacts created by `prepare-runbook.py`)

## When to Use

**Use this skill when:**
- Runbook has been prepared and artifacts exist
- Ready to execute multi-step plan
- Need systematic step-by-step execution with tracking
- Want automated error escalation

**Do NOT use when:**
- Runbook not yet prepared (use `/plan-adhoc` first)
- Single-step task (execute directly)
- Interactive execution needed (user decisions during execution)

## Execution Process

### 1. Verify Runbook Preparation

**Check for required artifacts:**

```bash
# Verify artifacts exist
ls -1 plans/<runbook-name>/steps/step-*.md
ls -1 .claude/agents/<runbook-name>-task.md
ls -1 plans/<runbook-name>/orchestrator-plan.md
```

**Required artifacts:**
- Plan-specific agent: `.claude/agents/<runbook-name>-task.md`
- Step files: `plans/<runbook-name>/steps/step-*.md`
- Orchestrator plan: `plans/<runbook-name>/orchestrator-plan.md`

**If artifacts missing:**
- ERROR: "Runbook not prepared. Run `/plan-adhoc` first to create execution artifacts."
- Stop execution

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

### 3. Execute Steps Sequentially

**For each step in order:**

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

**3.3 Post-step tree check:**

After agent returns success:
```bash
git status --porcelain
```
- If clean (no output): proceed to next step
- If ANY output: **STOP orchestration immediately**
  - Report: "Step N left uncommitted changes: [file list]"
  - Do NOT proceed regardless of whether changes look expected
  - Do NOT clean up on behalf of the step
  - Escalate to user

**There are no exceptions.** Every step must leave a clean tree. If a step generates output files, the step itself must commit them. Report files, artifacts, and any other changes must be committed by the step agent before returning success.

**3.4 Checkpoint at phase boundary:**

At every phase boundary, delegate to vet-fix-agent for quality review.

**Phase boundary detection:** When step file `Phase: N` field changes from previous step.

**Checkpoint delegation:**
1. Gather context: design path, changed files (`git diff --name-only`), phase scope
2. Delegate to vet-fix-agent with prompt:
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
3. Read report: if UNFIXABLE issues, STOP and escalate to user
4. If all fixed: commit checkpoint, continue to next phase

**3.5 On success:**
- Log step completion
- Continue to next step

**3.6 On failure:**
- Read error report
- Determine escalation level
- Escalate according to orchestrator plan

### 4. Error Escalation

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

**For TDD runbooks** (runbook frontmatter has `type: tdd`):
1. Delegate to vet-fix-agent for quality review
2. After vet completes, delegate to review-tdd-process agent for process analysis
3. Report overall success with links to both reports
4. Next action: `/commit` to commit changes

**TDD completion delegation:**
```
Task(subagent_type="vet-fix-agent",
     prompt="Review all changes from TDD execution. Write report to plans/<name>/reports/vet-review.md",
     description="Vet review of TDD execution")

# After vet completes:
Task(subagent_type="review-tdd-process",
     prompt="Analyze TDD execution for runbook: plans/<name>/runbook.md
             Commit range: <start-commit>..<end-commit>
             Write report to: plans/<name>/reports/tdd-process-review.md",
     description="TDD process quality analysis")
```

**For general runbooks:**
- Report overall success
- List created artifacts
- Suggest next action: delegate to vet-fix-agent to review changes, then `/commit`

**When blocked:**
- Report which step failed
- Provide error context
- List completed steps
- Indicate what's needed to proceed

## Weak Orchestrator Pattern

**Key characteristics:**

**Delegate, don't decide:**
- Orchestrator does NOT make judgment calls
- All decisions made during planning (/plan-adhoc)
- Execution is mechanical: invoke agent, check result, continue or escalate

**Trust agents:**
- If agent reports success, trust it
- If agent reports error, escalate according to plan
- Don't second-guess or validate agent output

**No inline logic:**
- Don't parse files to verify completion
- Don't make recovery decisions
- Don't modify steps during execution
- If something unexpected happens: escalate

**Error escalation only:**
- Simple errors → delegate to sonnet for fix
- Complex errors → stop and report to user
- Never suppress errors or proceed on failure

## Critical Constraints

**Tool Usage:**
- Use **Task** to invoke plan-specific agents
- Use **Read** to check artifacts and reports
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

Next: Delegate to vet-fix-agent to review and fix changes before committing."

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

## Integration with Workflows

**General workflow:**
1. `/design` - Opus creates design document
2. `/plan-adhoc` - Sonnet creates runbook and artifacts
3. `/orchestrate` - Haiku executes runbook (THIS SKILL)
4. vet-fix-agent - Review and fix changes before commit
5. Complete job

**TDD workflow reference:**
1. `/design` (TDD mode) - Opus creates design with TDD sections
2. `/plan-tdd` - Sonnet creates TDD runbook and artifacts
3. `/orchestrate` - Haiku executes TDD cycles (THIS SKILL)
4. vet-fix-agent - Review and fix changes
5. review-tdd-process - Analyze TDD process quality
6. Complete job

**Handoff:**
- Input: Prepared artifacts from `/plan-adhoc` or `/plan-tdd`
- Output: Executed steps with reports
- Next (general): Delegate to vet-fix-agent to review and fix changes
- Next (TDD): Delegate to vet-fix-agent, then review-tdd-process for process analysis

## References

**Example Orchestrator Plan**: `/Users/david/code/claudeutils/plans/unification/orchestrator-plan.md`
**Example Plan-Specific Agent**: `/Users/david/code/claudeutils/.claude/agents/unification-task.md`
**Example Step Files**: `/Users/david/code/claudeutils/plans/unification/steps/step-2-*.md`

These demonstrate the artifacts structure and execution pattern.

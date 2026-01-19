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
- prompt: "Execute step from: plans/<runbook-name>/steps/step-N.md"
- description: "Execute step N of runbook"
- model: [from orchestrator metadata, typically haiku]
```

**3.2 Check execution result:**

**Success indicators:**
- Agent returns completion message
- Report file created at expected path
- No error messages

**Failure indicators:**
- Agent reports error
- Missing report file
- Unexpected results mentioned

**3.3 On success:**
- Log step completion
- Continue to next step

**3.4 On failure:**
- Read error report
- Determine escalation level
- Escalate according to orchestrator plan

### 4. Error Escalation

**Escalation levels (from orchestrator metadata):**

**Level 1: Haiku → Sonnet**
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
- Report overall success
- List created artifacts
- Suggest next action (e.g., `/vet` to review changes, `/commit` to commit)

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

Next: Run `/vet` to review changes before committing."

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

**Scenario: Step succeeds but git shows unexpected changes**
- Action: Continue execution (don't inspect changes during orchestration)
- Reason: `/vet` skill reviews changes after execution
- Trust agent unless it reports error

## Integration with Oneshot Workflow

**Workflow stages:**
1. `/design` - Opus creates design document
2. `/plan-adhoc` - Sonnet creates runbook and artifacts
3. `/orchestrate` - Haiku executes runbook (THIS SKILL)
4. `/vet` - Review changes before commit
5. Complete job

**Handoff:**
- Input: Prepared artifacts from `/plan-adhoc`
- Output: Executed steps with reports
- Next: User invokes `/vet` to review changes

## References

**Example Orchestrator Plan**: `/Users/david/code/claudeutils/plans/unification/orchestrator-plan.md`
**Example Plan-Specific Agent**: `/Users/david/code/claudeutils/.claude/agents/unification-task.md`
**Example Step Files**: `/Users/david/code/claudeutils/plans/unification/steps/step-2-*.md`

These demonstrate the artifacts structure and execution pattern.

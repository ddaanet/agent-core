# Common Orchestration Scenarios

## Scenario: Step reports unexpected result but no error
- Action: Stop and report to user
- Reason: "Unexpected" means planning assumptions were wrong
- Do not proceed without user guidance

## Scenario: Report file missing after agent completes
- Action: Escalate to sonnet
- Reason: Likely agent error or path issue
- Sonnet can investigate and fix

## Scenario: Multiple steps fail with same error
- Action: After second failure, stop and report pattern to user
- Reason: Systemic issue, not one-off error
- User needs to update runbook or fix root cause

## Scenario: Agent never returns
- Action: Check task status with TaskOutput tool
- If hanging: Kill task and escalate to user
- If still running: Wait and check periodically

## Scenario: Resuming after context ceiling or kill
- Previous session hit token limit mid-execution. Fresh agent picks up.
- Action: Find last completed phase boundary (last checkpoint commit in git log)
- Run that checkpoint's verification commands from the runbook phase file
- Build complete inventory of remaining work from verification output
- Then resume from next step after the checkpoint
- Do NOT use `just precommit` as a state assessment tool -- it's a pass/fail gate, not a diagnostic. Use the runbook's checkpoint verification commands, which are designed to produce a complete inventory of what's done and what's missing.

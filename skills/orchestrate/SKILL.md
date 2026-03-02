---
name: orchestrate
description: Execute prepared runbooks with plan-specific agents and mechanical verification gates
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
---

# Execute Runbooks

Execute prepared runbooks through plan-specific agents. Sonnet orchestrator coordinates step dispatch, post-step verification, remediation, and phase boundary reviews. All common context (design, outline) lives in agent definitions — orchestrator provides file references only.

**Prerequisites:** Runbook prepared with `/runbook` (artifacts created by `prepare-runbook.py`)

## 1. Verify Runbook Preparation

```bash
ls -1 plans/<name>/orchestrator-plan.md
ls -1 .claude/agents/<name>-*.md 2>/dev/null
ls -1 plans/<name>/steps/step-*.md 2>/dev/null || true
```

**Required artifacts:**
- `plans/<name>/orchestrator-plan.md` — structured step list
- `.claude/agents/<name>-task.md` — general plans (or `<name>-tester.md` + `<name>-implementer.md` for TDD)
- `.claude/agents/<name>-corrector.md` — multi-phase plans only
- `plans/<name>/steps/step-*.md` — absent only for all-inline runbooks

Missing orchestrator plan → STOP. Missing step files with only `INLINE` entries → valid all-inline runbook. Missing step files with step references → STOP.

## 2. Read Orchestrator Plan

```
Read plans/<name>/orchestrator-plan.md
```

**Parse header fields:**
- `**Agent:**` — task agent name (or `none` for TDD)
- `**Corrector Agent:**` — corrector name (or `none` for single-phase)
- `**Type:**` — `tdd` or `general`
- `**Tester Agent:**` / `**Implementer Agent:**` — TDD only

**Parse `## Steps` section:** Pipe-delimited entries:
- General: `- step-N-M.md | Phase P | model | max_turns [| PHASE_BOUNDARY]`
- TDD: `- step-N-M-test.md | Phase P | model | max_turns | TEST [| PHASE_BOUNDARY]`
- TDD: `- step-N-M-impl.md | Phase P | model | max_turns | IMPLEMENT [| PHASE_BOUNDARY]`
- Inline: `- INLINE | Phase P | —`

**Execution mode:** STRICT SEQUENTIAL. One Task call per message. Steps modify shared state — parallel dispatch causes race conditions.

## 3. Execute Steps

For each entry in the `## Steps` list, branch by type:

### 3.0 Inline Execution (D-6)

Read the phase content from `plans/<name>/runbook-phase-P.md`. Execute edits directly — no Task dispatch.

1. Read target files, apply edits (Read → Edit/Write)
2. `just precommit` — fix failures, escalate if unfixable
3. Phase boundary review: ≤5 net lines across ≤2 files → self-review via `git diff`; larger → delegate to corrector (Section 3.5)
4. Commit inline phase changes

### 3.1 General Step Dispatch (D-2)

```
Task tool:
  subagent_type: [from **Agent:** header field]
  prompt: "Execute step from: plans/<name>/steps/<step-file>"
  model: [from step entry model field]
  max_turns: [from step entry max_turns field]
  description: "Step N-M: [step file name]"
```

Orchestrator provides file reference only. Agent definition caches design + outline — no inline content in prompt.

After dispatch → Section 3.3 (verification).

### 3.2 TDD Cycle Dispatch (D-5)

Per TDD cycle (paired TEST + IMPLEMENT entries):

**Step A — Dispatch tester:**
```
Task tool:
  subagent_type: [from **Tester Agent:** header]
  prompt: "Execute test spec from: plans/<name>/steps/<test-file>"
  model: [from step entry]
  max_turns: [from step entry]
```
Save agent ID for resume.

**Step B — RED gate:**
```bash
agent-core/skills/orchestrate/scripts/verify-red.sh <test_file_path>
```
- Exit 0 (test fails) → RED confirmed, proceed
- Exit 1 (test passes) → resume tester to fix, or escalate

**Step C — Test corrector:**
Dispatch `<name>-test-corrector` with changed files. Review test quality. If UNFIXABLE → STOP.

**Step D — Dispatch implementer:**
```
Task tool:
  subagent_type: [from **Implementer Agent:** header]
  prompt: "Execute implementation from: plans/<name>/steps/<impl-file>"
  model: [from step entry]
  max_turns: [from step entry]
```
Save agent ID for resume.

**Step E — GREEN gate:**
```bash
just test && agent-core/skills/orchestrate/scripts/verify-step.sh
```
- Both pass → proceed
- Test failure → resume implementer to fix, or escalate
- Dirty tree / precommit failure → remediate (Section 3.4)

**Step F — Impl corrector:**
Dispatch `<name>-impl-corrector` with changed files. Review implementation quality. If UNFIXABLE → STOP.

**Agent resume across cycles:** Resume tester for subsequent TEST steps (preserves test context). Resume implementer for subsequent IMPLEMENT steps (preserves codebase context). Fresh agent if >15 messages. Correctors are never resumed — each review is independent.

### 3.3 Post-Step Verification

```bash
agent-core/skills/orchestrate/scripts/verify-step.sh
```

- Exit 0 (CLEAN) → proceed to phase boundary check (Section 3.5)
- Exit 1 (DIRTY/SUBMODULE/PRECOMMIT) → remediate (Section 3.4)

### 3.4 Post-Step Remediation (D-3)

**Resume step agent** — it has context for fixing its own issues:
```
Task tool (resume):
  resume: [saved agent ID]
  prompt: "Your step left uncommitted changes or precommit failures. Fix and commit."
```
Skip resume if agent exchanged >15 messages (context near-full).

**If resume fails or skipped** — delegate recovery to fresh sonnet agent:
```
Task tool:
  subagent_type: "artisan"
  model: sonnet
  prompt: "[step file reference, git diff, git status, error output] Fix lint and commit issues."
```
Recovery is mechanical (lint-clean + git-clean). No design/outline context needed.

**After any remediation** — append RCA pending task:
`- [ ] **RCA: Step N dirty tree** — [brief description] | sonnet`

**If recovery fails** — escalate to user with full context (Section 4).

### 3.5 Phase Boundary

Read the phase field from the next step entry in the orchestrator plan (pipe-delimited format). If phase changes (or final step):

```bash
just precommit
git diff --name-only
```

**Delegate checkpoint to corrector:**
```
Task tool:
  subagent_type: [from **Corrector Agent:** header]
  prompt: |
    Phase P Checkpoint

    **First:** Run `just dev`, fix any failures, commit.

    **Scope:**
    - IN: [from Phase Summaries section]
    - OUT: [from Phase Summaries section]

    **Design reference:** plans/<name>/design.md
    **Review recall:** `Bash: claudeutils _recall resolve plans/<name>/recall-artifact.md` — if present, resolved content contains review-relevant entries. If absent or resolve fails: Read `memory-index.md`, identify review-relevant entries, batch-resolve via `claudeutils _recall resolve "when <trigger>" ...`.
    **Changed files:** [git diff --name-only output]

    Fix all issues. Write report to: plans/<name>/reports/checkpoint-P-review.md
    Return filepath or "UNFIXABLE: [description]"
```

Read report. If UNFIXABLE → STOP and escalate. Otherwise commit checkpoint, continue.

**Single-phase plans** (corrector = `none`): delegate to generic `corrector` with file references to design and outline (non-cached, read on demand).

**Final checkpoint** adds lifecycle audit: verify all stateful objects (MERGE_HEAD, staged content, lock files) cleared on success paths.

**Template enforcement:** IN/OUT scope lists must be non-empty. Changed files list must be present. Empty fields → STOP before delegating.

## 4. Error Escalation (D-4)

**2-level model:** Sonnet orchestrator handles execution-level issues (missing files, failed commands, dirty tree). Design-level issues escalate to user.

**Escalation prompt:**
```
Diagnose and fix from step N:
Error: [error message]
Step: [step objective]
Read step at: [step-path]
Write diagnostic to: plans/<name>/reports/step-N-diagnostic.md
Return: "fixed: [summary]" or "blocked: [what's needed]"
```

**Acceptance criteria:** Every resolution must pass precommit, leave clean tree, validate against step criteria.

**Execution bounds:** `max_turns` from orchestrator plan step entry — prevents spinning agents. Duration timeout deferred (platform gap).

## 5. Progress Tracking

Log each step: `Step N-M: [name] - completed` or `Step N-M: [name] - failed: [error]`

**Detailed tracking:** Read `references/progress-tracking.md` for optional progress file format.

## 6. Completion

```bash
git diff --name-only $(git log --all --oneline | tail -1 | cut -d' ' -f1)..HEAD
```

1. **Final review:** If multi-phase, phase boundary correctors already ran. Single-phase: delegate to generic `corrector` with design reference and changed files. Report to `plans/<name>/reports/review.md`.
2. **TDD audit:** If `**Type:** tdd`, delegate to `tdd-auditor`. Report to `plans/<name>/reports/tdd-process-review.md`.
3. **Cleanup:** Delete plan-specific agents:
   ```bash
   rm -f .claude/agents/<name>-task.md .claude/agents/<name>-corrector.md
   rm -f .claude/agents/<name>-tester.md .claude/agents/<name>-implementer.md
   rm -f .claude/agents/<name>-test-corrector.md .claude/agents/<name>-impl-corrector.md
   ```
4. **Deliverable review:** Create pending task:
   `- [ ] **Deliverable review: <name>** — /deliverable-review plans/<name> | opus | restart`
5. **Lifecycle entry:** Append `{YYYY-MM-DD} review-pending — /orchestrate` to `plans/<name>/lifecycle.md`.

## Continuation

This skill is **cooperative** with the continuation passing system. After completion, check Skill args suffix for `[CONTINUATION: ...]` transport. No continuation → use default-exit from frontmatter.

**Full protocol:** Read `references/continuation.md`.

## References

- **Verification scripts:** `agent-core/skills/orchestrate/scripts/verify-step.sh`, `verify-red.sh`
- **Common scenarios:** `references/common-scenarios.md`
- **Progress tracking:** `references/progress-tracking.md`
- **Continuation:** `references/continuation.md`

# TDD Workflow Guide

**Purpose:** Execute feature development using Test-Driven Development methodology.

## Overview

The TDD workflow implements the RED/GREEN/REFACTOR cycle for building features incrementally with test-first development. This workflow integrates with the oneshot workflow through shared orchestration infrastructure while maintaining TDD-specific protocols.

### When to Use TDD Workflow

**Use TDD workflow when:**
- Project has test-first culture
- User mentions "test", "TDD", or "red/green"
- Feature requires behavioral verification
- Project is pytest-md or similar test-focused codebase

**Use oneshot workflow instead when:**
- Infrastructure/migration work
- Refactoring without behavior change
- Prototype/exploration
- One-time fixes or cleanup tasks

### Integration with Oneshot Workflow

Both workflows share:
- `/design` skill (with mode-specific sections)
- `/orchestrate` execution engine (with runbook type detection)
- `/vet` review process
- Common orchestration patterns (weak orchestrator, plan-specific agents)

**Key difference:** TDD uses cycles (RED/GREEN/REFACTOR) instead of generic steps.

### Methodology Detection Signals

The `/oneshot` skill automatically detects TDD methodology based on:

| TDD Signal | General Signal |
|------------|----------------|
| Project has test-first culture | Infrastructure/migration work |
| User mentions "test", "TDD", "red/green" | Refactoring without behavior change |
| Feature requires behavioral verification | Prototype/exploration |
| Project is pytest-md or similar | One-time fixes |

---

## Workflow Stages

The TDD workflow follows this progression:

```
/design (TDD mode) → /plan-tdd → /orchestrate → /vet → Apply fixes → /review-analysis
```

### Stage 1: Design Session (TDD Mode)

**Skill:** `/design`
**Model:** Opus

**Purpose:** Create architectural specification with TDD-specific spike test section.

**TDD mode additions to design document:**
- **Spike Test section** - Verify current behavior, document framework defaults
- **`(REQUIRES CONFIRMATION)` markers** - Flag decisions needing user input
- **Flag reference table** - If adding CLI options
- **"What might already work" analysis** - Identify existing behavior

**Output:** Design document with TDD-specific sections consumed by `/plan-tdd`.

---

### Stage 2: TDD Planning

**Skill:** `/plan-tdd`
**Model:** Sonnet

**Purpose:** Create TDD runbook with RED/GREEN/REFACTOR cycles.

**Runbook structure:**
```markdown
---
name: feature-name
type: tdd
model: haiku
---

## Weak Orchestrator Metadata
- Runbook Type: TDD
- Total Cycles: N
- Execution Model: Haiku (tdd-task agent)
- Error Escalation: Haiku → Sonnet → User
- Report Locations: plans/<name>/reports/

## Common Context
[Shared knowledge for all cycles - design decisions, file paths, conventions]

## Cycle X.Y: [Description]

**Dependencies**: [Previous cycles or none]

### RED Phase
**Test**: [Test name and location]
**Assertions**: [Expected test assertions]
**Expected Failure**: [Exact failure message]

### GREEN Phase
**Implementation**: [Minimal implementation description]
**Files**: [Files to modify]
**Minimal**: [Guidance on minimal approach]

### Stop Conditions
- If RED passes unexpectedly: [Action]
- If GREEN fails after 2 attempts: [Action]
```

**Output:** Prepared TDD runbook ready for execution.

---

### Stage 3: TDD Execution

**Skill:** `/orchestrate`
**Model:** Haiku (weak orchestrator)

**Purpose:** Execute TDD cycles using tdd-task agent baseline.

**Execution pattern:**
1. `prepare-runbook.py` creates plan-specific agent from:
   - `agent-core/agents/tdd-task.md` (baseline protocol)
   - Runbook common context (design decisions, paths)
2. Orchestrator invokes plan-specific agent for each cycle
3. Agent executes full RED/GREEN/REFACTOR protocol
4. Structured log written to execution report

**Why agent-per-cycle:**
- Implementation agents benefit from broader context
- Each cycle gets fresh context (no accumulation)
- Solves TDD adherence through context isolation
- Consistent with general orchestration pattern

---

### Stage 4: Review

**Skill:** `/vet`
**Model:** Sonnet

**Purpose:** Review uncommitted changes before finalization.

**Scope:** All uncommitted changes from TDD execution.

**Activities:**
- Review all changes
- Identify issues (critical/major/minor)
- Classify fixes by urgency

**Fix application:**
- Critical/major issues → Apply fixes immediately
- Re-run `/vet` if significant changes made
- Minor issues → Document for future

---

### Stage 5: TDD Process Review

**Skill:** `/review-analysis`
**Model:** Sonnet

**Purpose:** Assess TDD compliance and process quality.

**Activities:**
- Compare planned cycles vs actual execution
- Assess adherence to RED/GREEN/REFACTOR protocol
- Identify process improvements
- Produce recommendations

**Future:** Uses claudeutils session extraction when available.

---

## TDD Cycle Structure

Each cycle follows strict RED/GREEN/REFACTOR protocol.

### RED Phase Protocol

**Objective:** Write failing test that specifies desired behavior.

**Steps:**
1. Write test exactly as specified in cycle definition
2. Run `just test` to execute test suite
3. Verify failure matches expected message from cycle spec
4. If test passes unexpectedly:
   - Check for `[REGRESSION]` marker in cycle spec
   - If not marked regression → STOP and report

**Success criteria:** Test fails with expected error message.

**Stop condition:** Unexpected pass (unless `[REGRESSION]` marker present).

---

### GREEN Phase Protocol

**Objective:** Write minimal implementation to make test pass.

**Steps:**
1. Write minimal implementation per cycle guidance
2. Run `just test` to verify new test passes
3. Run full test suite to check for regressions
4. Handle regressions individually (never batch multiple regression fixes)
5. If stuck after 2 attempts → STOP, mark BLOCKED, await guidance

**Success criteria:** New test passes, full suite passes (no regressions).

**Stop condition:** Unable to make test pass after 2 attempts.

---

### REFACTOR Phase Protocol (Mandatory)

**Objective:** Improve code quality while maintaining green tests.

**This phase is mandatory for every cycle** to ensure code quality is maintained throughout development.

**Step 1: Format & Lint**
```bash
just lint  # includes reformatting
```
Fix lint errors. Ignore complexity warnings and line limits (addressed in next steps).

**Step 2: Intermediate Commit (Rollback Point)**
```bash
git commit -m "WIP: Cycle X.Y [name]"
```
Creates rollback point before refactoring.

**Step 3: Quality Check**
```bash
just precommit  # validates green state BEFORE refactoring
```
Surfaces complexity warnings and line limit issues.

**Step 4: Refactoring Assessment (if warnings present)**

Determine appropriate handler based on warning type:

| Warning Type | Handler |
|--------------|---------|
| Common patterns (split module, simplify function) | Sonnet designs and executes |
| Architectural (new abstraction, multi-module impact) | Opus designs, decides escalation |
| New abstraction introduced | Opus, always escalate to human |

**Step 5: Execute Refactoring (if needed)**

See Refactoring Tiers section below for execution approach.

**Step 6: Post-Refactoring Updates (if code moved/renamed)**

Update all references to refactored code:
1. **Plans** - All designs and runbooks (`grep -r "old_ref" plans/`)
2. **Agent documentation** - Files in `agents/` (architecture, patterns, implementation)
3. **CLAUDE.md** - Only if behavioral rules affected (keep focused on behavior)
4. **Regenerate step files** - If runbook.md changed, re-run `prepare-runbook.py`

Verification: Use `grep` to confirm old references are gone.

**Step 7: Amend Commit**

Safety check before amending:
```bash
current_msg=$(git log -1 --format=%s)
if [[ "$current_msg" != WIP:* ]]; then
  echo "ERROR: Expected WIP commit, found: $current_msg"
  exit 1
fi
```

Amend and reword:
```bash
git commit --amend -m "Cycle X.Y: [name]"
```

**Goal:** Only precommit-validated states in commit history.

---

## Refactoring Tiers

When quality checks identify issues requiring refactoring, use tiered approach:

### Tier 1: Script-Based Refactoring

**Criteria:**
- Mechanical transformation
- Single pattern application
- No design judgment required

**Examples:**
- Split module by moving classes to new files
- Extract repeated code into helper function
- Rename variables for consistency

**Execution:**
- Sonnet writes transformation script
- Execute script directly (no orchestrator needed)
- Verify with `just precommit` after execution

**Why skip orchestrator:** Script-based refactoring is mechanical and verified by precommit. Orchestrator overhead not justified.

---

### Tier 2: Simple Runbook

**Criteria:**
- 2-5 steps required
- Minor design judgment needed
- Localized changes

**Examples:**
- Simplify complex function with multiple techniques
- Reorganize module structure with dependencies
- Extract and test new utility function

**Execution:**
- Create inline step list in cycle report
- Execute steps sequentially without prepare-runbook.py
- Verify with `just precommit` after completion

---

### Tier 3: Full Runbook

**Criteria:**
- 5+ steps required
- Design decisions embedded in execution
- Cross-cutting changes

**Examples:**
- Introduce new architectural abstraction
- Refactor multi-module subsystem
- Major restructuring with broad impact

**Execution:**
- Run `prepare-runbook.py` to create runbook artifacts
- Execute via `/orchestrate` with full orchestration
- Treat as nested runbook within TDD execution

**Note:** Tier 3 refactoring is rare. Most TDD refactoring is Tier 1 or 2.

---

## Commit Strategy

The TDD workflow uses WIP commits as rollback points with post-refactoring amends.

### Commit Flow Per Cycle

1. **After GREEN passes:** Create WIP commit
   ```bash
   git commit -m "WIP: Cycle X.Y [name]"
   ```

2. **Execute REFACTOR phase:** Lint, quality check, refactoring (if needed)

3. **Verify precommit passes:** Ensure all tests and checks pass

4. **Amend WIP commit:** Replace WIP with final message
   ```bash
   git commit --amend -m "Cycle X.Y: [name]"
   ```

### Safety Checks Before Amend

**Always verify WIP commit exists:**
```bash
current_msg=$(git log -1 --format=%s)
if [[ "$current_msg" != WIP:* ]]; then
  echo "ERROR: Expected WIP commit, found: $current_msg"
  exit 1
fi
```

### Rationale

- **Rollback safety:** WIP commit provides known-good state
- **Clean history:** Only precommit-validated states in commit history
- **Refactoring confidence:** Can reset to WIP if refactoring breaks tests

---

## Command Reference

Test and quality check commands used throughout TDD workflow:

| Command | Purpose | Used In |
|---------|---------|---------|
| `just test` | Run test suite | RED/GREEN phases |
| `just lint` | Lint + reformat code | REFACTOR phase (post-GREEN) |
| `just precommit` | Check + test (no reformat) | REFACTOR phase (validate before/after refactoring) |

**Note:** These are hardcoded initially. Project-specific configuration is TODO.

### Command Details

**`just test`**
- Runs test suite (typically pytest)
- Used to verify RED (expect failure) and GREEN (expect pass)
- Single test or full suite depending on phase

**`just lint`**
- Runs linter (ruff, pylint, etc.)
- Reformats code automatically
- Used immediately after GREEN to clean up formatting

**`just precommit`**
- Runs all checks without reformatting
- Includes: lint checks, complexity warnings, line limits, tests
- Used before and after refactoring to validate quality

---

## Stop Conditions and Escalation

### Stop Conditions

Agent stops and reports when encountering:

| Condition | Action |
|-----------|--------|
| RED passes unexpectedly (no `[REGRESSION]` marker) | STOP - Investigate why test passes |
| GREEN fails after 2 attempts | STOP - Mark BLOCKED, await guidance |
| Refactoring breaks tests | STOP - Keep state for diagnostic (no auto-reset) |
| Architectural refactoring detected | Escalate to Opus (Opus decides human escalation) |
| New abstraction introduced | Always escalate to human for approval |

### Escalation Chain

| Result | Action |
|--------|--------|
| `success` | Proceed to next cycle |
| `quality-check: warnings found` | Escalate to Sonnet for refactoring design |
| `architectural-refactoring` | Escalate to Opus (Opus decides human escalation) |
| `blocked: [reason]` | Standard escalation (Sonnet → User) |
| `error: [details]` | Standard escalation |
| `refactoring-failed` | STOP - Write diagnostic report, keep state |

---

## Integration Points

### Differences from Oneshot Workflow

| Aspect | Oneshot Workflow | TDD Workflow |
|--------|------------------|--------------|
| **Unit of work** | Steps | Cycles (RED/GREEN/REFACTOR) |
| **Planning skill** | `/plan-adhoc` | `/plan-tdd` |
| **Baseline agent** | `quiet-task.md` | `tdd-task.md` |
| **Execution focus** | Sequential steps | Test-first development |
| **Refactoring** | Optional | Mandatory per cycle |
| **Commit strategy** | Per step or milestone | WIP + amend per cycle |
| **Post-execution** | `/vet` only | `/vet` + `/review-analysis` |

### When to Use Each Workflow

**Use TDD workflow for:**
- Feature development requiring tests
- Projects with test-first culture
- Behavioral verification needed
- Incremental feature building

**Use oneshot workflow for:**
- Infrastructure setup
- Data migrations
- Refactoring existing code
- One-time fixes
- Prototypes/exploration

### Transition Between Workflows

**From TDD to Oneshot:**
- Complete TDD execution and process review
- Switch to oneshot for infrastructure/migration work
- Use `/oneshot` to start new oneshot task

**From Oneshot to TDD:**
- Complete oneshot execution and review
- Switch to TDD for feature development
- Use `/oneshot` (detects TDD methodology) or `/design` (TDD mode)

---

## Structured Log Entry

After each cycle, tdd-task agent appends to execution report:

```markdown
### Cycle X.Y: [name] [timestamp]
- Status: RED_VERIFIED | GREEN_VERIFIED | STOP_CONDITION | REGRESSION
- Test command: `[exact command]`
- RED result: [FAIL as expected | PASS unexpected | N/A]
- GREEN result: [PASS | FAIL - reason]
- Regression check: [N/N passed | failures]
- Refactoring: [none | description]
- Files modified: [list]
- Stop condition: [none | description]
- Decision made: [none | description]
```

This structured format enables:
- Process review analysis
- Debugging failed cycles
- TDD compliance assessment
- Progress tracking across sessions

---

## Related Documentation

- **CLAUDE.md**: Agent instructions, communication rules, patterns
- **agents/oneshot-workflow.md**: Oneshot workflow documentation
- **agents/context.md**: Current task context and architecture
- **agents/design-decisions.md**: Architectural decisions and rationale
- **agents/session.md**: Current session handoff context
- **agents/tdd-task.md**: TDD task agent baseline template

---

## Change Log

**2026-01-19**: Initial TDD workflow documentation

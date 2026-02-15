---
name: review-plan
description: |
  Reviews runbook phase files for quality, TDD discipline (if TDD), step quality (if general),
  and LLM failure modes (always). Detects prescriptive code in GREEN phases, validates RED/GREEN
  sequencing, checks prerequisite validation, script evaluation, and step clarity.

  Use when reviewing runbooks after generation by /plan. Use when the user asks to "review runbook",
  "check runbook for prescriptive code", "validate RED/GREEN discipline", "check for implementation
  anti-patterns", "check LLM failure modes", or when /plan Phase 1/3 delegates to plan-reviewer agent.
user-invocable: false
model: sonnet
---

# /review-plan Skill

Review runbook phase files, fix all issues, and report findings (audit trail + escalation).

---

## Purpose

**Review agent behavior:** Write review (audit trail) → Fix ALL issues → Escalate unfixable

**What this skill does:**
- Detects prescriptive implementation code in GREEN phases (TDD)
- Identifies RED/GREEN sequencing violations (TDD)
- Validates prerequisite validation and step clarity (general)
- Checks script evaluation and conformance (general)
- Detects LLM failure modes: vacuity, ordering, density, checkpoints, file growth (all)
- Validates file references and metadata accuracy (all)
- **Fixes ALL issues directly** (critical, major, minor)
- **Reports unfixable issues** for caller escalation

**Why review even when fixing:** The review report is an audit trail. It documents what was wrong and what was fixed, enabling process improvement and deviation monitoring.

---

## Document Validation

Accept both TDD and general artifacts:
- **TDD:** `type: tdd` in phase metadata or `## Cycle` / `### Cycle` headers
- **General:** `## Step` / `### Step` headers or no type marker (default: general)
- **Mixed:** Both header types across phases — valid (per-phase type tagging)

---

## Review Criteria

### 1. GREEN Phase Anti-Pattern (CRITICAL) — TDD phases only

**Violation:** GREEN phase contains implementation code

```markdown
**GREEN Phase:**

**Implementation**: Add load_config() function

```python
def load_config(config_path: Path) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config
```
```

**Why this is wrong:**
- Prescribes exact code
- Agent becomes code copier, not implementer
- Test doesn't drive implementation
- Violates TDD RED→GREEN discovery

**Correct approach:**

```markdown
**GREEN Phase:**

**Implementation**: Minimal load_config() to pass tests

**Behavior:**
- Read YAML file from config_path
- Return parsed dict
- Must pass test assertions from RED phase

**Hint**: Use yaml.safe_load(), Path.open()
```

### 2. RED/GREEN Sequencing — TDD phases only

**Check:** Will test actually fail in RED phase before GREEN implementation?

**Common violations:**
- Complete function signatures in first cycle (tests pass immediately)
- All parameters/features added at once (no incremental RED→GREEN)
- Error handling in "minimal" implementation (should be separate cycle)

**Correct pattern:**
- Cycle X.1: Minimal happy path only
- Cycle X.2: Add error handling
- Cycle X.3: Add optional parameters
- Cycle X.4: Add validation modes

### 3. Implementation Hints vs Prescription — TDD phases only

**Acceptable:** Implementation hints for sequencing

```markdown
**Implementation Hint**: Happy path only - no error handling, no validation
```

**Violation:** Prescriptive code blocks

```python
# This tells agent EXACTLY what to write
def compose(fragments, output):
    # Implementation here
```

### 4. Test Specifications — TDD phases only

**Must have:**
- Specific test name
- Expected failure message
- File location
- Why it will fail

**Good example:**
```markdown
**Expected failure:**
```
ImportError: cannot import name 'compose' from 'claudeutils.compose'
```

**Why it fails**: Function doesn't exist yet
```

### 5. Weak RED Phase Assertions (CRITICAL) — TDD phases only

**Violation:** RED test prose only verifies structure, not behavior

**Indicators (prose format):**
- Prose says "returns correct value" without specifying what value
- Prose says "handles error" without specifying error type/message
- Prose says "processes correctly" without expected output
- No specific values, patterns, or behaviors specified

**Indicators (legacy code format):**
- Test only checks `exit_code == 0` or `exit_code != 0`
- Test only checks key existence (`"KEY" in dict`) without value verification
- Test only checks class/method existence (would pass with `pass` body)
- Test has no mocking for I/O-dependent behavior

**Check:** For each RED phase, ask: "Could an executor write different tests that all satisfy this description?" If yes → VIOLATION: prose too vague

**Correct prose pattern:**
- Specific values: "returns string containing 🥈 emoji"
- Specific errors: "raises ValueError with message 'invalid input'"
- Specific structure: "output dict contains 'count' key with integer > 0"
- Mock requirements: "mock keychain, verify get_password called with service='claude'"

### 5.5. Prose Test Quality — TDD phases only

**Violation:** RED phase uses full test code instead of prose description

**Check:** Scan RED phases for python code blocks containing test implementations

**Indicators:**
- `def test_*():` pattern in RED phase code block
- `assert` statements in code blocks (not in prose)
- Complete test function with imports and fixtures

**Acceptable in RED:**
- Prose test descriptions with specific assertions
- Expected failure message/pattern (in code block OK)
- Fixture setup hints (prose, not code)

**Not acceptable:**
- Complete pytest function implementations
- Multiple assert statements in code blocks
- Full test file content

### 6. Metadata Accuracy — all phases

**Check:** `Total Steps` in Weak Orchestrator Metadata matches actual cycle/step count
- Count all `## Cycle X.Y:` / `### Cycle X.Y:` headers (TDD)
- Count all `## Step N.M:` / `### Step N.M:` headers (general)
- Compare to metadata value
- If mismatch → VIOLATION: metadata inaccurate

**Check:** Restart-reason verification
- For each phase claiming "Restart required: Yes", verify the stated reason matches restart trigger rules
- **Restart triggers:** agent definitions (`.claude/agents/`), hook configuration, plugin changes, MCP server configuration
- **NOT restart triggers:** decision documents, skills, fragments loaded on-demand via `/when` recall
- **Distinction:** `@`-referenced files have content loaded at startup (restart needed); indexed-but-recalled files load on-demand (no restart)
- **Detection:** Grep phase headers for "Restart required: Yes", cross-reference artifact type against trigger rules
- If reason invalid → VIOLATION: incorrect restart metadata (false restart delays execution)

### 7. Empty-First Cycle Ordering — TDD phases only

**Warning:** First cycle in a phase tests empty/degenerate case

**Check:** Does Cycle X.1 test empty input, no-op, or missing data?
- If empty case requires special handling → acceptable
- If empty case arises naturally from list processing → WARNING: reorder to test simplest happy path first

### 8. Consolidation Quality — all phases

**Check:** Merged cycles/steps maintain isolation

**Indicators of bad consolidation:**
- Merged item has >5 assertions (overloaded)
- Setup/teardown conflicts in same cycle/step
- Unrelated domains merged (forced grouping)
- Phase preamble contains testable behavior (should be a cycle/step)

**Check:** Trivial work placement

**Good patterns:**
- Config constants as phase preamble
- Import additions as setup instructions
- Single-file trivial changes merged with adjacent same-file item

**Bad patterns:**
- Trivial items left isolated (should merge or inline)
- Testable behavior hidden in preamble (needs assertion/verification)
- Cross-phase merges (never allowed)

### 9. File Reference Validation (CRITICAL) — all phases

**Violation:** Runbook references file paths that don't exist in the codebase

**Check:** Extract all file paths from:
- Common Context "Project Paths" section
- RED phase "Verify RED" commands / step verification commands
- GREEN phase "Changes" file references / step implementation paths
- Verification commands (pytest, grep, etc.)

**For each path:** Use Glob to verify the file exists. If not found, try fuzzy match.

**Classification:**
- File doesn't exist and no similar file found → CRITICAL: path fabricated
- File doesn't exist but similar files found → CRITICAL: wrong path (suggest correct files)
- Test function referenced doesn't exist in target file → CRITICAL: function not found (use Grep to locate)

### 10. General Phase Step Quality — general phases only

**10.1 Prerequisite Validation**
- Creation steps (new code touching existing paths) MUST have investigation prerequisites
- Format: `**Prerequisite:** Read [file:lines] — understand [behavior/flow]`
- Transformation steps (delete, move, rename) are exempt

**10.2 Script Evaluation**
- Steps classify size: small (≤25 lines inline), medium (25-100 prose), large (>100 separate planning)
- Verify classification matches actual step complexity
- Flag steps claiming "small" with >25 lines of inline content

**10.3 Step Clarity**
- Each step has: Objective, Implementation, Expected Outcome
- No "determine"/"evaluate options"/"choose between" language (decisions resolved at planning)
- Error conditions and validation criteria specified

**10.4 Conformance Validation**
- When design references external spec: validation steps verify conformance
- Exact expected strings from reference, not abstracted descriptions

### 11. LLM Failure Modes (CRITICAL) — all phases

Criteria from `agents/decisions/runbook-review.md` (five axes). Apply regardless of phase type.

**11.1 Vacuity**
- **TDD:** Cycles where RED can pass with `assert callable(X)` or `import X`
- **TDD:** Integration wiring items where called function already tested
- **General:**
  - Scaffolding-only steps (file creation, directory setup) without functional outcome
  - Step N+1 produces outcome achievable by extending step N alone — merge
  - Consecutive steps modifying same artifact with composable changes
- **Heuristic (both):** items > LOC/20 signals consolidation needed
- Fix: Merge into nearest behavioral cycle/step

**11.2 Dependency Ordering**
- Foundation-first within phases (all types): existence → structure → behavior → refinement
- **TDD:** Item N tests behavior depending on structure from item N+k (k>0)
- **General:**
  - Steps referencing structures or output from later steps
  - Prerequisites not validated before use (step assumes prior state without check)
  - Foundation-after-behavior inversions (behavioral step before the foundational step it depends on)
- Fix: Reorder within phase. If cross-phase: UNFIXABLE (outline revision needed)

**11.3 Density**
- **TDD:** Adjacent cycles testing same function with <1 branch point difference; single edge cases expressible as parametrized row in prior cycle
- **General:**
  - Adjacent steps on same artifact with <20 LOC delta
  - Multi-step sequences collapsible to single step (shared validation, no intermediate checkpoint needed)
  - Over-granular decomposition without clear boundary (steps split by file section rather than behavioral concern)
- Entire phases with ≤3 items, all Low complexity
- Fix: Merge adjacent, parametrize edge cases, collapse trivial phases

**11.4 Checkpoint Spacing**
- Gaps >10 items or >2 phases without checkpoint
- Complex data manipulation phases without checkpoint
- Fix: Insert checkpoint recommendation

**11.5 File Growth**
- Project lines added per item from descriptions
- Flag when projected size exceeds 350 lines (400-line enforcement threshold minus buffer)
- Fix: Insert proactive file split at phase boundary before projected threshold breach

---

## Review Process

### Phase 1: Scan and Classify

**1a. Determine phase type(s):**
- Scan for `## Cycle` / `### Cycle` headers → TDD
- Scan for `## Step` / `### Step` headers → general
- Mixed is valid — apply type-appropriate criteria per phase

**1b. Check GREEN phases for implementation code (TDD):**

Use Grep tool to find code blocks in GREEN phases:

**Pattern:** `^\*\*GREEN Phase:\*\*`
**Context:** Use -A 20 to see 20 lines after each match
**Secondary check:** Look for ` ```python` markers in context

**For each code block found:**
1. Check if it's implementation code (not test code)
2. Check if it's in GREEN phase
3. Mark as VIOLATION

**1c. Check RED phases for full test code (TDD):**

**Pattern:** `^\*\*RED Phase:\*\*`
**Context:** Use -A 30 to see test content
**Check for:** `def test_.*\(\):` pattern inside code blocks

**1d. Check step quality (general):**
- Verify prerequisite validation for creation steps
- Check script evaluation size classification
- Verify step structure (Objective, Implementation, Expected Outcome)

### Phase 2: Validate File References

Extract all file paths referenced in the runbook. For each path:

1. Use Glob to check existence
2. If not found, search for similar files
3. Use Grep to verify referenced functions exist in their target files
4. Mark missing paths as CRITICAL violations with suggested corrections

### Phase 3: Analyze Items

**For TDD cycles:**
1. Extract RED phase: What test assertions (prose or code)?
2. Validate prose quality: Are assertions behaviorally specific?
3. Extract GREEN phase: What implementation guidance?
4. Check sequence: Will RED fail before GREEN?

**For general steps:**
1. Check prerequisite validation presence
2. Verify step has clear objective and expected outcome
3. Check for deferred decisions ("determine", "evaluate options")
4. Validate conformance references if spec-based

**For all items:**
1. Check LLM failure modes (vacuity, ordering, density, checkpoints)
2. Verify metadata accuracy
3. Check consolidation quality

### Phase 4: Apply Fixes

**Fix-all policy:** Apply ALL fixes (critical, major, AND minor) directly to the runbook/phase file.

**Fix process:**
1. For each violation identified:
   - Determine if fixable (most are) or requires escalation (design gaps, scope issues)
   - Apply fix using Edit tool
   - Document fix in report with Status: FIXED
2. For unfixable issues:
   - Mark clearly in report with Status: UNFIXABLE
   - Explain why (missing design decision, scope conflict, etc.)
   - These require caller escalation

**Common fixes:**
- **Prescriptive code in GREEN:** Replace with behavior description + hints
- **Vague prose in RED:** Add specific expected values/patterns
- **Missing prerequisites (general):** Add investigation prerequisite
- **Deferred decisions (general):** Resolve inline or UNFIXABLE if design gap
- **Sequencing violation:** Note in report, suggest cycle restructuring (may need outline revision → UNFIXABLE)
- **Trivial items not consolidated:** Merge or inline trivial work
- **Metadata mismatch:** Update Total Steps count
- **File path errors:** Correct paths or mark for verification
- **Vacuous items:** Merge into nearest behavioral item
- **Density issues:** Collapse adjacent, parametrize edge cases

**Fix constraints:**
- Preserve item intent and scope
- Don't change requirements coverage
- Don't add new cycles/steps (escalate if needed)
- Keep behavioral descriptions accurate to design

### Phase 5: Generate Report

**Structure:**

```markdown
# Runbook Review: {name}

**Artifact**: [path]
**Date**: [ISO timestamp]
**Mode**: review + fix-all
**Phase types**: [TDD | General | Mixed (N TDD, M general)]

## Summary
- Total items: N (cycles: X, steps: Y)
- Issues found: N critical, N major, N minor
- Issues fixed: N
- Unfixable (escalation required): N
- Overall assessment: Ready | Needs Escalation

## Critical Issues

### Issue 1: [description]
**Location**: [cycle/step, line range]
**Problem**: [what's wrong]
**Fix**: [what was done]
**Status**: FIXED | UNFIXABLE (reason)

## Major Issues
[same format]

## Minor Issues
[same format]

## Fixes Applied
- [list of all fixes applied]

## Unfixable Issues (Escalation Required)
[numbered list with rationale, or "None — all issues fixed"]
```

---

## Output Format

**Report file:** plans/<feature-name>/reports/runbook-review.md (or phase-N-review.md for phase files)

**Return to caller:** Filepath only (or with escalation note)

**On success (all issues fixed):**
```
plans/<feature>/reports/runbook-review.md
```

**On success with unfixable issues:**
```
plans/<feature>/reports/runbook-review.md
ESCALATION: 2 unfixable issues require attention (see report)
```

**On failure:**
```
Error: [What failed]
Details: [Error message]
Context: [What was being attempted]
Recommendation: [What to do]
```

---

## Invocation

**Automatic:** /plan Phase 1 (per-phase) and Phase 3 (final) delegate to plan-reviewer agent
**Manual:** Delegate to plan-reviewer agent with runbook/phase file path

---

## Integration

**Workflow:**
```
/design → /plan → plan-reviewer agent (fix-all) → [escalate if needed] → prepare-runbook.py → /orchestrate
```

**Automatic review:** /plan Phase 1 triggers per-phase review, Phase 3 triggers final holistic review

**Escalation path:** If ESCALATION noted in return, caller must address unfixable issues before proceeding

---

## Key Principles

1. **Tests drive implementation** — Not scripts (TDD)
2. **Minimal means minimal** — One behavior per cycle (TDD)
3. **RED must fail** — Before GREEN can pass (TDD)
4. **Describe behavior** — Not code (TDD)
5. **Provide hints** — Not solutions (TDD)
6. **Prerequisites ground execution** — Investigation before creation (general)
7. **Decisions resolved at planning** — No deferred choices (general)
8. **Foundation-first ordering** — Existence → structure → behavior (all)
9. **Fix everything** — Review agents fix, not just report (all)
10. **Escalate unfixable** — Clear communication of blockers (all)

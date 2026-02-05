---
name: review-tdd-plan
description: This skill should be used when reviewing TDD runbooks after generation by /plan-tdd. Use when the user asks to "review TDD runbook", "check runbook for prescriptive code", "validate RED/GREEN discipline", "check for implementation anti-patterns", or when /plan-tdd Phase 3/5 delegates to tdd-plan-reviewer agent. Detects GREEN phases containing exact implementation code (violates TDD principles) and validates proper RED/GREEN sequencing.
user-invocable: false
model: sonnet
---

# /review-tdd-plan Skill

Review TDD runbooks, fix all issues, and report findings (audit trail + escalation).

---

## Purpose

**Review agent behavior:** Write review (audit trail) → Fix ALL issues → Escalate unfixable

**Critical anti-pattern:** Runbooks that prescribe exact implementation code violate TDD principles. Tests should drive implementation, not scripts.

**What this skill does:**
- Detects prescriptive implementation code in GREEN phases
- Identifies RED/GREEN sequencing violations
- Checks for proper minimal implementation guidance
- Validates stop conditions and error handling
- **Fixes ALL issues directly** (critical, major, minor)
- **Reports unfixable issues** for caller escalation

**Why review even when fixing:** The review report is an audit trail. It documents what was wrong and what was fixed, enabling process improvement and deviation monitoring.

**Target users:** T2 agents (sonnet for review)

---

## Review Criteria

### 1. GREEN Phase Anti-Pattern (CRITICAL)

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

### 2. RED/GREEN Sequencing

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

### 3. Implementation Hints vs Prescription

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

### 4. Test Specifications

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

### 5. Weak RED Phase Assertions (CRITICAL)

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

### 5.5. Prose Test Quality (NEW)

**Violation:** RED phase uses full test code instead of prose description

**Check:** Scan RED phases for python code blocks containing test implementations

**Indicators:**
- `def test_*():` pattern in RED phase code block
- `assert` statements in code blocks (not in prose)
- Complete test function with imports and fixtures

**Why this matters:**
- Full test code wastes planning tokens
- Haiku executors can generate tests from prose
- Prose is easier to review for behavioral coverage

**Acceptable in RED:**
- Prose test descriptions with specific assertions
- Expected failure message/pattern (in code block OK)
- Fixture setup hints (prose, not code)

**Not acceptable:**
- Complete pytest function implementations
- Multiple assert statements in code blocks
- Full test file content

### 6. Metadata Accuracy

**Check:** `Total Steps` in Weak Orchestrator Metadata matches actual cycle count
- Count all `## Cycle X.Y:` or `### Cycle X.Y:` headers
- Compare to metadata value
- If mismatch → VIOLATION: metadata inaccurate

### 7. Empty-First Cycle Ordering

**Warning:** First cycle in a phase tests empty/degenerate case

**Check:** Does Cycle X.1 test empty input, no-op, or missing data?
- If empty case requires special handling → acceptable
- If empty case arises naturally from list processing → WARNING: reorder to test simplest happy path first

### 8. Consolidation Quality

**Check:** Merged cycles maintain test isolation

**Indicators of bad consolidation:**
- Merged cycle has >5 assertions (overloaded)
- Setup/teardown conflicts in same cycle
- Unrelated domains merged (forced grouping)
- Phase preamble contains testable behavior (should be a cycle)

**Check:** Trivial work placement

**Good patterns:**
- Config constants as phase preamble
- Import additions as setup instructions
- Single-file trivial changes merged with adjacent same-file cycle

**Bad patterns:**
- Trivial cycles left isolated (should merge or inline)
- Testable behavior hidden in preamble (needs assertion)
- Cross-phase merges (never allowed)

**Why this matters:** Consolidation reduces orchestrator overhead but shouldn't sacrifice test isolation. Bad merges create flaky tests or miss coverage.

---

### 9. File Reference Validation (CRITICAL)

**Violation:** Runbook references file paths that don't exist in the codebase

**Check:** Extract all file paths from:
- Common Context "Project Paths" section
- RED phase "Verify RED" commands (e.g., `pytest tests/test_foo.py`)
- GREEN phase "Changes" file references
- GREEN phase "Verify GREEN" and "Verify no regression" commands

**For each path:** Use Glob to verify the file exists. If not found, try fuzzy match (e.g., `tests/test_account*.py` when `tests/test_account.py` is referenced).

**Classification:**
- File doesn't exist and no similar file found → CRITICAL: path fabricated
- File doesn't exist but similar files found → CRITICAL: wrong path (suggest correct files)
- Test function referenced doesn't exist in target file → CRITICAL: function not found (use Grep to locate)

**Why this matters:** Runbooks with wrong file paths fail immediately at execution. This is a complete blocker, not a quality issue.

---

## Review Process

### Phase 1: Scan for Code Blocks

**1a. Check GREEN phases for implementation code:**

Use Grep tool to find code blocks in GREEN phases:

**Pattern:** `^\*\*GREEN Phase:\*\*`
**Context:** Use -A 20 to see 20 lines after each match
**Secondary check:** Look for ` ```python` markers in context

**For each code block found:**
1. Check if it's implementation code (not test code)
2. Check if it's in GREEN phase
3. Mark as VIOLATION

**1b. Check RED phases for full test code (new check):**

**Pattern:** `^\*\*RED Phase:\*\*`
**Context:** Use -A 30 to see test content
**Check for:** `def test_.*\(\):` pattern inside code blocks

**For full test functions found:**
1. Check if it's a complete test implementation (not just expected failure)
2. If complete test with multiple asserts → VIOLATION: use prose instead
3. Exception: Expected failure message snippets are OK

### Phase 2: Validate File References

Extract all file paths referenced in the runbook (Common Context, RED/GREEN phases, verify commands). For each path:

1. Use Glob to check existence
2. If not found, search for similar files (e.g., `tests/test_account*.py`)
3. Use Grep to verify referenced test functions exist in their target files
4. Mark missing paths as CRITICAL violations with suggested corrections

**This phase catches runbooks generated with stale or assumed file paths.**

### Phase 3: Analyze Cycles

**For each cycle (X.Y):**

1. **Extract RED phase:** What test assertions (prose or code)?
2. **Validate prose quality:** Are assertions behaviorally specific?
3. **Extract GREEN phase:** What implementation guidance?
4. **Check sequence:** Will RED fail before GREEN?

**Prose quality check:**
- Each assertion specifies concrete expected value or pattern
- Not vague ("works correctly", "handles error")
- Could haiku write the test from this prose? If unclear → WARNING

**Sequencing check:**
- If cycle X.1 includes complete signature + error handling → VIOLATION
- If cycle X.1 includes all features → VIOLATION
- If "minimal implementation" has 10+ lines → WARNING

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
- **Sequencing violation:** Note in report, suggest cycle restructuring (may need outline revision → UNFIXABLE)
- **Trivial cycles not consolidated:** Merge or inline trivial work
- **Metadata mismatch:** Update Total Steps count
- **File path errors:** Correct paths or mark for verification

**Fix constraints:**
- Preserve cycle intent and scope
- Don't change requirements coverage
- Don't add new cycles (escalate if needed)
- Keep behavioral descriptions accurate to design

### Phase 5: Generate Report

**Structure:**

```markdown
# TDD Runbook Review: {name}

**Artifact**: [path]
**Date**: [ISO timestamp]
**Mode**: review + fix-all

## Summary
- Total cycles: N
- Issues found: N critical, N major, N minor
- Issues fixed: N
- Unfixable (escalation required): N
- Overall assessment: Ready | Needs Escalation

## Critical Issues

### Issue 1: GREEN phase contains implementation code
**Location**: Cycle 2.1, line 490-528
**Problem**: Complete load_config() implementation prescribed
**Fix**: Replaced with behavior description
**Status**: FIXED

### Issue 2: RED/GREEN sequencing violation
**Location**: Cycle 3.1
**Problem**: "Minimal" implementation includes all features
**Fix**: N/A - requires outline restructuring
**Status**: UNFIXABLE (escalation: cycle decomposition needed)

## Major Issues

### Issue 1: Vague prose in RED phase
**Location**: Cycle 1.2
**Problem**: "returns correct value" without specifying value
**Fix**: Added specific assertion: "returns string containing 🥈 emoji"
**Status**: FIXED

## Minor Issues

### Issue 1: Metadata mismatch
**Location**: Weak Orchestrator Metadata
**Problem**: Total Steps says 12, actual count is 14
**Fix**: Updated to 14
**Status**: FIXED

## Fixes Applied

- Cycle 2.1 GREEN: Replaced implementation code with behavior description
- Cycle 1.2 RED: Strengthened prose assertions
- Metadata: Corrected Total Steps count

## Unfixable Issues (Escalation Required)

1. **Cycle 3.1 sequencing** — Requires outline revision to split into incremental cycles
   - Recommendation: Return to runbook outline, decompose Phase 3

(If none: "None — all issues fixed")

## Recommendations
   - Cycle X.1: Happy path only
   - Cycle X.2: Error handling
   - Cycle X.3: Optional features

3. **Add implementation hints where sequencing matters**
   - "Happy path only - no error handling"
   - "Hardcoded separator '\n---\n\n'"
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

**Automatic:** /plan-tdd Phase 3 (per-phase) and Phase 5 (final) delegate to tdd-plan-reviewer agent
**Manual:** Delegate to tdd-plan-reviewer agent with runbook/phase file path

---

## Integration

**Workflow:**
```
/design (TDD mode) → /plan-tdd → tdd-plan-reviewer agent (fix-all) → [escalate if needed] → prepare-runbook.py → /orchestrate
```

**Automatic review:** /plan-tdd Phase 3 triggers per-phase review, Phase 5 triggers final holistic review

**Escalation path:** If ESCALATION noted in return, caller must address unfixable issues before proceeding

---

## Key Principles

1. **Tests drive implementation** - Not scripts
2. **Minimal means minimal** - One behavior per cycle
3. **RED must fail** - Before GREEN can pass
4. **Describe behavior** - Not code
5. **Provide hints** - Not solutions
6. **Fix everything** - Review agents fix, not just report
7. **Escalate unfixable** - Clear communication of blockers

---

**Created**: 2026-01-26
**Updated**: 2026-02-05
**Purpose**: Prevent prescriptive TDD runbooks, ensure proper RED/GREEN discipline, autofix all issues

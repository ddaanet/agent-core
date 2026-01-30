---
name: review-tdd-plan
description: This skill should be used when reviewing TDD runbooks after generation by /plan-tdd. Use when the user asks to "review TDD runbook", "check runbook for prescriptive code", "validate RED/GREEN discipline", "check for implementation anti-patterns", or when /plan-tdd Phase 5 delegates to tdd-plan-reviewer agent. Detects GREEN phases containing exact implementation code (violates TDD principles) and validates proper RED/GREEN sequencing.
user-invocable: false
model: sonnet
---

# /review-tdd-plan Skill

Review TDD runbooks to ensure proper RED/GREEN discipline and non-prescriptive implementation guidance.

---

## Purpose

**Critical anti-pattern:** Runbooks that prescribe exact implementation code violate TDD principles. Tests should drive implementation, not scripts.

**What this skill does:**
- Detects prescriptive implementation code in GREEN phases
- Identifies RED/GREEN sequencing violations
- Checks for proper minimal implementation guidance
- Validates stop conditions and error handling

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

**Violation:** RED test only verifies structure, not behavior

**Indicators:**
- Test only checks `exit_code == 0` or `exit_code != 0`
- Test only checks key existence (`"KEY" in dict`) without value verification
- Test only checks class/method existence (would pass with `pass` body)
- Test has no mocking for I/O-dependent behavior

**Check:** For each RED phase, ask: "Would a stub that returns a constant/empty value pass this test?" If yes → VIOLATION: weak assertion

**Correct pattern:**
- Assert on output content, mock interactions, or computed values
- Mock external dependencies and verify interaction
- Use fixtures for filesystem state

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

---

## Review Process

### Phase 1: Scan for Code Blocks

Use Grep tool to find code blocks in GREEN phases:

**Pattern:** `^\*\*GREEN Phase:\*\*`
**Context:** Use -A 20 to see 20 lines after each match
**Secondary check:** Look for ` ```python` markers in context

**For each code block found:**
1. Check if it's implementation code (not test code)
2. Check if it's in GREEN phase
3. Mark as VIOLATION

### Phase 2: Analyze Cycles

**For each cycle (X.Y):**

1. **Extract RED phase:** What test assertions?
2. **Extract GREEN phase:** What implementation guidance?
3. **Check sequence:** Will RED fail before GREEN?

**Sequencing check:**
- If cycle X.1 includes complete signature + error handling → VIOLATION
- If cycle X.1 includes all features → VIOLATION
- If "minimal implementation" has 10+ lines → WARNING

### Phase 3: Generate Report

**Structure:**

```markdown
# TDD Runbook Review: {name}

## Summary
- Total cycles: N
- Violations found: N critical, N warnings
- Overall assessment: PASS | NEEDS REVISION

## Critical Issues

### Issue 1: GREEN phase contains implementation code
**Location**: Cycle 2.1, line 490-528
**Problem**: Complete load_config() implementation prescribed
**Recommendation**: Replace with behavior description

### Issue 2: RED/GREEN sequencing violation
**Location**: Cycle 3.1
**Problem**: "Minimal" implementation includes all features
**Recommendation**: Split into incremental cycles

## Warnings

### Warning 1: Large "minimal" implementation
**Location**: Cycle 4.1
**Details**: 50 lines in first cycle suggests not minimal

## Recommendations

1. **Remove implementation code from GREEN phases**
   - Describe behavior, not code
   - Provide hints for approach, not exact solution

2. **Restructure cycles for proper RED→GREEN**
   - Cycle X.1: Happy path only
   - Cycle X.2: Error handling
   - Cycle X.3: Optional features

3. **Add implementation hints where sequencing matters**
   - "Happy path only - no error handling"
   - "Hardcoded separator '\n---\n\n'"
```

---

## Output Format

**Report file:** plans/<feature-name>/reports/runbook-review.md

**Return to caller:** Summary + path to report

```markdown
Review complete: 6 violations found

**Critical:**
- 4 cycles contain implementation code
- 2 cycles violate RED/GREEN sequence

**Report**: plans/unification/consolidation/reports/runbook-review.md

**Recommendation**: Apply fixes before execution
```

---

## Invocation

**Automatic:** /plan-tdd Phase 5 delegates to tdd-plan-reviewer agent
**Manual:** Delegate to tdd-plan-reviewer agent with runbook path

---

## Integration

**Workflow:**
```
/design (TDD mode) → /plan-tdd → tdd-plan-reviewer agent → [apply fixes] → prepare-runbook.py → /orchestrate
```

**Automatic review:** /plan-tdd Phase 5 triggers tdd-plan-reviewer agent automatically

---

## Key Principles

1. **Tests drive implementation** - Not scripts
2. **Minimal means minimal** - One behavior per cycle
3. **RED must fail** - Before GREEN can pass
4. **Describe behavior** - Not code
5. **Provide hints** - Not solutions

---

**Created**: 2026-01-26
**Purpose**: Prevent prescriptive TDD runbooks, ensure proper RED/GREEN discipline

# TDD Cycle Planning Guidance

Applied within TDD-type phases during Phase 1 expansion.

## 1. Number Cycles

X.Y format (1.1, 1.2, ..., 2.1, 2.2, ...)
- Start at 1.1 (not 0.1 or 1.0)
- Sequential within phases
- No duplicates (error), gaps acceptable (warn)

## 2. Generate RED Specifications (prose format)

```markdown
**RED Phase:**

**Test:** [test function name]
**Assertions:**
- [Specific assertion 1 -- behavioral, not structural]
- [Specific assertion 2]
- [Expected values/behaviors]

**Bootstrap:** [Create/Add to module with stub returning default]. Do not commit.

**Expected failure:** `AssertionError` — [specific behavioral mismatch]

**Why it fails:** [Stub returns default, test expects real behavior]

**Verify RED:** `pytest [file]::[test_function] -v`
```

**Bootstrap Pattern (mandatory for TDD RED):**

When the function/module under test does not yet exist, the RED phase includes a **Bootstrap** step: create the module with a stub implementation (return `None`, `""`, `[]`, or no-op) so the test can import and execute. The test then fails on a **behavioral assertion** — not `ImportError`.

- Bootstrap stubs are uncommitted scaffolding — the GREEN phase replaces them
- Expected failure must be `AssertionError` against a specific assertion, never `ImportError` or `AttributeError`
- This proves assertion strength: a trivial implementation would fail the same way

**When the module already exists** (subsequent cycles in the same phase): Bootstrap adds stub function signatures to the existing module. Use `Add to <module>` instead of `Create <module>`.

**Prose Test Description Rules:**

RED phase uses **prose descriptions**, not full code blocks. Saves planning tokens while providing enough specificity for haiku.

**Assertion Quality Requirements:**

| Weak (vague) | Strong (specific) |
|---|---|
| "returns correct value" | "returns string containing medal emoji" |
| "handles error case" | "raises ValueError with message 'invalid input'" |
| "processes input correctly" | "output dict contains 'count' key with integer > 0" |

**Validation rule:** Prose must specify exact expected values, patterns, or behaviors. If assertion could be satisfied by multiple implementations, it's too vague.

## 3. Generate GREEN Specifications

```markdown
**GREEN Phase:**

**Implementation:** [Brief description]

**Behavior:**
- [What the code must DO -- not HOW to write it]

**Approach:** [Brief hint about algorithm/strategy]

**Changes:**
- File: [path]
  Action: [what to add/modify -- describe, don't write code]
  Location hint: [where in file]

**Verify lint:** `just lint`
**Verify GREEN:** [Test command]
**Verify no regression:** [Full test suite]
```

**CRITICAL -- No prescriptive code:** GREEN phases describe BEHAVIOR and provide HINTS. Do NOT include complete function implementations or code blocks that can be copied verbatim.

**Integration-first cycle ordering:** Default to integration test cycles that exercise production call paths. Add unit test cycles only when integration coverage is insufficient (combinatorial, fault injection, internal contracts -- see Testing Strategy). Within a phase, plan integration cycles before or alongside unit cycles, not as follow-up.

**Wire-then-isolate:** When a phase builds a component, the first testable cycle should verify the component works through its production entry point. Subsequent cycles can isolate specific behaviors if edge-case coverage requires it.

## 4. Classify and Add Investigation Prerequisites

- **Transformation cycles** (delete, move, rename): Self-contained recipe sufficient
- **Creation cycles** (new test, new integration, touching existing paths): MUST include `**Prerequisite:** Read [file:lines] -- understand [behavior/flow]`

## 5. Assign Dependencies

- **Default:** Sequential within phase (1.1 -> 1.2 -> 1.3)
- **Cross-phase:** `[DEPENDS: X.Y]`
- **Regression:** `[REGRESSION]`

## 6. Stop Conditions

Common TDD stop/error conditions (auto-injected by prepare-runbook.py into Common Context):
- RED fails to fail -> STOP, diagnose test
- GREEN passes without implementation -> STOP, test too weak
- Test requires mocking not yet available -> STOP, add prerequisite cycle
- Implementation needs architectural decision -> STOP, escalate to opus

Only add custom domain-specific stop conditions per-cycle when needed.

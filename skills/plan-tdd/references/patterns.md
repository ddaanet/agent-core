# TDD Runbook Patterns

This document provides detailed guidance for decomposing features into atomic TDD cycles with proper granularity, numbering, and dependency management.

---

## Granularity Criteria

**Each cycle should have:**
- **1-3 assertions** - Focused verification of specific behavior
- **Clear RED failure expectation** - Predictable failure message/pattern
- **Minimal GREEN implementation** - Smallest code change to pass test
- **Independent verification** - Test doesn't rely on external state changes

**Too granular (avoid):**
- Single assertion that's trivial (e.g., "variable exists")
- Setup-only cycles with no behavioral verification
- Cycles that take <30 seconds to implement

**Too coarse (split):**
- >5 assertions in single test
- Multiple distinct behaviors tested together
- Complex setup + multiple verification steps
- Implementation spans multiple modules/files

**Example - Just Right:**
```
Cycle 2.1: Test -rp flag shows passed tests
- Single assertion: "## Passes" section exists
- Clear RED: Section not present
- Minimal GREEN: Add passes section to output
```

**Example - Too Coarse (should split):**
```
Cycle 2.1: Implement complete pass reporting with formatting
- Test passes section exists
- Test passes have correct format
- Test verbose mode shows passes
- Test quiet mode hides passes
→ Split into 4 cycles (2.1, 2.2, 2.3, 2.4)
```

---

## Numbering Scheme

**Format: X.Y**

**X (Phase number):**
- Represents logical grouping of related functionality
- Typically maps to design document phases
- Examples:
  - Phase 1: Core functionality
  - Phase 2: Error handling
  - Phase 3: Edge cases
  - Phase 4: Integration

**Y (Increment number):**
- Represents sequential behavioral increment within phase
- Starts at 1 for each phase
- Increments sequentially (1, 2, 3, ...)

**Numbering rules:**
- Start at 1.1 (not 0.1 or 1.0)
- Sequential within phase (1.1 → 1.2 → 1.3)
- Gaps acceptable but discouraged (1.1, 1.2, 1.4 with note about skipped 1.3)
- No duplicates (error condition)

**Example numbering:**
```
Phase 1: Separate Errors from Failures
  Cycle 1.1: Add setup error test fixture
  Cycle 1.2: Test errors in separate section
  Cycle 1.3: Test default mode shows both

Phase 2: Pass Reporting
  Cycle 2.1: Test -rp flag shows passes
  Cycle 2.2: Test verbose mode shows passes

Phase 3: Warnings
  Cycle 3.1: Add warning fixture
  Cycle 3.2: Test -rw flag shows warnings
```

---

## Dependency Management

**Default: Sequential within phase**

Cycles within same phase depend on previous cycle by default:
- 1.1 → 1.2 → 1.3 (sequential)
- Safe assumption for incremental development
- Prevents parallelization issues

**Explicit dependencies: [DEPENDS: X.Y]**

Use when cycle depends on cycle from different phase:
```
Cycle 2.1: Test -rp flag [DEPENDS: 1.3]
- Requires error separation from Phase 1
- Cannot execute until 1.3 complete
```

**Regression tests: [REGRESSION]**

Use when testing existing behavior:
```
Cycle 2.2: Test verbose mode [REGRESSION]
- Feature already exists
- Creating test for coverage
- No RED expected (should pass immediately)
- No dependency on other cycles
```

**No circular dependencies (error):**
```
❌ Invalid:
Cycle 2.1 [DEPENDS: 3.1]
Cycle 3.1 [DEPENDS: 2.1]
→ Circular dependency detected, STOP
```

**Dependency validation:**
- All references must exist
- No forward dependencies (2.1 can't depend on 3.1 unless 3.1 also specified)
- No self-dependencies (2.1 can't depend on 2.1)
- Topological sort must succeed

---

## Stop Conditions Generation

**Standard template (use for all cycles):**

```markdown
**Stop Conditions:**

**STOP IMMEDIATELY if:**
- Test passes on first run (expected RED failure)
- Test failure message doesn't match expected
- Test passes after partial GREEN implementation
- Any existing test breaks (regression failure)

**Actions when stopped:**
1. Document what happened in cycle notes
2. If test passes unexpectedly:
   - Investigate: Feature already implemented?
   - If yes: Mark as [REGRESSION], proceed
   - If no: Fix test to ensure RED, retry
3. If regression detected:
   - STOP execution
   - Report broken tests
   - Escalate to user
4. If scope unclear:
   - STOP execution
   - Document ambiguity
   - Request clarification
```

**Custom conditions (add when needed):**

Complex cycles may need additional stop conditions:

```markdown
**Additional stop conditions for Cycle 3.2 (Database Integration):**
- Database connection fails → Check credentials in .env
- Schema migration fails → Verify migration script syntax
- Performance >100ms → Optimize query, document results
- Transaction rollback fails → Check isolation level
```

**When to add custom conditions:**
- External dependencies (database, API, filesystem)
- Performance requirements
- Security concerns
- Complex setup/teardown

---

## Common Patterns

**Pattern 1: Basic CRUD Operations**

**Structure:** 1 cycle per operation

```
Cycle 1.1: Create entity
Cycle 1.2: Read entity
Cycle 1.3: Update entity
Cycle 1.4: Delete entity
```

**Why:** Each operation is independent behavioral increment.

---

**Pattern 2: Feature Flag with Multiple Modes**

**Structure:** 1 cycle per mode + 1 for default

```
Cycle 2.1: Test -rp flag (explicit enable)
Cycle 2.2: Test default mode (flag absent)
Cycle 2.3: Test -rN flag (explicit disable)
```

**Why:** Each mode has distinct behavior to verify.

---

**Pattern 3: Authentication Flow**

**Structure:** 1 cycle for happy path, 1+ for error cases

```
Cycle 3.1: Test successful authentication
Cycle 3.2: Test invalid credentials error
Cycle 3.3: Test expired token error
Cycle 3.4: Test missing credentials error
```

**Why:** Happy path first (core functionality), then error handling.

---

**Pattern 4: Integration with External Service**

**Structure:** 1 cycle for connection, 1+ for data exchange

```
Cycle 4.1: Test API connection established
Cycle 4.2: Test data retrieval
Cycle 4.3: Test data submission
Cycle 4.4: Test connection retry on failure
```

**Why:** Verify connection before data operations.

---

**Pattern 5: Edge Cases and Boundary Conditions**

**Structure:** Separate cycles for each boundary

```
Cycle 5.1: Test empty input
Cycle 5.2: Test maximum length input
Cycle 5.3: Test special characters in input
Cycle 5.4: Test null/None input
```

**Why:** Each boundary condition is distinct test scenario.

---

**Pattern 6: Refactoring Existing Code**

**Structure:** Regression test first, then refactor

```
Cycle 6.1: Add regression tests for current behavior [REGRESSION]
Cycle 6.2: Refactor implementation (tests should still pass)
```

**Why:** Ensure refactor doesn't break existing functionality.

---

**Pattern 7: Multi-Step Feature with Setup**

**Structure:** Setup cycle (if needed), then incremental cycles

```
Cycle 7.1: Add test fixture/helper (setup only, may not have full RED/GREEN)
Cycle 7.2: Test core functionality using fixture
Cycle 7.3: Test edge case using fixture
```

**Why:** Shared setup reduces duplication in later cycles.

**Note:** Minimize setup-only cycles. Prefer folding setup into first test cycle.

---

**Pattern 8: Composite Functionality**

**Structure:** Test individual components first, then integration

```
Cycle 8.1: Test component A works independently
Cycle 8.2: Test component B works independently
Cycle 8.3: Test A + B integration [DEPENDS: 8.1, 8.2]
```

**Why:** Isolate failures to specific component.

---

## Granularity Decision Tree

```
Does increment have testable behavior?
├─ No → Fold into next increment (or skip cycle)
└─ Yes
    ├─ How many assertions needed?
        ├─ 1-3 → Good cycle
        ├─ 4-5 → Acceptable, consider splitting
        └─ >5 → Split into multiple cycles
    └─ Implementation complexity?
        ├─ Single function/method → Good cycle
        ├─ Multiple files → Consider splitting
        └─ Multiple modules → Definitely split
```

---

## Cycle Breakdown Algorithm Summary

**For each design document:**

1. **Identify phases** (major feature groupings)
2. **Identify increments** within each phase (behavioral changes)
3. **Number cycles** (X.Y format)
4. **For each cycle:**
   - Define RED: What to test, expected failure
   - Define GREEN: Minimal implementation
   - Assign dependencies (default: sequential within phase)
   - Generate stop conditions (standard + custom if needed)
5. **Validate:**
   - Check granularity (1-3 assertions ideal)
   - Verify dependencies (no cycles, all valid references)
   - Confirm RED/GREEN completeness

**Result:** Well-structured TDD runbook with atomic, verifiable cycles.

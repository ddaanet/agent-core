---
name: plan-tdd
description: Create TDD runbook with RED/GREEN/REFACTOR cycles from design document
model: sonnet
requires:
  - Design document from /design (TDD mode)
  - CLAUDE.md for project conventions (if exists)
outputs:
  - TDD runbook at plans/<feature-name>/runbook.md
  - Ready for prepare-runbook.py processing
---

# /plan-tdd Skill

Create detailed TDD runbooks with RED-GREEN-REFACTOR cycles from design documents. This skill transforms design specifications into structured execution plans compatible with weak orchestrator agents and prepare-runbook.py processing.

---

## Purpose and Context

### What This Skill Does

The /plan-tdd skill automates the creation of TDD (Test-Driven Development) runbooks from design documents. It:

1. Analyzes design documents to extract feature requirements and design decisions
2. Decomposes features into atomic behavioral increments
3. Generates RED-GREEN-REFACTOR cycles for each increment
4. Creates a structured runbook with numbered cycles (X.Y format)
5. Produces output compatible with prepare-runbook.py and weak orchestrator pattern

### When to Use

**Use /plan-tdd when:**
- Design document specifies TDD mode or strict RED-GREEN-REFACTOR discipline
- Feature requires atomic verification with test-first approach
- Implementation needs structured cycle-by-cycle execution
- Working in projects with strong testing culture

**Do NOT use when:**
- Design is exploratory or requires iteration
- Implementation approach is unclear
- Feature is simple and doesn't warrant TDD overhead
- Use /plan-adhoc instead for general runbook generation

### Workflow Integration

```
User → /design (TDD mode) → Design document created
     → /plan-tdd → TDD runbook generated
     → prepare-runbook.py → Execution artifacts created
     → /orchestrate → Cycles executed with weak orchestrator
```

---

## Process: Five-Phase Execution

### Phase 1: Intake

**Objective:** Load design document and project conventions.

**Actions:**

1. **Determine Design Document Path**

   User invocation patterns:
   - `/plan-tdd` → Find latest `design.md` in `plans/` directory
   - `/plan-tdd <path>` → Use specified absolute path
   - `/plan-tdd <feature-name>` → Use `plans/<feature-name>/design.md`

   Use Glob tool to find latest design.md if no path specified:
   ```
   Glob pattern: plans/*/design.md
   Sort by modification time, take most recent
   ```

2. **Read Design Document**

   Use Read tool to load design document content.

   Error handling:
   - File not found → STOP, report: "Design document not found at {path}. Create with /design first."
   - Empty file → STOP, report: "Design document is empty."
   - Permission denied → STOP, report: "Cannot read {path}: permission denied."

3. **Read Project Conventions (Optional)**

   Check for CLAUDE.md in project root:
   ```
   If CLAUDE.md exists:
       Read tool to load
       Extract testing patterns, tool usage rules
   Else:
       Use default conventions
   ```

4. **Initial Validation**

   Verify design document indicates TDD mode:
   - Check frontmatter for `type: tdd`
   - Check title/goal for "TDD" keyword
   - Look for RED-GREEN-REFACTOR protocol section

   If TDD mode unclear:
   → Ask user: "This design doesn't explicitly indicate TDD mode. Create TDD runbook? (yes/no)"
   → If no: STOP, suggest /plan-adhoc

**Outputs:**
- `design_content`: Full design document text
- `design_path`: Absolute path to design
- `feature_name`: Extracted feature name
- `conventions`: Project rules (if available)

---

### Phase 2: Analysis

**Objective:** Extract feature information and validate design completeness.

**Actions:**

1. **Extract Feature Information**

   Search for goal/objective:
   - Pattern: `**Goal:**`, `## Goal`, or first H1 heading
   - Extract concise goal statement (1-2 sentences)

   Extract feature name:
   - From design filename (e.g., `auth-feature-design.md` → `auth-feature`)
   - From H1 title
   - From frontmatter `name:` field if present

   Error handling:
   - No goal found → STOP, ask user: "What is the goal of this feature?"
   - Feature name unclear → Infer from filename or ask user

2. **Extract Design Decisions**

   Search for design decisions section:
   - Pattern: `## Design Decisions`, `### Decision N:`
   - Extract each decision with rationale

   Format for storage:
   ```
   Decision 1: [Title]
   - Choice: [What was decided]
   - Rationale: [Why this choice]

   Decision 2: [Title]
   ...
   ```

   Error handling:
   - No design decisions section → WARNING, create minimal Common Context
   - Unstructured decisions → Extract best-effort from content

3. **Check for Unresolved Items**

   Use Grep tool to find confirmation markers:
   ```
   Patterns: "(REQUIRES CONFIRMATION)", "(TBD)", "(TODO: decide)", "[DECIDE:]", "???"
   Output mode: content
   Context: -C 2 (2 lines before/after)
   ```

   If found:
   → STOP, report:
   ```
   Found {N} unresolved items in design:

   1. Line {L}: {context}
   2. Line {L}: {context}
   ...

   Please resolve these decisions before proceeding with TDD runbook generation.
   ```

4. **Identify Implementation Structure**

   Parse design for phases and increments:

   **Phases** (X in X.Y numbering):
   - Look for `## Phase N:` headers
   - Look for major feature sections (## Authentication, ## Reporting)
   - If no explicit phases, treat as single phase

   **Increments** (Y in X.Y numbering):
   - Look for H3 subsections under phases
   - Look for bullet lists of features/behaviors
   - Look for test scenarios or acceptance criteria

   Heuristics:
   - Each action verb (Add, Implement, Create, Test) → potential increment
   - Each test scenario → cycle
   - Each behavioral change → increment

5. **Estimate Cycle Count**

   Count increments and apply granularity factor:
   ```
   base_increments = count_increments()
   setup_cycles = count_phases()  # One setup cycle per phase often needed
   estimated_cycles = base_increments + setup_cycles
   ```

   If estimated_cycles > 20:
   → WARNING: "Large runbook ({N} cycles estimated). This will be comprehensive. Continue? (yes/no)"

**Outputs:**
- `goal`: Feature objective statement
- `feature_name`: Clean name for paths
- `design_decisions`: Structured list of decisions
- `phases`: List of phase definitions
- `increments`: List of behavioral increments per phase
- `cycle_estimate`: Total cycle count

---

### Phase 3: Cycle Planning

**Objective:** Generate cycle definitions with RED/GREEN/Stop Conditions.

**Actions:**

1. **Number Cycles**

   For each phase (X) and increment (Y):
   ```
   Cycle ID = X.Y
   Example: Phase 1, Increment 3 → Cycle 1.3
   ```

   Validate:
   - Start numbering at 1.1 (not 0.1 or 1.0)
   - Sequential within phases (1.1, 1.2, 1.3)
   - No gaps (acceptable but warn if found)
   - No duplicates (error if found)

2. **Generate RED Specifications**

   For each cycle, create RED phase:

   **Template:**
   ```markdown
   **RED Phase:**

   **Test:** [What to test - specific assertion]

   **Expected failure:**
   ```
   [Exact error message or pattern]
   ```

   **Why it fails:** [Explanation of missing implementation]

   **Verify RED:** [Command to run - be specific]
   - Must fail with [expected pattern]
   - If passes, STOP - feature may already exist
   ```

   **Generation logic:**
   - Parse increment description for expected behavior
   - Infer test location from project structure (tests/, test_*.py)
   - Generate assertion based on behavior (e.g., "assert section exists", "assert output contains X")
   - Predict failure message from assertion type
   - Provide specific test command with file and function name

   **Example:**
   ```markdown
   **RED Phase:**

   **Test:** Add test in `tests/test_errors.py` asserting "## Errors" section exists when using -rE flag

   **Expected failure:**
   ```
   AssertionError: Expected '## Errors' section for setup/teardown errors
   ```

   **Why it fails:** Current implementation combines all failures in single "## Failures" section

   **Verify RED:** Run `pytest tests/test_errors.py::test_errors_separate -v`
   - Must fail with AssertionError
   - If passes, STOP - separation may already be implemented
   ```

3. **Generate GREEN Specifications**

   For each cycle, create GREEN phase:

   **Template:**
   ```markdown
   **GREEN Phase:**

   **Implementation:** [Minimal code change to pass test]

   **Changes:**
   - File: [absolute or project-relative path]
     Action: [specific change - add line, modify function, etc.]
   - File: [another file if needed]
     Action: [specific change]

   **Verify GREEN:** [Command to run test]
   - Must pass

   **Verify no regression:** [Command to run full test suite]
   - All existing tests must pass
   ```

   **Generation logic:**
   - Extract implementation approach from design decisions
   - Identify file locations from design or infer from project structure
   - Specify minimal change (single feature, no over-engineering)
   - Use same test command as RED verification
   - Default regression command: `pytest` or `just test` if justfile exists

   **Example:**
   ```markdown
   **GREEN Phase:**

   **Implementation:** Add separate errors bucket and section generator

   **Changes:**
   - File: `src/plugin.py`
     Action: Add `self.errors = []` list after line 111
     Action: Modify `_categorize_single_report()` to separate setup errors from failures
     Action: Add `_generate_errors()` method
     Action: Update `_build_report_lines()` to include errors section when -rE flag

   **Verify GREEN:** Run `pytest tests/test_errors.py::test_errors_separate -v`
   - Must pass

   **Verify no regression:** Run `pytest tests/`
   - All existing tests must pass
   ```

4. **Assign Dependencies**

   For each cycle, determine dependencies:

   **Rules:**
   - **Default within phase:** Sequential (1.1 → 1.2 → 1.3)
   - **Cross-phase:** Only if design explicitly requires
   - **Regression:** No dependency, tests existing behavior
   - **Parallel:** Only if increments are truly independent

   **Dependency markers:**
   - `[DEPENDS: X.Y]` → Explicit dependency on cycle X.Y
   - `[REGRESSION]` → Tests existing behavior, no new implementation
   - No marker → Implicit sequential dependency on previous cycle in phase

   **Example:**
   ```
   Cycle 1.1: Add test fixture [first in phase, no marker]
   Cycle 1.2: Test errors section [implicit dependency on 1.1]
   Cycle 1.3: Test default mode [implicit dependency on 1.2]
   Cycle 2.1: Test -rp flag [DEPENDS: 1.3] (uses error separation from Phase 1)
   Cycle 2.2: Test verbose mode [REGRESSION] (existing behavior)
   ```

5. **Generate Stop Conditions**

   For each cycle, include stop conditions:

   **Standard template:**
   ```markdown
   **Stop Conditions:**

   **STOP IMMEDIATELY if:**
   - Test passes on first run (expected RED failure)
   - Test failure message doesn't match expected
   - Test passes after partial GREEN implementation
   - Any existing test breaks (regression failure)

   **Actions when stopped:**
   1. Document what happened in `plans/{feature_name}/reports/cycle-{X}-{Y}-notes.md`
   2. If test passes unexpectedly:
      - Investigate: Is feature already implemented?
      - If yes: Mark cycle as `[REGRESSION]`, update runbook, proceed
      - If no: Fix test to ensure RED, retry cycle
   3. If regression detected:
      - STOP execution of runbook
      - Report which tests broke and why
      - Escalate to user for guidance
   4. If scope is unclear:
      - STOP execution
      - Document ambiguity
      - Request clarification from user
   ```

   **Custom conditions (add if needed):**
   - External dependencies (database, API) fail
   - Performance requirements not met
   - Security concerns identified

6. **Build and Validate Dependency Graph**

   Create dependency graph:
   ```
   For each cycle:
       dependencies[cycle_id] = [list of cycles this depends on]
   ```

   Validate:
   - All referenced cycles exist
   - No circular dependencies (topological sort)
   - Dependencies don't reference future cycles

   **Topological sort algorithm:**
   ```
   visited = {}
   visiting = {}

   def has_cycle(node):
       if node in visiting:
           return True  # Cycle detected
       if node in visited:
           return False

       visiting[node] = True
       for dependency in dependencies[node]:
           if has_cycle(dependency):
               return True
       del visiting[node]
       visited[node] = True
       return False

   For each cycle:
       if has_cycle(cycle):
           STOP, report: "Circular dependency detected: {cycle_chain}"
   ```

   Error handling:
   - Invalid reference → STOP, report: "Cycle {X.Y} depends on {A.B} which doesn't exist"
   - Circular dependency → STOP, report: "Circular dependency: {A.B} → {C.D} → {A.B}"
   - Forward dependency → STOP, report: "Cycle {X.Y} depends on future cycle {A.B}"

**Outputs:**
- `cycles`: List of cycle definitions with full RED/GREEN/Stop Conditions
- `dependency_graph`: Validated adjacency list
- `execution_order`: Topologically sorted cycle execution order

---

### Phase 4: Runbook Generation

**Objective:** Create runbook file with all sections.

**Actions:**

1. **Generate Frontmatter**

   ```yaml
   ---
   name: {feature_name}
   type: tdd
   model: haiku
   ---
   ```

2. **Generate Title and Context**

   ```markdown
   # {Feature Name} TDD Runbook

   **Context**: {goal}

   **Design**: {design_path}

   **Status**: Draft
   **Created**: {current_date}
   ```

3. **Generate Weak Orchestrator Metadata**

   ```markdown
   ## Weak Orchestrator Metadata

   **Total Steps**: {cycle_count}

   **Execution Model**:
   - All cycles: Haiku (TDD execution)

   **Step Dependencies**: {sequential|parallel|mixed}

   **Error Escalation**:
   - Haiku → User: Stop conditions triggered, regression failure, unclear test results

   **Report Locations**: `plans/{feature_name}/reports/`

   **Success Criteria**:
   - All cycles complete with GREEN verification
   - No regression failures
   - All tests passing

   **Prerequisites**:
   {extract_prerequisites_from_design}
   ```

   **Dependency type logic:**
   ```
   If all cycles sequential:
       "Sequential"
   Else if any parallel-safe cycles exist:
       "Mixed (sequential within phases, some parallel-safe regressions)"
   ```

4. **Generate Common Context**

   ```markdown
   ## Common Context

   **Key Design Decisions:**

   {numbered_list_from_design_decisions}

   **TDD Protocol:**

   This runbook follows strict RED-GREEN-REFACTOR discipline:

   1. **RED:** Write test that fails with expected error
   2. **Verify RED:** Confirm test fails as expected
   3. **GREEN:** Write minimal implementation to pass test
   4. **Verify GREEN:** Confirm test passes
   5. **Verify Regression:** Confirm no existing tests break
   6. **REFACTOR:** Clean up if needed (optional)

   **Project Paths:**
   {extract_file_paths_from_design}

   **Conventions:**
   - Use Read/Write/Edit tools for file operations (NOT cat/sed/awk)
   - Use Grep tool for searching (NOT bash grep)
   - Use Bash only for running tests and builds
   - Report all errors explicitly (never suppress with || true)
   - Write cycle notes to plans/{feature_name}/reports/cycle-{X}-{Y}-notes.md
   ```

5. **Generate Cycle Sections**

   For each cycle in execution order:

   ```markdown
   ## Cycle {X.Y}: {cycle_name} {dependency_markers}

   **Objective**: {clear_goal}

   **Script Evaluation**: Direct execution (TDD cycle)

   **Execution Model**: Haiku

   **Implementation:**

   {RED_phase_content}

   ---

   {GREEN_phase_content}

   ---

   {Stop_conditions_content}

   **Expected Outcome**: Test passes (GREEN), no regressions

   **Error Conditions**:
   - RED doesn't fail → STOP, see stop conditions
   - GREEN doesn't pass → Debug, check implementation
   - Regression failure → STOP, escalate to user

   **Validation**:
   - Test fails during RED phase ✓
   - Test passes during GREEN phase ✓
   - No existing tests break ✓

   **Success Criteria**:
   - RED verified (test fails as expected)
   - GREEN verified (test passes after implementation)
   - No regression (all tests pass)

   **Report Path**: `plans/{feature_name}/reports/cycle-{X}-{Y}-notes.md`

   ---
   ```

6. **Generate Design Decisions Section**

   ```markdown
   ## Design Decisions

   {copy_from_design_document_with_formatting}
   ```

7. **Generate Dependencies Section**

   ```markdown
   ## Dependencies

   **Before This Runbook**:
   {prerequisites_from_design}

   **After This Runbook**:
   - Feature implemented with test coverage
   - All cycles verified with RED-GREEN-REFACTOR
   - Test suite confirms behavior
   - Ready for integration/deployment
   ```

8. **Write Runbook File**

   Output path: `plans/{feature_name}/runbook.md`

   Check if file exists:
   - If yes → Ask user: "Runbook already exists at {path}. Overwrite? (yes/no)"
   - If no from user → STOP, report: "Runbook generation cancelled."

   Use Write tool to create file with all sections combined.

   Error handling:
   - Permission denied → STOP, report: "Cannot write to {path}: permission denied"
   - Write fails → STOP, report error details

**Outputs:**
- `runbook_path`: Absolute path to generated runbook
- Runbook file written to disk

---

### Phase 5: Validation

**Objective:** Verify runbook format and prepare-runbook.py compatibility.

**Actions:**

1. **Verify Runbook Format**

   Read generated runbook and check:
   - Valid YAML frontmatter (parse with YAML regex)
   - `type: tdd` present in frontmatter
   - Weak Orchestrator Metadata section exists
   - Common Context section exists
   - All cycle headers match `## Cycle \d+\.\d+:` pattern
   - No duplicate cycle IDs

   Error handling:
   - Invalid YAML → STOP, report: "Generated frontmatter is invalid: {error}"
   - Missing section → STOP, report: "Missing required section: {section_name}"
   - Invalid cycle headers → STOP, report: "Cycle headers don't match expected format"
   - Duplicates → STOP, report: "Duplicate cycle IDs: {list}"

2. **Check prepare-runbook.py Compatibility**

   Verify prepare-runbook.py exists:
   ```
   Check: agent-core/bin/prepare-runbook.py
   If not found → WARNING: "prepare-runbook.py not found. Manual processing required."
   ```

   Simulate parsing:
   - Extract cycle headers with regex: `## Cycle (\d+)\.(\d+):`
   - Verify all cycles extractable
   - Check Common Context extractable

3. **Validate Dependencies (Double-Check)**

   Re-run topological sort on final cycles.
   Should pass (already validated in Phase 3), but double-check.

4. **Generate Success Report**

   ```markdown
   TDD runbook created successfully!

   **Location**: {runbook_path}
   **Cycles**: {count}
   **Dependencies**: {structure}
   **Estimated execution time**: {count * 5} minutes (assuming 5 min/cycle average)

   **Next steps:**

   1. **Review runbook:**
      Read {runbook_path} to verify cycles match your intent

   2. **Generate execution artifacts:**
      python3 agent-core/bin/prepare-runbook.py {runbook_path}

      This creates:
      - .claude/agents/{feature_name}-task.md (plan-specific agent)
      - plans/{feature_name}/steps/cycle-{X}-{Y}.md (individual cycles)
      - plans/{feature_name}/orchestrator-plan.md (execution index)

   3. **Execute cycles:**
      Option A: /orchestrate plans/{feature_name}/orchestrator-plan.md
      Option B: Manual cycle execution with plan-specific agent

   **Tips:**
   - Read cycle files before execution to understand context
   - Follow stop conditions strictly (TDD discipline)
   - Document unexpected results in cycle notes
   - Regression failures require immediate attention
   ```

5. **Report to User**

   Display success report.
   Include runbook path and next steps.

**Outputs:**
- Success report displayed
- Runbook ready for prepare-runbook.py

---

## Cycle Breakdown Guidance

This section provides detailed guidance for decomposing features into atomic TDD cycles during Phase 3: Cycle Planning.

### Granularity Criteria

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

### Numbering Scheme

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

### Dependency Management

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

### Stop Conditions Generation

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

### Common Patterns

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

### Granularity Decision Tree

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

### Anti-Patterns to Avoid

**Anti-Pattern 1: Setup-Only Cycles**

❌ **Bad:**
```
Cycle 1.1: Create test fixture (no test, just fixture code)
```

✅ **Good:**
```
Cycle 1.1: Test fixture works correctly
- RED: Fixture doesn't exist
- GREEN: Create fixture
- Verify: Fixture behaves as expected
```

---

**Anti-Pattern 2: God Cycles**

❌ **Bad:**
```
Cycle 2.1: Implement entire authentication system
- Test login works
- Test logout works
- Test token refresh works
- Test password reset works
- Test 2FA works
```

✅ **Good:**
```
Cycle 2.1: Test basic login
Cycle 2.2: Test logout
Cycle 2.3: Test token refresh
Cycle 2.4: Test password reset
Cycle 2.5: Test 2FA
```

---

**Anti-Pattern 3: Unclear RED Expectations**

❌ **Bad:**
```
**Expected failure:** Something will fail
```

✅ **Good:**
```
**Expected failure:**
```
ModuleNotFoundError: No module named 'auth'
```

**Why it fails:** Auth module not created yet
```

---

**Anti-Pattern 4: Missing Regression Verification**

❌ **Bad:**
```
**Verify GREEN:** Run pytest tests/test_new.py
```

✅ **Good:**
```
**Verify GREEN:** Run pytest tests/test_new.py
- Must pass

**Verify no regression:** Run pytest tests/
- All existing tests must pass
```

---

**Anti-Pattern 5: Coupled Cycles**

❌ **Bad:**
```
Cycle 3.1: Modify shared state
Cycle 3.2: Test that shared state was modified (implicit dependency)
```

✅ **Good:**
```
Cycle 3.1: Test state modification [sets up state]
Cycle 3.2: Test state query [DEPENDS: 3.1]
- Explicit dependency
- Clear execution order
```

---

### Cycle Breakdown Algorithm Summary

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

---

## Templates

### Frontmatter Template

```yaml
---
name: {feature_name}
type: tdd
model: haiku
---
```

### Weak Orchestrator Metadata Template

```markdown
## Weak Orchestrator Metadata

**Total Steps**: {N}

**Execution Model**:
- All cycles: Haiku (TDD execution)

**Step Dependencies**: Sequential / Parallel / Mixed

**Error Escalation**:
- Haiku → User: Stop conditions triggered, regression failure

**Report Locations**: `plans/{name}/reports/`

**Success Criteria**: All cycles GREEN, no regressions

**Prerequisites**:
- {List from design doc}
```

### Common Context Template

```markdown
## Common Context

**Key Design Decisions:**

1. **{Decision Title}**
   - Choice: {what was decided}
   - Rationale: {why}

**TDD Protocol:**

Strict RED-GREEN-REFACTOR discipline:
1. RED: Write failing test
2. Verify RED: Confirm expected failure
3. GREEN: Minimal implementation
4. Verify GREEN: Test passes
5. Verify Regression: No breaks
6. REFACTOR: Clean up (optional)

**Project Paths:**
- {path descriptions}

**Conventions:**
- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly
- Write notes to plans/{name}/reports/cycle-{X}-{Y}-notes.md
```

### Cycle Definition Template

```markdown
## Cycle {X.Y}: {Name} {[DEPENDS: A.B]} {[REGRESSION]}

**Objective**: {Clear goal}

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** {What to test}

**Expected failure:**
```
{Error message}
```

**Why it fails:** {Explanation}

**Verify RED:** {Command}
- Must fail with {pattern}
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** {Minimal code}

**Changes:**
- File: {path}
  Action: {change}

**Verify GREEN:** {Command}
- Must pass

**Verify no regression:** {Command}
- All tests must pass

---

**Stop Conditions:**

**STOP IMMEDIATELY if:**
- Test passes on first run
- Failure message doesn't match
- Partial implementation passes
- Regression detected

**Actions when stopped:**
1. Document in cycle notes
2. Investigate unexpected results
3. Escalate to user if needed

**Expected Outcome**: GREEN verification, no regressions

**Error Conditions**:
- RED doesn't fail → STOP
- GREEN doesn't pass → Debug
- Regression → STOP

**Validation**:
- RED verified ✓
- GREEN verified ✓
- No regressions ✓

**Success Criteria**:
- Test fails during RED
- Test passes during GREEN
- No existing tests break

**Report Path**: `plans/{name}/reports/cycle-{X}-{Y}-notes.md`

---
```

---

## Examples

### Example Design Document Snippet

```markdown
# Authentication Feature Design

**Goal:** Implement OAuth2 authentication with Google and GitHub providers

## Design Decisions

**Decision 1: Provider Architecture**
- Choice: Strategy pattern with provider interface
- Rationale: Allows easy addition of new providers

**Decision 2: Session Storage**
- Choice: JWT tokens with Redis cache
- Rationale: Stateless, scalable, fast lookup

## Phase 1: Core OAuth2 Flow

### Implement provider interface
Define common interface for all OAuth2 providers

### Add Google provider
Implement Google-specific OAuth2 flow

### Add GitHub provider
Implement GitHub-specific OAuth2 flow

## Phase 2: Session Management

### Generate JWT tokens
Create JWT tokens after successful authentication

### Implement token validation
Validate JWT tokens on protected routes
```

### Example Generated Cycle

```markdown
## Cycle 1.1: Implement Provider Interface

**Objective**: Define common interface for OAuth2 providers

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Add test in `tests/test_auth.py` asserting provider interface has required methods

**Expected failure:**
```
ModuleNotFoundError: No module named 'auth.providers'
```

**Why it fails:** Provider module doesn't exist yet

**Verify RED:** Run `pytest tests/test_auth.py::test_provider_interface -v`
- Must fail with ModuleNotFoundError
- If passes, STOP - module may already exist

---

**GREEN Phase:**

**Implementation:** Create provider interface with required methods

**Changes:**
- File: `src/auth/providers/__init__.py`
  Action: Create directory and file
  Action: Define ProviderInterface class with authenticate(), get_user(), refresh_token() methods

**Verify GREEN:** Run `pytest tests/test_auth.py::test_provider_interface -v`
- Must pass

**Verify no regression:** Run `pytest tests/`
- All existing tests must pass

---

**Stop Conditions:**

**STOP IMMEDIATELY if:**
- Test passes on first run (expected RED failure)
- Test failure message doesn't match expected
- Test passes after partial GREEN implementation
- Any existing test breaks (regression failure)

**Actions when stopped:**
1. Document what happened in `plans/auth-feature/reports/cycle-1-1-notes.md`
2. If test passes unexpectedly:
   - Check if provider interface already exists
   - If yes: Mark as [REGRESSION], proceed
   - If no: Fix test to ensure RED, retry
3. If regression detected:
   - STOP execution
   - Report which tests broke
   - Escalate to user

**Expected Outcome**: Interface defined, test passes, no regressions

**Error Conditions**:
- RED doesn't fail → STOP, see stop conditions
- GREEN doesn't pass → Debug implementation
- Regression failure → STOP, escalate

**Validation**:
- Test fails during RED ✓
- Test passes during GREEN ✓
- No existing tests break ✓

**Success Criteria**:
- RED verified (ModuleNotFoundError)
- GREEN verified (test passes)
- No regression (all tests pass)

**Report Path**: `plans/auth-feature/reports/cycle-1-1-notes.md`

---
```

### Example Complete Runbook Structure

```markdown
---
name: auth-feature
type: tdd
model: haiku
---

# Authentication Feature TDD Runbook

**Context**: Implement OAuth2 authentication with Google and GitHub providers

**Design**: plans/auth-feature/design.md

**Status**: Draft
**Created**: 2026-01-20

---

## Weak Orchestrator Metadata

**Total Steps**: 5

**Execution Model**:
- All cycles: Haiku (TDD execution)

**Step Dependencies**: Sequential

**Error Escalation**:
- Haiku → User: Stop conditions triggered, regression failure

**Report Locations**: `plans/auth-feature/reports/`

**Success Criteria**: All cycles GREEN, no regressions

**Prerequisites**:
- Python 3.11+
- pytest installed
- Redis server available for testing

---

## Common Context

**Key Design Decisions:**

1. **Provider Architecture**
   - Choice: Strategy pattern with provider interface
   - Rationale: Allows easy addition of new providers

2. **Session Storage**
   - Choice: JWT tokens with Redis cache
   - Rationale: Stateless, scalable, fast lookup

**TDD Protocol:**

[Standard protocol section]

**Project Paths:**
- Source: `src/auth/`
- Tests: `tests/test_auth.py`

**Conventions:**
[Standard conventions]

---

## Cycle 1.1: Implement Provider Interface

[Full cycle content]

---

## Cycle 1.2: Add Google Provider [DEPENDS: 1.1]

[Full cycle content]

---

## Cycle 1.3: Add GitHub Provider [DEPENDS: 1.2]

[Full cycle content]

---

## Cycle 2.1: Generate JWT Tokens [DEPENDS: 1.3]

[Full cycle content]

---

## Cycle 2.2: Implement Token Validation [DEPENDS: 2.1]

[Full cycle content]

---

## Design Decisions

[Copy from design doc]

---

## Dependencies

**Before This Runbook**:
- Design document complete
- Prerequisites verified

**After This Runbook**:
- OAuth2 authentication implemented
- Google and GitHub providers working
- JWT session management complete
- Full test coverage

---
```

---

## Error Handling and Edge Cases

This section provides detailed guidance for handling errors and edge cases during runbook generation.

### Input Validation Errors

**Error: Design document not found**

**Trigger:** File doesn't exist at specified path

**Action:**
- Report exact path attempted
- List recent design.md files in plans/ directory
- Suggest: "Create design document with /design first"
- STOP execution

**Example message:**
```
Design document not found at: plans/auth-feature/design.md

Recent design documents:
- plans/reporting/design.md (modified 2 hours ago)
- plans/oauth/design.md (modified 1 day ago)

Create design document first with /design, then run /plan-tdd.
```

---

**Error: Missing TDD sections**

**Trigger:** Design doc lacks behavioral increments or test scenarios

**Action:**
- Report which sections are missing
- Suggest specific sections to add
- Ask if user wants general runbook instead
- STOP execution if TDD mode confirmed

**Example message:**
```
Design document missing TDD-specific sections:

Missing:
- Implementation phases or behavioral increments
- Test scenarios or acceptance criteria

This design may not be ready for TDD runbook generation.

Options:
1. Add behavioral increments to design document
2. Use /plan-adhoc for general runbook generation

Which would you prefer?
```

---

**Error: Unresolved confirmations**

**Trigger:** Design contains `(REQUIRES CONFIRMATION)`, `(TBD)`, or similar markers

**Action:**
- List all unresolved items with context
- Show line numbers and surrounding text
- Request user resolution
- STOP execution

**Example message:**
```
Found 3 unresolved items in design:

1. Line 45: Authentication method
   Context: "Use OAuth2 or API keys (REQUIRES CONFIRMATION)"

2. Line 78: Error handling strategy
   Context: "Retry logic to be determined (TBD)"

3. Line 102: Database choice
   Context: "SQLite or PostgreSQL [DECIDE:]"

Please resolve these decisions in the design document before proceeding.
TDD cycles require fully-resolved design decisions.
```

---

### Cycle Generation Errors

**Error: Empty cycle (no assertions)**

**Trigger:** Increment has no testable behavior

**Action:**
- Report which increment has no assertions
- Suggest folding into next increment
- Warn user
- Skip cycle or ask for confirmation

**Example message:**
```
WARNING: Cycle 2.3 has no testable assertions

Increment: "Set up logging configuration"

This appears to be setup-only with no behavioral verification.

Recommendation: Fold into Cycle 2.4 "Test logging output"

Skip Cycle 2.3? (yes/no)
```

---

**Error: Circular dependencies detected**

**Trigger:** Dependency graph has cycle (A → B → C → A)

**Action:**
- Report full cycle chain
- Identify which cycles involved
- Suggest breaking dependency
- STOP execution

**Example message:**
```
ERROR: Circular dependency detected

Cycle chain:
  Cycle 2.1 [DEPENDS: 3.2]
  → Cycle 3.2 [DEPENDS: 4.1]
  → Cycle 4.1 [DEPENDS: 2.1]

This creates an unresolvable execution order.

Recommendation: Remove one dependency from the chain.
Most likely: Remove [DEPENDS: 2.1] from Cycle 4.1
```

---

**Error: Invalid cycle ID format**

**Trigger:** Cycle ID doesn't match X.Y pattern

**Action:**
- Report all invalid IDs
- Show expected format
- STOP execution

**Example message:**
```
ERROR: Invalid cycle ID format

Invalid IDs found:
- "Cycle 1" (expected format: "Cycle X.Y")
- "Cycle 2.0.1" (expected format: "Cycle X.Y", not X.Y.Z)
- "Cycle A.1" (expected format: numeric X, not letter)

Expected format: Cycle X.Y where X and Y are positive integers
Example: Cycle 1.1, Cycle 2.3, Cycle 10.5
```

---

**Error: Duplicate cycle IDs**

**Trigger:** Two or more cycles have same ID

**Action:**
- Report all duplicates with locations
- Show which increments have duplicates
- STOP execution

**Example message:**
```
ERROR: Duplicate cycle IDs detected

Cycle 2.2 appears 2 times:
1. Line 234: "Cycle 2.2: Test error handling"
2. Line 389: "Cycle 2.2: Test validation logic"

Each cycle must have unique ID.
Renumber second occurrence to Cycle 2.3.
```

---

### Integration Errors

**Error: Cannot write runbook file**

**Trigger:** Write tool fails (permissions, disk full, path issues)

**Action:**
- Report exact path and error
- Check permissions if applicable
- Check disk space if applicable
- Suggest alternative path
- STOP execution

**Example message:**
```
ERROR: Cannot write runbook file

Path: plans/auth-feature/runbook.md
Error: Permission denied

Check directory permissions:
  ls -la plans/auth-feature/

Alternative: Use different location with write access
```

---

**Error: prepare-runbook.py not available**

**Trigger:** Script not found at expected location

**Action:**
- Report expected path
- Check if agent-core/ directory exists
- Provide manual processing guidance
- WARNING (not fatal error, runbook still usable)

**Example message:**
```
WARNING: prepare-runbook.py not found

Expected location: agent-core/bin/prepare-runbook.py

Runbook created successfully, but automatic processing unavailable.

Manual processing:
1. Review runbook at plans/auth-feature/runbook.md
2. Create cycle files manually following structure
3. Or install agent-core tools and retry processing
```

---

### Edge Cases

**Edge Case 1: Single-cycle feature**

**Scenario:** Design has only one behavioral increment

**Handling:**
- Valid scenario
- Create Cycle 1.1 only
- Include all standard sections
- No dependencies
- Proceed normally

**Example:**
```
Single-cycle runbook created:
- Cycle 1.1: Implement feature X

This is valid for simple features.
All sections included (RED/GREEN/Stop Conditions).
```

---

**Edge Case 2: No dependencies between cycles**

**Scenario:** All cycles are independent (parallel-safe)

**Handling:**
- Mark in Weak Orchestrator Metadata as "Parallel"
- Document independence in Common Context
- Enable parallel execution if orchestrator supports
- Valid for regression test suites

**Example metadata:**
```
**Step Dependencies**: Parallel (all cycles independent)

Note: All cycles are regression tests verifying existing behavior.
Can be executed in any order or in parallel.
```

---

**Edge Case 3: All cycles are regressions**

**Scenario:** Feature already implemented, only creating tests

**Handling:**
- Valid scenario
- Mark all cycles as `[REGRESSION]`
- Adjust stop conditions (no RED expected)
- Document in Common Context

**Example:**
```
## Common Context

**Note:** This runbook creates test coverage for existing feature.
All cycles marked [REGRESSION] - tests should pass immediately.

If any test fails:
- Existing implementation may be broken
- Test may be incorrect
- Stop and investigate
```

---

**Edge Case 4: Cycle depends on future cycle**

**Scenario:** Dependency graph has forward reference

**Handling:**
- Invalid scenario
- STOP execution
- Report ordering issue
- Suggest renumbering or removing dependency

**Example message:**
```
ERROR: Forward dependency detected

Cycle 1.2 [DEPENDS: 2.1]

Cycle 1.2 cannot depend on later cycle 2.1.

Options:
1. Renumber: Make current 2.1 into 1.2, push other cycles back
2. Remove dependency: If 1.2 doesn't actually need 2.1
3. Reorder phases: Move increment to later phase
```

---

**Edge Case 5: Empty cycle (no assertions)**

**Scenario:** Increment is pure setup, no testable behavior

**Handling:**
- Option 1 (preferred): Skip cycle, fold setup into next cycle
- Option 2: Create setup-only cycle (GREEN only, no RED)
- Warn user about non-standard structure

**Example message:**
```
WARNING: Cycle 1.1 appears to be setup-only

Increment: "Create test fixture class"

No behavioral verification identified.

Recommendation:
- Fold fixture creation into Cycle 1.2 GREEN phase
- First test in 1.2 will create and use fixture

Proceed with setup-only cycle? (not recommended)
```

---

**Edge Case 6: Complex cycle (>5 assertions)**

**Scenario:** Increment tests many behaviors

**Handling:**
- Warn user about complexity
- Suggest splitting into sub-cycles
- Ask for confirmation to proceed
- Document complexity in cycle

**Example message:**
```
WARNING: Cycle 3.2 has high complexity

Identified assertions:
1. Test authentication succeeds
2. Test token is valid JWT
3. Test token has correct claims
4. Test token has expiration
5. Test refresh token created
6. Test session stored in Redis
7. Test user profile loaded

Recommendation: Split into multiple cycles
- Cycle 3.2: Basic authentication (assertions 1-2)
- Cycle 3.3: Token validation (assertions 3-4)
- Cycle 3.4: Session management (assertions 5-7)

Proceed with complex cycle? (not recommended)
```

---

**Edge Case 7: Missing design decisions**

**Scenario:** Design doc has no "Design Decisions" section

**Handling:**
- Attempt to extract decisions from content
- Create minimal Common Context
- Warn user about missing context
- Proceed (not fatal)

**Example message:**
```
WARNING: No "Design Decisions" section found in design

Attempting to extract decisions from content...

Created minimal Common Context with:
- Goal statement
- File paths (inferred from increments)
- Standard conventions

Recommendation: Add "Design Decisions" section to design for better context.
```

---

**Edge Case 8: Very large runbook (>50 cycles)**

**Scenario:** Decomposition creates many cycles

**Handling:**
- Warn user about size
- Confirm intent
- Suggest splitting into phases/sub-features
- Proceed if confirmed

**Example message:**
```
WARNING: Large runbook detected

Estimated cycles: 67

This will create a very comprehensive runbook.

Considerations:
- Execution time: ~5.5 hours (5 min/cycle avg)
- Review effort: Significant
- Maintenance: Complex

Recommendation: Split into multiple runbooks by phase

Proceed with 67-cycle runbook? (yes/no)
```

---

### Recovery Protocols

**Protocol 1: Validation failure**

**When:** Format validation fails after generation

**Actions:**
1. Report specific validation issue
2. Show expected vs actual format
3. Offer to regenerate section
4. If user declines: Save partial runbook with ".draft" extension

**Example:**
```
Validation failed: Invalid cycle header format

Expected: ## Cycle 1.2: Feature name
Actual: ### Cycle 1.2: Feature name (H3 instead of H2)

Regenerate with correct format? (yes/no)

If no: Partial runbook saved to plans/auth-feature/runbook.draft.md
```

---

**Protocol 2: Partial runbook generation**

**When:** Error occurs during Phase 4 (Generation)

**Actions:**
1. Save progress to temporary file
2. Report which section failed
3. Provide fix guidance
4. Ask if user wants to continue from checkpoint

**Example:**
```
ERROR during runbook generation

Failed at: Cycle 3.2 GREEN phase generation

Progress saved to: plans/auth-feature/runbook.partial.md

Error: Cannot infer implementation from design decisions

Options:
1. Add implementation guidance to design doc for increment 3.2
2. Skip Cycle 3.2 and continue with remaining cycles
3. Abort and review design document

Choice?
```

---

**Protocol 3: User intervention needed**

**When:** Ambiguity or missing information detected

**Actions:**
1. Save current state
2. Document specific issue clearly
3. Provide clear next action
4. Wait for user input

**Example:**
```
User intervention required

Issue: Cannot determine cycle granularity for Phase 2

Increment: "Implement comprehensive error handling"

This could be:
1. Single cycle (test all errors together)
2. Multiple cycles (one per error type)

Design document doesn't specify granularity.

Please clarify:
- How many error types should be tested?
- Should each error type be separate cycle?

State saved. Reply with guidance to continue.
```

---

**Protocol 4: Dependency resolution failure**

**When:** Circular or invalid dependencies detected

**Actions:**
1. Show dependency graph
2. Highlight problem area
3. Suggest specific fix
4. Offer to auto-resolve if possible

**Example:**
```
Dependency resolution failed

Dependency graph:
  1.1 → 1.2
  1.2 → 1.3
  1.3 → 2.1
  2.1 → 1.2  ← CYCLE DETECTED

Suggested fix: Remove [DEPENDS: 1.2] from Cycle 2.1

Auto-resolve? (yes/no)

If yes: Cycle 2.1 will depend on 1.3 instead (sequential within phases)
If no: Manual intervention required
```

---

**Protocol 5: prepare-runbook.py compatibility issue**

**When:** Generated runbook won't work with prepare-runbook.py

**Actions:**
1. Report compatibility issue
2. Show problematic section
3. Offer to regenerate with fixes
4. Provide manual workaround if needed

**Example:**
```
Compatibility issue detected

Problem: Cycle IDs contain non-numeric characters

Incompatible:
  ## Cycle 1.A: Feature name
  ## Cycle 1.B: Another feature

prepare-runbook.py expects numeric IDs only.

Regenerate with numeric IDs? (yes/no)

If yes: Will renumber as Cycle 1.1, Cycle 1.2
If no: Manual processing required (prepare-runbook.py will fail)
```

---

## Constraints and Error Handling

### Tool Usage Rules

**Required tools:**
- **Read**: Load design documents, CLAUDE.md, verify runbook
- **Write**: Create runbook file
- **Grep**: Search for unresolved confirmations, TDD indicators
- **Glob**: Find design documents when path not specified
- **Bash**: Run prepare-runbook.py validation (optional)

**Prohibited:**
- **Bash** for file content manipulation (use Read/Write/Edit)
- **Bash** grep/find (use Grep/Glob tools)
- Heredocs in Bash (sandbox blocks them)

### Error Handling Protocol

**Fail fast with clear messages:**

1. **File not found:**
   - Report exact path attempted
   - Suggest alternatives (list recent design docs)
   - Provide creation guidance

2. **Unresolved confirmations:**
   - List all items with context
   - STOP execution
   - Request user resolution

3. **Invalid structure:**
   - Report specific issue (missing section, invalid format)
   - Provide fix guidance
   - Offer to help restructure if needed

4. **Dependency errors:**
   - Report cycle chain for circular dependencies
   - Report missing cycle for invalid references
   - Suggest fix (reordering, removing dependency)

5. **Validation failures:**
   - Report specific check that failed
   - Show expected vs actual format
   - Offer to regenerate section

**Never suppress errors:**
- Report all errors explicitly
- Escalate to user when stuck
- Document unexpected results

### Validation Rules

**Cycle granularity:**
- Each cycle: 1-3 assertions (guideline)
- Warn if >5 assertions (suggest splitting)
- Reject if 0 assertions (unless setup-only cycle with justification)

**Dependency validation:**
- All references must exist
- No circular dependencies
- No forward dependencies (earlier cycles can't depend on later ones)
- Sequential within phase is default (safe)

**Format validation:**
- YAML frontmatter must parse
- Required sections must exist
- Cycle headers must match pattern
- No duplicate cycle IDs

**prepare-runbook.py compatibility:**
- `type: tdd` in frontmatter
- `## Cycle X.Y:` header format
- Common Context extractable
- All sections parseable

---

## Integration Notes

### prepare-runbook.py Processing

After /plan-tdd generates runbook:

1. **User runs:** `python3 agent-core/bin/prepare-runbook.py plans/{name}/runbook.md`

2. **Script detects:** `type: tdd` in frontmatter

3. **Script uses:** `agent-core/agents/tdd-task.md` as baseline

4. **Script generates:**
   - `.claude/agents/{name}-task.md` (baseline + Common Context)
   - `plans/{name}/steps/cycle-{X}-{Y}.md` (individual cycles)
   - `plans/{name}/orchestrator-plan.md` (execution index)

5. **Each cycle file contains:**
   - Reference to plan-specific agent baseline
   - Common Context (design decisions, conventions)
   - Specific cycle content (RED/GREEN/Stop Conditions)
   - Execution instructions

6. **Orchestrator uses:**
   - Plan-specific agent for all cycles
   - Isolated context per cycle (no cumulative bloat)
   - Stop conditions for error escalation

### Workflow After Runbook Generation

```
/plan-tdd → plans/{name}/runbook.md created

User reviews runbook

prepare-runbook.py → Execution artifacts created

Option A: Automated
  /orchestrate plans/{name}/orchestrator-plan.md
  → Orchestrator executes cycles sequentially
  → Stops on any stop condition trigger

Option B: Manual
  Invoke plan-specific agent with cycle files
  → Execute cycle-by-cycle with review between
  → More control, slower execution

Results:
  → Feature implemented with test coverage
  → All cycles verified RED→GREEN
  → No regressions
  → Ready for integration
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Design Not TDD-Ready

**Problem:** Design document lacks behavioral increments or test scenarios.

**Solution:**
- STOP and report missing structure
- Suggest: "Run /design again in TDD mode" or "Add behavioral increments to design"
- Provide example of TDD-ready structure

### Pitfall 2: Over-Granular Cycles

**Problem:** Decomposition creates 50+ tiny cycles.

**Solution:**
- Combine increments with single assertions
- Warn user about runbook size
- Suggest coarser granularity if appropriate

### Pitfall 3: Under-Granular Cycles

**Problem:** Cycles test 10+ behaviors each.

**Solution:**
- Detect >5 assertions per cycle
- Warn and suggest splitting
- Provide split guidance (what to separate)

### Pitfall 4: Missing Dependencies

**Problem:** Cycles appear independent but share state.

**Solution:**
- Default to sequential within phase (safe)
- Only mark parallel-safe if design explicitly indicates
- Warn about potential hidden dependencies

### Pitfall 5: Unclear RED Failure

**Problem:** Can't predict specific failure message.

**Solution:**
- Use generic patterns: "Must fail with [error type]"
- Include guidance: "Exact message may vary"
- Emphasize: Verify failure happens, message is secondary

### Pitfall 6: prepare-runbook.py Not Available

**Problem:** Tool not found in expected location.

**Solution:**
- WARNING (not error)
- Provide manual processing guidance
- Report path where tool expected

---

## Success Criteria

**Runbook generation succeeds when:**

1. ✓ Valid TDD runbook created at `plans/{name}/runbook.md`
2. ✓ Frontmatter has `type: tdd`
3. ✓ All cycles have RED/GREEN/Stop Conditions
4. ✓ Dependency graph is valid (no cycles)
5. ✓ Format compatible with prepare-runbook.py
6. ✓ Common Context extracted from design
7. ✓ Cycle count reasonable (1-50 typical)
8. ✓ User informed of next steps

**Execution fails (expected stops) when:**

1. Design document not found
2. Unresolved confirmations in design
3. Invalid structure (can't identify increments)
4. Circular dependencies detected
5. Invalid dependency references
6. Cannot write runbook file

**Warnings (proceed with caution) when:**

1. No design decisions section
2. Large runbook (>20 cycles)
3. prepare-runbook.py not found
4. CLAUDE.md not found (use defaults)

---

**End of /plan-tdd Skill Documentation**

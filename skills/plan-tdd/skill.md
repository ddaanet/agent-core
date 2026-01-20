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

This section provides essential guidance for decomposing features into atomic TDD cycles during Phase 3: Cycle Planning.

**For detailed patterns and examples, see:**
- `references/patterns.md` - Granularity criteria, numbering schemes, common patterns
- `references/anti-patterns.md` - Patterns to avoid with examples

**Key principles:**
- Each cycle: 1-3 assertions
- Clear RED failure expectation
- Minimal GREEN implementation
- Sequential dependencies within phase (default)

**Dependency markers:**
- **Sequential (default):** Cycles in same phase depend on previous (1.1 → 1.2 → 1.3)
- **[DEPENDS: X.Y]:** Explicit cross-phase dependency
- **[REGRESSION]:** Testing existing behavior, no new implementation

**Stop conditions:**
- Standard template for all cycles
- Add custom conditions for external dependencies, performance, security
- Always include actions when stopped

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

## Constraints and Error Handling

**For detailed error handling guidance, see:**
- `references/error-handling.md` - Complete error catalog, edge cases, recovery protocols

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

1. **File not found:** Report exact path, suggest alternatives, provide creation guidance
2. **Unresolved confirmations:** List all items with context, STOP execution
3. **Invalid structure:** Report specific issue, provide fix guidance
4. **Dependency errors:** Report cycle chain for circular dependencies, suggest fix
5. **Validation failures:** Report specific check that failed, offer to regenerate

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
- No forward dependencies
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

## Additional Resources

For detailed guidance, consult these reference files:

- **`references/patterns.md`** - Granularity criteria, numbering schemes, common patterns, decision trees
- **`references/anti-patterns.md`** - Patterns to avoid with examples and corrections
- **`references/error-handling.md`** - Error handling, edge cases, recovery protocols
- **`references/examples.md`** - Complete TDD runbook examples with design document

---

**End of /plan-tdd Skill Documentation**

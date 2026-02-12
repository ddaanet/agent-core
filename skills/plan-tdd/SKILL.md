---
name: plan-tdd
description: Create TDD runbook with RED/GREEN/REFACTOR cycles from design document
model: sonnet
allowed-tools: Task, Read, Write, Edit, Skill, Bash(mkdir:*, agent-core/bin/prepare-runbook.py, echo:*|pbcopy)
requires:
  - Design document from /design (TDD mode)
  - CLAUDE.md for project conventions (if exists)
outputs:
  - TDD runbook at plans/<feature-name>/runbook.md
  - Ready for prepare-runbook.py processing
---

# /plan-tdd Skill

Create detailed TDD runbooks with RED-GREEN-REFACTOR cycles from design documents. Transforms design into structured execution plans compatible with weak orchestrators and prepare-runbook.py.

---

## Purpose and Context

### What This Skill Does

1. Analyzes design documents to extract requirements and decisions
2. Decomposes features into atomic behavioral increments
3. Generates RED-GREEN-REFACTOR cycles for each increment
4. Creates structured runbook with numbered cycles (X.Y format)
5. Delegates to clean sonnet agent for comprehensive review
6. Applies review feedback to ensure completeness and correct test sequencing
7. Produces output compatible with prepare-runbook.py

### When to Use

**Use /plan-tdd when:**
- Design specifies TDD mode or strict RED-GREEN-REFACTOR discipline
- Feature requires atomic verification with test-first approach
- Working in projects with strong testing culture

**Do NOT use when:**
- Design is exploratory or requires iteration
- Implementation approach is unclear
- Use /plan-adhoc for general runbooks

### Workflow Integration

```
/design (TDD mode) → /plan-tdd → [tdd-plan-reviewer] → [apply fixes] → prepare-runbook.py → /orchestrate
```

**CRITICAL:** After runbook generation and review:
1. If violations found: Apply fixes to runbook
2. prepare-runbook.py runs **automatically** (Phase 5 step 5) — no manual invocation needed
3. Skill auto-commits, hands off, and copies `/orchestrate {name}` to clipboard

**Note:** /plan-tdd now includes automatic delegation to tdd-plan-reviewer agent for prescriptive code detection.

---

## Process: Five-Phase Execution (with Review)

### Phase 0: Tier Assessment

**Objective:** Evaluate implementation complexity before proceeding.

**Actions:**

Analyze the task and produce explicit assessment output:

```
**Tier Assessment:**
- Files affected: ~N
- Open decisions: none / [list]
- Cycles estimated: ~N (rough count from design requirements/phases)
- Model requirements: single / multiple
- Session span: single / multi

**Tier: [1/2/3] — [Direct TDD / Lightweight TDD / Full Runbook]**
**Rationale:** [1-2 sentences]
```

**Cycle estimation (rough):** Scan design's requirements/phases sections — count major behavioral increments without full Phase 2-3 decomposition.

When uncertain between tiers, prefer the lower tier (less overhead). Ask user only if genuinely ambiguous.

**Tier 1: Direct TDD** (~1-3 cycles estimated, single test file, single source file)
- Write tests and implementation directly (RED/GREEN discipline still applies)
- Delegate to vet agent for review
- Apply fixes, tail-call `/handoff --commit`

**Tier 2: Lightweight TDD** (~4-10 cycles estimated, 2-3 test files)
- Plan cycle descriptions (lightweight — no full runbook format)
- For each cycle: delegate via `Task(subagent_type="tdd-task", model="haiku", prompt="...")` with context included in prompt (file paths, design decisions, project conventions, stop conditions specific to this feature)
- Intermediate checkpoints: every 3-5 delegated cycles, run tests and review accumulated changes
- Delegate to vet agent for final review
- Apply fixes, tail-call `/handoff --commit`

**Tier 3: Full Runbook** (>10 cycles estimated, multiple phases, cross-component dependencies)
- Proceed to Phase 1-5 below

**Output:** Tier decision with rationale.

---

### Phase 1: Intake (Tier 3 Only)

**Objective:** Load design and project conventions.

**Actions:**

0. **Read documentation perimeter and requirements (if present):**
   - If design includes "Documentation Perimeter" section, read all listed files under "Required reading"
   - Note Context7 references for potential additional queries
   - If design includes "Requirements" section, read and summarize functional/non-functional requirements, note scope boundaries
   - This provides designer's recommended context before discovery

1. **Determine design path:**
   - `/plan-tdd` → Find latest `plans/*/design.md` using Glob (sort by mtime)
   - `/plan-tdd <path>` → Use absolute path
   - `/plan-tdd <feature>` → Use `plans/<feature>/design.md`

2. **Read design:** Use Read tool. STOP if: not found, empty, permission denied.

3. **Read CLAUDE.md (optional):** Extract testing patterns and conventions if exists.

4. **Validate TDD mode:** Check frontmatter for `type: tdd` or TDD keywords. If unclear, ask user.

**Outputs:** design_content, design_path, feature_name, conventions

---

### Phase 1.5: Generate Runbook Outline (Tier 3 Only)

**Objective:** Create holistic outline with TDD-specific structure before generating full cycles.

**Actions:**

1. **Create runbook outline:**
   - File: `plans/<feature>/runbook-outline.md`
   - Include:
     - **Requirements mapping table:** Link each requirement from design to implementation phase/cycle
     - **Phase structure:** Break work into logical phases with cycle titles (no full RED/GREEN content yet)
     - **Key decisions reference:** Link to design sections with architectural decisions
     - **Complexity per phase:** Estimated cycle count and model requirements per phase
   - Use TDD-specific format:
     - Cycles instead of steps (X.Y numbering)
     - RED/GREEN markers in cycle titles where appropriate
     - Test-first sequencing visible in structure

2. **Verify outline quality:**
   - **All implementation choices resolved** — No "choose between" / "decide" / "determine" / "select approach" / "evaluate which" language. Each cycle commits to one approach. If uncertain, use `/opus-design-question` to resolve.
   - **Inter-cycle dependencies declared** — If cycle N.M depends on cycle N.K having created a file/module/function, declare `Depends on: Cycle N.K`.
   - **Code fix cycles enumerate affected sites** — For cycles fixing code: list all affected call sites (file:function or file:line). If different sites need different treatment, specify per-site decision tree.
   - **Later cycles reference post-phase state** — Cycles in Phase N+1 that modify files changed in Phase N must note expected state after Phase N (e.g., "After Phase 2 refactor, helpers are in conftest.py").
   - **Phases ≤8 cycles each** — Split phases with >8 cycles or add an internal checkpoint. Large phases without checkpoints make diagnosis difficult when early cycles break things.
   - **Cross-cutting issues scope-bounded** — If a cross-cutting issue is only partially addressed, explicitly note what's in scope and what's deferred. Prevents executing agent from attempting unscoped refactors.
   - **No vacuous cycles** — Every cycle must test a branch point (conditional, state transformation, error path). Cycles that only verify scaffolding (import exists, function callable) or integration wiring (A calls B when B is already tested) are vacuous. Merge into the nearest behavioral cycle.
   - **Foundation-first ordering within phases** — Order cycles: existence → structure → behavior → refinement. If cycle N tests dedup, the container it deduplicates must exist from cycle N-k, not cycle N+k. Forward dependencies cause haiku to implement against wrong structural assumptions.
   - **Edge-case clusters collapse** — Multiple cycles testing edge cases of the same function (special chars, truncation, empty input) collapse into one cycle with parametrized test description. Exception: edge cases requiring different setup or teardown stay separate.

3. **Review outline:**
   - Delegate to `runbook-outline-review-agent` (fix-all mode)
   - Agent fixes all issues (critical, major, minor)
   - Agent returns review report path

4. **Validate and proceed:**
   - Read review report
   - If critical issues remain: STOP and escalate to user
   - Otherwise: proceed to phase-by-phase cycle expansion

**Why outline-first:**
- Establishes cross-phase structure before expensive cycle generation
- Enables early feedback on phase boundaries and cycle sequencing
- Catches requirements gaps before RED/GREEN details
- Provides roadmap for phase-by-phase expansion

**Fallback for small TDD runbooks:**
- If outline has ≤3 phases and ≤10 total cycles → generate entire runbook at once (skip phase-by-phase)
- Single review pass instead of per-phase
- Simpler workflow for simple features

**Outputs:** runbook-outline.md, outline review report

---

### Phase 1.6: Consolidation Gate — Outline (Tier 3 Only)

**Objective:** Merge trivial phases with adjacent complexity before expensive expansion.

**Actions:**

1. **Scan outline for trivial phases:**
   - Phases with ≤2 cycles AND complexity marked "Low"
   - Single-constant changes or configuration updates
   - Pattern: setup/cleanup work that could batch with adjacent feature work

2. **Evaluate merge candidates:**

   For each trivial phase, check:
   - Can it merge with preceding phase? (same domain, natural continuation)
   - Can it merge with following phase? (prerequisite relationship)
   - Would merging create >10 cycles in target phase? (reject if so)

3. **Apply consolidation:**

   **Merge pattern:**
   ```markdown
   ## Phase N: [Combined Name]

   ### [Original feature cycles]
   ### [Trivial work as final cycles]
   ```

   **Do NOT merge if:**
   - Trivial phase has external dependencies (blocking other work)
   - Merged phase would exceed 10 cycles
   - Domains are unrelated (forced grouping hurts coherence)

4. **Update traceability:**
   - Adjust requirements mapping table
   - Update phase structure in outline
   - Note consolidation decisions in Expansion Guidance

**When to skip:**
- Outline has no trivial phases
- All trivial phases have cross-cutting dependencies
- Outline is already compact (≤3 phases)

**Rationale:** Rather than standalone trivial steps that fragment execution, batch simple work with adjacent complexity. This reduces orchestrator overhead and creates natural commit boundaries.

---

### Phase 2: Analysis (Tier 3 Only)

**Objective:** Extract feature info and validate completeness.

**Actions:**

1. **Extract feature info:**
   - Goal: Find `**Goal:**`, `## Goal`, or H1 heading (1-2 sentences)
   - Name: From filename, H1, or frontmatter `name:` field
   - STOP if no goal: Ask user "What is the goal?"

2. **Extract design decisions:**
   - Pattern: `## Design Decisions`, `### Decision N:`
   - Format: `Decision N: [Title]\n- Choice: [what]\n- Rationale: [why]`
   - If missing: WARNING, create minimal Common Context

3. **Check unresolved items:**
   - Use Grep for: `(REQUIRES CONFIRMATION)`, `(TBD)`, `(TODO: decide)`, `[DECIDE:]`, `???`
   - If found: STOP, report with line numbers and context

3.5. **Memory discovery:**
   - Check loaded memory-index context (already in CLAUDE.md) for entries relevant to the task domain
   - When entry is relevant, Read the referenced file
   - Factor known constraints, patterns, and prior decisions into cycle design
   - This prevents re-learning known patterns or contradicting established rules
   - **Do NOT grep memory-index.md** — it's already loaded, scan it mentally

4. **Discover codebase structure (REQUIRED):**
   - Use Glob to find existing test files: `tests/test_*.py`, `tests/**/test_*.py`
   - Use Glob to find source modules referenced by design
   - Map design components → actual file paths (source and test)
   - Record file mapping in working notes for Phase 3
   - STOP if expected files not found: report missing files to user
   - **NEVER infer file paths from conventions alone** — always verify with Glob/Grep

5. **Identify structure:**
   - **Phases (X):** Look for `## Phase N:` or major sections
   - **Increments (Y):** Look for H3 subsections, bullet lists, test scenarios
   - Heuristics: action verbs (Add, Implement, Create, Test) = potential increments

6. **Estimate cycles:**
   - `estimated_cycles = base_increments + setup_cycles`
   - If >20: WARN "Large runbook ({N} cycles). Continue?"

**Outputs:** goal, feature_name, design_decisions, phases, increments, cycle_estimate, file_mapping

---

### Phase 2.5: Complexity Check Before Expansion (Tier 3 Only)

**Objective:** Assess expansion complexity BEFORE generating cycle content. Gate expensive expansion with callback mechanism.

**Actions:**

1. **Assess expansion scope:**
   - Count total cycles from outline
   - Identify pattern-based cycles (same test structure, different inputs)
   - Identify algorithmic cycles (unique logic, edge cases)
   - Estimate token cost of full expansion

2. **Apply fast-path if applicable:**
   - **Pattern cycles (≥5 similar):** Generate pattern template + variation list instead of per-cycle expansion
   - **Trivial phases (≤2 cycles, low complexity):** Inline instructions instead of full TDD cycle format
   - **Single constant change:** Skip cycle, add as inline task

3. **Callback mechanism — if expansion too large:**

   **Callback triggers:**
   - Outline exceeds 25 cycles → callback to design (scope too large)
   - Phase exceeds 10 cycles → callback to outline (phase needs splitting)
   - Single cycle too complex → callback to outline (decompose further)

   **Callback levels:**
   ```
   step → runbook outline → design → design outline → requirements
   ```

   **When callback triggered:**
   - STOP expansion
   - Document issue: "Phase N contains [issue]. Callback to [level] required."
   - Return to previous level with specific restructuring recommendation
   - DO NOT proceed with expensive expansion of poorly-structured work

4. **Proceed with expansion:**
   - Only if complexity checks pass
   - Fast-path applied where appropriate
   - Callback mechanism available for discovered issues

**Rationale:** Complexity assessment is a planning concern (sonnet/opus). Don't delegate to haiku executor — they optimize for completion, not scope management. Catch structural problems before expensive expansion.

---

### Phase 2.7: Planning-Time File Size Awareness

**Objective:** Track file growth during cycle planning and proactively plan splits before hitting the 400-line limit.

**Convention:** When a cycle adds content to an existing file, note the current file size and plan splits proactively.

**Process:**

1. **For each cycle adding content to existing file:** Note `(current: ~N lines, adding ~M)`
2. **Check threshold:** If `N + M > 350`, include a split step in the same phase
3. **Threshold rationale:** The 400-line limit is a hard fail at commit time. Planning to 350 leaves a 50-line margin for vet fixes and minor additions

**Why 350:** Planning to the exact 400-line limit creates brittleness. A 50-line margin is pragmatic — accounts for vet review additions, formatting changes, and minor refactoring that happen during execution.

**Concrete example:** A file at 360 lines after implementation gets +25 lines from vet error handling improvements, +10 lines from formatting fixes, reaching 395 lines (still under limit). Without the margin, same file at 395 lines would exceed limit after vet fixes.

**Example:**
- Cycle 3.2 adds `format_model()` to `display.py` (current: ~320 lines, adding ~40)
- Cycle 3.2: Implement `format_model()` (~360 lines total)
- Cycle 3.3: Split `display.py` into `display_core.py` + `display_formatters.py`

**No runtime enforcement:** This is a planning convention. The commit-time `check_line_limits.sh` remains the hard gate. This prevents write-then-split rework loops.

**When to apply:**
- Actively planning file modifications (not exploratory edits)
- Files tracking toward 400-line limits
- Runbooks with many phase-spanning changes to same files

---

### Phase 3: Phase-by-Phase Cycle Expansion (Tier 3 Only)

**Objective:** Generate detailed cycle content for each phase with TDD-specific review.

**Actions:**

**For each phase identified in the outline:**

1. **Generate phase cycles:**
   - **Read Expansion Guidance:** Check for `## Expansion Guidance` section at end of `plans/<feature>/runbook-outline.md`. If present, incorporate recommendations (consolidation candidates, cycle expansion notes, checkpoint guidance) into phase content generation.
   - File: `plans/<feature>/runbook-phase-N.md`
   - Include cycle details using **prose test descriptions** (not full code)
   - Use cycle planning guidance from Phase 3.1-3.6 below

2. **Review and fix phase cycles:**
   - Delegate to `tdd-plan-reviewer` (fix-all mode)
   - Agent checks for:
     - Prescriptive code in GREEN phases
     - RED/GREEN violations
     - **Prose test quality** (behaviorally specific assertions)
   - Agent fixes ALL issues directly in phase file
   - Agent writes review report (audit trail)
   - Agent returns review report path (with escalation note if unfixable issues)

   **Background review pattern:** After writing each phase file, launch its review agent with `run_in_background=true` and immediately proceed to generating the next phase. Reviews run concurrently with subsequent phase generation.

   ```
   Write runbook-phase-1.md → launch review (background) → write runbook-phase-2.md → launch review (background) → ...
   After all phases written: read output files to collect report paths, check for escalations
   ```

   Per-phase reviews are independent (no cross-phase input needed). Cross-phase consistency is checked in Phase 5 (holistic review).

   **Domain Validation:**

   When writing vet checkpoint steps for TDD runbooks, check if a domain validation skill exists at `agent-core/skills/<domain>-validation/SKILL.md` for the artifact types being tested. If found, include domain validation in the checkpoint:

   - Add "Domain validation" instruction to tdd-plan-reviewer or vet-fix-agent delegation
   - Reference the skill file path
   - Specify artifact type (e.g., skills, agents, hooks, commands, plugin-structure)
   - Domain criteria are additive — TDD discipline + generic quality + domain checks all apply

   Example: For plugin development TDD work, include:
   ```
   - **Domain validation:** Read and apply criteria from
     `agent-core/skills/plugin-dev-validation/SKILL.md`
     for artifact type: [skills|agents|hooks|commands|plugin-structure]
   ```

3. **Handle review outcome:**
   - Read review report
   - If ESCALATION noted: STOP, address unfixable issues before proceeding
   - If all issues fixed: proceed to next phase

**Fallback:** If outline indicated ≤3 phases and ≤10 total cycles, skip phase-by-phase and generate all cycles at once with single review.

---

### Phase 3.1-3.6: Cycle Planning Guidance (Applied Per-Phase)

**Objective:** Generate cycle definitions with RED/GREEN/Stop Conditions.

**Actions (applied within each phase file):**

1. **Number cycles:** X.Y format (1.1, 1.2, ..., 2.1, 2.2, ...)
   - Start at 1.1 (not 0.1 or 1.0)
   - Sequential within phases
   - No duplicates (error), gaps acceptable (warn)

2. **Generate RED specifications (prose format):**

```markdown
**RED Phase:**

**Test:** [test function name]
**Assertions:**
- [Specific assertion 1 — behavioral, not structural]
- [Specific assertion 2]
- [Expected values/behaviors]

**Expected failure:** [Error type or pattern — e.g., "AttributeError: method not found"]

**Why it fails:** [Missing implementation]

**Verify RED:** `pytest [file]::[test_function] -v`
```

   **Prose Test Description Rules:**

   RED phase uses **prose descriptions** of tests, not full code blocks. This saves planning tokens while providing enough specificity for haiku to implement correctly.

   **Prose assertion format:**
   ```markdown
   **Assertions:**
   - format_model("Claude Sonnet 4") returns string containing 🥈 emoji
   - format_model("Claude Opus 4") returns string containing 🥇 emoji
   - Output includes model name substring (e.g., "Sonnet")
   ```

   **NOT full code (anti-pattern):**
   ```python
   def test_format_model():
       result = formatter.format_model("Claude Sonnet 4")
       assert "🥈" in result
       assert "Sonnet" in result
   ```

   **Assertion Quality Requirements:**

   Prose descriptions MUST be behaviorally specific:

   | Weak (vague) | Strong (specific) |
   |---|---|
   | "returns correct value" | "returns string containing 🥈 emoji" |
   | "handles error case" | "raises ValueError with message 'invalid input'" |
   | "processes input correctly" | "output dict contains 'count' key with integer > 0" |

   **Validation rule:** Prose must specify exact expected values, patterns, or behaviors. If assertion could be satisfied by multiple implementations, it's too vague.

   **Logic:**
   - Parse increment for expected behavior
   - Use file mapping from Phase 2 step 4 (discovered via Glob, not inferred)
   - Generate prose assertion from behavior (specific values/patterns)
   - Predict failure message
   - Provide specific test command with actual file path

### Mandatory Conformance Test Cycles

**Trigger:** When design document includes external reference (shell prototype, API spec, visual mockup) in `Reference:` field or spec sections.

**Requirement:** Planner MUST include conformance test cycles that bake expected behavior from the reference into test assertions.

**Mechanism:**
- Reference is consumed at authoring time (during planning)
- Expected strings from reference become test assertions
- Tests are permanent living documentation of expected behavior (reference not preserved as runtime artifact)

**Test precision (from Gap 4):**
- Use precise prose descriptions with exact expected strings from reference
- Example: "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator"
- NOT abstracted: "Assert output contains formatted model with emoji and color"

**Rationale:** Tests that include exact expected strings eliminate translation loss between spec and implementation. This addresses parity failures where tests verified structure but not conformance.

**Related:** See testing.md "Conformance Validation for Migrations" for detailed guidance.

---

3. **Generate GREEN specifications:**

```markdown
**GREEN Phase:**

**Implementation:** [Brief description of what to add/change]

**Behavior:**
- [Behavioral requirement 1 — what the code must DO]
- [Behavioral requirement 2]
- [Behavioral requirement 3]

**Approach:** [Brief hint about algorithm/strategy, referencing design decisions or shell lines if applicable]

**Changes:**
- File: [path]
  Action: [what to add/modify — describe, don't write code]
  Location hint: [where in file, e.g., "after existing method X"]

**Verify GREEN:** [Test command]
- Must pass

**Verify no regression:** [Full test suite]
- All existing tests pass
```

   **CRITICAL — No prescriptive code:** GREEN phases describe BEHAVIOR and provide HINTS. Do NOT include:
   - Complete function implementations
   - Code blocks that can be copied verbatim
   - Exact logic and control flow

   The executor (haiku) must WRITE the code to satisfy RED tests. That's the TDD discipline.

   **Logic:**
   - Extract behavioral requirements from design decisions
   - Describe what the code must DO, not HOW to write it
   - Provide approach hints (algorithm name, shell line reference, pattern to follow)
   - Specify file path and insertion location
   - Use same test command as RED
   - Default regression: `pytest` or `just test`

4. **Classify step type and add investigation prerequisites:**

   **Transformation cycles** (delete, move, rename, replace pattern): Self-contained recipe sufficient. Executor can apply mechanically.

   **Creation cycles** (new test for existing behavior, new integration, new feature touching existing code paths): MUST include investigation prerequisite specifying which production code to read and what to understand before writing.

   **Format for creation cycles:**
   ```markdown
   **Prerequisite:** Read `[file:lines]` — understand [specific behavior/flow/trigger conditions]
   ```

   **Why:** Executors in throughput mode treat all cycles as recipes. Without explicit investigation prerequisites, creation cycles get attempted without understanding the code being tested, leading to trial-and-error failures. The planner has (or can acquire) the system understanding; the executor optimizes for output.

   **Example:** A cycle testing precommit fallback behavior needs: "Read `merge_phases.py:220-260` — understand when `apply_theirs_resolution` is called and what merge state triggers it."

5. **Assign dependencies:**
   - **Default:** Sequential within phase (1.1 → 1.2 → 1.3)
   - **Cross-phase:** `[DEPENDS: X.Y]` if design requires
   - **Regression:** `[REGRESSION]` for existing behavior tests
   - **Parallel:** Only if truly independent

5. **Verify integration coverage:**
   - For each component that reads external state (files, keychain, APIs): at least one cycle mocks and tests the real interaction
   - For each entry point: at least one cycle asserts on output content (not just structure)
   - If components are created separately and need wiring: plan explicit integration cycles
   - **For composition tasks:** Plan xfail integration test at phase start, passing at phase end (see Checkpoints)
   - Metadata cycle count MUST equal actual cycles defined

6. **Stop conditions (auto-generated):**

   Standard TDD stop/error conditions are injected by `prepare-runbook.py` into Common Context during assembly. Expansion agents do NOT need to include per-cycle stop conditions.

   **Custom conditions only:** If a cycle has domain-specific stop conditions beyond standard TDD (external dependencies, performance, security), add them to the cycle content. Standard conditions are inherited from Common Context.

6. **Validate dependency graph:**
   - All referenced cycles exist
   - No circular dependencies (topological sort)
   - No forward dependencies
   - STOP on errors (see error-handling.md)

**Outputs:** cycles, dependency_graph, execution_order

---

### Phase 4: Assembly and Metadata (Tier 3 Only)

**Objective:** Validate phase files are ready for assembly, then delegate to prepare-runbook.py.

**Actions:**

1. **Pre-assembly validation:**
   - Verify all phase files exist (`runbook-phase-1.md` through `runbook-phase-N.md`)
   - Check phase reviews completed (all phase review reports in `reports/` directory)
   - Confirm no ESCALATION flags in review reports

2. **Metadata preparation:**
   - Count total cycles across all phases
   - Extract Common Context elements from design
   - Verify Design Decisions section ready for inclusion

3. **IMPORTANT — Do NOT manually assemble:**
   - Phase files remain separate until prepare-runbook.py processes them
   - Manual concatenation bypasses validation logic (cycle numbering, metadata calculation)
   - prepare-runbook.py will handle assembly in Phase 5 step 5

**Assembled Runbook Structure (reference — generated by prepare-runbook.py, not manually created):**

```markdown
---
name: {feature_name}
type: tdd
model: haiku
---

# {Feature Name} TDD Runbook

**Context**: {goal}
**Design**: {design_path}
**Status**: Draft
**Created**: {date}

## Weak Orchestrator Metadata

**Total Steps**: {N}
**Execution Model**: All cycles: Haiku (TDD execution)
**Step Dependencies**: {sequential|parallel|mixed}
**Error Escalation**: Haiku → User on stop conditions/regression
**Report Locations**: plans/{name}/reports/
**Success Criteria**: All cycles GREEN, no regressions
**Prerequisites**: {from_design}

## Common Context

**Requirements (from design):**
- FR-1: [summary] — addressed by [design element]
- FR-2: [summary] — addressed by [design element]
- NFR-1: [summary] — addressed by [design element]

**Scope boundaries:** [in/out of scope]

**Key Design Decisions:**
{numbered_list}

**TDD Protocol:**
Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Project Paths:**
{paths_from_design}

**Conventions:**
- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly (never suppress)
- Write notes to plans/{name}/reports/cycle-{X}-{Y}-notes.md

**Stop Conditions (all cycles):**
STOP IMMEDIATELY if: RED phase test passes (expected failure) • RED phase failure message doesn't match expected • GREEN phase tests don't pass after implementation • Any phase existing tests break (regression)

Actions when stopped: 1) Document in reports/cycle-{X}-{Y}-notes.md 2) Test passes unexpectedly → Investigate if feature exists 3) Regression → STOP, report broken tests 4) Scope unclear → STOP, document ambiguity

**Dependencies (all cycles):**
{sequential|parallel|per-cycle-specific - factorize if all cycles share pattern}

**Output Optimization Note:** Factorize repetitive content (stop conditions, dependencies, conventions, common patterns) to Common Context. Cycles inherit context during runbook compilation. Reduces planner token output by eliminating per-cycle boilerplate.

## Cycle {X.Y}: {Name} {[DEPENDS: A.B]} {[REGRESSION]}

**Objective**: {goal}

{RED_phase}

---

{GREEN_phase}

---

[Repeat for each cycle]

## Design Decisions
{copy_from_design}

## Dependencies

**Before**: {prerequisites}
**After**: Feature implemented with test coverage, all cycles verified, ready for integration
```

**Write file:**
- Output: `plans/{feature_name}/runbook.md`
- If exists: Ask to overwrite
- STOP on write errors

**Outputs:** runbook_path, runbook file

---

### Phase 4.5: Consolidation Gate — Runbook (Tier 3 Only)

**Objective:** Merge isolated trivial cycles with related features before final review.

**Actions:**

1. **Identify isolated trivial cycles:**
   - Cycles marked for fast-path during Phase 2.5
   - Single-line changes or constant updates
   - Cycles with no test assertions (pure configuration)

2. **Check merge candidates:**

   For each trivial cycle:
   - **Same-file cycles:** Merge with adjacent cycle modifying same file
   - **Setup cycles:** Promote to phase preamble (not separate cycle)
   - **Cleanup cycles:** Demote to phase postamble

3. **Apply cycle consolidation:**

   **Merge into adjacent cycle:**
   ```markdown
   ## Cycle X.Y: [Feature Name]

   **Additional setup:** [trivial work folded in]

   [Standard RED/GREEN content]
   ```

   **Convert to inline instruction:**
   ```markdown
   **Pre-phase setup:**
   - Update config constant to X
   - Add import statement for Y

   ## Cycle X.1: [First real cycle]
   ```

4. **Update metadata:**
   - Adjust Total Steps count
   - Update cycle numbering if merges occurred
   - Note consolidations in runbook header

**Constraints:**
- Never merge cycles across phases
- Preserve test isolation (don't merge if tests would conflict)
- Keep merged cycles ≤5 assertions total

**When to skip:**
- No trivial cycles identified in Phase 2.5
- All cycles have substantial test coverage
- Runbook is already compact (<15 cycles)

**Rationale:** Trivial cycles add orchestrator overhead. A haiku executor can handle "update constant X and then implement feature Y" in one delegation. Consolidation reduces round-trips without losing coverage.

---

### Phase 5: Final Review and Preparation (Tier 3 Only)

**Objective:** Perform holistic review across phase files and prepare execution artifacts.

**Actions:**

1. **Collect per-phase review results:**

   If Phase 3 launched background review agents, read all output files now. For each report: check for ESCALATION. If any escalation found, STOP before holistic review.

2. **Delegate holistic review across phase files:**

   **Agent:** `tdd-plan-reviewer` (fix-all mode)

   **Input:** Multiple phase files (`runbook-phase-1.md` through `runbook-phase-N.md`)

   **What it checks:**
   - Cross-phase consistency (cycle numbering, dependencies across phase boundaries)
   - Prescriptive code in GREEN phases (critical violation)
   - RED/GREEN sequencing within and across phases
   - Overall cycle progression and incremental coherence
   - Metadata alignment (total cycle count across phases)

   **Agent behavior:**
   - Reads ALL phase files in single batched Read call (equally efficient as single file)
   - Fixes issues directly in phase files via batched Edit calls
   - Writes consolidated report to `plans/{name}/reports/runbook-final-review.md`
   - Returns report path (with escalation note if unfixable issues)

   **Triggering phrase:**
   "Review the TDD runbook phases at plans/{name}/runbook-phase-*.md for cross-phase consistency, prescriptive code, and RED/GREEN violations."

   **NOTE:** Batched reads of N files = same efficiency as reading 1 file. No monolithic assembly needed.

3. **Handle review outcome:**
   - Read review report
   - If ESCALATION noted: STOP, address unfixable issues before proceeding
   - If all issues fixed: proceed to step 4

4. **Validate phase file completeness:**
   - All expected phase files exist
   - Design Decisions section ready for inclusion
   - No missing cycles or gaps in numbering

5. **Run prepare-runbook.py** (automated, with sandbox bypass):
   ```bash
   agent-core/bin/prepare-runbook.py plans/{name}/
   # MUST use dangerouslyDisableSandbox: true (writes to .claude/agents/)
   ```

   **Script behavior:**
   - Detects phase files (`runbook-phase-*.md` pattern)
   - Assembles phases into `runbook.md` with metadata
   - Validates cycle numbering and dependencies
   - Generates agent/step artifacts
   - If script fails: STOP and report error to user

   **NOTE:** prepare-runbook.py handles assembly. Planner provides phase files + metadata preparation.

6. **Copy orchestrate command to clipboard:**
   ```bash
   echo -n "/orchestrate {name}" | pbcopy
   ```

7. **Tail-call `/handoff --commit`**

   As the **final action** of this skill, invoke `/handoff --commit`. This:
   - Hands off session context (marks planning complete, adds orchestration as pending)
   - Then tail-calls `/commit` which commits everything and displays the next pending task

   The next pending task (written by handoff) will instruct: "Restart session, switch to haiku model, paste `/orchestrate {name}` from clipboard."

   **Why restart:** prepare-runbook.py creates a new agent in `.claude/agents/`. Claude Code only discovers agents at session start.

**Outputs:** Artifacts created, clipboard loaded, then handoff + commit via tail-call chain

---

## Cycle Breakdown Guidance

**Key principles:**
- Each cycle: 1-3 assertions
- Clear RED failure expectation
- Minimal GREEN implementation
- Sequential dependencies within phase (default)

**Cycle ordering:**
- Start with simplest happy path, not empty/degenerate case
- Only test empty case if it requires special-casing that wouldn't arise naturally from list processing or normal control flow
- Anti-pattern: Cycle 1 tests empty input → GREEN returns `[]` → stub never replaced
- Foundation-first within phase: existence → structure → behavior → refinement
- Anti-pattern: Dedup cycle before the container/key-path creation cycle it operates on
- Each cycle must test a branch point — if RED can pass with `assert callable(X)`, the cycle is vacuous

**Dependency markers:**
- **Sequential (default):** 1.1 → 1.2 → 1.3
- **[DEPENDS: X.Y]:** Cross-phase dependency
- **[REGRESSION]:** Testing existing behavior

**Detailed guidance:** See `references/patterns.md` for granularity criteria, numbering schemes, common patterns

---

## What NOT to Test (Presentation vs Behavior)

TDD tests **behavior**, not **presentation**. Avoid generating cycles for:

| Category | Skip Testing | Test Instead |
|----------|--------------|--------------|
| CLI help text | Exact phrasing, word presence | Command parses correctly, options work |
| Error messages | Exact wording | Error raised, exit code, error type |
| Log output | Format, phrasing | Logged events occur, data captured |
| Documentation | Generated content | Generation process works |

**Heuristic:** If users see output directly and quality is self-evident, don't test exact phrasing.

**Valid exceptions:**
- Regulatory/legal requirements (must include specific warnings)
- Complex generated content (logic produces correct structure)
- Machine-parsed output (API responses, serialization formats)

---

## Checkpoints

Checkpoints are verification points inserted between phases. They validate accumulated work and create commit points.

**Two checkpoint tiers:**

**Light checkpoint** (Fix + Functional):
- **Placement:** Every phase boundary
- **Process:**
  1. **Fix:** Run `just dev`, sonnet quiet-task diagnoses and fixes failures, commit when passing
  2. **Functional:** Sonnet reviews implementations against design
     - Check: Are implementations real or stubs? Do functions compute or return constants?
     - Check: Are I/O operations mocked and tested, or just exit-code tested?
     - If stubs found: STOP, report which implementations need real behavior
     - If all functional: Proceed to next phase

**Full checkpoint** (Fix + Vet + Functional):
- **Placement:** Final phase boundary, or phases marked `checkpoint: full` in runbook
- **Process:**
  1. **Fix:** Run `just dev`, sonnet quiet-task diagnoses and fixes failures, commit when passing
  2. **Vet:** Sonnet reviews accumulated changes (presentation, clarity, design alignment)
     - **REQUIRED:** Apply all fixes (critical, major, minor)
     - Commit when complete
  3. **Functional:** Sonnet reviews implementations against design (same checks as light checkpoint)

**Integration tests (composition tasks):**

When runbook targets multi-module integration:

1. **Phase start:** Write integration test marked `@pytest.mark.xfail(reason="Phase N not implemented")`
   - Test calls top-level entry point
   - Asserts on critical content in output (not just structure)
   - Must fail before phase work begins

2. **Phase end:** Remove xfail marker, verify test passes
   - If test still fails: Phase incomplete, debug before proceeding
   - Integration test catches gaps unit tests miss (results consumed, not just functions called)

**Why:** Unit tests verify modules in isolation. Integration tests verify composition — that functions are called AND their results are used. The statusline-wiring execution found 3 major gaps at vet checkpoint that integration tests would have caught earlier.

**Example:**
```python
# Phase start: xfail
@pytest.mark.xfail(reason="Phase N not implemented")
def test_output_contains_expected_data():
    result = entry_point()
    assert "expected_field" in result
    assert result["count"] > 0

# Phase end: remove xfail, test must pass
def test_output_contains_expected_data():
    result = entry_point()
    assert "expected_field" in result
    assert result["count"] > 0
```

**When to mark `checkpoint: full` during planning:**
- Phase introduces new public API surface or contract
- Phase crosses module boundaries (changes span 3+ packages)
- Runbook expected to exceed 20 cycles total

**Rationale:** Light checkpoints catch dangerous issues (broken tests, stubs) at low cost. Full checkpoints catch quality debt (naming, duplication, abstraction) at boundaries where accumulated changes justify the vet review cost.

**Example:**
```markdown
## Cycle 2.3: Add --verbose flag (final cycle of Phase 2)
[standard RED/GREEN phases]

---

**Light Checkpoint** (end of Phase 2)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 2 implementations against design. Check for stubs.

---

## Cycle 3.1: Add error handling (Phase 3 begins)
[standard RED/GREEN phases]

---

**Full Checkpoint** (end of Phase 3 - final phase)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review all changes for quality, clarity, design alignment. Apply all fixes. Commit.
3. Functional: Review all implementations against design. Check for stubs.
```

---

## Constraints and Error Handling

**Tool usage:**
- **Required:** Read, Write, Grep, Glob
- **Prohibited:** Bash for file content, heredocs

**Error handling:** See `references/error-handling.md` for complete catalog, edge cases, recovery protocols

**Validation rules:**
- Cycle granularity: 1-3 assertions (warn if >5, reject if 0)
- Dependency validation: No circular, forward, or invalid references
- Format validation: Valid YAML, required sections, pattern-compliant cycle headers
- prepare-runbook.py: `type: tdd`, `## Cycle X.Y:` format, extractable Common Context

**Anti-patterns:** See `references/anti-patterns.md` for patterns to avoid

---

## Integration Notes

### prepare-runbook.py Processing

After /plan-tdd generates and reviews runbook, prepare-runbook.py runs **automatically**:

1. Script detects `type: tdd`, uses `agent-core/agents/tdd-task.md` baseline
2. Script generates:
   - `.claude/agents/{name}-task.md` (baseline + Common Context)
   - `plans/{name}/steps/step-{X}-{Y}.md` (individual cycles)
   - `plans/{name}/orchestrator-plan.md` (execution index)
3. Skill commits artifacts, hands off session, copies orchestrate command to clipboard
4. User restarts session, switches to haiku, pastes `/orchestrate {name}`

### Workflow After Generation

```
/plan-tdd → runbook.md → tdd-plan-reviewer → fixes → prepare-runbook.py (auto) → pbcopy
↓
tail: /handoff --commit → updates session.md
↓
tail: /commit → commits everything → displays next pending task
↓
User restarts session, switches to haiku, pastes from clipboard
↓
/orchestrate → Automated execution
↓
Feature implemented with test coverage
```

---

## Success Criteria

**Runbook succeeds when:**
1. ✓ Valid TDD runbook at `plans/{name}/runbook.md`
2. ✓ Frontmatter has `type: tdd`
3. ✓ All cycles have RED/GREEN/Stop Conditions
4. ✓ Valid dependency graph (no cycles)
5. ✓ prepare-runbook.py compatible
6. ✓ Common Context from design
7. ✓ Reasonable cycle count (1-50 typical)
8. ✓ User informed of next steps

**Expected stops (fatal):**
- Design not found
- Unresolved confirmations
- Invalid structure
- Circular dependencies
- Cannot write file

**Warnings (proceed with caution):**
- No design decisions section
- Large runbook (>20 cycles)
- prepare-runbook.py not found

---

## Additional Resources

- **`references/patterns.md`** - Granularity criteria, numbering, common patterns, decision trees
- **`references/anti-patterns.md`** - Patterns to avoid with corrections
- **`references/error-handling.md`** - Error catalog, edge cases, recovery protocols
- **`references/examples.md`** - Complete runbook examples

---

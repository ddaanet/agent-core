# Runbook Examples

Complete examples demonstrating proper runbook structure for both TDD and general steps.

## TDD Examples

---

## Example: Authentication Feature

### Design Document (Excerpt)

```markdown
# Authentication Feature Design

**Goal:** Implement OAuth2 authentication with Google and GitHub providers

## Design Decisions

**Decision 1: Provider Architecture**
- Choice: Strategy pattern with provider interface
- Rationale: Easy addition of new providers

**Decision 2: Session Storage**
- Choice: JWT tokens with Redis cache
- Rationale: Stateless, scalable, fast lookup

## Phase 1: Core OAuth2 Flow

### Provider interface
Define common interface for all OAuth2 providers (authenticate, get_user, refresh_token methods)

### Google provider
Implement Google-specific OAuth2 flow

### GitHub provider
Implement GitHub-specific OAuth2 flow

## Phase 2: Session Management

### JWT generation
Create JWT tokens after successful authentication

### Token validation
Validate JWT tokens on protected routes
```

---

### Generated Runbook (Excerpt)

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

## Weak Orchestrator Metadata

**Total Steps**: 5
**Execution Model**: All cycles: Haiku (TDD execution)
**Step Dependencies**: Sequential
**Error Escalation**: Haiku → User on stop conditions/regression
**Report Locations**: plans/auth-feature/reports/
**Success Criteria**: All cycles GREEN, no regressions
**Prerequisites**: Python 3.11+, pytest, Redis server

## Common Context

**Key Design Decisions:**

1. **Provider Architecture**
   - Choice: Strategy pattern with provider interface
   - Rationale: Easy addition of new providers

2. **Session Storage**
   - Choice: JWT tokens with Redis cache
   - Rationale: Stateless, scalable, fast lookup

**TDD Protocol:**
Strict RED-GREEN-REFACTOR: 1) RED: failing test, 2) Verify RED, 3) GREEN: minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Project Paths:**
- Source: src/auth/
- Tests: tests/test_auth.py

**Conventions:**
- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly
- Write notes to plans/auth-feature/reports/cycle-{X}-{Y}-notes.md

---

## Cycle 1.1: Implement Provider Interface

**Objective**: Define common interface for OAuth2 providers

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Add test in tests/test_auth.py asserting provider interface has required methods

**Expected failure:**
```
ModuleNotFoundError: No module named 'auth.providers'
```

**Why it fails:** Provider module doesn't exist yet

**Verify RED:** Run pytest tests/test_auth.py::test_provider_interface -v
- Must fail with ModuleNotFoundError
- If passes, STOP - module may already exist

---

**GREEN Phase:**

**Implementation:** Create provider interface with required methods

**Changes:**
- File: src/auth/providers/__init__.py
  Action: Create directory and file
  Action: Define ProviderInterface class with authenticate(), get_user(), refresh_token() methods

**Verify GREEN:** Run pytest tests/test_auth.py::test_provider_interface -v
- Must pass

**Verify no regression:** Run pytest tests/
- All existing tests must pass

---

**Stop Conditions:**

**STOP IMMEDIATELY if:**
- Test passes on first run (expected RED failure)
- Test failure message doesn't match expected
- Test passes after partial GREEN implementation
- Any existing test breaks (regression failure)

**Actions when stopped:**
1. Document in plans/auth-feature/reports/cycle-1-1-notes.md
2. If test passes unexpectedly: Check if interface exists, mark [REGRESSION] or fix test
3. If regression: STOP, report broken tests, escalate

**Expected Outcome**: Interface defined, test passes, no regressions

**Error Conditions**:
- RED doesn't fail → STOP
- GREEN doesn't pass → Debug
- Regression → STOP, escalate

**Validation**:
- RED verified ✓
- GREEN verified ✓
- No regressions ✓

**Success Criteria**:
- RED verified (ModuleNotFoundError)
- GREEN verified (test passes)
- No regression (all tests pass)

**Report Path**: plans/auth-feature/reports/cycle-1-1-notes.md

---

## Cycle 1.2: Add Google Provider [DEPENDS: 1.1]

[Similar structure: RED → GREEN → Stop Conditions]

---

## Cycle 1.3: Add GitHub Provider [DEPENDS: 1.2]

[Similar structure]

---

## Cycle 2.1: Generate JWT Tokens [DEPENDS: 1.3]

[Similar structure]

---

## Cycle 2.2: Validate JWT Tokens [DEPENDS: 2.1]

[Similar structure]

---

## Design Decisions

[Copied from design document]

---

## Dependencies

**Before**: Design complete, prerequisites verified
**After**: OAuth2 implemented, Google/GitHub working, JWT session management complete, full test coverage

---
```

---

## Key Observations

**Runbook structure:**
- Frontmatter with `type: tdd` enables prepare-runbook.py detection
- Weak Orchestrator Metadata provides execution guidance
- Common Context shared across all cycles
- Each cycle: complete RED-GREEN-Stop pattern

**Cycle breakdown:**
- 5 cycles for 5 increments (1:1 mapping)
- Sequential dependencies within phases (1.1 → 1.2 → 1.3)
- Cross-phase dependency (2.1 depends on 1.3)

**Execution flow:**
- prepare-runbook.py splits into individual cycle files
- Orchestrator executes sequentially
- Each cycle isolated, stop on any condition trigger

---

## General Step Examples

### Example: Creation Step (with investigation prerequisite)

```markdown
## Step 3.1: Create review-taxonomy.md reference file

**Objective**: Extract status taxonomy from corrector into standalone reference file to keep agent under 400-line threshold.

**Prerequisites**:
- Read `agent-core/agents/corrector.md` (understand current status handling and report format)
- Read `agents/decisions/pipeline-contracts.md` (ODC classification context for taxonomy grounding)

**Implementation**:

Create `agent-core/agents/review-taxonomy.md`:

1. **Four-status definitions** with criteria and examples:
   - FIXED: Applied, no action needed
   - DEFERRED: Real issue, explicitly out of scope (maps to scope OUT)
   - OUT-OF-SCOPE: Not relevant to current review
   - UNFIXABLE: Technical blocker requiring user decision (with subcategory code)

2. **UNFIXABLE subcategory codes**:
   - U-REQ: Requirements ambiguity or conflict
   - U-ARCH: Architectural constraint or design conflict
   - U-DESIGN: Design decision needed, multiple valid approaches

3. **Deferred Items report section template**

**Expected Outcome**:
- review-taxonomy.md exists with all four statuses defined
- Each status has criteria text and at least one concrete example
- UNFIXABLE subcategories have codes and descriptions
- Deferred Items template is copy-pasteable into reports

**Error Conditions**:
- If status definitions overlap -> sharpen distinguishing criteria (DEFERRED = in scope OUT list; OUT-OF-SCOPE = unrelated to review)
- If subcategory codes ambiguous -> add decision tree for classification

**Validation**:
1. Commit changes
2. Delegate to agent-creator: "Review review-taxonomy.md for completeness and clarity of status definitions"
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-3.1-agent-review.md
```

---

### Example: Transformation Step (self-contained)

```markdown
## Step 6.1: Delete Phase 1.4 from runbook skill

**Objective**: Remove obsolete Phase 1.4 (file size awareness) section, now redundant with outline-level enforcement.

**Prerequisites**:
- Read `agent-core/skills/runbook/SKILL.md` (locate Phase 1.4 section boundaries)

**Implementation**:

1. **Locate Phase 1.4**: heading "Phase 1.4: File Size Awareness"
2. **Delete entire section**: heading through next phase heading
3. **Verify no orphaned references**: Grep SKILL.md for "1.4" and "file size awareness"
4. **Remove cross-references**: update any remaining mentions

**Expected Outcome**:
- Phase 1.4 section no longer exists in SKILL.md
- No references to "Phase 1.4" or "file size awareness" remain in the file
- Surrounding sections maintain correct structure

**Error Conditions**:
- If section heading not found -> Grep for variants ("File Size", "file growth", "1.4")
- If orphaned references found -> update or remove each reference

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review runbook skill Phase 1.4 deletion for clean removal"
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-6.1-skill-review.md
```

---

### Key Observations

**General step structure:**
- No RED/GREEN phases — steps describe direct implementation
- Prerequisites scale with step type: creation needs investigation, transformation needs target read
- Expected Outcome must be concrete and verifiable, not vague
- Error Conditions map specific failures to recovery actions
- Validation delegates to domain-appropriate reviewer (see artifact review routing in `pipeline-contracts.md`)

**Creation vs transformation:**
- Creation steps: 2+ prerequisite reads (pattern + context), investigation gate if cross-file
- Transformation steps: single prerequisite read (target file), recipe in Implementation section
- Both: concrete Expected Outcome, specific Error Conditions, reviewer-based Validation

---

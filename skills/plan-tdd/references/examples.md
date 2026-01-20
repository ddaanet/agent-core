# TDD Runbook Examples

Complete examples demonstrating proper TDD runbook structure.

---

## Example Design Document Snippet

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

---

## Example Generated Cycle

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

---

## Example Complete Runbook Structure

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

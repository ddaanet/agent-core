# Error Handling and Edge Cases

This document provides detailed guidance for handling errors and edge cases during TDD runbook generation.

---

## Input Validation Errors

### Error: Design document not found

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

### Error: Missing TDD sections

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

### Error: Unresolved confirmations

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

## Cycle Generation Errors

### Error: Empty cycle (no assertions)

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

### Error: Circular dependencies detected

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

### Error: Invalid cycle ID format

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

### Error: Duplicate cycle IDs

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

## Integration Errors

### Error: Cannot write runbook file

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

### Error: prepare-runbook.py not available

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

## Edge Cases

### Edge Case 1: Single-cycle feature

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

### Edge Case 2: No dependencies between cycles

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

### Edge Case 3: All cycles are regressions

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

### Edge Case 4: Cycle depends on future cycle

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

### Edge Case 5: Empty cycle (no assertions)

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

### Edge Case 6: Complex cycle (>5 assertions)

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

### Edge Case 7: Missing design decisions

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

### Edge Case 8: Very large runbook (>50 cycles)

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

## Recovery Protocols

### Protocol 1: Validation failure

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

### Protocol 2: Partial runbook generation

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

### Protocol 3: User intervention needed

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

### Protocol 4: Dependency resolution failure

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

### Protocol 5: prepare-runbook.py compatibility issue

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

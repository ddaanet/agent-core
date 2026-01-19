## Error Classification for Weak Orchestrator

When agents execute steps, errors fall into distinct categories that determine escalation path and recovery strategy. This classification prevents silent failures and enables appropriate escalation timing.

### Error Category Taxonomy

| Category | Definition | Examples | Trigger Conditions | Escalation Path |
|----------|-----------|----------|-------------------|-----------------|
| **Prerequisite Failure** | Resources or assumptions referenced in plan don't exist or are inaccessible | File path doesn't exist (phase2: `/Users/david/code/pytest-md/CLAUDE.md` → actually `AGENTS.md`); External dependency unavailable; Environment variable missing; Directory structure different than expected | Agent attempts operation on non-existent resource; Test detects assumption violation; File I/O fails with "not found" | Haiku → Sonnet (diagnostic) → Fix applied or plan revision requested |
| **Execution Error** | Script or command fails during normal operation | Test suite failure; Build compilation error; Git merge conflict; Linting errors; Script returns non-zero exit code | Agent runs command successfully but receives non-zero exit code; Tool operation fails after initial validation; Logic error in script | Haiku → Sonnet (if recoverable) or Opus (if complex) |
| **Unexpected Result** | Operation succeeds but output differs from expected specification | File created but with wrong format; Analysis missing required sections; Output size doesn't match expected range; Validation criteria not met | Agent validates output against success criteria; Actual outcome ≠ expected outcome; Content check finds missing data | Haiku → Sonnet (verification) → Plan revision or workaround |
| **Ambiguity Error** | Requirements or context insufficient to proceed safely | Step instructions unclear; Multiple valid interpretations; Conflicting instructions in plan; Unclear success criteria | Agent cannot determine correct action; Multiple valid approaches exist; Plan doesn't specify preference | Haiku → Sonnet (diagnostic) → Opus (plan update) |

### Escalation Flow Walkthrough

**Phase 2 Validation Example: Step 2.3 Prerequisite Failure**

```
Orchestrator (haiku):
  "Execute step 2.3: Analyze pytest-md AGENTS.md"
  Invoke plan-specific agent with step 2.3 reference

Agent (haiku):
  Attempts: Read("/Users/david/code/pytest-md/CLAUDE.md")
  Result: File not found
  Classifies: PREREQUISITE_FAILURE
  Returns: "Error: Prerequisite failure - CLAUDE.md referenced in plan
            but file doesn't exist at specified path"

Orchestrator:
  Receives error message
  Classifies: Simple error (prerequisite mismatch)
  Escalates to Sonnet for diagnostic

Diagnostic Agent (sonnet):
  Reads error context and plan step
  Checks actual directory: /Users/david/code/pytest-md/
  Finds: AGENTS.md exists (not CLAUDE.md)
  Analyzes: Plan mistakenly referenced wrong filename
  Determines: Fix is simple - update path in step
  Returns: "Prerequisite issue resolved. File is AGENTS.md, not CLAUDE.md.
            Corrected step 2.3 reference and re-executed.
            Report: reports/phase2-step3-execution.md"

Orchestrator:
  Step 2.3 complete → Continue to next step
```

**Key insight:** Prerequisite validation during planning phase would have caught this before execution. Prevention impact: ~80% of escalation-triggering errors.

### Integration with Weak Orchestrator Pattern

**During Planning (Haiku Prevention):**
- Sonnet reviews plan before execution
- Includes prerequisite validation checklist
- Verifies all referenced files, directories, external resources exist
- Documents verification method (Bash check, Read tool, Glob tool, etc.)
- Catches prerequisite failures ~80% of time before orchestration starts

**During Execution (Haiku Detection):**
- Agent executes step and validates results
- If error occurs, agent stops immediately (no retries without escalation)
- Agent classifies error into one of 4 categories
- Agent returns clear error message with category and details
- Orchestrator makes escalation decision based on category

**During Escalation (Sonnet Recovery):**
- Sonnet receives error context from orchestrator
- Sonnet reads plan step and error details
- Sonnet determines if error is fixable (simple) or requires plan revision (complex)
- Simple errors: Sonnet fixes and re-executes
- Complex errors: Sonnet reports to orchestrator, escalates to user

### Error Classification Logic for Agents

When executing a step, use this decision tree:

```
If operation fails or output unexpected:
  1. Does error indicate missing resource (file/directory/dependency)?
     YES → PREREQUISITE_FAILURE (escalate to sonnet for diagnostic)
     NO → Continue

  2. Did command/script execute but return non-zero exit code?
     YES → EXECUTION_ERROR (escalate to sonnet for analysis)
     NO → Continue

  3. Did operation succeed but output doesn't match validation criteria?
     YES → UNEXPECTED_RESULT (escalate to sonnet for verification)
     NO → Continue

  4. Are requirements ambiguous or insufficient to proceed safely?
     YES → AMBIGUITY_ERROR (escalate to sonnet, may need opus plan update)
     NO → Step succeeded

Return error message with category and diagnostic details.
Stop immediately - do NOT retry without escalation.
```

### Common Patterns by Category

**Prerequisite Failure Indicators:**
- `No such file or directory`
- `Permission denied` (insufficient access)
- `Connection refused` (external service unavailable)
- `Module not found` or `ImportError`
- Tool/command not found in PATH
- Environment variable not set

**Execution Error Indicators:**
- Command exits with non-zero status
- Test assertions fail
- Build compilation error
- Git operations fail (merge conflict, push rejected)
- Lint/format violations
- Script error output on stderr

**Unexpected Result Indicators:**
- File created but wrong format/structure
- Output present but missing expected sections
- Counts don't match (expected 5 items, got 3)
- File size out of expected range
- Content validation check fails (format, encoding)

**Ambiguity Error Indicators:**
- Multiple valid interpretations of instructions
- Conflicting requirements in plan
- Unclear success criteria
- Unknown recovery protocol
- Plan silent on error handling for this condition

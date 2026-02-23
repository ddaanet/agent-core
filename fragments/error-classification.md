## Error Classification for Weak Orchestrator

When agents execute steps, errors fall into distinct categories that determine escalation path and recovery strategy. This classification prevents silent failures and enables appropriate escalation timing.

**Framework grounding:** Classification adapted from Avižienis Fundamental Error Framework (fault/failure chain), Temporal retry semantics (retryable vs non-retryable), and MASFT FC2 (inter-agent misalignment). See `plans/reports/error-handling-grounding.md` for full grounding analysis.

### Fault vs Failure Vocabulary

Categories 1 and 4 are **faults** (causes): prerequisite = environment fault, ambiguity = specification fault. Response: prevention-oriented (validate, clarify).

Categories 2, 3, and 5 are **failures** (observations): execution error = service deviation, unexpected result = output deviation, misalignment = agent behavioral deviation. Response: tolerance-oriented (retry, escalate, compensate).

### Error Category Taxonomy

| Category | Definition | Examples | Trigger Conditions | Escalation Path |
|----------|-----------|----------|-------------------|-----------------|
| **Prerequisite Failure** | Resources or assumptions referenced in plan don't exist or are inaccessible | File path doesn't exist (phase2: `/Users/david/code/pytest-md/CLAUDE.md` → actually `AGENTS.md`); External dependency unavailable; Environment variable missing; Directory structure different than expected | Agent attempts operation on non-existent resource; Test detects assumption violation; File I/O fails with "not found" | Haiku → Sonnet (diagnostic) → Fix applied or plan revision requested |
| **Execution Error** | Script or command fails during normal operation | Test suite failure; Build compilation error; Git merge conflict; Linting errors; Script returns non-zero exit code | Agent runs command successfully but receives non-zero exit code; Tool operation fails after initial validation; Logic error in script | Haiku → Sonnet (if recoverable) or Opus (if complex) |
| **Unexpected Result** | Operation succeeds but output differs from expected specification | File created but with wrong format; Analysis missing required sections; Output size doesn't match expected range; Validation criteria not met | Agent validates output against success criteria; Actual outcome ≠ expected outcome; Content check finds missing data | Haiku → Sonnet (verification) → Plan revision or workaround |
| **Ambiguity Error** | Requirements or context insufficient to proceed safely | Step instructions unclear; Multiple valid interpretations; Conflicting instructions in plan; Unclear success criteria | Agent cannot determine correct action; Multiple valid approaches exist; Plan doesn't specify preference | Haiku → Sonnet (diagnostic) → Opus (plan update) |
| **Inter-Agent Misalignment** | Agent deviates from specification or provided context (MASFT FC2) | Vet confabulation (inventing issues); Over-escalation (pattern-matching not design); Skipping steps; Premature termination; Incomplete verification; Reasoning-action mismatch | Agent output contradicts explicit instructions; Verification reveals drift from spec; Review catches fabricated claims | Detected by existing review pipeline (outline-corrector, runbook-corrector, corrector). No new detection mechanism — category names what reviews already catch |

### Retryable vs Non-Retryable (Temporal Pattern)

Each failure is classified as retryable or non-retryable. This informs recovery strategy per subsystem.

| Category | Retryable | Non-Retryable |
|----------|-----------|---------------|
| Prerequisite Failure | Transient env issue (service restart, network blip) | Missing file, wrong path, missing dependency |
| Execution Error | Timeout, write conflict, flaky test | Compilation error, design flaw, logic error |
| Unexpected Result | Stale cache, race condition | Wrong algorithm, spec mismatch |
| Ambiguity Error | — (never retryable) | Always: insufficient spec |
| Inter-Agent Misalignment | Context window overflow (retry with less context) | Systematic: model limitation, contradictory instructions |

**Subsystem response varies:**
- **Orchestration (Layer 2):** Retries retryable failures via Sonnet diagnostic before escalating. Non-retryable escalate immediately.
- **CPS chains (Layer 4):** Records classification but aborts regardless (0 retries by default). Classification informs the recorded error context for manual resume.
- **Task lifecycle (Layer 3):** Retryable → `[!]` blocked (waiting on fix). Non-retryable → `[✗]` failed (requires user decision).

### Tier-Aware Classification

Error classification responsibility depends on agent model tier:

- **Sonnet/Opus execution agents:** Self-classify using the 5-category taxonomy and report the classified error with category label
- **Haiku execution agents:** Report raw error with diagnostic details. Orchestrator classifies on their behalf.

**Rationale:** Execution agent has full error context (stack trace, file state). Sonnet/Opus can classify reliably. Transmitting raw errors to orchestrator for haiku agents preserves fidelity without requiring haiku to make nuanced classification judgments.

### Escalation Flow Walkthrough

**Phase 2 Validation Example: Step 2.3 Prerequisite Failure**

```
Orchestrator (haiku):
  "Execute step 2.3: Analyze pytest-md AGENTS.md"
  Invoke plan-specific agent with step 2.3 reference

Agent (haiku):
  Attempts: Read("/Users/david/code/pytest-md/CLAUDE.md")
  Result: File not found
  Returns: "Error: File not found - CLAUDE.md referenced in plan
            but file doesn't exist at specified path"
  (Haiku reports raw error — does not self-classify)

Orchestrator:
  Receives raw error from haiku agent
  Classifies: PREREQUISITE_FAILURE (simple, retryable: no — wrong path)
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

**During Execution (Agent Detection):**
- Agent executes step and validates results
- If error occurs, agent stops immediately (no retries without escalation)
- Sonnet/Opus agents self-classify into one of 5 categories; haiku agents report raw error
- Agent returns clear error message with category (or raw details for haiku) and retryable/non-retryable classification
- Orchestrator classifies on behalf of haiku agents, then makes escalation decision

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

  4. Does output contradict explicit instructions, skip specified steps,
     or contain fabricated claims?
     YES → INTER_AGENT_MISALIGNMENT (detected by review pipeline)
     NO → Continue

  5. Are requirements ambiguous or insufficient to proceed safely?
     YES → AMBIGUITY_ERROR (escalate to sonnet, may need opus plan update)
     NO → Step succeeded

Return error message with: category, retryable/non-retryable classification,
and diagnostic details.
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

**Inter-Agent Misalignment Indicators:**
- Agent output contradicts explicit instruction in prompt
- Verification reveals drift from design spec
- Vet report contains fabricated fix claims
- Agent skips steps or terminates before completing scope
- Reasoning traces show correct analysis but action diverges
- Review catches issues not present in source material (confabulation)

**Ambiguity Error Indicators:**
- Multiple valid interpretations of instructions
- Conflicting requirements in plan
- Unclear success criteria
- Unknown recovery protocol
- Plan silent on error handling for this condition

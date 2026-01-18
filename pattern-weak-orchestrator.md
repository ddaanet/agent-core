# Pattern: Weak Orchestrator

## Problem Statement

When executing multi-step plans, we face a fundamental trade-off:

**Strong orchestration** (sonnet/opus-level reasoning):
- Makes judgment calls about errors and recovery
- Adapts plan on-the-fly based on results
- High token cost per step
- Risk of silent failure (orchestrator "fixes" problems without escalation)
- Context bloat from decision-making

**Weak orchestration** (haiku-level delegation):
- Executes steps mechanically
- Escalates on any deviation from expected path
- Minimal token cost per step
- Explicit error handling (forced escalation)
- Lean context (delegation-only, no reasoning)

**The problem:** We need reliable plan execution with minimal token cost and explicit error visibility.

## Solution

The weak orchestrator is a **delegation-only agent** with haiku-level complexity:

**Core principle:** No judgment calls. Only execute → verify → continue or escalate.

**Role boundaries:**
- **Planning:** Done before orchestration begins (opus-level)
- **Execution:** Delegated to plan-specific agents (step by step)
- **Recovery:** Escalated to higher-level agents (sonnet for simple, opus for complex)
- **Orchestration:** Mechanical step progression with explicit error handling

**Key insight:** By removing judgment from the orchestrator, we force errors to surface explicitly rather than being silently handled.

## Implementation

### Orchestrator Behavior (Step-by-Step)

```
For each step in plan:
  1. Read plan step specification
  2. Invoke plan-specific agent with step reference
  3. Receive result (filename or error message)
  4. If success:
     - Mark step complete
     - Continue to next step
  5. If error:
     - Classify error (simple vs complex)
     - Escalate appropriately
```

### Error Classification

**Simple errors** (delegate to sonnet for diagnostic/fix):
- Missing dependencies (install, configure)
- Environment setup issues (paths, permissions)
- Known failure modes (test failure, lint error)
- Recoverable without plan changes

**Complex errors** (abort, request opus plan update):
- Plan assumptions violated (file structure different than expected)
- Architectural conflicts (design incompatible with codebase)
- Ambiguous requirements (unclear how to proceed)
- Require plan revision to resolve

### Agent Invocation Pattern

```
Invoke plan-specific agent:
  System prompt = baseline agent + plan context
  User prompt = "Execute step N: [step reference]"

Expect terse response:
  Success: "reports/step-N.md"
  Failure: "Error: [diagnostic info]"
```

### Escalation Protocol

**Simple error flow:**
```
Orchestrator (haiku):
  "Step 3 failed with [error]. Delegating to sonnet for diagnostic."

Diagnostic Agent (sonnet):
  - Reads error context
  - Determines fix
  - Either: Fixes and returns to orchestrator
  - Or: Reclassifies as complex, escalates to opus
```

**Complex error flow:**
```
Orchestrator (haiku):
  "Step 3 failed with [error]. Plan assumption violated.
   Aborting execution. Context: [details]
   Requesting opus plan update."

Planning Agent (opus):
  - Reviews plan step
  - Reviews error context
  - Updates plan or provides guidance
  - Returns to orchestrator for retry
```

## Integration with Other Patterns

### Plan-Specific Agents

The weak orchestrator relies on **plan-specific agents** for execution:

**Plan-specific agent = baseline agent + plan context**

**Benefits:**
- Context caching (plan context reused across steps)
- Clean execution (fresh agent per step, no noise)
- Specialization (agent knows plan goals, constraints, structure)

**Orchestrator's role:**
- Append step reference to create step-specific prompt
- Invoke agent, receive result
- No context management (agent handles plan knowledge)

### Quiet Execution Pattern

The weak orchestrator depends on **quiet execution** for efficiency:

**Quiet execution requirements:**
- Agents write detailed output to files (reports directory)
- Agents return only: filename (success) or error message (failure)
- Orchestrator never parses detailed output

**Benefits:**
- Orchestrator context stays lean
- Detailed logs available for debugging
- Token-efficient delegation
- Parallel execution possible (independent steps)

**Integration:**
```
Orchestrator delegates step → Agent executes → Agent writes report
  ↓
Orchestrator receives filename → Marks step complete → Continues
  ↓
(Optional) Summary agent reads report → Provides distilled update to user
```

## Examples

### Success Case

```
Orchestrator (haiku):
  Step 1: Create baseline agent template
  → Invoke plan-specific agent

Agent (haiku):
  Executes step 1
  Writes: plans/task-agents/reports/step-1.md
  Returns: "plans/task-agents/reports/step-1.md"

Orchestrator:
  Step 1 complete → Continue to step 2
```

### Simple Error Case

```
Orchestrator (haiku):
  Step 3: Run tests
  → Invoke plan-specific agent

Agent (haiku):
  Executes step 3
  Returns: "Error: Tests failed - dependency missing"

Orchestrator:
  Simple error (dependency issue)
  → Delegate to sonnet for fix

Diagnostic Agent (sonnet):
  Reads error: "dependency missing"
  Installs dependency
  Retries tests
  Returns: "Fixed. Tests passing. Report: reports/step-3-retry.md"

Orchestrator:
  Step 3 complete → Continue to step 4
```

### Complex Error Case

```
Orchestrator (haiku):
  Step 5: Integrate with existing module
  → Invoke plan-specific agent

Agent (haiku):
  Attempts step 5
  Returns: "Error: Module structure incompatible with plan assumptions.
            Expected src/module.ts, found lib/index.ts with different exports."

Orchestrator:
  Complex error (plan assumption violated)
  → Abort execution
  → Escalate to opus

Context provided to user:
  "Step 5 failed due to architectural mismatch.
   Plan assumed module structure A, codebase has structure B.
   Requesting plan revision before continuing.
   Error details: [context]"
```

## Constraints

### What the Orchestrator Should NOT Do

**Do not make judgment calls:**
- Do not decide how to fix errors
- Do not adapt the plan based on results
- Do not interpret ambiguous requirements
- Do not choose between alternative approaches

**Do not execute directly:**
- Do not run commands
- Do not edit files
- Do not analyze code
- Delegation only

**Do not accumulate context:**
- Do not read detailed reports
- Do not summarize progress
- Do not maintain execution history
- Keep transcript minimal

**Do not hide errors:**
- Do not retry without escalation
- Do not assume "probably fine"
- Do not continue on unexpected results
- Surface all deviations explicitly

### What the Orchestrator SHOULD Do

**Execute mechanically:**
- Read step specification
- Invoke plan-specific agent
- Receive result
- Continue or escalate

**Classify errors explicitly:**
- Simple (delegate to sonnet)
- Complex (escalate to opus)
- No ambiguity

**Maintain lean context:**
- Track step completion
- Record escalations
- Minimal transcript

**Surface visibility:**
- Report progress (step N complete)
- Report escalations (step N failed, reason)
- Provide context for human review

## Design Rationale

### Why Haiku-Level?

**Token efficiency:**
- Plan execution is mechanical (read, delegate, verify, continue)
- No complex reasoning required
- High step count → cost multiplier matters

**Forced escalation:**
- Haiku cannot make sophisticated judgment calls
- Errors must surface explicitly
- Prevents silent failure modes

**Speed:**
- Faster response time per step
- Unblocked execution for simple cases

### Why Delegation-Only?

**Separation of concerns:**
- Planning (opus): What to do
- Execution (haiku via plan-specific agents): Do it
- Orchestration (haiku): Track progress, escalate issues

**Context management:**
- Execution details stay in agent transcripts
- Orchestrator sees only success/failure
- No context bloat from implementation details

**Error visibility:**
- No orchestrator "fixes" (would require judgment)
- All errors escalate explicitly
- Clear audit trail

### Why Escalation Tiers?

**Cost optimization:**
- Simple errors → sonnet (fast, cheap, capable)
- Complex errors → opus (slow, expensive, necessary)
- Orchestrator doesn't need to solve, only classify

**Clear boundaries:**
- Simple = fixable without plan changes
- Complex = requires plan revision
- Reduces ambiguity in error handling

## Status

**Implementation status:** Proof-of-concept phase

**Validation approach:**
1. Document pattern (this file)
2. Execute real plan step using weak orchestrator
3. Capture lessons learned
4. Refine pattern based on results

**Open questions:**
- Can haiku reliably classify errors as simple vs complex?
- Does escalation overhead outweigh token savings?
- How often do "simple" errors require reclassification?
- Is step-level granularity appropriate, or should orchestrator handle sub-steps?

**Next steps:**
- Apply to Phase 2 unification plan
- Measure token usage vs. direct sonnet orchestration
- Document failure modes
- Refine error classification criteria

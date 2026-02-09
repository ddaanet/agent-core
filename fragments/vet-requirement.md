## Vet Requirement

**Rule:** After creating any production artifact, delegate to `vet-fix-agent` for review and fix.

**Production artifacts requiring vet:**
- Plans (runbooks)
- Code (implementations, scripts)
- Tests
- Agent procedures
- Skill definitions
- Documentation that defines behavior or contracts

**Design documents:** Reviewed by opus (`design-vet-agent`).

**Artifacts NOT requiring vet:**
- Execution reports
- Diagnostic outputs
- Log files
- Temporary analysis
- Session handoffs (already reviewed during /handoff)

**Vet process:**
1. Create artifact
2. Delegate to `vet-fix-agent` with execution context (see below)
3. Read report, grep for UNFIXABLE (see detection protocol below)
4. If UNFIXABLE found: STOP, escalate to user
5. If all fixed: proceed

**No importance filtering.** The vet-fix-agent applies all fixes (critical, major, minor). The caller does not triage or defer fixes.

**Why:** Early review catches issues before they propagate. Applying all fixes eliminates drift from deferred minor issues accumulating across sessions.

### Execution Context

**Rule:** Every vet delegation must include execution context — what was done, what state the system should be in, and what's in/out of scope.

**Why:** Vet validates against current filesystem, not execution-time state. Without context, vet may confabulate issues from future work, validate stale state, or miss drift from prior phases.

**Required context fields:**
- **Scope IN:** What was implemented/changed (methods, features, files)
- **Scope OUT:** What is NOT yet implemented (future phases, deferred items) — prevents false positives
- **Changed files:** Explicit file list (from `git diff --name-only` or known from implementation)
- **Requirements summary:** What the implementation should satisfy (from design/requirements)

**Optional context fields (for phased work):**
- **Prior state:** What earlier phases established (dependencies, data models, interfaces)
- **Design reference:** Path to design document for alignment checking

**Delegation template:**

Review [scope description].

**Scope:**
- IN: [list what was implemented]
- OUT: [list what is NOT yet done — do NOT flag these]

**Changed files:** [file list]

**Requirements:**
- [requirement 1]
- [requirement 2]

Fix all issues. Write report to: [report-path]
Return filepath or error.

### UNFIXABLE Detection Protocol

**Rule:** After vet-fix-agent returns, mechanically check for UNFIXABLE issues before proceeding.

**Detection steps:**
1. Read the report file returned by vet-fix-agent
2. Use Grep to search for `UNFIXABLE` in the report content
3. If found: **STOP** — do NOT proceed to next step
4. Report UNFIXABLE issues to user with report path
5. Wait for user guidance

**Why mechanical grep, not judgment:** Weak orchestrator pattern requires mechanical checks. UNFIXABLE detection is pattern-matching (grep), not evaluation — consistent with "trust agents, escalate failures."

**Anti-pattern:** Reading vet report, seeing UNFIXABLE issues, and proceeding anyway because they "seem minor." ALL UNFIXABLE issues require user decision.

**Example:**
```
1. Create: agent-core/agents/test-hooks.md
2. Vet: Task(subagent_type="vet-fix-agent") with execution context
3. Read report → grep UNFIXABLE → none found
4. Result: All fixable issues resolved, proceed
```

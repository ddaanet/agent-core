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

**Alignment verification:** Vet must verify output matches design/requirements/acceptance criteria. This is not optional — vet checks presence AND correctness.

**Model-agnostic:** Applies to haiku, sonnet, opus equally.

**Delegation requires specification:** If delegating implementation, provide criteria for alignment verification. Without criteria, executing agent cannot verify alignment, vet cannot check drift.

**Reports exempt:** Reports ARE the verification artifacts.

### Execution Context

**Rule:** Every vet delegation must include execution context — what was done, what state the system should be in, and what's in/out of scope.

**Why:** Vet validates against current filesystem, not execution-time state. Without context, vet may confabulate issues from future work, validate stale state, or miss drift from prior phases.

**Required context fields — must be structured lists, not empty prose. Fail loudly if any field is missing or contains only placeholder text.**
- **Scope IN:** Structured list of what was implemented/changed. Each item must name a concrete artifact (file, function, section). Grounds the review — without IN, vet has no target.
- **Scope OUT:** Structured list of what is NOT yet implemented (future phases, deferred items). Each item must be specific enough to match against vet findings. Prevents false positives — without OUT, vet confabulates issues from future work.
- **Changed files:** Explicit file list (from `git diff --name-only` or known from implementation). Must not be empty.
- **Requirements summary:** What the implementation should satisfy (from design/requirements). Must reference specific FRs, acceptance criteria, or behavioral expectations.

**Anti-pattern:** Give vet-fix-agent full design.md when reviewing phase checkpoint — agent may confabulate issues from future phases.

**Correct pattern:** Precommit-first grounds agent in real work; explicit IN/OUT scope prevents confabulating future-phase issues.

**Rationale:** Agent saw content in Phase 2 design, invented that test existed and claimed to fix it. Fix claims are dangerous (trusted by orchestrator), observations less so.

**Mitigations:** Precommit-first, explicit scope, "Do NOT flag items outside provided scope" constraint.

**Optional context fields (for phased work):**
- **Prior state:** What earlier phases established (dependencies, data models, interfaces)
- **Design reference:** Path to design document for alignment checking

**Delegation template:**

Review [scope description].

**Scope:**
- IN:
  - [concrete artifact 1: file path, function name, or section heading]
  - [concrete artifact 2]
- OUT (do NOT flag these):
  - [specific future item 1 — e.g., "Phase 4 semantic propagation checklist"]
  - [specific future item 2 — e.g., "FR-17 execution feedback (deferred to wt/error-handling)"]

**Changed files:**
- [file1.md]
- [file2.md]

**Requirements:**
- [FR-N: specific requirement text or acceptance criterion]
- [FR-M: specific requirement text or acceptance criterion]

Fix all issues. Write report to: [report-path]
Return filepath or error.

**Enforcement:** If a delegation prompt has empty IN, empty OUT, or missing changed files, the orchestrator must halt and populate the fields before delegating. An incomplete execution context produces unreliable vet results — better to fail early than review against incomplete scope.

### UNFIXABLE Detection Protocol

**Rule:** After vet-fix-agent returns, mechanically check for UNFIXABLE issues before proceeding.

**Four issue statuses:**
- **FIXED** — Fix applied, issue resolved. No action needed.
- **DEFERRED** — Real issue, explicitly out of scope. Item appears in scope OUT list or design documents it as future work. Informational only — does NOT block.
- **OUT-OF-SCOPE** — Not relevant to current review. Item falls outside the review's subject matter entirely — not a known deferral, just irrelevant. Does NOT block.
- **UNFIXABLE** — Technical blocker requiring user decision. All investigation gates passed, no fix path exists. Must include subcategory code (U-REQ, U-ARCH, U-DESIGN) and investigation summary.

**Full taxonomy reference:** `agent-core/agents/vet-taxonomy.md` (subcategory codes, investigation format, examples).

**Detection steps:**
1. Read the report file returned by vet-fix-agent
2. Use Grep to search for `UNFIXABLE` in the report content
3. If found: validate each UNFIXABLE issue (see validation below)
4. If validation fails: resume vet-fix-agent for reclassification with guidance
5. If validated UNFIXABLE remains: **STOP**, report to user with report path, wait for guidance
6. If no UNFIXABLE found: proceed (DEFERRED and OUT-OF-SCOPE are non-blocking)

**UNFIXABLE validation (per issue):**
- Has subcategory code (U-REQ, U-ARCH, or U-DESIGN)
- Has investigation summary showing all 4 gates checked (scope OUT, design deferral, codebase patterns, conclusion)
- Does NOT overlap with scope OUT list (overlap → should be DEFERRED, not UNFIXABLE)
- If any check fails: resume vet-fix-agent with specific reclassification guidance (e.g., "Issue X overlaps scope OUT — reclassify as DEFERRED" or "Issue Y missing investigation summary — complete 4-gate checklist or downgrade")

**DEFERRED is not UNFIXABLE.** DEFERRED items match the execution context OUT section — they are known future work, not blockers. Do not escalate DEFERRED items.

**OUT-OF-SCOPE is not DEFERRED.** OUT-OF-SCOPE items are unrelated to the review target. DEFERRED items are related but intentionally deferred. The distinction matters: DEFERRED items track known debt, OUT-OF-SCOPE items are noise.

**Why mechanical grep, not judgment:** Weak orchestrator pattern requires mechanical checks. UNFIXABLE detection is pattern-matching (grep), not evaluation — consistent with "trust agents, escalate failures."

**Anti-pattern:** Reading vet report, seeing UNFIXABLE issues, and proceeding anyway because they "seem minor." ALL validated UNFIXABLE issues require user decision.

**Example:**
```
1. Create: agent-core/agents/test-hooks.md
2. Vet: Task(subagent_type="vet-fix-agent") with execution context
3. Read report → grep UNFIXABLE → none found (DEFERRED items present but non-blocking)
4. Result: All fixable issues resolved, proceed
```

# Review Dispatch Template

Prompt template for reviewer delegation from /inline Phase 4a. Reviewer selection happens upstream (Phase 4a routing logic) — this template structures the prompt for the selected reviewer.

## Template

Delegate to selected reviewer agent (Task tool, `subagent_type` per routing table):

```
Review implementation changes against design specification.

**Baseline:** <$BASELINE commit hash>

**Changed files:** `git diff --name-only $BASELINE`

**Requirements:**
<FR/NFR items relevant to this execution, from outline or design>

**Scope:**
- IN: <implementation targets from design>
- OUT: <explicitly excluded from design scope>

**Design reference:** plans/<job>/outline.md (or design.md if present)

**Recall context:**
1. Read agents/memory-index.md (skip if already in context). Select review-relevant triggers.
2. If plans/<job>/recall-artifact.md exists: `edify _recall resolve plans/<job>/recall-artifact.md` — artifact mode resolves all entry keys in one call.
3. Resolve additional triggers from memory-index not in artifact: `edify _recall resolve "when <trigger>" ...`
4. No relevant entries (no artifact, no triggers selected): `edify _recall resolve null` — proves gate was reached.

**Review criteria:**
- Implementation matches design decisions
- Scope completeness: every Scope IN item has a corresponding deliverable (not just components/decisions — standalone scope items too)
- Test quality (if behavioral code): behavior-focused, meaningful assertions
- Code quality: clarity, patterns, no duplication
- Integration: consistency with existing patterns

Fix all issues (critical, major, minor). Write report to: plans/<job>/reports/review.md

Return filepath on success, or "UNFIXABLE: [description]" on failure.
```

## Field Rules

- **Baseline:** `$BASELINE` captured at /inline Phase 1 (`git rev-parse HEAD` before edits). When `/inline execute` follows /design, baseline excludes design-phase artifacts — only execution edits are uncommitted.
- **Design context:** Always `outline.md` or `design.md` — never `requirements.md`. Requirements are upstream abstractions; design/outline contains the implementation-level decisions the reviewer needs.
- **Recall artifact:** Reference the file path. Reviewer resolves entries itself — do not pre-resolve and paste content into the prompt. Token economy: reference, never repeat.
- **Scope IN/OUT:** From design or outline, not invented. Prevents reviewer from flagging work explicitly deferred.
- **Scope completeness:** Reviewer must mechanically diff every Scope IN item against deliverables. Design scope items that aren't mapped to named components are the gap — component+decision validation alone misses standalone scope items (e.g., planstate specified in Scope IN but not part of any C1-C4 component).
- **Constraint:** This template is for implementation changes only. Planning artifacts (runbooks, outlines, designs) route to runbook-corrector per pipeline contracts.

## Example: Skill Creation Task

```
Review implementation changes against design specification.

**Baseline:** abc1234

**Changed files:** `git diff --name-only abc1234`

**Requirements:**
- FR-2: Pre-work context loading (task-context.sh, brief, recall)
- FR-3: Execute wrapper with delegation protocol
- FR-4: Corrector dispatch with standardized template
- FR-8: Deliverable-review chain via handoff continuation

**Scope:**
- IN: SKILL.md (~1500 words), references/review-dispatch-template.md
- OUT: /design modifications (FR-1, FR-9), /runbook modifications (FR-10), pipeline contracts, memory-index

**Design reference:** plans/inline-execute/outline.md

**Recall artifact:** plans/inline-execute/recall-artifact.md

**Review criteria:**
- Implementation matches design decisions
- Scope completeness: every Scope IN item has a corresponding deliverable
- Skill structure follows D+B convention (tool call anchors per phase)
- Continuation protocol correctly implemented
- Delegation protocol complete and accurate

Fix all issues. Write report to: plans/inline-execute/reports/review-skill.md

Return filepath on success, or "UNFIXABLE: [description]" on failure.
```

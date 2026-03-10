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

**Recall artifact:** plans/<job>/recall-artifact.md
Read this file. Batch-resolve all entries via `claudeutils _recall resolve`.
If absent: Read agents/memory-index.md, identify review-relevant entries, batch-resolve.

**Review criteria:**
- Implementation matches design decisions
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
- IN: SKILL.md (~1500 words), references/corrector-template.md
- OUT: /design modifications (FR-1, FR-9), /runbook modifications (FR-10), pipeline contracts, memory-index

**Design reference:** plans/inline-execute/outline.md

**Recall artifact:** plans/inline-execute/recall-artifact.md

**Review criteria:**
- Implementation matches design decisions
- Skill structure follows D+B convention (tool call anchors per phase)
- Continuation protocol correctly implemented
- Delegation protocol complete and accurate

Fix all issues. Write report to: plans/inline-execute/reports/review-skill.md

Return filepath on success, or "UNFIXABLE: [description]" on failure.
```

# Corrector Dispatch Template

Standard template for corrector delegation from /inline Phase 4a. Single pattern replacing 3+ ad-hoc corrector invocations across /design and /runbook.

## Template

Delegate to corrector agent (Task tool, `subagent_type: "corrector"`):

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
<resolved entries from recall-artifact.md relevant to review — failure modes, quality anti-patterns>

If no recall artifact: do lightweight recall — Read agents/memory-index.md,
identify review-relevant entries, batch-resolve via agent-core/bin/when-resolve.py.

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
- **Design context:** Always `outline.md` or `design.md` — never `requirements.md`. Requirements are upstream abstractions; design/outline contains the implementation-level decisions corrector needs.
- **Recall context:** Curate from plan recall-artifact. Include entries about review failure modes, quality anti-patterns, over-escalation patterns. Use `plans/<job>/corrector-recall-artifact.md` if prepared during Phase 3 delegation.
- **Scope IN/OUT:** From design or outline, not invented. Prevents corrector from flagging work explicitly deferred.
- **Constraint:** Corrector reviews implementation changes only. Planning artifacts (runbooks, outlines, designs) route to runbook-corrector per pipeline contracts.

## Lightweight Recall Fallback

When `plans/<job>/recall-artifact.md` is absent (e.g., cold-start task with no prior design phase):

1. Read `agents/memory-index.md`
2. Identify review-relevant entries: quality patterns, failure modes, corrector-specific decisions
3. Batch-resolve:
   ```bash
   agent-core/bin/when-resolve.py \
     "when concluding reviews" \
     "when corrector rejects planning artifacts" \
     "when recall-artifact is absent during review" \
     "when batch changes span multiple artifact types" \
     "when routing implementation findings"
   ```
4. Include resolved content in corrector prompt under **Recall context**

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

**Recall context:**
[resolved entries from corrector-recall-artifact.md — quality patterns, failure modes]

**Review criteria:**
- Implementation matches design decisions
- Skill structure follows D+B convention (tool call anchors per phase)
- Continuation protocol correctly implemented
- Delegation protocol complete and accurate

Fix all issues. Write report to: plans/inline-execute/reports/review-skill.md

Return filepath on success, or "UNFIXABLE: [description]" on failure.
```

# Vet Status Taxonomy

Reference for vet-fix-agent issue classification. Four statuses with orthogonal subcategories for UNFIXABLE.

## Status Definitions

| Status | Meaning | Blocks? | Criteria |
|--------|---------|---------|----------|
| FIXED | Fix applied | No | Edit made, issue resolved |
| DEFERRED | Real issue, explicitly out of scope | No | Item appears in scope OUT list or design documents it as future work |
| OUT-OF-SCOPE | Not relevant to current review | No | Item falls outside the review's subject matter entirely |
| UNFIXABLE | Technical blocker requiring user decision | **Yes** | All 4 investigation gates passed, no fix path exists |

**DEFERRED vs OUT-OF-SCOPE:** DEFERRED acknowledges a real issue that is intentionally deferred (referenced in scope OUT or design). OUT-OF-SCOPE means the item is unrelated to the current review target — not a known deferral, just irrelevant.

## UNFIXABLE Subcategory Codes

Every UNFIXABLE issue must include a subcategory code and an investigation summary showing all 4 gates were checked.

| Code | Category | When to use |
|------|----------|-------------|
| U-REQ | Requirements ambiguity or conflict | Requirements contradict each other, or a requirement is ambiguous enough that multiple valid interpretations exist |
| U-ARCH | Architectural constraint or design conflict | Fix would violate an architectural invariant or conflict with a documented design decision |
| U-DESIGN | Design decision needed | Multiple valid approaches exist and the choice has non-trivial downstream consequences |

### Examples

**U-REQ:**
- FR-3 requires "all errors surfaced" but FR-7 requires "silent recovery for transient failures" — contradictory error handling requirements
- Requirement says "validate input" but does not specify validation rules or error behavior

**U-ARCH:**
- Fix requires sub-agent to spawn sub-agents, but Task tool does not support nested delegation
- Correction requires hook to fire in sub-agent context, but hooks only execute in main session

**U-DESIGN:**
- Error recovery could use retry-with-backoff or circuit-breaker — both valid, different failure characteristics
- Taxonomy could be flat list or hierarchical tree — affects query patterns and extensibility differently

## Investigation Summary Format

When classifying UNFIXABLE, include the investigation summary showing gate results:

```
**Status:** UNFIXABLE (U-REQ)
**Investigation:**
1. Scope OUT: not listed
2. Design deferral: not found in design.md
3. Codebase patterns: Grep found no existing pattern for this case
4. Conclusion: [why no fix path exists]
```

## Deferred Items Report Section

Use this template when the report contains DEFERRED items:

```markdown
## Deferred Items

The following items were identified but are out of scope:
- **[Item]** — Reason: [why deferred, reference to scope OUT or design]
```

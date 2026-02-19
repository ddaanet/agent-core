## Error Handling

**Errors should never pass silently.**

- Do not swallow errors or suppress error output
- Errors provide important diagnostic information
- Report all errors explicitly to the user
- Never use error suppression patterns (e.g., `|| true`, `2>/dev/null`, ignoring exit codes)
- If a command fails, surface the failure - don't hide it

**Exception:** In bash scripts using token-efficient pattern, `|| true` is used to handle expected non-zero exits (grep no-match, diff differences). See `/token-efficient-bash` skill.

### Error Handling Framework

Error handling spans three subsystems, unified by a layered architecture:

| Layer | Name | Fragment | Purpose |
|-------|------|----------|---------|
| 0 | Prevention | `prerequisite-validation.md` | Validate preconditions before execution (~80% of errors caught) |
| 1 | Taxonomy | `error-classification.md` | 5-category classification with fault/failure vocabulary, retryable/non-retryable |
| 2 | Orchestration | `escalation-acceptance.md`, `orchestrate/SKILL.md` | Escalation criteria, rollback, timeout |
| 3 | Task lifecycle | `task-failure-lifecycle.md`, `handoff/SKILL.md` | Error states (blocked/failed/canceled), persistence |
| 4 | CPS chains | `continuation-passing.md` | Chain abort-and-record, pivot transactions, orphaned continuation recovery |

**Common patterns across all subsystems:**
- **Prevention over recovery** — Layer 0 validation is always cheaper than error handling
- **Mechanical detection** — Grep for UNFIXABLE, `git status --porcelain` for dirty tree, `just precommit` for validation
- **Clean tree as invariant** — Every step/skill must leave git tree clean before passing control
- **Classify then route** — 5-category taxonomy (Layer 1) determines escalation path in all subsystems

### Hook Error Protocol (D-6)

Hook failures are visible but non-fatal for the session:

| Failure Mode | Behavior | Rationale |
|-------------|----------|-----------|
| Hook crash (non-zero exit) | stderr output visible to agent, session continues | Degraded mode preferable to session abort |
| Hook timeout | Session proceeds without hook output | Hook is advisory, not blocking |
| Invalid output (malformed JSON) | Fallback to no-hook behavior | Partial output is worse than no output |

The CPS hook already silently catches errors — this formalizes it as intentional degraded mode. Hook errors should be logged (stderr visible) so the user can diagnose, but must not abort the session or skill chain.

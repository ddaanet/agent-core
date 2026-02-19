## Task Failure Lifecycle

Extended task state model for session.md. Complements the base notation in `execute-rule.md` with error-related states.

### State Notation

| Marker | State | Semantics |
|--------|-------|-----------|
| `[ ]` | Pending | Waiting to start |
| `[>]` | In-progress | Currently executing |
| `[x]` | Complete | Successfully finished |
| `[!]` | Blocked | Waiting on external signal to unblock |
| `[✗]` | Failed | System-detected terminal failure |
| `[–]` | Canceled | User-initiated abort |

**Grounding:** State model adapted from Temporal WorkflowExecutionStatus (Running, Completed, Failed, Canceled, TimedOut). Blocked maps to Temporal's "waiting on signal" concept.

### State Transitions

```
pending → in-progress → complete
                      → blocked → pending (when unblocked)
                      → failed  (terminal — requires user decision)
                      → canceled (terminal — user-initiated)
```

- **Blocked → Pending:** When the blocking condition resolves, task returns to pending for re-execution. Record what unblocked it.
- **Failed is terminal:** Requires explicit user decision to retry (re-mark as pending) or abandon (delete task). System does not auto-retry.
- **Canceled is distinct from failed:** Canceled = user chose to stop. Failed = system detected unrecoverable error. The distinction matters for understanding why work stopped.

### Error Context Recording

When a task transitions to blocked or failed, record the error inline:

```markdown
- [!] **Task Name** — description | model
  - Blocked: [reason] — [what needs to happen to unblock]
  - Error category: [from error-classification.md taxonomy]

- [✗] **Task Name** — description | model
  - Failed: [error summary]
  - Error category: [category] | Retryable: [yes/no]
  - Report: [path to diagnostic report if available]
```

### Persistence Rules

- Failed and canceled tasks persist until user explicitly resolves them (retry, abandon, or delete)
- They are NOT trimmed during handoff — trimming would lose the signal that something needs attention
- Blocked tasks persist until unblocking condition is met, then transition back to pending
- Handoff preserves error context verbatim (reason, category, report path)

### Integration

- **Handoff skill:** Recognizes all six states, preserves error context during carry-forward
- **Execute rule:** `#execute` skips blocked/failed/canceled tasks, picks first pending
- **CPS chains:** Chain failure records task as blocked with continuation context for manual resume via `r`
- **Orchestration:** Step failure can trigger task state change (blocked if retryable, failed if non-retryable)

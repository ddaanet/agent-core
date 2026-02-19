# Continuation Passing Protocol

Skills chain through continuation passing — a hook-based system that replaces hardcoded tail-calls with composable chains.

## How It Works

```
User: "/design plans/foo, /runbook and /orchestrate"
  → Hook parses multi-skill input, injects continuation via additionalContext
  → /design executes, peels /runbook, tail-calls with remainder
  → /runbook executes, peels /orchestrate, tail-calls with remainder
  → /orchestrate executes, no continuation → uses own default-exit
```

**Single skills** pass through unchanged — the hook only activates for multi-skill chains. Skills manage their own default-exit behavior when standalone.

## Frontmatter Schema

Cooperative skills declare continuation support in YAML frontmatter. "Cooperative" means the skill implements the consumption protocol (reads continuation, peels first entry, tail-calls remainder).

```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

- `cooperative: true` — Skill understands continuation protocol
- `default-exit` — Tail-call chain used when standalone or last in continuation chain. Empty `[]` for terminal skills.

## Consumption Protocol

Add to cooperative skills (~5-8 lines replacing hardcoded tail-calls):

```markdown
## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain)
   or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If continuation present: peel first entry, tail-call with remainder
3. If no continuation: skill implements its own default-exit behavior (standalone/last-in-chain)

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts.
```

## Transport Format

**First invocation** (hook → skill): JSON `additionalContext` with `[CONTINUATION-PASSING]` marker.

**Subsequent invocations** (skill → skill): Suffix in Skill args parameter:
```
[CONTINUATION: /runbook, /orchestrate, /handoff --commit, /commit]
```

Bracket-delimited, comma-separated entries. Each entry: `/skill optional-args`.

## Sub-Agent Isolation

Continuation metadata must never reach sub-agents:
- Do NOT include `[CONTINUATION: ...]` in Task tool prompts
- Continuation lives in main conversation context only
- Skills construct Task prompts explicitly — no accidental inclusion path

## Cooperative Skills

| Skill | Default Exit | Notes |
|-------|-------------|-------|
| `/design` | `["/handoff --commit", "/commit"]` | Planning entry point |
| `/runbook` | `["/handoff --commit", "/commit"]` | Runbook planning (unified) |
| `/orchestrate` | `["/handoff --commit", "/commit"]` | Runbook execution |
| `/handoff` | `["/commit"]` | Context preservation |
| `/commit` | `[]` | Terminal skill |

**Note**: Default Exit column documents each skill's standalone behavior (implemented by skill, not enforced by hook).

## Error Propagation

Five cooperative skills chain via tail-calls with zero implicit error handling. A failure mid-chain orphans the remaining continuation.

### Default Behavior: Abort and Record

When a skill fails during a CPS chain (D-1):
1. **Abort remaining continuation** — do not invoke the next skill in the chain
2. **Record in session.md Blockers section** — include: which skill failed, error category (from `error-classification.md`), retryable/non-retryable classification, and the remaining continuation that was orphaned
3. **Update task state** — mark the task as `[!]` blocked (see `task-failure-lifecycle.md`)
4. **Manual resume via `r`** — user reviews blocker, resolves, and resumes from recorded context

**No automatic retry.** 0 retries by default. Add targeted retry for specific failure types only if they prove common in practice. The retryable/non-retryable classification informs the recorded error context (helping the user decide how to resume), not the immediate response.

**Recovery operations must be idempotent** — a resumed skill may re-execute work that partially completed before failure. Skills should tolerate re-application (e.g., Edit that matches current content, Write that overwrites).

### Pivot Transactions

Points of no return in the chain where compensation is impractical (Saga pattern concept):

| Chain Position | Pivot? | Reason |
|---------------|--------|--------|
| `/design` completes | No | Outline/design is additive, can be revised |
| `/runbook` completes | No | Runbook artifacts can be regenerated |
| `/orchestrate` completes execution | **Yes** | Multiple commits, file changes, reports — compensating transactions impractical |
| `/handoff` completes | **Yes** | Session state updated, learnings written — reversion loses institutional knowledge |
| `/commit` completes | **Yes** | Git history modified, push may have occurred |

After a pivot transaction, the chain records the point-of-no-return. Recovery proceeds forward (fix and continue) rather than backward (undo and retry).

### Orphaned Continuation Recovery

When a chain aborts, the remaining continuation is recorded in session.md:

```markdown
## Blockers / Gotchas

**Orphaned CPS continuation:**
- Chain: `/design → /runbook → /orchestrate → /handoff --commit → /commit`
- Failed at: `/orchestrate` (EXECUTION_ERROR, retryable: timeout)
- Remaining: `/handoff --commit → /commit`
- Resume: Fix orchestration issue, then `r` to resume from `/orchestrate`
```

The `r` command picks up the full chain context including remaining continuation.

### Skill-Level Error Handling

Each cooperative skill should handle errors by:
- Catching failures from its own operations (Task tool errors, Read/Write failures)
- Classifying per `error-classification.md` taxonomy (5 categories, retryable/non-retryable)
- If the error is within the skill's scope to fix: fix and continue
- If not: abort, record in session.md Blockers, do NOT invoke continuation tail-call

**Anti-pattern:** Skill catches error, records it, then proceeds to invoke next skill in chain. The chain must stop at the failure point.

## Adding Continuation to a New Skill

1. Add `continuation:` block to YAML frontmatter
2. Add `Skill` to `allowed-tools` if not present (needed for tail-call)
3. Replace hardcoded tail-call with consumption protocol section
4. Ensure Task tool prompts exclude continuation metadata
5. Add error handling: on failure, abort continuation and record in session.md Blockers

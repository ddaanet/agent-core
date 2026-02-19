## Escalation Acceptance Criteria

When an error is escalated and a fix is attempted (by Sonnet diagnostic, refactor agent, or manual intervention), all three criteria must pass before the step is considered resolved:

**Required (all three):**
- `just precommit` passes — mechanical validation (lint, format, type checks)
- Git tree clean — no uncommitted changes (`git status --porcelain` returns empty)
- Output validates against step acceptance criteria — the step's stated objective is met

**Verification sequence:**

```
1. Apply fix
2. Run `just precommit`
   - If fails: fix issues, re-run (loop until pass or give up)
3. Check `git status --porcelain`
   - If dirty: commit fix, verify clean
4. Validate step output against acceptance criteria from step file
   - If criteria undefined: escalate as ambiguity error
5. All three pass → step resolved, resume execution
   Any fails after reasonable attempts → escalate to next level
```

**Rollback protocol (D-5):**

When escalation fails partway through a step — the fix attempt itself causes new issues or acceptance criteria cannot be met:

- Revert to the last clean commit before the failed step: `git revert HEAD` (if fix was committed) or `git checkout -- .` (if uncommitted)
- This is a simplification of the Saga compensating transaction pattern, enabled by git's atomic snapshot model: reverting a commit restores state (no concurrent modifications within single orchestration)
- **Assumption:** All relevant state is git-managed. If non-git state is involved (external service calls, session.md edits outside repo), the simple revert model breaks — escalate to user.
- After rollback, re-execute the step from clean state or escalate to user

**Dirty tree recovery:**

When a step leaves the tree dirty (uncommitted changes detected by post-step verification):
- Do NOT proceed regardless of whether changes look expected
- Do NOT clean up on behalf of the step
- Revert to last clean commit: `git checkout -- . && git clean -fd`
- Report the dirty tree and escalate

**Timeout handling:**

Two independent guards for two independent failure modes:

| Failure Mode | Guard | Threshold | Basis |
|-------------|-------|-----------|-------|
| Spinning (high activity, no convergence) | `max_turns` on Task tool | ~150 | Clean data: p90=40, p95=52, p99=73, max=129 |
| Hanging (no activity, wall-clock grows) | Duration timeout | ~600s | Clean data: p90=225s, p95=301s, p99=485s, max=855s |

- `max_turns` is actionable now — parameter already exists on Task tool
- Duration timeout requires Claude Code infrastructure support (deferred)
- A single blanket `max_turns` suffices across agent types — the spinning failure mode is type-independent
- Per-type refinement deferred until false positives observed
- Calibrated from 938 clean observations with sleep-inflated outliers filtered (>30s/tool flagged as laptop-suspend artifacts)

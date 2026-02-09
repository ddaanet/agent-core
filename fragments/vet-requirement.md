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
2. Delegate to `vet-fix-agent`: review, apply ALL fixes, write report
3. Read report, check for UNFIXABLE issues
4. Escalate UNFIXABLE issues to user

**No importance filtering.** The vet-fix-agent applies all fixes (critical, major, minor). The caller does not triage or defer fixes.

**Why:** Early review catches issues before they propagate. Applying all fixes eliminates drift from deferred minor issues accumulating across sessions.

**Example:**
```
1. Create: agent-core/agents/test-hooks.md
2. Vet: Task(subagent_type="vet-fix-agent") → reviews, fixes ALL issues, writes report
3. Read report, check for UNFIXABLE issues
4. Result: All fixable issues resolved
```

## Vet Requirement

**Rule:** After creating any production artifact, delegate to vet agent for review.

**Two vet agents — choose by caller context:**
- `vet-agent` — review only. Use when caller has context to apply fixes (Tier 1/2, direct work)
- `vet-fix-agent` — review + apply critical/major fixes. Use in orchestration where no other agent has context (Tier 3)

**Production artifacts requiring vet:**
- Plans (runbooks)
- Code (implementations, scripts)
- Tests
- Agent procedures
- Skill definitions
- Documentation that defines behavior or contracts

**Design documents:** Reviewed by opus.

**Artifacts NOT requiring vet:**
- Execution reports
- Diagnostic outputs
- Log files
- Temporary analysis
- Session handoffs (already reviewed during /handoff)

**Vet process (Tier 1/2 — caller has context):**
1. Create artifact
2. Delegate to `vet-agent`: review, write report to file
3. Read report, apply critical/major fixes with full context
4. Document minor issues for later if appropriate

**Vet process (Tier 3 — orchestration):**
1. Create artifact
2. Delegate to `vet-fix-agent`: review, apply critical/major fixes, write report
3. Read report, check for UNFIXABLE issues
4. Escalate UNFIXABLE critical/major issues to user

**Why:** Early review catches issues before they propagate. Sonnet provides objective analysis without author bias. Agent selection ensures fixes happen where context exists.

**Example:**
```
# Tier 1/2: After writing test procedure (caller has context)
1. Create: agent-core/agents/test-hooks.md
2. Vet: Task(subagent_type="vet-agent") → writes report
3. Read report, apply critical/major fixes directly
4. Result: Higher quality artifact

# Tier 3: During orchestration (orchestrator has no context)
1. Step agent creates implementation
2. Checkpoint: Task(subagent_type="vet-fix-agent") → reviews AND fixes
3. Orchestrator reads report, checks for UNFIXABLE issues
4. Result: Fixes applied by agent with context
```

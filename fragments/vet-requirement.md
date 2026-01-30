## Vet Requirement

**Rule:** After creating any production artifact, delegate to sonnet subagent for vet review, then apply fixes.

**Production artifacts requiring sonnet vet:**
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

**Vet process:**
1. Create artifact
2. Delegate to sonnet subagent: "Vet [artifact]" with specific review criteria
3. Review feedback
4. Apply high-priority fixes immediately
5. Document medium/low-priority issues for later if appropriate

**Why:** Early review catches issues before they propagate. Sonnet provides objective analysis without author bias.

**Example:**
```
# After writing test procedure
1. Create: agent-core/agents/test-hooks.md
2. Vet: Task tool → sonnet subagent → review for completeness, correctness, clarity
3. Fix: Apply high-priority feedback
4. Result: Higher quality artifact, fewer regressions
```

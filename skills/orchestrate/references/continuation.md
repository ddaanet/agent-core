# Continuation Protocol

This skill is **cooperative** with the continuation passing system.

## Consumption

After completing the orchestration, check the Skill args suffix for `[CONTINUATION: ...]` transport.

IF continuation present:
1. Parse the `[CONTINUATION: ...]` structured list
2. Peel first entry: `(/skill args)` or `/skill` (if no args)
3. Strip continuation from current context (delete `[CONTINUATION: ...]` suffix)
4. Invoke next skill: `Skill(/skill args="args [CONTINUATION: remainder]")` where remainder = remaining entries (if any)

IF no continuation present:
- Use default-exit from frontmatter: `/handoff --commit` then `/commit`
- Invoke first entry, pass remainder as continuation to that skill

## Examples

Incoming: `/orchestrate myplan [CONTINUATION: /commit]`
- Complete orchestration
- Strip continuation from current context
- Peel first entry: `/commit`
- No remainder, so invoke: `Skill(/commit)`

Incoming: `/orchestrate myplan [CONTINUATION: /handoff --commit, /commit]`
- Complete orchestration
- Strip continuation from current context
- Peel first: `/handoff --commit`
- Remainder: `/commit`
- Invoke: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`

Incoming: `/orchestrate myplan` (no continuation)
- Complete orchestration
- Use default-exit: `["/handoff --commit", "/commit"]`
- Invoke: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`

## Constraint

This skill does NOT pass continuations to sub-agents (Task tool). Continuations apply only to the main session skill chain.

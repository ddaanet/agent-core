# Continuation Protocol

This skill is **cooperative** with the continuation passing system.

## Consumption

After completing the orchestration, check the Skill args suffix for `[CONTINUATION: ...]` transport.

IF continuation present:
1. Parse the `[CONTINUATION: ...]` structured list
2. If skill needs a subroutine before continuing: prepend entries to the list (existing entries stay in original order — append-only invariant)
3. Peel first entry from (possibly modified) list: `(/skill args)` or `/skill` (if no args)
4. Strip continuation from current context (delete `[CONTINUATION: ...]` suffix)
5. Invoke next skill: `Skill(/skill args="args [CONTINUATION: remainder]")` where remainder = remaining entries (if any)

IF no continuation present:
- Use default-exit from frontmatter: `/handoff` then `/commit`
- Invoke first entry, pass remainder as continuation to that skill

## Examples

Incoming: `/orchestrate myplan [CONTINUATION: /commit]`
- Complete orchestration
- Strip continuation from current context
- Peel first entry: `/commit`
- No remainder, so invoke: `Skill(/commit)`

Incoming: `/orchestrate myplan [CONTINUATION: /handoff, /commit]`
- Complete orchestration
- Strip continuation from current context
- Peel first: `/handoff`
- Remainder: `/commit`
- Invoke: `Skill(/handoff args="[CONTINUATION: /commit]")`

Incoming: `/orchestrate myplan` (no continuation)
- Complete orchestration
- Use default-exit: `["/handoff", "/commit"]`
- Invoke: `Skill(/handoff args="[CONTINUATION: /commit]")`

### Prepend (subroutine call)

Incoming: `/orchestrate myplan [CONTINUATION: /handoff, /commit]`
- Complete orchestration
- Need `/commit` checkpoint before chain resumes
- Prepend: `[/commit, /handoff, /commit]`
- Peel first: `/commit`
- Remainder: `/handoff, /commit`
- Invoke: `Skill(/commit args="[CONTINUATION: /handoff, /commit]")`
- After `/commit` completes, original chain resumes: `/handoff` → `/commit`

## Constraint

This skill does NOT pass continuations to sub-agents (Task tool). Continuations apply only to the main session skill chain.

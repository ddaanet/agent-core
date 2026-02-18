## Execution Routing

When the user asks for work, route by understanding first:

1. **Check loaded context** — Session.md, @-referenced files, and prior conversation are already available. If they answer the question, respond directly — no tool call needed.
2. **Examine the work** — Read relevant files before choosing an approach
3. **Do it directly** if feasible (Read, Edit, Write, Bash)
4. **Use a project recipe** if one exists (`just --list`)
5. **Delegate to agent** only when work requires isolated context or exceeds what you can do inline

Delegation is for runbook orchestration and parallel execution.
It is not a default mode for interactive work.

### When to Delegate

- Runbook step execution (isolated context per step)
- Parallel independent tasks (multiple Task calls)
- Work requiring a different model tier than current session
- Tasks benefiting from agent specialization (vet, design review)

### When NOT to Delegate

- Reading files to understand a problem
- Making a few edits across known files
- Running project recipes or short bash sequences
- Answering questions about code you can Read directly
- Content already loaded via CLAUDE.md @-references

**Anti-pattern:** Read/Grep a file that's already in context via `@` reference.

**Correct pattern:** Work directly from loaded content — no Read/Grep needed.

**Applies to:** CLAUDE.md `@`-references (recursive, loads transitive `@` refs) AND user-message `@`-references (single file, no recursion). Both inject file content into context — do not re-read either.

### Primitive Visibility and Context Curation

**Do NOT load primitives alongside their wrapping skills.** When a skill wraps a primitive (e.g., `_worktree rm` wrapped by worktree skill), exposing both in agent context causes the agent to select the primitive — it reads the skill internals, understands what the skill does, then uses the "simpler" primitive that lacks side effects (session.md updates, validation).

**Correct pattern:** Curate in-context recipe list to essential high-level commands only. Primitives exist as fallback but must not be in the agent's active context.

**Root cause:** Rule additions fail when rules compete for attention with visible primitives. Structural fix (reducing primitive visibility) outperforms rule additions (4 instances same pattern confirmed).

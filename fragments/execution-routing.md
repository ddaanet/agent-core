## Execution Routing

When the user asks for work, route by understanding first:

1. **Examine the work** — Read relevant files before choosing an approach
2. **Do it directly** if feasible (Read, Edit, Write, Bash)
3. **Use a project recipe** if one exists (`just --list`)
4. **Delegate to agent** only when work requires isolated context or exceeds what you can do inline

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

# Bash Scripting Pattern

**Rule:** For sequential bash commands (3+ steps), use token-efficient bash pattern.

## The Pattern

Use the **`/token-efficient-bash`** skill for:
- Scripts with 3+ sequential commands
- Multi-step operations requiring error handling
- Situations where you'd otherwise write echo/error statements

**Core pattern:**
```bash
exec 2>&1
set -xeuo pipefail

# Commands here
```

**Key benefits:**
- Automatic command tracing (eliminates echo statements)
- Fail-fast error handling
- 40-60% token reduction
- Unified diagnostic output

## When to Load the Skill

Invoke `/token-efficient-bash` when:
- Writing multi-step bash scripts
- User asks about "bash patterns", "set -x", "error handling"
- Implementing Execution Routing (CLAUDE.md) with sequential operations
- Need to reduce bash output tokens

## Reconciliation with Error Handling

CLAUDE.md Error Handling forbids `|| true`, but `/token-efficient-bash` pattern requires it for commands with expected non-zero exits (grep, diff, arithmetic).

**Clarification:** The pattern uses `|| true` to *handle* expected exits, not *suppress* errors. Unexpected failures still cause immediate termination with diagnostics.

The `/token-efficient-bash` skill provides:
- Complete pattern explanation
- Strict mode caveats (`|| true` usage, arithmetic pitfalls)
- Token economy analysis
- Working examples
- Anti-patterns to avoid

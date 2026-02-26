---
name: error-handling
description: |
  Bash error handling rules and token-efficient exception patterns. Loaded when agents need error handling guidance for bash command execution.
user-invocable: false
---

# Apply Bash Error Handling Rules

Content is in the always-loaded fragment: `agent-core/fragments/error-handling.md`

This skill exists for discovery only. The fragment loads at session start and contains all error handling rules including the `|| true` exception for token-efficient bash.

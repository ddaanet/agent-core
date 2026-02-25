---
name: error-handling
description: |
  This skill should be used when agents need error handling rules for bash command execution or token-efficient bash exception patterns.
user-invocable: false
---

# Error Handling

Content is in the always-loaded fragment: `agent-core/fragments/error-handling.md`

This skill exists for discovery only. The fragment loads at session start and contains all error handling rules including the `|| true` exception for token-efficient bash.

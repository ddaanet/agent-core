---
name: error-handling
description: |
  This skill should be used when agents execute bash commands and need error handling rules. Prevents silent failures, inappropriate error suppression, and documents the || true exception for token-efficient bash scripts.
user-invocable: false
---

# Error Handling

Error handling rules for agents executing bash commands. Prevents silent failures and inappropriate error suppression.

**Errors should never pass silently.**

- Do not swallow errors or suppress error output
- Errors provide important diagnostic information
- Report all errors explicitly to the user
- Never use error suppression patterns (e.g., `|| true`, `2>/dev/null`, ignoring exit codes)
- If a command fails, surface the failure - don't hide it

**Exception:** In bash scripts using token-efficient pattern, `|| true` is used to handle expected non-zero exits (grep no-match, diff differences). See `/token-efficient-bash` skill.

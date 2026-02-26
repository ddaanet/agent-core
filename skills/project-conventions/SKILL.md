---
name: project-conventions
description: |
  Project prose and output conventions for sub-agents. Injected via skills: frontmatter — not user-invocable.
  Bundles deslop (prose quality), token economy, and tmp-directory rules.
user-invocable: false
---

# Apply Project Code and Output Conventions

## Code Quality

Prose quality rules have moved to ambient context (communication.md). For code:

- Docstrings only for non-obvious behavior
- Comments explain *why*, never *what*
- No section banners — let structure communicate grouping
- Abstractions only when a second use exists
- Guard only at trust boundaries
- Expose fields directly until access control needed
- Build for current requirements, extend when needed

## Token Economy

- Give file references (path:line), never repeat file contents
- Use bullets unless ordering matters (numbered lists cause renumbering churn)
- Direct, clear communication without verbosity

## Temporary Files

All temporary files go in `<project-root>/tmp/`, never `/tmp/` or `/tmp/claude/`.
For runbook execution, use `plans/*/reports/`. For ad-hoc work, use project-local `tmp/`.

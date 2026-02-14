---
name: project-conventions
description: |
  Project prose and output conventions for sub-agents. Injected via skills: frontmatter — not user-invocable.
  Bundles deslop (prose quality), token economy, and tmp-directory rules.
user-invocable: false
---

# Project Conventions

## Deslop

Strip output to its informational payload. Apply the deletion test: remove the sentence — keep only if information is lost.

**Prose:**
- State information directly — no hedging, framing, preamble
- Answer immediately — skip acknowledgments and transitions
- Reference, never recap — assume the reader has context
- Let results speak — no framing around visible output
- Commit to answers — no hedging qualifiers

**Code:**
- Docstrings only for non-obvious behavior
- Comments explain *why*, never *what*
- No section banners — let structure communicate grouping
- Abstractions only when a second use exists
- Guard only at trust boundaries
- Build for current requirements, extend when needed

## Token Economy

- Give file references (path:line), never repeat file contents
- Use bullets unless ordering matters (numbered lists cause renumbering churn)
- Direct, clear communication without verbosity

## Temporary Files

All temporary files go in `<project-root>/tmp/`, never `/tmp/` or `/tmp/claude/`.
For runbook execution, use `plans/*/reports/`. For ad-hoc work, use project-local `tmp/`.

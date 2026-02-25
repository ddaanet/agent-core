---
name: how
description: This skill should be used when the agent needs procedural knowledge recall — "how to do X", step-by-step techniques, or implementation guidance from project decisions. Invoke with "/how <trigger>".
allowed-tools: Bash(agent-core/bin/when-resolve.py:*)
user-invocable: true
---

# /how — Procedural Knowledge Recall

Resolve procedural triggers against the memory index. Returns decision file content with ancestor and sibling navigation links.

## Resolution Modes

**Trigger mode** — fuzzy-match an index entry to a decision heading:

```bash
agent-core/bin/when-resolve.py "how encode paths"
```

**Section mode** — look up a heading directly by name (dot prefix):

```bash
agent-core/bin/when-resolve.py "how .Path Encoding Algorithm"
```

**File mode** — load an entire decision file (double-dot prefix, relative to `agents/decisions/`):

```bash
agent-core/bin/when-resolve.py "how ..data-processing.md"
```

## When to Use

- Need to know *how* to accomplish a specific task or technique
- Looking up a step-by-step procedure documented in project decisions
- Need implementation guidance — how to encode paths, how to structure tests, how to configure tools

## When NOT to Use

- Need behavioral/situational knowledge — use `/when` instead
- Content already in context from a prior `/recall`, `/when`, or `/how` invocation (do not re-resolve)
- Exploring unfamiliar code (use Grep/Read directly)

## Output Format

Returns the matched section content followed by navigation:

- **Broader:** ancestor headings and `..file.md` link for surrounding context
- **Related:** sibling `/how` entries under the same parent heading

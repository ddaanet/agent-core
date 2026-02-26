---
name: when
description: Recall behavioral knowledge from project decisions. Triggers on "when to do X", situational patterns, or decision content for recognized situations. Invoke with "/when <trigger>".
allowed-tools: Bash(agent-core/bin/when-resolve.py:*)
user-invocable: true
---

# /when — Behavioral Knowledge Recall

Resolve behavioral triggers against the memory index. Returns decision file content with ancestor and sibling navigation links.

## Resolution Modes

**Trigger mode** — fuzzy-match an index entry to a decision heading:

```bash
agent-core/bin/when-resolve.py "when writing mock tests"
```

**Section mode** — look up a heading directly by name (dot prefix):

```bash
agent-core/bin/when-resolve.py "when .Mock Patching"
```

**File mode** — load an entire decision file (double-dot prefix, relative to `agents/decisions/`):

```bash
agent-core/bin/when-resolve.py "when ..testing.md"
```

## When to Use

- Facing a decision about *when* to apply a pattern, rule, or convention
- Recognizing a situation that may have documented behavioral guidance
- Need context before implementing — when to mock, when to delegate, when to stop, when to escalate

## When NOT to Use

- Need procedural/how-to knowledge — use `/how` instead
- Content already in context from a prior `/recall`, `/when`, or `/how` invocation (do not re-resolve)
- Exploring unfamiliar code (use Grep/Read directly)

## Output Format

Returns the matched section content followed by navigation:

- **Broader:** ancestor headings and `..file.md` link for surrounding context
- **Related:** sibling `/when` entries under the same parent heading

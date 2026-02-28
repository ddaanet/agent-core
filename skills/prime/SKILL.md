---
name: prime
description: |
  Load plan artifacts and recall for ad-hoc plan work outside workflow skills. Triggers on "/prime", "load plan context", "prime the plan", or when working on plan artifacts without a workflow skill (design, runbook, orchestrate). Reads existing plan files, then chain-calls /recall.
allowed-tools: Read, Glob, Skill
user-invocable: true
---

# /prime — Ad-hoc Plan Context Loading

Load plan artifacts into conversation context for work that bypasses workflow skills. Workflow skills (design, runbook, orchestrate) have built-in discovery gates. This skill covers the gap: fixing a blocker, revising an outline, patching a runbook-outline, debugging plan infrastructure.

## Invocation

```
/prime plans/<name>/
```

Argument: path to a plan directory.

## Process

### Step 1: Load Plan Artifacts

Glob the plan directory for markdown files, then Read each existing artifact:

```
Glob: plans/<name>/*.md
```

Read files in this priority order (skip any that don't exist):
- `requirements.md`
- `outline.md`
- `design.md`
- `runbook-outline.md`
- Any other `.md` files found by Glob (excluding `recall-artifact.md` — consumed by /recall, not displayed)

### Step 2: Chain-call /recall

```
Skill(skill: "recall")
```

No explicit topic. Plan content now in conversation gives `/recall` rich signal for entry selection. `/recall`'s cumulative tracking preserved — later invocations skip already-loaded entries.

## What This Is Not

- Not workflow optimization — workflow skills keep their discovery gates unchanged
- Not @ref injection — content enters via Read calls (no system-prompt duplication)
- Not a replacement for `/design`, `/runbook`, or `/orchestrate`

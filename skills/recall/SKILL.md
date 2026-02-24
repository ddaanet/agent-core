---
name: recall
description: |
  This skill should be used when the user asks to "recall", "load context", "recall pass", "load decisions", "what do I need to know", or when starting work on a topic that likely has relevant project decisions. Front-loads relevant decision file content into the session context. Cumulative — multiple invocations build up context as topics shift. Tail-recursive — saturates within a single invocation.
allowed-tools: Bash(agent-core/bin/when-resolve.py:*)
user-invocable: true
---

# /recall — Interactive Recall Pass

Load relevant project decisions and learnings into session context before working. The interactive equivalent of the pipeline's recall passes (design A.1, runbook Phase 0.5).

## Why This Exists

Agents self-retrieve at ~3% rate. The pipeline injects recall at fixed points, but interactive sessions bypass it. This skill fills the gap: front-load relevant decisions so they're available without the agent needing to "decide to recall."

## Invocation

```
/recall                     # Topic-based: select section entries relevant to current discussion
/recall <topic>             # Explicit topic: "recall error handling"
/recall deep                # Saturate: tail-recurse aggressively, full 4-pass depth
/recall broad               # Whole files: load entire decision files, not individual sections
/recall all                 # Deep + broad: maximum effort within topic scope
/recall everything          # Full corpus: load all entries (expensive, rare)
```

## Process

### Pass 1: Scan and Select

1. **Identify the active topic** from conversation context (or explicit argument)
2. **Read memory-index.md** (skip if already in context). Review entries for domain matches.
3. **Select targets** based on mode:
   - Default/deep: select relevant entry triggers (section-level)
   - Broad/all: select relevant `## agents/decisions/<file>.md` headers (file-level)
4. **Skip already-loaded content** — if a section or file is already in context from a prior `/recall`, `/when`, or `/how` invocation, do not reload it.

### Pass 2: Resolve and Load

Resolution method depends on mode:

**Section-level (default, deep):** Batch-resolve via `when-resolve.py`:

```bash
agent-core/bin/when-resolve.py "when <trigger>" "how <trigger>" ...
```

**File-level (broad, all):** Read decision files directly using the Read tool:

```
Read agents/decisions/testing.md
Read agents/decisions/implementation-notes.md
```

Batch multiple Read calls in a single message. Line limits are enforced by precommit — no cap logic needed at read time.

### Pass 3: Tail-Recurse or Exit

After loading, re-check memory-index (already in context from Pass 1) for targets that became relevant due to newly loaded context (e.g., a decision file references another pattern).

- **New targets found** → go to Pass 2 with the new targets
- **No new targets** → stop (saturation reached)

**Depth by mode:**
- Default: 1 pass (select all relevant entries from index in a single batch). Pass 2 only if loaded *content* reveals entries not identifiable from index headings alone
- Deep/all: up to 4 passes (aggressive re-scan, include tangential entries)
- Broad: 1 pass (whole files already capture internal connections)
- Everything: no recursion (full corpus loaded in one pass)

### Output

After completion, summarize what was loaded:

```
Recalled N entries from M decision files:
- <Entry Name> (source: decisions/<file>.md)
- <Entry Name> (source: decisions/<file>.md)
- ...
```

If tail-recursion added entries beyond the initial selection, note which pass found them.

## Cumulative Behavior

Each `/recall` invocation builds on prior ones within the session:

- Check which entries are already in context (by their heading + source path visible in prior conversation)
- On re-invocation, skip already-loaded entries
- New topic → new relevant entries selected → loaded on top of existing context
- The conversation window IS the accumulation mechanism (skill continuation)

## Modes

**`/recall` (default):** Select section-level entries relevant to current discussion topic. Single pass typical — tail-recurse only if loaded content reveals clearly relevant entries not yet loaded.

**`/recall <topic>`:** Override topic detection. Select entries matching the explicit topic instead of inferring from conversation.

**`/recall deep`:** Aggressive saturation. Tail-recurse through the full 4-pass depth, including tangentially related entries on each re-scan. Use when the topic has deep dependency chains across decision files.

**`/recall broad`:** Whole-file loading. Instead of resolving individual section entries, identify relevant decision files from memory-index's `## agents/decisions/<file>.md` headers and Read each file directly. Skip files already Read whole in a prior `/recall broad` or `/recall all` — check the output summary from prior invocations. Prior section-level loads do not count as "already loaded" (whole-file read captures content beyond the loaded sections, justifying the re-read cost). Use when the topic spans many entries within the same files — reading the whole file captures connective tissue between entries that section-level loading misses.

**`/recall all`:** Deep + broad combined. Maximum effort within topic scope. Identify relevant files, load them whole, then tail-recurse to discover and load additional files revealed by the content. The "give me everything on this topic" mode.

**`/recall everything`:** Full corpus dump. Bypass topic selection entirely — load every decision file in memory-index. Expensive (fills context). Use only when the task touches many domains or when genuinely unsure what's relevant. Not tail-recursive (nothing to discover — everything is loaded).

## Relationship to /when and /how

| Skill | Scope | Trigger |
|-------|-------|---------|
| `/when` | Single entry by trigger | Agent recognizes a specific situation |
| `/how` | Single entry by trigger | Agent needs a specific procedure |
| `/recall` | Multiple entries by topic | Front-load before work begins |

`/recall` uses the same resolution infrastructure (`when-resolve.py`) but selects multiple entries by topic relevance rather than resolving a single known trigger. It is the batch, proactive counterpart to `/when` and `/how`'s individual, reactive lookups.

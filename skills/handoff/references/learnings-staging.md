# Learnings Staging Protocol

Process learnings from session.md to staging area using add-learning.py script.

## When to Stage Learnings

If the session has learnings in the "Recent Learnings" section, stage them during handoff.

## Staging Procedure

**For each learning:**

1. **Extract title and content** (anti-pattern, correct pattern, rationale)
2. **Generate slug** from title (lowercase, hyphenated)
3. **Call script**: `python3 agent-core/bin/add-learning.py "slug" "content"`
4. **Script creates** `agents/learnings/{date}-{slug}.md` and updates `pending.md`

## Update session.md

After staging all learnings:

- Replace "Recent Learnings" section with reference: `@agents/learnings/pending.md`
- This enables @ chain expansion: session.md → pending.md → individual learning files

## Learning Content Format

```markdown
**[Title]:**
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]
```

## Example

```bash
python3 agent-core/bin/add-learning.py "tool-batching" "**Tool batching:**
- Anti-pattern: Sequential tool calls when operations are independent
- Correct pattern: Batch independent operations in single message
- Rationale: Reduces latency and improves efficiency"
```

## Line Count

Follow @ chain for size check: session.md + pending.md + learnings/*.md

The @ reference keeps session.md lean while preserving all learning content.

# Remember Skill Usage Patterns

Common patterns for using the remember skill to capture learnings and update documentation.

## Pattern: Error Handling After Failure

**When**: A failure revealed missing constraint or rule

**Steps**:
1. Read the relevant section of CLAUDE.md or related doc
2. Add constraint with concrete example
3. Commit with failure context in message

**Example**:
```
User encountered sandbox violation trying to write to /tmp/file.txt.
Read File System Rules section.
Add constraint: "Use project-local tmp/ directory, NOT /tmp/"
Commit: "Add file system rule: Use project tmp/ not system /tmp

- Sandbox blocks writes to /tmp/
- Project-local tmp/ directory is whitelisted
- Context: Prevented sandbox violation in [task]"
```

## Pattern: Workflow Improvement

**When**: Process improvement or optimization discovered

**Steps**:
1. Read the relevant workflow section
2. Add or update description
3. Include before/after if major change
4. Update session.md if affects current work

**Example**:
```
Discovered tool batching improves efficiency.
Read Tool Usage section.
Add: "Batch independent tool calls in single message"
Update session.md: Note batching pattern for current task
Commit: "Add tool batching guidance"
```

## Pattern: Design Decision

**When**: Architectural or design choice made that affects future work

**Steps**:
1. Check if agents/decisions/ directory exists with appropriate file for this decision
2. Add: problem, options considered, choice made, rationale
3. Reference from CLAUDE.md if decision creates rules

**Example**:
```
Decided to use weak orchestrator pattern for runbook execution.
Create or update agents/decisions/*.md as appropriate.
Add section: Weak Orchestrator Pattern
  - Problem: Complex runbooks need structured execution
  - Options: Direct, strong orchestrator, weak orchestrator
  - Choice: Weak orchestrator with plan-specific agents
  - Rationale: Context isolation, parallelization, model matching
Reference from CLAUDE.md Delegation section.
Commit: "Document weak orchestrator pattern decision"
```

## Pattern: Remove Obsolete Rule

**When**: Rule no longer applies due to workflow or tooling changes

**Steps**:
1. Verify rule is truly obsolete
2. Check for dependencies (other rules reference this one?)
3. Edit to remove
4. Commit with reason for removal

**Example**:
```
Old rule: "Always use xyz tool for task X"
Verification: xyz tool deprecated, replaced with abc tool.
Check references: No other rules mention xyz.
Remove rule.
Commit: "Remove obsolete xyz tool rule - tool deprecated"
```

## Pattern: Process Pending Learnings

**When**: Handoff created learnings in agents/learnings/pending.md

**Steps**:
1. Read `agents/learnings/pending.md`
2. For each learning: infer target skill from content keywords
3. Ask user if target unclear
4. Append to `.claude/skills/{skill}/references/learnings.md`
5. Remove @ reference from pending.md
6. Delete processed learning file

**Example**:
```
Read agents/learnings/pending.md
Find: @agents/learnings/2026-01-26-tool-batching.md
Content mentions "tool calls", "batch operations"
Infer target: tool usage skill or general CLAUDE.md
Ask user: "Consolidate to tool-usage skill or CLAUDE.md?"
User chooses: CLAUDE.md
Append to Tool Batching section
Remove @ reference from pending.md
Delete agents/learnings/2026-01-26-tool-batching.md
Commit: "Consolidate tool batching learning to CLAUDE.md"
```

## Tips

- **Be specific**: Include concrete examples, not abstract principles
- **Provide context**: Explain why the rule matters
- **Keep atomic**: One concept per rule
- **Verify placement**: Put rule where agents will look for it
- **Test understanding**: Would another agent understand this rule?

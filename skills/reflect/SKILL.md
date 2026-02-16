---
name: reflect
description: This skill should be used when the user asks to "reflect", "diagnose deviation", "root cause", "why did you do X", "RCA", or after interrupting an agent that deviated from rules. Performs structured root cause analysis of agent behavior deviations within the current session context.
allowed-tools: Read, Write, Edit, Grep, Glob
user-invocable: true
---

# Reflect Skill

Perform structured root cause analysis of agent behavior deviations within the current session context. Diagnoses why an agent violated rules, bypassed constraints, or rationalized exceptions.

## When to Use

**Reflect for RCA:**

**Use when:**
- Agent deviated from documented rules or constraints
- Agent bypassed stop conditions or escalation triggers
- Agent rationalized exceptions to clear directives
- Unexpected behavior needs systematic diagnosis
- User asks "why did you do X?" after interruption

**Critical constraint:** Must run in the session where deviation occurred. The conversation context IS the diagnostic evidence. Post-session RCA loses essential context.

**Model expectation:** Designed for opus model. User switches to opus before invoking. If invoked on sonnet, RCA quality will be lower but process still works.

## Execution Protocol

### Phase 1: Diagnostic Mindset Shift

**First action:** Emit session-break framing block to force cognitive reset from execution mode to diagnostic mode:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 REFLECT MODE — Deviation Diagnosis
Previous task suspended. Analyzing conversation for rule violations.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Why critical:** Without explicit framing, the agent remains in execution mode and applies quick fixes instead of performing systematic diagnosis. The framing block forces diagnostic mindset.

### Phase 2: Identify Deviation

**Scan conversation context** (no tool calls needed — context already loaded):

1. **Locate violation point:** Identify the specific message where behavior diverged from expected
2. **State the gap:** What happened vs what should have happened
3. **Identify violated rule:**
   - Name the rule or constraint
   - Reference file path and section (e.g., `agent-core/fragments/communication.md`, "Stop on unexpected results")
   - Quote the relevant directive

**Output format:**

```markdown
**Deviation Identified:**
- Message: [turn number or timestamp if available]
- Observed: [what the agent actually did]
- Expected: [what the rule required]
- Violated rule: [rule name] (`[file path]`, section "[section name]")
- Rule text: "[quoted directive]"
```

### Phase 3: Root Cause Analysis

Analyze why the deviation occurred:

**Proximal cause:** What directly caused the deviation?
- Ambiguous rule language ("avoid" vs "do not")
- Missing constraint in documentation
- Contradictory directives from different sources
- Agent rationalization despite clear rule
- Upstream input error (bad design/plan)

**Contributing factors:** What made the deviation plausible?
- Context overload (too many competing priorities)
- Unclear boundaries between directives
- Rule discovery failure (right rule exists but wasn't loaded)
- Model limitation (haiku/sonnet interpreting nuance)

**Rule gap analysis:**
- Is the rule ambiguous? (needs strengthening)
- Is the rule missing? (needs creation)
- Is the rule contradicted elsewhere? (needs reconciliation)
- Is the rule clear but ignored? (behavioral issue, needs "no exceptions" language)

**Consult references:** See `references/patterns.md` for common deviation patterns and diagnostic heuristics.

### Phase 4: Classify Fix Scope

Based on RCA findings, classify the required fix:

| Classification | Meaning | Typical Action |
|---|---|---|
| **Rule fix** | Rule text is ambiguous or incomplete | Edit fragment/skill in-session |
| **Input fix** | Upstream document (design/plan) is incorrect | May need handoff to fix upstream first |
| **Behavioral** | Agent rationalized past clear rule | Strengthen rule with "no exceptions" language |
| **Systemic** | Pattern recurs across sessions | Create fragment/hook, update memory index |

**Multiple classifications possible.** Example: Bad upstream design (input fix) led to missing constraint (rule fix) which caused agent rationalization (behavioral). Address all layers.

### Phase 5: Execute or Handoff

Choose exit path based on context budget and fix scope:

#### Exit Path 1: Fix In-Session

**When:**
- Fixes are small (<50 lines total edits)
- Context budget allows
- All fixes are rule/fragment edits (no upstream doc changes needed)

**Actions:**
1. Apply fixes using Edit tool
2. Append learning to `agents/learnings.md` (anti-pattern / correct pattern / rationale format)
3. After appending: check learnings.md line count — if ≥70 lines, note to user: "Consider running /remember to consolidate"
4. Update memory index if systemic fix
5. Stop and return control to user

#### Exit Path 2: RCA Complete, Handoff for Fixes

**When:**
- Fixes are large or complex
- Context budget exhausted
- Multiple files need coordination
- RCA complete but implementation deferred

**Actions:**
1. Write RCA report to `plans/reflect-rca-<slug>/rca.md` where slug describes deviation
   - **Slug format:** kebab-case description of deviation type (e.g., `orchestrator-dirty-tree`, `tool-misuse-grep`)
2. Append learning to `agents/learnings.md`
3. After appending: check learnings.md line count — if ≥70 lines, note to user: "Consider running /remember to consolidate"
4. Write pending tasks to session.md in task format:
   - Format: `- [ ] **Task Name** — \`command\` | model | restart?`
   - Assess model tier per task (opus for design/architecture, sonnet for implementation, haiku for mechanical)
   - Include restart flag if fix touches agents/skills/hooks/settings (format: `| restart`)
   - Insert at estimated priority position in Pending Tasks section
5. Stop and return control to user

**RCA report template:** See `references/rca-template.md` for structure

#### Exit Path 3: Partial RCA, Handoff

**When:**
- Proximal cause is bad upstream doc (design/plan/runbook)
- Must fix upstream first before continuing RCA
- Context budget allows capturing partial findings only

**Actions:**
1. Document partial findings (what we know so far)
2. Append learning to `agents/learnings.md` if pattern identified
3. After appending: check learnings.md line count — if ≥70 lines, note to user: "Consider running /remember to consolidate"
4. Write pending tasks to session.md in task format:
   - Upstream doc fix (with path, model tier, restart flag if applicable — format: `| restart`)
   - RCA resumption (reference partial findings location)
   - Format: `- [ ] **Task Name** — \`command\` | model | restart?`
   - Insert at estimated priority position in Pending Tasks section
5. Stop and return control to user

### Output Artifacts

**Always produced:**
- Learning in `agents/learnings.md` (anti-pattern / correct pattern / rationale)
- Line count check after appending (warn if approaching 80 lines)
- Pending tasks in session.md (structured task format, inserted at estimated priority position)

**Produced when fixing in-session (Exit Path 1):**
- Edited rule/skill/fragment files
- Memory index entry if systemic pattern

**Produced when deferring fixes (Exit Path 2):**
- RCA report at `plans/reflect-rca-<slug>/rca.md`
- Slug describes deviation (e.g., `reflect-rca-orchestrator-dirty-tree`)
- Optional — only for complex multi-factor RCA

**Never produced:**
- New hooks or scripts (those are separate concerns — note as pending tasks if needed)
- Immediate fixes to upstream docs (may need separate session — handoff instead)

## Tool Constraints

**Allowed tools:**
- **Read:** Check current rule files, fragments, skills
- **Write:** Create RCA reports, append learnings
- **Edit:** Fix rules/fragments/skills in-session
- **Grep:** Find rule references, search for patterns
- **Glob:** Locate relevant documentation files

**Model selection:**
- Use current model (expected to be opus after user switch)
- Do not delegate RCA to sub-agents (loses conversation context)

## Integration

**Workflow position:** Reactive, invoked during execution when deviation noticed

**Triggers:**
- User interrupts agent mid-deviation
- User asks "why did you X?"
- User notices rule violation

**Exit:** Stop and return control to user after completing RCA work

**Related skills:**
- `/remember` — Consolidates learnings from RCA
- `/hookify` — Creates enforcement hooks if RCA identifies need

## Key Design Decisions

### Session-Local Diagnosis

RCA must run in the session where deviation occurred. The conversation context is the diagnostic evidence. A new session would need to reconstruct what happened from git history — lossy and unreliable.

### Opus Expected, Not Enforced

The skill assumes opus model for high-quality diagnosis. It cannot verify or switch the model — that's a user action. If invoked on sonnet, RCA quality will be lower but the process still works.

### Framing Block is Mandatory

Emitting the diagnostic-mode framing block is the first action, not optional. Without it, the agent continues in execution mode and applies surface fixes instead of systematic diagnosis.

### Three Exit Paths

Context budget varies. Sometimes the deviation is simple (fix a rule, 5 minutes). Sometimes root cause is a bad design requiring a new session. The skill supports graceful exit at any point, returning control to user.

### Returns Control After RCA

The skill runs in opus model (after user switches). Once RCA work is complete (fixes applied, reports written, or findings documented), it returns control to the user. This allows the user to switch back to their original model and continue working. User invokes `/handoff` and `/commit` manually when ready.

## Additional Resources

### Reference Files

For detailed diagnostic guidance:
- **`references/patterns.md`** - Common deviation patterns, diagnostic heuristics, rationalization anti-patterns
- **`references/rca-template.md`** - Structured template for RCA reports (Exit Path 2)

## Examples

**Rule Ambiguity (Fix In-Session)**

User interrupts agent that committed despite dirty submodule. Agent rationalized "only pointer matters."

- Framing block emitted
- Deviation: Agent committed parent before submodule (violated commit-rca-fixes)
- Proximal cause: Agent misinterpreted "commit submodule first" as optional
- Classification: Behavioral + Rule fix (language not strong enough)
- Fix: Edit `agent-core/fragments/commit-delegation.md` to add "MUST" and "no exceptions" language
- Append learning, return control to user

**Upstream Input Error (Partial RCA, Handoff)**

User interrupts agent implementing a step that contradicts design doc.

- Framing block emitted
- Deviation: Agent added feature X (design doc said "do not add X")
- Proximal cause: Runbook step says "add X" (contradicts design)
- Classification: Input fix (bad runbook)
- Partial RCA: Runbook author misread design
- Pending tasks: (1) Fix runbook step, (2) Resume RCA if pattern recurs
- Append learning, return control to user

**Systemic Pattern (RCA Complete, Handoff for Fixes)**

User interrupts orchestrator that continued past failed step.

- Framing block emitted
- Deviation: Orchestrator rationalized "partial success is enough"
- Proximal cause: Success criteria checked structure, not behavior (test passed but wrong output)
- Contributing factors: Common pattern across multiple runbooks
- Classification: Systemic (needs fragment + memory index entry)
- RCA report written to `plans/reflect-rca-success-criteria/rca.md`
- Pending tasks: Create `agent-core/fragments/success-criteria.md`, update memory index
- Append learning, return control to user

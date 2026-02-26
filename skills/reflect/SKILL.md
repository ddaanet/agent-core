---
name: reflect
description: Diagnose agent deviations and rule violations via root cause analysis. Triggers on "reflect", "diagnose deviation", "root cause", "why did you do X", "what went wrong", or "RCA". Must run in the session where the deviation occurred.
allowed-tools: Read, Write, Edit, Grep, Glob
user-invocable: true
---

# Diagnose Agent Rule Violations

Perform structured root cause analysis of agent behavior deviations within the current session context. Diagnoses why an agent violated rules, bypassed constraints, or rationalized exceptions.

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

Based on RCA findings, classify the structural root cause:

| Classification | Meaning | Fix Approach |
|---|---|---|
| **Directive conflict** | Competing signals; agent follows the wrong one | Resolve the conflict — remove, reconcile, or separate competing signals |
| **Unanchored gate** | Decision point lacks tool-call anchor | Add Read/Bash anchor per D+B hybrid (implementation-notes.md) |
| **Missing enforcement** | Rule exists but nothing prevents violation | Environmental enforcement: hook, script, or structural constraint with guidance |
| **Insufficient context** | Relevant decisions not loaded at decision point | Add recall loading or context embedding before the decision |
| **Input fix** | Upstream document (design/plan) is incorrect | Handoff to fix upstream first |
| **Rule gap** | Rule is genuinely missing or ambiguous | Create or clarify rule — only after ruling out structural fixes above |
| **Systemic** | Pattern recurs across sessions | Combine structural fix with memory index entry |

**Multiple classifications possible.** Example: Well-specified problem.md creates execution pressure (directive conflict) at an unanchored triage gate (unanchored gate) where prior identical instance wasn't loaded (insufficient context). Address all layers.

**Anti-pattern: Language strengthening.** Adding "no exceptions," "MUST," or scenario-specific warnings to rules the agent already saw and rationalized past. If the rule was clear and the agent overrode it, clarity was not the problem — the environment allowed the override. Fix the environment, not the prose. Language strengthening is never the correct fix for behavioral deviation.

### Phase 4.5: Diagnostic Checkpoint

1. `agent-core/bin/when-resolve.py "when <trigger>" ...` — resolve entries matching (a) the deviation's pattern class and (b) design patterns for the artifact type being modified. Read `memory-index.md` first if triggers not known from context.

2. Read the primary target file(s) identified for fixes — verify current state matches RCA assumptions. Read `agents/learnings.md` for line count.

3. Present diagnostic summary:
   - Deviation(s) and violated rules (Phase 2)
   - Root cause classification (Phases 3-4)
   - Recall entries loaded and relevance to fix design
   - Proposed fixes with target files and scope estimate
   - Learnings line count

**STOP.** Do not proceed to Phase 5 without explicit user direction. The diagnostic is the deliverable of Phases 1-4; fixes are a separate decision.

**User options:**
- **Proceed** → Phase 5 (apply fixes)
- **Deepen** → revisit Phase 3 with further investigation
- **Additional recall** → invoke `/recall` for broader coverage
- **Redirect** → provide alternative fix direction

### Phase 5: Execute or Handoff

After user confirms at diagnostic checkpoint, choose exit path based on context budget and fix scope:

#### Exit Path 1: Fix In-Session

**When:**
- Fixes are small (<50 lines total edits)
- Context budget allows
- All fixes are rule/fragment edits (no upstream doc changes needed)

**Actions:**
1. Apply fixes using Edit tool
2. Append learning to `agents/learnings.md` (anti-pattern / correct pattern / rationale format)
3. After appending: check learnings.md line count — if ≥70 lines, note to user: "Consider running /codify to consolidate"
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
3. After appending: check learnings.md line count — if ≥70 lines, note to user: "Consider running /codify to consolidate"
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
3. After appending: check learnings.md line count — if ≥70 lines, note to user: "Consider running /codify to consolidate"
4. Write pending tasks to session.md in task format:
   - Upstream doc fix (with path, model tier, restart flag if applicable — format: `| restart`)
   - RCA resumption (reference partial findings location)
   - Format: `- [ ] **Task Name** — \`command\` | model | restart?`
   - Insert at estimated priority position in Pending Tasks section
5. Stop and return control to user

### Output Artifacts

**Always produced:**
- Learning in `agents/learnings.md` (anti-pattern / correct pattern / rationale)
- Line count check after appending (warn if ≥70 lines)
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

- Use current model (expected opus). Do not delegate RCA to sub-agents (loses conversation context).
- Related skills: `/codify` (consolidates learnings), `/hookify` (creates enforcement hooks)

## Reference Files

- **`references/patterns.md`** — Common deviation patterns, diagnostic heuristics, rationalization anti-patterns
- **`references/rca-template.md`** — Structured template for RCA reports (Exit Path 2)
- **`references/rca-design-decisions.md`** — Key design decisions (session-local, opus expected, framing mandatory, diagnostic-before-fixes, three exit paths)
- **`references/rca-examples.md`** — Worked examples for each exit path (unanchored gate, upstream input error, systemic pattern)

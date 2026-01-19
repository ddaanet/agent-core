---
description: Create execution plans for weak orchestrator agents using 4-point planning process
allowed-tools: Task, Read, Write, Bash(mkdir:*)
user-invocable: true
---

# Task Plan Skill

Create detailed execution plans suitable for weak orchestrator agents using a formalized 4-point planning process. This skill transforms high-level tasks into structured plans that haiku or sonnet agents can execute with minimal judgment.

## When to Use

**Use this skill when:**
- Creating execution plans for multi-step tasks
- Delegating work to weak orchestrator agents (haiku/sonnet)
- Complex tasks need explicit design decisions documented
- Tasks require clear error escalation and validation criteria

**Do NOT use when:**
- Task is simple and can be executed directly
- Task requires user input or interactive decisions
- Plan already exists and just needs execution

## 4-Point Planning Process

### Point 1: Evaluate Script vs Direct Execution

For each task in the plan, decide on execution approach:

**1.1 Small Tasks (≤25 lines)**: Write complete script inline

**Criteria:**
- Script is short and standalone
- Logic is straightforward
- No complex dependencies

**Example:**
```bash
#!/usr/bin/env bash
# Compare two files and output diff
diff -u /path/to/file1 /path/to/file2 > output.patch || true
echo "Diff size: $(wc -c < output.patch) bytes"
```

**1.2 Medium Tasks**: Provide prose description of implementation

**Criteria:**
- Implementation requires 25-100 lines
- Logic is clear but too long for inline script
- Steps are sequential and well-defined

**Example:**
```
Implementation:
1. Verify source files exist (provide error if missing)
2. Read both files using Read tool
3. Compare content line-by-line
4. Document differences in structured format
5. Write analysis to specified output path
```

**1.3 Large/Complex Tasks**: Separate planning session required

**Criteria:**
- Task requires >100 lines or complex logic
- Multiple design decisions needed
- Significant architectural choices
- Requires human review before implementation

**Action:** Mark task as requiring separate planning session. Delegate planning to sonnet or opus depending on complexity.

---

### Point 2: Include Weak Orchestrator Metadata

Every plan MUST include this metadata section at the top:

```markdown
## Weak Orchestrator Metadata

**Total Steps**: [N]

**Execution Model**:
- Steps X-Y: Haiku (simple file operations, scripted tasks)
- Steps A-B: Sonnet (semantic analysis, judgment required)
- Steps M-N: Opus (only if explicitly required for complex design)

**Step Dependencies**:
- Sequential | Parallel | [specific dependency graph]

**Error Escalation**:
- Haiku → Sonnet: [triggers]
- Sonnet → User: [triggers]

**Report Locations**: [pattern for where reports go]

**Success Criteria**: [overall plan success, not per-step]

**Prerequisites**:
- [Prerequisite 1] (✓ verified via [method])
- [Prerequisite 2] (path: /absolute/path/to/resource)
```

**Critical Requirements:**
- **Total Steps**: Exact count for tracking
- **Execution Model**: Match model capability to task complexity
- **Step Dependencies**: Enable orchestrator to parallelize when possible
- **Error Escalation**: Clear triggers for when to escalate
- **Success Criteria**: Overall plan success (step-level criteria go in step sections)
- **Prerequisites**: Verified before execution starts
- **Report Locations**: Where execution reports will be written

**What DOES NOT belong in orchestrator metadata:**
- Inline scripts or prose step descriptions (those go in step sections)
- Objective/expected outcome for each step (those go in step sections)
- Per-step validation/error handling (those go in step sections)
- Per-step success criteria (those go in step sections)

**Key Principles:**
1. **Orchestrator metadata is coordination info only** - not execution details
2. **Orchestrator trusts agents to report accurately** - no inline validation logic
3. **Validation is delegated** - if needed, it's a separate plan step
4. **Planning happens before execution** - orchestrator doesn't make decisions during execution

---

### Point 3: Plan Review by Sonnet

Before finalizing the plan, delegate review to a sonnet task agent.

**Review Prompt Template:**

```
Review the execution plan at [path] for weak orchestrator execution.

Evaluate:
1. Completeness - All design decisions documented? Any missing choices?
2. Executability - Can weak agents (haiku/sonnet) execute with just this plan?
3. Script vs Direct - Are complexity assessments appropriate (≤25 lines = inline)?
4. Validation - Are success criteria measurable and specific?
5. Error Handling - Are escalation triggers clear and actionable?

Output format:
- Overall Assessment: READY / NEEDS_REVISION
- Critical Issues: [Must fix before execution]
- Major Issues: [Strongly recommended to address]
- Minor Issues: [Quality improvements]

Write detailed review to: [review-path]
Return: "done: [summary]" or "error: [description]"
```

**Review Criteria (from reference):**

**Completeness:**
- All design decisions made (no deferred choices)
- Prerequisites verified (not just assumed)
- Error conditions identified
- Validation criteria specific

**Executability:**
- Model selection matches task complexity
- Implementation guidance sufficient (scripts or clear prose)
- No ambiguous instructions
- File paths absolute and verified

**Script vs Direct:**
- ≤25 lines = inline script included
- 25-100 lines = prose description
- >100 lines = separate planning session
- Rationale documented

**Missing Decisions:**
- Step dependencies (sequential/parallel)
- Error recovery protocol (what happens after escalation)
- Output format specifications (templates for analysis artifacts)
- Unexpected result handling (what if reality differs from expected)

**Assessment Criteria:**
- **READY**: All critical items addressed, minor issues only
- **NEEDS_REVISION**: Critical or major issues present

**Revision Loop:**
1. Read review report
2. Address critical and major issues
3. Update plan with fixes
4. Request re-review if changes are significant
5. Iterate until assessment is READY

---

### Point 4: Split Plan into Per-Step Files

**CRITICAL: This step is MANDATORY. Splitting creates isolated execution contexts.**

**Why splitting is fundamental:**

The entire point of the plan-specific agent pattern is **context isolation**. Each step gets a fresh agent invocation with ONLY:
- Common context (metadata, prerequisites, design decisions)
- The specific step to execute
- NO execution transcript from previous steps

**Benefits of splitting:**
- Prevents context bloat from accumulating across steps
- Each step starts with clean slate (no noise from previous steps)
- Execution logs stay in report files, not in agent context
- Enables plan-specific agent pattern with context caching
- Sequential steps ESPECIALLY need splitting (to prevent cumulative bloat)

**When NOT to split:**
- Never. Always split. This is not negotiable.

After plan is reviewed and ready, create per-step files for execution.

**Use Existing Split Script:**

The split script is located at: `agent-core/scripts/split-execution-plan.py`

**Script Features:**
- Auto-detects plan format (Phase or Step format)
- Extracts common context and individual step/phase sections
- Creates step files with context references
- Generates index file (README.md) with usage instructions

**Usage:**
```bash
python agent-core/scripts/split-execution-plan.py <plan-file.md> <output-dir>
```

**Example:**
```bash
python agent-core/scripts/split-execution-plan.py \
    plans/oauth2-auth/execution-plan.md \
    plans/oauth2-auth/steps
```

**Script Output:**
- `execution-context.md` or `consolidation-context.md` - Common context for all steps/phases
- `step{N}.md` or `phase{N}.md` - Individual step/phase files
- `README.md` - Index and usage instructions

**Per-Step File Structure:**

Each step file should:
- Reference main plan for context
- Include complete step content
- Provide execution instructions
- Specify report path
- Define return format

**Benefits of Splitting:**
- Enables plan-specific agent pattern
- Each step execution is isolated
- Clear context boundaries
- Easy to track progress
- Supports parallel execution when dependencies allow

---

## Critical Constraints

**Tool Usage:**
- Use **Task** to delegate review and complex steps
- Use **Read** to check existing files
- Use **Write** to create plan and step files
- Use **Bash** for mkdir only (NOT for file content manipulation)
- Use **Edit** if modifying existing plans

**Model Selection:**
- **Haiku**: Simple execution, scripted tasks, file operations
- **Sonnet**: Default for planning and review, semantic analysis
- **Opus**: Only when explicitly required for complex architecture

**Error Handling:**
- Report all errors explicitly
- Never suppress errors with `|| true` unless intentional
- Define clear escalation triggers
- Document recovery protocol

**Output Locations:**
- Execution logs: `plans/[plan-name]/reports/`
- Analysis artifacts: `scratch/[context]/analysis/` or plan-specific directory
- Per-step files: `plans/[plan-name]/steps/`

**Validation:**
- Success criteria must be measurable
- Use specific file paths (absolute)
- Include size/count checks
- Specify required sections/format

## Example Execution Flow

**User:** `/task-plan` for implementing authentication feature

**Agent:** "I'll help create an execution plan using the 4-point process.

What is the plan for? (Brief description): "

**User:** "Implement OAuth2 authentication with Google provider"

**Agent:**

**Point 1: Evaluating Tasks**

Let me break this down:

1. Setup OAuth2 configuration (small - inline script)
2. Implement auth routes and handlers (medium - prose description)
3. Add session management (medium - prose description)
4. Create user profile integration (medium - prose description)
5. Write integration tests (large - separate planning needed)

**Point 2: Creating Plan with Metadata**

*Delegates to sonnet task agent to create initial plan draft*

**Point 3: Plan Review**

*Delegates to sonnet task agent for review*
*Receives: "Review complete - 2 critical issues, 3 major issues - NEEDS_REVISION"*

*Addresses issues and requests re-review*
*Receives: "Re-review complete - All critical issues resolved - READY"*

**Point 4: Split into Steps**

*Writes Python script to split plan*
*Executes script to create per-step files*

Plan created:
- Main plan: `plans/oauth2-auth/execution-plan.md`
- Review: `plans/oauth2-auth/reports/plan-review.md`
- Steps: `plans/oauth2-auth/steps/step1.md` through `step4.md`
- Note: Step 5 (tests) marked for separate planning session

Ready for execution. Run steps with weak orchestrator using step files."

## Template Structure for Plans

**Main Plan File:**

```markdown
# [Plan Name] Execution Plan

**Context**: [Brief description of what this plan accomplishes]

**Source**: [Reference to requirements, design docs, or parent plan]
**Design**: [Reference to design decisions document if applicable]

**Status**: [Draft / In Review / Ready / Complete]
**Created**: YYYY-MM-DD
**Reviewed**: YYYY-MM-DD ([reviewer], [assessment])
**Revised**: YYYY-MM-DD (if applicable)

---

## Weak Orchestrator Metadata

[Metadata section as defined in Point 2]

---

## Step 1.1: [Step Name]

**Objective**: [Clear, concise objective]

**Script Evaluation**: [Direct execution / Small script / Prose description / Separate planning]

**Execution Model**: [Haiku / Sonnet / Opus]

**Implementation**:
[Inline script OR prose steps OR reference to separate plan]

**Expected Outcome**: [What should happen when successful]

**Unexpected Result Handling**:
- If [condition]: [Action to take]

**Error Conditions**:
- [Error type] → [Escalation action]

**Validation**:
- [Validation check 1]
- [Validation check 2]

**Success Criteria**:
- [Measurable criterion 1]
- [Measurable criterion 2]

**Report Path**: [Absolute path to execution log]

---

[Repeat for each step]

---

## Design Decisions

[Document key decisions made during planning]

---

## Dependencies

**Before This Plan**:
- [Prerequisite 1]
- [Prerequisite 2]

**After This Plan**:
- [What can be done next]
- [Artifacts available for downstream work]

---

## Revision History

**Revision 1 (YYYY-MM-DD)** - [Summary of changes]
**Revision 2 (YYYY-MM-DD)** - [Summary of changes]

**Review report**: [Path to review report]

---

## Notes

[Additional context, assumptions, or important details]
```

## Common Pitfalls

**Avoid:**
- Assuming prerequisites are met without verification
- Assigning semantic analysis tasks to haiku
- Leaving design decisions for "during execution"
- Vague success criteria ("analysis complete" vs "analysis has 6 sections with line numbers")
- Missing error escalation triggers
- Conflating execution logs and analysis artifacts
- Using relative paths instead of absolute
- Deferring validation to future phases

**Instead:**
- Verify prerequisites explicitly
- Match model to task complexity
- Make all decisions during planning
- Define measurable success criteria
- Document clear escalation triggers
- Separate execution logs from output artifacts
- Use absolute paths consistently
- Include validation in each step

## References

**Example Plan**: `/Users/david/code/claudeutils/plans/unification/phase2-execution-plan.md`
**Example Review**: `/Users/david/code/claudeutils/plans/unification/reports/phase2-plan-review.md`
**Split Script**: `/Users/david/code/agent-core/scripts/split-execution-plan.py`

These demonstrate the complete 4-point process in practice.

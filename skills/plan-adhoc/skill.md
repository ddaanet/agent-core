---
description: Create execution runbooks for weak orchestrator agents using 4-point planning process (oneshot workflow)
allowed-tools: Task, Read, Write, Bash(mkdir:*, python3:*)
user-invocable: true
---

# Plan Ad-hoc Skill

Create detailed execution runbooks suitable for weak orchestrator agents using a formalized 4-point planning process. This skill transforms high-level tasks into structured runbooks that haiku or sonnet agents can execute with minimal judgment.

**Workflow Context:** Part of oneshot workflow (design → planning → execution). Contrast with `/plan-tdd` (future, feature dev emphasis).

## When to Use

**Use this skill when:**
- Creating execution runbooks for multi-step tasks
- Delegating work to weak orchestrator agents (haiku/sonnet)
- Complex tasks need explicit design decisions documented
- Tasks require clear error escalation and validation criteria
- Ad-hoc oneshot work (vs iterative feature development)

**Do NOT use when:**
- Task is simple and can be executed directly
- Task requires user input or interactive decisions
- Plan already exists and just needs execution
- Feature development requiring TDD approach (use `/plan-tdd` when available)

## 4-Point Planning Process

### Point 1: Evaluate Script vs Direct Execution

For each task in the runbook, decide on execution approach:

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

Every runbook MUST include this metadata section at the top:

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

**Success Criteria**: [overall runbook success, not per-step]

**Prerequisites**:
- [Prerequisite 1] (✓ verified via [method])
- [Prerequisite 2] (path: /absolute/path/to/resource)
```

**Critical Requirements:**
- **Total Steps**: Exact count for tracking
- **Execution Model**: Match model capability to task complexity
- **Step Dependencies**: Enable orchestrator to parallelize when possible
- **Error Escalation**: Clear triggers for when to escalate
- **Success Criteria**: Overall runbook success (step-level criteria go in step sections)
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

Before finalizing the runbook, delegate review to a sonnet task agent.

**Review Prompt Template:**

```
Review the execution runbook at [path] for weak orchestrator execution.

Evaluate:
1. Completeness - All design decisions documented? Any missing choices?
2. Executability - Can weak agents (haiku/sonnet) execute with just this runbook?
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
3. Update runbook with fixes
4. Request re-review if changes are significant
5. Iterate until assessment is READY

---

### Point 4: Prepare Runbook Artifacts

**CRITICAL: This step is MANDATORY. Use `prepare-runbook.py` to create execution artifacts.**

**Why artifact preparation is fundamental:**

The entire point of the plan-specific agent pattern is **context isolation**. Each step gets a fresh agent invocation with ONLY:
- Common context (metadata, prerequisites, design decisions)
- The specific step to execute
- NO execution transcript from previous steps

**Benefits of preparation:**
- Prevents context bloat from accumulating across steps
- Each step starts with clean slate (no noise from previous steps)
- Execution logs stay in report files, not in agent context
- Enables plan-specific agent pattern with context caching
- Sequential steps ESPECIALLY need splitting (to prevent cumulative bloat)

**When NOT to prepare:**
- Never. Always prepare. This is not negotiable.

After runbook is reviewed and ready, use the preparation script to create artifacts.

**Use prepare-runbook.py Script:**

The script is located at: `agent-core/bin/prepare-runbook.py`

**Script Features:**
- Parses runbook with optional YAML frontmatter
- Extracts Common Context section
- Extracts individual Step sections (## Step N: or ## Step N.M:)
- Creates plan-specific agent (baseline + common context)
- Generates step files for execution
- Creates orchestrator plan
- Validates structure and reports errors clearly

**Usage:**
```bash
python3 agent-core/bin/prepare-runbook.py <runbook-file.md>
```

**Example:**
```bash
python3 agent-core/bin/prepare-runbook.py plans/oauth2-auth/runbook.md
```

**Script automatically derives paths:**
- Runbook name: From parent directory (e.g., `oauth2-auth` from `plans/oauth2-auth/runbook.md`)
- Plan-specific agent: `.claude/agents/<runbook-name>-task.md`
- Step files: `plans/<runbook-name>/steps/step-N.md` or `step-N-M.md`
- Orchestrator plan: `plans/<runbook-name>/orchestrator-plan.md`

**Script Output:**
```
✓ Created agent: .claude/agents/oauth2-auth-task.md
✓ Created step: plans/oauth2-auth/steps/step-1.md
✓ Created step: plans/oauth2-auth/steps/step-2.md
✓ Created step: plans/oauth2-auth/steps/step-3.md
✓ Created orchestrator: plans/oauth2-auth/orchestrator-plan.md

Summary:
  Runbook: oauth2-auth
  Steps: 3
  Model: haiku
```

**Runbook Format Requirements:**

**Optional YAML frontmatter:**
```yaml
---
name: custom-name  # Override derived name
model: sonnet      # Default model for plan-specific agent
---
```

**Required sections:**
- Steps: `## Step N:` or `## Step N.M:` headings
- At least one step must be present

**Optional sections:**
- `## Common Context` - Shared context for all steps
- `## Orchestrator Instructions` - Custom orchestrator guidance

**Benefits of prepare-runbook.py:**
- Automatic path derivation (no manual file creation)
- Validation (fails on missing baseline, duplicate steps, etc.)
- Idempotent (re-runnable after runbook updates)
- Consistent artifact structure
- Plan-specific agent with cached context

---

## Critical Constraints

**Tool Usage:**
- Use **Task** to delegate review and complex steps
- Use **Read** to check existing files
- Use **Write** to create runbook files
- Use **Bash** for mkdir and python3 script execution
- Use **Edit** if modifying existing runbooks

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
- Runbook: `plans/[runbook-name]/runbook.md` or `[name]-plan.md`
- Execution logs: `plans/[runbook-name]/reports/`
- Step files: `plans/[runbook-name]/steps/` (created by script)
- Plan-specific agent: `.claude/agents/[runbook-name]-task.md` (created by script)
- Orchestrator plan: `plans/[runbook-name]/orchestrator-plan.md` (created by script)

**Validation:**
- Success criteria must be measurable
- Use specific file paths (absolute)
- Include size/count checks
- Specify required sections/format

## Example Execution Flow

**User:** `/plan-adhoc` for implementing authentication feature

**Agent:** "I'll help create an execution runbook using the 4-point process.

What is the runbook for? (Brief description): "

**User:** "Implement OAuth2 authentication with Google provider"

**Agent:**

**Point 1: Evaluating Tasks**

Let me break this down:

1. Setup OAuth2 configuration (small - inline script)
2. Implement auth routes and handlers (medium - prose description)
3. Add session management (medium - prose description)
4. Create user profile integration (medium - prose description)
5. Write integration tests (large - separate planning needed)

**Point 2: Creating Runbook with Metadata**

*Creates initial runbook draft with orchestrator metadata*

**Point 3: Runbook Review**

*Delegates to sonnet task agent for review*
*Receives: "Review complete - 2 critical issues, 3 major issues - NEEDS_REVISION"*

*Addresses issues and requests re-review*
*Receives: "Re-review complete - All critical issues resolved - READY"*

**Point 4: Prepare Artifacts**

*Runs prepare-runbook.py to create execution artifacts*

```bash
python3 agent-core/bin/prepare-runbook.py plans/oauth2-auth/runbook.md
```

Artifacts created:
- Plan-specific agent: `.claude/agents/oauth2-auth-task.md`
- Steps: `plans/oauth2-auth/steps/step-{1,2,3,4}.md`
- Orchestrator plan: `plans/oauth2-auth/orchestrator-plan.md`
- Note: Step 5 (tests) marked for separate planning session

Ready for execution. Use `/orchestrate` to execute the runbook."

## Runbook Template Structure

**Main Runbook File:**

```markdown
---
name: runbook-name  # Optional: override directory-based name
model: haiku        # Optional: default model for plan-specific agent
---

# [Runbook Name]

**Context**: [Brief description of what this runbook accomplishes]

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

## Common Context

[Shared information for all steps]

**Key Constraints:**
- [Constraint 1]
- [Constraint 2]

**Project Paths:**
- [Path 1]: [Description]
- [Path 2]: [Description]

**Conventions:**
- [Convention 1]
- [Convention 2]

---

## Step 1: [Step Name]

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

## Orchestrator Instructions

[Optional: Custom instructions for weak orchestrator]

Default behavior if omitted:
- Execute steps sequentially using [runbook-name]-task agent
- Stop on error and escalate to sonnet

---

## Design Decisions

[Document key decisions made during planning]

---

## Dependencies

**Before This Runbook**:
- [Prerequisite 1]
- [Prerequisite 2]

**After This Runbook**:
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
- Forgetting to run prepare-runbook.py after review

**Instead:**
- Verify prerequisites explicitly
- Match model to task complexity
- Make all decisions during planning
- Define measurable success criteria
- Document clear escalation triggers
- Separate execution logs from output artifacts
- Use absolute paths consistently
- Include validation in each step
- Always run prepare-runbook.py to create artifacts

## References

**Example Runbook**: `/Users/david/code/claudeutils/plans/unification/phase2-execution-plan.md`
**Example Review**: `/Users/david/code/claudeutils/plans/unification/reports/phase2-plan-review.md`
**Preparation Script**: `/Users/david/code/claudeutils/agent-core/bin/prepare-runbook.py`
**Baseline Agent**: `/Users/david/code/claudeutils/agent-core/agents/quiet-task.md`

These demonstrate the complete 4-point process in practice.

## Integration with Oneshot Workflow

**Workflow stages:**
1. `/design` - Opus creates design document
2. `/plan-adhoc` - Sonnet creates execution runbook (THIS SKILL)
3. `/orchestrate` - Haiku executes runbook steps
4. `/vet` - Review changes before commit
5. Complete job

**Handoff:**
- Input: Design document from `/design` skill
- Output: Ready-to-execute artifacts (agent, steps, orchestrator plan)
- Next: User invokes `/orchestrate` to execute runbook

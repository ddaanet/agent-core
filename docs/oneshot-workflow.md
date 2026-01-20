# Oneshot Workflow Guide

**Purpose:** Execute one-off, ad-hoc tasks that don't repeat.

## What is a "Oneshot" Task?

**Oneshot tasks** are one-time operations that don't require ongoing maintenance:
- **Migrations** - Database migrations, data transformations, format conversions
- **Refactoring** - Code cleanup, architecture improvements, technical debt
- **Prototypes** - Experimental implementations, proof-of-concepts
- **Infrastructure** - One-time config changes, deployment updates, tooling setup
- **Fixes** - Legacy code updates, one-time bug fixes, cleanup tasks

**NOT oneshot** (use feature development workflow instead):
- **Repeatable features** - User-facing functionality with ongoing maintenance
- **Production features** - Require comprehensive tests and documentation
- **Business logic** - Features that will be used repeatedly and modified over time

**Key distinction:** If it needs ongoing maintenance, comprehensive tests, and user-facing documentation → **feature development**. If it's a one-time change → **oneshot**.

## Entry Point: `/oneshot` Skill

The easiest way to start a oneshot task:
```
/oneshot "migrate database from SQLite to PostgreSQL"
```

The `/oneshot` skill will:
1. Verify this is a oneshot task (not feature development)
2. Assess complexity (simple/moderate/complex)
3. Set up workflow stages in `session.md` as pending tasks
4. Begin executing the first stage

**User reads no docs** - the workflow guides itself through `session.md`.

---

## Terminology

| Term | Definition |
|------|------------|
| **Job** | What you want to accomplish (user goal) |
| **Design** | Architectural specification from Opus design session |
| **Phase** | Design-level segmentation for complex work |
| **Runbook** | Step-by-step implementation instructions |
| **Step** | Individual unit of work within a runbook |
| **Runbook prep** | 4-point process: Evaluate, Metadata, Review, Split |

---

## Workflow Overview

The oneshot workflow has 6 stages:

```
Discussion → [Design] → Planning → Execution → Review → Completion
              optional
```

### Decision Flow

1. **Simple job** → Execute directly (no workflow needed)
2. **Moderate complexity** → Skip to Planning (Stage 3)
3. **Complex/uncertain** → Start with Design (Stage 2)

**Complexity heuristics:**
- **Moderate**: Clear requirements, straightforward implementation
- **Complex**: Architectural decisions needed OR unclear requirements

---

## Stage 1: Initial Discussion

**Model:** Sonnet (orchestrator)

**Purpose:** Define job scope and choose workflow path.

**Activities:**
- Discuss requirements with user
- Clarify scope and constraints
- Determine complexity level
- Route to appropriate next stage

**Decision tree:**
- Simple → Execute directly using CLAUDE.md patterns
- Moderate → Continue to Planning (Stage 3)
- Complex → Handoff to Design (Stage 2)

---

## Stage 2: Design Session (Optional)

**Model:** Opus
**Skill:** `/design`

**Purpose:** Resolve architectural ambiguity and capture complex requirements.

**When to use:**
- Architectural decisions required
- User uncertain about requirements
- Multiple valid approaches exist
- Complex technical constraints

**Activities:**
- Examine existing artifacts
- Explore codebase (delegated to specialized agents)
- Search web if needed
- Get user validation on design outline
- Create dense design document

**Design document contains:**
- Motivation and scope
- Key architectural choices with rationale
- Design decisions with trade-offs
- Implementation phases (if complex)
- **NO detailed steps** (sonnet does this in Planning)

**Output:** Compact design doc targeting sonnet (not user).

---

## Stage 3: Planning Session

**Model:** Sonnet
**Skill:** `/plan-adhoc`

**Purpose:** Create executable runbook from requirements or design.

**Inputs:**
- User requirements (from Discussion), OR
- Design document (from Design Session)

**Activities:**

### 1. Evaluate
Determine implementation approach:
- **≤25 lines**: Direct script execution (no agent needed)
- **25-100 lines**: Consider script vs prose delegation
- **>100 lines**: Separate planning required

### 2. Metadata
Add weak orchestrator coordination info:
- Default model (haiku/sonnet)
- Error handling rules
- Reporting locations
- Sequencing constraints

### 3. Review
Delegate to sonnet sub-agent for validation:
- Completeness check
- Executability verification
- Context sufficiency
- Apply review fixes

### 4. Split
Run `prepare-runbook.py` to create:
- Plan-specific agent (`.claude/agents/<name>-task.md`)
- Step files (`plans/<name>/steps/step-*.md`)
- Orchestrator plan (`plans/<name>/orchestrator-plan.md`)

**Special case:** If job is simple enough for single step, offer immediate execution.

**Output:** Prepared runbook ready for execution.

---

## Stage 4: Execution

**Model:** Haiku (weak orchestrator)
**Skill:** `/orchestrate`

**Purpose:** Execute runbook steps reliably and efficiently.

**Inputs:**
- Orchestrator plan (from Planning)
- Plan-specific agent (cached in system prompt)
- Step files (one per step)

**Orchestrator responsibilities:**
- Invoke plan-specific agent for each step
- Track progress
- Handle errors per runbook rules:
  - **Simple error** → Delegate to sonnet for fix
  - **Complex error** → Abort, request opus plan update
- Write reports to specified locations

**Pattern: Quiet Execution**
- Agents write detailed output to files
- Orchestrator receives only:
  - Success: filename
  - Failure: error + diagnostic info
- Keeps orchestrator context lean

---

## Stage 5: Review

**Model:** Sonnet
**Skill:** `/vet`

**Purpose:** Review completed work before finalization.

**Scope:** Uncommitted changes, recent commits, or partial branch.

**Activities:**
- Determine review scope (ask user)
- Analyze changes
- Identify issues
- Suggest improvements

**Fix classification:**
- **Few/simple fixes** → Execute directly
- **Moderate fixes** → Delegate to sub-agent
- **Complex fixes** → Create fixes runbook (back to Planning)

**Note:** `/vet` is distinct from built-in `/review` (PR-focused).

---

## Stage 6: Completion

**Purpose:** Finalize work and update project documentation.

**Activities:**
- Update project documentation for changes
- Record architectural choices in `agents/design-decisions.md`
- Move relevant decisions OUT of `plans/` to permanent docs
- Delete plan-specific agent (no use beyond its runbook)
- Archive or delete plan directory per project convention

---

## Skills Reference

### `/oneshot`
**Stage:** Entry point (any)
**Model:** Sonnet (orchestrator)
**Use when:** Starting a new one-off task

**What it does:**
- Verifies task is oneshot (not feature development)
- Checks session.md state, offers to shelve if needed
- Assesses complexity (simple/moderate/complex)
- Sets up workflow stages as pending tasks in session.md
- Begins first stage automatically

**Why use it:** Single command to start oneshot workflow. No docs needed.

---

### `/design`
**Stage:** 2 (Design Session)
**Model:** Opus
**Use when:** Complex jobs, uncertain requirements, architectural decisions

**What it does:**
- Runs Opus design session with delegated exploration
- Creates dense design document
- Captures fuzzy requirements and technical constraints

---

### `/plan-adhoc`
**Stage:** 3 (Planning)
**Model:** Sonnet
**Use when:** Ready to create implementation steps

**What it does:**
- Executes 4-point runbook prep process
- Delegates review to validation sub-agent
- Invokes `prepare-runbook.py` to create execution artifacts
- Primes session.md for orchestrator handoff

**Future:** Will be complemented by `/plan-tdd` for feature development.

---

### `/orchestrate`
**Stage:** 4 (Execution)
**Model:** Haiku
**Use when:** Executing prepared runbooks only

**What it does:**
- Executes runbook steps using plan-specific agent
- Handles error escalation
- Tracks progress
- Reports to specified locations

**Prerequisites:** Must have prepared runbook from `/plan-adhoc`.

---

### `/vet`
**Stage:** 5 (Review)
**Model:** Sonnet
**Use when:** Reviewing in-progress or completed changes

**What it does:**
- Asks user what to review (uncommitted, recent commits, branch)
- Analyzes changes
- Identifies issues
- Suggests improvements

**Distinction:** NOT for PRs (use built-in `/review` for that).

---

### `/remember`
**Stage:** Any
**Model:** Sonnet
**Use when:** Documenting workflow learnings or updating rules

**What it does:**
- Updates CLAUDE.md with new rules/constraints
- Updates agents/context.md with pattern learnings
- Documents workflow improvements
- Adds constraints after discovering issues

**Principles:**
- Precision over brevity
- Examples over abstractions
- Constraints over guidelines
- Atomic changes

---

## Multi-Session Workflow

The oneshot workflow is designed for natural multi-session execution with model switching.

### How It Works

1. **Start with `/oneshot`** - Sets up workflow in `session.md`
2. **Work continues** - Agent executes stages, updates `session.md`
3. **Session break** - Agent calls `/handoff`, advises on model switch if needed
4. **User starts new session** - Types `#load` or just describes next step
5. **Agent continues** - Reads `session.md`, resumes from pending tasks
6. **Repeat** - Until all workflow stages complete

### Example Multi-Session Flow

**Session 1 (Sonnet):**
```
User: /oneshot "refactor auth system to support OAuth providers"
Agent: Assesses as complex oneshot task
Agent: Sets up workflow in session.md:
       - [ ] Design - Explore architecture (/design - Opus)
       - [ ] Planning - Create runbook (/plan-adhoc)
       - [ ] Execution - Run steps (/orchestrate - Haiku)
       - [ ] Review - Check changes (/vet)
       - [ ] Completion - Finalize docs
Agent: "Design stage requires Opus. Switch to Opus model and type #load to continue."
```

**Session 2 (User switches to Opus):**
```
User: #load
Agent: Reads session.md, sees Design stage pending
Agent: Invokes /design skill
Agent: Explores codebase, makes architectural decisions
Agent: Completes design document
Agent: Updates session.md (Design complete, Planning next)
Agent: Calls /handoff: "Switch to Sonnet for Planning stage"
```

**Session 3 (User switches to Sonnet):**
```
User: #load
Agent: Reads session.md, sees Planning stage pending
Agent: Invokes /plan-adhoc
Agent: Creates runbook with implementation steps
Agent: Runs prepare-runbook.py to generate artifacts
Agent: Updates session.md (Planning complete, Execution next)
Agent: Calls /handoff: "Switch to Haiku for Execution stage"
```

**Session 4 (User switches to Haiku):**
```
User: #load
Agent: Reads session.md, sees Execution stage pending
Agent: Invokes /orchestrate
Agent: Executes runbook steps
Agent: Updates session.md (Execution complete, Review next)
Agent: Calls /handoff: "Switch to Sonnet for Review stage"
```

**Session 5 (User switches to Sonnet):**
```
User: #load
Agent: Reads session.md, sees Review and Completion pending
Agent: Invokes /vet to review changes
Agent: Makes any fixes needed
Agent: Updates documentation
Agent: Updates session.md (all tasks complete)
Agent: Calls /handoff: "All workflow tasks complete. Start fresh session for new work."
```

### Key Benefits

- **Zero context overhead** - Each session starts fresh, reads state from `session.md`
- **Right model for right task** - Design uses Opus, Execution uses Haiku, etc.
- **Natural breaks** - Work can pause/resume at any stage
- **Transparent state** - User sees workflow in `session.md` at any time
- **Cost efficient** - Only use expensive models when needed

---

## Example Flows

### Example 1: Simple Job (No Workflow)

**Job:** "Fix typo in README"

**Flow:**
1. Discussion: Sonnet determines this is trivial
2. Execute directly (no workflow stages needed)

---

### Example 2: Moderate Complexity

**Job:** "Add logging to API endpoints"

**Flow:**
1. **Discussion** (Stage 1): Requirements clear, approach straightforward
2. **Planning** (Stage 3): Create runbook with `/plan-adhoc`
3. **Execution** (Stage 4): Run steps with `/orchestrate`
4. **Review** (Stage 5): Check changes with `/vet`
5. **Completion** (Stage 6): Update docs, finalize

---

### Example 3: Complex Job

**Job:** "Implement real-time data sync across services"

**Flow:**
1. **Discussion** (Stage 1): Complex, multiple approaches possible
2. **Design** (Stage 2): Use `/design` to explore options (WebSockets vs SSE vs polling)
3. **Planning** (Stage 3): Create runbook from design with `/plan-adhoc`
4. **Execution** (Stage 4): Run Phase 1 steps with `/orchestrate`
5. **Planning** (Stage 3): Plan Phase 2 after Phase 1 validation
6. **Execution** (Stage 4): Run Phase 2 steps
7. **Review** (Stage 5): Check all changes with `/vet`
8. **Completion** (Stage 6): Update architecture docs with `/remember`, finalize

---

## Tips and Best Practices

### When to Use Design Stage

**Use `/design` when:**
- You're not sure what approach to take
- Multiple valid solutions exist
- Architectural impact is significant
- Requirements are fuzzy or incomplete

**Skip `/design` when:**
- Implementation is obvious
- Requirements are crystal clear
- Changes are localized and low-risk

### Model Selection

- **Haiku**: Execution only (orchestrator in Stage 4)
- **Sonnet**: Planning, review, most work (Stages 1, 3, 5, 6)
- **Opus**: Design and complex architecture only (Stage 2)

### Runbook Changes Mid-Execution

If execution reveals issues with the runbook:

1. Update the runbook markdown file
2. Re-run `prepare-runbook.py` (idempotent, overwrites artifacts)
3. Resume execution from failed step

Git tracks all changes to runbook and artifacts.

### Documentation Flow

**During execution:**
- Record decisions in `plans/<name>/decisions.md`

**After completion:**
- Move important decisions to `agents/design-decisions.md`
- Delete plan-specific agent
- Archive plan directory (or delete per project convention)

---

## Related Documentation

- **CLAUDE.md**: Agent instructions, communication rules, patterns
- **agents/context.md**: Current task context and architecture
- **agents/design-decisions.md**: Architectural decisions and rationale
- **agents/session.md**: Current session handoff context

---

## Script: `prepare-runbook.py`

**Location:** `agent-core/bin/prepare-runbook.py`

**Purpose:** Transform runbook document into execution artifacts.

**Usage:**
```bash
prepare-runbook.py plans/foo/runbook.md
```

**Creates:**
- `.claude/agents/foo-task.md` (plan-specific agent)
- `plans/foo/steps/step-*.md` (individual steps)
- `plans/foo/orchestrator-plan.md` (orchestrator instructions)

**Runbook format:**
```markdown
---
name: <runbook-name>
model: sonnet  # default model for steps
---

## Common Context
[Shared knowledge for all steps]

## Step 1: [Title]
[Step instructions]

## Step 2: [Title]
[Step instructions]

## Orchestrator Instructions
[Sequencing, error handling, reporting]
```

**Validation:**
- Fails on: missing baseline, missing steps, duplicate numbers
- Warns on: existing artifacts, missing optional sections

---

## Change Log

**2026-01-19**: Initial workflow documentation (oneshot pattern formalized)

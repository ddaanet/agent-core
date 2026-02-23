# General Step Patterns

Guidance for decomposing prose-edit and non-TDD work into steps with proper granularity, prerequisites, and validation.

---

## Granularity Criteria

**Atomic steps** (single file, single concern):
- One file modified, one logical change
- <100 lines changed
- Single validation criterion
- Self-contained: no coordination with other files needed

**Composable steps** (multiple files, related changes):
- 2-5 files modified with shared purpose
- Related changes that must be consistent (e.g., update agent + its referenced taxonomy)
- Shared validation criteria across files
- Single commit boundary

**Complex steps** (needs decomposition):
- >100 lines changed across files
- Multiple unrelated concerns bundled together
- Requires separate investigation before implementation
- Split into atomic/composable steps before execution

### When to Split

- Files serve unrelated purposes (agent definition vs decision document)
- Different reviewers needed (skill-reviewer vs agent-creator vs corrector)
- Different validation criteria per artifact
- Independent failure modes (one can succeed while other fails)

### When to Merge

- Same file, sequential edits (avoid redundant read-edit-commit cycles)
- Shared success criteria (both changes verified by same reviewer)
- Tight coupling (change A is meaningless without change B)
- Same reviewer handles both artifacts

---

## Prerequisite Validation Patterns

### Creation Steps

Steps that create new files or add new sections require investigation prerequisites.

**Pattern:**
```markdown
**Prerequisites**:
- Read `path/to/file.md` (understand current structure and conventions)
- Read `path/to/reference.md` (pattern to follow)
```

**Why:** Without reading existing patterns, creation steps produce inconsistent artifacts. The agent has no reference for formatting, naming, or structural conventions.

**Heuristic:** If the step says "Create" or "Add new section," it needs a prerequisite reading the nearest existing example of that artifact type.

### Transformation Steps

Steps that modify existing content within known boundaries are self-contained.

**Pattern:**
```markdown
**Prerequisites**:
- Read `path/to/target.md` (current state of file being modified)
```

**Why:** The step file provides the transformation recipe. Reading the target file is sufficient context.

**Heuristic:** If the step says "Update," "Modify," "Replace," or "Delete" on a known file with specified changes, a single target-file read suffices.

### Investigation Gates

Some steps require codebase exploration before implementation can begin.

**When required:**
- Step references "existing patterns" without specifying which files
- Step requires understanding cross-file dependencies
- Step modifies behavior that other files consume
- Step says "verify" or "check" without specifying what to look for

**Pattern:**
```markdown
**Prerequisites**:
- Grep `pattern` in `directory/` (identify all consumers of X)
- Read results to understand usage patterns
```

**Heuristic:** If the implementer cannot complete the step without first discovering which files are affected, add an investigation prerequisite.

---

## Step Structure Template

```markdown
## Step X.Y: [Action verb] [target artifact]

**Objective**: [Single sentence: what changes and why]

**Prerequisites**:
- Read `path/to/file` (reason for reading)
- [Investigation gate if needed]

**Implementation**:
[Numbered list of concrete changes with file paths and section references]

**Expected Outcome**:
- [Concrete, verifiable statement about what exists after step completes]
- [Measurable: line counts, section names, field presence]

**Error Conditions**:
- If [specific failure] -> [concrete recovery action]

**Validation**:
1. Commit changes
2. Delegate to [appropriate reviewer] (see artifact review routing in `pipeline-contracts.md`)
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/[plan-name]/reports/step-X.Y-review.md

> **Orchestrator responsibility:** Review delegation in validation sections is executed by the orchestrator, not the execution agent. Sub-agents lack Task and Skill tools — they cannot delegate to any reviewer. All reviews must be delegated to prevent implementer bias. The execution agent commits; the orchestrator reads the validation section and delegates the review. See artifact review routing in `pipeline-contracts.md`.
```

---

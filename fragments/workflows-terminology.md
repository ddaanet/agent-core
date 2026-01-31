## Workflow Selection

**Entry point:**
- **Questions/research/discussion** → Handle directly (no workflow needed)
- **Implementation tasks** (code, files, scripts, migrations, refactoring) → Use `/oneshot` skill
- **Workflow in progress** (check session.md) → Continue from current state

The `/oneshot` skill auto-detects methodology and complexity, routing to appropriate workflow.

**TDD workflow** - Feature development with test-first methodology:
- **Signals:** Test-first culture, user mentions "test/TDD/red-green", behavioral verification needed
- **Route:** `/design` (TDD mode) → `/plan-tdd` → [tdd-plan-reviewer] → [apply fixes] → prepare-runbook.py (auto) → tail: `/handoff --commit` → tail: `/commit` → restart → `/orchestrate` → `/vet`
- **Review:** tdd-plan-reviewer agent checks for prescriptive code and RED/GREEN violations
- **Post-planning:** Automated via tail-call chain: prepare-runbook.py runs, orchestrate command copied to clipboard, then `/handoff --commit` → `/commit` → displays next pending task (restart instructions)

**Oneshot workflow** - General implementation tasks:
- **Signals:** Infrastructure, refactoring, prototyping, migrations, default case
- **Route:** `/design` → `/plan-adhoc` → prepare-runbook.py (auto) → tail: `/handoff --commit` → tail: `/commit` → restart → `/orchestrate` → `/vet`
- **Post-planning:** Automated via tail-call chain: prepare-runbook.py runs, orchestrate command copied to clipboard, then `/handoff --commit` → `/commit` → displays next pending task (restart instructions)
- **Detailed guide:** `agent-core/agents/oneshot-workflow.md` (read when executing oneshot workflow)

**Progressive discovery:** Don't preload all workflow documentation. Read detailed guides only when executing that specific workflow type. Use references as needed during execution.

---

## Terminology

| Term | Definition |
|------|------------|
| **Job** | What the user wants to accomplish |
| **Design** | Architectural specification from Opus design session |
| **Phase** | Design-level segmentation for complex work |
| **Runbook** | Step-by-step implementation instructions (previously called "plan") |
| **Step** | Individual unit of work within a runbook |
| **Runbook prep** | 4-point process: Evaluate, Metadata, Review, Split |

**Note on directory naming:** The `plans/` directory is a historical convention and remains unchanged. It contains runbooks, step files, and execution artifacts.

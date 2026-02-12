## Workflow Selection

**Entry point:**
- **Questions/research/discussion** → Handle directly (no workflow needed)
- **Implementation tasks** → Use `/design` skill (triages complexity, routes to appropriate workflow)
- **Workflow in progress** (check session.md) → Continue from current state

The `/design` skill includes complexity triage: simple tasks execute directly, moderate tasks skip design and route to planning, complex tasks get full design treatment.

**Implementation workflow** — unified planning for all implementation work:
- **Route:** `/design` → `/runbook` → [plan-reviewer] → prepare-runbook.py (auto) → tail: `/handoff --commit` → tail: `/commit` → restart → `/orchestrate` → [vet agent]
- **Per-phase typing:** Each phase tagged TDD or general. TDD phases get RED/GREEN cycles, general phases get task steps. Mixed runbooks supported.
- **Review:** plan-reviewer agent checks TDD discipline, step quality, and LLM failure modes (type-aware per phase)
- **Post-planning:** Automated via tail-call chain: prepare-runbook.py runs, orchestrate command copied to clipboard, then `/handoff --commit` → `/commit` → displays next pending task
- **Tier assessment:** `/runbook` includes tier assessment — small tasks (Tier 1/2) bypass runbook creation
- **TDD process review:** After orchestration of TDD runbooks, review-tdd-process analyzes execution quality

**Progressive discovery:** Don't preload all workflow documentation. Read detailed guides only when executing that specific workflow type. Use references as needed during execution.

---

## Terminology

| Term | Definition |
|------|------------|
| **Job** | What the user wants to accomplish |
| **Design** | Architectural specification from Opus design session |
| **Phase** | Design-level segmentation for complex work |
| **Runbook** | Step-by-step implementation instructions (previously called "plan") |
| **Phase type** | `tdd` or `general` — determines expansion format and review criteria for that phase |
| **Step** | Individual unit of work within a runbook |
| **Runbook prep** | 4-point process: Evaluate, Metadata, Review, Split |

**Note on directory naming:** The `plans/` directory is a historical convention and remains unchanged. It contains runbooks, step files, and execution artifacts.

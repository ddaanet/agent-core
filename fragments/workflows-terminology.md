## Workflow Selection

**Entry point:**
- **Questions/research/discussion** → Handle directly (no workflow needed)
- **Requirements capture** → Use `/requirements` skill (extract from conversation or elicit through questions)
- **Implementation tasks** → Use `/design` skill (triages complexity, routes to appropriate workflow)
- **Workflow in progress** (check session.md) → Continue from current state

The `/design` skill includes complexity triage: simple tasks execute directly, moderate tasks skip design and route to planning, complex tasks get full design treatment.

**Progressive discovery:** Don't preload all workflow documentation. Details in design, runbook, and orchestrate skills.

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

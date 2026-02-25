# RCA Examples

Worked examples for the reflect skill's three exit paths.

---

## Unanchored Gate (Fix In-Session)

User interrupts agent that committed despite dirty submodule. Agent rationalized "only pointer matters."

- Framing block emitted
- Deviation: Agent committed parent before submodule (violated commit-rca-fixes)
- Proximal cause: Submodule check was prose instruction with no tool-call anchor — skipped in execution mode
- Classification: Unanchored gate (no Bash check before commit) + Insufficient context (submodule pattern not recalled)
- Fix: Anchor submodule check with `git submodule status` Bash call in commit skill; add submodule handling to recall-relevant entries
- Append learning, return control to user

## Upstream Input Error (Partial RCA, Handoff)

User interrupts agent implementing a step that contradicts design doc.

- Framing block emitted
- Deviation: Agent added feature X (design doc said "do not add X")
- Proximal cause: Runbook step says "add X" (contradicts design)
- Classification: Input fix (bad runbook)
- Partial RCA: Runbook author misread design
- Pending tasks: (1) Fix runbook step, (2) Resume RCA if pattern recurs
- Append learning, return control to user

## Systemic Pattern (RCA Complete, Handoff for Fixes)

User interrupts orchestrator that continued past failed step.

- Framing block emitted
- Deviation: Orchestrator rationalized "partial success is enough"
- Proximal cause: Success criteria checked structure, not behavior (test passed but wrong output)
- Contributing factors: Common pattern across multiple runbooks
- Classification: Systemic (needs fragment + memory index entry)
- RCA report written to `plans/reflect-rca-success-criteria/rca.md`
- Pending tasks: Create `agent-core/fragments/success-criteria.md`, update memory index
- Append learning, return control to user

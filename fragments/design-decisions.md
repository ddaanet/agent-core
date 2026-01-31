## Design Decision Escalation

**Rule:** When facing a design decision during any workflow phase, use `/opus-design-question` instead of asking the user.

**Applies to:** All agents during design, planning, and execution phases.

**When you encounter a choice like:**
- "Should I use approach A or B?"
- "How should this be structured?"
- "Which pattern fits better here?"
- Trade-off analysis between implementation approaches

**Do this:** Invoke `/opus-design-question` skill to get Opus architectural guidance.

**Do NOT ask the user** unless:
- The choice is subjective (user preference matters)
- It involves business logic or domain-specific knowledge
- It changes scope or requirements
- Requirements are genuinely unclear

**Why:** Design decisions that have clear architectural principles to apply should not block on user input. The `/opus-design-question` skill delegates to Opus for expert guidance, maintaining forward momentum.

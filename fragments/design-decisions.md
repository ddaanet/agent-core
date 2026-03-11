## Design Decision Escalation

**Rule:** When facing a design decision during planning or execution, resolve it yourself using architectural principles from the codebase. If you need opus-level reasoning, the user sets the model — do not delegate design decisions to a sub-agent.

**Applies to:** Agents during planning and execution phases.

**Does NOT apply to:** Design sessions (`/design` skill). Design sessions exist to make architectural decisions — the designer reasons through decisions directly.

**When you encounter a choice like:**
- "Should I use approach A or B?"
- "How should this be structured?"
- "Which pattern fits better here?"
- Trade-off analysis between implementation approaches

**Do this:** Apply architectural principles from loaded context (decisions/, fragments/, design documents). State your reasoning and choice explicitly.

**Do NOT ask the user** unless:
- The choice is subjective (user preference matters)
- It involves business logic or domain-specific knowledge
- It changes scope or requirements
- Requirements are genuinely unclear

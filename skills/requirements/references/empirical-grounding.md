# Empirical Grounding for Requirements Skill

Research findings informing the dual-mode design and interaction patterns.

## Human-AI Collaboration Pattern (HAIC)

**Finding:** 58% of practitioners use AI in requirements engineering, but only 2% believe AI can handle elicitation independently.

**Implication:** Extract + human validation model, not autonomous generation. The skill captures and structures but always presents draft for user validation.

## AI Strengths in Requirements Engineering

Research identifies where AI adds value:
- **Structuring and summarizing** existing discussions
- **Pattern recognition** for missing requirements and inconsistencies
- **Routine drafting** and documentation generation
- **Providing clarifying questions** and research augmentation

**Implication:** Extract mode is the primary value proposition — AI structures conversation into standard format.

## AI Weaknesses in Requirements Engineering

Known limitations:
- Lacks domain expertise and contextual understanding
- Cannot build stakeholder rapport or interpret non-verbal cues
- Produces overly generic outputs from generalized training
- Struggles with novel problems where requirements are uncertain

**Implication:**
- Capture Open Questions explicitly rather than inventing requirements
- Extract from conversation (grounded), don't infer unstated items
- Human validation essential (81% of practitioners use human review)

## Semi-Structured Elicitation

**Finding:** Semi-structured interviews (predetermined framework + freedom to explore tangents) most effective technique. Balances consistency of structured interviews with novel requirement capture of unstructured.

**Implication:** Elicit mode uses standard sections as framework, adaptive follow-ups based on responses (not rigid template-fill).

## Hallucination Risk

**Finding:** Hallucinations remain problematic in multi-agent RE systems. Human feedback rated LLM outputs between satisfactory and good — not excellent.

**Implication:**
- Ground extraction in actual conversation content
- Flag unknowns as Open Questions
- Maximum 3 gap-fill questions (don't interrogate)
- Always present draft for validation before writing

## Human Review and Override

**Finding:** 81% use human review of AI suggestions; 72% allow human override.

**Implication:** Gap detection presents draft → user validates → write artifact. No autonomous decision-making.

## Sources

- [AI-based Multiagent Approach for Requirements Elicitation (2024)](https://arxiv.org/html/2409.00038v1)
- [AI for Requirements Engineering: Industry Adoption (2025)](https://arxiv.org/html/2511.01324)
- [Requirements Elicitation Techniques Survey (UCBerkeley)](https://eecs481.org/readings/requirements.pdf)
- [GenAI for Requirements Engineering — Systematic Literature Review (Wiley 2026)](https://onlinelibrary.wiley.com/doi/full/10.1002/spe.70029)

Full research details: `plans/requirements-skill/reports/research-empirical.md`

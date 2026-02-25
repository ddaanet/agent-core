# Grounding Criteria

Detailed criteria for trigger assessment, quality labeling, parameter selection, and synthesis templates.

**Research foundation:** Synthesized from Double Diamond (Design Council), Rapid Review (evidence synthesis), and RAG-as-Grounding (hallucination mitigation). See `plans/reports/ground-skill-research-synthesis.md` for full research basis.

---

## Trigger Criteria

### Mandatory Grounding

External grounding is required when output makes:
- **Methodological claims** — "the best way to X is Y"
- **Framework claims** — "these are the dimensions/axes/criteria for X"
- **Best practice claims** — "established practice is to X"
- **Taxonomic claims** — "there are N types of X"

**Decision heuristic:** Does the output assert how things *should* be done, or describe how things *are* done? The former needs grounding; the latter doesn't.

### Grounding Not Required

- Project-specific logical analysis (reading code, tracing dependencies)
- Applying an already-grounded framework to data
- Mechanical execution of defined procedures
- Describing existing codebase patterns or conventions

---

## Quality Label Definitions

| Label | Criteria | Evidence requirement |
|-------|----------|---------------------|
| Strong | 2+ established frameworks found, adapted with project-specific criteria | Named sources with citation links |
| Moderate | 1 framework with partial applicability, supplemented by internal analysis | Named source + internal rationale for adaptations |
| Thin | No directly applicable framework; structural inspiration only | Document what was searched and why nothing matched |
| None | External search returned no relevant results | Search queries documented; output flagged as ungrounded |

**Label placement:** Attach at the top of the output document, immediately after the title. Format: `**Grounding:** Strong | Moderate | Thin | None`

---

## Parameterization Guide

| Parameter | Options | Selection criteria |
|-----------|---------|-------------------|
| Internal scope | codebase / conceptual | Descriptive ("what patterns exist for X") → codebase. Generative ("what dimensions/constraints apply to X") → conceptual |
| Model tier | sonnet / opus | Codebase → sonnet (scout pattern extraction). Conceptual → opus (generative divergence) |
| Research breadth | narrow (1-2) / broad (3-5) | High-stakes, novel domain, or unfamiliar territory → broad. Familiar domain with known prior art → narrow |
| Output format | reference doc / skill body / decision entry | Reusable methodology → reference doc. Encoding into procedure → skill body. One-time decision → decision entry |

**Cost awareness:** Broad + opus is the most expensive combination. Reserve for genuinely novel methodology creation. Most tasks work with narrow + sonnet.

---

## Search Query Templates

Starting patterns for the external branch. Adapt domain, topic, and year to context.

**Framework discovery:**
```
"[topic] framework" OR "[topic] methodology" established
```

**Academic grounding:**
```
"[topic] systematic review" OR "[topic] meta-analysis"
```

**Practice patterns:**
```
"[topic] best practices" [domain] 2024 2025 2026
```

**Comparison/evaluation:**
```
"[topic] comparison" OR "[topic] evaluation criteria" OR "[topic] taxonomy"
```

Templates are starting points. Refine based on initial results — if first search returns noise, narrow the domain or add qualifying terms.

---

## Process Skill Internal Sources

When the grounding topic is a **process skill** (agent workflows, decision procedures, execution patterns, skill behavior), the internal codebase branch must include git history mining alongside current file inspection.

Git history surfaces what current files cannot: failure patterns, correction cycles, and behavioral deviations that motivated rule additions. This is the highest-signal internal source for process grounding — external frameworks describe how processes *should* work, git history documents how *this* process actually fails.

**Sources to mine in Branch A for process skills:**

- `git log --oneline --all | head -200` — scan for /reflect, RCA, fix, deviat, correct in messages
- `git log --oneline --grep="reflect\|RCA\|deviat\|correct" --all` — targeted failure-pattern commits
- `agents/learnings.md` — accumulated antipatterns with evidence and root causes
- `plans/reports/workflow-grounding-audit.md` — grounding provenance for workflow skills (if present)
- `/reflect` RCA artifacts in `plans/reports/` — structured failure analyses

**Scope selector:** If topic is a process skill → use codebase scope **with git history mining**. Standard codebase scope (file inspection only) misses the failure evidence that makes process grounding credible.

---

## Convergence Template

Read both branch artifacts from `plans/reports/` before synthesizing. Required sections:

**Framework Mapping:**
- Which external framework(s) selected and why
- How internal dimensions map onto external structure
- Where mappings are tight vs loose

**Adaptations:**
- What was changed from the external framework and rationale
- Project-specific additions not present in any source
- What was deliberately excluded from the external framework and why

**Framing direction:** Each adapted principle states the general insight first, then the project implementation as instance. The external branch supplies the principle; the internal branch validates its applicability. Inverted framing (project-specific problem → external validation) produces entries that read as local fixes rather than transferable knowledge.

**Grounding Assessment:**
- Quality label (Strong/Moderate/Thin/None)
- Evidence basis for the label
- What searches were performed (queries, sources checked)
- What gaps remain

**Sources:**
- Each source with URL and retrieval context (what was extracted, how it was used)
- Distinguish primary sources (framework originators) from secondary (summaries, blog posts)

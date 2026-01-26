# Rule Management Guidelines

Comprehensive guidance for managing rules in CLAUDE.md and related documentation.

## Tiering (Critical First)

**Tier 1** (~20%, top): Violations cause immediate problems • Non-negotiable • Critical constraints
**Tier 2** (~60%, middle): Quality-important • Standard practices • Regular reference
**Tier 3** (~20%, bottom): Nice-to-have • Edge cases • Style • Optional guidance

**Rationale**: Recency bias → place must-follow rules early

Place critical rules at the top of CLAUDE.md so agents see them first. Less important guidance can appear later.

## Budgeting

**Target**: CLAUDE.md ~40-60 rules. Fewer better. Strong models → terse explanations.

**Add if:**
- Necessary? Can't combine with existing rule?
- Specific/actionable? Will agents actually follow it?

**Remove if:**
- Obsolete? Never violated?
- Redundant? Covered by another rule?
- Too vague? Not actionable?

Keep the rule set lean and focused. Every rule should earn its place.

## Maintenance

**Promote** (move to Tier 1):
- Repeated violations despite being in Tier 2/3
- Severe impacts when violated
- Steep learning curve (non-obvious)

**Demote** (move to Tier 2 or 3):
- Edge cases only
- Never violated in practice
- Obvious to strong models

**Delete**:
- Obsolete (workflow changed)
- Redundant (covered elsewhere)
- Never referenced or followed

**Refine**:
- Vague → examples (make concrete)
- Specific → generalize (broader applicability)
- Long → distill (reduce verbosity)
- Abstract → application (show usage)

## Regular Review

Periodically review CLAUDE.md:

1. Check rule violations in recent work
2. Identify rules that need promotion (frequent violations)
3. Identify rules that can be demoted or deleted (never violated)
4. Refine rules that cause confusion
5. Update examples to reflect current codebase

Maintain a living document that evolves with project needs.

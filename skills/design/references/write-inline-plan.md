## Moderate Agentic-Prose Path: Inline Plan

Reference for `plans/<job>/inline-plan.md` — execution plan for direct inline implementation on the agentic-prose Moderate path.

### Format

```markdown
## Scope
**Affected files:** [enumerated from code reading — actual paths, not brief assumptions]
**Changes:** [per-file: what changes and why]

## Boundaries
IN: [specific changes included]
OUT: [explicitly excluded]

## Dependencies
[Cross-file or external dependencies discovered during code reading]
```

### Generation Rules

- **Code reading required.** Read all affected files before writing. Brief assumptions are starting points — actual codebase state determines the artifact. The value is catching brief/codebase divergence before execution.
- **File paths from filesystem.** Enumerate actual paths using Glob/Grep, not brief assumptions. Verify files exist.
- **Per-file changes specific.** Each file entry states what section/line changes and why. Not "update SKILL.md" — "add §Routing Moderate section after §Classification Criteria."
- **Boundaries explicit.** IN/OUT section prevents scope creep during /inline execution.
- **No architecture, no options.** The design decision has already been made (it's why the job is Moderate, not Complex). Record what changes, not why the approach was chosen.

### Properties

- **Prose-only artifact.** Scope validation, not design generation.
- **No automated corrector.** Document is small — /proof (human review) catches scope issues better than pattern matching. Dispatch in /proof Corrector Dispatch table: `inline-plan.md → -- (no corrector)`.
- **Status:** `inline-planned` → `/inline plans/{plan}` (parallel to `planned` → `/orchestrate`).

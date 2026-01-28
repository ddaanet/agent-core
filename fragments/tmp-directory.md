## Temporary Files

**Use project-local `tmp/` directory, NOT system `/tmp/`**

- **CRITICAL:** All temporary files must go in `<project-root>/tmp/`, never in `/tmp/` or `/tmp/claude/`
- Rationale: Sandbox restrictions, project isolation, cleanup control
- Permission enforcement: `Write(/tmp/*)` is denied in settings.json
- For runbook execution: Use `plans/*/reports/` directory
- For ad-hoc work: Use project-local `tmp/`

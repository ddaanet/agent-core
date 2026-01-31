## Sandbox Exemptions

### Exempt Commands (use directly, no sandbox override needed)

**Rule:** When a command is in `excludedCommands` or `permissions.allow`, invoke it with the **exact prefix** that matches the exemption. Do NOT add `python3` or other interpreter prefixes — this breaks the pattern match and triggers unnecessary permission prompts.

**prepare-runbook.py:**
- Exempted in settings.json: `excludedCommands` and `permissions.allow`
- Invocation: `agent-core/bin/prepare-runbook.py <runbook>` (has shebang, runs directly)
- Do NOT use: `python3 agent-core/bin/prepare-runbook.py` (breaks exemption match)

### Commands Requiring `dangerouslyDisableSandbox: true`

**General pattern:**
- Commands writing to `.claude/` directory (except `.claude/debug/`)
- Commands writing to system config locations
- Commands requiring network access to non-whitelisted hosts

**Settings exemption (persistent):**
Add to `.claude/settings.json` `excludedCommands` array, then invoke with matching prefix.

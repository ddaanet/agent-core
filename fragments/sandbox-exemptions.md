## Sandbox Exemptions

**Commands requiring `dangerouslyDisableSandbox: true`**

These commands write to paths outside the sandbox allowlist and must run with sandbox disabled:

**prepare-runbook.py:**
- Writes to `.claude/agents/[plan-name]-task.md`
- Already configured in `excludedCommands` in settings.json
- Used by plan-tdd and plan-adhoc skills

**General pattern:**
- Commands writing to `.claude/` directory (except `.claude/debug/`)
- Commands writing to system config locations
- Commands requiring network access to non-whitelisted hosts

**How to use:**
```python
{
  "command": "python scripts/prepare-runbook.py ...",
  "description": "Generate runbook artifacts",
  "dangerouslyDisableSandbox": true
}
```

**Settings exemption (persistent):**
Add to `.claude/settings.json`:
```json
{
  "excludedCommands": [
    "python scripts/prepare-runbook.py"
  ]
}
```

This avoids the failed-call → retry cycle for known sandbox-sensitive commands.

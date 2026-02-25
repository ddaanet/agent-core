# Good/Bad Examples by Artifact Type

Examples for plugin-dev-validation review criteria.

---

## Skills

**Good frontmatter:**
```yaml
---
name: commit
description: Create git commits with multi-line messages and gitmoji selection
user-invocable: true
allowed-tools: Bash, Read, Grep, Skill
---
```

**Bad frontmatter (missing user-invocable):**
```yaml
---
name: commit
description: Commit tool
---
```

**Good progressive disclosure:**
```markdown
## When to Use
[simple trigger conditions]

## Quick Start
[basic usage example]

## Advanced Patterns
[edge cases, complex scenarios]
```

**Bad structure (dump all content):**
```markdown
# Skill Name

[3000 words of mixed content without organization]
```

---

## Agents

**Good frontmatter:**
```yaml
---
name: corrector
description: |
  Review agent that applies all fixes directly.
  Reviews changes, writes report, applies all fixes (critical, major, minor),
  then returns report filepath.

  Usage: delegate to corrector
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---
```

**Bad frontmatter (vague description):**
```yaml
---
name: review
description: Reviews code
model: sonnet
tools: []
---
```

---

## Hooks

**Good security pattern:**
```python
ALLOWED = {"git restore", "git checkout"}
if command in ALLOWED:
    # Allow
```

**Bad security (exploitable):**
```python
if command.startswith("git restore"):
    # Exploitable: "git restore && rm -rf /"
```

**Good error output:**
```bash
if [[ invalid ]]; then
    >&2 echo "Operation blocked: reason"
    exit 2
fi
```

**Bad error (wrong stream/code):**
```bash
echo "Error" # stdout, not stderr
exit 1       # wrong exit code
```

---

## Commands

**Good command frontmatter:**
```yaml
---
name: deploy
description: Deploy application to environment
arguments:
  - name: environment
    type: string
    required: true
    description: Target environment (dev/staging/prod)
---
```

**Bad frontmatter (missing args):**
```yaml
---
name: deploy
description: Deploys stuff
---
```

---

## Plugin Structure

**Good plugin.json:**
```json
{
  "description": "Plugin for X functionality",
  "hooks": {
    "PreToolUse": [...]
  },
  "skills": [...],
  "version": "1.0.0"
}
```

**Bad plugin.json (missing description):**
```json
{
  "hooks": {...}
}
```

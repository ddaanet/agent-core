---
name: plugin-dev-validation
description: Domain validation criteria for plugin components. Consumed by vet-fix-agent during artifact review.
user-invocable: false
---

# Plugin Development Validation

Review criteria for Claude Code plugin components. This skill is consumed by vet-fix-agent during artifact review, not invoked interactively.

## Scope

**Artifact types covered:**
- Skills (`.claude/skills/**/SKILL.md`, `agent-core/skills/**/SKILL.md`)
- Agents (`.claude/agents/*.md`)
- Hooks (`.claude/hooks/*.{sh,py}`, `.claude/settings.json` hook configuration)
- Commands (`.claude/commands/**/*`)
- Plugin structure (`plugin.json`, directory layout)

**Path patterns:**
- `.claude/plugins/**/*`
- `.claude/skills/**/*`
- `.claude/agents/**/*`
- `.claude/hooks/**/*`
- `agent-core/skills/**/*`
- `agent-core/agents/**/*`

---

## Review Criteria by Artifact Type

### Skills

**Critical:**

- **Valid frontmatter:** YAML block with required fields (name, description)
  - `name` field must match directory name
  - `description` field must be concise (1-2 sentences)
  - `user-invocable` field required (true/false)
  - Rationale: Frontmatter enables skill discovery and invocation

- **Progressive disclosure:** Content organized from simple to complex
  - Start with "When to Use" or "Purpose"
  - Core patterns before edge cases
  - Examples before full specifications
  - Rationale: Users discover incrementally, not all-at-once

- **Imperative form:** Instructions use imperative verbs (Read, Write, Invoke, Check)
  - ✅ "Read the design document"
  - ❌ "The design document should be read"
  - Rationale: Direct commands reduce ambiguity

**Major:**

- **Triggering conditions:** Clear "When to Use" section
  - Explicit conditions (file patterns, task types, user requests)
  - Counter-conditions ("Do NOT use when...")
  - Rationale: Prevents skill misapplication

- **Lean SKILL.md:** Main skill file focuses on protocol, detailed guidance in subdirectories
  - Target 500-1500 words for main SKILL.md
  - Move detailed examples to `examples/`, patterns to `patterns/`
  - Rationale: Token economy, progressive disclosure

**Minor:**

- **Consistent formatting:** Headings, lists, code blocks follow project style
- **No duplicate content:** Cross-references instead of copying content
- **Clear section boundaries:** H2/H3 structure with logical grouping

**Good/Bad Examples:**

✅ **Good frontmatter:**
```yaml
---
name: commit
description: Create git commits with multi-line messages and gitmoji selection
user-invocable: true
allowed-tools: Bash, Read, Grep, Skill
---
```

❌ **Bad frontmatter (missing user-invocable):**
```yaml
---
name: commit
description: Commit tool
---
```

✅ **Good progressive disclosure:**
```markdown
## When to Use
[simple trigger conditions]

## Quick Start
[basic usage example]

## Advanced Patterns
[edge cases, complex scenarios]
```

❌ **Bad structure (dump all content):**
```markdown
# Skill Name

[3000 words of mixed content without organization]
```

---

### Agents

**Critical:**

- **Valid frontmatter:** YAML with name (3-50 chars), description with examples, model, color, tools
  - `name`: 3-50 characters, hyphen-separated
  - `description`: Multi-line with usage examples
  - `model`: sonnet|opus|haiku
  - `color`: Valid color name
  - `tools`: Array of tool names
  - Rationale: Frontmatter enables agent discovery and configuration

- **Tool access specification:** `tools` array lists only necessary tools
  - Review agents: Read, Write, Edit, Bash, Grep, Glob
  - Execution agents: May include Write, Edit for artifact creation
  - Rationale: Principle of least privilege

**Major:**

- **System prompt clarity:** Agent body clearly states role, responsibilities, constraints
  - Explicit role statement ("You are a code review agent...")
  - Clear boundaries (what agent does vs doesn't do)
  - Rationale: Prevents scope drift

- **Triggering examples:** Description includes invocation patterns
  - Example: "delegate to vet-fix-agent"
  - Example: "use tdd-plan-reviewer for TDD runbooks"
  - Rationale: Helps orchestrators discover correct agent

**Minor:**

- **Color consistency:** Related agents use related colors (all review agents cyan)
- **Naming convention:** Agent names end with `-agent` or `-task`

**Good/Bad Examples:**

✅ **Good frontmatter:**
```yaml
---
name: vet-fix-agent
description: |
  Vet review agent that applies all fixes directly.
  Reviews changes, writes report, applies all fixes (critical, major, minor),
  then returns report filepath.

  Usage: delegate to vet-fix-agent
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---
```

❌ **Bad frontmatter (vague description):**
```yaml
---
name: vet
description: Reviews code
model: sonnet
tools: []
---
```

---

### Hooks

**Critical:**

- **Security:** Exact match for allowed operations, not `startswith()`
  - ✅ `command in allowed_commands`
  - ❌ `command.startswith(allowed_prefix)`
  - Rationale: Shell operators (&&, ;, ||) can chain commands

- **Valid event types:** PreToolUse, PostToolUse, UserPromptSubmit, SessionStart
  - Check hook script references valid event
  - Rationale: Invalid events never fire

- **Error output to stderr:** Blocking hooks must write to stderr and exit 2
  - ✅ `>&2 echo "Error message"; exit 2`
  - ❌ `echo "Error message"; exit 1`
  - Rationale: Claude Code expects stderr + exit 2 for deny decisions

**Major:**

- **Matcher patterns:** PreToolUse hooks specify tool matcher (Bash, Write, Edit)
  - Check settings.json or plugin.json for matcher field
  - Rationale: Hooks without matcher fire for all tools (performance issue)

- **Output format:** Hooks use hookSpecificOutput for structured data
  - `additionalContext` for context injection
  - `systemMessage` for user-visible messages
  - Rationale: Structured output prevents transcript pollution

**Minor:**

- **Script permissions:** Hook scripts have execute bit (`chmod +x`)
- **Shebang present:** Scripts start with `#!/usr/bin/env bash` or `#!/usr/bin/env python3`

**Good/Bad Examples:**

✅ **Good security pattern:**
```python
ALLOWED = {"git restore", "git checkout"}
if command in ALLOWED:
    # Allow
```

❌ **Bad security (exploitable):**
```python
if command.startswith("git restore"):
    # Exploitable: "git restore && rm -rf /"
```

✅ **Good error output:**
```bash
if [[ invalid ]]; then
    >&2 echo "Operation blocked: reason"
    exit 2
fi
```

❌ **Bad error (wrong stream/code):**
```bash
echo "Error" # stdout, not stderr
exit 1       # wrong exit code
```

---

### Commands

**Critical:**

- **Valid YAML frontmatter:** Command definition with name, arguments, description
  - Required: name, description
  - Optional: arguments (array of arg definitions)
  - Rationale: Commands.json parses frontmatter for discovery

- **Executable script:** Command script exists and has execute permissions
  - Check shebang line present
  - Check file mode includes +x
  - Rationale: Non-executable commands fail silently

**Major:**

- **Argument structure:** If command accepts arguments, frontmatter declares them
  - Each argument has: name, type, description
  - Optional vs required clearly marked
  - Rationale: Enables argument validation and help generation

**Minor:**

- **Consistent naming:** Command names use kebab-case
- **Help text:** Command includes --help flag with usage info

**Good/Bad Examples:**

✅ **Good command frontmatter:**
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

❌ **Bad frontmatter (missing args):**
```yaml
---
name: deploy
description: Deploys stuff
---
```

---

### Plugin Structure

**Critical:**

- **Valid plugin.json:** Root manifest with description and hooks/skills/agents
  - Required: description field
  - Optional: hooks, skills, agents (arrays or objects)
  - Rationale: Claude Code requires valid JSON for plugin loading

- **Directory layout:** Standard structure (skills/, agents/, hooks/)
  - Skills in `skills/skill-name/SKILL.md`
  - Agents in `agents/agent-name.md`
  - Hooks in `hooks/hook-name.{sh,py}`
  - Rationale: Auto-discovery relies on conventional paths

**Major:**

- **No broken symlinks:** All symlinks resolve to valid targets
  - Check `.claude/agents/`, `.claude/skills/` symlinks
  - Rationale: Broken symlinks cause silent discovery failures

- **Frontmatter consistency:** All artifacts have required frontmatter fields
  - Skills: name, description, user-invocable
  - Agents: name, description, model, color, tools
  - Rationale: Discovery mechanism depends on frontmatter

**Minor:**

- **README present:** Plugin directory includes README.md with usage
- **Version tracking:** plugin.json includes version field

**Good/Bad Examples:**

✅ **Good plugin.json:**
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

❌ **Bad plugin.json (missing description):**
```json
{
  "hooks": {...}
}
```

---

## Alignment Criteria

**What "correct" means for each artifact type:**

**Skills:**
- Skill enables user/agent to accomplish stated purpose
- Instructions are unambiguous and executable
- Examples demonstrate common use cases
- Progressive disclosure supports incremental learning

**Agents:**
- Agent behavior matches description
- Tool access matches responsibilities
- System prompt provides clear protocol
- Triggering conditions are discoverable

**Hooks:**
- Hook fires at correct event
- Security constraints prevent exploitation
- Output format matches Claude Code expectations
- Performance impact is acceptable (matcher prevents over-firing)

**Commands:**
- Command executes successfully with declared arguments
- Help text guides users to correct usage
- Error messages are actionable

**Plugin structure:**
- All components discoverable via auto-discovery
- No silent failures from broken paths or invalid JSON
- Symlinks resolve correctly

**How to verify alignment:**

1. **Functional test:** Can the artifact be used as intended?
2. **Discovery test:** Does Claude Code discover and load the artifact?
3. **Integration test:** Does artifact work with related components?
4. **Security test:** Are there exploitable patterns (hooks especially)?

### Verification Procedures

**For vet-fix-agent performing alignment verification:**

**Skills verification:**
1. Check "When to Use" or "Purpose" section exists and is clear
2. Verify examples demonstrate stated purpose
3. Check progressive disclosure (simple before complex)
4. Confirm imperative form in instructions

**Agents verification:**
1. Compare frontmatter description to system prompt body
2. Verify tool list matches responsibilities in system prompt
3. Check triggering examples in description
4. Confirm model tier matches complexity (haiku=execution, sonnet=balanced, opus=architecture)

**Hooks verification:**
1. Check event type is valid (PreToolUse, PostToolUse, UserPromptSubmit, SessionStart)
2. Verify security patterns (exact match not startswith for commands)
3. Test error output format (stderr + exit 2)
4. Check matcher exists for PreToolUse hooks (performance)

**Commands verification:**
1. Check YAML frontmatter parses correctly
2. Verify script exists and is executable (shebang + +x)
3. Compare frontmatter arguments to script usage
4. Check help text exists (--help flag)

**Plugin structure verification:**
1. Parse plugin.json for validity
2. Check directory structure matches conventions
3. Verify symlinks resolve (test with readlink or equivalent)
4. Confirm all referenced artifacts exist

**Alignment check against design/requirements:**

If task prompt includes design document or requirements context:
1. Read design/requirements to understand intended behavior
2. Check implementation matches design decisions (algorithms, patterns, structure)
3. Verify functional requirements are satisfied
4. Flag gaps as major issues

**Escalation criteria:**

If verification reveals the artifact fundamentally doesn't serve its stated purpose, mark as UNFIXABLE with explanation. Alignment issues that require architectural rework cannot be fixed via edits.

---

## Fix Procedures

### Fixable Issues

**What vet-fix-agent can fix directly:**

- **Missing frontmatter fields:** Add required fields with sensible defaults
  - `user-invocable: true` for skills (can be adjusted)
  - `model: sonnet` for agents (common default)
  - `tools: []` for agents (minimal set)

- **Format issues:** Heading structure, list formatting, code block markers
  - Convert prose to bulleted lists
  - Fix heading levels (H2 → H3 when nested)
  - Add missing code block language tags

- **Imperative form:** Convert passive voice to imperative
  - "The file should be read" → "Read the file"

- **Security patterns (hooks):** Replace `startswith()` with exact match
  - Rewrite condition to use `in` check with set/list

- **Progressive disclosure:** Reorder sections to simple-first
  - Move "When to Use" before "Advanced Patterns"
  - Extract examples to separate section

- **Lean skill content:** Move detailed content to subdirectories
  - Create `examples/` or `patterns/` subdirectories
  - Move content, replace with cross-reference

### Unfixable Issues (Escalate)

**What requires human decision:**

- **Missing purpose/goal:** Skill or agent lacks clear statement of what it does
  - Escalation: "UNFIXABLE: Cannot infer purpose from content. Add explicit purpose statement."

- **Tool access ambiguity:** Agent needs tools not in allowed list, or has unnecessary tools
  - Escalation: "UNFIXABLE: Agent behavior requires [tool] but frontmatter doesn't include it. Verify tool access matches responsibilities."

- **Security vulnerability (complex):** Hook pattern exploitable in non-obvious ways
  - Escalation: "UNFIXABLE: Hook security pattern may be vulnerable. Manual security review required."

- **Broken references:** Skill references non-existent files or agents
  - Escalation: "UNFIXABLE: References [path] which doesn't exist. Verify paths or remove references."

- **Architectural issues:** Agent responsibilities overlap with existing agents
  - Escalation: "UNFIXABLE: Agent duplicates responsibilities of [existing-agent]. Clarify scope or consolidate."

### Fix Priority

1. **Critical first:** Frontmatter validity, security issues
2. **Major next:** Triggering conditions, tool access
3. **Minor last:** Formatting, naming conventions

### Fix Constraints

- **Preserve intent:** Don't change what the artifact does, only how it's expressed
- **No scope creep:** Fix identified issues only, don't refactor surrounding content
- **Minimal edits:** Change as little as possible to resolve issue

---

## Integration with Vet Workflow

**How this skill is used:**

1. **Planner detects domain:** Planning-time detection via rules files or design doc mentions
2. **Planner writes vet step:** Runbook vet checkpoint includes reference to this skill + artifact type
3. **Orchestrator delegates:** Task prompt includes: "Read and apply criteria from `agent-core/skills/plugin-dev-validation/SKILL.md` for artifact type: [skills|agents|hooks|commands|plugin-structure]"
4. **Vet-fix-agent reads skill:** Loads criteria for specified artifact type
5. **Vet-fix-agent reviews:** Applies generic + alignment + domain criteria
6. **Vet-fix-agent fixes:** All fixable issues (critical, major, minor)
7. **Vet-fix-agent reports:** Writes review report with fix status, escalates UNFIXABLE

**No changes to vet-fix-agent protocol:** This skill provides enriched criteria; vet-fix-agent applies them using existing review process.

---

## Usage Notes

**For planners:**
- Reference this skill in vet checkpoint steps when planning plugin development work
- Specify artifact type (skills, agents, hooks, commands, plugin-structure) for targeted review
- This skill is additive — generic quality + alignment checks still apply

**For vet-fix-agent:**
- Read this skill when task prompt references it
- Apply criteria for specified artifact type
- Use fix procedures to determine fixable vs UNFIXABLE
- Report all findings, fix all fixable issues, escalate UNFIXABLE

**For users:**
- This skill is NOT user-invocable (consumed by vet-fix-agent)
- For interactive plugin review, use dedicated review agents (skill-reviewer, plugin-validator)
- For validation workflow questions, see `agent-core/fragments/vet-requirement.md`

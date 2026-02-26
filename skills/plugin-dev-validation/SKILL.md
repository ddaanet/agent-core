---
name: plugin-dev-validation
description: Domain validation criteria for plugin components. Consumed by corrector during artifact review.
user-invocable: false
---

# Validate Plugin Components During Review

Review criteria for Claude Code plugin components. This skill is consumed by corrector during artifact review, not invoked interactively.

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

See `references/examples-per-type.md` Skills section for good/bad examples.

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
  - Example: "delegate to corrector"
  - Example: "use runbook-corrector for runbook review"
  - Rationale: Helps orchestrators discover correct agent

**Minor:**

- **Color consistency:** Related agents use related colors (all review agents cyan)
- **Naming convention:** Agent names end with `-agent` or `-task`

See `references/examples-per-type.md` Agents section for good/bad examples.

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

See `references/examples-per-type.md` Hooks section for good/bad examples.

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

See `references/examples-per-type.md` Commands section for good/bad examples.

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

See `references/examples-per-type.md` Plugin Structure section for good/bad examples.

---

## Fix Procedures

### Fixable Issues

**What corrector can fix directly:**

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

## Integration with Review Workflow

**How this skill is used:**

1. **Planner detects domain:** Planning-time detection via rules files or design doc mentions
2. **Planner writes review step:** Runbook review checkpoint includes reference to this skill + artifact type
3. **Orchestrator delegates:** Task prompt includes: "Read and apply criteria from `agent-core/skills/plugin-dev-validation/SKILL.md` for artifact type: [skills|agents|hooks|commands|plugin-structure]"
4. **Corrector reads skill:** Loads criteria for specified artifact type
5. **Corrector reviews:** Applies generic + alignment + domain criteria
6. **Corrector fixes:** All fixable issues (critical, major, minor)
7. **Corrector reports:** Writes review report with fix status, escalates UNFIXABLE

**No changes to corrector protocol:** This skill provides enriched criteria; corrector applies them using existing review process.


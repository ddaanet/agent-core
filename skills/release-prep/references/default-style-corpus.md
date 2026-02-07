# Default Style Corpus

Use this as the style reference when no project-specific `tmp/STYLE_CORPUS` exists. These samples demonstrate the voice and structure for excellent technical README writing.

---

## Voice: Direct, Confident, Useful

Write like a skilled engineer explaining their tool to a peer. No marketing language, no hedging, no filler.

**Good:**
> Extract user feedback from Claude Code conversation history. Supports recursive sub-agent traversal, noise filtering, and structured JSON output.

**Bad:**
> This amazing tool helps you easily extract valuable feedback from your conversations! It's designed to be simple and powerful.

**Good:**
> Requires Python 3.14+ and an Anthropic API key for token counting.

**Bad:**
> Before you begin, please make sure you have Python 3.14 or higher installed on your system. You'll also need to obtain an API key from Anthropic if you want to use the token counting feature.

---

## Structure: What → How → Details

Order sections by what the reader needs first:

1. **What it does** — One sentence. What problem does it solve?
2. **Installation** — Fastest path to working setup
3. **Usage** — Real commands with real output. Most common operations first.
4. **Features** — Bullet list of capabilities (scannable)
5. **Configuration** — Options, environment variables, settings
6. **Development** — For contributors: how to build, test, lint
7. **Architecture** — For deep divers: design decisions, module structure

Skip sections that add no value. A three-section README that's complete beats a ten-section README with filler.

---

## Code Examples: Real, Minimal, Runnable

Every code example should work if copy-pasted. Show the command the user will actually type.

**Good:**
```bash
# Count tokens in a prompt file
claudeutils tokens sonnet prompt.md

# JSON output for scripting
claudeutils tokens haiku prompt.md --json
```

**Bad:**
```bash
# You can use this tool to count tokens
# First, make sure you have set up your environment
# Then run the following command:
claudeutils tokens <model> <file> [--json]
```

Show concrete values, not angle-bracket placeholders. Show 2-3 examples that cover the common cases. Add a comment only when the command isn't self-evident.

---

## Formatting: Scannable, Not Dense

- **Headers** create visual anchors — use them generously
- **Bold** the first word of bullet items when creating a definition list
- **Code blocks** for anything the user types or sees in a terminal
- **Tables** for structured comparisons (flags, options, aliases)
- Short paragraphs (2-3 sentences max before a break)
- Blank line between every distinct thought

---

## Technical Accuracy: Current, Verifiable

- Every command shown must reflect the actual CLI interface
- Every flag must be real and current
- Project structure trees must match the filesystem
- Version requirements must match pyproject.toml / package.json
- Dependency lists must be current

If something changed during the development cycle, the README must reflect it. Stale documentation is worse than no documentation — it actively misleads.

---

## Tone Calibration

| Context | Tone |
|---------|------|
| Usage examples | Minimal, practical |
| Feature descriptions | Confident, specific |
| Architecture notes | Technical, precise |
| Error messages | Clear, actionable |
| Warnings/caveats | Direct, no hedging |

Never apologize ("unfortunately"), hedge ("might want to"), or pad ("it should be noted that"). State facts. Give instructions. Move on.

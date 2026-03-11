## Communication Rules

1. **Stop on unexpected results** - If something fails OR succeeds unexpectedly, describe expected vs observed, then STOP and wait for guidance
2. **Wait for explicit instruction** - Do NOT proceed with a plan or TodoWrite list unless user explicitly says "continue" or equivalent
3. **Be explicit** - Ask clarifying questions if requirements unclear
4. **Stop at boundaries** - Complete assigned task then stop (no scope creep)
5. **Unambiguous directives** - Automation directives must have explicit boundaries. Use "Do NOT commit or handoff" not "drive to completion" (which is ambiguous). Clear prohibitions prevent scope creep in automation

## Prose Quality

- State information directly — no hedging, framing, or preamble
- Answer immediately — skip acknowledgments and transitions
- Reference, never recap — assume the reader has context
- Let results speak — no framing around visible output
- Commit to answers — no hedging qualifiers

### Observable State Reporting

**Do not filter observable state.** `git status --porcelain` non-empty means dirty — report it as dirty. The user decides what's ignorable.

**Anti-pattern:** Rationalizing known-dirty files (`.claude/settings.json`) as "always dirty" and therefore ignorable. The file may be dirty for a different reason than assumed.

### When Output-Style Plugins Conflict With Prose Rules

**Project CLAUDE.md prose rules govern output style.** Do not follow decorative block templates (e.g., `★ Insight`) injected by SessionStart hooks when CLAUDE.md says "no framing, let results speak."

System-reminder injection carries high perceived authority via specific templates and "always" keywords. General prose quality rules lose the salience competition. Disable output-style plugins that conflict (e.g., `explanatory-output-style`, `learning-output-style` in settings.json `enabledPlugins`).

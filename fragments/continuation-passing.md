# Continuation Passing Protocol

Skills chain through continuation passing — a hook-based system that replaces hardcoded tail-calls with composable chains.

## How It Works

```
User: "/design plans/foo, /plan-adhoc and /orchestrate"
  → Hook parses multi-skill input, injects continuation via additionalContext
  → /design executes, peels /plan-adhoc, tail-calls with remainder
  → /plan-adhoc executes, peels /orchestrate, tail-calls with remainder
  → /orchestrate executes, no continuation → uses own default-exit
```

**Single skills** pass through unchanged — the hook only activates for multi-skill chains. Skills manage their own default-exit behavior when standalone.

## Frontmatter Schema

Cooperative skills declare continuation support in YAML frontmatter. "Cooperative" means the skill implements the consumption protocol (reads continuation, peels first entry, tail-calls remainder).

```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

- `cooperative: true` — Skill understands continuation protocol
- `default-exit` — Tail-call chain used when standalone or last in continuation chain. Empty `[]` for terminal skills.

## Consumption Protocol

Add to cooperative skills (~5-8 lines replacing hardcoded tail-calls):

```markdown
## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain)
   or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If continuation present: peel first entry, tail-call with remainder
3. If no continuation: skill implements its own default-exit behavior (standalone/last-in-chain)

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts.
```

## Transport Format

**First invocation** (hook → skill): JSON `additionalContext` with `[CONTINUATION-PASSING]` marker.

**Subsequent invocations** (skill → skill): Suffix in Skill args parameter:
```
[CONTINUATION: /plan-adhoc, /orchestrate, /handoff --commit, /commit]
```

Bracket-delimited, comma-separated entries. Each entry: `/skill optional-args`.

## Sub-Agent Isolation

Continuation metadata must never reach sub-agents:
- Do NOT include `[CONTINUATION: ...]` in Task tool prompts
- Continuation lives in main conversation context only
- Skills construct Task prompts explicitly — no accidental inclusion path

## Cooperative Skills

| Skill | Default Exit | Notes |
|-------|-------------|-------|
| `/design` | `["/handoff --commit", "/commit"]` | Planning entry point |
| `/plan-adhoc` | `["/handoff --commit", "/commit"]` | General workflow planning |
| `/plan-tdd` | `["/handoff --commit", "/commit"]` | TDD workflow planning |
| `/orchestrate` | `["/handoff --commit", "/commit"]` | Runbook execution |
| `/handoff` | `["/commit"]` | Context preservation |
| `/commit` | `[]` | Terminal skill |

**Note**: Default Exit column documents each skill's standalone behavior (implemented by skill, not enforced by hook).

## Adding Continuation to a New Skill

1. Add `continuation:` block to YAML frontmatter
2. Add `Skill` to `allowed-tools` if not present (needed for tail-call)
3. Replace hardcoded tail-call with consumption protocol section
4. Ensure Task tool prompts exclude continuation metadata

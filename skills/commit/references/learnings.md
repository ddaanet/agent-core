# Commit Skill Learnings

Accumulated patterns and best practices for commit workflow.

## Multiline Commit Messages in Bash

**Anti-pattern:** Using `"...\n..."` for multiline git commit messages (backslash-n not interpreted by bash).

**Correct pattern:** Use heredoc syntax (preferred) or literal newlines in double quotes:

```bash
# Heredoc (preferred for clean formatting)
git commit -m "$(cat <<'EOF'
Title

- Detail 1
- Detail 2
EOF
)"

# Alternative: literal newlines in double quotes
git commit -m "Title

- Detail 1
- Detail 2"
```

**Issue:** Opus blindly followed buggy skill instruction despite knowing correct syntax.

**Root cause:** Uncritical compliance with prescriptive skill instruction over model knowledge.

**Rationale:** Bash interprets literal newlines in double quotes; backslash-n requires echo -e or printf.

**Impact:** Skill instructions should demonstrate working syntax, not prescribe broken patterns.

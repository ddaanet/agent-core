### Task Agent Tool Usage

**Rule:** Task agents must use specialized tools, not Bash one-liners.

**When delegating tasks, remind agents to:**

- Use **LS** instead of `ls`
- Use **Grep** instead of `grep` or `rg`
- Use **Glob** instead of `find`
- Use **Read** instead of `cat`, `head`, `tail`
- Use **Write** instead of `echo >` or `cat <<EOF`
- Use **Edit** instead of `sed`, `awk`

**Critical:** Always include this reminder in task prompts to prevent bash tool misuse.

# Claude Code environment setup — sourced by .envrc
# Shared across all projects using agent-core

# Load claude-env and model overrides (managed by claudeutils)
watch_file ~/.claude/claude-env
dotenv_if_exists ~/.claude/claude-env
watch_file ~/.claude/claude-model-overrides
dotenv_if_exists ~/.claude/claude-model-overrides

# Project-local tmp directory for Claude Code sandbox
# Prevents "operation not permitted: /tmp/claude-501/cwd-*" errors
export CLAUDE_CODE_TMPDIR="$PWD/tmp/claude"
mkdir -p "$CLAUDE_CODE_TMPDIR"

# Fix zsh heredoc in sandbox: zsh uses TMPPREFIX (not TMPDIR) for heredoc temp files
export TMPPREFIX="${TMPDIR:-/tmp}/zsh"

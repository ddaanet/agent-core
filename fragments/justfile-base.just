# Base justfile recipes for agent projects
# This file is extracted and composed into project-specific justfiles
#
# Template variables for project customization:
#   SRC_DIR - directory containing source code (usually 'src')
#   TEST_DIR - directory containing tests (usually 'tests')
#   VENV - path to virtual environment (usually '.venv')

# Sandbox detection for Claude Code environment
# When in Claude Code sandbox, uv run crashes on system config access
[private]
sandboxed := shell('[ -w /tmp ] && echo "0" || echo "1"')

# Conditional tool invocation based on sandbox status
[private]
_sync := if sandboxed == "1" { '' } else { 'uv sync -q' }
[private]
_pytest := if sandboxed == "1" { '{{VENV}}/bin/pytest' } else { "uv run pytest" }
[private]
_ruff := if sandboxed == "1" { '{{VENV}}/bin/ruff' } else { "uv run ruff" }
[private]
_mypy := if sandboxed == "1" { '{{VENV}}/bin/mypy' } else { "uv run mypy" }

# Bash helper definitions for consistent output formatting
[private]
_bash-defs := '''
COMMAND="''' + style('command') + '''"
ERROR="''' + style('error') + '''"
GREEN=$'\033[32m'
NORMAL="''' + NORMAL + '''"
safe () { "$@" || status=false; }
end-safe () { ${status:-true}; }
show () { echo "$COMMAND$*$NORMAL"; }
visible () { show "$@"; "$@"; }
fail () { echo "${ERROR}$*${NORMAL}" >&2; exit 1; }
'''

# Display available recipes
help:
    just --list --unsorted

# Development workflow: run all checks (format, check, test)
[no-exit-message]
dev: format check test

# Run test suite with optional arguments
[no-exit-message]
test *ARGS:
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    {{ _sync }}
    {{ _pytest }} {{ ARGS }}

# Format code with ruff and docformatter
format:
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    {{ _sync }}
    tmpfile=$(mktemp tmp-fmt-XXXXXX)
    trap "rm $tmpfile" EXIT
    patch-and-print() {
        patch "$@" | sed -Ene "/^patching file '/s/^[^']+'([^']+)'/\\1/p"
    }
    {{ _ruff }} check -q --fix-only --diff | patch-and-print >> "$tmpfile" || true
    {{ _ruff }} format -q --diff | patch-and-print >> "$tmpfile" || true
    # docformatter --diff applies the change *and* outputs the diff, so we need to
    # reverse the patch (-R) and dry run (-C), and it prefixes the path with before and
    # after (-p1 ignores the first component of the path). Hence `patch -RCp1`.
    docformatter --diff {{SRC_DIR}} {{TEST_DIR}} | patch-and-print -RCp1 >> "$tmpfile" || true

    modified=$(sort --unique < "$tmpfile")
    if [ -n "$modified" ] ; then
        bold=$'\033[1m'; nobold=$'\033[22m'
        red=$'\033[31m'; resetfg=$'\033[39m'
        echo "${bold}${red}**Reformatted files:**"
        echo "$modified" | sed "s|^|${bold}${red}  - ${nobold}${resetfg}|"
    fi

# Check code style without modifying files
[no-exit-message]
check:
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    {{ _sync }}
    show "# ruff check"
    safe {{ _ruff }} check -q
    show "# docformatter -c"
    safe docformatter -c {{SRC_DIR}} {{TEST_DIR}}
    show "# mypy"
    safe {{ _mypy }}
    end-safe

# Format, check with complexity disabled, test (lint recipe)
[no-exit-message]
lint: format
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    {{ _sync }}
    show "# ruff check"
    safe {{ _ruff }} check -q --ignore=C901
    show "# docformatter -c"
    safe docformatter -c {{SRC_DIR}} {{TEST_DIR}}
    show "# mypy"
    safe {{ _mypy }}
    show "# pytest"
    safe {{ _pytest }} -q
    end-safe

# Ruff auto-fix (safe fixes only)
[no-exit-message]
ruff-fix:
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    {{ _sync }}
    show "# ruff check --fix"
    safe {{ _ruff }} check --fix {{SRC_DIR}} {{TEST_DIR}}
    end-safe

# Compile Python files (quick syntax validation)
[no-exit-message]
compile:
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    {{ _sync }}
    show "# python -m compileall"
    safe python -m compileall -q {{SRC_DIR}} {{TEST_DIR}}
    end-safe

# Role: code - verify tests pass
[group('roles')]
[no-exit-message]
role-code *ARGS: (test ARGS)

# Role: lint - format and verify all checks pass (no complexity)
[group('roles')]
[no-exit-message]
role-lint: lint

# Role: refactor - full development cycle
[group('roles')]
[no-exit-message]
role-refactor: dev

# Fail if CLAUDECODE is set (prevents recipes from running in agent context)
[no-exit-message]
[private]
_fail_if_claudecode:
    #!/usr/bin/env bash -euo pipefail
    if [ "${CLAUDECODE:-}" != "" ]; then
        echo -e '{{ style("error") }}⛔️ Denied: Protected recipe{{ NORMAL }}'
        exit 1
    fi

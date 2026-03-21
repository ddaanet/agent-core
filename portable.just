# Portable justfile module — distributed with edify plugin
# Import in consuming projects: import 'portable.just'
# Variables merge across import boundaries; root justfile's bash_prolog overrides this one.

# Self-contained bash prolog for portable module (cannot rely on root justfile's bash_prolog)
bash_prolog := "/usr/bin/env bash\nset -euo pipefail\n" + '''
export PATH="$PWD/node_modules/.bin:$PATH"
RED=$'\033[31m'
GREEN=$'\033[32m'
NORMAL=$'\033[0m'
COMMAND=$'\033[1m'
ERROR=$'\033[1;31m'
HEADER_STYLE=$'\033[1;36m'
safe () { "$@" || status=false; }
end-safe () { ${status:-true}; }
show () { echo "$COMMAND$*$NORMAL"; }
visible () { show "$@"; "$@"; }
fail () { echo "${RED}FAIL: $*${NORMAL}" >&2; exit 1; }
wt-path() {
    local parent
    parent="$(cd .. && basename "$PWD")"
    if [[ "$parent" == *-wt ]]; then
        echo "$(cd .. && pwd)/$1"
    else
        echo "$(cd .. && pwd)/$(basename "$PWD")-wt/$1"
    fi
}
add-sandbox-dir() {
    local dir="$1" settings="$2"
    mkdir -p "$(dirname "$settings")"
    python3 -c "
import json, sys, os
path = sys.argv[1]
settings_file = sys.argv[2]
data = {}
if os.path.exists(settings_file):
    with open(settings_file) as f:
        data = json.load(f)
dirs = data.setdefault('permissions', {}).setdefault('additionalDirectories', [])
if path not in dirs:
    dirs.append(path)
    with open(settings_file, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
" "$dir" "$settings"
}

# Do not uv sync when in Claude Code sandbox
sync() { if [ -w /tmp ]; then uv sync -q; fi; }
set-tmpfile() {
    if [[ ! -v tmpfile ]]; then
        tmpfile=$(mktemp tmp/justfile-XXXXXX)
        trap "rm $tmpfile" EXIT
    fi
}
report () {
    # Usage: report "header" command args
    header=$1; shift
    set-tmpfile
    safe "$@" &> "$tmpfile"
    if [ -s "$tmpfile" ]; then
        echo "${HEADER_STYLE}# $header${NORMAL}"
        cat "$tmpfile"
    fi
}
run-checks() {
    report "ruff check" ruff check -q
    report "docformatter -c" docformatter -c src tests
    report "mypy" mypy
}
run-lint-checks() {
    ruff_ignores=C901,PLR0904,PLR0911,PLR0912,PLR0913,PLR0914,PLR0915,PLR0916,PLR0917,PLR1701,PLR1702
    report "ruff check" ruff check -q --ignore=$ruff_ignores
    report "docformatter -c" docformatter -c src tests
    report "mypy" mypy
}
run-pytest() {
    # Test sentinel: skip pytest if inputs unchanged
    local sentinel="tmp/.test-sentinel"
    mkdir -p tmp
    local current_hash
    current_hash=$( {
        python3 --version 2>&1
        git ls-files -z src/ tests/ agent-core/hooks/ agent-core/bin/ | sort -z | xargs -0 cat
        cat pyproject.toml
    } | cksum )
    if [ -f "$sentinel" ] && [ "$(cat "$sentinel")" = "$current_hash" ]; then
        echo "Tests cached (inputs unchanged)"
        return
    fi
    local pytest_output pytest_failed=false
    pytest_output=$(pytest 2>&1) || pytest_failed=true
    echo "$pytest_output"
    if echo "$pytest_output" | grep -q "skipped"; then fail "Tests skipped — all tests must run"; fi
    if [ "$pytest_failed" = true ]; then
        status=false
    else
        echo "$current_hash" > "$sentinel"
    fi
}
run-line-limits() {
    ./scripts/check_line_limits.sh
}
report-end-safe() {
    if end-safe
    then echo "${GREEN}✓$NORMAL $1 OK"
    else echo "${RED}✗$NORMAL $1 failed"
    fi
    end-safe
}
'''

# Launch Claude Code with plugin loaded from submodule
[no-exit-message]
claude:
    #!{{ bash_prolog }}
    exec claude --plugin-dir ./agent-core

# Launch Claude Code with plugin and empty system prompt (clean-slate workflow)
[no-exit-message]
claude0:
    #!{{ bash_prolog }}
    exec claude --plugin-dir ./agent-core --system-prompt ""

# Run all checks
[no-exit-message]
precommit:
    #!{{ bash_prolog }}
    sync
    report "validate memory-index" claudeutils validate memory-index
    report "validate learnings" claudeutils validate learnings
    report "validate tasks" claudeutils validate tasks
    report "validate planstate" claudeutils validate planstate
    report "validate session-structure" claudeutils validate session-structure
    run-checks
    report "version consistency" python3 agent-core/bin/check-version-consistency.py
    run-pytest
    run-line-limits
    report-end-safe "Precommit"

# Run edify-plugin validators only (subset of precommit, no lint/test/line-limits)
[no-exit-message]
precommit-base:
    #!{{ bash_prolog }}
    sync
    report "validate memory-index" claudeutils validate memory-index
    report "validate learnings" claudeutils validate learnings
    report "validate tasks" claudeutils validate tasks
    report "validate planstate" claudeutils validate planstate
    report "validate session-structure" claudeutils validate session-structure
    report-end-safe "Precommit-base"

# Run test suite
[no-exit-message]
test *ARGS:
    #!{{ bash_prolog }}
    sync
    pytest {{ ARGS }}
    report-end-safe "Tests"

# Format code
format:
    #!{{ bash_prolog }}
    sync
    set-tmpfile
    patch-and-print() {
        patch "$@" | sed -Ene "/^patching file '/s/^[^']+'([^']+)'/\\1/p"
    }
    ruff check -q --fix-only --diff | patch-and-print >> "$tmpfile" || true
    ruff format -q --diff | patch-and-print >> "$tmpfile" || true
    docformatter --diff src tests | patch-and-print -RCp1 >> "$tmpfile" || true
    modified=$(sort --unique < "$tmpfile")
    if [ -n "$modified" ] ; then
        bold=$'\033[1m'; nobold=$'\033[22m'
        red=$'\033[31m'; resetfg=$'\033[39m'
        echo "${bold}${red}**Reformatted files:**"
        echo "$modified" | sed "s|^|${bold}${red}  - ${nobold}${resetfg}|"
    fi

# Format, check without complexity, NO test
[no-exit-message]
red-lint: format
    #!{{ bash_prolog }}
    sync
    run-lint-checks
    report-end-safe "Red Lint"

# Format, check without complexity, test
[no-exit-message]
lint: format
    #!{{ bash_prolog }}
    sync
    run-lint-checks
    run-pytest
    report-end-safe "Lint"

# Check code style
[no-exit-message]
check:
    #!{{ bash_prolog }}
    sync
    run-lint-checks
    report-end-safe "Checks"

# Create a git worktree for parallel work
[no-exit-message]
wt-new name base="HEAD" session="":
    #!{{ bash_prolog }}
    slug="{{name}}"
    branch="$slug"
    wt_dir=$(wt-path "$slug")
    if [ -d "$wt_dir" ]; then
        fail "Worktree already exists: $wt_dir"
    fi
    mkdir -p "$(dirname "$wt_dir")"
    branch_exists=false
    if git rev-parse --verify "$branch" >/dev/null 2>&1; then
        branch_exists=true
    fi
    if [ "$branch_exists" = true ]; then
        # Use existing branch
        if [ -n "{{session}}" ]; then
            echo "${RED}Warning: session= ignored for existing branch${NORMAL}" >&2
        fi
        visible git worktree add "$wt_dir" "$branch"
    elif [ -n "{{session}}" ]; then
        # Pre-commit focused session.md to branch before worktree creation
        blob=$(git hash-object -w "{{session}}")
        tmp_index=$(mktemp -p tmp/)
        trap "rm -f '$tmp_index'" EXIT ERR
        GIT_INDEX_FILE="$tmp_index" git read-tree "{{base}}"
        GIT_INDEX_FILE="$tmp_index" git update-index --cacheinfo "100644,$blob,agents/session.md"
        new_tree=$(GIT_INDEX_FILE="$tmp_index" git write-tree)
        rm -f "$tmp_index"
        trap - EXIT ERR
        new_commit=$(git commit-tree "$new_tree" -p "$(git rev-parse "{{base}}")" -m "Focused session for $slug")
        git branch "$branch" "$new_commit"
        visible git worktree add "$wt_dir" "$branch"
    else
        visible git worktree add "$wt_dir" -b "$branch" "{{base}}"
    fi
    # Submodule: create worktree (shared object store) instead of --reference clone
    submodule_branch_exists=false
    if git -C agent-core rev-parse --verify "$branch" >/dev/null 2>&1; then
        submodule_branch_exists=true
    fi
    if [ "$submodule_branch_exists" = true ]; then
        visible git -C agent-core worktree add "$wt_dir/agent-core" "$branch"
    else
        visible git -C agent-core worktree add "$wt_dir/agent-core" -b "$branch"
    fi
    # Register container directory in sandbox permissions
    wt_container="$(dirname "$wt_dir")"
    main_repo="$(git rev-parse --show-toplevel)"
    add-sandbox-dir "$wt_container" .claude/settings.local.json
    add-sandbox-dir "$wt_container" "$wt_dir/.claude/settings.local.json"
    add-sandbox-dir "$main_repo" "$wt_dir/.claude/settings.local.json"
    # Set up development environment in worktree
    if (cd "$wt_dir" && just --summary 2>/dev/null | tr ' ' '\n' | grep -qx setup); then
        (cd "$wt_dir" && just setup)
    else
        (cd "$wt_dir" && direnv allow && uv sync -q && npm install)
    fi
    echo ""
    echo "${GREEN}✓${NORMAL} Worktree ready: $wt_dir"
    echo "  Launch: ${COMMAND}cd $wt_dir && claude${NORMAL}"

# Create worktree with focused session for a specific task
[no-exit-message]
wt-task name task_name base="HEAD":
    #!{{ bash_prolog }}
    focused_session="tmp/wt-{{name}}-session.md"
    mkdir -p tmp
    # Generate focused session inline (focus-session.py not yet implemented)
    echo "# Session: Worktree — {{task_name}}" > "$focused_session"
    echo "" >> "$focused_session"
    echo "**Status:** Focused worktree for parallel execution." >> "$focused_session"
    echo "" >> "$focused_session"
    echo "## Pending Tasks" >> "$focused_session"
    echo "" >> "$focused_session"
    # Extract task from session.md
    grep -A5 "^- \[ \] \*\*{{task_name}}\*\*" agents/session.md >> "$focused_session" || \
        fail "Task not found in agents/session.md: {{task_name}}"
    just wt-new "{{name}}" "{{base}}" "$focused_session"
    rm -f "$focused_session"

# List active git worktrees
wt-ls:
    @git worktree list --porcelain | awk '/^worktree/ {path=$2; branch=""} /^branch/ {branch=$2; sub(/^refs\/heads\//, "", branch)} /^$/ && branch != "" && path != "{{justfile_directory()}}" {n=split(path, parts, "/"); print parts[n] "\t" branch "\t" path; branch=""}'

# Remove a git worktree and its branch
[no-exit-message]
wt-rm name:
    #!{{ bash_prolog }}
    slug="{{name}}"
    branch="$slug"
    wt_dir=$(wt-path "$slug")
    # Check if worktree exists (branch-only cleanup is valid)
    if [ -d "$wt_dir" ]; then
        # Warn about uncommitted changes
        if [ -d "$wt_dir/.git" ] && ! (cd "$wt_dir" && git diff --quiet HEAD 2>/dev/null); then
            echo "${RED}Warning: $wt_dir has uncommitted changes${NORMAL}" >&2
        fi

        # Probe: is parent worktree registered?
        parent_registered=false
        if git worktree list | grep -q "$wt_dir"; then
            parent_registered=true
        fi

        # Probe: is submodule worktree registered?
        submodule_registered=false
        if [ -d "$wt_dir/agent-core" ] && git -C agent-core worktree list | grep -q "$wt_dir/agent-core"; then
            submodule_registered=true
        fi

        # Remove submodule worktree first (git refuses parent removal while submodule worktree exists)
        if [ "$submodule_registered" = true ] && [ -d "$wt_dir/agent-core" ]; then
            visible git -C agent-core worktree remove --force "$wt_dir/agent-core"
        fi
        if [ "$parent_registered" = true ]; then
            visible git worktree remove --force "$wt_dir"
        fi

        # Remove directory if still exists (orphaned or git failed)
        if [ -d "$wt_dir" ]; then
            rm -rf "$wt_dir"
        fi

        # Verify cleanup succeeded
        if [ -d "$wt_dir" ]; then
            echo "${RED}Sandbox blocked worktree removal${NORMAL}" >&2
            echo "Retry with: Bash(\"just wt-rm $slug\", dangerouslyDisableSandbox=true)" >&2
            exit 1
        fi
    fi
    # Remove empty container directory
    wt_parent="$(dirname "$wt_dir")"
    if [ -d "$wt_parent" ] && [ -z "$(ls -A "$wt_parent")" ]; then
        rmdir "$wt_parent"
    fi
    # Remove branch if fully merged
    if git rev-parse --verify "$branch" >/dev/null 2>&1; then
        if git merge-base --is-ancestor "$branch" HEAD 2>/dev/null; then
            visible git branch -d "$branch"
        else
            echo "${RED}Branch $branch has unmerged commits. Merge first.${NORMAL}" >&2
        fi
    fi
    echo "${GREEN}✓${NORMAL} Worktree removed: $wt_dir"

# Merge a worktree branch back and resolve submodule + session.md
[no-exit-message]
wt-merge name:
    #!{{ bash_prolog }}
    slug="{{name}}"
    branch="$slug"
    wt_dir=$(wt-path "$slug")

    # Pre-checks: Clean tree (exempt session files)
    session_exempt="agents/session.md agents/learnings.md"
    dirty=$(git status --porcelain | grep -vE "^.. ($(echo "$session_exempt" | tr ' ' '|'))$" || true)
    if [ -n "$dirty" ]; then
        echo "${RED}Dirty tree (non-session files):${NORMAL}" >&2
        echo "$dirty" >&2
        fail "Clean tree required for merge"
    fi
    submodule_dirty=$(git -C agent-core status --porcelain | grep -vE "^.. ($(echo "$session_exempt" | tr ' ' '|'))$" || true)
    if [ -n "$submodule_dirty" ]; then
        echo "${RED}Dirty agent-core submodule:${NORMAL}" >&2
        echo "$submodule_dirty" >&2
        fail "Clean tree required for merge"
    fi

    # Check worktree (THEIRS) for uncommitted changes
    if ! git -C "$wt_dir" diff --quiet --exit-code 2>/dev/null && ! git -C "$wt_dir" diff --cached --quiet --exit-code 2>/dev/null; then
        echo "${RED}Worktree has uncommitted changes:${NORMAL}" >&2
        git -C "$wt_dir" status --short >&2
        fail "Worktree has uncommitted changes. Commit or stash before merging."
    fi

    if ! git rev-parse --verify "$branch" >/dev/null 2>&1; then
        fail "Branch not found: $branch"
    fi
    if [ ! -d "$wt_dir" ]; then
        echo "${RED}Warning: worktree directory not found: $wt_dir${NORMAL}" >&2
    fi

    # Phase 2: Submodule Resolution
    wt_commit=$(git ls-tree "$branch" -- agent-core | awk '{print $3}')
    local_commit=$(git -C agent-core rev-parse HEAD)
    if [ "$wt_commit" != "$local_commit" ]; then
        # Check ancestry
        if ! git -C agent-core merge-base --is-ancestor "$wt_commit" "$local_commit" 2>/dev/null; then
            # Fetch submodule commits if not already reachable (no-op for worktree-based submodules)
            if ! git -C agent-core cat-file -e "$wt_commit" 2>/dev/null; then
                if [ -d "$wt_dir/agent-core" ]; then
                    visible git -C agent-core fetch "$wt_dir/agent-core" HEAD
                fi
            fi
            # Merge
            if ! visible git -C agent-core merge --no-edit "$wt_commit"; then
                echo "${RED}Submodule merge conflict in agent-core${NORMAL}" >&2
                fail "Resolve in agent-core/, commit, then re-run: just wt-merge $slug"
            fi
            # Stage and commit
            visible git add agent-core
            git diff --quiet --cached || visible git commit -m "🔀 Merge agent-core from $slug"
        fi
    fi

    # Phase 3: Parent Merge
    if ! git merge --no-commit --no-ff "$branch" 2>&1; then
        conflicts=$(git diff --name-only --diff-filter=U)

        # agent-core: keep ours (already merged in Phase 2)
        if echo "$conflicts" | grep -q "^agent-core$"; then
            visible git checkout --ours agent-core
            visible git add agent-core
        fi

        # Session files: extract tasks from theirs before keeping ours
        if echo "$conflicts" | grep -q "^agents/session.md$"; then
            # Extract new tasks from worktree side
            theirs_tasks=$(git show :3:agents/session.md | sed -n 's/^- \[ \] \*\*\([^*]*\)\*\*.*/\1/p' || true)
            ours_tasks=$(git show :2:agents/session.md | sed -n 's/^- \[ \] \*\*\([^*]*\)\*\*.*/\1/p' || true)

            # Keep ours as base
            visible git checkout --ours agents/session.md

            # Append new tasks if any (simplified - just warns for now)
            if [ -n "$theirs_tasks" ]; then
                echo "${RED}Warning: Manual task extraction needed from worktree session.md${NORMAL}" >&2
                echo "  New tasks in worktree: $theirs_tasks" >&2
            fi

            visible git add agents/session.md
        fi

        # learnings.md: keep both (append theirs to ours)
        if echo "$conflicts" | grep -q "^agents/learnings.md$"; then
            # Simplified: just keep ours for now (full logic needs parsing)
            echo "${RED}Warning: Manual learning merge needed${NORMAL}" >&2
            visible git checkout --ours agents/learnings.md
            visible git add agents/learnings.md
        fi

        # Check for any remaining conflicts
        remaining=$(git diff --name-only --diff-filter=U)
        if [ -n "$remaining" ]; then
            echo "${RED}Conflicts need resolution:${NORMAL}" >&2
            echo "$remaining" >&2
            echo "Resolve conflicts, git add, then: git commit -m '🔀 Merge $slug'" >&2
            exit 3
        fi
    fi

    # Commit merge
    visible git commit -m "🔀 Merge $slug"

    # Post-merge precommit gate
    echo ""
    echo "Running precommit validation..."
    if ! just precommit >/dev/null 2>&1; then
        echo "${RED}Precommit failed after merge${NORMAL}" >&2
        echo "  Fix issues and amend: git commit --amend" >&2
        exit 1
    fi

    echo ""
    echo "${GREEN}✓${NORMAL} Merged $branch"
    echo "  Cleanup: ${COMMAND}just wt-rm $slug${NORMAL}"

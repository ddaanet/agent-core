# Directory Changes

Handling directory changes safely with the token-efficient pattern.

## Using trap

```bash
# Work in different directory, restore on exit
exec 2>&1
set -xeuo pipefail

trap "cd $(printf %q "$PWD")" EXIT

cd /some/other/directory
# Work in other directory
```

**Why `trap` is needed:**
- `set -e` exits on error, leaving you in wrong directory
- `trap EXIT` runs cleanup even on error or success
- Restores shell to original location

**Quoting with `printf %q`:**
- `printf %q` shell-escapes the path for safe inclusion in script
- Handles spaces, special characters correctly
- Example: `/path/with spaces` becomes `$'/path/with spaces'`

## Using Subshell (simpler for one-off commands)

```bash
# Work in different directory using subshell
exec 2>&1
set -xeuo pipefail

(
  cd /some/other/directory
  # Work here
)

# Already back in original directory
```

Subshell auto-restores directory without trap, but creates new process.

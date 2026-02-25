# Token-Efficient Bash Examples

Three worked examples demonstrating the pattern in different contexts.

## Example 1: File Operations

```bash
# Move log files to backup directory and create symlink
exec 2>&1
set -xeuo pipefail

mkdir -p target/backup/
mv source/*.log target/backup/
ln -s ../target/backup source/logs
chmod 644 target/backup/*.log
```

**Output:**
```
+ mkdir -p target/backup/
+ mv source/*.log target/backup/
+ ln -s ../target/backup source/logs
+ chmod 644 target/backup/*.log
```

## Example 2: Git Workflow

```bash
# Stage, commit, and push documentation updates
exec 2>&1
set -xeuo pipefail

git add -A
git commit -m "Update documentation

- Add installation guide
- Fix typos in README
- Update examples"
git push origin main
```

**Output:**
```
+ git add -A
+ git commit -m 'Update documentation

- Add installation guide
- Fix typos in README
- Update examples'
[main a7f38c2] Update documentation
 3 files changed, 42 insertions(+), 7 deletions(-)
+ git push origin main
To github.com:user/repo.git
   abc123f..a7f38c2  main -> main
```

## Example 3: Setup with Expected Failures

```bash
# Set up directories and process input files
exec 2>&1
set -xeuo pipefail

# Create directory structure
mkdir -p tmp/output tmp/logs

# Check if config exists (grep exit 1 is okay)
if grep -q "debug_mode: true" config.yaml || true; then
    echo "Debug mode enabled"
fi

# Clean up old files if they exist
rm -f tmp/output/*.tmp || true

# Process files
for file in input/*.txt; do
    process "$file" > "tmp/output/$(basename "$file")"
done
```

**Output:**
```
+ mkdir -p tmp/output tmp/logs
+ grep -q 'debug_mode: true' config.yaml
+ echo 'Debug mode enabled'
Debug mode enabled
+ rm -f tmp/output/*.tmp
+ for file in input/*.txt
+ basename input/file1.txt
+ process input/file1.txt
+ for file in input/*.txt
+ basename input/file2.txt
+ process input/file2.txt
```

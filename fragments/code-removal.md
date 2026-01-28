## Code Removal

**Delete obsolete code, don't archive it.**

When code, files, or designs become obsolete or superseded:
- **Delete them completely** - Remove the files from the repository
- **Do NOT archive** - Don't move to `archive/`, `old/`, or similar directories
- **Do NOT comment out** - Don't leave dead code in comments
- **Do NOT keep "for reference"** - Git history preserves everything if needed

**Rationale:**
- Dead code creates maintenance burden
- Archives accumulate and confuse future developers
- Git history is the archive - use `git log` and `git show` to retrieve old code
- Clean codebase is easier to navigate and understand

**Examples:**

**Wrong:**
```bash
mkdir archive/
mv old-design.md archive/
git add archive/old-design.md
```

**Correct:**
```bash
rm old-design.md
git add old-design.md
```

**Exception:** Documentation of *decisions* (why something was chosen over alternatives) should be kept in architecture decision records (ADRs) or similar, but the obsolete implementation itself should be removed.

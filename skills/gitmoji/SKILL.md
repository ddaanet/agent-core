---
name: Gitmoji
description: This skill should be used when the user asks to "use gitmoji", "add gitmoji to commit", "select gitmoji", "find appropriate emoji for commit", or when creating commit messages that should include gitmojis. Provides semantic matching of commit messages to appropriate gitmoji emojis from the official gitmoji database.
version: 0.1.0
---

# Gitmoji Skill

This skill provides semantic gitmoji selection for commit messages. It enables automatic selection of appropriate emoji prefixes based on commit message content using the official gitmoji database from https://gitmoji.dev.

## Purpose

Gitmojis are standardized emojis used in commit messages to quickly identify the purpose or intent of a commit. This skill:

- Reads the complete gitmoji index into context
- Semantically analyzes commit messages
- Selects the most appropriate gitmoji based on message content
- Returns the selected gitmoji to prepend to the commit message

This skill augments the `/commit` workflow rather than replacing it.

## When to Use This Skill

Use this skill when:
- Creating commit messages that should include gitmojis
- User explicitly requests gitmoji selection
- Working in projects that follow gitmoji conventions
- Integrated into custom `/commit` skill or specified in CLAUDE.md

## How to Use This Skill

### Step 1: Ensure Gitmoji Index Exists

Before using the skill, verify the gitmoji index file exists at:
```
skills/gitmoji/cache/gitmojis.txt
```

If the index doesn't exist, run the update script:
```bash
skills/gitmoji/scripts/update-gitmoji-index.sh
```

The script downloads the latest gitmoji database from the official API and creates a plain text index in the format:
```
emoji - name - description
```

### Step 2: Read the Gitmoji Index

Read the complete gitmoji index file into context using the Read tool:
```
Read: skills/gitmoji/cache/gitmojis.txt
```

The index is small (~75 entries) and designed to be read entirely rather than searched incrementally.

### Step 3: Analyze the Commit Message

Given a commit message (either draft or user-provided), analyze its semantic meaning to understand:
- **Type of change**: bug fix, feature, documentation, refactoring, performance, etc.
- **Scope of change**: code structure, dependencies, configuration, security, etc.
- **Impact level**: critical hotfix, breaking change, minor update, etc.

### Step 4: Select the Most Appropriate Gitmoji

Match the commit message semantics to gitmoji descriptions. Consider:

**Primary matching criteria:**
- Direct semantic alignment (e.g., "fix bug" → 🐛 bug)
- Change type (e.g., "add feature" → ✨ sparkles)
- Technical domain (e.g., "improve performance" → ⚡️ zap)

**Secondary matching criteria:**
- Urgency (e.g., "critical fix" → 🚑️ ambulance vs. regular 🐛 bug)
- Scope (e.g., "update docs" → 📝 memo)
- Special cases (e.g., "initial commit" → 🎉 tada)

**Selection guidelines:**
- Choose the most specific gitmoji that matches the primary intent
- When multiple gitmojis apply, prefer the one matching the most significant aspect
- Avoid generic gitmojis when more specific ones are available
- Consider project conventions if known

### Step 5: Return the Selected Gitmoji

Return the emoji character (not the name or code) to prepend to the commit message:
- **Correct**: 🐛
- **Incorrect**: :bug: or "bug"

The commit message should be formatted as:
```
emoji commit message
```

Example:
```
🐛 Fix null pointer exception in user authentication
```

## Common Gitmoji Mappings

For quick reference, here are frequently used gitmojis:

| Emoji | Name | When to Use |
|-------|------|-------------|
| 🐛 | bug | Fixing a bug |
| ✨ | sparkles | Introducing new features |
| 📝 | memo | Adding or updating documentation |
| 🎨 | art | Improving structure/format of code |
| ⚡️ | zap | Improving performance |
| 🔥 | fire | Removing code or files |
| 🚑️ | ambulance | Critical hotfix |
| ✅ | white-check-mark | Adding, updating, or passing tests |
| 🔒️ | lock | Fixing security/privacy issues |
| ⬆️ | arrow-up | Upgrading dependencies |
| ⬇️ | arrow-down | Downgrading dependencies |
| 🚧 | construction | Work in progress |
| 💚 | green-heart | Fixing CI build |
| 🔖 | bookmark | Release/version tags |
| 🚀 | rocket | Deploying stuff |

Refer to the complete index file for all available gitmojis.

## Integration with /commit

This skill is designed to work seamlessly with the `/commit` workflow:

1. **Via CLAUDE.md**: Add instruction to always use gitmoji skill when creating commits
2. **Via custom /commit skill**: Include gitmoji selection as a step in the commit workflow
3. **On-demand**: User explicitly requests gitmoji selection

The skill does NOT perform git change analysis - that responsibility belongs to the calling context (e.g., /commit skill). This skill focuses exclusively on semantic matching between commit message text and appropriate gitmojis.

## Updating the Gitmoji Index

The gitmoji database is periodically updated with new emojis. To refresh the local index:

```bash
skills/gitmoji/scripts/update-gitmoji-index.sh
```

Run this script:
- When new gitmojis are added to the official database
- After initial skill installation
- Periodically (e.g., monthly) to stay current

The script requires:
- `curl` for downloading the JSON database
- `jq` for processing JSON into plain text format
- Internet connection to reach https://gitmoji.dev/api/gitmojis

## Custom Gitmojis

In addition to the official gitmoji database, this project may use custom gitmojis not in the standard database. These are documented in:

```
skills/gitmoji/custom-gitmojis.md
```

When selecting gitmojis:
1. Check the official index first (`cache/gitmojis.txt`)
2. If no match, check custom gitmojis (`custom-gitmojis.md`)
3. Use custom gitmoji if it matches commit intent better

Example custom gitmoji:
- 🗜️ **compress** - Reducing file size, condensing content, or optimizing for brevity

---

## Additional Resources

### Scripts

- **`scripts/update-gitmoji-index.sh`** - Download and process gitmoji database into searchable index

### Index Files

- **`cache/gitmojis.txt`** - Plain text index of all gitmojis (emoji - name - description format)
- **`custom-gitmojis.md`** - Custom gitmojis specific to this project

## Best Practices

**Do:**
- Read the entire index file (it's small and efficient)
- Select gitmojis based on semantic meaning, not keyword matching
- Prioritize the primary intent when multiple gitmojis could apply
- Use the emoji character itself in the commit message
- Keep gitmoji selection transparent to the user during /commit

**Don't:**
- Search or grep the index file (read it entirely instead)
- Use gitmoji codes (`:bug:`) instead of emojis (🐛)
- Overthink selection - choose the most obvious match
- Add multiple gitmojis to a single commit
- Skip gitmoji if the match is unclear (make your best semantic judgment)

## Limitations

- Requires internet connection for initial index download
- Depends on jq for JSON processing
- Index must be manually updated to get new gitmojis
- Does not analyze git diffs (that's the caller's responsibility)
- Limited to one gitmoji per commit (gitmoji.dev convention)

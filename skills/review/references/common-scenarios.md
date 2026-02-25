# Common Review Scenarios

## Review finds secrets in code
- Mark as CRITICAL issue
- Do not show the secret value in review
- Recommend using environment variables or secure config
- Suggest tools like `git-secrets` if not already used

## Changes span multiple concerns
- Note in review if changes should be split into multiple commits
- Group issues by concern
- Suggest commit organization

## Code works but doesn't follow project patterns
- Mark as MAJOR issue if pattern is important
- Explain the project pattern
- Show example of correct pattern from codebase

## Review requested for already-committed work
- Still provide review
- Note in summary that changes are already committed
- Recommendations can be addressed in follow-up commit

## Large changeset (1000+ lines)
- Focus on high-level patterns and critical issues
- Do not nitpick every line
- Suggest breaking into smaller reviewable chunks if not committed yet

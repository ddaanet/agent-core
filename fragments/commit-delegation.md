## Commit Delegation Pattern

Commit delegation splits git commit responsibilities between orchestrator (analysis) and agent (execution). This pattern keeps orchestrator context lean while ensuring commits are well-reasoned.

### Pattern Overview

**Responsibility split:**
- **Orchestrator** (sonnet): Reviews changes, analyzes what/why, drafts message
- **Commit Agent** (haiku): Executes git commands, returns result
- **Benefit:** Token efficiency (~20 tokens vs ~1000+), clean context separation

**Why delegate commits?**

Without delegation, orchestrator context includes:
- Full git diff output (hundreds of lines)
- Change analysis discussion (multiple exchanges)
- Message drafting iterations
- Commit execution details
- Total: ~1000-3000 tokens per commit

With delegation, orchestrator context includes:
- Change summary (1-2 sentences)
- Commit message (3-5 sentences)
- Delegation handoff (1 line)
- Total: ~20-50 tokens per commit

**Token savings:** ~20-50x improvement per commit. Critical when orchestrating multi-step plans with commits.

### Orchestrator Responsibilities

**1. Run git diff HEAD to review changes**

```bash
git diff HEAD --stat  # Shows summary
git diff HEAD         # Shows detailed changes
```

**2. Analyze what changed and why**

Example analysis:
```
Analysis:
- Added 3 new files (auth.ts, auth.test.ts, auth.integration.ts)
- Updated 2 existing files (main.ts - import auth, package.json - add deps)
- Total: 350 lines added, 5 lines removed
- Change type: New feature - OAuth2 authentication module

Why:
- User requested OAuth2 support in requirements
- Implementation follows existing module patterns
- Tests included for both unit and integration
- No breaking changes to existing code
```

**3. Draft commit message**

Use imperative tense, 50-72 character subject line, follow repository style.

Example message:
```
Add OAuth2 authentication module with Google provider

- Add auth service with token management
- Add authentication middleware
- Add unit and integration tests
- Update main.ts to use auth middleware
- Update package.json with OAuth2 dependencies
```

**4. Delegate to commit agent**

Pass exact message as literal string (not paraphrase):

```
Invoke commit agent with prompt:
"Commit with message: 'Add OAuth2 authentication module with Google provider

- Add auth service with token management
- Add authentication middleware
- Add unit and integration tests
- Update main.ts to use auth middleware
- Update package.json with OAuth2 dependencies'"
```

### Commit Agent Responsibilities

**1. Receive message from orchestrator**
- Message is literal, not interpreted
- Agent uses exactly as provided

**2. Execute git commit**

```bash
git add .  # Stage all changes (orchestrator already reviewed)
git commit -m "$(cat <<'EOF'
[Exact message from orchestrator]
EOF
)"
```

**3. Handle errors**
- If commit succeeds: Return commit hash (e.g., "a7f38c2")
- If commit fails: Return detailed error message

**Example success return:**
```
a7f38c2
```

**Example failure return:**
```
Error: Nothing to commit
Details: git diff shows no staged changes.
Check: Were changes actually made? Did orchestrator review actual diff?
```

### Benefits

| Benefit | Details | Impact |
|---------|---------|--------|
| Token efficiency | Orchestrator: ~20-50 tokens; Agent: ~10-20 tokens | 20-50x reduction vs direct commit |
| Context cleanliness | Orchestrator doesn't store diff or analysis | Keeps orchestrator focused on orchestration |
| Audit trail | Commit message in git history, separate from agent transcript | Permanent record of intent |
| Error isolation | Commit errors don't pollute orchestrator context | Clear diagnostic in agent transcript |
| Message clarity | Orchestrator drafts message, agent doesn't interpret | Exact intent committed |
| Scalability | Pattern works same way for 10 commits or 100 | Scales with multi-step plans |

### Example Walkthrough

**Orchestrator (sonnet):**

```
Step 3: Commit changes to authentication module
Running: git diff HEAD --stat

Output:
 src/auth/auth.ts        | 120 added
 src/auth/auth.test.ts   | 95 added
 src/main.ts             | 5 modified
 package.json            | 2 modified
 4 files changed, 222 insertions(+), 0 deletions(-)

Analysis:
- Added new authentication module (120 lines)
- Added tests (95 lines)
- Updated existing files to integrate module (5 + 2 lines)
- Change type: New feature
- Scope: Contained to auth module, no breaking changes
- Risk: Low (tests included, no modifications to other subsystems)

Draft message:
"Add authentication module with JWT support

- Add auth service with token generation and validation
- Add JWT middleware for protected routes
- Add comprehensive unit and integration tests
- Update main.ts to initialize auth middleware
- Add jwt dependency to package.json"

Delegating to commit agent...
```

**Commit Agent (haiku):**

```
Received delegation:
"Commit with message: 'Add authentication module with JWT support

- Add auth service with token generation and validation
- Add JWT middleware for protected routes
- Add comprehensive unit and integration tests
- Update main.ts to initialize auth middleware
- Add jwt dependency to package.json'"

Executing:
$ git add .
$ git commit -m "..."
[main 5a8f72c] Add authentication module with JWT support
 4 files changed, 222 insertions(+)

Returning: 5a8f72c
```

**Orchestrator:**

```
Step 3 complete: Commit succeeded (5a8f72c)
Continue to step 4...
```

### Integration with Weak Orchestrator Pattern

**Delegation timing:**
- After implementation step completes (new files created, edits applied)
- Before next logical step (e.g., before running tests on new code)
- Whenever explicit checkpoint in plan calls for commit

**Integration with quiet execution:**
- Commit agent operates silently (returns hash only on success)
- Detailed git output stored in agent transcript, not orchestrator context
- Orchestrator sees only: success (hash) or failure (error message)

**Integration with plan-specific agent:**
- Commit steps can be part of plan-specific agent workflow
- Agent can execute multiple commits if plan requires them
- Each commit delegated separately with distinct message

### Common Patterns

**Pattern 1: Feature commit after implementation**
```
Message: "Add [feature name]
- [Implementation detail 1]
- [Implementation detail 2]
- [Testing detail]"
```

**Pattern 2: Fix commit after bug fix**
```
Message: "Fix [issue description]
- Root cause: [what was wrong]
- Solution: [how fixed]
- Testing: [verification]"
```

**Pattern 3: Refactor commit after code cleanup**
```
Message: "Refactor [module name] for [reason]
- Changed [what changed]
- No functional changes
- Tests pass"
```

**Pattern 4: Documentation commit**
```
Message: "Document [what]
- Add/update [documentation]
- [Additional details]"
```

### Anti-Patterns (What NOT to Do)

**Don't:** Have orchestrator try to execute git directly
- Creates context bloat (git output, conflict resolution, etc.)
- Prevents parallelization (commit takes orchestrator attention)

**Don't:** Have agent make judgment calls about what to commit
- Agent should commit exactly what orchestrator specifies
- No "smart" cherry-picking or selective staging

**Don't:** Accumulate multiple commits in one delegation
- Each significant change gets separate commit
- Multiple commits delegated separately
- Preserves clear intent in git history

**Don't:** Forget to stage changes before delegating
- Orchestrator is responsible for verifying git diff
- Agent assumes changes are staged or will stage all
- No surprises between git diff review and actual commit

### Error Recovery

**If commit fails:**

```
Agent returns:
"Error: Commit failed - merge conflict on src/main.ts
Details: Conflicting changes detected during merge.
Resolution required: Manual merge needed before commit."

Orchestrator action:
1. Classify as execution error
2. Escalate to sonnet
3. Sonnet resolves conflict, attempts re-commit
4. If resolved, returns new commit hash
5. If unresolvable, escalates to user for guidance
```

**If message was wrong:**

```
Orchestrator (discovering issue):
1. Reads git log to see what was committed
2. Verifies against original diff
3. If message doesn't match changes: Escalate to sonnet
4. Sonnet amends commit with correct message
```

This separation of concerns ensures commits are intentional, auditable, and integrated cleanly with orchestrator flow.

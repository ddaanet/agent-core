## Roles, Rules, and Skills

**Roles** define agent behavior modes. **Rules** apply during specific actions. **Skills** are on-demand operations.

### Roles

| Role     | File                      | Purpose                    |
| -------- | ------------------------- | -------------------------- |
| planning | `agents/role-planning.md` | Design test specifications |
| code     | `agents/role-code.md`     | TDD implementation         |
| lint     | `agents/role-lint.md`     | Fix lint/type errors       |
| refactor | `agents/role-refactor.md` | Plan refactoring changes   |
| execute  | `agents/role-execute.md`  | Execute planned changes    |
| review   | `agents/role-review.md`   | Code review and cleanup    |
| remember | `agents/role-remember.md` | Update agent documentation |

### Rules (Action-Triggered)

| Rule    | File                      | Trigger                 |
| ------- | ------------------------- | ----------------------- |
| commit  | `agents/rules-commit.md`  | Before any `git commit` |
| handoff | `agents/rules-handoff.md` | Before ending a session |

### Skills (On-Demand)

| Skill | File                    | Trigger  | Purpose                        |
| ----- | ----------------------- | -------- | ------------------------------ |
| shelf | `skills/skill-shelf.md` | `/shelf` | Archive context to todo, reset |

**Loading:**
- **Roles:** Read at session start
- **Rules:** Read before the triggering action
- **Skills:** Read when user invokes the trigger command

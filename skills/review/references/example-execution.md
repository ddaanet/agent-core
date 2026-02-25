# Example Review Execution

**User:** `/review`

**Agent:** "What should I review?

1. Uncommitted changes
2. Recent commits
3. Current branch
4. Specific files
5. Everything"

**User:** "Uncommitted changes"

**Agent:** "Reviewing uncommitted changes...

*Runs git status and git diff HEAD*

Found changes in 5 files:
- agent-core/agents/artisan.md (new file)
- agent-core/bin/prepare-runbook.py (new file)
- CLAUDE.md (modified)
- plans/general-workflow/design.md (modified)
- .claude/agents/unification-task.md (new file)

Analyzing changes...

*Reviews each file for quality, standards, security*

Review complete.

**Overall Assessment**: Ready

**Issues found:**
- Critical: 0
- Major: 0
- Minor: 2

Full review written to: scratch/reviews/review-report-2026-01-19-142530.md

**Minor issues:**
1. prepare-runbook.py: Consider adding --help flag example to docstring
2. artisan.md: Typo in line 87 \"specificed\" -> \"specified\"

**Recommendations:**
- All files follow project conventions
- Good documentation in script
- Comprehensive error handling

**Next steps:**
1. Fix minor typo if desired (optional)
2. Ready to commit"

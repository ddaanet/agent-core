# Review Analysis Axes

10-category checklist for analyzing changes during review.

## Code Quality
- Logic correctness
- Edge case handling
- Error handling
- Code clarity and readability
- Appropriate abstractions (not over/under-engineered)

## Design Conformity (when design doc available)
- Implementation matches design specifications
- All design-specified behaviors actually implemented (not stubbed)
- Integration between components matches design architecture
- No hardcoded values where design specifies dynamic behavior
- Check: grep for hardcoded return values in functions that should compute

## Functional Completeness
- CLI commands produce meaningful output (not just "OK" or empty)
- Functions return computed values (not empty strings or hardcoded constants)
- Components that should read external state actually do so
- Check: look for stub patterns: `return ""`, `return {}`, hardcoded constructors
- Integration: components that exist separately are wired together

## Project Standards
- Follows existing patterns and conventions
- Consistent with codebase style
- Proper file locations
- Appropriate dependencies

## Runbook File References (when reviewing runbooks/plans)
- Extract all file paths referenced in steps/cycles
- Use Glob to verify each path exists in the codebase
- Flag missing files as CRITICAL issues (runbooks with wrong paths fail immediately)
- Check test function names exist in referenced test files (use Grep)
- Suggest correct paths when similar files are found

## Self-Referential Modification (when reviewing runbooks/plans)
- Flag any step containing file-mutating commands (`sed -i`, `find ... -exec`, `Edit` tool, `Write` tool)
- Check if target path overlaps with `plans/<plan-name>/` (excluding `reports/` subdirectory)
- Mark as MAJOR issue if runbook steps modify their own plan directory during execution
- Rationale: Runbook steps must not mutate the plan directory they're defined in (creates ordering dependency, breaks re-execution)

## Security
- No hardcoded secrets or credentials
- Input validation where needed
- No obvious vulnerabilities
- Proper authentication/authorization

## Testing
- Tests included where appropriate
- Tests cover main cases
- Tests are clear and maintainable

## Documentation
- Code comments where logic isn't obvious
- Updated relevant documentation
- Clear commit messages (if reviewing commits)

## Completeness
- All TODOs addressed or documented
- No debug code left behind
- No commented-out code (unless explained)
- Related changes included

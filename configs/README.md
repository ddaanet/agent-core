# Base Configuration Files

This directory contains base configuration files for agent projects. These provide common settings for build tools, linters, and type checkers.

## Files

- **justfile-base.just** - Common justfile recipes (help, dev, test, check, format, lint)
- **ruff-base.toml** - Ruff linter base configuration
- **mypy-base.toml** - Mypy type checker base configuration
- **docformatter-base.toml** - Docformatter base configuration

## Usage

### Current Status (Phase 4 Complete)

These base files are organized and ready for use. Projects can reference them, but automatic composition/import is not yet implemented.

### Future: Justfile Import

Justfiles can use the `import` or `mod` directive to include base recipes:

```just
import "agent-core/configs/justfile-base.just"

# Project-specific recipes here
```

### Future: TOML Composition

For pyproject.toml, projects currently need to manually sync base configurations. Future options:

1. **Manual sync** - Copy base configs and customize (current approach)
2. **Composition tooling** - Build tool to merge base + project configs (requires Phase 5-7 implementation)
3. **Runtime imports** - TOML doesn't support this natively

### Template Variables

The base justfile uses these template variables that projects must define:

- `SRC_DIR` - Source directory (usually "src")
- `TEST_DIR` - Test directory (usually "tests")
- `VENV` - Virtual environment path (usually ".venv")

## Related

- See `plans/unification/design.md` for original composition design
- Phase 5-7 (compose.py tooling) was marked obsolete for CLAUDE.md but may still be needed for config files

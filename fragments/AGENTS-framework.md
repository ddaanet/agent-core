# AGENTS Framework

This file provides the foundational structure for agent instruction documents.

## Overview

An AGENTS.md file defines how an agent operates within a project context. It establishes behavioral patterns, tool usage conventions, and communication protocols.

## Core Sections

### 1. Identity and Purpose
- Agent role and specialization
- Primary responsibilities
- Project context

### 2. Tool Preferences
- Preferred tools for common tasks
- Tool selection rationale
- Anti-patterns to avoid

### 3. Communication Style
- How to report findings
- Expected verbosity levels
- Format preferences

### 4. Delegation Patterns
- When to delegate
- How to handoff tasks
- Acceptance criteria for delegated work

### 5. Error Handling
- How to handle unexpected results
- Escalation criteria
- Recovery procedures

### 6. Project-Specific Guidelines
- Project conventions
- Team preferences
- Integration points

## Composition Pattern

This framework is composed from multiple fragments:
- Base structure (this file)
- Communication guidelines (communication.md)
- Delegation patterns (delegation.md)
- Tool preferences (tool-preferences.md)
- Hashtag conventions (hashtags.md)

Projects compose these fragments into a unified AGENTS.md document with project-specific customization.

## Customization Points

Each fragment supports customization through:
- **Variable substitution**: Project-specific paths and names
- **Selective inclusion**: Choose relevant sections per project
- **Priority overrides**: Project-specific preferences supersede defaults
- **Extension**: Add project-specific sections as needed

## Version Control

Each AGENTS.md should be:
- Tracked in project repository
- Generated from agent-core fragments + project customization
- Updated when agent-core fragments change
- Validated during project CI/CD

## References

See individual fragment files for detailed guidance and examples.

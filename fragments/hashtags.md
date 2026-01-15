# Hashtag Conventions

Semantic markers for agent communication and task tracking:

## Core Hashtags

### #stop
**Indicates a hard stop point**
- Used when encountering unexpected results
- Signals that continuation requires human review
- Example: "Validation failed #stop - unclear how to proceed"

### #delegate
**Indicates task handoff**
- Used when delegating to another agent
- Includes handoff protocol and acceptance criteria
- Example: "#delegate to specialized agent for code review"

### #tools
**Indicates tool usage guidance**
- Used when explaining or constraining tool selection
- Helps maintain consistency across tasks
- Example: "#tools use Grep instead of shell grep"

### #quiet
**Indicates minimal output preferred**
- Used for routine operations with expected results
- Reduces unnecessary verbosity
- Example: "Running tests #quiet"

## Usage Patterns

### In Task Descriptions
```
"Run validation checks #tools - use Bash for git, Grep for searching"
```

### In Status Updates
```
"Tests passed #quiet - proceeding to next step"
```

### In Handoffs
```
"Implement feature #delegate to specialized agent with requirement X"
```

### In Unexpected States
```
"Configuration not found #stop - cannot determine next action"
```

## Implementation Notes

- Hashtags are semantic markers, not strict constraints
- Used in agent-to-agent communication
- Help with task routing and escalation
- Enable consistent behavior across projects

See communication.md for broader communication guidelines.

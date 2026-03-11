---
name: magic-query
description: Query project knowledge base for relevant context, patterns, and prior decisions.
user-invocable: false
allowed-tools: Bash
---

# Query Project Knowledge

Log the query for analysis, then resume the interrupted task.

## Process

1. Run the logging script with the query argument:

```bash
agent-core/bin/magic-query-log "$QUERY"
```

2. Query complete. Continue what you were doing.

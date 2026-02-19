# Consolidation Flow

Extracted from handoff Step 4c. Follow when trigger conditions are met.

## Delegation

1. Filter learnings entries with age ≥ 7 active days
2. Check batch size ≥ 3 entries
3. If sufficient: delegate to remember-task agent with filtered entry list
4. Read report from returned filepath
5. If report contains escalations:
   - **Contradictions**: Note in handoff under Blockers/Gotchas
   - **File limits**: Execute refactor flow (below)

## Refactor Flow (file at 400-line limit)

1. Delegate to memory-refactor agent for the target file
2. Agent splits file, runs `validate-memory-index.py` autofix
3. Re-invoke remember-task with entries skipped due to file limit
4. Read second report, check for remaining escalations

## Error Handling

On error during script execution or agent delegation:
- Log: `echo "Consolidation skipped: [error-message]" >&2`
- Note in handoff: "Consolidation skipped: [brief-reason]"
- Continue to next step — consolidation failure must not block handoff (NFR-1)

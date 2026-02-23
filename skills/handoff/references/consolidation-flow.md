# Consolidation Flow

Extracted from handoff Step 4c. Follow when trigger conditions are met.

## Inline Execution

1. Filter learnings entries with age ≥ 7 active days
2. Check batch size ≥ 3 entries
3. If sufficient: invoke `/remember` skill in current session (requires clean session — fresh start)
4. If escalations during consolidation:
   - **Contradictions**: Note in handoff under Blockers/Gotchas
   - **File limits**: Execute refactor flow (below)

## Refactor Flow (file at 400-line limit)

1. Check target file `wc -l` — if >400 lines, split needed
2. Split by H2/H3 boundaries into 100-300 line sections
3. Run `agent-core/bin/validate-memory-index.py --fix` after split
4. Resume consolidation with entries skipped due to file limit

## Error Handling

On error during script execution or agent delegation:
- Log: `echo "Consolidation skipped: [error-message]" >&2`
- Note in handoff: "Consolidation skipped: [brief-reason]"
- Continue to next step — consolidation failure must not block handoff (NFR-1)

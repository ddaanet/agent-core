## Tool Batching

**Precondition:** Edit requires a prior Read call for the target file. @-references don't satisfy this gate. Read files in an earlier message, then batch edits. A failed precondition cascades to all sibling tool calls, wasting their inputs.

**Planning phase (before tool calls):**
1. Identify ALL changes needed for current task
2. Group by file: same-file edits sequential, different-file edits parallel
3. For multi-edit files: list all edit targets; edits with non-overlapping strings can run in parallel

**Execution phase:**
4. **Batch reads:** Read multiple files in one message when needed soon
5. **Different files:** Edit in parallel when independent
6. **Same file:** Edit in parallel when strings don't overlap; sequentially when one edit's result is another's target
7. **Refresh context:** If you plan to modify a file again in next iteration, Read it in the batch

**Task tool parallelization:**
8. **Independent agents:** Launch all independent Task calls in a single message — concurrent execution
9. **Sequential anti-pattern:** Launching Task agents one-at-a-time when all inputs are ready (wastes wall time — batch instead)

---

# Codify Learnings

Domain-specific patterns for the codification process.

## When Naming Learning Headings

**Anti-pattern:** Naming the heading after the antipattern itself ("When recall step uses skip condition language"). Describes what went wrong, not where you are.

**Correct pattern:** Name after the situation at the decision point — the activity you're doing when the rule applies ("When recall gate has skip condition" → you're at the gate, evaluating it). Same principle applies to memory-index trigger naming: trigger = situation, not antipattern label.

## When Splitting Decision Files With Memory-Index Entries

The validation script handles relocating memory-index entries to match their actual file locations. Do not manually move entries between sections during a file split — add new entries, let the validator handle section assignment.

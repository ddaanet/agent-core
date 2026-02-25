# Mandatory Conformance Validation

**Trigger:** When design includes external reference (shell prototype, API spec) in `Reference:` field.

**Requirement:** Runbook MUST include validation items that verify implementation conforms to the reference.

**Validation precision:**
- Use precise descriptions with exact expected strings from reference
- Example: "Output matches reference: `medal sonnet \033[35m...` with double-space separators"
- NOT abstracted: "Output contains formatted model with appropriate styling"

**Related:** See `agents/decisions/testing.md` "Conformance Validation for Migrations".

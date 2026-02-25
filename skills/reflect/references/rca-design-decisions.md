# RCA Design Decisions

Key design decisions for the reflect skill's diagnostic approach.

---

## Session-Local Diagnosis

RCA must run in the session where deviation occurred. The conversation context is the diagnostic evidence. A new session would need to reconstruct what happened from git history — lossy and unreliable.

## Opus Expected, Not Enforced

The skill assumes opus model for high-quality diagnosis. It cannot verify or switch the model — that's a user action. If invoked on sonnet, RCA quality will be lower but the process still works.

## Framing Block is Mandatory

Emitting the diagnostic-mode framing block is the first action, not optional. Without it, the agent continues in execution mode and applies surface fixes instead of systematic diagnosis.

## Diagnostic Before Fixes

Phase 4.5 checkpoint stops after presenting findings and before applying any changes. Anchored with Read calls per D+B hybrid pattern (implementation-notes.md). Follows multi-layer RCA stop pattern (operational-practices.md): analysis and remediation are separate decisions. The checkpoint enables `/recall` loading between diagnosis and fixes — the gap that caused the original deviation (no recall before fixing the design skill in-session).

## Three Exit Paths

Context budget varies. Sometimes the deviation is simple (fix a rule, 5 minutes). Sometimes root cause is a bad design requiring a new session. The skill supports graceful exit at any point, returning control to user.

## Returns Control After RCA

The skill runs in opus model (after user switches). Once RCA work is complete (fixes applied, reports written, or findings documented), it returns control to the user. This allows the user to switch back to their original model and continue working. User invokes `/handoff` and `/commit` manually when ready.

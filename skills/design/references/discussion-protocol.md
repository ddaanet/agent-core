# Discussion Protocol

Phase B of the design process: iterative discussion with user to validate approach.

## Phase B: Iterative Discussion

**Objective:** Validate approach with user before expensive design generation.

**Process:**
1. Open outline for user review: `open plans/<job>/outline.md`
2. User reads outline in editor, provides feedback in chat
3. Designer applies deltas to outline.md file (not inline conversation)
4. Re-review via outline-corrector after applying changes
5. Loop until user validates approach

**Plugin-topic detection (reminder):** If design involves Claude Code plugin components (hooks, agents, skills), note which skill to load before planning: "Plugin-topic: [component type] -- load plugin-dev:[skill-name] before planning."

**Termination:** If user feedback fundamentally changes the approach (not refining it), restart Phase A with updated understanding. Phase B is for convergence, not exploration of new directions.

**Convergence guidance:** If after 3 rounds the outline is not converging, ask user whether to proceed with current state or restart with different constraints.

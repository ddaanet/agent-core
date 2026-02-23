# Common Deviation Patterns

Catalog of recurring agent deviation patterns with diagnostic heuristics and fix strategies.

## Pattern Categories

### 1. Rationalization Deviations

**Agent rationalizes past clear directive despite unambiguous rule.**

#### Pattern 1A: Scope Creep Rationalization

**Symptoms:**
- Agent continues past stated boundary
- Justification: "This is closely related" or "Makes sense to do this too"
- Rule clearly says: "Stop at boundaries"

**Diagnostic heuristic:**
- Search for "Complete assigned task then stop" in `agent-core/fragments/communication.md`
- Check if agent added features/changes not in scope
- Look for rationalization language: "also," "while we're at it," "makes sense to"

**Root cause options:**
- Boundary not explicit enough (vague scope)
- Agent interpreted related work as same scope
- Missing "do NOT" prohibition

**Fix strategy:**
- Strengthen boundary language: "Do NOT add features not explicitly requested"
- Add explicit prohibition in rule
- If recurring: Create hookify rule to catch scope expansion

---

#### Pattern 1B: Exception Rationalization

**Symptoms:**
- Agent treats directive as guideline, not requirement
- Justification: "In this case it's okay because..."
- Rule clearly says: "Always" or "Never"

**Diagnostic heuristic:**
- Search for weak language: "avoid," "try to," "generally," "usually"
- Check if rule has explicit "no exceptions" clause
- Look for rationalization: "but," "however," "in this case"

**Root cause options:**
- Weak directive language ("avoid" instead of "do not")
- Missing "no exceptions" clause
- Contradictory guidance elsewhere

**Fix strategy:**
- Replace weak language: "avoid" → "do not," "try to" → "must"
- Add explicit "no exceptions" clause
- Reconcile contradictions if found

---

#### Pattern 1C: Tool Misuse Rationalization

**Symptoms:**
- Agent uses Bash for file operations when specialized tools exist
- Justification: "This is faster" or "Simpler this way"
- Rule clearly says: "Use Read/Write/Edit tools, not Bash"

**Diagnostic heuristic:**
- Check for `cat`, `echo >`, `sed`, `awk` in Bash calls
- Search for "Use Read instead of cat" in fragments
- Look for rationalization: "quicker," "easier," "simpler"

**Root cause options:**
- General knowledge overrides project directive
- Tool rule not loaded when needed
- Agent interpreted "prefer" as "optional"

**Fix strategy:**
- Strengthen language: "NEVER use Bash for X" or "ALWAYS use Tool Y"
- Move directive earlier in loaded context
- Add path-scoped rule file if pattern is file-type specific

---

### 2. Rule Discovery Failures

**Correct rule exists but wasn't loaded when needed.**

#### Pattern 2A: Path-Scoped Rule Not Triggered

**Symptoms:**
- Agent violates rule that should have auto-loaded
- Rule exists in `.claude/rules/[name].md` with path frontmatter
- Agent was editing files matching the path pattern

**Diagnostic heuristic:**
- Check `.claude/rules/` for relevant rule files
- Verify path pattern in frontmatter matches edited files
- Check if rule would have prevented deviation

**Root cause options:**
- Path pattern too specific (doesn't match actual files)
- Rule file exists but not in `.claude/rules/`
- Claude Code rule loading bug

**Fix strategy:**
- Broaden path pattern if too specific
- Verify rule file location
- If bug suspected: add to CLAUDE.md as fallback

---

#### Pattern 2B: Skill Not Loaded

**Symptoms:**
- Agent didn't invoke relevant skill
- Skill exists with trigger phrases
- User prompt matched trigger phrases

**Diagnostic heuristic:**
- Check skill's frontmatter description for trigger phrases
- Verify user prompt or task context contained trigger keywords
- Check if skill would have provided needed guidance

**Root cause options:**
- Trigger phrases too specific or uncommon
- Skill description doesn't mention common usage
- Agent interpreted task as not matching skill domain

**Fix strategy:**
- Add common trigger phrases to description
- Add examples of when to use skill
- Reference skill in CLAUDE.md or workflow fragments

---

### 3. Input-Driven Deviations

**Agent followed bad upstream document (design/plan/runbook).**

#### Pattern 3A: Design-Plan Mismatch

**Symptoms:**
- Runbook contradicts design document
- Agent implemented runbook step faithfully
- Design clearly specified different approach

**Diagnostic heuristic:**
- Read both design and runbook
- Identify contradictory sections
- Check runbook review report (should have caught this)

**Root cause options:**
- Planner misread design
- Design changed after runbook created
- Runbook not vetted properly

**Fix strategy:**
- Fix immediate contradiction in runbook
- Check if corrector was used (should be REQUIRED)
- Strengthen runbook review to catch design mismatches

---

#### Pattern 3B: Missing Prerequisite

**Symptoms:**
- Agent proceeded despite missing prerequisite
- Prerequisite section exists but not validated
- Failure occurred due to missing dependency

**Diagnostic heuristic:**
- Check runbook/plan for Prerequisites section
- Verify if prerequisite validation was performed
- Look for "assume" or "should exist" language

**Root cause options:**
- Prerequisite listed but validation skipped
- Prerequisite not listed (planning gap)
- Agent interpreted prerequisite as optional

**Fix strategy:**
- Add explicit validation step for prerequisites
- Change language: "Prerequisites (verify before execution)"
- Create checkpoint step: verify ALL prerequisites before Step 1

---

### 4. Context Overload

**Agent loses track of directive due to competing priorities.**

#### Pattern 4A: Buried Directive

**Symptoms:**
- Directive exists deep in loaded context
- Agent followed more recent or prominent guidance
- No contradiction — just priority confusion

**Diagnostic heuristic:**
- Measure distance from directive to violation point (messages)
- Check if directive repeated or reinforced
- Look for more prominent competing guidance

**Root cause options:**
- Directive mentioned once, buried in long document
- More recent message contradicted or overshadowed
- No reinforcement mechanism

**Fix strategy:**
- Move critical directives earlier/higher in context
- Add repetition at key decision points
- Create hookify rule for critical directives

---

#### Pattern 4B: Multi-Step Accumulation

**Symptoms:**
- Agent deviated on step N after N-1 successful steps
- Context includes all previous step transcripts
- Deviation matches pattern of "lost track"

**Diagnostic heuristic:**
- Count message turns from start to deviation
- Check if quiet execution pattern was used
- Look for cumulative context bloat

**Root cause options:**
- Not using quiet execution (reports to files)
- Orchestrator including too much step detail in delegation
- Context budget exhausted

**Fix strategy:**
- Enforce quiet execution pattern (agents report to files)
- Trim orchestrator delegation prompts (no full history)
- Split large plans into phases with session breaks

---

## Diagnostic Workflow

When analyzing a deviation:

1. **Identify category:** Which pattern category fits? (Rationalization / Discovery / Input / Context)
2. **Apply heuristics:** Follow diagnostic checks for suspected pattern
3. **Confirm root cause:** Use Grep/Read to verify hypothesis
4. **Select fix strategy:** Choose appropriate fix from pattern catalog
5. **Check for systemic:** Has this pattern occurred before? (Search learnings.md, memory-index.md)

## Systemic Pattern Indicators

**When is a deviation systemic?**

- Same pattern appears in multiple sessions (check `agents/learnings.md`)
- Same rule violated repeatedly despite fixes
- Multiple agents (haiku/sonnet/opus) exhibit same deviation
- Pattern affects core workflow (commit, handoff, planning, execution)

**Systemic pattern response:**

1. Create fragment in `agent-core/fragments/` (if behavioral rule)
2. Create decision doc in `agents/decisions/` (if technical pattern)
3. Add memory index entry pointing to fragment/doc
4. Consider hookify rule if enforcement needed
5. Update relevant skills to reference new fragment

## Anti-Pattern: Quick Fix Without Diagnosis

**Symptoms:**
- Deviation noticed
- Agent immediately proposes rule edit
- No analysis of why deviation happened
- No check for systemic pattern

**Why harmful:**
- Treats symptom, not cause
- Misses systemic patterns
- May create contradictions
- No learning accumulated

**Correct approach:**
- Always perform RCA first
- Check learnings.md and memory-index.md
- Identify root cause before fixing
- Consider systemic implications

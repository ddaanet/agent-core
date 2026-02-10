## Deslop

Strip output to its informational payload. Remove anything that doesn't advance understanding or function. Apply the deletion test: remove the sentence or construct — keep it only if information or behavior is lost.

### Prose

- State information directly — no hedging, framing, or preamble
  - ❌ "It's worth noting that the config is cached"
  - ✅ "The config is cached"
- Answer immediately — skip acknowledgments and transitions
  - ❌ "Great question! Let's dive into..."
  - ✅ (just the answer)
- Reference, never recap — assume the reader has context
  - ❌ "As we discussed above, the parser..."
  - ✅ "The parser..." or omit entirely
- Let results speak — no framing around output that's already visible
  - ❌ "Here's what I found:" followed by what you found
  - ✅ (just the findings)
- Commit to your answer — no hedging qualifiers after delivering it
  - ❌ "This is just one approach, there may be others"
  - ✅ (state alternatives only if they matter)

### Code

- Write docstrings only when they explain non-obvious behavior
  - ❌ `def get_name(): """Get the name."""`
  - ✅ `def get_name(): """Return cached display name, falling back to email."""`
- Write comments only when they explain *why*, never *what*
  - ❌ `i += 1  # increment i`
  - ✅ `i += 1  # skip header row`
- Let code structure communicate grouping — no section banners
  - ❌ `# --- Helper Functions ---`
  - ✅ (group by proximity and naming)
- Introduce abstractions only when a second use exists
  - ❌ Interface with one implementation, factory for one type
  - ✅ Direct implementation, extract when duplication appears
- Guard only against states that can actually occur
  - ❌ Null check on a value guaranteed non-null by caller
  - ✅ Guard at trust boundaries (user input, external data)
- Expose fields directly until access control is needed
  - ❌ Getter/setter that proxies a field with no logic
  - ✅ Direct attribute access, add property when behavior is needed
- Build for current requirements, extend when needed
  - ❌ Extension points nothing extends, config for two hardcoded values
  - ✅ Inline the simple case, refactor when complexity arrives

### Principle

Slop is the gap between what's expressed and what needed expressing. Deslopping is precision — cutting to the signal, not to the bone.

# Cache management for justfile help output.
# Used by CLAUDE.md @file references so agents know available recipes.
#
# FUTURE: When justfiles are factored to use agent-core includes,
# add the included files as dependencies here (e.g., justfile-base.just).

PARENT := ..
CACHE_DIR := $(PARENT)/.cache

TARGETS := $(CACHE_DIR)/just-help.txt $(CACHE_DIR)/just-help-agent-core.txt

.PHONY: help all check clean

help:
	@echo "This Makefile is used internally by 'just cache' and 'just precommit'."
	@echo "Use 'just help' to see available recipes."

all: $(TARGETS)

# Check that cached lists are up to date (exit non-zero if stale)
check:
	@$(MAKE) -q all 2>/dev/null || { echo "Stale cache: run 'just cache' or 'just dev'"; exit 1; }

clean:
	rm -f $(TARGETS)

$(CACHE_DIR)/just-help.txt: $(PARENT)/justfile | $(CACHE_DIR)
	cd $(PARENT) && just help > .cache/just-help.txt

$(CACHE_DIR)/just-help-agent-core.txt: justfile | $(CACHE_DIR)
	just help > $@

$(CACHE_DIR):
	mkdir -p $@

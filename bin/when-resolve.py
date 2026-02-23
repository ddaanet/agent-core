#!/usr/bin/env python3
"""Thin wrapper for the when CLI command.

Usage: when-resolve.py "when <query>" ["how <query>" ...]
"""

from claudeutils.when.cli import when_cmd

if __name__ == "__main__":
    when_cmd()

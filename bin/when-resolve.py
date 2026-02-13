#!/usr/bin/env python3
"""
Thin wrapper for the when/how CLI commands.

Usage: when-resolve.py {when|how} <query...>
"""

from claudeutils.when.cli import when_cmd

if __name__ == "__main__":
    when_cmd()

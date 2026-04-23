#!/usr/bin/env python3
"""
arifOS AAA MCP SEAL Check

Entry point for running as a module:
    python -m tests.seal_harness [options]
"""

from .cli import main

if __name__ == "__main__":
    main()

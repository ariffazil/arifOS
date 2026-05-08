#!/usr/bin/env python3
"""
WEALTH MCP entrypoint — thin wrapper around canonical internal/monolith.py
══════════════════════════════════════════════════════════════════════════

Per AGENTS.md Tier A registry, internal/monolith.py is the sole canonical
WEALTH implementation. This file exists only to preserve boot paths that
expect server.py at the repo root (Docker, Compose, CLI, docs).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from internal.monolith import *

if __name__ == "__main__":
    mcp.run()

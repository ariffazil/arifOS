# DEPRECATED - MCP v41.3 Entry Point

**Status:** ARCHIVED (replaced 2025-12-26)
**Reason:** Updated to v42 MCP server with unified 15-tool interface

---

## What Was Replaced

**Old Version (v41.3):**
- File: `arifos_mcp_entry_v41.3.py` (9.1KB, Dec 14, 2024)
- Mode: v0-strict with REAL APEX PRIME evaluation
- Surface Area: 1 tool (arifos_evaluate)
- Implementation: Custom legacy code

**New Version (v42):**
- File: `scripts/arifos_mcp_entry.py` (1.8KB, Dec 25, 2025)
- Mode: Full constitutional governance
- Surface Area: 15 tools (5 legacy + 10 constitutional pipeline)
- Implementation: Imports from arifos_core.mcp.server

---

## Migration

The v42 version uses the unified MCP server from `arifos_core/mcp/server.py` instead of custom implementation.

All tools are now consistently governed through the constitutional pipeline.

---

**DITEMPA BUKAN DIBERI** — Forged, not given

# MIGRATION_MAP.md — arifOS MCP Migration
**Generated:** 2026-05-25
**Phase:** PHASE 1 — Inventory
**DITEMPA BUKAN DIBERI**

---

## Architecture Decision

| Layer | Old (arifosmcp) | New (arifos_mcp) |
|-------|-----------------|-------------------|
| Package name | `arifos` (confusing) | `arifos-mcp` (clear) |
| Transport | HTTP-first, STDIO confusion | **STDIO native**, HTTP optional |
| Tool surface | 21 tools, inconsistent | **72 tools, typed contracts** |
| Governance | Scattered symbolic | **Central constitutional middleware** |
| Memory | Stub returns `{}` | **Honest status: healthy/degraded/unavailable** |
| Response shape | Inconsistent | **Single canonical envelope** |
| Error handling | Raw tracebacks | **Structured error envelope** |
| Registry | Multiple scattered | **One canonical registry** |

---

## Tool Count Breakdown

| Organ | Claimed | Implemented | Stub? | Notes |
|-------|---------|------------|-------|-------|
| Gateway | 2 | 2 | YES | mcp_health_check, mcp_drift_check — return hardcoded SEALS |
| Kernel | 13 | 13 | YES | All return dummy data, no real session/vault |
| GEOX | 11 | 11 | YES | All return hardcoded geological values |
| WEALTH | 32 | 32 | PARTIAL | 1 tool (wealth_ledger_write) has real F01 ack guard |
| WELL | 14 | 14 | YES | All return hardcoded vitality values |
| **TOTAL** | **72** | **72** | **ALL STUBS** | No real implementations |

---

## File Migration Map

| Old Path | New Path | Status | Action |
|----------|----------|--------|--------|
| `arifos_mcp/arifos_mcp/tools/canonical/kernel.py` | `arifos_mcp/arifos_mcp/tools/canonical/kernel.py` | PORT | Wire real implementations from live 8088 server |
| `arifos_mcp/arifos_mcp/tools/canonical/gateway.py` | `arifos_mcp/arifos_mcp/tools/canonical/gateway.py` | PORT | Implement mcp_drift_check with real registry count |
| `arifos_mcp/arifos_mcp/tools/canonical/geox.py` | `arifos_mcp/arifos_mcp/tools/canonical/geox.py` | REWRITE | Wire to live GEOX MCP at 8081 |
| `arifos_mcp/arifos_mcp/tools/canonical/wealth.py` | `arifos_mcp/arifos_mcp/tools/canonical/wealth.py` | REWRITE | Wire to live WEALTH MCP at 8082 |
| `arifos_mcp/arifos_mcp/tools/canonical/well.py` | `arifos_mcp/arifos_mcp/tools/canonical/well.py` | REWRITE | Wire to live WELL MCP at 8083 |
| `arifos_mcp/arifos_mcp/server/factory.py` | `arifos_mcp/arifos_mcp/server/factory.py` | REWRITE | Add real FastMCP middleware |
| `arifos_mcp/arifos_mcp/server/config.py` | `arifos_mcp/arifos_mcp/server/config.py` | KEEP | Good as-is |
| `arifos_mcp/arifos_mcp/transports/stdio.py` | `arifos_mcp/arifos_mcp/transports/stdio.py` | FIX | Make it actually work with FastMCP |
| `arifos_mcp/arifos_mcp/transports/streamable_http.py` | `arifos_mcp/arifos_mcp/transports/streamable_http.py` | KEEP | Mark as experimental |
| `arifos_mcp/arifos_mcp/schemas/tools.py` | `arifos_mcp/arifos_mcp/schemas/tools.py` | REWRITE | Add canonical response envelope |
| `arifos_mcp/arifos_mcp/manifests/` | `arifos_mcp/arifos_mcp/manifests/` | CREATE | Generate tools.json, resources.json, prompts.json |
| `arifOS/arifOS_mcp_runtime.py` | **DELETE** | DELETE | Legacy chaos |
| `arifOS/arifosd.py` | **DELETE** | DELETE | Legacy daemon |

---

## Transport Status

| Transport | Current Status | Target |
|----------|--------------|--------|
| STDIO | BROKEN — fastmcp not installed | PRIMARY — must work |
| HTTP | DISABLED in config | OPTIONAL — secondary |
| SSE | Not implemented | OPTIONAL |

---

## Critical Issues

1. **All 72 tools return dummy data** — no real system calls
2. **FastMCP not installed** in the VPS environment
3. **No session management** — session_id/actor_id not actually tracked
4. **No vault integration** — returns fake entry_ids
5. **No memory integration** — returns empty lists
6. **No real GEOX/WEALTH/WELL wiring** — all stubs
7. **HTTP disabled** but not removed cleanly

---

## Migration Sequence

1. **Install FastMCP** in arifos_mcp venv
2. **Test STDIO startup** — make it boring and working
3. **Wire kernel tools** to real implementations from live 8088 server
4. **Wire organ proxies** — GEOX→8081, WEALTH→8082, WELL→8083
5. **Implement canonical envelope** — all tools return same shape
6. **Add drift detection** — startup surface budget check
7. **Add constitutional middleware** — F01-F13 per tool
8. **Seal with tests**

---

## NOT MIGRATING (delete)

- `arifOS/arifOS_mcp_runtime.py` — duplicate, confusing
- `arifOS/arifosd.py` — old daemon, superseded
- `arifOS/arifos_wiki_tools/` — replace with proper wiki tools in arifos_mcp

*Ditempa Bukan Diberi — Intelligence is forged, not given.*

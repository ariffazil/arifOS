# FEDERATION_STATUS.md — arifOS Federation Live Status
> **Canonical Source of Truth:** `ariffazil/arifOS`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Last Verified:** 2026-05-25
> **Rule:** All other repo READMEs must point here for live/degraded/disabled status.

---

## Federation Organ Status

| Organ | Repo | Runtime Path | Port | Status | Notes |
|-------|------|-------------|------|--------|-------|
| **Constitutional Kernel** | `ariffazil/arifOS` | `/root/arifOS` | `8088` | ✅ OPERATIONAL | streamable-http, 13 tools, F1-F13 active |
| **AAA Control Plane** | `ariffazil/AAA` | `/root/AAA` | `3001` (A2A) | ✅ OPERATIONAL | Cockpit + A2A gateway |
| **GEOX Earth Intel** | `ariffazil/geox` | `/root/geox` | `18081` | ✅ OPERATIONAL | 28 canonical tools |
| **WEALTH Capital** | `ariffazil/wealth` | `/root/WEALTH` | `18082` | ✅ OPERATIONAL | 17 public MCP tools |
| **WELL Vitality** | `ariffazil/well` | `/root/WELL` | `18083` | ✅ OPERATIONAL | 45 live MCP tools (post PHOENIX-73F), 51 decorators, `streamable-http` at `https://well.arif-fazil.com/mcp` |
| **A-FORGE Execution** | `ariffazil/A-FORGE` | `/root/A-FORGE` | `7071` (bridge) | ✅ OPERATIONAL | TypeScript engine |
| **APEX Verdict** | `ariffazil/arifOS` (subdir) | `/root/APEX` | `3002` | ✅ OPERATIONAL | A2A deliberation |
| **HERMES ASI Relay** | `ariffazil/AAA` (agent) | — | — | ✅ OPERATIONAL | ASI judgment relay |

## Known Gaps / Degraded Services

| Service | Severity | Detail |
|---------|----------|--------|
| `graphiti-mcp` | ⚠️ PARTIAL | Container running but not remotely queryable. L5 entity graph via arifOS MCP only. |
| `langfuse` | WARNING | NOT_WIRED. Trace ingest degraded. jp.cloud.langfuse.com auth check failing. |
| `SEA-LION` | WARNING | Unreachable. Ollama local fallback active. Deterministic fallback enabled. |
| `vault999` | OK | Append-only ledger healthy. |

## Live Memory State

See `FEDERATION_MEMORY.md` for verified 6-layer memory map — live counts, agent access matrix, and known discrepancies vs. stale docs.

## MCP Multi-Client Concurrency Note

> **PHOENIX-73C:** The MCP SDK (streamable-http transport) uses a singleton SSE stream key. Only ONE SSE client can hold the stream per session at a time. Concurrent SSE attempts → `409 Conflict`. Clients should use POST-based JSON-RPC or implement reconnection with backoff. This is a transport-layer constraint of the MCP SDK, not an arifOS bug.

## Status Update Protocol

When status changes:
1. Update this file in `ariffazil/arifOS`
2. Commit with message: `docs(status): update federation status YYYY-MM-DD`
3. Notify via VAULT999 event

**Do not rely on individual repo READMEs for live status.** They may be stale.

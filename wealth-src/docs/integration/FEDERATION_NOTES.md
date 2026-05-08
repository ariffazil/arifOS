# FEDERATION_NOTES.md — WEALTH Integration State

> Domain-specific integration notes for WEALTH.
> Source: AAA/agents/hermes/MEMORY.md — canonical home is AAA.

## WEALTH MCP Status (2026-05-05)
- Server: wealth-organ container
- Port: 8082
- Transport: **SSE-only** (POST returns 405/406)
- Tools: 19 (verified from monolith.py)
- Public domain: wealth.arif-fazil.com

## Verified Integration Gap

### WEALTH SSE-Only Transport
**Problem:** arifOS (and likely other federation callers) cannot JSON-RPC POST to WEALTH.

```bash
# This fails (405 Method Not Allowed):
curl -X POST http://localhost:8082/mcp -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# This also fails (406 Not Acceptable):
curl -H "Accept: application/json" http://localhost:8082/mcp
```

**Why it matters:** arifOS has no SSE client implementation. Federation calls from arifOS to WEALTH fail silently or return error.
**Impact:** NPV/EMV/valuation tools cannot be called via arifOS gateway.

## What Works
- WEALTH MCP server is healthy and up
- 19 tools registered in monolith.py
- Caddy routing to wealth-organ:8082 is correct
- Direct SSE connection to wealth.arif-fazil.com/mcp works

## What Needs Fixing
Option A: Add SSE client to arifOS (recommended — arifOS should be able to call SSE servers)
Option B: Add POST endpoint to WEALTH (changes WEALTH transport contract)
Option C: Add HTTP gateway proxy in A-FORGE that converts REST→SSE

## Active Hold
- FED-SSE-001: federation transport mismatch; SSE client or transport adaptation required

## Routing
- Canonical home for full state: `AAA/agents/hermes/MEMORY.md`
- arifOS constitutional references: `arifOS/docs/canon/HERMES_AGENT_CANON.md`
- A-FORGE runtime audit: `A-FORGE/ops/runtime/HERMES_RUNTIME_AUDIT.md`

Last updated: 2026-05-05

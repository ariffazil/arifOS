# WEALTH Organ — Source of Truth
**Status:** MCP Live — Public streamable-http endpoint active

## Configuration
- **Canonical Git Source:** `/root/WEALTH` (Branch: `main`)
- **Deployment Mirror:** `/opt/arifos/src/wealth`
- **Runtime Entrypoint:** `internal/monolith.py` (AGENTS.md Tier A canonical)
- **Backward-Compat Wrapper:** `server.py`
- **Supplemental Surface:** `mcp/server.py`

## Public Surface
- `/` — Static human landing page
- `/health` — JSON health & status endpoint
- `/mcp` — Live MCP streamable-http endpoint (default transport)
- `/sse` — Optional SSE transport; enable via `MCP_TRANSPORT=sse`

## MCP Endpoint
- **URL:** `https://wealth.arif-fazil.com/mcp`
- **Transport:** streamable-http (FastMCP 3.2.0)
- **Status:** **SEALED** — returns real MCP JSON-RPC responses
- **Caddy Route:** `reverse_proxy /mcp* wealth-organ:8082`

## Operational Doctrine
- All long-term source changes MUST be committed to `/root/WEALTH`.
- `/opt/arifos/src/wealth` serves as the active build context and deployment target.
- Default transport is `streamable-http`; SSE is compatibility-only.

## Branch Policy
- **Canonical Branch:** `main`
- **Legacy Status:** `master` retired after unification commit `a9c0be0`.
- **Publishing:** `gh-pages` is publish-only, not source truth.

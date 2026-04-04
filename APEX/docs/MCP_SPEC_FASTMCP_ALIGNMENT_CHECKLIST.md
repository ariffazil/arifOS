# MCP + FastMCP Alignment Checklist (arifOS)

Last updated: 2026-02-22  
Scope: `aaa_mcp/*`, runtime entrypoints, REST adapter, container entrypoint

Pinned FastMCP runtime baseline: `3.0.1`

## Source Index

- MCP doc index: `https://modelcontextprotocol.io/llms.txt`
- MCP build-server guide: `https://modelcontextprotocol.io/docs/develop/build-server`
- MCP Inspector guide: `https://modelcontextprotocol.io/docs/tools/inspector`
- MCP spec (2025-11-25): `https://modelcontextprotocol.io/specification/2025-11-25/index`
- FastMCP doc index: `https://gofastmcp.com/llms.txt`
- FastMCP server guide: `https://gofastmcp.com/servers`
- FastMCP running-server guide: `https://gofastmcp.com/deployment/running-server`
- FastMCP client transports guide: `https://gofastmcp.com/clients/transports`

## Protocol Baseline

- Transport baseline:
  - `stdio` required for local MCP workflows
  - `http` preferred for remote streamable transport
  - `sse` treated as legacy compatibility path
- Capability baseline:
  - Tool listing and call must use MCP methods (`tools/list`, `tools/call`)
  - Stable tool schemas and JSON responses
  - Health/custom routes allowed alongside HTTP transport
- Server construction baseline:
  - One canonical FastMCP constructor path for runtime entrypoints

## arifOS Current Status

- [x] Canonical constructor exists: `aaa_mcp/server.py` → `create_unified_mcp_server()`
- [x] CLI uses canonical constructor: `aaa_mcp/__main__.py`
- [x] REST mode supported in CLI: `python -m aaa_mcp rest`
- [x] REST adapter calls canonical 5-organ tools internally
- [x] Legacy 9-verb names kept as HTTP aliases only
- [x] Streamable HTTP server aligned to canonical 5-organ tools + aliases
- [x] Docker entrypoint aligned to HTTP REST bridge (`python -m aaa_mcp rest`)
- [x] Contract tests added for entrypoint/alias drift prevention
- [x] Declarative FastMCP config exists: `fastmcp.json` (source/environment/deployment)

## Contract Tests (must stay green)

- `tests/test_entrypoint_contract.py`
- `tests/test_fastmcp_config_contract.py`
- `tests/integration/test_health_metrics.py`
- `tests/test_e2e_core_to_aaa_mcp.py`

Run:

```bash
.venv/Scripts/python.exe -m pytest \
  tests/test_entrypoint_contract.py \
  tests/test_fastmcp_config_contract.py \
  tests/integration/test_health_metrics.py \
  tests/test_e2e_core_to_aaa_mcp.py -q
```

## FastMCP-Specific Guardrails

- FastMCP server identity set via `FastMCP(name=...)`
- Runtime started via `mcp.run(...)` transport selection
- HTTP transport path remains primary for deployment
- SSE remains available only for compatibility (legacy clients)
- Keep tool registration deterministic; avoid duplicate registration paths
- Do not auto-start server on import; only start from explicit entrypoint (`python -m aaa_mcp ...`)
- For async contexts, use `run_async()` in dedicated async wrappers only

## Transport Policy (Aligned to FastMCP Running Guide)

- `stdio`: default local/dev and desktop-client compatibility path
- `http` (streamable): primary network/deployment transport
- `sse`: compatibility-only transport; not the default for new deployments

Current arifOS entrypoints:

- `python -m aaa_mcp stdio`
- `python -m aaa_mcp http`
- `python -m aaa_mcp rest` (REST bridge for external HTTP adapter usage)
- `python -m aaa_mcp sse` (legacy compatibility)
- `fastmcp run fastmcp.json` (declarative FastMCP project config)

## Client Transport Policy (Aligned to FastMCP Client Transports)

- STDIO clients must pass required env explicitly; do not assume inherited shell env.
- HTTP (`StreamableHttpTransport`) is preferred for remote production clients.
- SSE client transport is compatibility-only for older servers.
- In-memory client transport is preferred for unit/integration tests that do not need subprocess/network behavior.
- Multi-server client usage should namespace tools predictably and avoid name collisions.

## HTTP Deployment Notes (FastMCP)

- Remote deployment target should expose Streamable HTTP MCP endpoint at `/mcp/`
- Add health endpoint via `@mcp.custom_route("/health", ...)` when server is run as HTTP app
- For horizontally scaled deployments, prefer `stateless_http=True`
- Keep OAuth/auth configuration externalized via environment variables

## Inspector Validation Pass (manual)

Local stdio:

```bash
npx -y @modelcontextprotocol/inspector .venv/Scripts/python.exe -m aaa_mcp stdio
```

Verify:

- Tools tab lists canonical 5-organ API and expected utilities
- Tool schemas are stable and executable
- Notifications/logs show clean startup (no import errors)

## Non-Negotiable CI Gate

Fail CI if any of these regressions appear:

- `ImportError` on entrypoint startup
- REST/streamable adapters importing removed legacy Python symbols
- Docker CMD diverges from canonical entrypoint
- Alias map no longer resolves legacy names to canonical 5-organ tools

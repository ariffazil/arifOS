# arifOS v55.5 – Railway Deployment Playbook

This is the minimal, reproducible path to deploy the modernized MCP (Streamable HTTP) server on Railway and front it with Caddy/Cloudflare.

## Container
- Image builds from `Dockerfile` (Python 3.12-slim, FastMCP streamable HTTP).
- Entry point: `codebase-mcp-sse` (maps to `mcp.entrypoints.sse_entry:main`).
- Health endpoint: `GET /health` (exposed by `SSETransport`).
- Port: `PORT` (Railway default 8000). `HOST` defaults to `127.0.0.1` locally and is overridden to `0.0.0.0` in `railway.toml`.

## Railway settings
`railway.toml` (already committed):
```
[deploy]
startCommand = "codebase-mcp-sse"
healthcheckPath = "/health"
healthcheckTimeout = 120

[deploy.env]
HOST = "0.0.0.0"
ARIFOS_ENV = "production"
ARIFOS_VERSION = "v55.5-CODEBASE-AAA"
ARIFOS_LOG_LEVEL = "INFO"
ARIFOS_CLUSTER = "3"
REDIS_URL = "${{Redis.REDIS_URL}}"
```

## Caddy / Cloudflare
- `Caddyfile` already reverse-proxies to `localhost:8000` for both `mcp.arif-fazil.com` and `arifos.arif-fazil.com`.
- For MCP clients, set upstream path to `/` (FastMCP handles `/mcp` RPC + `/health` + `/metrics/json` internally).
- Behind Cloudflare, keep proxying enabled and allow SSE/streamable HTTP by turning on “WebSockets” and disabling HTML minify for `/mcp`.

## Smoke test after deploy
1) `curl -s https://mcp.arif-fazil.com/health` → expect `{ "status": "healthy", ... }`
2) `curl -s -X POST https://mcp.arif-fazil.com/mcp -d '{"jsonrpc":"2.0","id":"1","method":"list_tools","params":{}}' -H "Content-Type: application/json" -H "MCP-Protocol-Version: 2025-11-25"`
3) `curl -s https://mcp.arif-fazil.com/metrics/json`

## Rollback
- Git tag `v53.2.9-pre-v55` remains the rollback point: `git reset --hard v53.2.9-pre-v55`.

DITEMPA BUKAN DIBERI — Deploy with constitutional safeguards.

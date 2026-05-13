---
id: deployment
title: Deployment
sidebar_position: 3
description: Canonical VPS deployment for the current arifOS runtime MCP surface.
---

# Deployment

> Canonical production files: `docker-compose.yml`, `Dockerfile`, `.env.docker.example`, `prod.fastmcp.json`.

## Canonical VPS Path

Use the repo root compose file for production:

```bash
git clone https://github.com/ariffazil/arifosmcp.git /srv/arifOS
cd /srv/arifOS
cp .env.docker.example .env.docker
```

Set at minimum before exposing the service:

- `ARIFOS_GOVERNANCE_SECRET`
- `POSTGRES_PASSWORD`
- `GRAFANA_PASSWORD`
- `WEBHOOK_SECRET`

Temporary local/dev override:

- `ARIFOS_GOVERNANCE_OPEN_MODE=1` uses a fixed public development continuity key instead of a private governance secret.
- Use that only for single-instance local/dev work. Do not use it for production or shared deployments.

The default public tool profile is:

```env
ARIFOS_PUBLIC_TOOL_PROFILE=chatgpt
ARIFOS_MCP_PATH=/mcp
```

Start the stack:

```bash
docker compose up -d --build
```

## Public Runtime Contract

- Reverse proxy target: `http://127.0.0.1:8080`
- MCP endpoint: `/mcp`
- Health endpoint: `/health`
- Tools endpoint: `/tools`
- Well-known discovery: `/.well-known/mcp/server.json`
- Dashboard: `/dashboard/`

The public ChatGPT-safe profile exposes:

- `arifOS_kernel`
- `search_reality`
- `ingest_evidence`
- `session_memory`
- `audit_rules`
- `check_vital`
- `open_apex_dashboard`

Legacy compatibility aliases: `arifOS.kernel` and `metabolic_loop_router` map to `arifOS_kernel`.

If you need the full staged tool stack instead, override:

```env
ARIFOS_PUBLIC_TOOL_PROFILE=full
```

## Coolify / VPS Notes

- Use `docker-compose.yml` as the compose path.
- `docker-compose.override.yml` is dev-only.
- Mounted helper configs come from:
  - `deployment/hooks.json`
  - `infrastructure/deploy_from_git.sh`
  - `infrastructure/prometheus/prometheus.yml`
  - `infrastructure/grafana/datasources/prometheus.yml`

## Verification

Local on the VPS:

```bash
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:8080/tools
curl -fsS http://127.0.0.1:8080/.well-known/mcp/server.json
```

Public through your domain:

```bash
curl -i https://arifosmcp.arif-fazil.com/health
curl -i https://arifosmcp.arif-fazil.com/.well-known/mcp/server.json
curl -sS https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"deploy-check","version":"1.0"}}}'
```

## 888_HOLD

Before production rollout, confirm:

- The VPS has a real `.env.docker` with a strong `ARIFOS_GOVERNANCE_SECRET`
- Traefik or Nginx points `/mcp` to `127.0.0.1:8080`
- The repo clone includes the `infrastructure/` helper files used by compose mounts

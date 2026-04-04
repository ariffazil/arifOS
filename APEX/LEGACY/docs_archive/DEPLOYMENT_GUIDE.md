# Deployment Guide

This guide is the canonical deployment path for the latest arifOS AAA MCP runtime.

## Runtime Target

- Module: `arifos_aaa_mcp`
- Primary transport: `sse` on port `8080`
- Fallback transport: `http` on port `8089` (mapped to `/mcp` externally)
- Canonical MCP surface: 13 tools, 2 resources, 1 prompt

## VPS Deployment (Docker Compose)

Use:

- `deployment/docker-compose.vps.yml`
- `start-trinity.sh`
- `Dockerfile`

Bring up services:

```bash
docker compose -f deployment/docker-compose.vps.yml up -d --build
```

Check health:

```bash
curl -fsS http://localhost:8889/health
curl -N --max-time 2 http://localhost:8088/sse
```

## Required Environment

Create `.env.docker` from `.env.docker.example` and set at minimum:

- `ARIF_SECRET` (or `ARIF_JWT_SECRET`)
- `DATABASE_URL`
- `REDIS_URL`

Search grounding (optional but recommended):

- `PPLX_API_KEY` (preferred) or `PERPLEXITY_API_KEY`
- `PPLX_MODEL` (optional, default `sonar-pro`)
- `BRAVE_API_KEY` (fallback provider)

## Public Endpoints

- SSE: `https://<your-domain>/sse`
- MCP streamable HTTP: `https://<your-domain>/mcp`
- Health: `https://<your-domain>/health`

## CI/CD Notes

- Workflow: `.github/workflows/deploy.yml`
- Deploy path includes `arifos_aaa_mcp/**`
- VPS smoke check validates `python -m arifos_aaa_mcp sse`

## Registry Metadata

If publishing to MCP Registry, keep `server.json` aligned with runtime surface:

- resources: `arifos://aaa/schemas`, `arifos://aaa/full-context-pack`
- prompt: `arifos.prompt.aaa_chain`

---
id: mcp-server
title: MCP Server
sidebar_position: 2
description: Technical reference for the canonical arifOS AAA MCP runtime.
---

# arifOS AAA MCP Server

> Registry ID: `io.github.ariffazil/arifos-mcp`
> Live base URL: `https://arifosmcp.arif-fazil.com`
> Runtime module: `arifos_aaa_mcp`
> Version: `2026.2.27`

If you're wondering what an "MCP Server" is: **It's the bridge that connects an AI (like Claude or Cursor) to arifOS.** 

The Model Context Protocol (MCP) is a standard that lets AI models securely use external tools. arifOS runs its own MCP server so that any AI can connect to it and instantly be bound by the 13 constitutional floors.

## Runtime profile

- **Production transport:** Streamable HTTP (`/mcp`) — Current MCP standard
- **Local transport:** stdio — For Claude Desktop, Cursor IDE
- **Constitutional envelope:** 333 axioms + 13 laws + APEX dials
- **Port:** 8080 (default)
- **Current protocol version:** `2025-11-25`
- **Supported protocol versions:** `2025-11-25`, `2025-03-26`

## Version negotiation

Protocol version is negotiated during `initialize` and fixed per session.
If a client sends an unsupported version, the server returns a JSON-RPC error and no session is created.

## Launch commands (How to run it)

Depending on where you are running the AI, you start the server differently:

```bash
# Local stdio (for Claude Desktop, Cursor)
python -m arifos_aaa_mcp stdio

# Streamable HTTP (production - recommended)
HOST=0.0.0.0 PORT=8080 python -m arifos_aaa_mcp http
```

**Why streamable HTTP for production?**
Instead of complicated two-way communication channels, streamable HTTP means the AI and the server can talk securely over a standard web connection, which is much easier to scale in the cloud and protects against firewall blocks.

## Canonical MCP surface

### Tools (13)

| Tool | Purpose |
|:--|:--|
| `anchor_session` | 000 INIT: Start governed session |
| `reason_mind` | 333 REASON: AGI cognition |
| `recall_memory` | 444 EVIDENCE: Memory retrieval |
| `simulate_heart` | 555 EMPATHY: Impact analysis |
| `critique_thought` | 666 ALIGN: 7-model critique |
| `apex_judge` | 777/888 APEX: Constitutional verdict |
| `eureka_forge` | 888 FORGE: Execute with gates |
| `seal_vault` | 999 SEAL: Commit to ledger |
| `search_reality` | Web evidence discovery |
| `fetch_content` | Fetch raw content |
| `inspect_file` | Filesystem inspection |
| `audit_rules` | Rule compliance check |
| `check_vital` | System health metrics |

**Test live:** `curl https://arifosmcp.arif-fazil.com/health`

### Resources (2)

- `arifos://aaa/schemas`
- `arifos://aaa/full-context-pack`

### Prompt (1)

- `arifos.prompt.aaa_chain`

## Deployment files to keep aligned

- `Dockerfile`
- `start-trinity.sh`
- `docker-compose.yml`
- `deployment/docker-compose.vps.yml`
- `.github/workflows/deploy.yml`
- `server.json`

## Required secrets (minimum)

- `ARIF_SECRET` or `ARIF_JWT_SECRET`
- `DATABASE_URL`
- `REDIS_URL`

Optional web grounding:

- `PPLX_API_KEY` (preferred) or `PERPLEXITY_API_KEY`
- `PPLX_MODEL` (default `sonar-pro`)
- `BRAVE_API_KEY` (fallback)

---
sidebar_position: 2
title: Connection
description: How to connect to arifOS MCP server
---

# MCP Connection

## Live Server

| Property | Value |
|----------|-------|
| **SSE Endpoint** | `https://arifos.arif-fazil.com/sse` |
| **Messages** | `https://arifos.arif-fazil.com/messages` |
| **Health** | `https://arifos.arif-fazil.com/health` |
| **Transport** | Server-Sent Events (SSE) |
| **Docs** | `https://arifos.arif-fazil.com/docs` |
| **Dashboard** | `https://arifos.arif-fazil.com/dashboard` |
| **Metrics** | `https://arifos.arif-fazil.com/metrics/json` |
| **Checkpoint** | `https://arifos.arif-fazil.com/checkpoint` |

## Claude Desktop

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```

Restart Claude Desktop after editing.

## Claude Code (VS Code Extension)

Create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "arifOS-Remote": {
      "url": "https://arifos.arif-fazil.com/sse"
    },
    "arifOS-Local": {
      "command": "python",
      "args": ["-m", "arifos.mcp"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

## Cursor IDE

Create `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```

## Local Server

### Start the Server

```bash
# Install
pip install arifos

# Run SSE server
# Run SSE server (Production)
python -m arifos.mcp sse

# Run Stdio server (Local Development)
python -m arifos.mcp trinity
```

### Local Config

```json
{
  "mcpServers": {
    "arifOS-Local": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `ARIFOS_ENV` | `dev` | Environment mode (dev/production) |
| `ARIFOS_VAULT_PATH` | `VAULT999` | Constitutional config path |
| `ARIFOS_LEDGER_PATH` | `VAULT999/BBB_LEDGER` | Cooling ledger path |

## Health Check

```bash
curl https://arifos.arif-fazil.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "v52.5.1-SEAL",
  "motto": "DITEMPA BUKAN DIBERI",
  "endpoints": {
    "sse": "/sse",
    "messages": "/messages",
    "health": "/health",
    "docs": "/docs",
    "dashboard": "/dashboard",
    "metrics": "/metrics/json",
    "checkpoint": "/checkpoint"
  }
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check if server is running |
| 404 on /sse | Verify URL doesn't have trailing slash |
| Tools not showing | Restart client after config change |
| Timeout | Check firewall/network settings |

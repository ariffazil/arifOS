---
sidebar_position: 2
title: Connection
description: How to connect to arifOS MCP server
---

# MCP Connection

## Live Server

| Property | Value |
|----------|-------|
| **MCP Endpoint** | `https://arifos.arif-fazil.com/mcp` |
| **Health** | `https://arifos.arif-fazil.com/health` |
| **Dashboard** | `https://arifos.arif-fazil.com/dashboard` |
| **Metrics** | `https://arifos.arif-fazil.com/metrics/json` |
| **Discovery** | `https://arifos.arif-fazil.com/` |
| **Transport** | Streamable HTTP (MCP 2024-11-05+) |

:::info Migrated from SSE
Previous versions used `/sse` + `/messages` (SSE transport). v53.2.1 uses `/mcp` (Streamable HTTP — single POST endpoint). The old `/checkpoint`, `/docs`, and `/openapi.json` endpoints have been removed.
:::

## Claude Desktop

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
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
      "url": "https://arifos.arif-fazil.com/mcp"
    },
    "arifOS-Local": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
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
      "url": "https://arifos.arif-fazil.com/mcp"
    }
  }
}
```

## Kimi CLI

Edit `~/.kimi/mcp_config.json`:

```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

:::note
Kimi CLI requires both `cwd` and `PYTHONPATH` to resolve the `codebase.mcp` module correctly.
:::

## Gemini CLI

Edit `~/.gemini/settings.json` (or `~/.gemini/antigravity/mcp_config.json` for Antigravity mode):

```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

## ChatGPT Developer Mode / OpenAI Codex

These clients connect via **HTTP** to the live server:

```
MCP Endpoint: https://arifos.arif-fazil.com/mcp
Transport: Streamable HTTP (POST)
```

In ChatGPT Developer Mode, add the MCP server URL in the **Actions** or **MCP** settings panel.

## Local Server

### Start the Server

```bash
# Install
pip install -e .

# Run HTTP server (Production/Remote)
codebase-mcp-sse

# Run stdio server (Local Development — used by Claude Desktop, Kimi, Gemini)
python -m codebase.mcp
```

### Local Config (HTTP)

```json
{
  "mcpServers": {
    "arifOS-Local": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `ARIFOS_ENV` | `dev` | Environment mode (dev/production) |
| `ARIFOS_VERSION` | `v53.2.1-CODEBASE` | Version identifier |
| `ARIFOS_LOG_LEVEL` | `INFO` | Logging level |
| `ARIFOS_RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |

## Health Check

```bash
curl https://arifos.arif-fazil.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "v53.2.1-CODEBASE",
  "mode": "CODEBASE",
  "transport": "streamable-http",
  "tools": 6,
  "architecture": "v53.2.1-simplified"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check if server is running (`curl /health`) |
| 404 on /sse | **Deprecated** — use `/mcp` instead (v53.2.1+) |
| 404 on /mcp | Verify URL has no trailing slash |
| Tools not showing | Restart client after config change |
| Timeout | Check firewall/network settings |
| Rate limit exceeded | Wait for cooldown or check `ARIFOS_RATE_LIMIT_ENABLED` |
| Module not found | Ensure `cwd` and `PYTHONPATH` are set correctly |

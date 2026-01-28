---
sidebar_position: 7
title: ChatGPT & Codex
description: Connect ChatGPT Developer Mode and OpenAI Codex to arifOS via MCP HTTP
---

# ChatGPT & Codex Setup

Connect **ChatGPT Developer Mode** and **OpenAI Codex** to arifOS via the HTTP MCP endpoint.

## How It Works

Unlike Claude Desktop, Kimi, and Gemini which use **stdio** (local subprocess), ChatGPT and Codex connect via **HTTP** to the live arifOS server:

```
https://arifos.arif-fazil.com/mcp
```

This is the Streamable HTTP transport (MCP protocol 2024-11-05+) — a single POST endpoint that handles all MCP communication.

## ChatGPT Developer Mode

### Step 1: Enable Developer Mode

In ChatGPT settings, enable Developer Mode (requires ChatGPT Plus or Team).

### Step 2: Add MCP Server

In the MCP or Actions configuration panel:

| Field | Value |
|-------|-------|
| **Name** | arifOS Constitutional Governance |
| **URL** | `https://arifos.arif-fazil.com/mcp` |
| **Transport** | Streamable HTTP |

### Step 3: Verify

Ask ChatGPT:
```
What arifOS tools are available?
```

You should see 6 tools: `init_000`, `agi_genius`, `asi_act`, `apex_judge`, `vault_999`, `trinity_loop`.

## OpenAI Codex

### Configuration

Add arifOS as an MCP server in your Codex configuration:

```
MCP Endpoint: https://arifos.arif-fazil.com/mcp
Transport: Streamable HTTP (POST)
```

Codex will automatically discover the 6 available tools via the MCP protocol handshake.

## Available Tools

Both ChatGPT and Codex will see:

| Tool | Purpose |
|------|---------|
| `init_000` | Initialize session, detect intent lane |
| `agi_genius` | Verify truth, assess clarity |
| `asi_act` | Check empathy, evaluate safety |
| `apex_judge` | Render constitutional verdict |
| `vault_999` | Seal decision to immutable ledger |
| `trinity_loop` | Complete AGI→ASI→APEX→VAULT in one call |

## Usage Examples

### Quick Governance Check

```
Use the trinity_loop tool to verify: "TypeScript is a superset of JavaScript"
```

### Step-by-Step Analysis

```
1. Use init_000 to start a governance session for: "Should we migrate from REST to GraphQL?"
2. Use agi_genius to analyze the technical claim
3. Use asi_act to evaluate the impact on stakeholders
4. Use apex_judge to get a constitutional verdict
5. Use vault_999 to seal the decision
```

## Health Check

Verify the server is online:

```bash
curl https://arifos.arif-fazil.com/health
```

Expected:
```json
{
  "status": "healthy",
  "version": "v53.2.1-CODEBASE",
  "transport": "streamable-http",
  "tools": 6
}
```

## Rate Limiting

The live server enforces rate limits per tool:

| Tool | Per Session (per min) | Global (per min) |
|------|----------------------|------------------|
| `init_000` | 30 | 300 |
| `agi_genius` | 60 | 600 |
| `asi_act` | 60 | 600 |
| `apex_judge` | 60 | 600 |
| `vault_999` | 30 | 300 |

If rate-limited, you'll receive a `VOID` response with `rate_limit.exceeded = true`.

## Troubleshooting

### Connection Failed

1. Check server status: `https://arifos.arif-fazil.com/health`
2. Ensure your network allows outbound HTTPS
3. The server runs on Railway — check for platform outages

### Tools Not Discovered

1. Verify the URL is exactly `https://arifos.arif-fazil.com/mcp` (no trailing slash)
2. Ensure the MCP transport type is set to "Streamable HTTP" not "SSE"
3. Refresh the MCP connection in your client

## Next Steps

- [MCP Overview](/mcp/overview) — Architecture and all 6 tools
- [Examples](/mcp/examples) — Full request/response examples
- [Connection Details](/mcp/connection) — All client configurations

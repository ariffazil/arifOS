---
sidebar_position: 1
title: Quick Start
description: Get arifOS running in 5 minutes
---

# Quick Start

Get arifOS governance running in 5 minutes. Choose your path:

## Option 1: Copy-Paste System Prompt (Easiest)

Works with **any AI** — ChatGPT, Claude, Gemini, etc.

1. Go to [System Prompt](/ai/system-prompt)
2. Copy the entire prompt
3. Paste into your AI's "Custom Instructions" or "System Prompt" field

| Platform | Where to Paste |
|----------|----------------|
| **ChatGPT** | Settings → Personalization → Custom Instructions |
| **Claude** | Start of conversation or Project instructions |
| **Gemini** | Conversation starter or system message |

That's it! The AI will now self-govern using TEACH principles.

---

## Option 2: MCP Connection (Claude Desktop/Cursor)

Connect your AI client directly to the live arifOS server.

### Claude Desktop

Edit `claude_desktop_config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/mcp"
    }
  }
}
```

Restart Claude Desktop. You should see "arifOS" in the MCP tools list.

### Cursor IDE

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

---

## Option 3: Install Locally

Run your own arifOS server:

```bash
# Install from PyPI
pip install arifos

# Run MCP server (stdio mode)
python -m codebase.mcp

# Or run HTTP server (for remote connections)
codebase-mcp-sse
```

Then configure your client to connect to `http://localhost:8000/mcp`.

---

## Verify It Works

### Check Live Server Health

```bash
curl https://arifos.arif-fazil.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "v53.2.1-CODEBASE",
  "transport": "streamable-http",
  "tools": 6
}
```

### Test Governance

With MCP connected, the AI will:
- Call `init_000` at session start
- Route through `agi_genius` → `asi_act` → `apex_judge`
- Seal decisions with `vault_999`

You should see verdicts like **SEAL**, **SABAR**, **VOID**, or **888_HOLD** in responses.

---

## Next Steps

- [Installation](/getting-started/installation) — Detailed installation options
- [First Governance Check](/getting-started/first-check) — Hands-on tutorial
- [TEACH Framework](/concepts/teach) — Understand the 5 principles

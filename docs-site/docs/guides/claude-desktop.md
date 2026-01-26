---
sidebar_position: 2
title: Claude Desktop
description: Connect Claude Desktop to arifOS via MCP
---

# Claude Desktop Setup

Connect Claude Desktop to arifOS for constitutional AI governance with full MCP integration.

## Prerequisites

- [Claude Desktop](https://claude.ai/download) installed
- macOS, Windows, or Linux

## Configuration

### Step 1: Locate Config File

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/claude/claude_desktop_config.json
```

### Step 2: Add arifOS Server

Open the config file and add:

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```

### Step 3: Restart Claude Desktop

Completely quit and reopen Claude Desktop. The arifOS tools should now appear.

## Verify Connection

After restarting, you should see 5 new tools available:

| Tool | Icon | Purpose |
|------|------|---------|
| `init_000` | 🚪 | Initialize session |
| `agi_genius` | 🧠 | Truth & reasoning |
| `asi_act` | ❤️ | Empathy & safety |
| `apex_judge` | ⚖️ | Final verdict |
| `vault_999` | 🔒 | Seal decision |

## Usage Example

Once connected, Claude will automatically use arifOS tools when appropriate. Try:

> "Use the arifOS tools to verify: What is the capital of France?"

Claude will:
1. Call `init_000` to initialize
2. Call `agi_genius` to verify truth
3. Call `asi_act` to check empathy
4. Call `apex_judge` for verdict
5. Call `vault_999` to seal

## Local Server Option

For lower latency or offline use, run arifOS locally:

### Step 1: Install arifOS

```bash
pip install arifos
```

### Step 2: Update Config

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python",
      "args": ["-m", "arifos.mcp"]
    }
  }
}
```

### Step 3: Restart Claude Desktop

The local server will start automatically when Claude Desktop launches.

## Troubleshooting

### Tools Not Appearing

1. **Check JSON syntax** — Use a JSON validator
2. **Check file location** — Must be in the exact path for your OS
3. **Restart completely** — Quit Claude Desktop fully, then reopen

### Connection Refused

1. **Check server status**: Visit https://arifos.arif-fazil.com/health
2. **Check firewall**: Ensure outbound HTTPS is allowed
3. **Try local server**: Use the local installation method above

### Tool Calls Failing

Check the response for floor violations:

```json
{
  "verdict": "VOID",
  "reason": "F2 (Truth) failed",
  "floor_summary": {
    "failed": ["F2"]
  }
}
```

This means the governance system is working correctly!

## Advanced Configuration

### Multiple MCP Servers

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/sse"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    }
  }
}
```

### Custom Timeout

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/sse",
      "timeout": 30000
    }
  }
}
```

## Next Steps

- [Claude Code Setup](/guides/claude-code) — Terminal-based Claude
- [Python Integration](/guides/python) — Programmatic access
- [MCP Examples](/mcp/examples) — Request/response examples

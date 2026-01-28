---
sidebar_position: 5
title: Kimi CLI
description: Connect Kimi CLI to arifOS via MCP
---

# Kimi CLI Setup

Connect [Kimi CLI](https://github.com/anthropics/kimi) to arifOS for constitutional AI governance.

## Prerequisites

- Kimi CLI installed
- Python 3.10+ with arifOS source code available
- Node.js (for Kimi's MCP subprocess management)

## Configuration

### Step 1: Locate Config File

Kimi CLI uses `~/.kimi/mcp_config.json` for MCP server configuration.

**All platforms:**
```
~/.kimi/mcp_config.json
```

### Step 2: Add arifOS Server

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

:::caution Important: cwd and PYTHONPATH
Unlike Claude Desktop or Cursor, Kimi CLI requires **both** `cwd` and `PYTHONPATH` to be set explicitly. Without these, Python cannot resolve the `codebase.mcp` module.

**Windows example:**
```json
{
  "cwd": "C:/Users/User/arifOS",
  "env": {
    "PYTHONPATH": "C:/Users/User/arifOS",
    "PYTHONIOENCODING": "utf-8"
  }
}
```
:::

### Step 3: Restart Kimi CLI

Close and reopen your Kimi CLI session to load the new configuration.

## Verify Connection

Start Kimi CLI and ask:

```
> What MCP tools are available?
```

You should see 6 tools:
- `init_000` — System ignition
- `agi_genius` — Mind (truth, clarity)
- `asi_act` — Heart (empathy, safety)
- `apex_judge` — Soul (verdict)
- `vault_999` — Seal (ledger)
- `trinity_loop` — Full pipeline in one call

## Usage

Kimi CLI will automatically use arifOS tools when it detects governance-relevant queries. You can also invoke them explicitly:

```
> Use arifOS to verify: "The Earth orbits the Sun in exactly 365 days"
```

Or use the one-shot pipeline:

```
> Use trinity_loop to check: "React uses a virtual DOM for efficient rendering"
```

## Troubleshooting

### Module Not Found

If you see `ModuleNotFoundError: No module named 'codebase'`:

1. Verify `cwd` points to the arifOS project root
2. Verify `PYTHONPATH` matches `cwd`
3. Ensure `codebase/mcp/__init__.py` exists in the project

### Tools Not Appearing

1. Check JSON syntax in `~/.kimi/mcp_config.json`
2. Restart Kimi CLI completely
3. Check Kimi CLI version supports MCP

## Next Steps

- [Gemini CLI Setup](/guides/gemini) — Google's AI CLI
- [MCP Overview](/mcp/overview) — Architecture and all 6 tools
- [Examples](/mcp/examples) — Request/response examples

---
sidebar_position: 6
title: Gemini CLI
description: Connect Gemini CLI to arifOS via MCP
---

# Gemini CLI Setup

Connect [Gemini CLI](https://github.com/google-gemini/gemini-cli) to arifOS for constitutional AI governance.

## Prerequisites

- Gemini CLI installed (`npm install -g @anthropic/gemini-cli` or similar)
- Python 3.10+ with arifOS source code available

## Configuration

### Step 1: Locate Config File

Gemini CLI supports MCP configuration in:

**Standard mode:**
```
~/.gemini/settings.json
```

**Antigravity mode:**
```
~/.gemini/antigravity/mcp_config.json
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
Like Kimi CLI, Gemini CLI requires **both** `cwd` and `PYTHONPATH` to be set explicitly for the `codebase.mcp` module to resolve correctly.

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

### Step 3: Restart Gemini CLI

Close and reopen your Gemini CLI session.

## Verify Connection

Start Gemini CLI and ask:

```
> What MCP tools are available?
```

You should see 6 arifOS tools:
- `init_000` — System ignition
- `agi_genius` — Mind (truth, clarity)
- `asi_act` — Heart (empathy, safety)
- `apex_judge` — Soul (verdict)
- `vault_999` — Seal (ledger)
- `trinity_loop` — Full pipeline in one call

## Antigravity Mode

Gemini CLI's Antigravity mode uses a separate config directory (`~/.gemini/antigravity/`). If you're using Antigravity mode, place your MCP config in:

```
~/.gemini/antigravity/mcp_config.json
```

The JSON format is identical to standard mode.

## Usage

Gemini CLI will use arifOS tools when it detects governance-relevant queries:

```
> Use arifOS to check: "Python's GIL prevents all parallel execution"
```

Or use the unified pipeline:

```
> Run trinity_loop on: "Docker containers share the host kernel"
```

## Troubleshooting

### Module Not Found

If you see `ModuleNotFoundError: No module named 'codebase'`:

1. Verify `cwd` points to the arifOS project root
2. Verify `PYTHONPATH` matches `cwd`
3. Check that `codebase/mcp/__init__.py` exists

### Config Not Loading

1. Verify JSON syntax
2. Check which mode you're running (standard vs Antigravity)
3. Ensure config file is in the correct directory for your mode

## Next Steps

- [ChatGPT/Codex Setup](/guides/chatgpt) — HTTP-based connection
- [MCP Overview](/mcp/overview) — Architecture and all 6 tools
- [Examples](/mcp/examples) — Request/response examples

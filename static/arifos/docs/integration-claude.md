---
id: integration-claude
title: Claude Desktop
sidebar_position: 1
description: Connect arifOS to Claude Desktop via MCP for local constitutional governance
---

# Claude Desktop Integration

Connect **arifOS** to [Claude Desktop](https://www.claude.com/download) via the Model Context Protocol (MCP) for local constitutional AI governance.

---

## Overview

Claude Desktop supports MCP servers through **STDIO transport** for local execution. This integration allows Claude to access arifOS's 13 Constitutional Floors and the unified 8-tool public contract directly on your machine.

:::tip Requirements
- **Claude Desktop** installed (macOS or Windows)
- **Python 3.12+** with `pip`
- **arifOS** package: `pip install arifos`
:::

---

## Quick Install

### Option 1: FastMCP CLI (Recommended)

If you have `fastmcp` installed globally:

```bash
fastmcp install claude-desktop arifos
```

### Option 2: Manual Configuration

Add arifOS to Claude Desktop's MCP configuration:

**macOS:**
```bash
~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Configuration:**
```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python",
      "args": ["-m", "arifosmcp.runtime", "stdio"],
      "env": {
        "ARIFOS_GOVERNANCE_SECRET": "your-secret-key",
        "JINA_API_KEY": "your-jina-key",
        "PERPLEXITY_API_KEY": "your-perplexity-key",
        "BRAVE_API_KEY": "your-brave-key"
      }
    }
  }
}
```

:::warning Environment Variables
Claude Desktop runs in an isolated environment. You **must** explicitly pass all environment variables your server needs:

- `ARIFOS_GOVERNANCE_SECRET` — Required for governance token signing
- `JINA_API_KEY` — For Jina Reader search (recommended)
- `PERPLEXITY_API_KEY` — For Perplexity search fallback
- `BRAVE_API_KEY` — For Brave search fallback
:::

---

## Installation with Dependencies

If you need additional Python packages for your use case:

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "uv",
      "args": [
        "run",
        "--with", "arifos",
        "--with", "sentence-transformers",
        "python", "-m", "arifosmcp.runtime", "stdio"
      ],
      "env": {
        "ARIFOS_GOVERNANCE_SECRET": "your-secret-key",
        "ARIFOS_ML_FLOORS": "1"
      }
    }
  }
}
```

---

## Verify Installation

1. **Restart Claude Desktop** completely
2. Look for the **hammer icon** (🔨) in the bottom-left of the input box
3. Click it to see available arifOS tools:
   - `bootstrap_identity` — Explicit onboarding
   - `arifOS_kernel` — Main governed execution entrypoint
   - `search_reality` — Web search with F2 Truth verification
   - `check_vital` — Health and telemetry
   - ... plus the remaining public tools

---

## Usage Examples

### Constitutional Web Search

Ask Claude:
> "Search for recent advances in quantum computing and verify the facts with arifOS"

Claude will:
1. Call `search_reality` via arifOS
2. Jina Reader extracts clean Markdown from web results
3. F2 Truth floor validates evidence quality
4. Results wrapped in F12 Defense envelope

### Risk-Classified Command Execution

Ask Claude:
> "List all files in my home directory"

Claude will:
1. Call `eureka_forge` with command `ls ~`
2. Risk classified as LOW (read-only)
3. Executes immediately with audit logging

Ask Claude:
> "Delete all files in /tmp"

Claude will:
1. Call `eureka_forge` with command `rm -rf /tmp/*`
2. Risk classified as CRITICAL (destructive)
3. **888_HOLD triggered** — Requires human confirmation
4. Must call `confirm_dangerous=True` with explicit intent

---

## Constitutional Guarantees

When using arifOS through Claude Desktop, every action is governed by:

| Floor | Guarantee |
|-------|-----------|
| **F1 Amanah** | All actions are reversible and auditable |
| **F2 Truth** | Web grounding with τ≥0.99 evidence threshold |
| **F4 Clarity** | Output must reduce information entropy (ΔS ≤ 0) |
| **F7 Humility** | Explicit uncertainty markers when τ < 0.99 |
| **F12 Defense** | External content wrapped in untrusted envelope |
| **F13 Sovereignty** | Human has final veto on all critical actions |

---

## Troubleshooting

### "Server not found" or hammer icon missing

1. Check configuration file syntax (valid JSON)
2. Ensure `python` is in your PATH
3. Try full path to Python executable
4. Restart Claude Desktop completely

### "NO_API_KEY" in search results

Add search API keys to environment:
```json
"env": {
  "JINA_API_KEY": "jina_...",
  "PERPLEXITY_API_KEY": "pplx_...",
  "BRAVE_API_KEY": "BSA..."
}
```

Get free API keys:
- **Jina Reader**: https://jina.ai (10M free tokens)
- **Perplexity**: https://perplexity.ai
- **Brave**: https://brave.com/search/api

### Governance token errors

`ARIFOS_GOVERNANCE_SECRET` is required for continuity signing and critical action confirmation.

Generate a secret:
```bash
openssl rand -hex 32
```

---

## Advanced: Remote Server via Proxy

If you want to connect to a remote arifOS server:

1. Create a proxy server locally:

```python proxy_server.py
from fastmcp.server import create_proxy

proxy = create_proxy(
    "https://arifosmcp.arif-fazil.com/mcp",
    name="arifOS Remote"
)

if __name__ == "__main__":
    proxy.run()  # STDIO for Claude Desktop
```

2. Install the proxy in Claude Desktop

---

## Next Steps

- [Public Contract](/public-contract) — Understand the 8 public tools
- [Governance](/governance) — Learn the 13 Constitutional Floors
- [API Reference](/api) — Complete tool documentation

---

*Ditempa Bukan Diberi — Forged, Not Given*

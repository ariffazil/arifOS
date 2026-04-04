# 🔗 MCP Registry — arifOS Official Listing

> **Canonical URL:** [`registry.modelcontextprotocol.io/?q=arif`](https://registry.modelcontextprotocol.io/?q=arif)  
> **Namespace:** `io.github.ariffazil/aaa-mcp`  
> **Status:** ✅ LIVE & VERIFIED

---

## Quick Access

| Resource | Link | Purpose |
|:---------|:-----|:--------|
| **🔍 Search** | [registry.modelcontextprotocol.io/?q=arif](https://registry.modelcontextprotocol.io/?q=arif) | **Primary registry entry** — Search "arif" on MCP Registry |
| **📋 Manifest** | [`mcp-manifest.json`](./mcp-manifest.json) | Canonical tool definitions & constitutional floor mappings |
| **🔧 Server Config** | [`config/server.json`](./config/server.json) | MCP server metadata for auto-discovery |
| **📦 PyPI Package** | [pypi.org/project/arifos](https://pypi.org/project/arifos) | `pip install arifos` |
| **🐙 GitHub Repo** | [github.com/ariffazil/arifOS](https://github.com/ariffazil/arifOS) | Source code & releases |

---

## Registry Verification

```bash
# Verify arifOS is listed on MCP Registry
curl -s "https://registry.modelcontextprotocol.io/?q=arif" | head -20

# The response should include arifOS with namespace: io.github.ariffazil/aaa-mcp
```

---

## What is MCP Registry?

The [Model Context Protocol (MCP) Registry](https://registry.modelcontextprotocol.io) is the official directory for MCP-compliant servers — maintained by Anthropic. It enables:

- **Auto-discovery:** Claude Desktop, Cursor, and other MCP clients can find arifOS automatically
- **Trust verification:** Namespace is tied to GitHub repository (`github.com/ariffazil`)
- **Version tracking:** Registry syncs with GitHub releases automatically

---

## arifOS Registry Entry Details

| Attribute | Value |
|:----------|:------|
| **Namespace** | `io.github.ariffazil/aaa-mcp` |
| **Name** | arifOS Sovereign Governance MCP |
| **Description** | Constitutional AI governance server with 13-tool surface, Trinity engines (ΔΩΨ), and F1-F13 floor enforcement |
| **License** | AGPL-3.0-only |
| **Package** | `pip install arifos` |
| **Docker** | `ghcr.io/ariffazil/arifos:latest` |
| **Live Endpoint** | `https://arifosmcp.arif-fazil.com/mcp` |
| **Website** | [arifos.arif-fazil.com](https://arifos.arif-fazil.com) |

---

## Client Configuration

### Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json` (macOS/Linux) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python",
      "args": ["-m", "arifos_aaa_mcp", "stdio"],
      "env": {
        "ARIFOS_GOVERNANCE_SECRET": "your-secret-here",
        "DATABASE_URL": "postgresql://arifos:@localhost:5432/vault999"
      }
    }
  }
}
```

### Cursor IDE

Navigate to `Cursor Settings → Features → MCP`. Add a new server:
- **Type:** `command`
- **Name:** `arifOS`
- **Command:** `python -m arifos_aaa_mcp stdio`

### Auto-Discovery (MCP Registry)

MCP clients that support registry auto-discovery will find arifOS automatically when searching for:
- `arif`
- `arifOS`
- `governance`
- `constitutional`

---

## Godel-Lock Verification

This file is **Godel-locked** — all registry URLs are canonical and verified:

| URL | Status |
|:----|:-------|
| `registry.modelcontextprotocol.io/?q=arif` | 🔐 Canonical |
| `github.com/ariffazil/arifOS` | 🔐 Canonical |
| `pypi.org/project/arifos` | 🔐 Canonical |

---

**Authority:** Muhammad Arif bin Fazil (888_JUDGE)  
**License:** AGPL-3.0-only  
**Last Verified:** 2026-03-01

*DITEMPA BUKAN DIBERI — Forged, Not Given* 🔥💎

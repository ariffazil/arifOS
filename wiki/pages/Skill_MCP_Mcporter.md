---
type: Tool
tier: 20_RUNTIME
strand:
- tools
- mcp
- integrations
audience:
- engineers
- operators
difficulty: intermediate
prerequisites:
- MCP_Tools
- Tool_Surface_Architecture
tags:
- mcp
- mcporter
- interoperability
- cli
- tool-calling
- server-discovery
- codegen
sources:
- Hermes official skill: official/mcp/mcporter
- mcporter CLI docs
- MCP specification
last_sync: '2026-05-18'
confidence: 0.95
---

# Skill: MCP — mcporter

**mcporter** is the universal MCP (Model Context Protocol) CLI — discover, configure, authenticate, and call MCP servers and tools directly from the terminal. It auto-discovers servers from other MCP clients (Claude Desktop, Cursor, Codex, OpenCode, etc.) and enables ad-hoc connections without config files.

## Purpose

To give every federation agent a single CLI for the entire MCP ecosystem:
- List all MCP servers configured across all agent clients on the machine
- Call any MCP tool with key=value syntax or JSON payload
- Connect to ad-hoc HTTP or stdio servers without editing config files
- Generate TypeScript clients and CLI wrappers from MCP schemas
- Authenticate with OAuth-enabled MCP servers

## Specifications

- **Stage**: 111 (Sensing) + 010 (Forge)
- **Layer**: PROTOCOL
- **Trinity**: Δ (Mind — structured discovery and execution against the MCP mesh)
- **Floors touched most directly**: F2 (Truth — server discovery), F4 (Guardrails — auth boundaries), F8 (Audit — all tool calls logged)

## Installation

```bash
# No install needed (runs via npx)
npx mcporter list

# Or install globally
npm install -g mcporter
```

**Installed on**: `/root` (VPS host)  
**Binary**: `/usr/local/bin/mcporter`  
**Version**: 0.9.0

## Quick Start

```bash
# List all MCP servers on this machine (auto-discovers from all clients)
mcporter list

# List tools for a specific server with full schema
mcporter list arifOS --schema

# Call a tool with key=value syntax
mcporter call arifOS.arif_sense_observe query="docker status"

# Machine-readable JSON output
mcporter call arifOS.arif_ops_measure mode=health --output json
```

## Server Discovery

mcporter auto-discovers servers from other MCP clients:
- `.codex/config.toml` — Codex agent
- `.config/opencode/opencode.json` — OpenCode agent
- `.claude.json` — Claude Desktop / Claude Code
- `~/.hermes/config.yaml` — Hermes agent
- `.cursor/mcp.json` — Cursor editor

### Ad-hoc Connections (no config needed)

```bash
# HTTP MCP server
mcporter list --http-url https://some-mcp-server.com --name my_server

# Stdio MCP server on the fly
mcporter list --stdio "npx -y @modelcontextprotocol/server-filesystem" --name fs
```

## Calling Tools

### Key=value syntax
```bash
mcporter call linear.list_issues team=ENG limit:5
```

### Function syntax
```bash
mcporter call "linear.create_issue(title: 'Bug fix needed')"
```

### JSON payload
```bash
mcporter call arifOS.arif_sense_observe --args '{"mode": "search", "query": "docker"}'
```

### Ad-hoc HTTP call
```bash
mcporter call https://api.example.com/mcp.fetch url=https://example.com
```

### Ad-hoc stdio call
```bash
mcporter call --stdio "bun run ./server.ts" scrape url=https://example.com
```

## Auth and Config

```bash
# OAuth login for a server
mcporter auth <server | url> [--reset]

# Manage config
mcporter config list
mcporter config get <key>
mcporter config add <server>
mcporter config remove <server>
mcporter config import <path>
```

**Config file**: `./config/mcporter.json` (override with `--config`)

## Daemon (Persistent Connections)

```bash
mcporter daemon start
mcporter daemon status
mcporter daemon stop
mcporter daemon restart
```

## Code Generation

```bash
# Generate a CLI wrapper for an MCP server
mcporter generate-cli --server arifOS

# Generate TypeScript types/client
mcporter emit-ts arifOS --mode client
mcporter emit-ts arifOS --mode types

# Inspect a generated CLI
mcporter inspect-cli <path> [--json]
```

## Federation Context

**Current MCP mesh on this host** (discovered by mcporter):
| Server | Tools | Source Client | Status |
|--------|-------|---------------|--------|
| arifOS | 14 | Codex | ✅ healthy |
| github | 26 | OpenCode | ✅ healthy |
| exa | 2 | OpenCode | ✅ healthy |
| time | 2 | OpenCode | ✅ healthy |
| memory | 9 | OpenCode | ✅ healthy |
| filesystem | 14 | OpenCode | ✅ healthy |
| brave_search | 6 | Codex | ✅ healthy |
| git | 28 | OpenCode | ✅ healthy |
| meyhem | 5 | OpenCode | ✅ healthy |
| supabase | — | Codex | 🔒 auth required |
| search | — | OpenCode | ❌ offline |

**arifOS Federation MCP servers** (canonical):
| Server | Port | Endpoint |
|--------|------|----------|
| arifOS | 8080 | http://127.0.0.1:8080/mcp |
| GEOX | 8081 | http://127.0.0.1:8081/mcp |
| WEALTH | 8082 | http://127.0.0.1:8082/mcp |
| WELL | 8083 | http://127.0.0.1:8083/mcp |

## Pitfalls

| Problem | Fix |
| :--- | :--- |
| Server not found | Check if the source client config is valid; try ad-hoc `--http-url` or `--stdio` |
| Auth required | Run `mcporter auth <server>` — may need interactive browser (use `pty=true`) |
| OAuth flow hangs | Use terminal with PTY: `mcporter auth <server>` in interactive mode |
| JSON parsing errors | Use `--output json` for structured output; escape quotes in `--args` |
| Offline server | Check if the server process is running (`docker compose ps`) |

## Related

- [[MCP_Tools]] (Tool surface architecture)
- [[Tool_Surface_Architecture]] (Registry canon vs runtime)
- [[Skill_Docker_Management]] (Container ops for MCP server deployment)
- [[Reference_MCP_Servers]] (Official 7-server MCP substrate layer)

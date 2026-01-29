# arifOS MCP Server (AAA Framework)

**Artifact · Authority · Architecture**

The official Model Context Protocol (MCP) server for arifOS v53.2.7.
Exposes the **Trinity of Constitutional Verdicts** to external AI clients.

## 🏗️ Architecture
- **Transport**: stdio (JSON-RPC 2.0)
- **Tools**: 7 Canonical Tools (`_init_`, `_agi_`, `_asi_`, `_apex_`, `_vault_`, `_trinity_`, `_reality_`)
- **Kernels**: Directly bridges to `arifOS/codebase` kernels.

## 🛠️ Tools
See `MCP_FORGE_COMPLETE.md` for full tool definitions.

## 📦 Installation
1. Ensure `arifOS/codebase` is in your PYTHONPATH.
2. Install dependencies: `mcp`, `pydantic`.

## 🏃 Execution
```bash
python server.py
# Server will listen on stdin/stdout
```

## 📜 Constitution
This server enforces the **13 Floors (F1-F13)**. All tool calls are validated against:
- `codebase.enforcement.floor_validators`
- `codebase.mcp.constitutional_metrics`

**DITEMPA BUKAN DIBERI**

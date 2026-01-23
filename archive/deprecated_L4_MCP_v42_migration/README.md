# L4_MCP — MCP Server (The Hands)

**Layer:** L4
**Purpose:** Model Context Protocol server for IDE integration
**License:** AGPL-3.0

---

## What Lives Here

| Directory | Contents |
|-----------|----------|
| `arifos_mcp/` | MCP server package |
| `arifos_mcp/tools/` | MCP tool implementations |
| `arifos_mcp/config/` | IDE configuration files |
| `tests/` | MCP-specific tests |

---

## MCP Tools

| Tool | Purpose |
|------|---------|
| `apex_llama` | Governed LLM call |
| `apex_judge` | Get verdict for metrics |
| `apex_recall` | Memory recall (0.85 ceiling) |
| `apex_audit` | Audit trail query |
| `arifos_fag_read` | Governed file read |
| `arifos_fag_write` | Governed file write |

---

## Dependency Rules

```
L4_MCP ← L5_CLI, L6_SEALION, L7_DEMOS may use MCP tools
       → Imports from L3_KERNEL (arifos_core)
       → Reads governance from L2_GOVERNANCE
       → NEVER imports from higher layers
```

---

## IDE Integration

### VS Code

Add to `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "arifos": {
      "command": "arifos-mcp",
      "args": []
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "servers": {
    "arifos": {
      "command": "arifos-mcp"
    }
  }
}
```

---

## Running the Server

```bash
# Install
pip install arifos

# Run MCP server
arifos-mcp
```

---

**DITEMPA BUKAN DIBERI** — The hands execute what the mind governs.

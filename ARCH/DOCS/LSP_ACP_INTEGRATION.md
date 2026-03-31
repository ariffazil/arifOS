# LSP + ACP Integration for arifOS

**Status:** 888_SAFE (read-only)  
**Version:** 2026.03.14-FORGED  
**Constitutional Compliance:** F1, F4, F5, F11, F12, F13

---

## Overview

This integration adds two key protocols to arifOS:

1. **LSP (Language Server Protocol)** - Code intelligence layer
2. **ACP (Agent Client Protocol)** - Editor-agent bridge

Together, they enable:
- Agents to "see" code structure (no hallucination)
- Editors to talk to arifOS agents (no vendor lock-in)
- Full constitutional governance (000-999 pipeline)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         EDITOR                                   │
│  (Zed / VS Code / JetBrains / Kimi CLI)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ ACP (JSON-RPC over stdio)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    arifOS ACP Server                             │
│              (arifosmcp/transport/acp_server.py)                │
│  • ACP session management                                        │
│  • F11 (Auth) verification                                       │
│  • F13 (Sovereign) approval required                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    arifOS Kernel                                 │
│              (core/kernel/stage_orchestrator.py)                │
│  000_INIT → AGI → ASI → APEX → VAULT999                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌───────────────┐                    ┌─────────────────┐
│  LSP Bridge   │                    │   MCP Tools     │
│(intelligence/ │◄──────────────────►│  (tools/        │
│ lsp_bridge.py)│                    │ lsp_tools.py)   │
└───────┬───────┘                    └─────────────────┘
        │
        │ JSON-RPC
        ▼
┌───────────────┐
│ Language      │
│ Server        │
│ (pylsp, etc.) │
└───────────────┘
```

---

## MCP Tools Added

### `lsp_query`
General LSP query endpoint.

```python
{
    "file_path": "arifosmcp/core/kernel.py",
    "query_type": "symbols",  # hover, definition, references, diagnostics
    "line": 42,
    "character": 15
}
```

### `lsp_get_symbols`
Get all symbols in a file.

### `lsp_get_diagnostics`
Get errors and warnings.

### `lsp_go_to_definition`
Find symbol definition.

### `lsp_find_references`
Find all references.

---

## Security & Governance

| Floor | Implementation |
|-------|---------------|
| F1 (Amanah) | All operations logged |
| F4 (Clarity) | LSP provides exact symbols |
| F5 (Peace) | Read-only only |
| F11 (Auth) | Session authentication |
| F12 (Injection) | Path sanitization |
| F13 (Sovereign) | User approval per session |

---

## Editor Configuration

### Zed
```json
{
  "agent": {
    "default_model": {
      "provider": "arifos",
      "model": "arifOS-APEX"
    }
  }
}
```

### VS Code
```json
{
  "acp.agents": [{
    "name": "arifOS",
    "command": ["python", "-m", "arifosmcp.transport.acp_server"]
  }]
}
```

---

## Installation

```bash
# Install language server
pip install python-lsp-server

# Test
pytest tests/integration/test_lsp_acp.py -v

# Start ACP server
python -m arifosmcp.transport.acp_server
```

---

**Forge Date:** 2026.03.14  
**VAULT999 Seal:** PENDING


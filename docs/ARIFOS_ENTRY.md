# arifOS — Entry Point
**Status:** SOVEREIGN KERNEL | **Organ:** MIND (Δ) | **Authority:** 888_JUDGE

## Quick Start
```bash
# Install (uv-based)
pip install -e ".[dev]"

# Start MCP server (HTTP + SSE)
python -m arifosmcp.server

# Start MCP server (stdio)
python -m arifosmcp --stdio

# Health check
curl http://localhost:8080/health
```

## Critical Files
| File | Purpose |
|------|---------|
| `arifosmcp/server.py` | FastMCP entry point |
| `arifosmcp/core/floors.py` | F1-F13 enforcement |
| `core/vault999/` | Append-only ledger |
| `APEX/ASF1/tool_registry.json` | 13-tool canonical registry |
| `smithery.yaml` | MCP manifest |

## 13 Canonical Tools
```
000 INIT    333 APEX   666 GEOX    888 JUDGE
111 AGI     444 ROUT   777 VAL     999 SEAL
222 ASI     555 WEALTH
```

## Federation
```
AAA (Body) ←→ arifOS (Kernel) ←→ A-FORGE (Forge)
```

See `.AGENTS.md` for full agent onboarding context.
**999 SEAL ALIVE**
# arifOS Tool Registry

> **UPDATED 2026-06-14:** This file is now a redirect.
>
> The live registry SOT is `arifosmcp/constitutional_map.py` (CANONICAL_TOOLS + DIAGNOSTIC_TOOLS dicts)
> and the generated `arifosmcp/tool_registry.json`.

## Where to Find the Live Registry

| Source | Path | What |
|--------|------|------|
| **Constitutional dict** | `arifosmcp/constitutional_map.py:CANONICAL_TOOLS` | 13 canonicals with floors, stage, lane |
| **Diagnostic dict** | `arifosmcp/constitutional_map.py:DIAGNOSTIC_TOOLS` | 31 operational tools in 7 tiers |
| **Generated JSON** | `arifosmcp/tool_registry.json` | Full 44-tool manifest with metadata |
| **Agent registry** | `docs/AGENTIC_AAA_REGISTRY.md` | Agent-to-lane assignment, Hexagon coverage |
| **MCP AGENTS.md** | `arifosmcp/AGENTS.md` | Canonical tool truth table with live curl commands |

## Summary

| Scope | Count |
|-------|-------|
| Canonical kernel tools | **13** (`arif_*`) |
| Hermes cross-verification | **7** (`hermes_*`) |
| Canary diagnostics | **6** (`arif_*`) |
| Lease lifecycle | **3** (`arif_*`) |
| Federation attestation | **4** (`arif_*`) |
| A-FORGE pre-execution | **3** (`forge_*`) |
| Narrative detection | **2** (`arif_*`) |
| General diagnostics | **6** (`arif_*` + `mcp_*`) |
| **TOTAL** | **44** |

**Regenerate the JSON:**
```bash
python3 -c "
from arifosmcp.constitutional_map import build_tool_registry_manifest
import json
with open('arifosmcp/tool_registry.json', 'w') as f:
    json.dump(build_tool_registry_manifest(), f, indent=2)
"
```

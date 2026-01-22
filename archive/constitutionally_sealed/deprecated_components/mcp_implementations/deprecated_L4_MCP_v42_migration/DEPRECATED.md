# DEPRECATED - L4_MCP Migrated to arifos_core/mcp

**Status:** ARCHIVED (v42 migration completed 2025-12-26)
**Reason:** Concern-based architecture migration (L1-L7 layers → arifos_core modules)

---

## Migration Summary

### What Was Migrated

| Original Location | New Location | Purpose |
|-------------------|--------------|---------|
| `L4_MCP/arifos_well/bindings/` | `arifos_core/mcp/tools/well/` | Multi-platform MCP bindings |
| `L4_MCP/arifos_well/server/app.py` | `arifos_core/mcp/well_api.py` | FastAPI REST server |
| `L4_MCP/arifos_well/manifest.json` | `docs/manifests/well_manifest_v42.json` | Platform manifest |

### What Was NOT Migrated (Empty/Redundant)

- `L4_MCP/arifos_mcp/` — Empty config/tools directories
- `L4_MCP/tests/` — Empty test directory
- `L4_MCP/arifos_well/core/` — Re-export wrapper (redundant)

### Core Logic Location

**NOT AFFECTED** by this migration:
- `arifos_core/waw/well_file_care.py` — Core @WELL implementation (already existed)

---

## Migration Commands

```bash
# Bindings
cp L4_MCP/arifos_well/bindings/* arifos_core/mcp/tools/well/

# REST API
cp L4_MCP/arifos_well/server/app.py arifos_core/mcp/well_api.py

# Manifest
cp L4_MCP/arifos_well/manifest.json docs/manifests/well_manifest_v42.json

# Archive
cp -r L4_MCP archive/deprecated_L4_MCP_v42_migration/
```

---

## New Usage Patterns

### Claude MCP (@WELL Server)

**Old:**
```json
{
  "mcpServers": {
    "well": {
      "command": "python",
      "args": ["-m", "arifos_well.bindings.mcp_claude"]
    }
  }
}
```

**New:**
```json
{
  "mcpServers": {
    "well": {
      "command": "python",
      "args": ["-m", "arifos_core.mcp.tools.well.mcp_claude"]
    }
  }
}
```

### REST API Server

**Old:**
```bash
python -m arifos_well.server.app
```

**New:**
```bash
python -m arifos_core.mcp.well_api
```

---

## References

- **Migration Commit:** (to be added after commit)
- **v42 Architecture:** See `L1_THEORY/canon/02_actors/` for concern-based structure
- **@WELL Documentation:** `arifos_core/waw/well_file_care.py` (core logic)

---

**DITEMPA BUKAN DIBERI** — Forged, not given

Archived: 2025-12-26 by v42 concern-based migration

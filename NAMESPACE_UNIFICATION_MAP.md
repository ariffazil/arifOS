# arifOS MCP Namespace Unification Map
## Canonical Names → Internal Implementation Mapping

**Version:** 2026.04.06  
**Status:** UNIFIED  
**Authority:** 888_JUDGE

---

## Canonical Tool Surface (10 Tools)

| Canonical Name | Stage | Trinity | Internal Implementation | File Location |
|----------------|-------|---------|------------------------|---------------|
| `arifos.init` | 000_INIT | Ψ | `init_anchor` | `megaTools/tool_01_init_anchor.py` |
| `arifos.sense` | 111_SENSE | Δ | `physics_reality` | `megaTools/tool_08_physics_reality.py` |
| `arifos.mind` | 333_MIND | Δ | `agi_mind` | `megaTools/tool_05_agi_mind.py` |
| `arifos.route` | 444_ROUTER | Ψ | `arifOS_kernel` | `megaTools/tool_02_arifOS_kernel.py` |
| `arifos.memory` | 555_MEMORY | Ω | `engineering_memory` | `megaTools/tool_07_engineering_memory.py` |
| `arifos.heart` | 666_HEART | Ω | `asi_heart` | `megaTools/tool_06_asi_heart.py` |
| `arifos.ops` | 777_OPS | Ω | `math_estimator` | `megaTools/tool_09_math_estimator.py` |
| `arifos.judge` | 888_JUDGE | Ψ | `apex_soul` | `megaTools/tool_03_apex_soul.py` |
| `arifos.vault` | 999_VAULT | Ψ | `vault_ledger` | `megaTools/tool_04_vault_ledger.py` |
| `arifos.forge` | FORGE_010 | Δ | `code_engine` | `megaTools/tool_10_code_engine.py` |

**Additional Tools (Non-Canonical):**
| Canonical Name | Internal Name | File |
|----------------|---------------|------|
| `arifos.registry` | `architect_registry` | `megaTools/tool_11_architect_registry.py` |
| `arifos.probe` | `compat_probe` | `megaTools/tool_12_compat_probe.py` |

---

## Key Unification Changes

### 1. RuntimeEnvelope.tool Field
**Before:** Used internal names (`init_anchor`, `agi_mind`, etc.)  
**After:** Uses canonical names (`arifos.init`, `arifos.mind`, etc.)

### 2. RuntimeEnvelope.canonical_tool_name Field
**Before:** Always `null`  
**After:** Always populated with canonical name

### 3. HARDENED_DISPATCH_MAP Keys
**Before:** Mixed internal and canonical names  
**After:** All canonical names + legacy aliases for backward compatibility

### 4. tool_registry.json
**Before:** Used wrong names (`init_session_anchor`, `sense_reality`, etc.)  
**After:** Uses canonical names (`arifos.init`, `arifos.sense`, etc.)

---

## Legacy Aliases (Backward Compatibility)

For backward compatibility, the following aliases are still supported in `HARDENED_DISPATCH_MAP`:

```python
LEGACY_ALIASES = {
    "init_anchor": "arifos.init",
    "physics_reality": "arifos.sense",
    "agi_mind": "arifos.mind",
    "arifOS_kernel": "arifos.route",
    "engineering_memory": "arifos.memory",
    "asi_heart": "arifos.heart",
    "math_estimator": "arifos.ops",
    "apex_soul": "arifos.judge",
    "vault_ledger": "arifos.vault",
    "code_engine": "arifos.forge",
}
```

**Note:** Legacy aliases will be deprecated in v3.0.0

---

## File Consolidation

### Consolidated Files
| Old Files | Consolidated To |
|-----------|----------------|
| `kernel_router.py` + `kernel_router_hardened.py` | `kernel_router.py` (hardened version) |
| `server.py` + `server_v2.py` | `server.py` (v2 version) |
| `tool_specs.py` + `tool_specs_v2.py` | `tool_specs.py` (v2 version) |

### Removed Directories
- `/root/arifOS/arifos_mcp/` — Duplicate package directory

### Backup Location
All original files backed up to:  
`/root/arifOS/arifosmcp/.archive/namespace_backup_2026-04-06/`

---

## Migration Status

| Task | Status | Date |
|------|--------|------|
| Fix tool_01_init_anchor.py | ✅ Complete | 2026-04-06 |
| Fix all megaTools | ✅ Complete | 2026-04-06 |
| Update tool_registry.json | ✅ Complete | 2026-04-06 |
| Remove arifos_mcp directory | ✅ Complete | 2026-04-06 |
| Consolidate kernel_router files | ✅ Complete | 2026-04-06 |
| Consolidate server files | ✅ Complete | 2026-04-06 |

---

## Response Envelope Example

```json
{
  "tool": "arifos.init",
  "canonical_tool_name": "arifos.init",
  "stage": "000_INIT",
  "verdict": "SEAL",
  "session_id": "sess_abc123",
  "payload": {...}
}
```

**NOT:**
```json
{
  "tool": "init_anchor",
  "canonical_tool_name": null,
  ...
}
```

---

## Verification Commands

```bash
# Check canonical names in code
grep -r "canonical_tool_name" /root/arifOS/arifosmcp/runtime/megaTools/

# Verify no null canonical_tool_name
grep -r 'canonical_tool_name.*None' /root/arifOS/arifosmcp/runtime/megaTools/ | grep -v "str | None"

# Check tool_registry.json
cat /root/arifOS/arifosmcp/tool_registry.json | jq '.tools[].function.name'
```

---

*Ditempa Bukan Diberi — Forged, Not Given* 🔧⚖️

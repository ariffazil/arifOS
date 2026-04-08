---
type: Synthesis
tags: [audit, MCP, tools, wiki, alignment, drift]
sources: [tool_specs.py, tools.py, capability_map.py, megaTools/__init__.py, tool_registry.json, Concept_Architecture.md, Concept_Metabolic_Pipeline.md]
last_sync: 2026-04-08
confidence: 0.90
---

# Audit: MCP Tools vs Ω-Wiki Alignment

> **Auditor**: Ω-Auditor Agent  
> **Date**: 2026-04-08  
> **Motto**: *DitemPA BUKAN DIBERI*

---

## 1. MCP Surface Inventory (Canonical 11 Tools)

| # | Tool Name (Code) | Stage | Layer | Legacy Wiki Name | Status |
|---|------------------|-------|-------|------------------|--------|
| 1 | `arifos_init` | 000 | GOVERNANCE | `init_anchor` | ✅ |
| 2 | `arifos_sense` | 111 | MACHINE | `physics_reality` | ✅ |
| 3 | `arifos_mind` | 333 | INTELLIGENCE | `agi_mind` | ✅ |
| 4 | `arifos_route` | 444 | GOVERNANCE | `arifOS_kernel` | ✅ |
| 5 | `arifos_heart` | 666 | INTELLIGENCE | `asi_heart` | ✅ |
| 6 | `arifos_ops` | 777 | MACHINE | `math_estimator` | ✅ |
| 7 | `arifos_judge` | 888 | GOVERNANCE | `apex_soul` | ✅ |
| 8 | `arifos_memory` | 555 | INTELLIGENCE | `engineering_memory` | ✅ |
| 9 | `arifos_vault` | 999 | GOVERNANCE | `vault_ledger` | ✅ |
| 10 | `arifos_forge` | 010 | EXECUTION | *(not in wiki)* | ⚠️ MISSING |
| 11 | `arifos_vps_monitor` | 111 | MACHINE | *(not in wiki)* | ⚠️ MISSING |

---

## 2. Tool Count Discrepancy

| Source | Count | Discrepancy |
|--------|-------|-------------|
| `tool_specs.py` `TOOLS` | **11** | Canonical spec |
| `megaTools/__init__.py` `MEGA_TOOLS` | **12** | +compat_probe (old compat layer) |
| `CANONICAL_TOOL_HANDLERS` | **11** | ✅ Matches spec |
| `tool_registry.json` | **10** | Missing `arifos_vps_monitor` |
| Wiki `Concept_Architecture.md` | **10** | Says "9+1 Tool Surface" |
| Wiki `Concept_Metabolic_Pipeline.md` | **11** | Says "10 + 1 canonical tools" |

**Finding**: Wiki contradicts itself on tool count (10 vs 11). Code is internally consistent at 11 tools.

---

## 3. Naming Drift

| Aspect | Code Uses | Wiki Uses | tool_registry.json Uses |
|--------|-----------|-----------|------------------------|
| Tool Names | `arifos_init` | `init_anchor` | `arifos.init` |

**Finding**: Three naming conventions in active use. The `arifos_*` underscore format is the canonical modern form.

---

## 4. Import Error Detected — **CONFIRMED**

**File**: `arifosmcp/capability_map.py` line 10
```python
from .runtime.tool_specs import MEGA_TOOLS, MegaToolName
```

**Problem**: 
- `tool_specs.py` defines `TOOLS` (tuple of ToolSpec), NOT `MEGA_TOOLS`
- `MegaToolName` does not exist anywhere in the codebase
- `MEGA_TOOLS` IS defined in `megaTools/__init__.py` (dict of handlers)

**Verification**:
```bash
$ python -c "from arifosmcp.capability_map import MEGA_TOOLS"
ImportError: cannot import name 'MEGA_TOOLS' from 'arifosmcp.runtime.tool_specs'
```

**Severity**: HIGH — Server would crash on startup if `capability_map.py` is imported

**Proposed Fix** (F1: Reversible):
```python
# Option A: Add alias to tool_specs.py (backward compat)
MEGA_TOOLS = TOOLS  # Add after TOOLS definition
MegaToolName = str  # Or Literal type if needed

# Option B: Fix import in capability_map.py (correct)
from .runtime.megaTools import MEGA_TOOLS
# Remove MegaToolName if not used
```

---

## 5. Missing Wiki Documentation

### Not in any wiki page:
- **`arifos_forge`** — The Execution Bridge (10th tool)
  - Purpose: Issues signed execution manifests to AF-FORGE substrate
  - Gate: Requires `judge verdict = "SEAL"`
  - Floors: F1, F2, F7, F13

- **`arifos_vps_monitor`** — Secure VPS Telemetry (11th tool)
  - Purpose: Read-only CPU/Memory/ZRAM/Disk telemetry
  - Floors: F4, F12

---

## 6. AGENTS.md Drift

**File**: `arifosmcp/AGENTS.md`

Issues:
- Uses old tool names (`init_anchor`, `physics_reality`, `agi_mind`)
- Lists tools not in canonical surface (`search_reality`, `agentzero_engineer`)
- Needs full rewrite to align with 11-tool canonical surface

---

## 7. Recommended Fixes

### HIGH PRIORITY

| # | Action | File(s) | Floors |
|---|--------|---------|--------|
| 1 | Add `MEGA_TOOLS = TOOLS` alias to `tool_specs.py` OR fix `capability_map.py` import | `tool_specs.py`, `capability_map.py` | F11 |
| 2 | Choose "10" or "11" and update both wiki pages to agree | `Concept_Architecture.md`, `Concept_Metabolic_Pipeline.md` | F2 |
| 3 | Add `arifos_forge` and `arifos_vps_monitor` to wiki | `wiki/pages/` (new) | F2 |

### MEDIUM PRIORITY

| # | Action | File(s) |
|---|--------|---------|
| 4 | Normalize `tool_registry.json` to use underscore naming | `tool_registry.json` |
| 5 | Rewrite `AGENTS.md` to match 11-tool canonical surface | `arifosmcp/AGENTS.md` |

---

## 8. HOLD List

The following require human review before changes:

1. **Deep refactor of `megaTools/__init__.py`**: The 12-tool `MEGA_TOOLS` dict with compat_probe vs the 11-tool canonical surface — which is truth?
2. **Tool count decision**: Should `arifos_vps_monitor` be public-facing or internal-only?
3. **`tool_registry.json` contract**: Is changing the naming convention a breaking change for downstream consumers?

---

## 9. Verdict

| Finding | Severity | Verdict |
|---------|----------|---------|
| Tool count drift (wiki) | MEDIUM | PARTIAL — wiki needs sync |
| Import error | HIGH | VOID — code would crash |
| Missing wiki pages | MEDIUM | PARTIAL — docs incomplete |
| Naming drift | LOW | ACKNOWLEDGED — transitional state |

**Overall**: Code is internally consistent (11 tools). Wiki needs alignment work.

---

> [!NOTE]
> This audit is a snapshot as of 2026-04-08. Code and wiki evolve; re-audit after fixes.

**F11**: Logged in `wiki/log.md`  
**F2**: All claims traceable to source files in `arifosmcp/` and `wiki/pages/`

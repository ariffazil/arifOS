# Archived MCP Servers - v46.2

**Date**: 2026-01-16
**Reason**: Consolidated into `unified_server.py`
**Authority**: Engineer Boundaries (Ω Territory)

---

## 📦 **What Was Archived**

This directory contains MCP server implementations that were **consolidated** into the unified server architecture.

### **Archived Files:**

1. **`server.py`** (782 lines)
   - **Status**: OLD primary MCP server
   - **Tools**: 27 tools (11 individual stage tools + 16 others)
   - **Architecture**: Individual stage tools (mcp_000, mcp_111, mcp_222, etc.)
   - **Issues**:
     - Redundant individual stage tools (111, 222, 333, etc.)
     - Ungoverned APEX_LLAMA tool
     - 9 separate vault999 tools (cognitive overload)
   - **Replaced By**: `unified_server.py`

2. **`constitution.py`** (666 lines)
   - **Status**: Theoretical "constitutional particle" implementation
   - **Architecture**: Kimi Orthogonal Directive (particle independence)
   - **Unused**: Not actively imported by any production code
   - **Concept**: AAA MCP Architecture with orthogonal particles
   - **Replaced By**: Constitutional governance now in unified_server.py

3. **`arifos_mcp_server.py`** (if exists)
   - **Status**: Remote AAA server
   - **Tools**: 10 tools for remote AI federation
   - **Replaced By**: Remote tools integrated into unified_server.py

4. **`vault999_server.py`** (if active in this version)
   - **Status**: Vault-999 gateway server
   - **Tools**: 8 separate memory tools
   - **Replaced By**: 3 consolidated vault999 tools in unified_server.py

---

## ✅ **What Replaced Them**

### **`unified_server.py`** (1300+ lines)

**Consolidation Result:**
- From **34 tools → 17 tools** (-50%)
- Removed 11 redundant pipeline stage tools
- Deleted 1 ungoverned tool (APEX_LLAMA)
- Consolidated 9 vault999 tools → 3 tools (-67% memory tools)
- Added 2 new search tools (agi_search, asi_search)
- Clean naming convention (no mcp_ prefix)
- All 19 core capabilities preserved
- 29 deprecated aliases for backward compatibility

**New Architecture:**
```
17 Tools Total:
├── Constitutional Pipeline (5): arifos_live, agi_think, agi_reflect, asi_act, apex_seal
├── Search Tools (2): agi_search (111+), asi_search (444)
├── VAULT-999 (3): vault999_query, vault999_store, vault999_seal
├── FAG (4): fag_read, fag_write, fag_list, fag_stats
├── Validation (1): arifos_meta_select
└── System (2): arifos_executor, github_govern
```

---

## 🔄 **Migration Path**

### **For Code Referencing Old Server:**

**Old Import (DEPRECATED):**
```python
from arifos.mcp.server import mcp_server
```

**New Import (ACTIVE):**
```python
from arifos.mcp.unified_server import mcp_server
```

### **For Old Tool Names:**

All old tool names are automatically mapped via `DEPRECATED_ALIASES` in unified_server.py:

```python
# Old names still work (with deprecation warning)
"arifos_judge" → "arifos_live"
"apex_audit" → "apex_seal"
"vault999_recall" → "vault999_query"
"vault999_audit" → "vault999_seal"
# ... 25 more aliases
```

**Backward Compatibility**: All old tool names work until v47, then they'll be removed.

---

## 📊 **Consolidation Benefits**

| Metric | Before (Old Servers) | After (Unified) | Improvement |
|--------|----------------------|-----------------|-------------|
| **Total Tools** | 34 (across 3 servers) | 17 (single server) | -50% |
| **Vault999 Tools** | 9 | 3 | -67% |
| **Cognitive Load** | High (34 tools to remember) | Low (17 tools) | -50% |
| **Search Capabilities** | 0 (orphaned code) | 2 (exposed) | ✅ NEW |
| **Ungoverned Tools** | 1 (APEX_LLAMA) | 0 | ✅ FIXED |
| **Deprecated Aliases** | 17 | 29 | +71% (backward compatibility) |
| **Code Duplication** | High (3 servers) | None (1 server) | ✅ ELIMINATED |

---

## 🎯 **Why This Archive Exists**

**DITEMPA BUKAN DIBERI** - Forged, not given; we preserve history while moving forward.

These files represent the evolution of arifOS MCP architecture:
- **Phase 1**: Individual stage tools (mcp_111, mcp_222, etc.) - TOO GRANULAR
- **Phase 2**: Theoretical constitutional particles - TOO ABSTRACT
- **Phase 3**: Unified consolidation - ✅ JUST RIGHT

We archive them to:
1. **Preserve history**: Track architectural evolution
2. **Prevent confusion**: Clear single source of truth (unified_server.py)
3. **Enable rollback**: If unified server has issues, we can reference old implementations
4. **Document decisions**: Why we chose consolidation over separation

---

## 🧠 **Architectural Lessons Learned**

### **F4 (ΔS - Clarity):**
Too many tools = cognitive entropy. 17 tools with clear semantic names > 34 tools with overlapping functions.

### **F6 (Amanah - Reversibility):**
Deprecation aliases preserve reversibility. Old code doesn't break, new code is cleaner.

### **F7 (Ω₀ - Humility):**
We might be wrong. Archive enables rollback if consolidation has unforeseen issues.

### **Dual Search Discovery:**
The orphaned Meta Search implementation revealed that powerful capabilities can hide in implementation code without MCP exposure. Always map capabilities to tools.

---

**Version**: v46.3
**Status**: ARCHIVED
**Active Server**: `arifos/mcp/unified_server.py`
**Entry Point**: `scripts/arifos_mcp_entry.py` (updated to use unified_server)

**Verdict**: SEAL - Consolidation complete, backward compatibility maintained, history preserved.

# arifOS MCP Unified Naming Convention

**Authority**: Engineer Boundaries (Ω Territory)
**Date**: 2026-01-16
**Status**: PROPOSED
**Purpose**: Remove redundant `mcp_` prefix, establish clear naming rules

---

## 🎯 **Problem Statement**

**Current naming has 3 issues:**

1. **Redundant `mcp_` prefix** - All tools in MCP server already "mcp tools"
2. **Inconsistent conventions** - Some tools have prefixes, some don't
3. **Clarity violation (F4)** - Hard to distinguish domain vs. layer

**Example redundancy:**
```python
# In arifOS MCP server (already MCP context):
"mcp_888_judge"  # "mcp" prefix adds ZERO information
```

This is like labeling every file in a "photos" folder with "photo_".

---

## ✅ **Unified Naming Rules**

### **Rule 1: Pipeline Stages → `stage_NNN_function`**

Pipeline stages are numbered 000→999. Use numbers as primary identifier:

| Current | Proposed | Clarity Gain |
|---------|----------|--------------|
| `mcp_000_reset` | `stage_000_reset` | Clear it's a pipeline stage |
| `mcp_111_sense` | `stage_111_sense` | Numbers indicate position |
| `mcp_222_reflect` | `stage_222_reflect` | Self-documenting order |
| `mcp_333_atlas` | `stage_333_atlas` | No "mcp" noise |
| `mcp_444_evidence` | `stage_444_evidence` | Consistent pattern |
| `mcp_555_empathize` | `stage_555_empathize` | Stage = pipeline |
| `mcp_666_align` | `stage_666_align` | Clean |
| `mcp_777_forge` | `stage_777_forge` | Clear |
| `mcp_888_judge` | `stage_888_judge` | Self-explanatory |
| `mcp_889_proof` | `stage_889_proof` | Obvious role |
| `mcp_999_seal` | `stage_999_seal` | Final stage clear |

**Alternative (even cleaner):**
```
000_reset, 111_sense, 222_reflect, ..., 999_seal
```
If context makes "stage" obvious, numbers alone work.

---

### **Rule 2: Domain Tools → Keep Domain Prefix**

Domain prefixes add **useful** context (which system/subsystem):

| Current | Proposed | Domain | Rationale |
|---------|----------|--------|-----------|
| `arifos_judge` | `arifos_judge` | arifOS | ✅ Keep - main pipeline |
| `arifos_recall` | `arifos_recall` | arifOS | ✅ Keep - memory system |
| `arifos_audit` | `arifos_audit` | arifOS | ✅ Keep - audit system |
| `arifos_executor` | `arifos_executor` | arifOS | ✅ Keep - execution |
| `arifos_validate_full` | `arifos_validate_full` | arifOS | ✅ Keep - validation |
| `arifos_meta_select` | `arifos_meta_select` | arifOS | ✅ Keep - routing |
| `vault_search` | `vault_search` | Vault | ✅ Keep - memory band |
| `vault_fetch` | `vault_fetch` | Vault | ✅ Keep - retrieval |
| `vault_receipts` | `vault_receipts` | Vault | ✅ Keep - ZKPC |
| `vault999_store` | `vault999_store` | Vault-999 | ✅ Keep - EUREKA |
| `vault999_eval` | `vault999_eval` | Vault-999 | ✅ Keep - TAC |

---

### **Rule 3: Bundles → No Prefix (Self-Explanatory)**

Orthogonal bundles are conceptually clear without prefix:

| Current | Proposed | Rationale |
|---------|----------|-----------|
| `agi_think` | `agi_think` | ✅ Already perfect |
| `asi_act` | `asi_act` | ✅ Already perfect |
| `apex_audit` | `apex_audit` | ✅ Already perfect |

---

### **Rule 4: FAG Tools → Remove Double Prefix**

FAG (File Access Governance) is already arifOS-specific:

| Current | Proposed | Rationale |
|---------|----------|-----------|
| `arifos_fag_read` | `fag_read` | Remove `arifos_` redundancy |
| `arifos_fag_write` | `fag_write` | FAG already implies arifOS |
| `arifos_fag_list` | `fag_list` | Cleaner, still clear |
| `arifos_fag_stats` | `fag_stats` | Shorter name |

**Why?** FAG = File Access Governance = arifOS feature. No need for `arifos_fag_*`.

---

### **Rule 5: Utility Tools → Descriptive Names**

| Current | Proposed | Rationale |
|---------|----------|-----------|
| `APEX_LLAMA` | `apex_llama` | Lowercase consistency |
| `memory_get_receipts` | `memory_receipts` | Shorter, verb implied |
| `memory_verify_seal` | `memory_verify_seal` | ✅ Already clear |
| `github_aaa_govern` | `github_govern` | AAA redundant (context clear) |

---

## 📊 **Complete Renaming Matrix**

### **Before → After (All 34 Tools)**

| # | Current Name | Proposed Name | Category | Change |
|---|--------------|---------------|----------|--------|
| **CONSTITUTIONAL PIPELINE** |
| 1 | `mcp_000_reset` | `stage_000_reset` | Pipeline | Remove `mcp_` |
| 2 | `mcp_000_gate` | `stage_000_gate` | Pipeline | Remove `mcp_` |
| 3 | `mcp_111_sense` | `stage_111_sense` | Pipeline | Remove `mcp_` |
| 4 | `mcp_222_reflect` | `stage_222_reflect` | Pipeline | Remove `mcp_` |
| 5 | `mcp_444_evidence` | `stage_444_evidence` | Pipeline | Remove `mcp_` |
| 6 | `mcp_555_empathize` | `stage_555_empathize` | Pipeline | Remove `mcp_` |
| 7 | `mcp_666_align` | `stage_666_align` | Pipeline | Remove `mcp_` |
| 8 | `mcp_777_forge` | `stage_777_forge` | Pipeline | Remove `mcp_` |
| 9 | `mcp_888_judge` | `stage_888_judge` | Pipeline | Remove `mcp_` |
| 10 | `mcp_889_proof` | `stage_889_proof` | Pipeline | Remove `mcp_` |
| 11 | `mcp_999_seal` | `stage_999_seal` | Pipeline | Remove `mcp_` |
| **CORE/LEGACY** |
| 12 | `arifos_judge` | `arifos_judge` | Core | ✅ No change |
| 13 | `arifos_recall` | `arifos_recall` | Core | ✅ No change |
| 14 | `arifos_audit` | `arifos_audit` | Core | ✅ No change |
| 15 | `APEX_LLAMA` | `apex_llama` | Core | Lowercase |
| **ORTHOGONAL BUNDLES** |
| 16 | `agi_think` | `agi_think` | Bundle | ✅ No change |
| 17 | `asi_act` | `asi_act` | Bundle | ✅ No change |
| 18 | `apex_audit` | `apex_audit` | Bundle | ✅ No change |
| **MEMORY TOOLS** |
| 19 | `memory_get_receipts` | `memory_receipts` | Memory | Shorter |
| 20 | `memory_verify_seal` | `memory_verify_seal` | Memory | ✅ No change |
| **TRACK A/B/C** |
| 21 | `arifos_validate_full` | `arifos_validate_full` | Validation | ✅ No change |
| 22 | `arifos_meta_select` | `arifos_meta_select` | Routing | ✅ No change |
| **FAG TOOLS** |
| 23 | `arifos_fag_read` | `fag_read` | FAG | Remove `arifos_` |
| 24 | `arifos_fag_write` | `fag_write` | FAG | Remove `arifos_` |
| 25 | `arifos_fag_list` | `fag_list` | FAG | Remove `arifos_` |
| 26 | `arifos_fag_stats` | `fag_stats` | FAG | Remove `arifos_` |
| **VAULT/MEMORY SEARCH** |
| 27 | `vault_search` | `vault_search` | Vault | ✅ No change |
| 28 | `vault_fetch` | `vault_fetch` | Vault | ✅ No change |
| 29 | `vault_receipts` | `vault_receipts` | Vault | ✅ No change |
| **VAULT-999 TAC/EUREKA** |
| 30 | `vault999_store` | `vault999_store` | Vault-999 | ✅ No change |
| 31 | `vault999_eval` | `vault999_eval` | Vault-999 | ✅ No change |
| **REMOTE GOVERNANCE** |
| 32 | `github_aaa_govern` | `github_govern` | GitHub | Remove `_aaa` |
| 33 | `arifos_executor` | `arifos_executor` | Execution | ✅ No change |

---

## 📈 **Impact Analysis**

### **Changes Summary**

| Change Type | Count | Examples |
|-------------|-------|----------|
| Remove `mcp_` prefix | 11 tools | All pipeline stages |
| Remove `arifos_` from FAG | 4 tools | FAG read/write/list/stats |
| Shorten names | 2 tools | `memory_get_receipts`, `github_aaa_govern` |
| Lowercase consistency | 1 tool | `APEX_LLAMA` → `apex_llama` |
| **No change** | **16 tools** | Already clean |
| **TOTAL** | **34 tools** | |

### **Lines Changed**

| File Type | Estimated Changes |
|-----------|-------------------|
| Tool implementations | ~11 files (rename functions) |
| Tool registry | 1 file (update TOOLS dict) |
| Tool descriptions | 1 file (update TOOL_DESCRIPTIONS) |
| Tests | ~30 files (update tool names) |
| Documentation | ~5 files (update references) |

---

## 🎯 **Benefits**

### **F4 (ΔS - Clarity)** ✅ MASSIVE IMPROVEMENT
- **Before**: `mcp_888_judge` - What does "mcp" tell you? Nothing (already in MCP).
- **After**: `stage_888_judge` - Clear it's pipeline stage 888.
- **Entropy Reduction**: Remove 11× redundant `mcp_` prefixes

### **F2 (Truth - Accuracy)** ✅ IMPROVED
- **Before**: Naming conventions inconsistent (some `mcp_`, some not)
- **After**: Clear rules - pipeline = `stage_`, domain = keep prefix, bundles = no prefix
- **Predictability**: Developer can guess tool name from category

### **Developer Experience** ✅ IMPROVED
- **Before**: "Should I use `mcp_888_judge` or `apex_audit`?"
- **After**: Clear hierarchy - `stage_888_judge` (granular) vs `apex_audit` (bundle)
- **Typing**: Shorter names = less typing, fewer typos

---

## 🔄 **Migration Path**

### **Phase 1: Add Aliases (Backward Compatible)**
```python
TOOLS = {
    # New names (canonical)
    "stage_888_judge": mcp_888_judge_sync,
    "fag_read": arifos_fag_read,

    # Old names (deprecated, for backward compatibility)
    "mcp_888_judge": mcp_888_judge_sync,  # DEPRECATED
    "arifos_fag_read": arifos_fag_read,    # DEPRECATED
}
```

### **Phase 2: Update Documentation**
- Mark old names as DEPRECATED in tool descriptions
- Update all examples to use new names

### **Phase 3: Remove Aliases (Future Version)**
- After 1-2 versions, remove deprecated aliases
- Breaking change, major version bump

---

## 📋 **Implementation Checklist**

- [ ] Rename tool functions in implementation files
- [ ] Update TOOLS registry with new names
- [ ] Update TOOL_DESCRIPTIONS with new names
- [ ] Add aliases for backward compatibility
- [ ] Update all tests to use new names
- [ ] Update AGENTS.md references
- [ ] Update README.md examples
- [ ] Update CHANGELOG.md with deprecation notice
- [ ] Update Claude Desktop config (if needed)

---

## 🎓 **Constitutional Validation**

### **F4 (ΔS - Clarity)** ✅ PASS
- Reduces naming entropy by removing redundant prefixes
- Establishes clear, predictable patterns
- Easier to understand tool categories

### **F6 (Amanah - Reversibility)** ✅ PASS
- Aliases provide backward compatibility
- No functionality changes
- Git-reversible

### **F7 (Ω₀ - Humility)** ✅ PASS
- Change is well-understood (renaming only)
- Low risk (no logic changes)
- Testable (all tests can be updated)

---

**DITEMPA BUKAN DIBERI** - Clarity through simplicity, not decoration.

**Status**: Ready for implementation in unified MCP server.

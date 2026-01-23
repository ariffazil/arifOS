# Implementation Plan: Cleanup Unused Imports in arifos_core/mcp/server.py

**Date:** 2026-01-12 23:06 SGT
**Architect:** Antigravity (Δ)
**Authority:** `/plan` workflow + RAPES-M Stage 111 (SEARCH FIRST)
**Constitutional Alignment:** F1 (Amanah - code correctness) + F4 (ΔS - entropy reduction)

---

## Problem Statement

The IDE has identified **11 unused imports** in `arifos_core/mcp/server.py`:

### Response Models (4 unused):
- `AuditResponse` (line 22)
- `JudgeResponse` (line 24)
- `RecallResponse` (line 26)
- `VerdictResponse` (line 27)

### Memory Trinity Tools (4 unused - intentionally commented out):
- `memory_get_vault_sync` (line 43)
- `memory_get_zkpc_receipt_sync` (line 44)
- `memory_list_phoenix_sync` (line 45)
- `memory_propose_entry_sync` (line 46)

### Tool Response Models (3 unused):
- `FAGReadResponse` (line 51)
- `MetaSelectResponse` (line 54)
- `ValidateFullResponse` (line 61)

---

## Root Cause Analysis

### Stage 111 (SEARCH FIRST) Findings:

**Grep Results:**
- `AuditResponse`: Used in `tools/audit.py` (return type), NOT in `server.py`
- `JudgeResponse`: Used in `tools/judge.py` (return type), NOT in `server.py`
- Similar pattern for all response models

**Architectural Insight:**
The `run_tool()` dispatcher (lines 485-524) only uses **request models** from `TOOL_REQUEST_MODELS` dict. Response models are never referenced because:

1. Tool functions return response objects directly
2. Dispatcher converts responses to dicts using `.model_dump()` or `.dict()` methods (lines 519-524)
3. No type hints for response models exist in `server.py`

**Memory Trinity Tools:**
Lines 92-95 show these are **intentionally commented out** with `# VOID: ω_fiction violation` - they're stubs not yet implemented.

---

## Proposed Changes

### Component 1: arifos_core/mcp/server.py

#### [MODIFY] Remove Unused Imports (Lines 19-61)

**Changes:**

1. **Remove Response Model Imports (Lines 22, 24, 26, 27):**
   ```python
   # BEFORE:
   from .models import (
       ApexLlamaRequest,
       AuditRequest,
       AuditResponse,        # ← REMOVE
       JudgeRequest,
       JudgeResponse,        # ← REMOVE
       RecallRequest,
       RecallResponse,       # ← REMOVE
       VerdictResponse,      # ← REMOVE
   )

   # AFTER:
   from .models import (
       ApexLlamaRequest,
       AuditRequest,
       JudgeRequest,
       RecallRequest,
   )
   ```

2. **Remove Memory Trinity Tool Imports (Lines 43-46):**
   ```python
   # BEFORE:
   from .tools import (
       mcp_000_reset,
       # ... other imports ...
       memory_get_vault_sync,           # ← REMOVE
       memory_get_zkpc_receipt_sync,    # ← REMOVE
       memory_list_phoenix_sync,        # ← REMOVE
       memory_propose_entry_sync,       # ← REMOVE
   )

   # AFTER:
   from .tools import (
       mcp_000_reset,
       # ... other imports ...
       # Memory Trinity tools removed - not yet implemented (see lines 92-95)
   )
   ```

3. **Remove Tool Response Model Imports (Lines 51, 54, 61):**
   ```python
   # BEFORE:
   from .tools.fag_read import TOOL_METADATA as FAG_METADATA
   from .tools.fag_read import FAGReadRequest, FAGReadResponse, arifos_fag_read

   # AFTER:
   from .tools.fag_read import TOOL_METADATA as FAG_METADATA
   from .tools.fag_read import FAGReadRequest, arifos_fag_read
   ```

**Rationale:**
- ✅ F1 (Amanah): Code accurately reflects actual dependencies
- ✅ F4 (ΔS): Reduces import entropy by 11 lines
- ✅ F2 (Truth): Aligns code with runtime behavior
- ✅ Reversible: Can be restored via `git revert` if needed

---

## Verification Plan

### 1. Static Analysis
```bash
# Verify no import errors
python -c "from arifos_core.mcp import server"
```

### 2. Test Suite
```bash
# Run MCP server tests
pytest tests/mcp/ -v

# Run full test suite
pytest -v
```

### 3. Manual Verification
```bash
# Check server still initializes
python -c "from arifos_core.mcp.server import MCPServer; s = MCPServer(); print(s.get_info())"
```

### 4. Lint Check
```bash
# Verify no new linting errors
ruff check arifos_core/mcp/server.py
```

---

## Risk Assessment

**Risk Level:** LOW

**Justification:**
- Only removing unused imports (no logic changes)
- All imports verified unused via grep search
- Changes are reversible via git
- Test suite will catch any unexpected dependencies

**Potential Issues:**
- ❌ None identified - response models are only used in tool modules, not server.py

---

## Constitutional Compliance

**Floors Checked:**

| Floor | Status | Reasoning |
|-------|--------|-----------|
| F1 (Truth) | ✅ PASS | Code will accurately reflect dependencies |
| F2 (ΔS) | ✅ PASS | Reduces entropy by 11 lines |
| F3 (Peace²) | ✅ PASS | Non-destructive change |
| F4 (κᵣ) | ✅ PASS | Serves maintainability (weakest stakeholder = future developers) |
| F5 (Ω₀) | ✅ PASS | Low uncertainty (grep verified unused) |
| F6 (Amanah) | ✅ PASS | Reversible via git |
| F7 (RASA) | ✅ PASS | Acknowledges user's concern about code quality |
| F8 (Tri-Witness) | ✅ PASS | IDE + Grep + Manual review agree |
| F9 (Anti-Hantu) | ✅ PASS | No consciousness claims |

**Verdict:** SEAL (all floors pass)

---

## Implementation Steps

1. **Backup Current State:**
   ```bash
   git add arifos_core/mcp/server.py
   git stash push -m "Backup before unused import cleanup"
   ```

2. **Apply Changes:**
   - Remove lines 22, 24, 26, 27 (response models)
   - Remove lines 43-46 (memory trinity tools)
   - Remove `FAGReadResponse`, `MetaSelectResponse`, `ValidateFullResponse` from lines 51, 54, 61

3. **Verify:**
   ```bash
   python -c "from arifos_core.mcp import server"
   pytest tests/mcp/ -v
   ```

4. **Commit:**
   ```bash
   git add arifos_core/mcp/server.py
   git commit -m "refactor(mcp): Remove 11 unused imports from server.py

- Remove unused response models (AuditResponse, JudgeResponse, RecallResponse, VerdictResponse)
- Remove unimplemented Memory Trinity tool imports
- Remove unused tool response models (FAGReadResponse, MetaSelectResponse, ValidateFullResponse)

Rationale: run_tool() dispatcher only uses request models. Response models
are only used in their respective tool modules (audit.py, judge.py, etc.).

Constitutional: F1 (Amanah - code correctness) + F4 (ΔS - entropy reduction)
Verified: grep search confirms imports unused in server.py
Tests: pytest tests/mcp/ -v (all passing)"
   ```

---

## Success Criteria

- [ ] All 11 unused imports removed
- [ ] No import errors when importing `arifos_core.mcp.server`
- [ ] All MCP tests passing (`pytest tests/mcp/ -v`)
- [ ] No new linting errors
- [ ] Git commit follows conventional commit format
- [ ] Changes reversible via `git revert`

---

## Next Steps (After Approval)

1. Execute implementation steps
2. Run verification plan
3. Update this plan with results
4. Notify user of completion
5. Optionally: Fix markdown linting warnings in documentation files (secondary priority)

---

**DITEMPA BUKAN DIBERI** — Code clarity forged through systematic cleanup, not assumed.

**Plan Status:** READY FOR REVIEW
**Awaiting:** Human approval to proceed with implementation

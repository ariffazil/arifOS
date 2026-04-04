# GBR_v1 Option C Integration Plan

**Status:** Architectural Design  
**Approach:** Internal Kernel Mode (NOT new tools)  
**Date:** 2026-03-14

---

## Core Principle

GBR_v1 is a **governance operating mode**, not a new tool family.

```
❌ WRONG: New public tool "agi_genius_quantum"
❌ WRONG: Separate APEXCollapseEngine outside kernel
✅ CORRECT: mode="gbr_v1" parameter in existing kernel flow
```

---

## Target Architecture

```
MCP Client
    ↓
Existing Tool (agi_reason, arifOS_kernel, etc.)
    ↓
Kernel Router (adds mode="gbr_v1" based on governance context)
    ↓
┌─────────────────────────────────────────────────────────┐
│  Mode="simple":   Standard single-path reasoning        │
│  Mode="gbr_v1":   Branch exploration → APEX collapse    │
└─────────────────────────────────────────────────────────┘
    ↓
APEX_JUDGE (same verdict surface, enhanced with quantum metadata)
    ↓
VAULT999 (witness from existing infrastructure)
```

---

## Files to Create (Internal Only)

| File | Location | Purpose |
|------|----------|---------|
| `branch_explorer.py` | `core/organs/` or `core/governance/` | Branch exploration engine |
| `apex_collapse.py` | `core/governance/` | Collapse logic (wrapped by existing APEX) |
| `quantum_types.py` | `core/contracts/` | Internal types only (BranchState, BranchSet) |
| `witness_adapter.py` | `core/telemetry/` | Adapter to existing witness/Vault |

**NOT created:**
- No `quantum_adapter.py` in `aaa_mcp/`
- No new ToolSpec in `public_registry.py`
- No new public tool names

---

## Integration Points

### 1. Kernel Router (`core/kernel/stage_orchestrator.py` or `core/pipeline.py`)

Add mode dispatch:
```python
async def route_query(query, session_id, mode="simple", **kwargs):
    if mode == "gbr_v1":
        # Check 888_HOLD via existing auth
        if not await check_quantum_auth(session_id):
            raise HoldRequired("888_HOLD required for GBR mode")
        return await gbr_kernel.process(query, session_id)
    else:
        return await standard_kernel.process(query, session_id)
```

### 2. APEX_JUDGE Tool (`arifosmcp/runtime/tools.py`)

No change to ToolSpec. Internally:
```python
async def apex_judge(candidate_output, session_id, context=None):
    # Existing logic...
    
    # If GBR mode was requested in context:
    if context and context.get("mode") == "gbr_v1":
        verdict = await apex_collapse_engine.collapse(branch_set)
    else:
        verdict = await standard_judge.evaluate(candidate_output)
    
    # Return same verdict schema
    return verdict
```

### 3. Internal AGI Tools

Add optional `mode` parameter (not exposed in public schema):
```python
async def agi_reason(query, session_id, mode="simple", auth_context=None):
    """
    Internal parameter:
    - mode="simple": Standard reasoning
    - mode="gbr_v1": Quantum branching (requires 888_HOLD in auth_context)
    """
```

---

## Authentication Flow (F11/F13)

```
1. User calls existing tool with high-stakes context
2. Kernel detects risk tier → suggests GBR mode
3. If 888_HOLD present in auth_context:
       → Route to GBR kernel
   Else:
       → Return HOLD_REQUIRED
       → User must confirm via existing 888_HOLD flow
       → Retry with auth_context containing hold_token
```

Key: Reuse existing `888_HOLD` infrastructure, don't create parallel auth.

---

## Witness Integration (F3)

**Current GBR:** In-memory `WitnessLogger` with its own Merkle chain  
**Required:** Wire to existing VAULT999 infrastructure

```python
# witness_adapter.py
class QuantumWitnessAdapter:
    """Adapts GBR quantum events to existing witness pipeline."""
    
    def __init__(self, vault_client, session_id):
        self.vault = vault_client
        self.session_id = session_id
    
    def log_superposition_created(self, branch_set):
        # Emit to existing witness/telemetry pipeline
        # NOT new in-memory chain
        self.vault.emit_event({
            "type": "quantum_superposition",
            "session_id": self.session_id,
            "set_id": branch_set.set_id,
            "branches": len(branch_set.branches),
        })
```

---

## Floor Enforcement (F1-F13)

Hardcoded thresholds → Bind to canon:

```python
# Instead of:
FLOOR_WEIGHTS = {"F01": 1.0, "F02": 0.95, ...}  # Hardcoded

# Use:
from core.shared.floors import THRESHOLDS, WEIGHTS
weights = WEIGHTS.get("quantum", DEFAULT_QUANTUM_WEIGHTS)
```

---

## Concrete Changes Needed

### Phase 1: Internal Types (Safe)
```python
# core/contracts/quantum_types.py
# - BranchState, BranchSet, VerdictQuantum
# - NO F-alignment claims in comments without real wiring
# - Clear docstring: "Internal types for quantum branching mode"
```

### Phase 2: Engine Integration (Careful)
```python
# core/governance/quantum_collapse.py
# - APEXCollapseEngine uses existing APEX verdict types
# - Returns SEAL/PARTIAL/SABAR/VOID with quantum metadata
```

### Phase 3: Kernel Wiring (Critical)
```python
# core/pipeline.py
# - Add mode="gbr_v1" path
# - Gate behind existing 888_HOLD check
```

### Phase 4: Telemetry Adapter
```python
# core/telemetry/quantum_witness.py
# - Adapter pattern to existing witness
# - No standalone Merkle chain
```

---

## Public API Surface (Unchanged)

```python
# Existing tools - NO NEW TOOLSPECS
init_anchor_state()     # Same
arifOS_kernel()         # Same (adds internal mode routing)  
agi_reason()            # Same (adds internal mode param)
apex_judge()            # Same (adds quantum metadata in response)
vault_seal()            # Same
```

**Only addition:** Quantum metadata in existing verdict responses when mode="gbr_v1" was used.

---

## Epistemic Status

| Claim | Status |
|-------|--------|
| Architecture is sound | PLAUSIBLE |
| Implementation ready | NOT YET |
| Constitutional compliance | PENDING wiring to real F11/F13/Vault |

---

## Next Steps (When Ready)

1. **Review this plan** with constitutional lens
2. **Surgical implementation** following Phase 1-4
3. **Evals** asserting branches considered, floor violations logged
4. **888_HOLD integration** with real auth flow
5. **Vault witness integration** replacing in-memory logger

---

## Seal

```
888_JUDGE
GBR_v1 Option C Plan
Internal Kernel Mode Only
No New Public Tools

Ditempa Bukan Diberi
```

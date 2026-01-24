# 🏛️ Architecture: MCP-Core Unification (v51)

**Status:** APPROVED (For v51 Cycle)
**Track:** B (Architecture)
**Objective:** Wire the "Head" (MCP Tools) to the "Body" (Core Engines) to eliminate parallel implementations.

---

## 1. The Current Gap (v50.5)

Currently, `arifos` operates as two parallel systems:

| Layer | Implementation | Source of Truth |
|:---|:---|:---|
| **Track C (MCP)** | `mcp_trinity.py` | **Standalone Logic** (Hardcoded in file) |
| **Track B (Core)** | `arifos.core.engines.*` | **Authority Specs** (Loads `metrics.py` & JSONs) |

**The Risk:** Changes to JSON specs (The Law) are *not* automatically respected by MCP tools because MCP uses its own inline logic.

---

## 1.1 The Geometry of Separation (v51 Target)

This is the definitive contrast between the three zones in the v51 architecture.

### 1) AAA_MCP (The Body / The Hands)
- **Role:** Application layer.
- **Nature:** Universal adapter. Speaks JSON-RPC (MCP) to the outside world.
- **Logic Level:** Zero. It does not think; it only routes.
- **Contrast:** High kinetic energy (I/O, transport, serialization), zero authority.
- **Contents (target):** `server.py`, `bridge.py`, `rate_limiter.py`.

### 2) arifos/core (The Brain / The Soul)
- **Role:** Kernel.
- **Nature:** Pure logic. Speaks Python dataclasses and mathematics.
- **Logic Level:** Total. All reasoning, judgment, and ignition happens here.
- **Contrast:** High potential energy (decision making), zero connectivity.
- **Contents (target):** `engines/`, `system/constitution.py`, `system/metrics.py`.

### 3) arifos/mcp (The Ghost / The Skin)
- **Role:** Legacy / archive.
- **Nature:** Monolith (v50 mixed Body + Brain).
- **Logic Level:** Deprecated.
- **Contrast:** Entropy (duplicated logic, hardcoded rules).
- **Fate:** Rename to `_legacy_mcp` or delete to prevent accidental imports.

**Power of this separation:** The Brain can evolve without breaking the Body.
Track B law governs core directly; AAA_MCP only delivers the verdict.

---

## 2. The Unification Target (v51)

We will refactor `mcp_trinity.py` from a **Monolith** into a **Thin Adapter**.

### 🔌 The "Adapter Pattern"

The MCP layer should **only** handle:
1.  Protocol translation (JSON schema `-->` Python Objects).
2.  Rate limiting.
3.  Error formatting.

It should **delegate** all thinking/logic to `arifos.core.engines`.

### 🗺️ The Wiring Map

| MCP Tool | Adapter Call | Core Engine Target |
|:---|:---|:---|
| **`agi_genius`** | `engine.sense(...)`<br>`engine.think(...)` | [`arifos.core.engines.agi_engine.AGIEngine`](file:///c:/Users/User/arifOS/arifos/core/engines/agi_engine.py) |
| **`asi_act`** | `engine.process(...)` | `arifos.core.engines.asi_engine.ASIEngine` |
| **`apex_judge`** | `engine.judge(...)` | `arifos.core.engines.apex_engine.APEXEngine` |
| **`999_vault`** | `vault.seal(...)` | `arifos.core.memory.vault.Vault` |

---

## 3. Implementation Plan

### Phase 1: The Bridge (Safe Transition)
Create a new module `arifos/mcp/tools/v51_bridge.py`.
This module imports the Heavy Engines and exposes simplified functions.

```python
# arifos/mcp/tools/v51_bridge.py
from arifos.core.engines.agi_engine import AGIEngine

_AGI = AGIEngine()  # Singleton or Session-scoped

def bridge_agi_sense(query: str, context: dict) -> dict:
    result = _AGI.sense(query, context)
    return result.as_dict()  # Convert Core Dataclass to Dict
```

### Phase 2: The Swap
Modify `mcp_trinity.py` to use the bridge instead of inline logic.

**Before:**
```python
def mcp_agi_genius(action...):
    # Inline logic...
    lane = "HARD" # Hardcoded
    return {...}
```

**After:**
```python
from .v51_bridge import bridge_agi_sense

def mcp_agi_genius(action...):
    if action == "sense":
        return bridge_agi_sense(query, context)
```

### Phase 3: The Purge
Delete the thousands of lines of duplicate logic from `mcp_trinity.py`.
This reduces the file size by ~80% and ensures **Single Source of Truth**.

---

## 4. Why This is "Proper"

1.  **Constitutional Integrity:** Updating a JSON threshold in `AAA_MCP` immediately affects MCP behavior because Core Engines read it.
2.  **DRY (Don't Repeat Yourself):** Logic exists in one place (`arifos.core`), not two.
3.  **Testability:** We can test `AGIEngine` in isolation without spinning up an MCP server.

** Recommendation:** Execute Phase 1 & 2 in the next development cycle (v51).

# v55.5 Contrast Analysis: Existing vs New Code

## Executive Summary

| Component | Existing | New | Merge Decision |
|-----------|----------|-----|----------------|
| **types.py** | Pydantic models, complete | Missing | **KEEP EXISTING** |
| **physics.py** | Greek symbols (encoding issues) | ASCII + complete | **MERGE: Keep functions, add ASCII aliases** |
| **crypto.py** | Complete | Missing | **KEEP EXISTING** |
| **guards.py** | F9/F10 guards | Missing | **KEEP EXISTING** |
| **atlas.py** | Missing | Complete | **ADD NEW** |
| **_0_init.py** | Missing | Complete Airlock | **ADD NEW** |
| **core_*.py** | Stage functions | Missing | **KEEP EXISTING, refactor to organs/** |

## Detailed Contrast

### 1. shared/types.py

**Existing (KEEP):**
- ✅ Pydantic BaseModel classes
- ✅ ThoughtNode, ThoughtChain
- ✅ FloorScores with all 13 floors
- ✅ AgiMetrics, AsiMetrics, ApexMetrics
- ✅ Verdict enum

**New (DISCARD - not present):**
- N/A

**Merge Action:** Keep existing types.py entirely.

---

### 2. shared/physics.py

**Existing (PARTIAL KEEP):**
- ✅ Uses actual Greek symbols (ΔS, Ω_0, etc.) - causes Windows encoding issues
- ✅ Basic implementations
- ❌ Missing some functions

**New (MERGE IN):**
- ✅ ASCII aliases (delta_S, Omega_0)
- ✅ More complete implementations
- ✅ ConstitutionalTensor unified state
- ✅ Better documentation

**Merge Action:** 
- Keep new physics.py as base
- Ensure all functions have ASCII aliases
- Add any missing functions from existing

---

### 3. shared/crypto.py

**Existing (KEEP):**
- ✅ Ed25519, SHA-256, Merkle
- ✅ Complete implementation

**New (DISCARD - not present):**
- N/A

**Merge Action:** Keep existing crypto.py.

---

### 4. shared/guards.py

**Existing (KEEP):**
- ✅ F9 Anti-Hantu detection
- ✅ F10 Ontology validation
- ✅ Injection guards

**New (DISCARD - not present):**
- N/A

**Merge Action:** Keep existing guards.py.

---

### 5. shared/atlas.py

**Existing (NONE):**
- N/A

**New (ADD):**
- ✅ Λ(), Θ(), Φ() functions
- ✅ Lane classification
- ✅ GPV (Governance Placement Vector)

**Merge Action:** Add new atlas.py entirely.

---

### 6. organs/_0_init.py

**Existing (NONE):**
- N/A

**New (ADD):**
- ✅ Complete Airlock implementation
- ✅ F11: Command Authority
- ✅ F12: Injection Guard (25+ patterns)
- ✅ SessionToken with crypto signing
- ✅ AuthorityLevel enum

**Merge Action:** Add new _0_init.py entirely.

---

### 7. core_*.py → organs/_1_agi.py, _2_asi.py, _3_apex.py, _4_vault.py

**Existing (REFACTOR):**
- ✅ core_asi.py: Stage 444, 555, 666 functions
- ✅ core_apex.py: Stage 777, 888, 889 functions
- ✅ core_memory.py: VAULT999 operations

**New (not yet implemented):**
- ⏳ _1_agi.py
- ⏳ _2_asi.py (merge with core_asi.py)
- ⏳ _3_apex.py (merge with core_apex.py)
- ⏳ _4_vault.py (merge with core_memory.py)

**Merge Action:**
- Refactor core_asi.py → _2_asi.py
- Refactor core_apex.py → _3_apex.py
- Refactor core_memory.py → _4_vault.py
- Create new _1_agi.py

---

## Hardened Merge Plan

### Phase 1: shared/ (Complete)
1. ✅ types.py - Keep existing
2. ✅ crypto.py - Keep existing
3. ✅ guards.py - Keep existing
4. ✅ physics.py - Merge new with ASCII compatibility
5. ✅ atlas.py - Add new

### Phase 2: organs/ (Complete foundation)
1. ✅ _0_init.py - Add new (Airlock)
2. ⏳ _1_agi.py - Create new
3. ⏳ _2_asi.py - Refactor from core_asi.py
4. ⏳ _3_apex.py - Refactor from core_apex.py
5. ⏳ _4_vault.py - Refactor from core_memory.py

### Phase 3: Archive old files
- Move core_*.py to core/archive/

---

## Import Alignment

All imports must use:
```python
from core.shared.types import ...
from core.shared.physics import ...
from core.shared.crypto import ...
from core.shared.guards import ...
from core.shared.atlas import ...
from core.organs._0_init import ...
```

---

**Status:** Analysis Complete → Ready for Hardened Merge

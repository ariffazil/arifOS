# arifOS v47 Migration Guide

## Overview

Version 47 introduces the **Equilibrium Architecture** - a thermodynamic reorganization of arifOS core to reduce entropy and improve structural clarity.

**Entropy Reduction:** ΔS -5.5 (from 11.9 to 6.4)

## What Changed

### 1. State Management Layer (New: `arifos_core.state`)

**Moved from:** `arifos_core.apex.governance`  
**Moved to:** `arifos_core.state`

Ledger and merkle functionality now has its own dedicated module, separate from governance logic.

#### Migration

**Old imports:**
```python
from arifos_core.apex.governance.ledger_hashing import sha256_hex, compute_entry_hash
from arifos_core.apex.governance.merkle import build_merkle_tree, MerkleTree
from arifos_core.apex.governance.ledger_cryptography import CryptographicLedger
from arifos_core.apex.governance.merkle_ledger import MerkleLedger
```

**New imports:**
```python
from arifos_core.state.ledger_hashing import sha256_hex, compute_entry_hash
from arifos_core.state.merkle import build_merkle_tree, MerkleTree
from arifos_core.state.ledger_cryptography import CryptographicLedger
from arifos_core.state.merkle_ledger import MerkleLedger
```

**Backward Compatibility:** Old imports still work with deprecation warnings until v48.

---

### 2. Hypervisor Layer (New: `arifos_core.hypervisor`)

**Moved from:** `arifos_core.guards`  
**Moved to:** `arifos_core.hypervisor`

System-level guards (F10-F12) now organized under hypervisor layer for clearer separation.

#### Migration

**Old imports:**
```python
from arifos_core.guards import InjectionGuard, OntologyGuard, NonceManager, DependencyGuard
from arifos_core.guards.injection_guard import scan_for_injection
from arifos_core.guards.session_dependency import SessionState
```

**New imports:**
```python
from arifos_core.hypervisor import InjectionGuard, OntologyGuard, NonceManager, DependencyGuard
from arifos_core.hypervisor.guards.injection_guard import scan_for_injection
from arifos_core.hypervisor.guards.session_dependency import SessionState
```

**Backward Compatibility:** Old imports still work with deprecation warnings until v48.

---

### 3. Dead Code Removed

**Removed:** `arifos_core/system/research/`

The research directory contained proof-of-concept code (DSPy demo) that was not used in production. It has been archived to `archive/removed_in_v47/research/` for reference.

**Impact:** None if you're using production code. If you were importing research modules, they are now in the archive.

---

## Updated Architecture

```
arifos_core/
├── state/              # NEW: State management (ledger, merkle)
│   ├── ledger.py
│   ├── ledger_cryptography.py
│   ├── ledger_hashing.py
│   ├── merkle.py
│   └── merkle_ledger.py
│
├── hypervisor/         # NEW: System-level protection
│   └── guards/         # Moved from arifos_core/guards
│       ├── injection_guard.py (F12)
│       ├── ontology_guard.py (F10)
│       ├── nonce_manager.py (F11)
│       └── session_dependency.py
│
├── apex/
│   └── governance/     # REFINED: Pure governance logic
│       ├── fag.py
│       ├── session_physics.py
│       ├── sovereign_signature.py
│       └── proof_of_governance.py
│
├── enforcement/        # AUDITED: All 12 subdirs active
│   ├── attestation/
│   ├── audit/
│   ├── eval/
│   ├── evidence/
│   ├── floor_detectors/
│   ├── judiciary/
│   ├── routing/
│   ├── stages/
│   ├── trinity/
│   ├── validators/
│   └── verification/
│
├── guards/             # DEPRECATED: Backward compat shims
├── memory/             # UNCHANGED
├── system/             # CLEANED: research/ removed
└── ...
```

---

## Migration Steps

### For Library Users

1. **Update imports** (recommended but not required immediately):
   ```python
   # Find and replace in your codebase:
   from arifos_core.apex.governance -> from arifos_core.state
   from arifos_core.guards -> from arifos_core.hypervisor
   ```

2. **Test your code** to ensure backward compatibility shims work.

3. **Remove deprecation warnings** by updating to new import paths before v48.

### For Core Developers

1. **Always use new import paths** in new code:
   - State: `arifos_core.state`
   - Hypervisor: `arifos_core.hypervisor`

2. **Update tests** to use new paths (tests don't trigger deprecation warnings).

3. **Document any new modules** following the v47 structure.

---

## Deprecation Timeline

- **v47 (2026-01-12):** New structure introduced, old imports work with warnings
- **v48 (TBD):** Backward compatibility shims removed, old imports fail

---

## Rationale

### Why Separate State from Governance?

**Before (v46):** `apex/governance` mixed:
- Authority logic (who can do what)
- State persistence (ledger, merkle)

**After (v47):**
- `apex/governance` = Pure governance (authority, proofs, session physics)
- `state` = Pure state management (what happened, cryptographic verification)

**Benefit:** Clearer separation of concerns, easier to reason about.

### Why Elevate Guards to Hypervisor?

**Before (v46):** `guards` felt like a miscellaneous collection.

**After (v47):** `hypervisor` clearly signals "system-level protection layer."

**Benefit:** Aligns with OS-level protection metaphor (hypervisor = kernel-level enforcement).

---

## Testing

Run the test suite to verify no breakage:

```bash
# Allow legacy spec (existing issue, unrelated to v47)
ARIFOS_ALLOW_LEGACY_SPEC=1 pytest tests/

# Test state imports
python3 -c "from arifos_core.state import merkle, ledger_hashing; print('OK')"

# Test hypervisor imports  
python3 -c "from arifos_core.hypervisor import InjectionGuard, DependencyGuard; print('OK')"

# Test backward compatibility
python3 -c "import warnings; warnings.simplefilter('always'); from arifos_core.guards import InjectionGuard"
```

---

## Questions?

See:
- Architecture doc: `docs/ARIFOS_CORE_ARCHITECTURE.md`
- Issue: [FEAT] arifOS Core Equilibrium Architecture v47
- Removed code: `archive/removed_in_v47/README.md`

---

**DITEMPA BUKAN DIBERI** — Architecture forged from constitutional principles, not convenience.

# CCC Constitutional Memory

**Location:** `vault_999/CCC_CONSTITUTIONAL/`

**Purpose:** Constitutional knowledge referencing vault seals as canonical source

**New in v50.1:** Complete integration with vault seal system

---

## Overview

CCC (Constitutional Core Context) is the **single source of constitutional truth**.

**Key Insight:** All constitutional knowledge comes from the vault seal.

---

## What CCC Provides

### **1. Floor Thresholds (from Seal)**

```python
from arifos.core.memory.vault.ccc_constitutional_memory import get_constitutional_memory

ccc = get_constitutional_memory()

# Get floor threshold from sealed state
truth_threshold = ccc.get_floor_threshold("F2_truth")  # Returns 1.0
```

### **2. Action Validation (against Seal)**

```python
# Validate action against sealed constitution
is_valid = ccc.validate_action("write_file", {"path": "data.json"})

if is_valid:
    # Action complies with sealed constitution
    proceed_with_action()
else:
    # Action violates constitutional floors
    raise ConstitutionalViolation()
```

### **3. Sealed Constants (all floors)**

```python
# Get all constitutional constants
constants = ccc.get_sealed_constants()

# Returns:
# {
#   version: "50.0.0",
#   timestamp: "2026-01-20T19:25:00Z",
#   floors: { F1_amanah: {...}, F2_truth: {...}, ... },
#   zkpc: { merkle_root: "...", has_floor_proofs: true, ... },
#   status: "SEALED"
# }
```

---

## Architecture

```
CCC Constitutional Memory
    ↓ references
vault_999/seals/current_seal.yaml
    ↓ contains
ZKPC Proof + Floor Validation Results
    ↓ used by
Floor Validators (F1-F13)
    ↓ enforce
Constitutional Governance
```

---

## Logs

CCC maintains audit trails in:

### **constitutional_decisions.jsonl**
Records of constitutional decisions:
```json
{
  "timestamp": "2026-01-20T19:30:00Z",
  "action": "write_file",
  "decision": {
    "result": "SEAL",
    "reason": "Action complies with sealed constitution"
  },
  "seal_version": "50.0.0"
}
```

### **access_log.jsonl**
Vault access attempts:
```json
{
  "timestamp": "2026-01-20T19:30:00Z",
  "operation": "READ",
  "target": "AAA_MEMORY",
  "seal_version": "50.0.0",
  "seal_valid": true
}
```

---

## Implementation

**Code:** `arifos/core/memory/vault/ccc_constitutional_memory.py` (239 lines)

**Key Class:**
```python
class ConstitutionalMemory:
    def __init__(self, vault_path: str = "vault_999")
    def get_seal_version(self) -> str
    def get_floor_threshold(self, floor: str) -> float
    def get_floor_status(self, floor: str) -> Dict[str, Any]
    def validate_action(self, action: str, context: Dict) -> bool
    def log_decision(self, action: str, decision: Dict) -> None
    def get_sealed_constants(self) -> Dict[str, Any]
    def get_decision_history(self, limit: int = 100) -> List[Dict]
```

---

## Why CCC References Seals

### **Before (Hardcoded)**
```python
TRUTH_THRESHOLD = 0.99  # Hardcoded constant
```

### **After (Sealed)**
```python
ccc = get_constitutional_memory()
TRUTH_THRESHOLD = ccc.get_floor_threshold("F2_truth")  # From vault seal
```

**Benefits:**
- ✅ Single source of truth (F4 ΔS)
- ✅ Verifiable provenance (ZKPC proofs)
- ✅ Audit trail (every access logged)
- ✅ Dynamic updates (seal updates propagate)

---

## Usage in Floor Validators

Example from F2 Truth validator:

```python
def validate_f2_truth(query: str, response: dict) -> dict:
    """F2 Truth validator using CCC memory"""
    ccc = get_constitutional_memory()

    # Get threshold from sealed state (not hardcoded!)
    threshold = ccc.get_floor_threshold("F2_truth")

    # Compute truth score
    score = compute_truth_score(query, response)

    # Validate and log
    result = {
        "pass": score >= threshold,
        "score": score,
        "threshold": threshold,
        "seal_version": ccc.get_seal_version()
    }

    # Log constitutional decision
    ccc.log_decision("F2_truth_validation", result)

    return result
```

---

## Related Notes

- [[Index - vault_999 Guide]]
- [[Seals - ZKPC Keys]]
- [[Constitutional Floors]]
- [[Vault Architecture]]

---

**Created:** 2026-01-20
**Version:** v50.1
**Implementation:** `arifos/core/memory/vault/ccc_constitutional_memory.py`

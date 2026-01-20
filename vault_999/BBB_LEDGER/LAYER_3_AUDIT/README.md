# Constitutional Audit Trail (Layer 3)

**Version:** v49.0.2
**Authority:** 888 Judge (APEX)
**Status:** OPERATIONAL

---

## Purpose

Immutable verdict log with zkPC Merkle receipts for constitutional governance.

**Constitutional Requirements:**
- **F8 Tri-Witness**: Audit trail evidence (Human·AI·Earth ≥0.95)
- **Stage 889 PROOF**: zkPC receipt generation (Merkle root + proof)
- **Stage 999 VAULT**: Memory tower placement (Phoenix-72 cooling)
- **Hash-chain integrity**: Each entry links to previous (blockchain verification)

---

## File Structure

```
LAYER_3_AUDIT/
├── constitutional_ledger.jsonl    # Primary audit trail (append-only)
├── merkle_roots.jsonl              # Merkle tree roots (cryptographic verification)
├── hash_chain.txt                  # Latest hash for chain verification
└── README.md                       # This file
```

---

## Ledger Schema (constitutional_ledger.jsonl)

Each line is a **single JSON object** (JSONL format, newline-delimited):

```json
{
  "entry_id": "UUID v4",
  "timestamp": "ISO8601 datetime",
  "session_id": "CLIP_YYYYMMDD_NNN format",
  "verdict": "SEAL|PARTIAL|VOID|SABAR|888_HOLD",
  "floor_scores": {
    "F1_amanah": true,
    "F2_truth": 0.99,
    "F3_triwitness": 0.97,
    "F4_clarity": -0.18,
    "F5_peace": 1.0,
    "F6_empathy": 0.96,
    "F7_humility": 0.04,
    "F8_genius": 0.85,
    "F9_cdark": 0.15,
    "F10_ontology": true,
    "F11_authority": true,
    "F12_injection": 0.98,
    "F13_curiosity": 0.87
  },
  "trinity_indices": {
    "vitality_psi": 1.2,
    "genius_g": 0.82,
    "dark_cleverness_c": 0.12
  },
  "zkpc_receipt": {
    "merkle_root": "SHA256 hash",
    "proof_type": "Merkle|zkSNARK",
    "witness_consensus": 0.98
  },
  "cooling_tier": 0,
  "previous_hash": "SHA256 of previous entry",
  "current_hash": "SHA256 of this entry"
}
```

---

## Lifecycle (EUREKA Sieve TTL)

Retention based on verdict:
- **SEAL** → ∞ (forever, permanent record)
- **PARTIAL** → 730 days (2 years)
- **888_HOLD** → ∞ (until reviewed)
- **SABAR** → 730 days (2 years)
- **VOID** → 0 (NEVER STORE, immediate discard)

---

## Phoenix-72 Cooling Tiers

| Tier | Duration | Verdict | Purpose |
|------|----------|---------|---------|
| 0 | 0h | SEAL | Immediate release (all floors pass) |
| 1 | 42h | PARTIAL | Minor soft floor warnings |
| 2 | 72h | SABAR | Standard cooling (rethink required) |
| 3 | 168h | Constitutional amendments | Critical changes (7-day cooling) |

---

## Hash Chain Verification

Each entry includes:
1. **previous_hash**: SHA-256 of previous entry (links chain)
2. **current_hash**: SHA-256 of current entry (computed from entry_id + timestamp + verdict + floor_scores + previous_hash)

**Verification:**
```python
import hashlib
import json

def verify_hash_chain(entry, previous_entry):
    # Verify previous_hash matches
    computed_previous = hashlib.sha256(
        json.dumps(previous_entry, sort_keys=True).encode()
    ).hexdigest()

    if entry["previous_hash"] != computed_previous:
        return False, "Hash chain broken"

    # Verify current_hash
    entry_copy = {k: v for k, v in entry.items() if k != "current_hash"}
    computed_current = hashlib.sha256(
        json.dumps(entry_copy, sort_keys=True).encode()
    ).hexdigest()

    return entry["current_hash"] == computed_current, "Valid"
```

---

## Constitutional Authority

**Stage 889 PROOF** (zkPC Merkle Receipt):
- Combines F1-F13 floor scores into Merkle tree
- Calculates Merkle root (SHA-256)
- Generates zkPC proof (Merkle path + root)

**Stage 999 VAULT** (Memory Placement):
- Writes to BBB_LEDGER/LAYER_3_AUDIT (permanent storage)
- Updates hash chain (continuous verification)
- Enforces Phoenix-72 cooling (tier assignment)
- Applies EUREKA Sieve TTL (retention policy)

---

## Usage (Python Example)

```python
import json
import uuid
import hashlib
from datetime import datetime, timezone

def write_ledger_entry(verdict, floor_scores, trinity_indices, zkpc_receipt, cooling_tier=0, previous_hash=None):
    """Write constitutional verdict to audit trail"""

    entry_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    entry = {
        "entry_id": entry_id,
        "timestamp": timestamp,
        "session_id": f"CLIP_{datetime.now().strftime('%Y%m%d')}_{entry_id[:3]}",
        "verdict": verdict,
        "floor_scores": floor_scores,
        "trinity_indices": trinity_indices,
        "zkpc_receipt": zkpc_receipt,
        "cooling_tier": cooling_tier,
        "previous_hash": previous_hash or "GENESIS",
    }

    # Calculate current hash
    entry_copy = {k: v for k, v in entry.items() if k != "current_hash"}
    current_hash = hashlib.sha256(
        json.dumps(entry_copy, sort_keys=True).encode()
    ).hexdigest()
    entry["current_hash"] = current_hash

    # Append to ledger (JSONL format)
    with open("vault_999/BBB_LEDGER/LAYER_3_AUDIT/constitutional_ledger.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Update latest hash
    with open("vault_999/BBB_LEDGER/LAYER_3_AUDIT/hash_chain.txt", "w") as f:
        f.write(current_hash)

    return entry_id, current_hash
```

---

**DITEMPA BUKAN DIBERI** — Constitutional audit trail forged through cryptographic sealing, not given through trust.

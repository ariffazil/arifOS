# Memory & Cooling Ledger Tests

**Scope:** 5-Layer Memory Hierarchy & Ledger Integrity
**Target:** `CoolingLedger`, `Phoenix-72`, Memory Routing

This directory tests the **memory layer** including the cooling ledger, cryptographic integrity, and temporal memory management.

---

## Test Files

| File | Description |
|------|-------------|
| `test_cooling_ledger.py` | Basic ledger operations (create, read, seal) |
| `test_cooling_ledger_integrity.py` | Hash chain integrity verification |
| `test_cooling_ledger_integrity_mocked.py` | Integrity tests with mocked dependencies |
| `test_cooling_ledger_kms_integration.py` | Key Management System integration |
| `test_cooling_ledger_schema_compliance.py` | Schema validation and compliance |
| `test_ledger_cryptography.py` | Cryptographic hash and signature validation |
| `test_ledger_sanity.py` | Sanity checks and basic operations |
| `test_memory_phase1_invariants.py` | Memory phase 1 invariant enforcement |
| `test_memory_phase1_routing.py` | Memory routing logic |
| `test_memory_trinity.py` | Trinity-based memory operations |
| `test_phoenix72.py` | Phoenix 72-hour cooling tests |
| `test_phoenix_72_guardrail.py` | Phoenix cooling policy guardrails |

---

## Key Concepts

### 5-Layer Memory Hierarchy
| Layer | TTL | Purpose |
|-------|-----|---------|
| L0 | 0h | Hot session memory (volatile) |
| L1 | 24h | Daily cooling |
| L2 | 72h | Phoenix cooling (truth stabilizes) |
| L3 | 7d | Weekly reflection |
| L4 | 30d | Monthly canon |
| L5 | 365d+ | Constitutional law (immutable) |

### Phoenix-72 Cooling
Truth must "cool" for 72 hours before promotion:
- Prevents hasty canonization
- Allows for error correction
- Reduces temporal bias

### Cooling Ledger (VAULT-999)
Immutable hash-chained audit trail:
- Every decision recorded
- Cryptographic integrity
- Non-repudiation

---

## Running Tests

```bash
# Run all memory tests
pytest tests/memory/ -v

# Run ledger-specific tests
pytest tests/memory/test_cooling_ledger*.py -v

# Run Phoenix cooling tests
pytest tests/memory/test_phoenix*.py -v
```

---

**Constitutional Floor:** F1 (Amanah), F8 (Tri-Witness)
**DITEMPA BUKAN DIBERI**

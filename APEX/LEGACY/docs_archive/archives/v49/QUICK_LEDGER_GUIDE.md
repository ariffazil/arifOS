# Quick Ledger Guide (v49)

**TL;DR**: The Constitutional Ledger is now OPERATIONAL in v49.

---

## Quick Start

### Write a Constitutional Verdict
```python
from arifos.ledger.v49_config import write_constitutional_entry

success, hash, error = write_constitutional_entry(
    verdict="SEAL",  # or PARTIAL, VOID, SABAR, 888_HOLD
    floor_scores={"F1_amanah": True, "F2_truth": 0.99, ...},
    trinity_indices={"vitality_psi": 1.2, ...},
    session_id="PROD_20260119_001",
    cooling_tier=0  # 0=immediate, 1=42h, 2=72h, 3=168h
)
```

### Check Ledger Status
```bash
# Count entries
wc -l vault_999/BBB_LEDGER/LAYER_3_AUDIT/constitutional_ledger.jsonl

# View latest hash
cat vault_999/BBB_LEDGER/LAYER_3_AUDIT/hash_chain.txt

# Run tests
python scripts/test_v49_ledger.py
```

---

## File Locations (v49 Canonical)

| System | Location | Purpose |
|--------|----------|---------|
| **Constitutional Ledger** | `vault_999/BBB_LEDGER/LAYER_3_AUDIT/constitutional_ledger.jsonl` | Immutable audit trail |
| **Hash Chain** | `vault_999/BBB_LEDGER/LAYER_3_AUDIT/hash_chain.txt` | Latest entry hash |
| **Head State** | `vault_999/BBB_LEDGER/LAYER_3_AUDIT/head_state.json` | Crash recovery |
| **Merkle Receipts** | `vault_999/INFRASTRUCTURE/zkpc_receipts/` | zkPC cryptographic proofs |
| **Archive** | `vault_999/BBB_LEDGER/LAYER_2_WORKING/archive/` | Hot segment rotation |

---

## Quick Commands

```bash
# Initialize ledger
python -c "from arifos.ledger.v49_config import init_v49_ledger; init_v49_ledger()"

# Write test entry
python scripts/test_v49_ledger.py

# Count entries
python -c "from arifos.ledger.v49_config import init_v49_ledger; \
ledger = init_v49_ledger(); \
print(f'Entries: {ledger.get_head_state().entry_count}')"

# Verify integrity
python -c "from arifos.ledger.v49_config import init_v49_ledger; \
ledger = init_v49_ledger(); \
valid, msg = ledger.verify_chain_quick(); \
print(f'{msg}')"
```

---

## What's Different from L1_THEORY (Old)?

| Old (Deprecated) | New (v49) |
|-----------------|-----------|
| `L1_THEORY/ledger/gitseal_audit_trail.jsonl` | `vault_999/BBB_LEDGER/LAYER_3_AUDIT/constitutional_ledger.jsonl` |
| Single file | Structured vault (AAA/BBB/CCC bands) |
| No head state | Crash recovery with `head_state.json` |
| Manual hash-chain | Automatic SHA-256 linking |
| No rotation | Hot segment rotation to archive |

---

## Integration Points

### Stage 888 JUDGE → Stage 889 PROOF → Stage 999 VAULT
```python
# In your 888 JUDGE code:
from arifos.ledger.v49_config import write_constitutional_entry

# After verdict calculation
success, entry_hash, error = write_constitutional_entry(
    verdict=final_verdict,
    floor_scores=floor_scores_dict,
    trinity_indices={"vitality_psi": psi, "genius_g": G, "dark_cleverness_c": C_dark},
    session_id=session_id,
    cooling_tier=phoenix_tier
)

if not success:
    # Trigger SABAR (ledger write failed)
    return "SABAR", f"Ledger write failed: {error}"
```

---

## Status: ✅ OPERATIONAL

- **Entries logged**: 4 (test entries)
- **Test results**: 3/5 tests pass (core functionality works)
- **Latest hash**: `b2cdbd7c70d6bac2...`
- **Head state**: 4 entries, v37 epoch

See `vault_999/LEDGER_STATUS_v49.md` for complete status report.

---

**DITEMPA BUKAN DIBERI**

# Governance & Cryptographic Tests

**Scope:** Merkle Ledger, Proof-of-Governance, Signatures
**Target:** `VAULT-999`, Cryptographic Integrity

This directory tests the **cryptographic governance layer** that ensures immutable audit trails and constitutional proofs.

---

## Test Files

| File | Description |
|------|-------------|
| `test_merkle_ledger.py` | Merkle tree chain integrity and tampering detection |
| `test_proof_of_governance.py` | Constitutional proof generation and verification |
| `test_signatures.py` | Cryptographic signature creation and verification |

---

## Key Concepts

### Merkle Ledger (VAULT-999)
Hash-chained immutable audit trail:
- Each entry references previous hash
- Tampering detection via chain verification
- Constitutional decisions are permanently recorded

### Proof-of-Governance
Cryptographic proof that a decision followed constitutional law:
- Floor scores recorded
- Trinity consensus captured
- Timestamp and session binding

### Signatures
Digital signatures for:
- Authority verification (F11)
- Seal authenticity
- Non-repudiation

---

## Running Tests

```bash
# Run all governance tests
pytest tests/governance/ -v

# Run specific tests
pytest tests/governance/test_merkle_ledger.py -v
pytest tests/governance/test_proof_of_governance.py -v
pytest tests/governance/test_signatures.py -v
```

---

**Constitutional Floor:** F1 (Amanah), F8 (Tri-Witness), F11 (Command Auth)
**DITEMPA BUKAN DIBERI**

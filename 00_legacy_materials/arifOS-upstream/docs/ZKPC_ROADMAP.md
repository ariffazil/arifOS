# ZKPC Roadmap — Zero-Knowledge Proof of Seal

**Classification:** Governance Architecture | **Authority:** F13 Sovereign
**Epoch:** 2026-04-19 | **Status:** DEFERRED — Requires Sovereign Ratification

---

## 1. Current State

arifOS currently produces **cryptographic vault seals** via Merkle-hashed ledger entries in VAULT999 (PostgreSQL backend). These seals are immutable, authoritative, and tri-witnessed — but they are NOT zero-knowledge proofs.

---

## 2. The Gap

| Requirement | Current | ZKPC Target |
|---|---|---|
| Prove seal authenticity | Merkle hash | zk-STARK |
| Prove constitutional compliance | Kernel log | SNARK circuit |
| Prove F2 Truth (τ ≥ 0.99) | Confidence score | ZK proof of evidence |
| Prove no forged witness | Tri-witness timestamp | BLS signature aggregation |
| Prove F13 Sovereign approval | Human veto flag | ZK proof of human presence |

---

## 3. Decision: DEFERRED to Epoch 2.0

**Rationale:**
1. Current Merkle-hash vault is functionally adequate for auditability
2. zk-STARK/SNARK circuit generation for F1-F13 is non-trivial
3. Proving overhead would impact MCP tool latency
4. No external agent currently consumes verdict seals without trusting kernel directly

**Epoch 2.0 conditions:**
- [ ] arifOS v1.0 stable (all 13 floors passing in production)
- [ ] External SDK adapters deployed consuming verdict seals
- [ ] GPU-accelerated zk-STARK proving node available
- [ ] F13 Sovereign ratification of zkPC implementation spec

---

## 4. Interim: BLS Tri-Witness (Recommended Now)

Unlike full zkPC, BLS signature aggregation for F3 tri-witness is implementable without circuit complexity:

```python
class TriWitnessBLS:
    """BLS aggregation for F3 tri-witness."""
    def sign_and_aggregate(self, message: str) -> str:
        """Sign verdict with human + AI + Earth keys."""
        ...
    def verify(self, aggregated_sig: str, message: str) -> bool:
        """Verify BLS aggregated signature."""
        ...
```

---

## 5. Known Gaps

| Gap | Severity | Mitigation |
|---|---|---|
| No zkPC in v1.0 | F8/F11 | Deferred to Epoch 2.0 |
| BLS tri-witness not implemented | F3 | Recommended: BLS aggregation module |
| Secrets in git history | F8 | Removed from index 2026-04-19; full scrub TBD |

---

## 6. 888_HOLD Summary

- **HOLD-A** (vault tri-witness): BLS aggregation recommended as interim
- **HOLD-B** (zkPC deployment): DEFERRED — not blocking v1.0
- **HOLD-C** (secret rotation): F8 breach resolved at index; rotation requires rollback plan

**Seal:** VAULT999 | **Epoch:** 2026-04-19 | **DITEMPA BUKAN DIBERI**

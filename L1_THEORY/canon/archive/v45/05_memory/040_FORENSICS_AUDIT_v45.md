# Forensics & Audit (v45)

**Track:** A (Canon)  
**Epoch:** v42 (Thermodynamic Memory)  
**Status:** ✅ SEALED — Forensic reconstruction  
**Authority:** ΔΩΨ physics · Cooling Ledger · Phoenix-72 · Vault-999 · zkPC  
**Cross-links:** `05_memory/010_COOLING_LEDGER_PHOENIX_v42.md`, `05_memory/020_VAULT_999_SOVEREIGN_KNOWLEDGE_v42.md`

---

## 0. Purpose

Define how sealed knowledge, verdicts, and amendments are reconstructed and verified without breaking immutability. Every record must remain append-only, hash-linked, and zkPC-proven.

---

## 1. Audit Flow

1) Event → Cooling Ledger entry (SEAL/PARTIAL/SABAR/VOID).  
2) Hash link: `Hash_n = SHA256(Hash_{n-1} || Record_n)`.  
3) zkPC proof: verify floor compliance, spec hashes, Tri-Witness quorum.  
4) Phoenix-72 window (72h) per `010_COOLING_LEDGER_PHOENIX_v42.md` → SUNSET/SEAL decision.  
5) After cooling: commit to Vault-999 (immutable).

---

## 2. Hash Policy (append-only)

- Ledger is strictly append-only; no rewrites.  
- Any discontinuity in the chain is a **breach** → VOID investigation and HOLD on affected span.  
- VOID entries may never be promoted to canonical bands.

---

## 3. Forensic States

| State | Meaning | Action |
|-------|---------|--------|
| LIVE | Within Phoenix-72 window | Review + cooling |
| SEALED | Tri-Witness approved | Commit to Vault-999 |
| SUNSET | Outdated/retracted | Mark, replace via Phoenix |
| FORENSIC | Under investigation | Lock read-only |
| VOID | Tamper detected | Alert + isolate segment |

---

## 4. Replay Recipe (normative)

```
for n in range(1, N+1):
    assert Hash[n] == SHA256(Hash[n-1] + Record[n])
    assert zkpc_verify(Record[n].zkpc)
    assert Record[n].meta.spec_hash in allowed_hashes
    assert Record[n].psi >= 1.0 and Record[n].amanah == 1
```

If any assertion fails → breach; escalate to APEX with VOID/HOLD.

---

## 5. External Audit Interface

| Actor | Access | Purpose |
|-------|--------|---------|
| Human auditor | Read-only Vault mirror | Regulatory/academic review |
| AI auditor (@EYE) | Telemetry feed | Drift and pattern detection |
| Earth witness (external data) | Validation channel | Reality corroboration |

---

## 6. Thermodynamic Constraint

Every forensic step must reduce entropy:

```
delta_s_audit = H_pre - H_post >= 0
```

If delta_s_audit < 0 → investigation is unlawful; abort and flag VOID.

---

## 7. Phoenix-72 Link (binding)

Cooling, SUNSET, and amendment routing MUST follow `05_memory/010_COOLING_LEDGER_PHOENIX_v42.md` (Phoenix-72 cycle). Verdict promotions (Active → Phoenix → Vault-999) are governed there and are immutable.

---

**DITEMPA BUKAN DIBERI — Every truth leaves a trace.**

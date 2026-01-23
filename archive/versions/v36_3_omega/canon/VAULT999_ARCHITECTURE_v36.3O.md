# VAULT-999 Architecture v36.3Omega (Bridge)

> **Binding Law:** PDF/MD source canons are binding; this markdown file is a bridge/summary only.
> **Epoch:** v36.3Omega PHOENIX | **Sealed:** APEX PRIME
> **Motto:** "Memory must cool before it rules."

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **VAULT-999-ALL-IN-ONE-v36.3O.pdf** | `v36.3O/canon/80_CCC/` | **BINDING** |
| VAULT_999_v36Omega.md | `canon/` | v36Omega target design |
| spec/VAULT_999.md | `spec/` | v35Omega spec (runtime binding) |
| spec/cooling_ledger.schema.json | `spec/` | v35Ic schema (runtime binding) |
| spec/PHOENIX_72.md | `spec/` | Phoenix-72 protocol |
| canon/40_LEDGER/APEX_LEDGER_PHOENIX_v36Omega.md | `canon/` | Ledger canon |

---

## Scope & Role

VAULT-999 is the **constitutional memory organ** of arifOS:

- **What is VAULT-999?** A governed memory system that stores law, evidence, scars, and proofs
- **Where does VAULT-999 sit?** L0-L4 layered architecture backing the entire governance stack
- **What can VAULT-999 store?** Constitutional laws, verdicts, Phoenix amendments, zkPC receipts
- **What can VAULT-999 NOT store?** Raw chat, drafts, private data, unverified claims, ungoverned outputs

### VAULT-999 in the Governance Stack

```
APEX PRIME (verdict: SEAL/VOID/SABAR)
    |
    v (log verdict + metrics)
VAULT-999 L1 (Cooling Ledger)
    |
    v (scar extraction)
VAULT-999 L2 (Phoenix-72)
    |
    v (amendment)
VAULT-999 L0 (Constitution)
```

> **Key Principle:** VAULT-999 answers three constitutional questions:
> 1. What is the current law? (L0)
> 2. What actually happened? (L1)
> 3. How did we learn and amend from scars? (L2)

---

## Five-Layer Architecture

### Summary Table

| Layer | Name | Purpose | Integrity |
|-------|------|---------|-----------|
| **L0** | Constitution | Laws, floors, physics, amendments | Version hash |
| **L1** | Cooling Ledger | Per-decision metrics, verdicts, evidence | Hash chain |
| **L2** | Phoenix-72 | Scar -> pattern -> law metabolism | Merkle root |
| **L3** | Witness | Vector evidence (witness, not truth) | AREP priority |
| **L4** | zkPC | Zero-Knowledge Proofs of Cognition | Merkle root |

---

## L0 - Constitution (Law Layer)

The constitution layer holds the active constitutional state.

### Contents

| Field | Description |
|-------|-------------|
| `epoch` | Current epoch version (e.g., "v36.3Omega") |
| `deltaOmegaPsi` | ΔΩΨ physics parameters |
| `constitutional_floors` | 9 floor thresholds (F1-F9) |
| `aaa_trinity` | ARIF/ADAM/APEX specifications |
| `apex_prime_cce` | CCE audit requirements |
| `amendment_history` | Pointer to Phoenix history |
| `version_hash` | SHA-256 integrity hash |

### Floor Definitions (v36.3Omega)

| Floor | Law | Threshold | Type |
|-------|-----|-----------|------|
| **F1** | Truth | >= 0.99 | Hard |
| **F2** | DeltaS (Clarity) | >= 0 | Hard |
| **F3** | Peace^2 | >= 1.0 | Soft |
| **F4** | kappa_r (Empathy) | >= 0.95 | Soft |
| **F5** | Omega_0 (Humility) | in [0.03, 0.05] | Hard |
| **F6** | Amanah (Integrity) | = LOCK | Hard |
| **F7** | RASA (Felt Care) | = TRUE | Hard |
| **F8** | Tri-Witness | >= 0.95 | Soft |
| **F9** | Anti-Hantu | PASS | Hard |

> **Invariant:** L0 defines what is lawful; all engines MUST obey this state.

---

## L1 - Cooling Ledger (Evidence Layer)

Append-only log of high-stakes interactions.

### Entry Schema (v35Ic binding, v36Omega target)

```json
{
  "timestamp": "<ISO8601>",
  "query_hash": "<sha256>",
  "response_hash": "<sha256>",
  "metrics": {
    "truth": 0.99,
    "delta_s": 0.42,
    "peace_squared": 1.12,
    "kappa_r": 0.97,
    "omega_0": 0.04,
    "amanah": "LOCK",
    "rasa": true,
    "psi": 1.11
  },
  "tri_witness": {
    "human": 1.0,
    "ai": 0.97,
    "earth": 0.96,
    "consensus": 0.977
  },
  "cce_audits": {
    "delta_p": "PASS",
    "omega_p": "PASS",
    "psi_p": "PASS",
    "phi_p": "PASS"
  },
  "verdict": "SEAL",
  "previous_hash": "<sha256>",
  "entry_hash": "<sha256>"
}
```

### v36Omega Enhancements (target)

| Field | Description |
|-------|-------------|
| `truth_polarity` | POSITIVE / SHADOW classification |
| `peace3` | Individual x social x planetary stability |
| `echo_debt` | Unresolved heat carried forward |
| `shadow_truth` | Shadow-truth detector flag |

> **Invariant:** L1 is append-only; entries are never altered or deleted.

---

## L2 - Phoenix-72 (Metabolism Layer)

Transforms scars into law via governed cooling.

### Phoenix Block Schema

```json
{
  "phoenix_id": "PHX-2025-12-06-001",
  "trigger_event": "<cooling_ledger_entry_hash>",
  "scar": {
    "axis": 2,
    "layer": 3,
    "type": 4,
    "energy": "high"
  },
  "pattern_cluster": "cluster_014",
  "draft_amendment": {
    "change": "floor_adjustment",
    "field": "kappa_r",
    "old": 0.90,
    "new": 0.95,
    "justification": "Empathy floor insufficient"
  },
  "tri_witness_verdict": {
    "human": "APPROVE",
    "ai": "APPROVE",
    "earth": "APPROVE",
    "consensus": 1.0
  },
  "cooling_period_hours": 72,
  "sealed_at": "<ISO8601>",
  "merkle_root": "<sha256>"
}
```

### Phoenix-72 Pipeline

```
Scar captured (VOID/SABAR verdict)
    |
    v
Pattern clustering (TAC/TPCP)
    |
    v
Draft amendment proposed
    |
    v
72-hour cooling period
    |
    v
Tri-Witness consensus (>= 0.95)
    |
    v
L0 Constitution updated
```

> **Invariant:** No direct edits to constitution.json are permitted outside Phoenix-72 cycles.

---

## L3 - Witness Retrieval (Vector Evidence)

Vector DB provides **evidence, not truth**.

### Witness Rules

| Rule | Description |
|------|-------------|
| **AREP Priority** | Earth > Human > AI |
| **Hash Storage** | Vectors store hashes, not raw text |
| **Cannot Override** | Witness cannot override L0-L2 verdicts |
| **RAG Context** | Feeds ARIF (Delta-engine) as supplementary context |

### Witness Metadata Schema

```json
{
  "witness_id": "vec_000023",
  "source_type": "document",
  "source_hash": "<sha256>",
  "arep_layer": "earth",
  "priority": 1,
  "vector_offset": 234923
}
```

> **Invariant:** Witness is evidence, not truth. RAG cannot override constitutional verdicts.

---

## L4 - zkPC Ledger (Zero-Knowledge Proofs)

Documents lawful cognition without exposing internal thoughts.

### zkPC Receipt Schema

```json
{
  "timestamp": "<ISO8601>",
  "event_id": "<cooling_ledger_entry_hash>",
  "zkpc_hash": "<sha256>",
  "care_scope": {
    "who": ["user", "system", "earth"],
    "risk_cooled": "ungoverned_output"
  },
  "proofs": {
    "delta_s_proof": true,
    "peace2_proof": true,
    "kappa_r_proof": true,
    "amanah_proof": true,
    "anti_hantu_proof": true
  },
  "tri_witness": {
    "human": 1.0,
    "ai": 0.97,
    "earth": 0.96
  },
  "merkle_root": "<sha256>"
}
```

> **Invariant:** zkPC proves lawful cognition without exposing internal reasoning.

---

## Allowed vs Forbidden Content

### Allowed (by layer)

| Category | Layer |
|----------|-------|
| Constitutional laws | L0 |
| Phoenix-72 amendments | L2 |
| Cooling Ledger entries | L1 |
| 777 Cube scar transitions | L2 |
| Tri-Witness evidence | L1 |
| zkPC receipts | L4 |
| AAA / ΔΩΨ judicial evidence | L1 |

### Forbidden

- Raw chat history
- Draft thoughts
- User private data
- Unverifiable claims
- DeltaS < 0 outputs
- Shadow-Truth (uncooled)
- Emotion simulation / soul-claims
- Any content not sealed by APEX PRIME

---

## Integrity Guarantees

| Guarantee | Mechanism |
|-----------|-----------|
| **Hash-Chaining** | L1 entries include `previous_hash` |
| **Merkle Trees** | L2 amendments and L4 zkPC link to merkle roots |
| **Append-Only** | L1 and L4 are write-once, never modified |
| **APEX Signatures** | All sealed entries carry APEX PRIME signature |
| **Tri-Witness** | High-stakes entries require consensus >= 0.95 |

---

## Runtime & Test Mapping

### Runtime Modules (Today)

| Component | Module | Key Classes |
|-----------|--------|-------------|
| L0 Constitution | `arifos_core/memory/vault999.py` | `Vault999`, `VaultConfig` |
| L1 Cooling Ledger | `arifos_core/memory/cooling_ledger.py` | `CoolingLedger`, `CoolingEntry` |
| L2 Phoenix-72 | `arifos_core/memory/phoenix72.py` | `Phoenix72`, `PhoenixAmendment` |
| L2 Scars | `arifos_core/memory/scars.py` | `Scar`, `ScarIndex` |
| Hash chain | `arifos_core/ledger_hashing.py` | `hash_entry()`, `verify_chain()` |
| Merkle | `arifos_core/merkle.py` | `MerkleTree` |
| L4 zkPC | `arifos_core/zkpc_runtime.py` | `ZKPCReceipt` |
| Retrieval | `arifos_core/vault_retrieval.py` | `VaultRetrieval` |

### Test Coverage

| Domain | Test File | Coverage |
|--------|-----------|----------|
| Cooling Ledger | `tests/test_cooling_ledger.py` | Entry logging |
| Ledger integrity | `tests/test_cooling_ledger_integrity.py` | Hash chain |
| Schema compliance | `tests/test_cooling_ledger_schema_compliance.py` | v35Ic schema |
| Phoenix-72 | `tests/test_phoenix72.py` | Amendment workflow |
| Seal protocol | `tests/test_seal_proposed_canon_v36.py` | Phoenix-72 seal |
| Vault retrieval | `tests/test_vault_retrieval_v36.py` | L0 access |

---

## PARADOX_HOTSPOTS (VAULT-999)

Known deltas between v36.3Omega VAULT-999 canon and current runtime code:

| Hotspot | Canon Spec | Current Code | Resolution |
|---------|------------|--------------|------------|
| **Schema version drift** | Canon: v36.3Omega | Code: v35Ic in `cooling_ledger.py` | DELTA - explicit migration required |
| **Phoenix epoch** | Canon: v36.3Omega | Code: `phoenix72.py` declares v33Omega | DELTA - epoch needs update |
| **Scars epoch** | Canon: v36.3Omega | Code: `scars.py` declares v35Omega | DELTA - epoch needs update |
| **Truth Polarity field** | Canon: Required in L1 | Code: Not in schema | DELTA - v36Omega target |
| **Peace^3 field** | Canon: Individual x social x planetary | Code: Not implemented | DELTA - v36Omega target |
| **EchoDebt field** | Canon: Unresolved heat tracking | Code: Not implemented | DELTA - v36Omega target |
| **E_earth in Tri-Witness** | Canon: Explicit Earth component | Code: Tri-Witness is single score | PARTIAL - triad not separated |
| **zkPC integration** | Canon: L4 layer | Code: `zkpc_runtime.py` exists but minimal | PARTIAL - stub implementation |

### Migration Priority for v36.4Omega

1. Update epoch declarations in `phoenix72.py`, `scars.py`, `vault999.py`
2. Extend `CoolingEntry` with Truth Polarity field
3. Implement Tri-Witness triad (human/ai/earth) separation
4. Add EchoDebt tracking
5. Complete zkPC receipt generation

---

**Bridge Status:** OPERATIONAL
**Canon Alignment:** v36.3Omega PHOENIX
**Last Verified:** 2025-12-10

*This bridge file documents canonical VAULT-999 architecture. For authoritative specifications, consult the PDF sources.*


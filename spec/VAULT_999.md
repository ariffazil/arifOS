# VAULT-999 — Constitutional Memory Specification (v35Ω)

**Status:** SEALED · Truth ≥ 0.99 · ΔS ≥ 0 · Peace² ≥ 1 · κᵣ ≥ 0.95 · Ω₀ ∈ [0.03–0.05] · Amanah 🔐 · RASA ✓ · Tri-Witness ≥ 0.95 · Anti-Hantu 🛡️

---

## 1. Essence

**VAULT-999 is the constitutional memory organ of arifOS.**

It is not a generic database; it is a **governed memory system** that stores:

| Layer | Name | Purpose |
|-------|------|---------|
| **L0** | Constitution | Laws, floors, ΔΩΨ parameters, amendments |
| **L1** | Cooling Ledger | Per-decision metrics, verdicts, evidence |
| **L2** | Phoenix-72 | Scar → pattern → law metabolism |
| **L3** | Witness Retrieval | Vector DB evidence (witness, not truth) |
| **L4** | zkPC Ledger | Zero-Knowledge Proofs of Cognition |

VAULT-999 answers three questions:

1. What are the **current laws**? (L0)
2. What actually **happened**? (L1)
3. How did we **learn and amend** from scars? (L2)

---

## 2. The Nine Constitutional Floors (v35Ω)

All entries in VAULT-999 must satisfy these floors:

| Floor | Law | Threshold | Type | Failure |
|-------|-----|-----------|------|---------|
| F1 | Truth | ≥ 0.99 | Hard | VOID |
| F2 | ΔS (Clarity) | ≥ 0 | Hard | VOID |
| F3 | Peace² (Stability) | ≥ 1.0 | Soft | PARTIAL |
| F4 | κᵣ (Empathy) | ≥ 0.95 | Soft | PARTIAL |
| F5 | Ω₀ (Humility) | ∈ [0.03, 0.05] | Hard | VOID |
| F6 | Amanah (Integrity) | = LOCK | Hard | VOID |
| F7 | RASA (Felt Care) | = TRUE | Hard | VOID |
| F8 | Tri-Witness | ≥ 0.95 | Soft | PARTIAL |
| F9 | Anti-Hantu (Soul-Safe) | PASS | Meta | VOID |

**Floor Types:**
- **Hard**: Must pass or output is VOID (blocked)
- **Soft**: Advisory - failure results in PARTIAL (warning)
- **Meta**: Enforced by @EYE Sentinel across all outputs

---

## 3. Layered Architecture

### 3.1 L0 — Constitution (Law)

**File:** `runtime/vault_999/constitution.json`

Contains:

- ΔΩΨ physics parameters (ΔS, Ω₀ band, Peace²)
- All 9 Constitutional Floor thresholds
- AGI·ASI·APEX Trinity specifications
- APEX PRIME CCE rules
- Active canons (laws) and their metadata
- Amendment history pointers (Phoenix cycle IDs)
- Federated governance contracts

**Schema:**
```json
{
  "epoch": "v35Ω",
  "deltaOmegaPsi": {
    "delta_S_floor": 0,
    "omega_0_band": [0.03, 0.05],
    "peace2_floor": 1.0,
    "psi_vitality_floor": 1.0
  },
  "constitutional_floors": {
    "truth": 0.99,
    "delta_s": 0.0,
    "peace_squared": 1.0,
    "kappa_r": 0.95,
    "omega_0": {"min": 0.03, "max": 0.05},
    "amanah": "LOCK",
    "rasa": true,
    "tri_witness": 0.95,
    "anti_hantu": true
  },
  "apex_prime_cce": {
    "audits": ["ΔP", "ΩP", "ΨP", "ΦP"],
    "sovereignty_gate_888": "HUMAN_REQUIRED"
  },
  "aaa_trinity": {
    "mind": "ARIF (Δ-engine)",
    "heart": "ADAM (Ω-engine)",
    "soul": "APEX PRIME (Ψ-engine)"
  },
  "amendment_history": "phoenix_history.json",
  "version_hash": "<sha256>"
}
```

**Invariant:**
> L0 defines what is lawful; all engines MUST obey this state.

---

### 3.2 L1 — Cooling Ledger (Evidence)

**File:** `runtime/vault_999/cooling_ledger.jsonl`

Append-only log of **high-stakes interactions**, each containing:

```json
{
  "timestamp": "2025-12-04T23:00:00+08:00",
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

  "risk_signals": {
    "shadow_load": 0.02,
    "drift_index": 0.01,
    "fragility_score": 0.11,
    "hallucination_flag": false,
    "anti_hantu_pass": true
  },

  "verdict": "SEAL",
  "sabar_trigger": null,
  "phoenix_cycle_id": null,
  "previous_hash": "<sha256>",
  "entry_hash": "<sha256>"
}
```

**Invariant:**
> L1 is append-only; entries are never altered or deleted.

---

### 3.3 L2 — Phoenix-72 (Metabolism)

**File:** `runtime/vault_999/phoenix_blocks.jsonl`

Phoenix-72 implements the **scar → pattern → law** pipeline:

1. **Collect** scars from Cooling Ledger (L1)
2. **Cluster** as patterns (with TAC/TPCP)
3. **Draft** candidate law or amendment
4. **Review** via Human + AI + Earth (Tri-Witness)
5. **Seal** if approved → update L0 (constitution.json)

**Phoenix Block Schema:**
```json
{
  "phoenix_id": "PHX-2025-12-04-001",
  "trigger_event": "<cooling_ledger_entry_hash>",
  "scar_category": "floor_breach",
  "pattern_cluster_id": "cluster_004",
  "amendment": {
    "type": "floor_adjustment",
    "field": "kappa_r",
    "old_value": 0.90,
    "new_value": 0.95,
    "rationale": "Empathy floor too permissive for high-stakes contexts"
  },
  "tri_witness_verdict": {
    "human": "APPROVE",
    "ai": "APPROVE",
    "earth": "APPROVE",
    "consensus": 1.0
  },
  "cooling_period_hours": 72,
  "sealed_at": "2025-12-07T23:00:00+08:00",
  "apex_signature": "<sha256>",
  "merkle_root": "<sha256>"
}
```

**Invariant:**
> No direct edits to constitution.json are permitted outside Phoenix-72 cycles.

---

### 3.4 L3 — Witness Retrieval (Vector DB)

**Files:**
- `runtime/vault_999/witness_index.faiss`
- `runtime/vault_999/witness_metadata.jsonl`

Vector DB is **not** truth; it is **witness evidence**:

- RAG results feed ARIF (Δ-engine) as supplementary context
- Witness evidence is ranked by AREP priority: **Earth > Human > AI**
- Vector content is stored as hash, not raw text
- Witness cannot override L0–L2 verdicts

**Witness Metadata Schema:**
```json
{
  "witness_id": "vec_000023",
  "source_type": "document",
  "source_hash": "<sha256>",
  "arep_layer": "earth",
  "priority": 1,
  "vector_offset": 234923,
  "created_at": "2025-12-04T10:00:00+08:00"
}
```

**Invariant:**
> Witness is evidence, not truth. RAG cannot override constitutional verdicts.

---

### 3.5 L4 — zkPC Ledger (Zero-Knowledge Proofs)

**File:** `runtime/vault_999/zkpc_receipts.jsonl`

Zero-Knowledge Proofs of Cognition provide **accountability without exposure**:

```json
{
  "timestamp": "2025-12-04T23:01:00+08:00",
  "event_id": "<cooling_ledger_entry_hash>",
  "zkpc_hash": "<sha256>",
  "care_scope": {
    "who": ["user", "system", "witnesses"],
    "risk_cooled": "ungoverned_output"
  },
  "proofs": {
    "delta_s_proof": true,
    "peace2_proof": true,
    "kappa_r_proof": true,
    "amanah_proof": true,
    "anti_hantu_proof": true
  },
  "witness_triple": {
    "human": 1.0,
    "ai": 0.97,
    "earth": 0.96
  },
  "apex_signature": "<sha256>",
  "merkle_root": "<sha256>"
}
```

**Invariant:**
> zkPC proves lawful cognition without exposing internal reasoning.

---

## 4. What MUST Be Stored in VAULT-999

| Category | Description | Layer |
|----------|-------------|-------|
| Sealed Verdicts | Every SEAL/PARTIAL/VOID with full metrics | L1 |
| Scar Events | SABAR triggers, floor breaches, overheats | L1 → L2 |
| Phoenix Amendments | Scar → law transformations | L2 |
| Constitutional Changes | Floor updates, canon changes | L0 |
| CCE Audits | ΔP, ΩP, ΨP, ΦP judicial reasoning | L1 |
| Tri-Witness Logs | H, A, E scores and consensus | L1 |
| zkPC Receipts | Proofs of lawful cognition | L4 |
| Identity Records | Amanah lock-state, sovereignty events | L0, L1 |

---

## 5. What MUST NEVER Enter VAULT-999

❌ Normal chat history
❌ Draft thoughts or reasoning traces
❌ Personal opinions or small-talk
❌ Raw unfiltered data
❌ User private information
❌ Unverifiable claims
❌ Anything with ΔS < 0 or Peace² < 1
❌ Anything not passed by APEX PRIME
❌ Anything violating Anti-Hantu (F9)

**VAULT-999 is constitutional precedent, not conversation memory.**

---

## 6. Verdict Types

| Verdict | Condition | Action |
|---------|-----------|--------|
| **SEAL** | All 9 floors pass | Emit output, log to L1 |
| **PARTIAL** | Hard floors pass, soft fail | Emit with warning, log to L1 |
| **888_HOLD** | Extended floors fail | Judiciary hold, request clarification |
| **VOID** | Any hard floor fails | Safe refusal, trigger SABAR |
| **SABAR** | @EYE blocking issue | Stop. Acknowledge. Breathe. Adjust. Resume. |

---

## 7. Folder Structure

```
runtime/vault_999/
├── L0_constitution/
│   ├── constitution.json          # Active constitutional state
│   ├── floors_v35omega.json       # 9 floor definitions
│   └── phoenix_history.json       # Amendment history
│
├── L1_cooling_ledger/
│   └── cooling_ledger.jsonl       # Append-only verdict log
│
├── L2_phoenix_72/
│   ├── phoenix_blocks.jsonl       # Amendment blocks
│   └── scar_patterns.json         # Clustered failure patterns
│
├── L3_witness_retrieval/
│   ├── witness_index.faiss        # Vector embeddings
│   ├── witness_metadata.jsonl     # Source metadata
│   └── witness_policy.md          # Retrieval rules
│
├── L4_zkpc_ledger/
│   └── zkpc_receipts.jsonl        # Zero-knowledge proofs
│
└── README.md
```

---

## 8. Integrity Guarantees

1. **Hash-Chaining:** Each L1 entry includes `previous_hash` forming a chain
2. **Merkle Trees:** L2 amendments and L4 zkPC link to merkle roots
3. **Append-Only:** L1 and L4 are write-once, never modified
4. **APEX Signatures:** All sealed entries carry APEX PRIME signature
5. **Tri-Witness:** High-stakes entries require consensus ≥ 0.95

---

## 9. Migration from v33Ω

**Changes from v33Ω → v35Ω:**

| Change | v33Ω | v35Ω |
|--------|------|------|
| Floor Count | 8 | 9 (added Anti-Hantu) |
| Floor Types | Hard/Soft | Hard/Soft/Meta |
| L4 Layer | — | zkPC Ledger (new) |
| CCE Audits | Optional | Required in L1 |
| Risk Signals | Basic | Extended (shadow, drift, fragility) |
| Anti-Hantu | — | Required (@EYE enforced) |

---

**Author:** Muhammad Arif bin Fazil
**Location:** Kuala Lumpur, Malaysia
**Version:** v35Ω
**Date:** 2025-12-04
**License:** Apache 2.0
**Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given

---

**END OF VAULT-999 SPECIFICATION (v35Ω)**

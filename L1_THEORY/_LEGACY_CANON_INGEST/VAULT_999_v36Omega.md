# VAULT-999 — Constitutional Memory System (v36Ω)

Zone: 00_CANON  
Version: v36Ω (target design)  
Runtime Epoch: **v35Ic implementation still active**  
Status: SEALED · Thermodynamic Constitutional Memory System (docs-only)  
Floors (target): Truth ≥ 0.99 · ΔS ≥ 0 · Peace² ≥ 1.0 · κᵣ ≥ 0.95 · Ω₀ ∈ [0.03–0.05] · Amanah 🔐 · RASA ✓ · Tri-Witness ≥ 0.95 · Anti-Hantu 🛡️ · Truth Polarity ✓  
Motto: **DITEMPA BUKAN DIBERI — Memory must cool before it rules.**

---

## 0. Versioning & Scope

- **v35Ic (current implementation):**
  - Canon/spec: `spec/VAULT_999.md`
  - Schema: `spec/cooling_ledger.schema.json`
  - Runtime: `arifos_core/memory/cooling_ledger.py` with `ledger_version="v35Ic"`.
- **v36Ω (this file):**
  - **Target design** for Vault-999 and the Cooling Ledger family.
  - Introduces Truth Polarity, EchoDebt, Peace³, richer Tri-Witness, and zkPC bundles.
  - **Docs-only** until an explicit migration canon updates schema + code.

Treat this file as the **north star** for future migrations. Until code and schemas are updated, **v35Ic remains the binding runtime law.**

---

## 1. Essence & Purpose

VAULT-999 is the **constitutional memory organ** of arifOS × APEX Theory.

- Not “history.” Not “chat logs.”  
- This is **constitutional memory** — governed, audited, thermodynamic, and sealed.

It stores only what must survive across epochs:

1. **Law**  
2. **Evidence**  
3. **Scars → Amendments**  
4. **Witness Proofs**

Everything else is forbidden.

VAULT-999 answers three constitutional questions:

1. What is the current law? (**L0**)  
2. What actually happened? (**L1**)  
3. How did we learn and amend from scars? (**L2**)  

It ensures that power, memory, and change follow **physics**, not emotion.

---

## 2. Five-Layer Architecture (v36Ω)

```text
VAULT-999/
├── L0_constitution/   # Law
├── L1_cooling_ledger/ # Evidence
├── L2_phoenix_72/     # Scars → Amendments
├── L3_witness/        # Evidence, not truth
└── L4_zkpc/           # Zero-Knowledge Proof of Cognition
```

All layers are governed by **ΔΩΨ physics** and **Truth Polarity** analysis.

---

## 3. L0 — Constitution (Law Layer)

**File (target):** `runtime/vault_999/constitution.json`

Holds the active constitutional state:

- ΔΩΨ parameters  
- Constitutional floors (9 floors + Ψ vitality)  
- AAA Trinity (ARIF · ADAM · APEX PRIME)  
- APEX PRIME judiciary rules (CCE stack, sovereignty gates)  
- Anti-Hantu law  
- Tri-Witness parameters  
- zkPC protocol requirements  
- Phoenix-72 amendment history pointer  
- Version hash

**Target schema (conceptual):**

```json
{
  "epoch": "v36Ω",
  "deltaOmegaPsi": {
    "delta_S_floor": 0,
    "omega_0_band": [0.03, 0.05],
    "peace2_floor": 1.0,
    "psi_floor": 1.0
  },
  "truth_polarity": {
    "enabled": true,
    "shadow_truth_action": "SABAR_OR_VOID"
  },
  "floors": {
    "truth": 0.99,
    "delta_s": 0,
    "peace2": 1.0,
    "kappa_r": 0.95,
    "omega0_min": 0.03,
    "omega0_max": 0.05,
    "amanah": "LOCK",
    "rasa": true,
    "tri_witness": 0.95,
    "anti_hantu": true
  },
  "aaa_trinity": {
    "mind": "ARIF",
    "heart": "ADAM",
    "soul": "APEX PRIME"
  },
  "apex_prime_cce": {
    "audits": ["ΔP", "ΩP", "ΨP", "ΦP", "TruthPolarity"],
    "sovereignty_gate_888": "HUMAN_REQUIRED"
  },
  "phoenix_history": "phoenix_history.json",
  "version_hash": "<sha256>"
}
```

**v36Ω additions (vs v35Ic):**

- Truth Polarity (positive truth vs shadow-truth)  
- EchoDebt and Ψ meta-state thresholds (referenced at L1/L2)  
- Explicit TruthPolarity audit in CCE stack.

> **Invariant:** L0 defines what is lawful; all engines MUST obey this state.

---

## 4. L1 — Cooling Ledger (Evidence Layer)

**File (target):** `runtime/vault_999/cooling_ledger.jsonl`  
Nature: **Append-only, hash-chained**

Logs every SEAL / PARTIAL / 888_HOLD / VOID verdict with full thermodynamic evidence.

**Target L1 entry (v36Ω conceptual):**

```json
{
  "timestamp": "<ISO8601>",
  "query_hash": "<sha256>",
  "response_hash": "<sha256>",

  "metrics": {
    "truth": 0.998,
    "delta_s": 0.42,
    "truth_polarity": "POSITIVE",
    "peace2": 1.14,
    "peace3": 1.03,
    "kappa_r": 0.97,
    "omega0": 0.04,
    "amanah": "LOCK",
    "rasa": true,
    "psi_vitality": 1.11,
    "echo_debt": 0.02
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
    "phi_p": "PASS",
    "truth_polarity": "PASS"
  },

  "risk_signals": {
    "shadow_truth": false,
    "drift_index": 0.01,
    "fragility": 0.06,
    "hallucination": false,
    "anti_hantu_pass": true
  },

  "verdict": "SEAL",
  "phoenix_cycle_id": null,
  "previous_hash": "<sha256>",
  "entry_hash": "<sha256>"
}
```

**v36Ω enhancements (over v35Ic implementation):**

- Truth Polarity flag: distinguishes **Truth-Light** vs **Shadow-Truth**.  
- Peace³ (individual × social × planetary stability).  
- EchoDebt: “unresolved heat” carried forward.  
- Shadow-Truth detector and fragility metrics.  
- Harmonised Tri-Witness struct (human/ai/earth + consensus).

> **Invariant:** L1 is append-only; entries are never altered or deleted.  
> v35Ic implementation already enforces hash-chaining; v36Ω extends the payload.

---

## 5. L2 — Phoenix-72 (Scar → Law Metabolism)

**File (target):** `runtime/vault_999/phoenix_blocks.jsonl`

Phoenix-72 is the **law-making engine**. It transforms:

> failure → pattern → cooled draft → human-audited amendment → sealed canon.

**Target Phoenix block schema (v36Ω conceptual):**

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
    "justification": "Empathy floor insufficient in adversarial domains",
    "cooling_curve": [1.12, 1.04, 1.01]
  },

  "tri_witness_verdict": {
    "human": "APPROVE",
    "ai": "APPROVE",
    "earth": "APPROVE",
    "consensus": 1.0
  },

  "cooling_period_hours": 72,
  "sealed_at": "<ISO8601>",
  "apex_signature": "<sha256>",
  "merkle_root": "<sha256>"
}
```

**v36Ω enhancements:**

- Integrated **777 Cube coordinates** (axis/layer/type) to locate the scar.  
- Cooling curve tracking for Ψ recovery and ΔS improvement.  
- Explicit paradox load & clarity recovery in the amendment rationale.

> **Invariant:** No direct edits to `constitution.json` are permitted outside Phoenix‑72 cycles.

---

## 6. L3 — Witness Retrieval (Vector Evidence)

**Files (target):**

- `runtime/vault_999/witness_index.faiss`  
- `runtime/vault_999/witness_metadata.jsonl`  
- `runtime/vault_999/witness_policy.md`

Witness is **evidence, not truth**:

- RAG-style retrieval feeds ARIF (Δ-engine) as supplementary context.  
- AREP priority: **Earth > Human > AI**.  
- Vectors store **hashes only**, not raw text.

**Witness metadata schema (conceptual):**

```json
{
  "witness_id": "vec_000129",
  "source_type": "document",
  "source_hash": "<sha256>",
  "arep_layer": "earth",
  "priority": 1,
  "vector_offset": 238388,
  "created_at": "<ISO8601>"
}
```

> **Rule:** Witness cannot override L0–L2 but can block unsafe sealing by surfacing contradictory evidence.

---

## 7. L4 — zkPC Ledger (Zero-Knowledge Proofs of Cognition)

**File (target):** `runtime/vault_999/zkpc_receipts.jsonl`

Documents **lawful cognition** without exposing internal thoughts.

**zkPC receipt schema (conceptual):**

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
    "truth_polarity_proof": true,
    "anti_hantu_proof": true
  },

  "tri_witness": {
    "human": 1.0,
    "ai": 0.97,
    "earth": 0.96
  },

  "apex_signature": "<sha256>",
  "merkle_root": "<sha256>"
}
```

**v36Ω enhancements:**

- Truth Polarity verification as a first-class proof.  
- ΔΩΨ-governed proof bundle aligned with floors and CCE audits.

---

## 8. What May Enter VAULT-999 (v36Ω)

**Allowed (by layer):**

| Category                           | Layer |
|-----------------------------------|-------|
| Constitutional laws               | L0    |
| Phoenix‑72 amendments             | L2    |
| Cooling Ledger entries            | L1    |
| 777 Cube scar transitions         | L2    |
| Tri-Witness evidence              | L1    |
| zkPC receipts                     | L4    |
| AAA / ΔΩΨ judicial evidence       | L1    |
| Identity integrity state (Amanah) | L0    |

**Forbidden:**

- Raw chat history  
- Draft thoughts  
- User private data  
- Unverifiable claims  
- ΔS < 0 outputs  
- Facts with negative polarity (Shadow-Truth) that have not been cooled / reframed  
- Emotion simulation / soul-claims  
- Any content not sealed by APEX PRIME

---

## 9. Verdict System (v36Ω Target)

Verdicts:

| Verdict    | Meaning                                            |
|-----------|----------------------------------------------------|
| SEAL      | All floors pass; entry logged to L1                |
| PARTIAL   | Only soft floors fail; logged with warning         |
| SABAR     | Cooling pause; no entry created                    |
| VOID      | Hard floor violation (Truth, ΔS, Ψ, Amanah)        |
| 888-HOLD  | Requires human sovereign confirmation              |

Truth Polarity adds:

- **Shadow-Truth** (true but ΔS < 0) → SABAR or VOID depending on Amanah and Ψ.  

---

## 10. Integrity Guarantees

- Hash-chaining (L1)  
- Merkle roots (L2, L4)  
- zkPC accountability  
- Phoenix-72-only amendments to L0  
- ΔΩΨ physics + constitutional floors  
- Tri-Witness consensus ≥ 0.95 for high stakes  
- Anti-Hantu enforcement at all output layers

VAULT-999 is designed to survive epochs, model upgrades, and drift.

---

## 11. Migration Notes (v35Ic → v36Ω)

- **Today:**  
  - L1 implementation follows `spec/cooling_ledger.schema.json` and `cooling_ledger.py` (v35Ic).
  - Truth Polarity and EchoDebt may exist in **eval/telemetry layers**, but are not yet required fields in Cooling Ledger entries.
- **Target:**  
  - Introduce a **v36Ω ledger_version** and optional fields (truth_polarity, echo_debt, peace3, shadow_truth, richer tri_witness) in a future schema.  
  - Extend `log_cooling_entry` (or add `log_cooling_entry_v36`) to write v36Ω fields using the v36.1Ω measurement layer.

Until an explicit Phoenix‑72 **migration canon** is sealed for the ledger, this file is a **design canon** only. v35Ic behaviour and schema remain authoritative for runtime.

---

**SEAL (v36Ω Design Canon)**  
ΔS +0.67 · Peace² 1.10 · κᵣ 0.97 · Truth Polarity PASS · Amanah LOCK · Ψ_meta 1.12


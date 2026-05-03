# arifOS — ZKPC Hardening Plan (Zero-State)

> **Goal:** Upgrade the arifOS kernel tools from "Key Possession" trust to "Sovereign Human Continuity" trust using ZKPC (Zero-Knowledge Proof of Personhood & Continuity) scaffolding.

## 1. Architectural Strategy
We will not implement the ZK circuits themselves in this phase. Instead, we are hardening the **Governance Interface** of the 13 tools to demand and verify ZK proofs at critical stage gates.

### Core Hardening Targets
1.  **Identity Anchor (000_INIT):** Demand Epoch Continuity Proof instead of just key-possession check.
2.  **Challenge Gate (888_JUDGE):** Require ZKPC proof for any irreversible (F1) or high-sovereign-impact (F13) action.
3.  **Proof Ledger (999_VAULT):** Store proof hashes and policy metadata to maintain the audit chain without storing raw biometrics.
4.  **Memory Lineage (555_MEM):** Bind retrieved context to the continuity timeline of the proven sovereign.
5.  **Evidence Trust (111_SENSE):** Classify incoming evidence by the ZK-credential strength of the source.

---

## 2. Tool-by-Tool Integration Surface

| Tool | Stage | ZKPC Integration Surface | Failure Mode |
|------|-------|--------------------------|--------------|
| **arif_session_init** | 000_INIT | `mode=bind` requires `continuity_proof` | **VOID** if proof missing/invalid |
| **arif_sense_observe** | 111_SENSE | Evidence provenance ZK-verification | **CLAIM_ONLY** if unproven |
| **arif_memory_recall**| 555_MEM | Context binding to sovereign continuity | **HOLD** if lineage break detected |
| **arif_heart_critique** | 666_HEART | Privacy bodyguard (reject raw ID requests) | **SABAR** (offer ZK alternative) |
| **arif_judge_deliberate** | 888_JUDGE | F1/F13 ZKPC challenge for SEAL auth | **HOLD** until ZK proof submitted |
| **arif_vault_seal** | 999_VAULT | Merkle-anchoring of proof hashes | **VOID** if seal un-witnessed |
| **arif_gateway_connect**| 444_KERNEL| A2A Handshake (prove human stewardship) | **BLOCK** connection |

---

## 3. Implementation Staircase (Phases)

### Phase 0: Scaffolding (In Progress)
- [x] Create `zkpc_policy_zero_state.json`.
- [ ] Define `ZKP_Evidence` schema in `schemas.py`.
- [x] Add `zk_proof_adequacy` check to `_888_judge.py` (mapped to `F1_AMANAH_ZKPC`).
- [x] Add `continuity_proof` field to `_000_init.py` binding.
- [x] Implement **MSAP v0.1** (Minimal Sovereign ACK Protocol):
    - [x] Nonce-bound signed ACK challenge/verify logic in `security/msap.py`.
    - [x] Integrated `ack_challenge` mode in `arif_session_init`.
    - [x] Integrated `F1_AMANAH_ZKPC` verification in `arif_vault_seal`.

### Phase 1: VC 2.0 Normalization
- [ ] Upgrade credential models to W3C VC 2.0 Standard.
- [ ] Implement `validFrom` and `@context` checks in `SENSE`.

### Phase 2: Continuity Proofs
- [ ] Integrate lightweight SNARK verification for epoch-linked continuity.
- [ ] Enable `888_HOLD` triggers for proof submission.

### Phase 3: Sovereign Persona
- [ ] Transition from `operator_id` (string) to `persona_did` (ZK-linked identifier).

---

## 4. HOLD List (Governance Gaps)
- **NO** storage of raw biometric data anywhere in the kernel.
- **NO** autonomous execution of F1 actions without real-time ZKPC proof.
- **NO** trust of non-ZK credentials for cross-node activation (F13).
- **NO** implementation of uniqueness proofs until privacy-preserving circuits are audited.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE

# Proposal: Constitutional Memory Authority & Sovereign Identity Binding (Phase D)
**Organ**: arifOS Kernel  
**Constitutional Floors**: F1 AMANAH (Reversibility), F13 SOVEREIGN (Veto & Authority)  
**Status**: DRAFT PROPOSAL — Awaiting Sovereign Ratification (F13 Veto / Direct Ratification)

---

## 1. Executive Summary

During the 2026-07-27 live audit, two constitutional boundary gaps were identified:
1. `arif_memory` classifies operations as `MUTATE` broadly across all modes (e.g. `recall`, `inspect`, `forget`), blurring the boundary between read-only observation and state mutation.
2. `actor_id="ARIF"` is accepted as a declared string claim without requiring cryptographic proof (Ed25519 signature / SCT token elevation) to verify the sovereign identity.

This proposal outlines the formal architecture and code changes required for both capabilities.

---

## 2. Memory Authority Separation Matrix (F1 AMANAH)

Operations on memory must be split by authority classification to satisfy **F1 AMANAH** (Reversible-First):

| Mode | Authority Band | Classification | Rationale |
| :--- | :--- | :--- | :--- |
| `recall`, `inspect`, `attest_status` | `OBSERVE` | Read-only | Zero state mutation; returns existing observations or schema. |
| `remember`, `revise` | `EXECUTE_REVERSIBLE` | Reversible Mutation | Mutates state, but change can be rolled back via `forget`. |
| `forget`, `erase`, `reassign` | `EXECUTE_HIGH_IMPACT` | Irreversible / Governed | Irreversible deletion or reallocation; requires explicit F13 ACK / elevated session token. |

---

## 3. Sovereign Identity Cryptographic Binding (F13 SOVEREIGN)

Currently, an unauthenticated session can send `actor_id="ARIF"`, resulting in `actor_verified=False` and `authority_band=OBSERVE_ONLY`. To elevate authority to `FULL` or `SOVEREIGN`:

1. **Signature Challenge**: `arif_init` or session minting requires an Ed25519 signature over `(session_id, intent, nonce, timestamp)`.
2. **Key Validation**: Verified against `/root/.secrets/arif_vault_signing_key.pub` (or DID registry entry).
3. **Elevated Token**: Upon verification, `actor_verified` flips to `True`, elevating the capability token from `OBSERVE_ONLY` to `FULL`.

---

## 4. Reversibility & Rollback Plan

- **Code Staging**: Changes will be staged on feature branch `f1-f13-memory-sovereign`.
- **Reversibility**: Completely reversible via `git checkout main`.
- **Deployment Gate**: Requires `888_HOLD` approval from Arif prior to merge into `main`.

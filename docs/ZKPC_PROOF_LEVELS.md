# ZKPC Proof Levels — Sovereign Taxonomy (Sealed 2026-06-20)

> **ZKPC = Zero-Knowledge Proof of Context**
>
> A proof layer that lets an organ prove it followed a lawful context transition
> without exposing the full private context.

## Proof Levels

| Level | Name | What It Proves | How | Current Status |
|-------|------|---------------|-----|----------------|
| **L0** | Heuristic Coherence | Context transition is plausible | String-length scoring, dimension heuristics | `context_coherence.py` (was `zkpc_verifier.py`) |
| **L1** | Hash Commitment | Event has not been tampered with | blake3 hash receipt | `ZKPCReceipt` / `generate_zkpc_receipt()` |
| **L2** | Signed KSR Transition | Transition came from authorized kernel state | Ed25519 signature over KSR snapshot | `vault999-writer` (Ed25519 verification) |
| **L3** | Merkle Inclusion Proof | Event is in the canonical Vault chain | Merkle proof over Vault append | `seal_law.py` (chain_hash verification) |
| **L4** | Zero-Knowledge Circuit | Transition was lawful without revealing KSR | Groth16 / PLONK / STARK / Circom circuit | `zkpc_v2_epoch.circom` (candidate) |
| **L5** | Federated Cross-Organ Proof | Multiple organs attest without sharing private state | Multi-party ZK / recursive proofs | Not yet implemented |

## Where Each Lives in the Architecture

```
KSR present state
  ↓
kernel transition
  ↓
ZKPC-L0  — heuristic coherence check (is this transition plausible?)
  ↓
ZKPC-L1  — hash commitment (tamper-evidence)
  ↓
ZKPC-L2  — signed transition (Ed25519 authority)
  ↓
ZKPC-L3  — Merkle inclusion (chain proof)
  ↓
Ledger append
  ↓
Vault stores sealed event + proof receipt
  ↓
Federation memory indexes proof-bearing past
```

## Current Implementation Honest Classification

| Artifact | Proof Level | Notes |
|----------|-------------|-------|
| `context_coherence.py` (was `zkpc_verifier.py`) | **L0** | 7-dimension heuristic scorer. No cryptography. |
| `ZKPCReceipt` / `generate_zkpc_receipt()` | **L1** | blake3 hash commitment. Tamper-evident, not ZK. |
| `requires_zkpc_proof()` | **L2** (partial) | Signature gate for C4/C5. Backed by lease inspection. |
| `vault999-writer` Ed25519 verification | **L2** | Full signature verification over canonical payload. |
| `seal_law.py` chain verification | **L3** | Merkle chain integrity. Not ZK, but inclusion-proof-grade. |
| `zkpc_v2_epoch.circom` | **L4** (candidate) | Poseidon hash ZK circuit. Real cryptographic ZK. |

## Doctrine Line

> ZKPC is the proof membrane between live KSR transition and sealed Vault history.
> It may begin as coherence attestation and hash commitment, but its sovereign
> destination is cryptographic proof of lawful context transition without disclosure
> of private kernel state.

> KSR is present. Vault is past. Ledger is arrow. ZKPC is proof that the arrow moved lawfully.

## What This Means

- **Do not rename ZKPC.** It is an architectural destination, not just an implementation label.
- **Do not claim cryptographic finality** until L4 circuit-backed proof exists.
- **Do claim proof levels honestly.** Current code is L0-L3. L4-L5 are sovereign destinations.

## Sovereign Authority

This taxonomy is F13 SOVEREIGN ruling (Arif bin Fazil, 2026-06-20).
It overrides the naming-debt audit recommendation to rename ZKPC artifacts.

---

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE

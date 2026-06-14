# ZKPC — Distinction Audit (2026-06-14)

> **SOVEREIGN RULING:** "ZKPC" refers to two different things in this codebase.
> This document cleanly separates them so no agent confuses the two.
> **DITEMPA BUKAN DIBERI**

---

## The Two ZKPCs

| | ZKPC-A (Current Codebase) | ZKPC-B (Vision Document) |
|---|---|---|
| **Full name** | Zero-Knowledge Proof of Context | Zero-Knowledge Proof of Constraint / Consensus |
| **What it is** | Heuristic context coherence scorer (7 dimensions, 0.0–1.0) | Cryptographic proof that action obeyed constraints without revealing internal state |
| **Crypto?** | No — hash chain (blake3) + policy gate only | Yes — requires zkML circuits (EZKL, Giza, circom) |
| **Threat model** | Single-VPS, trusted localhost | Decentralized network, untrusted provers |
| **Status** | **LIVE** (misnamed) | **SPEC** (not implemented) |
| **File** | `arifosmcp/runtime/zkpc_verifier.py` | `AAA/wiki/raw/repos/ZKPC.md` |

---

## Three Layers — What Actually Exists

### Layer 1 — Heuristic Verifier (LIVE, ZKPC-A)

```
File:   arifosmcp/runtime/zkpc_verifier.py (112 lines)
What:   7-dimension context coherence check. Scores 0.0–1.0.
        wound_architecture, paradox_tolerance, moral_architecture,
        language_register, sovereign_intent, godel_lock, anti_behavior_sink
Floors: F2 (TRUTH), F7 (HUMILITY)
Crypto: NONE — pure heuristic scoring
Reality: This is a context coherence verifier, NOT a ZK proof.
         The name "ZKPC" is aspirational branding.
```

### Layer 2 — Circom Circuit (QUARANTINED, ZKPC-B prototype)

```
File:   /root/zkpc/circuits/zkpc_v2_epoch.circom (39 lines)
What:   zkSNARK circuit — Poseidon hash, identity commitment,
        epoch continuity, signal binding (action binding)
Status: TOY_QUARANTINED — not in production
Why:    Requires trusted setup, proving key, verifying key.
        No integration path to arifOS kernel.
Reality: Real cryptography, but not wired to anything.
```

### Layer 3 — Vision Document (SPEC, ZKPC-B)

```
File:   AAA/wiki/raw/repos/ZKPC.md (173 lines)
What:   Full constitutional ZK proof spec. Prove action complies
        with F1-F13 without revealing witness.
Status: Approved concept, not yet implemented.
        References EZKL, Giza, Bittensor as potential backends.
```

---

## Naming Recommendation → EXECUTED (2026-06-14)

| Old Name | New Name | Status |
|---|---|---|
| `zkpc_verifier.py` | `context_coherence.py` | ✅ RENAMED |
| `verify_zkpc()` | `verify_context_coherence()` | ✅ RENAMED (backward-compat alias in tests) |
| `ZKPCReceipt` | `HashCommitmentReceipt` | ✅ RENAMED (alias kept for compat) |
| `generate_zkpc_receipt()` | `generate_hash_commitment_receipt()` | ✅ RENAMED (alias kept for compat) |
| `ZKPCv2Epoch.circom` | `ZKPCv2Epoch.circom` | ✅ KEPT — correctly named (real ZK circuit) |
| `ZKPC.md` | `ZKPC.md` | ✅ KEPT — accurately describes the vision |

**Backward compatibility:** Old names retained as aliases. No existing code breaks. New code should use canonical names.

---

## Practical Guidance

**For agents auditing the codebase:**
- When you see `zkpc_verifier.py` → heuristic, not crypto. It's a F2/F7 gate.
- When you see `zkpc_v2_epoch.circom` → real circom circuit, quarantined.
- When you see `ZKPC.md` → vision document, not implementation.

**For the long-term ZKPC-B track:**
- Layer 2 (circom) needs: trusted setup ceremony, proving/verifying key generation, arifOS kernel integration path
- Layer 3 (vision) needs: zkML backend selection (EZKL vs Giza vs custom), safety circuit encoding, latency budget
- Neither is on the critical path for current federation operations

**What matters today:**
- F13 (SOVEREIGN) is the real trust anchor — not ZK proofs
- ADR-001 (localhost is the password) is the real security model
- The HMAC lease system (Phase 2c) is the real secret gate
- ZKPC-B is for when arifOS federates beyond a single VPS

---

## Boundary

- This is a **naming distinction document** — no code changes, no renames.
- Ratification required before renaming any file or changing any doc.
- The heuristic verifier (`zkpc_verifier.py`) remains functional and valuable — it just has a misleading name.

**DITEMPA BUKAN DIBERI — Forged, Not Given.**

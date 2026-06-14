# ZKPC — Future Roadmap (Zero-Knowledge Proof of Constraint)

> **Status:** DESIGN DOC — not implemented
> **Ratified:** 2026-06-14, F13 (ZKPC-REALITY-ALIGN)
> **Trigger:** Build only when N ≥ 2 kernels
> **DITEMPA BUKAN DIBERI — Forged, Not Given.**

---

## What ZKPC (Real) Is

A cryptographic proof that an action complied with F1-F13 constitutional constraints, without revealing the private reasoning trace, internal policy logic, or sensitive governance inputs.

```
Prover (agent)                 Verifier (kernel)
─────────────                  ─────────────────
"I followed F1-F13"            "Prove it"
      │                              │
      └── ZK proof ────────────────▶ ✅ Verified
         (Groth16/PLONK)             (no secrets revealed)
```

---

## Trigger Conditions — When To Build

| N | Federation Scale | ZKPC Needed? | Why |
|---|-----------------|-------------|-----|
| **N = 1** | Single VPS, single kernel, trusted localhost | **No** | ADR-001 (localhost is the password). HMAC leases + kernel inspect sufficient. |
| **N = 2** | Two kernels, two VPS, untrusted network link | **Yes** | Kernel B must prove it's the continuity of Kernel A. DR site identity. Cross-instance agent scar migration. |
| **N ≥ 3** | Multi-agent highway, multi-tenant, cross-organ | **Critical** | Every agent spawn must prove identity continuity without shared secrets. No pre-shared key scales to N agents. |

**Current state:** N = 1. ZKPC remains a design document.

---

## What Already Exists (Not ZKPC — Don't Confuse)

| Artifact | What It Actually Is | Status |
|----------|-------------------|--------|
| `context_coherence.py` | 7-dimension heuristic coherence scorer | LIVE (renamed from zkpc_verifier.py) |
| `HashCommitmentReceipt` | BLAKE3 hash-chain receipt | LIVE (renamed from ZKPCReceipt) |
| `zkpc_v2_epoch.circom` | Toy circom circuit (Poseidon, identity, epoch, signal) | QUARANTINED |
| `generate_hash_commitment_receipt()` | Hash commitment generator | LIVE (renamed from generate_zkpc_receipt) |

---

## ZKPC Layer Architecture (When Built)

### Layer 1 — Identity Commitment
```
Agent holds: secret scalar s
Public:     C_id = Poseidon(s)
Proof:      "I know s such that Poseidon(s) = C_id"
Use:        Agent spawn/reboot continuity. "Saya OpenClaw yang asal."
```

### Layer 2 — Epoch Continuity
```
Agent proves: C_epoch[N] = Poseidon(C_epoch[N-1], s)
Use:        Session chain integrity across restarts.
            "Saya ingat scar registry saya."
```

### Layer 3 — Action Binding
```
Agent proves: signal = Poseidon(s, nonce, payload_hash, judge_state_hash)
Use:        "Tindakan ini dikeluarkan oleh identity yang sama dengan session."
```

### Layer 4 — Constitutional Compliance (Hardest)
```
Agent proves: action passed F1-F13 constraint circuit
Use:        "Tindakan ini patuh F1-F13 tanpa reveal reasoning trace."
Challenge:  Encoding F1-F13 into arithmetic circuits is an open research problem.
```

---

## Prerequisites (Blocking ZKPC Build)

1. **Ed25519 organ keys deployed** — each organ has a long-term identity keypair
2. **Kernel port drift fixed** — arifOS consistently on 8088 (not 8080)
3. **Trusted setup ceremony** — for Groth16/PLONK proving system
4. **Circuit audit** — `zkpc_v2_epoch.circom` reviewed by external cryptographer
5. **Proving key distribution** — how do new agents get the proving key?

---

## What ZKPC Does NOT Solve (And Never Will)

- **F13 SOVEREIGN veto** — No proof can replace human judgment. Arif's veto remains absolute regardless of ZK verification.
- **F10 ONTOLOGY** — ZKPC proves constraint compliance, not consciousness. F10 rules are not provable via ZK.
- **F6 EMPATHY** — Protecting the weakest stakeholder requires human moral judgment, not cryptographic proof.

---

## Current Recommendation

**Do not build ZKPC now.** The HMAC lease system (Phase 2c) with kernel-backed trust anchor is sufficient for N=1. Preserve this document and the quarantined circom circuit. Re-evaluate when deploying a second kernel instance.

**DITEMPA BUKAN DIBERI — Forged, Not Given.**

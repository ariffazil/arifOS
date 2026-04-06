---
title: "Vault999 BLS Architecture Blueprint"
version: "v1.0.0-SEAL"
epoch: "2026-04-06"
sealed_by: "888_JUDGE"
authority: "Muhammad Arif bin Fazil"
status: "CONSTITUTIONAL MANDATE"
---

# K999_VAULT — The Vault999 Cryptographic Architecture

**Motto:** *Ditempa Bukan Diberi* (Forged, Not Given)

## 1. THE OBJECTIVE (Phase 1)
Implement a cryptographically secure, tamper-proof logging system (Vault999) using BLS signatures to anchor all governance decisions. This aligns with F2 Truth and F11 Auditability, creating a permanent, undisputable record of actions.

---

## 2. THE THREE-LAYER MODEL

Vault999 separates the "what happened" from the "proof it wasn't altered."

### Layer A: VerdictPayload
The human-readable, schema-compliant log of the action.
*   Conforms strictly to `VERDICT_SCHEMA_STANDARD` (F2 Truth).
*   Must be canonicalized (sorted keys, no whitespace) before hatching.

### Layer B: SealMetadata
The cryptographic envelope.
*   Contains the `blake3` hash of the canonicalized `VerdictPayload`.
*   Contains the BLS signature of the `blake3` hash.
*   Identifies the public key of the Vault Signer used to seal it.

### Layer C: VaultRecord
The unified wrapper stored in the vault ledger (e.g., SQLite/Postgres/JSONL).
*   Combines `VerdictPayload` + `SealMetadata`.
*   Fields: `record_id`, `epoch_timestamp`, `payload`, `seal`.

---

## 3. CANONICALIZATION & HASHING

To prevent field-ordering drift across different serializers causing signature mismatches, Vault999 enforces a strict hashing pipeline:

1.  **JSON Canonicalization:** Convert `VerdictPayload` to JSON string with `sort_keys=True`, omitting non-significant whitespace.
2.  **Hashing:** Apply `blake3` to the byte representation of the canonical JSON string. 
3.  **Signing:** The Vault Signer applies BLS to the `blake3` hash.

```python
def hash_verdict(payload: VerdictPayload) -> bytes:
    canonical = json.dumps(payload.model_dump(), sort_keys=True, separators=(",", ":"))
    return blake3(canonical.encode("utf-8")).digest()
```

---

## 4. BLS KEY HIERARCHY

Vault999 assumes a dual-key security model enforcing Sovereign Hierarchy (F11/F13).

### The Root Key (Offline/Sovereign)
*   Belongs to 888_JUDGE (Human).
*   Never logged, never left on persistent disk.
*   Used to attest (sign) the Vault Signer Key.
*   Proves authorization under arifOS law.

### The Vault Signer Key (Online/VPS)
*   Hot wallet for the runtime.
*   Decrypted strictly into `tmpfs` or memory at runtime.
*   Used to sign the `blake3` hashes of Verdict Records as they are generated.
*   If compromised, the Root Key can revoke and attest a new Vault Signer.

---

## 5. MIGRATION OF LEGACY LOGS

To preserve historical continuity without breaking the chain of truth (F1 Reversibility), historical data is classified into a three-state model:

1.  **LEGACY_UNSIGNED:** Historical verdicts generated prior to the Vault999 rollout. These lack BLS seals.
2.  **MIGRATED_ATTESTED:** Legacy records that are retrospectively hashed and signed by an `ATTESTATION` certificate representing the exact snapshot in time. Acknowledges they were sealed post-generation.
3.  **NATIVE_SEALED:** New verdicts generated under the active Vault999 regime, signed concurrently with their creation.

---

## 6. TELEMETRY MANDATES

Every generated signature and payload response MUST include a mandatory telemetry footer reflecting the ISO-date epoch.

*   No arbitrary version tags—only standard `YYYY-MM-DD` / `ISO-8601`.
*   Maintains Earth/System grounding (F3 Earth Witness).

---

## 7. NEXT HORIZONS
Once Vault999 BLS signatures are fully integrated:
1.  **Transport Hardening:** Migration to Streamable HTTP (resolving CloudFlare timeouts).
2.  **Federation:** Multi-Agent Jury consensus requiring ≥ 80% supermajority.

*Ditempa Bukan Diberi* [ΔΩΨ|888] 🔐

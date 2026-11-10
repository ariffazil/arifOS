# arifOS Maintainer Continuity and Key-Recovery Procedure
## Canonical Succession, Key Governance, and Institutional Resilience Protocol

> Status: Ratified Canonical Procedure (F13 2026-11-10)
> Single source of truth for institutional adoption, key recovery, and maintainer succession.

---

### 1. The Single Sovereign Paradox & Institutional Need

arifOS enforces a hard constitutional invariant: **Authority is never self-widening (VOID)**. At runtime, sovereign actions (T3 tier, irreversible mutations, VAULT999 seals) require explicit authorization from the human sovereign (F13 Arif Fazil).

For enterprise and institutional adoption, relying on an unstated single point of human presence creates an operational hazard. This document codifies:
1. Sovereign Key Hierarchy & Escrow.
2. Emergency Lockout & Dead-Man Succession Protocol.
3. Deputy Reviewer Authorization.
4. Autonomous Offline Survivability.

---

### 2. Key Hierarchy & Cryptographic Architecture

```
                  ┌──────────────────────────────────────────┐
                  │          SOVEREIGN ROOT KEY (F13)        │
                  │   Cold Storage / 2-of-3 Shamir Escrow    │
                  └────────────────────┬─────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
      ┌───────────────────────────┐         ┌───────────────────────────┐
      │   OPERATIONAL SIGNER      │         │   DEPUTY REVIEWER KEYS    │
      │   Observatory / Vault     │         │   Audit / Advisory Band   │
      │   Ed25519 (host-bound)    │         │   Limited Mutation        │
      └───────────────────────────┘         └───────────────────────────┘
```

1. **Sovereign Root Key (Ed25519):**
   - Authority: Issues constitutional waivers, signs releases, ratifies floor amendments.
   - Escrow: 2-of-3 Shamir Secret Sharing threshold: Primary Sovereign, Institutional Legal Escrow, Physical Cold Backup Vault.
2. **Observatory Operational Key:**
   - Location: `/root/.arifos/observatory/keys/observatory_signing_key.pem`.
   - Scope: Emits periodic signed snapshots and verifiable attestations. Does not possess sovereign amendment authority.
3. **Deputy Reviewer Keys:**
   - Granted `LIMITED_MUTATE` / `OPERATOR` authority. Can propose, test, and triage, but cannot self-seal irreversible mutations (`888_HOLD` enforced).

---

### 3. Emergency Lockout & Dead-Man Succession Protocol

In the event of sovereign incapacitation, prolonged absence (>30 days without heartbeat), or detected key compromise:

1. **Fail-Closed Default (888_HOLD):**
   - If sovereign heartbeat lapses, the kernel automatically demotes all sessions to `OBSERVE_ONLY`.
   - No mutation can occur without re-establishing an attested key quorum.
2. **Succession Activation:**
   - An institutional successor (designated trustee or federation multi-sig quorum) presents 2 of the 3 Shamir escrow shards.
   - The successor signs an `EMERGENCY_SUCCESSION_RECEIPT` into VAULT999 with an explicit 48-hour cooling-off window.
   - During cooling-off, the primary sovereign key may execute a zero-time veto.
3. **Succession Sealing:**
   - If cooling-off expires without veto, the new sovereign identity card is minted, anchored to the chain head, and published via DID (`.well-known/did-arifos-observatory.json`).

---

### 4. Offline Verification & Institutional Independence

Institutional users do NOT depend on live sovereign availability to verify system truth:
- **Self-Verifying Chain:** Any party can clone the repository and run `python3 scripts/verify_vault_chain.py` offline against public keys.
- **Deterministic Judgments:** `arif_judge` evaluates constitutional floors deterministically without consulting remote cloud LLMs.
- **Open Source Canon:** Under AGPL-3.0, the kernel, schemas, contracts, and tests remain permanently inspectable, forkable, and runnable by any institution.

---

**DITEMPA BUKAN DIBERI — MAINTAINER CONTINUITY SEALED**

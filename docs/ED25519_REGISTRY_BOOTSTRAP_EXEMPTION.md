# Ed25519 Registry Bootstrap Exemption

> **Status:** ACCEPTED RESIDUAL RISK  
> **Ratified by audit:** IRR-DIP-AUDIT FINAL 2026-07-09 (Priority 3)  
> **Code:** `arifosmcp/runtime/session_auth.py` → `_ED25519_EXEMPT_SYSTEM_ACTORS`  
> **Registry file:** `/root/A-FORGE/data/agent_identities.json`

---

## What is exempt

| actor_id | Authority granted without Ed25519 | Role |
|----------|-----------------------------------|------|
| `arif` | `sovereign` | F13 SOVEREIGN — human principal |
| `a-forge` | `operator` | A-FORGE execution organ |

All other actors **must** present `identity_proof.type == "ed25519"` in the
agent identity registry to resolve above `anonymous`.

---

## Why this exists (bootstrap constraint)

Authority resolution reads `agent_identities.json` and upgrades trust only when
an Ed25519 proof is present. Root principals (`arif`, `a-forge`) must be able
to **operate and bootstrap** that registry before every identity is keyed.

Requiring Ed25519 for these two first creates a **circular dependency**:

1. Registry validation needs a trusted operator.
2. Trusted operator would need registry Ed25519 proof.
3. Proof registration needs a trusted operator.

The exemption breaks the cycle. It is **not** an oversight.

---

## What this is not

- Not a general “skip signatures” flag for agents.
- Not a substitute for F13 veto or session binding.
- Not a license for anonymous actors to claim `arif` / `a-forge` without other
  L11 session controls (localhost / env / session store still apply elsewhere).

---

## Future hardening (non-blocking)

1. Issue **scoped bootstrap credentials** (limited verbs, short TTL) separate
   from day-to-day actor ids.
2. Require Ed25519 for `arif` / `a-forge` **outside** the bootstrap path.
3. Rotate and seal bootstrap material in VAULT999 when introduced.

Until then: treat this table as the single named residual risk for registry
root trust.

---

*DITEMPA BUKAN DIBERI — documented 2026-07-09 from IRR-DIP-AUDIT Priority 3.*

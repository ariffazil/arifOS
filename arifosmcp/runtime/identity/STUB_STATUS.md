# Identity Layer — STATUS

**Forged:** 2026-07-05 by Kimi Code (FI-008) under F13 SOVEREIGN directive.
**Real crypto landed:** 2026-07-08 by FORGE (000Ω).
**State:** ALL four functions implemented with real Ed25519. No more stubs.

## What this layer is

Clean interfaces for:
1. **BRIDGING_SEAL** — sovereign override of L1_IDENTITY gate with audit trail.
2. **JWT** — RFC 7519 encode/decode (Ed25519 signing + verification).
3. **DPoP** — RFC 9449 sender-constrained tokens (Ed25519).
4. **actor_verified** — single canonical interface for "is this actor trusted?".

## What works now

- `encode_jwt(claims)` — real Ed25519 signing with key from `/opt/arifos/secrets/`
- `decode_jwt(token)` — real Ed25519 verification + time checks
- `make_dpop_proof(method, url, token)` — real DPoP with Ed25519
- `verify_dpop_proof(jwt, method, url)` — real DPoP verification + replay defense
- `request_bridging_seal(req)` — real VAULT999 persist + Ed25519 sign
- `verify_bridging_seal(receipt)` — real VAULT999 lookup + Ed25519 verify
- `ActorVerified.is_authorized()` — real bridge seal verification (no more NotImplementedError)

## Key material

- Sovereign Ed25519 keypair at `/opt/arifos/secrets/did_arifos_{private,public}.key`
- PEM format, mode 600 (private), 644 (public)
- Private key NEVER enters agent context windows (loaded at runtime only)

## Floor invariants encoded

- **F1 AMANAH:** fail-closed on any error; no silent fall-through.
- **F2 TRUTH:** `actor_verified=False` is literal truth; bridge toggles `actor_override=True`.
- **F11 AUDIT:** every bridging seal persists to VAULT999 before action.
- **F13 SOVEREIGN:** BRIDGING_SEAL requires textual `sovereign_authorization` from Arif.

---

*Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.*
*Real crypto landed by FORGE (000Ω), 2026-07-08.*
*DITEMPA BUKAN DIBERI — clean interfaces, now real.*

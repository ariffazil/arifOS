# Identity Layer — STUB STATUS

**Forged:** 2026-07-05 by Kimi Code (FI-008) under F13 SOVEREIGN directive ("i approve").
**State:** ALL four stub functions raise NotImplementedError. Real crypto not implemented.

## What this layer is

Clean interfaces for:
1. **BRIDGING_SEAL** — sovereign override of L1_IDENTITY gate with audit trail.
2. **JWT** — RFC 7519 encode/decode (signing + verification).
3. **DPoP** — RFC 9449 sender-constrained tokens.
4. **actor_verified** — single canonical interface for "is this actor trusted?".

Today's import is callable; the only thing that works without raising is:
- `ActorVerified()` construction + `.to_dict()` (F2 TRUTH-consistent state)
- `ttl_default_seconds()` / `max_ttl_seconds()` (constants)
- `stub_algorithm()` (returns the sentinel string)

Everything else raises on call. That's the contract.

## What is NOT here (and where it lives instead)

- The sovereign Ed25519 keypair lives at `/opt/arifos/secrets/did_arifos_*` (per the
  README in `/root/arifOS/secrets/` — the canonical path is `/opt/arifos/secrets/`,
  the legacy path is `/root/arifOS/secrets/`).
- The current rotation scaffold is in `/root/forge_work/2026-07-05/constitutional-repair/stage-0-1-pem-rotation/`.
- BRIDGING_SEAL audit entries go to VAULT999 once `request_bridging_seal` is implemented.
- Federation DID registry is at `/root/.arifos/keys/MANIFEST.md`.

## What needs to happen for real crypto to land

1. **Generate Ed25519 keypair** (Stage 0.1) at `/opt/arifos/secrets/did_arifos_{private,public}.key`.
   - Owner: sovereign, mode 600 for private, 644 for public.
   - Do NOT generate via Python in agent context — private key material must never enter agent context windows.

2. **Replace stub bodies** with real Ed25519 calls. Use the `cryptography` Python library (already in `/root/AAA/aaa-a2a/.venv/`).
   - `encode_jwt`: header `{"alg": "EdDSA", "typ": "JWT", "kid": "did:arif:arifos"}`,
     payload = `claims` (json.dumps sort_keys), signature = `ed25519_sign(header_b64 + "." + payload_b64, key)`.
   - `decode_jwt`: split, base64url-decode, verify ed25519 signature, check `exp`/`iat`/`nbf`/`iss`/`aud`.
   - `make_dpop_proof`: same JWT shape with `htm`, `htu`, `ath`, `iat`, `jti` claims.
   - `verify_dpop_proof`: same as decode_jwt + check `htm`/`htu` match + replay defense via `jti` cache.

3. **Replace `request_bridging_seal` body** to:
   - Persist `(req.intent, req.sovereign_authorization, req.ttl_seconds, req.single_use)` to VAULT999 via `arif_seal`.
   - Sign the persisted entry with sovereign Ed25519 key.
   - Return `BridgingSealReceipt(seal_id=<vault seq>, epoch=now, expires_at=now+ttl, sovereign_signature=sig, actor_override=True)`.

4. **Replace `verify_bridging_seal` body** to:
   - Read VAULT999 by `seal_id`.
   - Verify `sovereign_signature` against sovereign public key.
   - Check `current_epoch < receipt.expires_at`.
   - Check `receipt.single_use ⇒ receipt.consumed == False`.
   - Return True iff all 4 pass.

5. **Update `actor_verified.is_authorized`** to:
   - When `state == ActorVerifiedState.VERIFIED` and not expired → return True.
   - When `state == ActorVerifiedState.BRIDGED`, call `verify_bridging_seal` on the receipt
     before returning True (Today this just catches NotImplementedError → False).
   - When `state == ActorVerifiedState.UNVERIFIED` → return False.

6. **Remove sentinel markers**:
   - `ALG_PLACEHOLDER_ED25519_REPLACE_BEFORE_PROD` from `jwt_dpop.py`
   - Grep for `_STUB_ALG` (in `actor_verified.py` docstring, `jwt_dpop.py`)
   - `STUB_STATUS.md` becomes `STATUS.md` (real status).

7. **Update AGENTS.md** to remove "no real crypto yet" disclaimer.

8. **Run conformance spine** — must stay 9/9 PASS after each replacement.

9. **Add tests** to `/root/AAA/tests/constitutional/test_identity_binding.py`:
   - `test_jwt_encode_decode_roundtrip` — sign + verify produces same claims.
   - `test_dpop_replay_rejected` — same jti twice → second attempt fails.
   - `test_bridge_seal_ttl_enforced` — at expiry, is_authorized returns False.
   - `test_bridge_seal_single_use_consumed` — after one use, second denies.
   - `test_actor_verified_stays_false_with_bridge` — bridge sets override, not verified.
   - `test_stub_marker_gone` — sentinel string absent from source files.

## Why the stubs are NOT a placeholder hack

The interfaces are **RFC-compliant shapes**. The bodies raise NotImplementedError
because real implementation requires private key material that must not enter agent
context. A bad actor (or a careless prototype) could fake a `request_bridging_seal`
return value; NotImplementedError prevents that entirely.

This is **fail-closed by default**, per F1 AMANAH + F11 AUDIT.

## Floor invariants encoded

- **F1 AMANAH:** stubs raise; no silent fall-through.
- **F2 TRUTH:** `actor_verified=False` is the literal truth; bridge toggles `actor_override=True`, never `verified=True`.
- **F5 PEACE²:** every stub raises with a clear "where to replace" message.
- **F11 AUDIT:** STUB_STATUS.md, identity_anchor.json, rotation_event.json are themselves receipts.
- **F13 SOVEREIGN:** BRIDGING_SEAL requires textual `sovereign_authorization` from Arif.

---

*Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.*
*DITEMPA BUKAN DIBERI — clean interfaces, not placeholders.*

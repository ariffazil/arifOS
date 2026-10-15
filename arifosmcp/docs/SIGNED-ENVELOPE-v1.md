# SIGNED-ENVELOPE v1 — Ed25519 Agent-Call Envelope (GAP #1 slice)

> Status: **LIVE-CODE, FLAG-GATED** (`ARIF_ENVELOPE_SIGNED=1`). Default behavior of
> every wired path is unchanged when the flag is off.
> Canonical home: this file (the `/root/AAA/docs/` tree is filesystem-immutable;
> this repo holds the verifier, the authoritative implementation of the wire contract).
> Closes toward: GAP #1 "Verified actor" — acceptance test: *every irreversible
> action carries an Ed25519 signature verifiable by an independent verifier*
> (`arif-fazil.com/arifos/` gap g1; metric `arifos_gap_verified_actor`).

## 1. Wire format

A `signed_envelope` object travels INSIDE the tool-call `arguments` of an
agent→kernel call (MCP `tools/call`, or any JSON body that maps to arguments):

```json
{
  "v": 1,
  "alg": "ed25519",
  "actor_id": "aaa",
  "session_id": "task-abc-123",
  "timestamp": 1760486400,
  "nonce": "9f86d081884c7d659a2feaa0c55ad015",
  "payload_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "sig": "<base64, 64 raw bytes of Ed25519>"
}
```

Field rules:

| field | type | rule |
|---|---|---|
| `v` | int | MUST be `1` (verifier enforces equality) |
| `alg` | string | MUST be `"ed25519"` (verifier enforces equality) |
| `actor_id` | string | caller identity; its Ed25519 public key MUST be resolvable from the AAA key registries (§4) |
| `session_id` | string | governing session/task id (may be empty string) |
| `timestamp` | int | unix epoch seconds at signing; verifier window §5 |
| `nonce` | string | ≥16 bytes fresh randomness, hex; single-use per verifier §5 |
| `payload_hash` | string | SHA-256 hex of CANON(payload) §3 |
| `sig` | string | base64 Ed25519 over CANON of the five signed fields §2 |

`v` and `alg` are outside the signature but are equality-checked, so a mutated
value fails as MALFORMED, never silently reinterpreted.

## 2. Signature

```
signing_input = CANON({actor_id, session_id, timestamp, nonce, payload_hash})
sig           = Ed25519.sign(signing_input, private_key)
```

## 3. Canonical serialization (CANON) — cross-language contract

Both the JS signer (`/root/AAA/a2a-server/envelope_v1.js`) and the Python
verifier (`/root/arifOS/arifosmcp/runtime/signed_envelope.py`) implement CANON
identically:

- UTF-8 JSON, keys sorted recursively, no whitespace: separators `,` `:`.
- Strings emitted raw (no `\u` escaping) — Python `ensure_ascii=False`.
- Signed-field values are constrained to ASCII (`actor_id`, `session_id`,
  nonce, payload_hash are ids/hex; `timestamp` is an int).
- Payload values for hashing SHOULD be ints / strings / bools / null / arrays /
  objects. Floats are NOT byte-stable across JSON serializers and are forbidden
  in hashed payloads (v1 limitation; MCP tool args in practice comply).
- Hash: `sha256(CANON(payload))` full lowercase hex (64 chars).

## 4. Key distribution

Actor public keys are registered in AAA (existing infrastructure — no new
registry minted):

1. arifOS `crypto_auth.resolve_actor_public_key` — PEM dirs
   `/root/AAA/IDENTITY/keys/{actor}_public.pem`, A-FORGE identity dirs,
   `agent_identities.json`, DID registry (canonical kernel SOT).
2. AAA DID registry `/root/AAA/auth/did_registry.yaml` — `organ_id` match,
   `public_key_hex` (e.g. `did:arif:aaa`).
3. AAA raw hex keys `/root/AAA/auth/keys/{actor}_public.key` (32-byte hex).

Signers keep private keys at `/root/AAA/auth/keys/{actor}_private.key`
(32-byte seed, hex), 0600, gitignored. Private keys never leave the signing
host and are never committed.

Gateway default actor: `aaa` (the AAA control-plane DID — "signs ingress
capsules" per the DID registry). Override with `ARIF_ENVELOPE_ACTOR`.

## 5. Replay window

- `|now − timestamp| ≤ ARIF_ENVELOPE_WINDOW_SECONDS` (default 300).
- `nonce` is single-use per verifier for the window length: the verifier keeps
  an in-process `nonce → expiry` map (bounded, purged). A repeated nonce inside
  the window is rejected (`NONCE_REPLAY`); after expiry the nonce may repeat.
- v1 limitation: the nonce store is per-process. The kernel ingress runs
  single-process today; a multi-replica deployment must swap in a shared store
  (Redis `SETEX`) before enforcement-default-on. Documented, not hidden.

## 6. Failure codes (fail-closed)

`ENVELOPE_MISSING_FIELDS` · `MALFORMED_ENVELOPE` · `KEY_NOT_REGISTERED` ·
`SIGNATURE_INVALID` · `PAYLOAD_HASH_MISMATCH` · `TIMESTAMP_OUT_OF_WINDOW` ·
`NONCE_REPLAY`

Any of these on a PRESENT envelope → the call is rejected before the tool
executes. An ABSENT envelope is pass-through while the flag is in
verify-if-present mode; rejecting absent envelopes is the later
default-on rollout step, not this slice.

## 7. Flag

`ARIF_ENVELOPE_SIGNED=1`

| side | flag off | flag on |
|---|---|---|
| AAA a2a-server (signer) | outbound `tools/call` unchanged | `signed_envelope` attached to `dispatchToOrgan` args |
| arifOS ingress (verifier) | envelopes ignored | present envelope verified; invalid → HOLD/DENY before tool runs |

## 8. Files

- Spec: this file.
- Python sign+verify: `/root/arifOS/arifosmcp/runtime/signed_envelope.py`
  (CLI: `python -m arifosmcp.runtime.signed_envelope verify --stdin`).
- Kernel wiring: `on_call_tool` hook, `/root/arifOS/arifosmcp/runtime/ingress_middleware.py`.
- JS signer: `/root/AAA/a2a-server/envelope_v1.js`, wired in `server.js::dispatchToOrgan`.
- Tests: `/root/arifOS/arifosmcp/tests/test_signed_envelope.py`,
  `/root/AAA/a2a-server/tests/envelope_v1.test.js` (interop: node signs → python verifies).

## 9. What this slice does NOT do

- No service restart / no deploy / no Caddy change — flag stays off in running
  processes until an authorized restart window.
- Metric `arifos_gap_verified_actor` stays MEASURED_FAIL until signed calls are
  observed live in the kernel ingress and the observation contract
  (`/var/www/html/mcp/shared/controlling-claims.json`) gains a probe-backed
  entry (generator already supports `bool_pass` rules).
- No per-actor key enrollment workflow; existing AAA keys are used as-is.

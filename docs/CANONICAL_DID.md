# Canonical arifOS DID — `did:web:arifos.arif-fazil.com`

> **Phase:** 4.2 — silk-speed-jericho
> **Date:** 2026-07-25
> **Slice:** Truth-preserving /999 and Observatory repairs
> **Status:** ACTIVE — no key rotation in this slice
> **Companion module:** `arifosmcp/runtime/did_inventory.py`
> **Live dump:** `from arifosmcp.runtime.did_inventory import get_did_inventory`

DITEMPA BUKAN DIBERI — Forged, Not Given.

---

## 1. Purpose

This document is the single source of truth for the arifOS Decentralized
Identifier (DID) surface. It enumerates every DID the runtime knows about,
its provenance, its current status, and the surface that serves it. It is
the human-facing companion to the machine-readable
`arifosmcp.runtime.did_inventory` module and the live `/.well-known/did.json`
route.

When the runtime identity changes (e.g. a new key, a new alias, a new
organ joining), update **this file first**, then the inventory helper,
then any `alsoKnownAs` reference in the well-known route.

## 2. Canonical DID

```
did:web:arifos.arif-fazil.com
```

This is the **canonical** arifOS DID. It is served at runtime by
`GET /.well-known/did.json` on the arifOS kernel (`:8088`) and
documented in source at
`arifosmcp/runtime/rest_routes/rest_routes.py::well_known_did`.

The DID document includes:

| Field | Value | Source |
|---|---|---|
| `id` | `did:web:arifos.arif-fazil.com` | this file |
| `alsoKnownAs` | `["did:web:arif-fazil.com"]` | static `.well-known/did.json` |
| `verificationMethod` | populated when local ed25519 key is bootstrapped; **empty array otherwise** (honest) | `crypto_auth.get_public_key_hex()` |
| `authentication` | mirrors `verificationMethod` when populated | runtime |
| `assertionMethod` | mirrors `verificationMethod` when populated | runtime |
| `service[ObservatorySnapshot]` | `…/api/observatory/v1/snapshot` | runtime |
| `service[MCP]` | `…/mcp` | runtime |

**Honest-empty contract:** when the local ed25519 key is not yet
bootstrapped, the well-known route serves a valid W3C DID document with
`verificationMethod: []`. The doc is structurally correct but the
verification methods are empty. The runtime never fabricates a placeholder
key — F2 TRUTH forbids fake-green on identity.

## 3. Aliases

| Alias | Owner | Notes |
|---|---|---|
| `did:web:arif-fazil.com` | human-facing sovereign domain | parent of the canonical DID; served as a static document at `static/.well-known/did.json` |
| `did:arifos:arif` | custom `did:arifos` method | resolves via `did_resolver._resolve_did_arifos` to a JsonWebKey2020 entry pointing at `/root/AAA/IDENTITY/keys/arif_public.pem`; never auto-resolved at boot |

`did:key:` derivations are produced on demand by the inventory helper when
the local ed25519 key is bootstrapped. They are not pinned in the canonical
DID document.

## 4. Sovereign key registry (read-only)

The arifOS kernel maintains a sovereign key registry in
`arifosmcp/runtime/governance_identity.py`. The Phase 4.2 slice does **not**
rotate, add, or remove keys — it only labels the legacy
`/var/www/html/arif/999/key-rotation-2026-05-03.json` artifact as
historical and points new consumers at this registry.

| Key ID | Actor | Notes |
|---|---|---|
| `ed25519:sha256:a8fbb5ae8b4772b0` | Arif `/000/` DID key | `did:web:arif-fazil.com` |
| `ed25519:sha256:9c35a833fef25f17` | Arif AAA identity key (2026-07-12) | not the Observatory signing key |

F13 SOVEREIGN decisions bind to these keys, not to names. Names like
`arif` or `sovereign` are NLP shortcuts — they are NEVER the basis of a
trust decision.

## 5. Runtime verification surface

The runtime serves four identity-related endpoints. All are public,
read-only, and never mutate the seal chain or the key material.

| Endpoint | Owner | Purpose |
|---|---|---|
| `GET /.well-known/did.json` | arifOS :8088 | canonical DID document (see §2) |
| `GET /999/verify` | arifOS :8088 | live vault head + cross-verification contract (Phase 4.1) |
| `GET /api/observatory/v1/snapshot` | arifOS :8088 | signed Observatory snapshot — same ed25519 key as the DID |
| `GET https://aaa.arif-fazil.com/api/seal-chain/head` | AAA :3001 | independent cross-verification reading (Phase 4.1) |

The **canonical Observatory DID** (the one whose key material signs
`snapshot_latest.json`) is documented here and is the same ed25519 key
embedded in `did:web:arifos.arif-fazil.com#ed25519-key-1` when the
well-known route is in its bootstrapped state.

## 6. Historical artifacts (labelled, not deleted)

The following legacy static files in the live webroot are SUPERSEDED by
the canonical surfaces above. They are kept for backward compatibility
with older agents and audit replays, but they are no longer the
authoritative proof source. Each is loaded with an explicit
`HISTORICAL` log line in `arifosmcp/core/sovereign_bridge.py::load_verification_state`.

| File (live webroot) | Status | Canonical replacement |
|---|---|---|
| `/var/www/html/arif/999/did-status.json` | HISTORICAL | `/.well-known/did.json` + `arifosmcp.runtime.did_inventory` |
| `/var/www/html/arif/999/seal.json` | HISTORICAL | `/999/verify` (arifOS) + `/aaa/api/seal-chain/head` (AAA) |
| `/var/www/html/arif/999/runtime-snapshot.sha256` | HISTORICAL | `/api/observatory/v1/snapshot` (signed) |
| `/var/www/html/arif/999/key-rotation-2026-05-03.json` | HISTORICAL | `arifosmcp.runtime.governance_identity.SOVEREIGN_KEY_IDS` (no rotation in Phase 4.2) |

These files MUST NOT be deleted in this slice — they are part of the
audit trail. A future slice may move them under an explicit
`/var/www/html/arif/999/_historical/` subpath with a permanent
"RETIRED — see docs/CANONICAL_DID.md" banner; that move is a
deploy-time concern and is out of scope for the source-only Phase 4.2
slice.

## 7. Cross-verification contract (Phase 4.1)

The `/999/verify` response carries an explicit
`falsification.cross_verify_endpoint` field that names the AAA cockpit's
`/api/seal-chain/head` endpoint as the independent witness. The
`falsification.how_to_cross_verify` field instructs any external agent to
compare the two live readings, NOT a static HTML element on the /999
page. The dynamic proof block on the canonical `/999` source
(`static/index.html`) renders both readings side-by-side, with no baked-in
hash, and reports `MATCH` / `MISMATCH` / `PARTIAL` on every poll.

## 8. Inventory helper

```python
from arifosmcp.runtime.did_inventory import (
    CANONICAL_DID,
    CANONICAL_DID_ALIASES,
    SOVEREIGN_DID_PREFIX,
    build_did_inventory,
    get_did_inventory,
)

inv = get_did_inventory()
inv["canonical_did"]            # "did:web:arifos.arif-fazil.com"
inv["dids"]                     # list of {did, method, source, status, ...}
inv["sovereign_keys"]           # list of {key_id, kind, actor_hint, source}
inv["verification_status"]      # "bootstrapped" | "absent"
inv["runtime"]["deployment_mode"]
inv["runtime"]["kernel_started_at"]
```

The helper is **read-only** — it never writes to the seal chain, the
key material, or any file under `/root/.local/share/arifos/`. The
`force_refresh=True` flag is for tests and process restart only.

## 9. Test surface

| Concern | Test |
|---|---|
| Inventory shape | `tests/runtime/test_did_inventory.py::test_build_did_inventory_shape` |
| Canonical DID value | `tests/runtime/test_did_inventory.py::test_canonical_did_is_pinned` |
| No rotation assertion | `tests/runtime/test_did_inventory.py::test_no_key_rotation_in_slice` |
| Honest-empty on absent key | `tests/runtime/test_did_inventory.py::test_verification_status_honest_when_absent` |
| Live dump | `tests/runtime/test_did_inventory.py::test_get_did_inventory_caches` |

## 10. Boundaries

- **No key rotation** in this slice. `SOVEREIGN_KEY_IDS` and
  `VERIFIED_KEY_IDS` are read-only. The local ed25519 key is whatever
  `crypto_auth.get_public_key_hex()` returns at boot.
- **No seal fabrication.** Inventory and well-known routes are
  read-only against the live chain.
- **No commitment to the seal chain.** The inventory does not write
  receipts. It surfaces state, not history.
- **No regeneration of legacy `did-status.json` / `seal.json`.** Those
  legacy files are explicitly labelled HISTORICAL and are not the
  authority.

## 11. See also

- `arifosmcp/runtime/did_inventory.py` — machine-readable inventory
- `arifosmcp/runtime/did_resolver.py` — `did:key` and `did:arifos` resolver
- `arifosmcp/runtime/governance_identity.py` — sovereign key registry
- `arifosmcp/runtime/rest_routes/vault_verify.py` — `/999/verify` and falsification contract
- `arifosmcp/core/sovereign_bridge.py` — `/999` verification state loader (HISTORICAL labels)
- `static/.well-known/did.json` — human-facing sovereign DID document
- `static/index.html` — canonical `/999` Observatory page with dynamic proof block
- `identity.toml` — canonical arifOS identity (canonical_name, caddy_domain, etc.)

---

DITEMPA BUKAN DIBERI — Forged, Not Given.

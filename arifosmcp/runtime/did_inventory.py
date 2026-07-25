"""
arifosmcp/runtime/did_inventory.py — Canonical DID inventory for arifOS.

Phase 4.2 (silk-speed-jericho, 2026-07-25): enumerated list of every DID
the arifOS runtime knows about, grouped by source, with provenance and
reachability. This is the README-of-record for the runtime identity
surface — the on-disk companion to the human-facing canonical DID
documentation at ``docs/CANONICAL_DID.md``.

NO KEY ROTATION in this slice. This module is a READ-ONLY inventory; it
never touches the live key material, the seal chain, or any file under
``/root/.local/share/arifos/``. It only reads:

    * ``arifosmcp.runtime.governance_identity`` (P0 sovereign key set)
    * ``arifosmcp.runtime.crypto_auth`` (optional ed25519 public key)
    * the static ``identity.toml`` at the repo root

and returns a structured inventory suitable for diagnostic dumps,
exposure to ``/.well-known/did.json``, and pre-deploy checks.

Usage::

    from arifosmcp.runtime.did_inventory import build_did_inventory
    inv = build_did_inventory()
    # inv["canonical_did"] -> "did:web:arifos.arif-fazil.com"
    # inv["dids"]          -> list of {did, source, status, ...}
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ── Canonical DIDs known to arifOS at this slice ──────────────────────────
# No key rotation. This list is the source-of-truth for the public-facing
# `/.well-known/did.json` route in rest_routes.py and is what the canonical
# DID documentation in `docs/CANONICAL_DID.md` describes.
CANONICAL_DID = "did:web:arifos.arif-fazil.com"
CANONICAL_DID_ALIASES: tuple[str, ...] = ("did:web:arif-fazil.com",)
SOVEREIGN_DID_PREFIX = "did:arifos:"


def _safe_crypto_auth_pubkey() -> str | None:
    """Return the hex-encoded ed25519 public key from crypto_auth, if any.

    Best-effort. Returns None if the key is not bootstrapped or the import
    fails — never raises. The well-known/did.json route also tolerates a
    None return and serves a valid DID doc with empty verificationMethod.
    """
    try:
        from arifosmcp.runtime.crypto_auth import get_public_key_hex

        pk = get_public_key_hex()
        return pk if pk else None
    except Exception as exc:  # noqa: BLE001
        logger.debug("crypto_auth.get_public_key_hex unavailable: %s", exc)
        return None


def _safe_governance_identity_keys() -> list[dict[str, str]]:
    """Return the SOVEREIGN_KEY_IDS / VERIFIED_KEY_IDS entries as a list.

    These are the source-of-truth identifiers that bind a sovereign actor
    to a verification method. They live in arifosmcp.runtime.governance_identity
    and are referenced by F13 SOVEREIGN. We never touch them — just read.
    """
    out: list[dict[str, str]] = []
    try:
        from arifosmcp.runtime.governance_identity import (
            SOVEREIGN_KEY_IDS,
            VERIFIED_KEY_IDS,
        )

        for k in sorted(SOVEREIGN_KEY_IDS):
            out.append(
                {
                    "key_id": k,
                    "kind": "sovereign",
                    "actor_hint": "arif",
                    "source": "arifosmcp.runtime.governance_identity.SOVEREIGN_KEY_IDS",
                }
            )
        for k, v in sorted(VERIFIED_KEY_IDS.items()):
            if k == v:
                continue  # Mirror entries (k == v) carry no new info
            out.append(
                {
                    "key_id": k,
                    "kind": "verified",
                    "actor_hint": v,
                    "source": "arifosmcp.runtime.governance_identity.VERIFIED_KEY_IDS",
                }
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("governance_identity import failed: %s", exc)
    return out


def _safe_static_identity() -> dict[str, str]:
    """Return a few fields from /root/arifOS/identity.toml.

    Best-effort. Returns {} on any I/O error. Used to surface the
    canonical_name + caddy_domain without a full toml parser dependency.
    """
    out: dict[str, str] = {}
    p = Path("/root/arifOS/identity.toml")
    if not p.exists():
        return out
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, _, v = s.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in {"canonical_name", "caddy_domain", "service_id", "version"}:
                out[k] = v
    except Exception as exc:  # noqa: BLE001
        logger.debug("identity.toml read failed: %s", exc)
    return out


def _status_for_crypto_key() -> str:
    """Return the verification status of the live ed25519 public key.

    Possible values:
        "bootstrapped"  — get_public_key_hex() returns a non-empty key
        "absent"        — key not yet bootstrapped; well-known serves an
                          empty verificationMethod (honest about state)
    """
    return "bootstrapped" if _safe_crypto_auth_pubkey() else "absent"


def build_did_inventory() -> dict[str, Any]:
    """Return the structured DID inventory for the current runtime.

    Shape::

        {
            "canonical_did": "did:web:arifos.arif-fazil.com",
            "canonical_did_aliases": ["did:web:arif-fazil.com"],
            "generated_at": "2026-07-25T...",
            "schema_version": "did-inventory.v1",
            "runtime": {
                "deployment_mode": "...",         # from observatory routes
                "kernel_started_at": "...",
                "arifos_release": "...",
            },
            "static_identity": {"canonical_name": "...", ...},
            "dids": [
                {
                    "did": "did:web:arifos.arif-fazil.com",
                    "method": "web",
                    "source": "well-known/did.json route in rest_routes.py",
                    "status": "live",
                    "notes": "..."
                },
                ...
            ],
            "sovereign_keys": [
                {"key_id": "ed25519:sha256:...", "kind": "sovereign", ...},
                ...
            ],
            "verification_status": "bootstrapped" | "absent",
            "documentation": "docs/CANONICAL_DID.md",
            "phase": "4.2-silk-speed-jericho-2026-07-25",
        }
    """
    from datetime import UTC, datetime

    static_identity = _safe_static_identity()
    crypto_status = _status_for_crypto_key()
    gov_keys = _safe_governance_identity_keys()
    pk = _safe_crypto_auth_pubkey()

    # ── DIDs the runtime knows about ──────────────────────────────────
    dids: list[dict[str, Any]] = [
        {
            "did": CANONICAL_DID,
            "method": "web",
            "source": (
                "arifosmcp/runtime/rest_routes/rest_routes.py::well_known_did "
                "GET /.well-known/did.json"
            ),
            "status": "live" if crypto_status == "bootstrapped" else "live-empty-keys",
            "also_known_as": list(CANONICAL_DID_ALIASES),
            "service_endpoints": [
                "/api/observatory/v1/snapshot",
                "/mcp",
            ],
            "notes": (
                "Canonical arifOS DID. The well-known route serves a valid "
                "W3C DID document; when the local ed25519 key is bootstrapped, "
                "the verificationMethod array is populated and the key is "
                "added to authentication + assertionMethod. When not yet "
                "bootstrapped, the doc is served with empty verificationMethod "
                "(honest about key state — never fakes a green badge)."
            ),
        },
        {
            "did": "did:web:arif-fazil.com",
            "method": "web",
            "source": (
                "static/.well-known/did.json (human-facing sovereign DID, "
                "parent of did:web:arifos.arif-fazil.com)"
            ),
            "status": "static-document",
            "service_endpoints": [
                "https://arif-fazil.com/proof/geologist-credential.json.sig",
                "https://arif-fazil.com/999",
            ],
            "notes": (
                "Static DID document published under the human-facing domain. "
                "Listed as alsoKnownAs by the arifOS canonical DID. NOT "
                "resolved at runtime by arifOS; consumers read it directly "
                "from the static .well-known path."
            ),
        },
        {
            "did": f"{SOVEREIGN_DID_PREFIX}arif",
            "method": "arifos",
            "source": "arifosmcp.runtime.did_resolver._resolve_did_arifos",
            "status": "resolver-only",
            "notes": (
                "Custom did:arifos method. The resolver looks up "
                "/root/AAA/IDENTITY/keys/arif_public.pem and embeds it in a "
                "JsonWebKey2020 verificationMethod. NEVER auto-resolved at "
                "boot — only when an agent explicitly calls resolve_did()."
            ),
        },
    ]

    if pk:
        dids.append(
            {
                "did": f"did:key:z{pk[:32]}…",
                "method": "key",
                "source": "arifosmcp.runtime.crypto_auth.get_public_key_hex",
                "status": "derived",
                "key_fingerprint_sha256": pk,
                "notes": (
                    "Ed25519 public key rendered as a did:key. Derived at "
                    "inventory time from the same key material that signs "
                    "Observatory snapshots. Stable as long as the local key "
                    "is not rotated (Phase 4.2: no rotation)."
                ),
            }
        )

    # ── Runtime envelope ─────────────────────────────────────────────
    runtime: dict[str, str] = {
        "deployment_mode": "unknown",
        "kernel_started_at": "unknown",
        "arifos_release": os.getenv("ARIFOS_RELEASE_NAME", "unknown"),
    }
    try:
        from arifosmcp.runtime.rest_routes.observatory_routes import (
            _detect_deployment_mode,
            _kernel_started_at_iso,
        )

        runtime["deployment_mode"] = str(_detect_deployment_mode())
        runtime["kernel_started_at"] = str(_kernel_started_at_iso())
    except Exception as exc:  # noqa: BLE001
        logger.debug("observatory_routes import failed: %s", exc)

    return {
        "canonical_did": CANONICAL_DID,
        "canonical_did_aliases": list(CANONICAL_DID_ALIASES),
        "schema_version": "did-inventory.v1",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "phase": "4.2-silk-speed-jericho-2026-07-25",
        "runtime": runtime,
        "static_identity": static_identity,
        "dids": dids,
        "sovereign_keys": gov_keys,
        "verification_status": crypto_status,
        "documentation": "docs/CANONICAL_DID.md",
        "no_key_rotation_in_this_slice": True,
    }


# ── Module-level singleton (read-once) ──────────────────────────────────
_INVENTORY_CACHE: dict[str, Any] | None = None


def get_did_inventory(*, force_refresh: bool = False) -> dict[str, Any]:
    """Return the cached DID inventory, building it on first call.

    The inventory is small and depends only on filesystem + module
    imports. We cache the result so repeated callers (e.g. the well-known
    route plus a CLI dump) don't pay the build cost twice per process.

    Pass ``force_refresh=True`` after any process restart or to bypass
    the cache in tests.
    """
    global _INVENTORY_CACHE
    if _INVENTORY_CACHE is None or force_refresh:
        _INVENTORY_CACHE = build_did_inventory()
    return _INVENTORY_CACHE

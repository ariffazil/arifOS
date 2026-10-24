"""
arifosmcp/runtime/sovereign_verify.py — Ed25519 Sovereign Identity Verification

L11 AUTH: Cryptographic proof of sovereign actor identity.
Delegates signature verification to crypto_auth.verify_init_identity,
which tries multiple payload formats with alias normalization.

Public key path: env ARIFOS_SOVEREIGN_PUBKEY_FILE → /run/sekrits/arifos_sovereign.pub
Payload formats (tried by verify_init_identity):
  1. "{actor_id}:{nonce}"                        — canonical
  2. "{actor_id}:{constitution_hash}:{nonce}"    — kernel compat
Signature: base64-encoded Ed25519 signature over UTF-8 payload bytes

Authority levels:
  SOVEREIGN — Ed25519 signature verified (via verify_init_identity)
  OBSERVER  — No signature provided (read-only access)
  VOID      — Signature provided but verification failed (reject session)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import time
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

# T3a Finding B: one sovereign keypair. Prefer compose sekrits / AAA (same fp).
# did_arifos_public.key is LEGACY FRAGMENT (different key) — last resort only.
_PUBKEY_CANDIDATES = [
    Path(os.environ.get("ARIFOS_SOVEREIGN_PUBKEY_FILE", ""))
    if os.environ.get("ARIFOS_SOVEREIGN_PUBKEY_FILE")
    else None,
    Path("/run/sekrits/arifos_sovereign.pub"),
    Path("/run/secrets/arifos_sovereign.pub"),
    Path("/root/compose/sekrits/arifos_sovereign.pub"),  # canonical
    Path("/root/AAA/IDENTITY/keys/arif_public.pem"),  # same fingerprint as compose
    Path("/opt/arifos/secrets/did_arifos_public.key"),  # legacy fragment — do not prefer
    Path("/root/.ssh/operator_did_ed25519.pub"),
]

# Authority level constants
AUTHORITY_SOVEREIGN = "SOVEREIGN"
AUTHORITY_VERIFIED = "VERIFIED"
AUTHORITY_OBSERVER = "OBSERVER"
AUTHORITY_VOID = "VOID"
AUTHORITY_HMAC = "HMAC_VERIFIED"


# HMAC-rootkey verification (for Telegram-native identity)
def verify_hmac_signature(
    actor_id: str,
    challenge: str,
    sig: str,
) -> tuple[bool, str]:
    """
    L11 AUTH via HMAC-rootkey (Telegram-native path).

    Args:
        actor_id: Must be "ariffazil"
        challenge: "timestamp:op_id" format (same as nonce)
        sig: HMAC-SHA256(rootkey, challenge) hex digest

    Returns:
        (verified: bool, reason: str)
    """
    import os

    if actor_id != "ariffazil":
        return False, "hmac_actor_id_mismatch"

    # Canonical vault name is ARIFOS_ROOTKEY; ARIF_ROOTKEY is legacy alias only.
    rootkey = os.getenv("ARIFOS_ROOTKEY", "") or os.getenv("ARIF_ROOTKEY", "")
    if not rootkey:
        return False, "hmac_rootkey_not_configured"

    if not is_challenge_fresh(challenge):
        return False, "hmac_challenge_stale"

    import logging

    logger = logging.getLogger("arifosmcp.sovereign")
    expected = hmac.new(
        rootkey.encode(),
        challenge.encode(),
        hashlib.sha256,
    ).hexdigest()

    logger.warning(
        "DEBUG-HMAC: actor=%s challenge=%s sig=%s expected=%s",
        actor_id,
        challenge[:30],
        sig[:16] if sig else "None",
        expected[:16],
    )
    if hmac.compare_digest(expected, sig):
        return True, "hmac_signature_verified"
    return False, "hmac_signature_invalid"


def is_challenge_fresh(challenge: str, window_sec: int = 300) -> bool:
    """
    Reject replayed challenges older than window_sec.
    Default 300s (5 min) for HMAC path.

    For timestamped challenges (format: `{timestamp}:{random}`), checks age.
    For plain random tokens (crypto_auth style), returns True — freshness
    is enforced by the crypto_auth challenge store (issue_actor_challenge).
    """
    try:
        ts = int(challenge.split(":")[0])
        return abs(time.time() - ts) <= window_sec
    except (ValueError, IndexError):
        # Plain random token — freshness managed by crypto_auth._issued_challenges
        return True


@lru_cache(maxsize=1)
def _load_public_key():
    """Load and cache the Ed25519 public key. Returns None if not available."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        pubkey_path = next((path for path in _PUBKEY_CANDIDATES if path and path.exists()), None)
        if pubkey_path is None:
            logger.warning(
                "Sovereign public key not found in any candidate path: %s",
                ", ".join(str(path) for path in _PUBKEY_CANDIDATES if path),
            )
            return None

        pem_bytes = pubkey_path.read_bytes()
        pubkey = load_pem_public_key(pem_bytes)
        if not isinstance(pubkey, Ed25519PublicKey):
            logger.error("Sovereign key is not Ed25519 (got %s)", type(pubkey).__name__)
            return None
        logger.info("Sovereign public key loaded from %s", pubkey_path)
        return pubkey
    except FileNotFoundError:
        logger.warning(
            "Sovereign public key not found at %s — identity verification disabled",
            pubkey_path,
        )
        return None
    except Exception as exc:
        logger.error("Failed to load sovereign public key: %s", exc)
        return None


def compute_verified_key_id(
    actor_id: str,
    nonce: str,
    actor_signature: str,
    constitution_hash: str | None = None,
) -> str | None:
    """P0 FIX 2026-09-04 (FI-008, F13 "auto go"): canonical key fingerprint
    for a signature that has ALREADY passed Ed25519 verification.

    Derives ``ed25519:sha256:<hex16>`` from the SAME public key the verifier
    resolves (``crypto_auth.resolve_actor_public_key`` — no drift), and only
    returns a fingerprint when this function can itself re-verify the
    signature over the canonical payload formats. Fail-closed: any failure
    returns None, which yields a non-sovereign bind rather than a false one.

    This closes the LIMITED_MUTATE bug: init set identity_verified=True but
    never derived verified_key_id, so bind_authority_state could never match
    SOVEREIGN_KEY_IDS (SECURITY P0 2026-07-12) and the sovereign landed on
    OPERATOR/OBSERVER_MUTATE.
    """
    if not actor_id or not nonce or not actor_signature:
        return None
    try:
        from arifosmcp.runtime.crypto_auth import (
            _canonical_payloads,
            resolve_actor_public_key,
        )

        pubkey = resolve_actor_public_key(actor_id)
        if pubkey is None:
            return None
        try:
            sig_bytes = base64.b64decode(actor_signature)
        except Exception:
            return None
        # Shared payload source with verify_init_identity — sovereign alias
        # variants included, so a signature over "ariffazil:<nonce>" derives
        # its key id even when the caller passes "ARIF"/"arif".
        payloads = _canonical_payloads(actor_id, nonce, constitution_hash)
        for _label, msg in payloads:
            try:
                pubkey.verify(sig_bytes, msg)
                raw = pubkey.public_bytes_raw()
                return f"ed25519:sha256:{hashlib.sha256(raw).hexdigest()[:16]}"
            except Exception:
                continue
        return None
    except Exception as exc:
        logger.warning("compute_verified_key_id failed: %s", exc)
        return None


def verify_sovereign_signature(
    actor_id: str,
    constitution_hash: str,
    nonce: str,
    actor_signature: str,
    *,
    public_key_pem: str | None = None,
) -> tuple[bool, str]:
    """
    Verify Ed25519 signature — delegates to crypto_auth.verify_init_identity.

    verify_init_identity tries multiple payload formats:
      1. "{actor_id}:{nonce}"                        — canonical
      2. "{actor_id}:{constitution_hash}:{nonce}"    — kernel compat
    with actor-alias normalization and challenge replay protection.

    If public_key_pem is provided, it is loaded and passed to verify_init_identity
    as the canonical public key, bypassing actor registry resolution. This ensures
    the verifier uses the same key that the signer used (B1 key unification).

    Returns:
        (verified: bool, reason: str)
    """
    from arifosmcp.runtime.crypto_auth import verify_init_identity
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives.serialization import load_pem_public_key

    pubkey: Ed25519PublicKey | None = None
    if public_key_pem:
        try:
            key = load_pem_public_key(public_key_pem.encode())
            if isinstance(key, Ed25519PublicKey):
                pubkey = key
        except Exception as e:
            logger.warning("Failed to load provided public_key_pem: %s", e)

    return verify_init_identity(
        actor_id=actor_id,
        nonce=nonce,
        signature_b64=actor_signature,
        constitution_hash=constitution_hash or None,
        public_key=pubkey,
    )


def resolve_authority_level(
    actor_id: str | None,
    identity_verified: bool,
    signature_provided: bool,
) -> str:
    """
    Resolve authority level based on verification result.

    SOVEREIGN — Ed25519 verified sovereign actor
    VERIFIED  — Ed25519 verified bounded non-sovereign actor
    OBSERVER  — No signature (anonymous read-only access)
    VOID      — Signature provided but failed (reject)
    """
    if identity_verified:
        from arifosmcp.runtime.governance_identity import is_protected_sovereign_id

        if is_protected_sovereign_id(actor_id):
            return AUTHORITY_SOVEREIGN
        return AUTHORITY_VERIFIED
    if signature_provided and not identity_verified:
        return AUTHORITY_VOID
    return AUTHORITY_OBSERVER


def purge_expired_nonces(nonce_store: dict[str, float], ttl_seconds: int = 300) -> int:
    """Remove expired nonces from the store. Returns count of purged entries."""
    cutoff = time.time() - ttl_seconds
    expired = [k for k, ts in list(nonce_store.items()) if ts < cutoff]
    for k in expired:
        del nonce_store[k]
    return len(expired)


def pubkey_status() -> dict:
    """Return public key availability status for health checks."""
    pubkey = _load_public_key()
    pubkey_path = next((path for path in _PUBKEY_CANDIDATES if path and path.exists()), None)
    return {
        "sovereign_pubkey_loaded": pubkey is not None,
        "sovereign_pubkey_path": str(pubkey_path) if pubkey_path else None,
        "sovereign_pubkey_exists": pubkey_path is not None,
        "ed25519_verification": "enabled" if pubkey is not None else "disabled",
    }


# ─── agent-card verification (Phase 1 · 2026-10-24 · kimi-code/FI-008) ─────────
# Implements the function that sign-agent-card.sh:114 points at — previously a
# dead pointer (verify_card did not exist anywhere in the federation).
#
# Signature format produced by sign-agent-card.sh (air-gapped Ed25519 signer):
#   card["signatures"] += {
#     "type": "Ed25519Signature2020",
#     "proofValue": b64(Ed25519.sign(canonical)),
#     "verificationMethod": "ed25519:sha256:" + sha256(DER_SPKI_pub).hexdigest(),
#     "created": timestamp,
#   }
#   where canonical = json.dumps(card_without_this_entry, sort_keys=True,
#                                separators=(",", ":")).encode("utf-8")
# (the signer canonicalises BEFORE appending the new entry).
#
# Fails CLOSED on: unreadable card, missing/empty/invalid public key, unknown
# signature type, kid mismatch (corrupt or foreign verificationMethod),
# undecodable or invalid proofValue. Legacy JWS `signature_legacy` entries are
# NOT verifiable (corrupt kid template 'arifos-a2a-card-2026-%q', body modified
# after signing) — they are reported as unattributable, never as passes.

def verify_card(
    card_path: str,
    public_key_pem: str | bytes | None = None,
    key_pem_path: str | None = None,
) -> dict:
    """Verify an agent-card.json signature. Returns a verdict dict; never raises
    on bad input (fail closed inside the dict)."""
    import json as _json

    result: dict = {
        "valid": False,
        "status": "FAILED",
        "checked": 0,
        "verified": 0,
        "results": [],
        "reason": None,
    }

    try:
        card = _json.loads(Path(card_path).read_text(encoding="utf-8"))
        if not isinstance(card, dict):
            raise ValueError("card is not a JSON object")
    except Exception as exc:  # noqa: BLE001 — fail closed, report reason
        result["reason"] = f"card_unreadable: {exc}"
        return result

    pem = public_key_pem
    if not pem and key_pem_path:
        try:
            pem = Path(key_pem_path).read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            result["reason"] = f"pubkey_unreadable: {exc}"
            return result
    if not pem or not str(pem).strip():
        result["reason"] = "empty_public_key — fail closed"
        return result

    try:
        from cryptography.hazmat.primitives import serialization

        pub = serialization.load_pem_public_key(
            pem.encode("utf-8") if isinstance(pem, str) else pem
        )
        der = pub.public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    except Exception as exc:  # noqa: BLE001
        result["reason"] = f"pubkey_invalid — fail closed: {exc}"
        return result

    fingerprint = hashlib.sha256(der).hexdigest()
    expected_vm = f"ed25519:sha256:{fingerprint}"

    signatures = card.get("signatures")
    if not isinstance(signatures, list) or not signatures:
        legacy = card.get("signature_legacy")
        note = (
            "legacy JWS entries present but unattributable (corrupt kid / body"
            " modified after signing) — see card['signature_legacy']"
            if legacy
            else "no signature entry in card['signatures']"
        )
        result["reason"] = f"no_verifiable_signature: {note}"
        return result

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except Exception as exc:  # noqa: BLE001
        result["reason"] = f"ed25519_unavailable — fail closed: {exc}"
        return result

    for index, entry in enumerate(signatures):
        row: dict = {"index": index, "ok": False, "reason": None}
        result["checked"] += 1

        if not isinstance(entry, dict) or entry.get("type") != "Ed25519Signature2020":
            row["reason"] = "unsupported_signature_type"
            result["results"].append(row)
            continue

        method = entry.get("verificationMethod", "")
        if method != expected_vm:
            row["reason"] = "kid_mismatch (corrupt or foreign verificationMethod)"
            result["results"].append(row)
            continue

        stripped = dict(card)
        stripped["signatures"] = [s for j, s in enumerate(signatures) if j != index]
        canonical = _json.dumps(stripped, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )

        try:
            raw = base64.b64decode(entry.get("proofValue", ""), validate=True)
            pub.verify(raw, canonical)
            row["ok"] = True
            result["verified"] += 1
        except Exception as exc:  # noqa: BLE001
            row["reason"] = f"signature_invalid: {type(exc).__name__}"
        result["results"].append(row)

    if result["checked"] and result["verified"] == result["checked"]:
        result["valid"] = True
        result["status"] = "VERIFIED"
    elif result["verified"]:
        result["status"] = "PARTIAL"
        result["reason"] = "some signatures verified, some failed"
    else:
        result["reason"] = result["reason"] or "no_signature_verified"
    return result

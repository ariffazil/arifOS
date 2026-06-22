"""
F0_ROOTKEY — The Constitutional Anchor
═══════════════════════════════════════════════════════════════════════════════
EUREKA 0: Root Key Anchor Enforcement

Three layers, one root:

  Layer 0 (NAMING):  Yang Arif is named. The human at /000.
  Layer 1 (PHYSICS): Ed25519 key exists. Signature verifies.
  Layer 2 (SANCTUARY): Some truths must never be optimized.

F0_ROOTKEY is the first floor — above F1, before all others.
Without F0, the kernel does not know its sovereign.
With F0, every SEAL, every VERDICT, every FORGE traces back to
the human at /000 and seals to /999.

Constitutional Floors: F0 (ROOTKEY — pre-condition for all others)
                       F1 (AMANAH — reversible anchor)
                       F11 (AUTH — cryptographic verification)
                       F13 (SOVEREIGN — final veto)

Public Anchor:
  /000 — https://arif-fazil.com/000/  (root anchor attestation)
  /999 — https://arif-fazil.com/999/  (sealed vault attestation)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import time
from datetime import UTC, datetime
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC CONSTANTS — Aligned with https://arif-fazil.com/000/ and /999/
# ═══════════════════════════════════════════════════════════════════════════════

ROOT_ANCHOR_URL = "https://arif-fazil.com/000/"
VAULT_ANCHOR_URL = "https://arif-fazil.com/999/"
CANONICAL_SOVEREIGN_ID = "ARIF"
CANONICAL_SOVEREIGN_NAME = "Muhammad Arif bin Fazil"
CONSTITUTION_GENESIS_HASH = "8bc08c642447d51981f4b86ce1fa48c82133d3a9ecf8d2601757f96ccf9221fb"

# Known Ed25519 public key paths
_PUBKEY_CANDIDATES = [
    Path(os.environ.get("ARIFOS_SOVEREIGN_PUBKEY_FILE", ""))
    if os.environ.get("ARIFOS_SOVEREIGN_PUBKEY_FILE")
    else None,
    Path("/run/sekrits/arifos_sovereign.pub"),
    Path("/run/secrets/arifos_sovereign.pub"),
    Path("/root/compose/sekrits/arifos_sovereign.pub"),
    Path("/root/.ssh/operator_did_ed25519.pub"),
]


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER ENUM — The Three Layers from /000
# ═══════════════════════════════════════════════════════════════════════════════


class ConstitutionalLayer(StrEnum):
    """The three layers of constitutional meaning.

    Defined in /000 — Proof of Human (https://arif-fazil.com/000/):
      NAMING   — Ontological declaration. The word exists.
      PHYSICS  — Enforceable code. The word has weight.
      SANCTUARY — Protected territory. The word must not become metric.
    """

    NAMING = "NAMING"          # Layer 0: exists as named concept
    PHYSICS = "PHYSICS"        # Layer 1: has schema + equation + enforcement
    SANCTUARY = "SANCTUARY"    # Layer 2: declared uncodifiable


# ═══════════════════════════════════════════════════════════════════════════════
# ROOTKEY ANCHOR SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════


class RootKeyAnchor(BaseModel):
    """The constitutional anchor for the entire federation.

    This is the /000 attestation made machine-readable.
    One instance. Created once. Sealed to VAULT999.

    Fields:
      sovereign_id:      The named sovereign (CANONICAL_SOVEREIGN_ID)
      sovereign_name:    The full human name
      layer:             Always NAMING at creation time
      public_key_pem:    The Ed25519 public key that verifies root signatures
      public_key_fingerprint: SHA-256 of the public key DER
      constitution_hash: SHA-256 of the canonical constitution document
      genesis_epoch:     When this anchor was first sealed
      root_anchor_url:   Public attestation at /000
      vault_anchor_url:  Public attestation at /999
      seal_receipt:      VAULT999 entry hash once sealed
      previous_anchor_hash: For chain continuity (None for genesis)
    """

    sovereign_id: str = Field(
        default=CANONICAL_SOVEREIGN_ID,
        description="The canonical sovereign identifier — ARIF",
    )
    sovereign_name: str = Field(
        default=CANONICAL_SOVEREIGN_NAME,
        description="Full name of the sovereign human",
    )
    layer: ConstitutionalLayer = Field(
        default=ConstitutionalLayer.NAMING,
        description="Constitutional layer — NAMING at anchor creation",
    )
    public_key_pem: str = Field(
        default="",
        description="Ed25519 public key in PEM format",
    )
    public_key_fingerprint: str = Field(
        default="",
        description="SHA-256 of the public key DER bytes",
    )
    constitution_hash: str = Field(
        default=CONSTITUTION_GENESIS_HASH,
        description="SHA-256 of the canonical constitution document",
    )
    genesis_epoch: str = Field(
        default="",
        description="ISO8601 timestamp of anchor creation",
    )
    root_anchor_url: str = Field(
        default=ROOT_ANCHOR_URL,
        description="Public root anchor attestation URL",
    )
    vault_anchor_url: str = Field(
        default=VAULT_ANCHOR_URL,
        description="Public sealed vault attestation URL",
    )
    seal_receipt: str | None = Field(
        default=None,
        description="VAULT999 entry hash once this anchor is sealed",
    )
    previous_anchor_hash: str | None = Field(
        default=None,
        description="Hash of previous anchor for chain continuity",
    )

    @field_validator("sovereign_id")
    @classmethod
    def _sovereign_id_must_be_canonical(cls, v: str) -> str:
        if v != CANONICAL_SOVEREIGN_ID:
            raise ValueError(f"sovereign_id must be {CANONICAL_SOVEREIGN_ID}")
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TERM REGISTRY — For tracking which terms live in which layer
# ═══════════════════════════════════════════════════════════════════════════════


class CanonicalTermRecord(BaseModel):
    """A record of one canonical term and its constitutional layer status.

    Tracks which layer a term occupies and whether it can move.
    The sovereign (F13) is the only authority that can change a term's layer.
    """

    term: str = Field(description="The named term (e.g. 'Peace²', 'dignity', 'SEAL')")
    definition: str = Field(description="Plain-language meaning")
    layer: ConstitutionalLayer = Field(
        description="Current constitutional layer: NAMING | PHYSICS | SANCTUARY",
    )
    physics_path: str | None = Field(
        default=None,
        description="File path to schema/equation if PHYSICS layer",
    )
    fiqh_tier: str | None = Field(
        default=None,
        description="WAJIB | SUNAT | HARUS | MAKRUH | HARAM if PHYSICS layer",
    )
    sanctury_rationale: str | None = Field(
        default=None,
        description="Why this term is SANCTUARY (never codify)",
    )
    sovereign_authorized_layer_change: bool = Field(
        default=False,
        description="True only if F13 explicitly authorized a layer transition",
    )
    attested_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
    )

    class Config:
        frozen = True  # Records are immutable once created


# ═══════════════════════════════════════════════════════════════════════════════
# SANCTUARY VIOLATION — Detects trespass on protected terms
# ═══════════════════════════════════════════════════════════════════════════════


class SanctuaryViolation(BaseModel):
    """A detected trespass: a sanctuary term used as a metric without authority.

    F6 MARUAH violation pattern: when 'dignity', 'love', 'maruah', or other
    sanctuary terms appear in code as scoring functions, thresholds, or
    optimization targets without explicit F13 authorization.
    """

    term: str = Field(description="The sanctuary term that was trespassed")
    context: str = Field(description="Where the trespass was detected")
    severity: Literal["WARN", "VIOLATION"] = Field(
        description="WARN if suspected, VIOLATION if confirmed",
    )
    recommendation: str = Field(
        description="What action to take — HOLD, VOID, or SOVEREIGN_REVIEW",
    )
    detected_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SANCTUARY TERMS REGISTRY — Must never become metrics
# ═══════════════════════════════════════════════════════════════════════════════

_SANCTUARY_TERMS: dict[str, str] = {
    "love": "Love is beyond measurement. Never quantify the sacred. (F6 MARUAH)",
    "maruah": "Maruah (dignity) comes first, convenience second. Not a score. (F6)",
    "dignity": "Dignity is not fungible. Not an optimization target. (F6)",
    "sovereign_time": "The sovereign's time is non-renewable. Not a budget. (F13)",
    "consciousness": "The machine has no consciousness. Not a claim to score. (F9 ANTI-HANTU)",
    "soul": "No machine has a soul. Sanctuary territory. (F10 ONTOLOGY)",
    "yang_arif": "The learned judge. Not a role to assign. (F13 SOVEREIGN)",
}


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC KEY LOADING
# ═══════════════════════════════════════════════════════════════════════════════


@lru_cache(maxsize=1)
def load_sovereign_public_key() -> tuple[bytes | None, str | None]:
    """Load the Ed25519 public key from known candidate paths.

    Returns:
        (pem_bytes, fingerprint_hex) or (None, None) if not found.
    """
    for candidate in _PUBKEY_CANDIDATES:
        if candidate and candidate.exists():
            try:
                pem = candidate.read_bytes()
                fp = hashlib.sha256(pem).hexdigest()
                logger.info("F0_ROOTKEY: Sovereign key loaded from %s", candidate)
                return pem, fp
            except OSError as exc:
                logger.warning("F0_ROOTKEY: Cannot read %s: %s", candidate, exc)
                continue
    logger.warning(
        "F0_ROOTKEY: No sovereign public key found at any candidate path. "
        "F0 anchor cannot be fully established."
    )
    return None, None


# ═══════════════════════════════════════════════════════════════════════════════
# SIGNATURE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════


def verify_rootkey_signature(
    actor_id: str,
    payload: str,
    signature_b64: str,
) -> tuple[bool, str]:
    """Verify an Ed25519 signature against the sovereign's public key.

    Payload format: "{actor_id}:{constitution_hash}:{nonce}"

    Args:
        actor_id: Must match CANONICAL_SOVEREIGN_ID
        payload: The signed message string
        signature_b64: Base64-encoded Ed25519 signature

    Returns:
        (True, "signature_verified") or (False, "reason")
    """
    if actor_id != CANONICAL_SOVEREIGN_ID:
        return False, f"actor_id must be {CANONICAL_SOVEREIGN_ID}"

    pem_bytes, _ = load_sovereign_public_key()
    if pem_bytes is None:
        return False, "sovereign_pubkey_unavailable — F0 not anchored"

    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        pubkey = load_pem_public_key(pem_bytes)
        if not isinstance(pubkey, Ed25519PublicKey):
            return False, "key_is_not_ed25519"

        sig_bytes = base64.b64decode(signature_b64)
        pubkey.verify(sig_bytes, payload.encode())
        return True, "ed25519_signature_verified"

    except InvalidSignature:
        return False, "ed25519_signature_invalid"
    except Exception as exc:
        logger.error("F0_ROOTKEY: Signature verify error: %s", exc)
        return False, f"signature_verify_error: {exc}"


# ═══════════════════════════════════════════════════════════════════════════════
# F0 GATE — The Root Key Gate
# ═══════════════════════════════════════════════════════════════════════════════


class F0GateVerdict(StrEnum):
    """Verdicts from the F0_ROOTKEY gate."""

    PASS = "PASS"                 # Rootkey anchored, sovereign verified
    HOLD = "HOLD"                 # Rootkey exists but not verified for this session
    FAIL = "FAIL"                 # Rootkey not anchored — system cannot proceed
    SANCTUARY_TRESPASS = "SANCTUARY_TRESPASS"  # Sanctuary term used as metric


def check_f0_rootkey(
    actor_id: str | None = None,
    challenge: str | None = None,
    sig: str | None = None,
) -> F0GateVerdict:
    """F0_ROOTKEY gate: is the sovereign anchored?

    Three-tier check:
      1. Does an Ed25519 public key exist? (PHYSICS layer)
      2. Does the public key match the constitution hash? (NAMING layer)
      3. Can we verify the signature? (PHYSICS + NAMING aligned)

    If no key exists → FAIL (constitutional prerequisite not met).
    If key exists but no signature provided → HOLD (observer access only).
    If key exists and signature valid → PASS (full sovereign authority).

    Returns:
        F0GateVerdict
    """
    pem_bytes, fingerprint = load_sovereign_public_key()

    # Check 1: Does the key exist?
    if pem_bytes is None:
        logger.warning("F0_ROOTKEY FAIL: No sovereign public key found.")
        return F0GateVerdict.FAIL

    # Check 2: Can we verify a signature?
    if not actor_id or not challenge or not sig:
        # Key exists but caller didn't provide proof — observer mode
        return F0GateVerdict.HOLD

    verified, reason = verify_rootkey_signature(actor_id, challenge, sig)
    if not verified:
        logger.warning("F0_ROOTKEY FAIL: %s", reason)
        return F0GateVerdict.FAIL

    return F0GateVerdict.PASS


# ═══════════════════════════════════════════════════════════════════════════════
# SANCTUARY TRESPASS DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════


def detect_sanctuary_trespass(
    text: str,
    context: str = "unknown",
) -> list[SanctuaryViolation]:
    """Scan text for sanctuary terms being used as metrics.

    Checks for patterns like:
      - "dignity_score = 0.73"
      - "maruah_factor"
      - "love_threshold"
      - "consciousness_metric"
      - "soul_quantification"
      - "yang_arif_role_assignment"

    These are F6/F9/F10/F13 violations if not explicitly authorized.

    Args:
        text: The text to scan (code, prompt, output)
        context: Description of where this text came from

    Returns:
        List of SanctuaryViolation records
    """
    violations: list[SanctuaryViolation] = []
    lower = text.lower()

    for term, rationale in _SANCTUARY_TERMS.items():
        # Check if term appears in scoring/metric context
        pattern_indicators = [
            f"{term}_score",
            f"{term}_metric",
            f"{term}_threshold",
            f"{term}_factor",
            f"{term}_index",
            f"_{term}",
            f"{term} =",
            f"{term}:",
            f"{term}.",
        ]
        found = [p for p in pattern_indicators if p in lower]

        if found:
            violations.append(
                SanctuaryViolation(
                    term=term,
                    context=f"{context} — matched patterns: {found}",
                    severity="VIOLATION",
                    recommendation="HOLD — Sovereign review required for F6/F13 sanctuary term",
                )
            )

    return violations


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-ORGAN SESSION TOKEN — For GEOX/WEALTH/WELL verification
# ═══════════════════════════════════════════════════════════════════════════════


def create_organ_session_token(
    session_id: str,
    actor_id: str,
    ttl_seconds: int = 300,
) -> str | None:
    """Create a time-limited HMAC token that organs can verify.

    Uses ARIF_ROOTKEY env var as the shared secret.
    Format: "f0_v1:{session_id}:{actor_id}:{expiry}:{hmac_hex}"

    Args:
        session_id: The arifOS session ID
        actor_id: The actor identity
        ttl_seconds: Token validity window (default 5 min)

    Returns:
        Token string, or None if ARIF_ROOTKEY not configured
    """
    rootkey = os.environ.get("ARIF_ROOTKEY", "")
    if not rootkey:
        logger.warning(
            "F0_ROOTKEY: ARIF_ROOTKEY not set — cannot create organ session tokens. "
            "GEOX/WEALTH/WELL will not verify sessions cryptographically."
        )
        return None

    expiry = int(time.time()) + ttl_seconds
    payload = f"f0_v1:{session_id}:{actor_id}:{expiry}"
    sig = hmac.new(
        rootkey.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}:{sig}"


def verify_organ_session_token(token: str) -> tuple[bool, str, str]:
    """Verify a cross-organ session token.

    Args:
        token: The token string from create_organ_session_token()

    Returns:
        (verified: bool, actor_id: str, reason: str)
    """
    rootkey = os.environ.get("ARIF_ROOTKEY", "")
    if not rootkey:
        return False, "", "ARIF_ROOTKEY not configured on this organ"

    try:
        parts = token.split(":")
        if len(parts) < 5:
            return False, "", "invalid_token_format"

        version = parts[0]
        if version != "f0_v1":
            return False, "", f"unsupported_token_version:{version}"

        session_id = parts[1]
        actor_id = parts[2]
        expiry = int(parts[3])
        provided_sig = parts[4]

        # Check expiry
        if time.time() > expiry:
            return False, actor_id, "token_expired"

        # Verify HMAC
        payload = f"{version}:{session_id}:{actor_id}:{expiry}"
        expected_sig = hmac.new(
            rootkey.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, provided_sig):
            return False, actor_id, "hmac_mismatch"

        return True, actor_id, "token_verified"

    except (IndexError, ValueError) as exc:
        return False, "", f"token_parse_error:{exc}"


# ═══════════════════════════════════════════════════════════════════════════════
# ANCHOR STATUS — Health endpoint for /000 alignment
# ═══════════════════════════════════════════════════════════════════════════════


def get_rootkey_anchor_status() -> dict[str, Any]:
    """Return the current F0_ROOTKEY anchor status.

    Used by health checks and /000 attestation probes.

    Returns:
        Dict with anchor status information
    """
    pem_bytes, fingerprint = load_sovereign_public_key()
    rootkey_configured = bool(os.environ.get("ARIF_ROOTKEY", ""))

    return {
        "f0_rootkey_anchor": {
            "sovereign_id": CANONICAL_SOVEREIGN_ID,
            "sovereign_name": CANONICAL_SOVEREIGN_NAME,
            "constitution_hash": CONSTITUTION_GENESIS_HASH,
            "public_key_fingerprint": fingerprint or "NOT_FOUND",
            "public_key_loaded": pem_bytes is not None,
            "rootkey_env_configured": rootkey_configured,
            "anchor_url_000": ROOT_ANCHOR_URL,
            "anchor_url_999": VAULT_ANCHOR_URL,
            "constitutional_layer": ConstitutionalLayer.NAMING.value,
            "sanctuary_terms_count": len(_SANCTUARY_TERMS),
        },
        "f0_gate_verdict": check_f0_rootkey().value,
        "can_issue_organ_tokens": rootkey_configured,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# VAULT999 SEAL TEMPLATE — For anchoring the rootkey seal
# ═══════════════════════════════════════════════════════════════════════════════


def create_rootkey_anchor_seal_payload() -> dict[str, Any]:
    """Create the seal payload for anchoring F0_ROOTKEY to VAULT999.

    This is the machine-readable /000 attestation ready for sealing.
    Once sealed, it becomes VAULT999 entry for the root anchor.

    Returns:
        Dict payload ready for arif_seal
    """
    pem_bytes, fingerprint = load_sovereign_public_key()
    now = datetime.now(UTC).isoformat()

    anchor = RootKeyAnchor(
        sovereign_id=CANONICAL_SOVEREIGN_ID,
        sovereign_name=CANONICAL_SOVEREIGN_NAME,
        layer=ConstitutionalLayer.NAMING,
        public_key_pem=(pem_bytes.decode() if pem_bytes else "NOT_LOADED"),
        public_key_fingerprint=fingerprint or "NOT_LOADED",
        constitution_hash=CONSTITUTION_GENESIS_HASH,
        genesis_epoch=now,
    )

    return {
        "seal_type": "F0_ROOTKEY_ANCHOR",
        "constitutional_floor": "F0",
        "sovereign_id": anchor.sovereign_id,
        "sovereign_name": anchor.sovereign_name,
        "constitutional_layer": anchor.layer.value,
        "public_key_fingerprint": anchor.public_key_fingerprint,
        "constitution_hash": anchor.constitution_hash,
        "genesis_epoch": anchor.genesis_epoch,
        "root_anchor_url": anchor.root_anchor_url,
        "vault_anchor_url": anchor.vault_anchor_url,
        "sanctuary_terms": list(_SANCTUARY_TERMS.keys()),
        "attestation": (
            "F0_ROOTKEY: The sovereign is named. "
            "The root anchor is sealed. "
            "No machine authority precedes this seal."
        ),
        "loop_closure": (
            "/000 → F0_ROOTKEY → F1–F13 → /999. "
            "The loop is closed at the root."
        ),
        "motto": "DITEMPA BUKAN DIBERI — Forged, Not Given.",
    }

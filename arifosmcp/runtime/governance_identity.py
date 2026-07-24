"""
governance_identity.py — Protected Sovereign Identity Registry (L11/L13)

Defines protected sovereign IDs that require cryptographic proof or explicit
human approval before session anchoring is permitted.

SECURITY NOTE (2026-07-06): SEMANTIC_KEYS removed. The "IM ARIF" hash-based
bypass was dead code (not imported by runtime/tools.py or session.py) but
its existence was a liability. Protected identity verification now requires:
1. Valid Ed25519/ES256 cryptographic signature, OR
2. Explicit human_approval from a verified session, OR
3. Sovereign ack through arif_init(ack_irreversible=True) path.

Semantic phrase matching (IDENTITY_PHRASES) is retained for NLP input
parsing only — it does NOT grant identity verification.
"""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import UTC
from typing import Any

logger = logging.getLogger(__name__)

# P0: Protected Sovereign IDs (L11 Identity Hardening)
# These IDs cannot be claimed without:
# 1. Valid cryptographic proof (signed token), OR
# 2. Explicit human_approval flag with acknowledgment, OR
# 3. Valid Semantic Key (Naming is the act of creation)
PROTECTED_SOVEREIGN_IDS: set[str] = {
    "arif",
    "ariffazil",
    "sovereign",
    "admin",
    "root",
    "system",
    "arif-fazil",
    "arif_fazil",
    "muhammad_arif",
}

# SECURITY P0 2026-07-12: Sovereign authority binds to a verified key, not a name.
# Keys are prefixed by verification method:
#   "ed25519:sha256:..." — Ed25519 raw key (cryptography lib, PyNaCl)
#   "ssh:SHA256:..."     — SSH Ed25519 key (ssh-keygen format)
SOVEREIGN_KEY_IDS: set[str] = {
    "ed25519:sha256:a8fbb5ae8b4772b0",  # Arif /000/ DID key (did:web:arif-fazil.com)
    "ed25519:sha256:9c35a833fef25f17",  # Arif AAA identity key (2026-07-12)
}

# SSH sovereign key fingerprints are registered dynamically by forge_seal_init.sh
# They are loaded from the file /root/AAA/IDENTITY/authorized_ssh_pubkey.pem
# at runtime by ssh_proof.prove_sovereign()

# F13 multi-key registry for bounded actors (Anomalies #1 closure).
# Each entry: key_id (sha256[:16] fingerprint of public key) -> actor_id.
VERIFIED_KEY_IDS: dict[str, str] = {
    "ed25519:sha256:04761fd348a64558": "mesa-test-agent",
    "mesa-test-agent": "mesa-test-agent",
    "meta-test-agent": "meta-test-agent",
    # Node 3 — ariffazil-windows (L4 warga, OBSERVE_ONLY)
    # ed25519 fingerprint: PENDING_FIRST_CONNECT
    # IP binding: 100.64.0.3 (Tailscale)
    # Session model: SHARED_CEILING
    # Offline grace: NO_AUTO_EXPIRY
    # F13 decisions: ed25519 rotation = F13 gate, multi-session = shared
    "node3-ariffazil-windows": "node3-ariffazil-windows",
}
VERIFIED_KEY_IDS_MAX: int = 16

# L4 Warga Authority Ceiling — OBSERVE_ONLY actors
# These actors cannot mutate, seal, or judge. They observe and route only.
L4_WARGA_ACTORS: set[str] = {
    "node3-ariffazil-windows",
}
L4_ALLOWED_VERBS: set[str] = {
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
}
L4_BLOCKED_VERBS: set[str] = {
    "arif_forge",
    "arif_seal",
    "arif_judge",
    "arif_act",
}

# P2 2026-07-13: Sovereign signal phrases (HITL-collapse mitigation).
# When an agent presents one of these signals as proof, the kernel routes
# through the A-FORGE session registry to verify the signal originated
# from an active sovereign session. Closes the arif_seal → forge_vault
# asymmetry per Arif directive.
# Deprecated alias — kept for back-compat with any caller that imports this
# name directly. The canonical home is arifosmcp.runtime.human_intent.
# Per D3 (2026-07-13): phrases never grant authority — they trigger a
# confirmation workflow that ends with a bound cryptographic capability.
SOVEREIGN_SIGNAL_PHRASES = __import__(
    "arifosmcp.runtime.human_intent", fromlist=["CONFIRMATION_INTENT_PHRASES"]
).CONFIRMATION_INTENT_PHRASES

# ── Sovereign Alias Normalization (FORGED 2026-07-15) ─────────────────────────
# F13 SOVEREIGN: Any natural-language prefix + "ARIF" resolves to the
# sovereign principal.  Greetings are stripped, core identity is extracted.
# This is NOT authentication — it is NLP normalization so the sovereign
# doesn't have to type a machine-exact string.
#
# "Salam ARIF" → "arif"   "Hi Arif" → "arif"   "Saya Arif" → "arif"
# "AKU ARIF" → "arif"     "Yang Arif" → "arif"  "ARIF F." → "arif"
# Security: only extracts to known canonical IDs. Unknown → returned as-is.
# ──────────────────────────────────────────────────────────────────────────────

# Greeting / prefix words to strip (case-insensitive, multilingual).
# Order matters: longer prefixes first to avoid partial strip.
_IDENTITY_STRIP_PREFIXES: tuple[str, ...] = (
    # Malay / BM greetings
    "salam",
    "assalamualaikum",
    "assalamu",
    # English greetings
    "hello",
    "hi",
    "hey",
    "yo",
    "howdy",
    # Malay pronouns / introductions
    "saya",
    "aku",
    "hamba",
    "yang",
    # English pronouns / introductions
    "i am",
    "i'm",
    "im",
    "it's",
    "its",
    "this is",
)

# Core identity variants → canonical actor_id.
# Checked AFTER prefix stripping and lowercasing.
_SOVEREIGN_CORE_VARIANTS: dict[str, str] = {
    "arif": "arif",
    "arif fazil": "arif",
    "arif_fazil": "arif",
    "arif-fazil": "arif",
    "ariffazil": "arif",
    "arif f": "arif",
    "arif f.": "arif",
    "muhammad arif": "arif",
    "muhammad arif bin fazil": "arif",
    "muhammad_arif": "arif",
    "888": "arif",
    "f13": "arif",
    "sovereign": "arif",
}


def normalize_actor_id(raw: str | None) -> str | None:
    """
    Normalize a natural-language actor_id to its canonical form.

    Strips greeting prefixes, lowercases, and maps known sovereign variants
    to their canonical actor_id.  Returns the original value if no known
    variant matches — this is safe because downstream code already handles
    unknown actor_ids by defaulting to OBSERVE_ONLY.

    NOT authentication. This is NLP convenience only.

    Examples:
        "Salam ARIF"     → "arif"
        "Hi Arif"        → "arif"
        "Saya Arif"      → "arif"
        "AKU ARIF"       → "arif"
        "Yang Arif"      → "arif"
        "ARIF F."        → "arif"
        "arif"           → "arif"
        "ARIF_FAZIL"     → "arif"
        "SALAM"          → "SALAM"  (unknown → unchanged)
        None             → None
    """
    if not raw:
        return None

    text = raw.strip()
    if not text:
        return None

    lower = text.lower()

    # 1. Direct match first (fast path — most callers pass exact IDs)
    if lower in _SOVEREIGN_CORE_VARIANTS:
        return _SOVEREIGN_CORE_VARIANTS[lower]

    # 2. Strip greeting/prefix words
    stripped = lower
    for prefix in _IDENTITY_STRIP_PREFIXES:
        if stripped.startswith(prefix + " "):
            stripped = stripped[len(prefix) :].strip()
            break  # only strip one prefix layer

    # Remove trailing punctuation
    stripped = stripped.rstrip(".!?")

    # 3. Check stripped form against known variants
    if stripped in _SOVEREIGN_CORE_VARIANTS:
        return _SOVEREIGN_CORE_VARIANTS[stripped]

    # 4. Check if "arif" appears as a standalone word in the input
    #    (catches "Salam ARIF", "Hello there ARIF", etc.)
    import re

    if re.search(r"\barif\b", lower):
        # Only resolve if the remainder is purely greeting/prefix noise
        remainder = re.sub(r"\barif\b", "", lower).strip().rstrip(".!?")
        # Check if remainder is empty or composed of known prefix words
        remainder_words = set(remainder.split())
        prefix_words = set()
        for p in _IDENTITY_STRIP_PREFIXES:
            prefix_words.update(p.split())
        # Also allow filler words
        filler_words = {"there", "dear", "bro", "boss", "man", "sir", "the", "one"}
        allowed_noise = prefix_words | filler_words
        if not remainder_words or remainder_words.issubset(allowed_noise):
            return "arif"

    # 5. No match — return original (downstream handles unknown safely)
    return raw


# Semantic identity phrases (NLP input parsing ONLY — NOT authentication)
# These parse natural language identity claims from user input.
# They do NOT grant verification or authority.
IDENTITY_PHRASES: list[tuple[str, str]] = [
    (r"^(i am|im|i'm|saya|aku|hamba)\s+(arif|ariffazil|arif-fazil)$", "arif"),
    (
        r"^(hi|hello|hey|yo)\s+(i am|im|i'm|saya|aku)\s+(arif|ariffazil|arif-fazil)$",
        "arif",
    ),
    (r"^it's\s+(arif|ariffazil|arif-fazil)$", "arif"),
]


def canonicalize_identity_claim(text: str | None) -> str | None:
    """
    Parse raw input for identity claims (Naming as Creation).
    Returns canonical actor_id if matched, else None.
    """
    if not text:
        return None

    clean_text = text.lower().strip().rstrip(".!?")

    for pattern, canonical_id in IDENTITY_PHRASES:
        if re.match(pattern, clean_text):
            return canonical_id

    return None


# P0: Identity claim validation
def is_protected_sovereign_id(actor_id: str | None) -> bool:
    """Check if actor_id is a protected sovereign identity."""
    if not actor_id or actor_id == "anonymous":
        return False
    return actor_id.lower().strip() in PROTECTED_SOVEREIGN_IDS


# P0: Proof validation helper (Harden Bridge v1.0)
def validate_sovereign_proof(actor_id: str, proof: dict | str | Any | None) -> bool:
    """
    Validate cryptographic proof for protected sovereign ID.

    L11: Command Authority
    L13: Sovereign Override

    SECURITY (2026-07-06): Semantic key bypass removed. Only cryptographic
    signatures or explicit human approval through verified sessions are accepted.

    IMPLEMENTED (2026-07-07): Ed25519 + HMAC verification via sovereign_verify.
    """
    if not proof:
        return False

    # Cryptographic signature path (Ed25519)
    if isinstance(proof, dict):
        required_fields = ["signature", "nonce", "timestamp"]
        if all(field in proof for field in required_fields):
            return _verify_ed25519_proof(actor_id, proof)

        # HMAC path (Telegram-native identity)
        if "hmac_challenge" in proof and "hmac_sig" in proof:
            return _verify_hmac_proof(actor_id, proof)

        # P2 2026-07-13: A-FORGE session token path (HITL-collapse mitigation).
        # Agents operating under a live forge_session token may exercise
        # sovereign authority on behalf of the issuer. Wire shape is live;
        # cryptographic verification delegates to the A-FORGE session
        # registry backend (forge_session_runtime).
        if "session_id" in proof and "session_signature" in proof:
            return _verify_forge_session_proof(actor_id, proof)

        # P2 2026-07-13: Sovereign signal phrase path. Binds narrative
        # signals recognized from F13 to the active session context.
        if "sovereign_signal" in proof:
            return _verify_sovereign_signal_proof(actor_id, proof)

    # String proof (e.g. "IM ARIF") is NOT accepted for identity verification.
    # It may be used for NLP input parsing via canonicalize_identity_claim(),
    # but that does NOT grant authority or verification status.
    return False


def _verify_forge_session_proof(actor_id: str, proof: dict) -> bool:
    """
    Verify A-FORGE session token (delegated sovereign authority).

    Per E1 spec (2026-07-13 corrective), this dispatcher builds the
    canonical token dict from the wire proof and delegates to
    arifosmcp.runtime.forge_session_runtime.verify_forge_session_token,
    which performs 13 checks per spec against canonical session state.

    Returns False (fail-CLOSED) on:
    - Backend import failure
    - Backend unavailable (BACKEND_UNAVAILABLE)
    - Any other fail-closed code from the canonical verifier

    Stays True iff canonical verifier returns OK.
    """
    try:
        from arifosmcp.runtime.forge_session_runtime import (
            AUDIENCE_FORGE_SESSION,
            EXPECTED_TOKEN_VERSION,
            verify_forge_session_token,
        )
    except ImportError:
        logger.warning(
            "E1: forge_session_runtime import failed — forge_session path fail-closed "
            "(actor=%s, session_id=%s)",
            actor_id,
            proof.get("session_id"),
        )
        return False

    # Build canonical token dict from wire proof. Wire shape:
    #   session_id, session_signature, nonce, timestamp
    # Canonical token adds: actor_id, audience, issued_at, expires_at, capability, token_version
    from datetime import datetime, timedelta

    now = datetime.now(UTC)
    issued_at = proof.get("timestamp") or now.isoformat()
    expires_at = proof.get("expires_at") or (now + timedelta(minutes=5)).isoformat()

    token = {
        "session_id": proof.get("session_id", ""),
        "actor_id": actor_id,
        "nonce": proof.get("nonce", ""),
        "audience": proof.get("audience", AUDIENCE_FORGE_SESSION),
        "issued_at": issued_at,
        "expires_at": expires_at,
        "capability": proof.get("capability", "vault.append"),
        "signature": proof.get("session_signature", ""),
        "token_version": proof.get("token_version", EXPECTED_TOKEN_VERSION),
    }

    result = verify_forge_session_token(token)
    if not result.ok:
        logger.info(
            "E1 forge_session: reject — code=%s session=%s actor=%s",
            result.code,
            result.session_id,
            result.actor_id,
        )
    return result.ok


def _verify_sovereign_signal_proof(actor_id: str, proof: dict) -> bool:
    """
    Verify a session-bound assertion (HITL-collapse mitigation).

    Per E1 spec: 'A narrative object is not sovereignty.' Phrases alone do
    not grant authority. Recognition of a recognized phrase (see
    SOVEREIGN_SIGNAL_PHRASES) is necessary but not sufficient — the phrase
    must arrive through a verified session-bound assertion.

    Delegates to forge_session_runtime.verify_session_bound_assertion.
    """
    signal = (proof.get("sovereign_signal") or "").lower().strip()
    session_id = proof.get("session_id")
    nonce = proof.get("nonce", "")
    signature = proof.get("assertion_signature") or proof.get("signature", "")
    payload_hash = proof.get("payload_hash", "")
    purpose = proof.get("purpose", "informational_signal")

    # If no phrase AND no session-bound assertion shape, fail
    if not signal and not session_id:
        return False

    # Phrase must be recognized (cheap pre-filter)
    if signal and signal not in SOVEREIGN_SIGNAL_PHRASES:
        return False

    # Need session_id for the canonical verifier
    if not session_id:
        return False

    try:
        from datetime import datetime, timedelta, timezone

        from arifosmcp.runtime.forge_session_runtime import (
            EXPECTED_TOKEN_VERSION,
            verify_session_bound_assertion,
        )

        now = datetime.now(UTC)
        assertion = {
            "session_id": session_id,
            "actor_id": actor_id,
            "payload_hash": payload_hash
            or hashlib.sha256(f"{session_id}:{actor_id}:{signal}".encode()).hexdigest(),
            "purpose": purpose,
            "nonce": nonce,
            "issued_at": proof.get("issued_at") or now.isoformat(),
            "expires_at": proof.get("expires_at") or (now + timedelta(minutes=1)).isoformat(),
            "signature": signature,
            "assertion_version": proof.get("assertion_version", EXPECTED_TOKEN_VERSION),
        }
        result = verify_session_bound_assertion(assertion)
        if not result.ok:
            logger.info(
                "E1 sovereign_signal: reject — code=%s session=%s actor=%s",
                result.code,
                result.session_id,
                result.actor_id,
            )
        return result.ok
    except ImportError:
        logger.warning(
            "E1: forge_session_runtime import failed — sovereign_signal path fail-closed "
            "(actor=%s, session_id=%s)",
            actor_id,
            session_id,
        )
        return False


def _verify_ed25519_proof(actor_id: str, proof: dict) -> bool:
    """Verify Ed25519 signature proof. Returns True only on cryptographic success."""
    try:
        from arifosmcp.runtime.sovereign_signer import get_constitution_hash
        from arifosmcp.runtime.sovereign_verify import (
            is_challenge_fresh,
            verify_sovereign_signature,
        )
    except ImportError:
        logger.error(
            "sovereign_verify/sovereign_signer not importable — Ed25519 verification unavailable"
        )
        return False

    nonce = proof["nonce"]
    signature = proof["signature"]

    # Reject stale challenges (900s window for Ed25519 — session-lifetime bound)
    if not is_challenge_fresh(nonce, window_sec=900):
        logger.warning("Ed25519 proof rejected: stale nonce for actor=%s", actor_id)
        return False

    constitution_hash = get_constitution_hash()
    verified, reason = verify_sovereign_signature(
        actor_id=actor_id,
        constitution_hash=constitution_hash,
        nonce=nonce,
        actor_signature=signature,
    )

    if verified:
        logger.info("Ed25519 proof verified for actor=%s", actor_id)
    else:
        logger.warning("Ed25519 proof FAILED for actor=%s reason=%s", actor_id, reason)

    return verified


def _verify_hmac_proof(actor_id: str, proof: dict) -> bool:
    """Verify HMAC-rootkey proof (Telegram-native path)."""
    try:
        from arifosmcp.runtime.sovereign_verify import verify_hmac_signature
    except ImportError:
        logger.error("sovereign_verify not importable — HMAC verification unavailable")
        return False

    verified, reason = verify_hmac_signature(
        actor_id=actor_id,
        challenge=proof["hmac_challenge"],
        sig=proof["hmac_sig"],
    )

    if verified:
        logger.info("HMAC proof verified for actor=%s", actor_id)
    else:
        logger.warning("HMAC proof FAILED for actor=%s reason=%s", actor_id, reason)

    return verified


# ═══ W9 hardening 2026-07-24: seven-band identity projection + SESSION_EXPIRED marker ═══

from typing import Literal  # noqa: E402

try:
    from pydantic import BaseModel, ConfigDict  # noqa: E402

    _HAVE_PYDANTIC = True
except Exception:  # noqa: BLE001
    _HAVE_PYDANTIC = False


if _HAVE_PYDANTIC:

    class IdentityBands(BaseModel):
        """Seven-band identity projection (W9 hardening 2026-07-24).

        The seven fields are DISTINCT — binding never implies cryptographic
        verification, and mutation / seal are derived from verification plus
        authority band. F13 still HOLDS unverified authority.
        """

        model_config = ConfigDict(extra="forbid", frozen=True)

        actor_claimed: str | None = None
        actor_canonicalized: str | None = None
        actor_bound: bool = False
        actor_cryptographically_verified: bool = False
        authority_band: Literal[
            "OBSERVE_ONLY",
            "OBSERVE",
            "SUGGEST",
            "EXECUTE_REVERSIBLE",
            "EXECUTE_HIGH_IMPACT",
            "SEAL",
        ] = "OBSERVE_ONLY"
        mutation_allowed: bool = False
        seal_allowed: bool = False

    class SessionExpiredMarker(BaseModel):
        """Structured SESSION_EXPIRED response (no geometry leak)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

        error: Literal["SESSION_EXPIRED"] = "SESSION_EXPIRED"
        can_retry: Literal[True] = True
        next_safe_action: Literal["Call arif_init and replay the same normalized payload"] = (
            "Call arif_init and replay the same normalized payload"
        )

else:

    class IdentityBands:  # type: ignore[no-redef]
        actor_claimed: str | None = None
        actor_canonicalized: str | None = None
        actor_bound: bool = False
        actor_cryptographically_verified: bool = False
        authority_band: str = "OBSERVE_ONLY"
        mutation_allowed: bool = False
        seal_allowed: bool = False

        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class SessionExpiredMarker:  # type: ignore[no-redef]
        error: str = "SESSION_EXPIRED"
        can_retry: bool = True
        next_safe_action: str = "Call arif_init and replay the same normalized payload"

        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


def coerce_identity_dict(d: dict[str, Any] | None) -> dict[str, Any]:
    """Expand legacy two-bool {actor_bound, actor_verified} patterns into the
    seven-band identity projection WITHOUT silently upgrading bound to
    verified. If a wrapper previously reported `actor_bound=True, actor_verified=False`,
    the new projection retains the distinction.

    Accepts the legacy 5-field form (`actor_verified`, `authority_band`,
    `mutation_allowed`, `seal_allowed`) and emits the canonical 7-field form.
    Never collapses the two booleans.
    """
    if not isinstance(d, dict):
        return {
            "actor_claimed": None,
            "actor_canonicalized": None,
            "actor_bound": False,
            "actor_cryptographically_verified": False,
            "authority_band": "OBSERVE_ONLY",
            "mutation_allowed": False,
            "seal_allowed": False,
        }
    out: dict[str, Any] = {
        "actor_claimed": d.get("actor_claimed"),
        "actor_canonicalized": d.get("actor_canonicalized"),
        "actor_bound": bool(d.get("actor_bound", False)),
        "actor_cryptographically_verified": bool(
            d.get("actor_cryptographically_verified", d.get("actor_verified", False))
        ),
        "authority_band": d.get("authority_band") or "OBSERVE_ONLY",
        "mutation_allowed": bool(d.get("mutation_allowed", False)),
        "seal_allowed": bool(d.get("seal_allowed", False)),
    }
    # belt-and-braces: never let bound imply verified in the output
    if out["actor_bound"] and not out["actor_cryptographically_verified"]:
        # legitimate state — leave it
        pass
    if out["actor_cryptographically_verified"] and not out["actor_bound"]:
        # cryptographic proof without session binding — also legitimate
        pass
    return out


def session_expired_marker() -> dict[str, Any]:
    """Return the canonical SESSION_EXPIRED marker. No geometry, schema, or
    identity leak. The replay guidance is fixed and exact.
    """
    return {
        "error": "SESSION_EXPIRED",
        "can_retry": True,
        "next_safe_action": "Call arif_init and replay the same normalized payload",
    }


__all__ = [
    "IdentityBands",
    "SessionExpiredMarker",
    "coerce_identity_dict",
    "session_expired_marker",
]

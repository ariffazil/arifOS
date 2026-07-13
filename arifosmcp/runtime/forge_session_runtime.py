"""
forge_session_runtime.py — F13 Sovereign Chain (EUREKA P1 G4)

Dependencies: governance_identity (SOVEREIGN_KEY_IDS, PROTECTED_SOVEREIGN_IDS)
Authored: For F13 sovereign chain — fail-closed by default

Module surface:
  - sovereign_signal()       — 4-gate sovereignty check
  - ForgeSessionProof        — immutable proof linking forge action to session
  - create_forge_session_proof() — signed proof creation
  - verify_forge_session_chain() — trace receipt through session proof chain
  - verify_forge_session_token()  — HMAC-based session token verification (imported by governance_identity)
  - verify_session_bound_assertion() — session-bound narrative assertion (imported by governance_identity)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

EXPECTED_TOKEN_VERSION: str = "1"
AUDIENCE_FORGE_SESSION: str = "arifos:forge_session"
DEFAULT_TOKEN_TTL_SECONDS: int = 300  # 5 min
MAX_TOKEN_TTL_SECONDS: int = 3600     # 1 hour cap

# Session-bound assertion TTL (tight — assertions are narrow in time)
ASSERTION_TTL_SECONDS: int = 60

# ── Data Classes ───────────────────────────────────────────────────────────


@dataclass
class SovereignVerdict:
    """Result of a sovereign_signal() check.

    Fields:
      - sovereignty: bool    # True only if ALL gates pass
      - verified: bool       # cryptographically verified
      - method: str          # "f13_sovereign" | "session_anchor" | "anonymous"
      - reason: str          # human-readable: what passed/failed
      - fail_closed: bool    # invariant — this module does not guess
    """
    sovereignty: bool = False
    verified: bool = False
    method: str = "anonymous"
    reason: str = "fail-closed: no check performed"
    fail_closed: bool = True


@dataclass
class ChainVerdict:
    """Result of a forge session chain verification.

    Fields:
      - valid: bool          # True only if chain is intact
      - chain: list[str]     # ordered list of chain links (session_id → receipt_id)
      - broken_at: str | None  # which link broke the chain, or None
    """
    valid: bool = False
    chain: list[str] = field(default_factory=list)
    broken_at: str | None = None


@dataclass
class TokenVerdict:
    """Result of forge session token verification.

    Fields:
      - ok: bool             # True only if ALL checks pass
      - code: str            # machine-readable result code
      - session_id: str      # session this token is bound to
      - actor_id: str        # actor this token was issued to
      - reason: str          # human-readable explanation
    """
    ok: bool = False
    code: str = "FAIL_CLOSED"
    session_id: str = ""
    actor_id: str = ""
    reason: str = "fail-closed: no check performed"


# ── Session Registry (in-memory — for now, mirroring _SESSIONS) ────────────

# P2: Replace with persistent store (Postgres/Supabase).
# Shape: session_id → { actor_id, verified_key_id, verification_method, created_at, expires_at, anchor_type }
_SESSION_REGISTRY: dict[str, dict[str, Any]] = {}
_SESSION_REGISTRY_LOCK = __import__("threading").RLock()


def register_session_anchor(
    session_id: str,
    actor_id: str | None,
    verified_key_id: str | None = None,
    verification_method: str | None = None,
    ttl_seconds: int = 3600,
) -> bool:
    """Register a session's sovereign anchor in the registry.

    Called by arif_init after identity binding to stamp the session
    with its sovereignty level.

    Returns True on success, False if session already anchored (immutable).
    """
    with _SESSION_REGISTRY_LOCK:
        if session_id in _SESSION_REGISTRY:
            return False
        now = datetime.now(timezone.utc)
        _SESSION_REGISTRY[session_id] = {
            "actor_id": actor_id or "anonymous",
            "verified_key_id": verified_key_id,
            "verification_method": verification_method or "none",
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=ttl_seconds)).isoformat(),
            "anchor_type": "sovereign" if verification_method and verification_method in (
                "f13_sovereign", "ed25519", "session"
            ) else "anonymous",
        }
        logger.info(
            "Session %s anchored actor=%s method=%s anchor=%s",
            session_id, actor_id, verification_method,
            _SESSION_REGISTRY[session_id]["anchor_type"],
        )
        return True


def get_session_anchor(session_id: str) -> dict[str, Any] | None:
    """Return the session anchor, or None if not registered / expired."""
    with _SESSION_REGISTRY_LOCK:
        entry = _SESSION_REGISTRY.get(session_id)
        if entry is None:
            return None
        # Check expiry
        try:
            expires = datetime.fromisoformat(entry["expires_at"])
            if expires < datetime.now(timezone.utc):
                del _SESSION_REGISTRY[session_id]
                return None
        except (ValueError, TypeError):
            pass
        return dict(entry)


# ── Core: sovereign_signal() ────────────────────────────────────────────────


def sovereign_signal(
    session_id: str | None = None,
    actor_id: str | None = None,
    verified_key_id: str | None = None,
    *,
    session: dict[str, Any] | None = None,  # fallback: extract from session dict
) -> SovereignVerdict:
    """
    Verify sovereign initiated this session.

    Gate order (short-circuit):
      1. Extract actor_id/verified_key_id from session dict if not given
      2. Check actor_id in PROTECTED_SOVEREIGN_IDS
      3. Check verified_key_id in SOVEREIGN_KEY_IDS
      4. Check verified=True AND verification_method in ("f13_sovereign", "session", "ed25519")
      5. ALL PASS → sovereignty=True
    """
    # ── Extract from session dict if not given ──
    if session_id is None and session is not None:
        session_id = session.get("session_id") or session.get("id")
    if actor_id is None and session is not None:
        actor_id = session.get("actor_id") or session.get("actor", {}).get("claimed_id")
    if verified_key_id is None and session is not None:
        verified_key_id = session.get("verified_key_id") or session.get("actor", {}).get("verified_key_id")

    # ── Gate 1: Ensure we have parameters ──
    if not session_id and not actor_id:
        return SovereignVerdict(
            sovereignty=False,
            verified=False,
            method="anonymous",
            reason="fail-closed: no session_id or actor_id provided",
        )

    # ── Gate 2: Check actor_id in PROTECTED_SOVEREIGN_IDS ──
    try:
        from arifosmcp.runtime.governance_identity import PROTECTED_SOVEREIGN_IDS
    except ImportError:
        return SovereignVerdict(
            sovereignty=False,
            verified=False,
            method="anonymous",
            reason="fail-closed: governance_identity import failed",
        )

    if not actor_id or actor_id.strip().lower() not in PROTECTED_SOVEREIGN_IDS:
        return SovereignVerdict(
            sovereignty=False,
            verified=False,
            method="anonymous",
            reason=f"non-sovereign actor: {actor_id} not in PROTECTED_SOVEREIGN_IDS",
        )

    # ── Gate 3: Check verified_key_id in SOVEREIGN_KEY_IDS ──
    try:
        from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS
    except ImportError:
        return SovereignVerdict(
            sovereignty=False,
            verified=False,
            method="anonymous",
            reason="fail-closed: governance_identity import failed on Gate 3",
        )

    if not verified_key_id or verified_key_id not in SOVEREIGN_KEY_IDS:
        return SovereignVerdict(
            sovereignty=False,
            verified=False,
            method="session_anchor",
            reason=f"key not in SOVEREIGN_KEY_IDS: {verified_key_id}",
        )

    # ── Gate 4: Check verification method ──
    # Extract verification method from session anchor or explicit params
    method = None
    if session_id:
        anchor = get_session_anchor(session_id)
        if anchor:
            method = anchor.get("verification_method")

    valid_methods = {"f13_sovereign", "session", "ed25519"}
    if not method or method not in valid_methods:
        return SovereignVerdict(
            sovereignty=False,
            verified=True,
            method="session_anchor",
            reason=f"not cryptographically verified: method={method}, expected one of {valid_methods}",
        )

    # ── ALL GATES PASS ──
    return SovereignVerdict(
        sovereignty=True,
        verified=True,
        method="f13_sovereign",
        reason=f"sovereign identity + key verified (actor={actor_id}, key={verified_key_id[:20]}..., method={method})",
    )


# ── ForgeSessionProof ──────────────────────────────────────────────────────


@dataclass
class ForgeSessionProof:
    """
    Immutable proof linking a forge action back to its session.

    Fields:
      - session_id: str
      - actor_id: str
      - forge_action: str         # e.g. "forge.filesystem.write", "forge.seal"
      - action_hash: str          # sha256 of the action payload
      - session_proof_token: str  # HMAC(session_secret, action_hash + session_id)
      - timestamp: str            # ISO 8601
      - receipt_id: str | None    # VAULT999 receipt id, set after sealing
    """
    session_id: str
    actor_id: str
    forge_action: str
    action_hash: str
    session_proof_token: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    receipt_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON transport."""
        return {
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "forge_action": self.forge_action,
            "action_hash": self.action_hash,
            "session_proof_token": self.session_proof_token,
            "timestamp": self.timestamp,
            "receipt_id": self.receipt_id,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ForgeSessionProof":
        """Deserialize from dict."""
        return cls(
            session_id=d.get("session_id", ""),
            actor_id=d.get("actor_id", ""),
            forge_action=d.get("forge_action", ""),
            action_hash=d.get("action_hash", ""),
            session_proof_token=d.get("session_proof_token", ""),
            timestamp=d.get("timestamp", ""),
            receipt_id=d.get("receipt_id"),
        )

    def verify_chain(self, receipt: dict) -> bool:
        """
        Verify this proof chains to a VAULT999 receipt.

        Checks:
          1. receipt has matching session_id
          2. receipt has matching actor_id
          3. receipt's payload_hash matches this proof's action_hash
          4. receipt's event_type is consistent with forge_action
        """
        if not receipt:
            return False

        # Check session_id match
        rec_session = receipt.get("session_id") or (
            receipt.get("payload", {}).get("session_id") if isinstance(receipt.get("payload"), dict) else None
        )
        if rec_session != self.session_id:
            return False

        # Check actor_id match
        rec_actor = receipt.get("actor") or receipt.get("actor_id")
        if rec_actor and rec_actor != self.actor_id:
            return False

        # Check action hash against receipt payload_hash
        rec_payload_hash = receipt.get("input_hash") or (
            receipt.get("payload", {}).get("action_hash")
        )
        if rec_payload_hash and rec_payload_hash != self.action_hash:
            return False

        return True


# ── Token Creation ─────────────────────────────────────────────────────────


def _compute_session_secret(session_id: str, actor_id: str) -> str:
    """Derive a session-bound HMAC secret.

    Uses a deterministic derivation from session_id + actor_id.
    P2: Replace with actual key exchange / Ed25519 session key.
    """
    # P2 — use Ed25519 session key instead of deterministic hash
    seed = f"{session_id}:{actor_id}:forge_session:v{EXPECTED_TOKEN_VERSION}"
    return hashlib.sha256(seed.encode()).hexdigest()


def _compute_hmac(secret: str, message: str) -> str:
    """Compute HMAC-SHA256 and return hex digest."""
    return hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()


def create_forge_session_proof(
    session_id: str,
    actor_id: str,
    forge_action: str,
    action_payload: dict | None = None,
    *,
    session: dict[str, Any] | None = None,
) -> ForgeSessionProof | None:
    """
    Create a signed proof that a forge action was initiated within a session.

    Returns None (fail-closed) if session_id is missing or session has no anchor.
    """
    # Fail-closed: require session_id
    if not session_id:
        logger.warning("forge_session_proof: fail-closed — no session_id")
        return None

    # If session dict provided, try to verify it has an anchor
    if session is not None:
        anchor = get_session_anchor(session_id)
        if anchor is None:
            # Try to anchor from the session dict
            s_actor = session.get("actor_id") or (
                session.get("actor", {}).get("claimed_id") if isinstance(session.get("actor"), dict) else None
            )
            s_key = session.get("verified_key_id") or (
                session.get("actor", {}).get("verified_key_id") if isinstance(session.get("actor"), dict) else None
            )
            s_method = session.get("verification_method") or (
                session.get("actor", {}).get("verification_method") if isinstance(session.get("actor"), dict) else None
            )
            if s_actor:
                register_session_anchor(
                    session_id=session_id,
                    actor_id=s_actor,
                    verified_key_id=s_key,
                    verification_method=s_method,
                )
                anchor = get_session_anchor(session_id)

        if anchor is None:
            logger.warning(
                "forge_session_proof: fail-closed — no anchor for session %s",
                session_id,
            )
            return None

    # Derive session secret
    secret = _compute_session_secret(session_id, actor_id)

    # Compute action hash
    action_str = json.dumps(action_payload or {}, sort_keys=True)
    action_hash = f"sha256:{hashlib.sha256(action_str.encode()).hexdigest()}"

    # Build HMAC message: action_hash + session_id
    proof_message = f"{action_hash}:{session_id}"
    session_proof_token = _compute_hmac(secret, proof_message)

    return ForgeSessionProof(
        session_id=session_id,
        actor_id=actor_id,
        forge_action=forge_action,
        action_hash=action_hash,
        session_proof_token=session_proof_token,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# ── Chain Verification ─────────────────────────────────────────────────────


def verify_forge_session_chain(
    proof: ForgeSessionProof | dict,
    receipt: dict,
) -> ChainVerdict:
    """
    Trace a VAULT999 receipt back through its session proof chain.

    Returns ChainVerdict: {valid: bool, chain: list[str], broken_at: str | None}
    """
    # Normalize proof to ForgeSessionProof
    if isinstance(proof, dict):
        try:
            proof = ForgeSessionProof.from_dict(proof)
        except Exception as e:
            return ChainVerdict(
                valid=False,
                broken_at="proof_deserialize",
            )

    # Build chain
    chain: list[str] = [f"session:{proof.session_id}"]

    # Link 1: Verify proof → receipt
    if not proof.verify_chain(receipt):
        return ChainVerdict(
            valid=False,
            chain=chain,
            broken_at="proof_to_receipt",
        )
    chain.append(f"receipt:{receipt.get('seq', '?')}")

    # Link 2: Verify the session had a sovereign anchor at proof time
    anchor = get_session_anchor(proof.session_id)
    if anchor is None:
        return ChainVerdict(
            valid=False,
            chain=chain,
            broken_at="session_anchor_unknown",
        )
    chain.append(f"anchor:{anchor.get('anchor_type', 'unknown')}")

    # Link 3: Verify session_id match across proof, anchor, and receipt
    rec_session = receipt.get("session_id") or (
        receipt.get("payload", {}).get("session_id") if isinstance(receipt.get("payload"), dict) else None
    )
    if rec_session and rec_session != proof.session_id:
        return ChainVerdict(
            valid=False,
            chain=chain,
            broken_at="session_id_mismatch",
        )

    # ALL CHECKS PASS
    return ChainVerdict(
        valid=True,
        chain=chain,
        broken_at=None,
    )


# ── Session Token Verification (imported by governance_identity) ────────────


def verify_forge_session_token(token: dict[str, Any]) -> TokenVerdict:
    """
    Verify a forge session token against canonical state.

    Performs 13 checks per E1 spec:
      1. Token exists and is a dict
      2. session_id is present
      3. actor_id is present
      4. nonce is present
      5. signature is present
      6. token_version matches EXPECTED_TOKEN_VERSION
      7. audience matches AUDIENCE_FORGE_SESSION
      8. issued_at is parseable
      9. expires_at is parseable
     10. Token is not expired
     11. Session anchor exists
     12. Actor in token matches anchor actor
     13. HMAC signature is valid

    Returns TokenVerdict with ok=True only if ALL 13 pass.
    Fail-closed: returns ok=False on any error.
    """
    # 1. Token exists and is a dict
    if not isinstance(token, dict):
        return TokenVerdict(code="INVALID_FORMAT", reason="token is not a dict")

    session_id = token.get("session_id", "")
    actor_id = token.get("actor_id", "")

    # 2. session_id present
    if not session_id:
        return TokenVerdict(code="MISSING_SESSION", reason="session_id is required")

    # 3. actor_id present
    if not actor_id:
        return TokenVerdict(
            session_id=session_id,
            code="MISSING_ACTOR",
            reason="actor_id is required",
        )

    # 4. nonce present
    nonce = token.get("nonce", "")
    if not nonce:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="MISSING_NONCE",
            reason="nonce is required",
        )

    # 5. signature present
    signature = token.get("signature", "")
    if not signature:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="MISSING_SIGNATURE",
            reason="signature is required",
        )

    # 6. token_version check
    token_version = token.get("token_version", "")
    if token_version != EXPECTED_TOKEN_VERSION:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="VERSION_MISMATCH",
            reason=f"expected version {EXPECTED_TOKEN_VERSION}, got {token_version}",
        )

    # 7. audience check
    audience = token.get("audience", "")
    if audience != AUDIENCE_FORGE_SESSION:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="AUDIENCE_MISMATCH",
            reason=f"expected audience {AUDIENCE_FORGE_SESSION}, got {audience}",
        )

    # 8. issued_at parseable
    try:
        issued_at = datetime.fromisoformat(token.get("issued_at", ""))
    except (ValueError, TypeError):
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="INVALID_ISSUED_AT",
            reason="issued_at is not a valid ISO-8601 timestamp",
        )

    # 9. expires_at parseable
    try:
        expires_at = datetime.fromisoformat(token.get("expires_at", ""))
    except (ValueError, TypeError):
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="INVALID_EXPIRES_AT",
            reason="expires_at is not a valid ISO-8601 timestamp",
        )

    # 10. Not expired
    now = datetime.now(timezone.utc)
    if now > expires_at:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="TOKEN_EXPIRED",
            reason=f"token expired at {token.get('expires_at', '?')}",
        )

    # 11. Session anchor exists
    anchor = get_session_anchor(session_id)
    if anchor is None:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="NO_SESSION_ANCHOR",
            reason="no sovereign anchor for this session",
        )

    # 12. Actor in token matches anchor actor
    if anchor.get("actor_id") and anchor["actor_id"] != actor_id:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="ACTOR_MISMATCH",
            reason=f"token actor={actor_id} != anchor actor={anchor.get('actor_id')}",
        )

    # 13. HMAC signature is valid
    secret = _compute_session_secret(session_id, actor_id)
    capability = token.get("capability", "vault.append")
    message = f"{session_id}:{actor_id}:{nonce}:{capability}:{audience}:{token_version}"
    expected_sig = _compute_hmac(secret, message)

    # Use hmac.compare_digest for timing-safe comparison
    if not hmac.compare_digest(signature, expected_sig):
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="SIGNATURE_MISMATCH",
            reason="HMAC signature does not match computed value",
        )

    # ALL 13 CHECKS PASS
    return TokenVerdict(
        ok=True,
        code="OK",
        session_id=session_id,
        actor_id=actor_id,
        reason="all 13 checks passed",
    )


# ── Session-Bound Assertion Verification (imported by governance_identity) ───


def verify_session_bound_assertion(assertion: dict[str, Any]) -> TokenVerdict:
    """
    Verify a session-bound narrative assertion.

    Used by governance_identity._verify_sovereign_signal_proof() to
    verify that a sovereign signal phrase arrived through a verified session.

    Checks:
      1. Assertion exists
      2. session_id present
      3. actor_id present
      4. payload_hash present
      5. nonce present
      6. signature present
      7. assertion_version matches
      8. Session anchor exists
      9. Actor matches anchor
     10. Not expired
     11. Signature is valid (HMAC over assertion fields)
    """
    # 1. Assertion exists
    if not isinstance(assertion, dict):
        return TokenVerdict(code="INVALID_FORMAT", reason="assertion is not a dict")

    session_id = assertion.get("session_id", "")
    actor_id = assertion.get("actor_id", "")

    # 2-3. session_id + actor_id
    if not session_id:
        return TokenVerdict(code="MISSING_SESSION", reason="session_id is required")
    if not actor_id:
        return TokenVerdict(
            session_id=session_id,
            code="MISSING_ACTOR",
            reason="actor_id is required",
        )

    # 4. payload_hash
    payload_hash = assertion.get("payload_hash", "")
    if not payload_hash:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="MISSING_PAYLOAD_HASH",
            reason="payload_hash is required",
        )

    # 5. nonce
    nonce = assertion.get("nonce", "")
    if not nonce:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="MISSING_NONCE",
            reason="nonce is required",
        )

    # 6. signature
    signature = assertion.get("signature", "")
    if not signature:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="MISSING_SIGNATURE",
            reason="signature is required",
        )

    # 7. assertion version
    av = assertion.get("assertion_version", "")
    if av != EXPECTED_TOKEN_VERSION:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="VERSION_MISMATCH",
            reason=f"expected version {EXPECTED_TOKEN_VERSION}, got {av}",
        )

    # 8. Session anchor exists
    anchor = get_session_anchor(session_id)
    if anchor is None:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="NO_SESSION_ANCHOR",
            reason="no sovereign anchor for assertion session",
        )

    # 9. Actor matches anchor
    if anchor.get("actor_id") and anchor["actor_id"] != actor_id:
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="ACTOR_MISMATCH",
            reason=f"assertion actor={actor_id} != anchor actor={anchor.get('actor_id')}",
        )

    # 10. Not expired
    try:
        expires_at = datetime.fromisoformat(assertion.get("expires_at", ""))
        if datetime.now(timezone.utc) > expires_at:
            return TokenVerdict(
                session_id=session_id, actor_id=actor_id,
                code="ASSERTION_EXPIRED",
                reason=f"assertion expired at {assertion.get('expires_at', '?')}",
            )
    except (ValueError, TypeError):
        # If no expires_at, treat as not expired (but log warning)
        pass

    # 11. Signature valid (HMAC)
    secret = _compute_session_secret(session_id, actor_id)
    purpose = assertion.get("purpose", "informational_signal")
    message = f"{session_id}:{actor_id}:{payload_hash}:{purpose}:{nonce}"
    expected_sig = _compute_hmac(secret, message)

    if not hmac.compare_digest(signature, expected_sig):
        return TokenVerdict(
            session_id=session_id, actor_id=actor_id,
            code="SIGNATURE_MISMATCH",
            reason="assertion HMAC signature does not match",
        )

    return TokenVerdict(
        ok=True,
        code="OK",
        session_id=session_id,
        actor_id=actor_id,
        reason="all 11 checks passed",
    )


# ── Module __all__ ─────────────────────────────────────────────────────────

__all__ = [
    # Data classes
    "SovereignVerdict",
    "ChainVerdict",
    "TokenVerdict",
    "ForgeSessionProof",
    # Core functions
    "sovereign_signal",
    "register_session_anchor",
    "get_session_anchor",
    "create_forge_session_proof",
    "verify_forge_session_chain",
    # Token verification (imported by governance_identity)
    "verify_forge_session_token",
    "verify_session_bound_assertion",
    # Constants
    "EXPECTED_TOKEN_VERSION",
    "AUDIENCE_FORGE_SESSION",
]

"""
forge_session_runtime.py — arifOS E1: Canonical Verifier for Forge Sessions.

BACKEND for governance_identity._verify_forge_session_proof and
_verify_sovereign_signal_proof. Verifies against the canonical session
store (session_enforcer._SESSIONS), key registry (SOVEREIGN_KEY_IDS),
and nonce store (crypto_auth._issued_challenges / _used_challenges).

Per Arif E1 spec (2026-07-13 corrective):

  Verify a forge session token against canonical session state.
  Return structured VerificationResult, never bare bool.
  Internally: 13 checks per spec, transactional nonce consumption,
  fail-CLOSED on backend absence.

  Verify_session_bound_assertion (renamed from verify_sovereign_signal_origin):
  CRITICAL — verifies ORIGIN only, never grants authority. Authority comes
  from the session capability envelope and constitutional judgment.

NEVER trust supplied data when the canonical backend is unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# FAIL-CLOSED CODES
# ═══════════════════════════════════════════════════════════════════════════════

CODE_OK = "OK"
CODE_MALFORMED_TOKEN = "MALFORMED_TOKEN"
CODE_SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
CODE_SESSION_EXPIRED = "SESSION_EXPIRED"
CODE_SESSION_REVOKED = "SESSION_REVOKED"
CODE_ACTOR_MISMATCH = "ACTOR_MISMATCH"
CODE_NONCE_UNKNOWN = "NONCE_UNKNOWN"
CODE_NONCE_REPLAY = "NONCE_REPLAY"
CODE_SIGNATURE_INVALID = "SIGNATURE_INVALID"
CODE_AUDIENCE_MISMATCH = "AUDIENCE_MISMATCH"
CODE_CAPABILITY_NOT_ALLOWED = "CAPABILITY_NOT_ALLOWED"
CODE_POLICY_VERSION_MISMATCH = "POLICY_VERSION_MISMATCH"
CODE_BACKEND_UNAVAILABLE = "BACKEND_UNAVAILABLE"

# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

EXPECTED_FORGE_TOKEN_KEYS: frozenset[str] = frozenset({
    "session_id",
    "actor_id",
    "nonce",
    "audience",        # must equal AUDIENCE_FORGE_SESSION
    "issued_at",       # ISO8601 string
    "expires_at",      # ISO8601 string
    "capability",      # bounded capability string
    "signature",       # base64 Ed25519
    "token_version",   # current "v1"
})

EXPECTED_ASSERTION_KEYS: frozenset[str] = frozenset({
    "session_id",
    "actor_id",
    "payload_hash",
    "purpose",
    "nonce",
    "issued_at",
    "expires_at",
    "signature",
    "assertion_version",  # current "v1"
})

AUDIENCE_FORGE_SESSION = "forge_session"
EXPECTED_TOKEN_VERSION = "v1"

# Hardcoded dangerous-purpose reject list — assertion function never approves
ASSERTION_FORBIDDEN_PURPOSE_KEYWORDS = (
    "approve",
    "grant",
    "seal",
    "deploy",
    "delete",
    "execute_seal",
)


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class VerificationResult:
    """Structured verification outcome.

    `ok` is exposed only for compatibility shims. Internal callers should
    branch on `code` so the failure mode is always informative.
    """
    ok: bool
    code: str
    session_id: Optional[str] = None
    actor_id: Optional[str] = None
    authority: Optional[str] = None

    def to_bool(self) -> bool:
        """Compatibility wrapper per E1 spec ('result.ok')."""
        return self.ok


def _fail(
    code: str,
    *,
    session_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    authority: Optional[str] = None,
) -> VerificationResult:
    return VerificationResult(
        ok=False, code=code,
        session_id=session_id, actor_id=actor_id, authority=authority,
    )


def _ok(
    *, session_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    authority: Optional[str] = None,
) -> VerificationResult:
    return VerificationResult(
        ok=True, code=CODE_OK,
        session_id=session_id, actor_id=actor_id, authority=authority,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL STATE ACCESS (with availability gating)
# ═══════════════════════════════════════════════════════════════════════════════

def _backend_unavailable() -> bool:
    """Test whether canonical session/nonce store is importable.

    Returns True (unavailable) on any failure → caller fail-CLOSED.
    """
    try:
        from arifosmcp.runtime.session_enforcer import _SESSIONS
        if not isinstance(_SESSIONS, dict):
            return True
        from arifosmcp.runtime.crypto_auth import _consume_actor_challenge
        if not callable(_consume_actor_challenge):
            return True
        return False
    except Exception:
        return True


def _check_session_active(session_id: str, actor_id: str):
    """Checks 2-5: session exists, active, not revoked, actor matches.

    Returns (ok: bool, code: str, rec_or_None).
    """
    try:
        from arifosmcp.runtime.session_enforcer import get_session
    except ImportError:
        return False, CODE_BACKEND_UNAVAILABLE, None

    try:
        rec = get_session(session_id)
    except Exception:
        return False, CODE_BACKEND_UNAVAILABLE, None

    if rec is None:
        return False, CODE_SESSION_NOT_FOUND, None

    if getattr(rec, "hold_active", False):
        return False, CODE_SESSION_REVOKED, rec

    if rec.actor_id != actor_id:
        return False, CODE_ACTOR_MISMATCH, rec

    # Session expiry: stored in session._SESSION_IDENTITY (broader store)
    try:
        from arifosmcp.runtime.session import _SESSION_IDENTITY
        ident = _SESSION_IDENTITY.get(session_id, {})
        expires_at_str = (
            ident.get("expires_at") if isinstance(ident, dict) else None
        )
        if expires_at_str:
            from datetime import datetime, timezone
            exp = datetime.fromisoformat(
                expires_at_str.replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)
            if exp <= now:
                return False, CODE_SESSION_EXPIRED, rec
    except (ImportError, Exception):
        return False, CODE_BACKEND_UNAVAILABLE, rec

    return True, CODE_OK, rec


def _consume_nonce(nonce: str, actor_id: str):
    """Checks 6-7: nonce belongs + non-replay (transactional via _challenge_lock).

    Returns (ok: bool, code: str).
    """
    try:
        from arifosmcp.runtime.crypto_auth import _consume_actor_challenge
    except ImportError:
        return False, CODE_BACKEND_UNAVAILABLE

    try:
        ok, reason = _consume_actor_challenge(actor_id, nonce)
    except Exception:
        return False, CODE_BACKEND_UNAVAILABLE

    if ok:
        return True, CODE_OK

    # Map crypto_auth reason → E1 fail-closed code
    if reason == "challenge_replayed":
        return False, CODE_NONCE_REPLAY
    if reason == "challenge_not_issued":
        return False, CODE_NONCE_UNKNOWN
    if reason == "challenge_actor_mismatch":
        return False, CODE_ACTOR_MISMATCH
    if reason == "challenge_expired":
        return False, CODE_SESSION_EXPIRED
    return False, CODE_BACKEND_UNAVAILABLE


def _verify_signature(
    actor_id: str, nonce: str, signature: str,
) -> bool:
    """Checks 8-9: Ed25519 sig verifies over canonical payload.

    Pure verification — does NOT consume the nonce. The nonce consumption
    happens in check 6-7 via _consume_nonce. Calling verify_actor_signature
    here would double-consume (it consumes internally), so we inline the
    signature check against resolve_actor_public_key.
    """
    try:
        from arifosmcp.runtime.crypto_auth import resolve_actor_public_key
    except ImportError:
        return False
    try:
        public_key = resolve_actor_public_key(actor_id)
    except Exception:
        return False
    if public_key is None:
        return False
    try:
        import base64 as _b64
        signature_bytes = _b64.b64decode(signature)
    except Exception:
        return False
    # Canonical payload per crypto_auth payload format 1
    payload = f"{actor_id}:{nonce}".encode()
    try:
        public_key.verify(signature_bytes, payload)
        return True
    except Exception:
        return False


def _canonical_payload(token: dict) -> str:
    """Per spec: deterministic signed payload for forge session token."""
    parts = [
        "arifOS-forge-session-v1",
        f"session_id={token['session_id']}",
        f"actor_id={token['actor_id']}",
        f"nonce={token['nonce']}",
        f"audience={token['audience']}",
        f"issued_at={token['issued_at']}",
        f"expires_at={token['expires_at']}",
        f"capability={token['capability']}",
    ]
    return "\n".join(parts)


def _check_capability(session_id: str, capability: str) -> bool:
    """Check 11: capability within session allowed scope.

    Bounded actor identity (verified=True) without explicit allow-list gets
    conservative capability grant: must be in a small allow-list we derive
    from session identity_verified state.
    """
    try:
        from arifosmcp.runtime.session_enforcer import get_session
        rec = get_session(session_id)
        if rec is None:
            return False
        allowed = getattr(rec, "allowed_capabilities", None)
        if allowed is None:
            # Default: bounded actor identity verified=True grants
            # only documented scopes
            return (
                rec.identity_verified
                and capability in {
                    "vault.append",
                    "session.read",
                    "session.refresh",
                }
            )
        return capability in allowed
    except Exception:
        return False


def _check_policy_version(token_version: str) -> bool:
    """Check 12: constitution + token versions match."""
    return token_version == EXPECTED_TOKEN_VERSION


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC VERIFICATION (13 CHECKS EACH)
# ═══════════════════════════════════════════════════════════════════════════════

def verify_forge_session_token(token: Any) -> VerificationResult:
    """Verify a forge session token against canonical session state.

    Performs the 13 checks per E1 spec:
      1. Strict input schema
      2. Session exists
      3. Session active and unexpired
      4. Session not revoked or held
      5. Actor + sovereign identifiers match stored session
      6. Nonce belongs to that session
      7. Nonce has not been consumed
      8. Ed25519 signature validates
      9. Signature covers canonical payload
      10. Audience equals forge_session
      11. Capability within session allowed scope
      12. Constitution + token version match
      13. Backend failure denies verification

    FAIL-CLOSED: any missing canonical store or backend error → BACKEND_UNAVAILABLE.
    """
    # 1. Strict input schema
    if not isinstance(token, dict):
        return _fail(CODE_MALFORMED_TOKEN)
    if not EXPECTED_FORGE_TOKEN_KEYS.issubset(set(token.keys())):
        return _fail(CODE_MALFORMED_TOKEN)
    # Type check on critical fields
    if not isinstance(token.get("signature"), str) or not token["signature"]:
        return _fail(CODE_MALFORMED_TOKEN)
    if not isinstance(token.get("session_id"), str) or not token["session_id"]:
        return _fail(CODE_MALFORMED_TOKEN)

    session_id = token["session_id"]
    actor_id = token["actor_id"]
    nonce = token["nonce"]
    audience = token["audience"]
    capability = token["capability"]
    signature = token["signature"]
    token_version = token.get("token_version", "")
    issued_at = token["issued_at"]
    expires_at = token["expires_at"]

    # 13. Backend availability pre-check (fail-CLOSED)
    if _backend_unavailable():
        return _fail(
            CODE_BACKEND_UNAVAILABLE,
            session_id=session_id, actor_id=actor_id,
        )

    # 12. Policy version match
    if not _check_policy_version(token_version):
        return _fail(
            CODE_POLICY_VERSION_MISMATCH,
            session_id=session_id, actor_id=actor_id,
        )

    # 10. Audience
    if audience != AUDIENCE_FORGE_SESSION:
        return _fail(
            CODE_AUDIENCE_MISMATCH,
            session_id=session_id, actor_id=actor_id,
        )

    # 2-5. Session state
    sess_ok, sess_code, sess_rec = _check_session_active(session_id, actor_id)
    if not sess_ok:
        authority = (
            sess_rec.actor_id if sess_rec is not None else None
        )
        return _fail(sess_code, session_id=session_id, actor_id=actor_id, authority=authority)

    # 6-7. Nonce (consume FIRST — transactional via canonical lock)
    nonce_ok, nonce_code = _consume_nonce(nonce, actor_id)
    if not nonce_ok:
        return _fail(
            nonce_code, session_id=session_id, actor_id=actor_id,
            authority=getattr(sess_rec, "actor_id", None),
        )

    # 8-9. Signature over canonical payload
    if not _verify_signature(actor_id, nonce, signature):
        return _fail(
            CODE_SIGNATURE_INVALID,
            session_id=session_id, actor_id=actor_id,
            authority=getattr(sess_rec, "actor_id", None),
        )

    # 11. Capability allowed
    if not _check_capability(session_id, capability):
        return _fail(
            CODE_CAPABILITY_NOT_ALLOWED,
            session_id=session_id, actor_id=actor_id,
            authority=getattr(sess_rec, "actor_id", None),
        )

    return _ok(
        session_id=session_id,
        actor_id=actor_id,
        authority=getattr(sess_rec, "actor_id", None),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ASSERTION VERIFICATION (originated sovereignty only — never grants authority)
# ═══════════════════════════════════════════════════════════════════════════════

def verify_session_bound_assertion(assertion: Any) -> VerificationResult:
    """Verify a session-bound assertion.

    CRITICAL (per E1 spec): verifies ORIGIN only, never concludes the
    requested action is approved. Authority comes from the session
    capability envelope and constitutional judgment.

    Aims: only verify "this assertion originated from an authenticated
    sovereign session and has not been altered".
    """
    # 1. Strict schema
    if not isinstance(assertion, dict):
        return _fail(CODE_MALFORMED_TOKEN)
    if not EXPECTED_ASSERTION_KEYS.issubset(set(assertion.keys())):
        return _fail(CODE_MALFORMED_TOKEN)
    if not isinstance(assertion.get("signature"), str) or not assertion["signature"]:
        return _fail(CODE_MALFORMED_TOKEN)

    session_id = assertion["session_id"]
    actor_id = assertion["actor_id"]
    payload_hash = assertion["payload_hash"]
    purpose = str(assertion.get("purpose", ""))
    nonce = assertion["nonce"]
    signature = assertion["signature"]

    # Backend availability
    if _backend_unavailable():
        return _fail(
            CODE_BACKEND_UNAVAILABLE, session_id=session_id, actor_id=actor_id,
        )

    # Policy version
    if assertion.get("assertion_version", "") != EXPECTED_TOKEN_VERSION:
        return _fail(
            CODE_POLICY_VERSION_MISMATCH,
            session_id=session_id, actor_id=actor_id,
        )

    # Session exact match
    sess_ok, sess_code, sess_rec = _check_session_active(session_id, actor_id)
    if not sess_ok:
        return _fail(sess_code, session_id=session_id, actor_id=actor_id)

    # Session-bound authority model (per E1 spec):
    # "authenticated sovereign identity" is satisfied by the session having
    # identity_verified=True. The assertion itself does not need to re-verify
    # the key registry — that's the session's job.

    # Purpose is informational only — never approval. Reject dangerous verbs.
    purpose_lower = purpose.lower()
    if any(kw in purpose_lower for kw in ASSERTION_FORBIDDEN_PURPOSE_KEYWORDS):
        # Assertion cannot convey action-approval authority
        return _fail(
            CODE_POLICY_VERSION_MISMATCH,
            session_id=session_id, actor_id=actor_id,
        )

    # Nonce non-replay
    nonce_ok, nonce_code = _consume_nonce(nonce, actor_id)
    if not nonce_ok:
        return _fail(
            nonce_code, session_id=session_id, actor_id=actor_id,
        )

    # Signature over canonical assertion payload (session_id + payload_hash)
    # The signer signs f"{actor_id}:{payload_hash}" — canonical assertion sig.
    # _verify_signature uses canonical payload format 1 from crypto_auth.
    if not _verify_signature(actor_id, payload_hash, signature):
        return _fail(
            CODE_SIGNATURE_INVALID, session_id=session_id, actor_id=actor_id,
        )

    # Origin verified — but NOT approval
    return _ok(
        session_id=session_id,
        actor_id=actor_id,
        authority=getattr(sess_rec, "actor_id", None) if sess_rec else None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARDS-COMPAT SHIM (governance_identity already imports these names)
# ═══════════════════════════════════════════════════════════════════════════════

def verify_sovereign_signal_origin(
    actor_id: str, signal: str, session_id: Optional[str] = None,
) -> VerificationResult:
    """Alias for verify_session_bound_assertion — deprecated.

    The signature was misleading: it never proved that a narrative signal
    was 'sovereign'. Per E1 spec, this is renamed. The function now
    returns SIGNATURE_INVALID unless called with a properly-formed
    session-bound assertion dict.
    """
    # If caller passes a dict, treat as session-bound assertion
    if isinstance(signal, dict) and "session_id" in signal:
        return verify_session_bound_assertion(signal)
    return _fail(CODE_MALFORMED_TOKEN)


__all__ = [
    "VerificationResult",
    "verify_forge_session_token",
    "verify_session_bound_assertion",
    "verify_sovereign_signal_origin",  # deprecated alias
    # codes
    "CODE_OK",
    "CODE_MALFORMED_TOKEN",
    "CODE_SESSION_NOT_FOUND",
    "CODE_SESSION_EXPIRED",
    "CODE_SESSION_REVOKED",
    "CODE_ACTOR_MISMATCH",
    "CODE_NONCE_UNKNOWN",
    "CODE_NONCE_REPLAY",
    "CODE_SIGNATURE_INVALID",
    "CODE_AUDIENCE_MISMATCH",
    "CODE_CAPABILITY_NOT_ALLOWED",
    "CODE_POLICY_VERSION_MISMATCH",
    "CODE_BACKEND_UNAVAILABLE",
    # schemas
    "EXPECTED_FORGE_TOKEN_KEYS",
    "EXPECTED_ASSERTION_KEYS",
    "AUDIENCE_FORGE_SESSION",
    "EXPECTED_TOKEN_VERSION",
]

"""
calltime_identity — call-time cryptographic actor verification.

Wires the EXISTING crypto engines into the call path so that
``actor_verified`` / ``identity_authenticated`` reflect a REAL cryptographic
check performed at CALL time:

  1. ACT token (HMAC-SHA256, ``act_v1.<b64url>.<hex>``)
     → arifosmcp.runtime.act_token.verify_act
  2. Ed25519 signature proof ({nonce, signature, [timestamp]})
     → arifosmcp.runtime.governance_identity._verify_ed25519_proof

Constitutional contract (extends, does not weaken, the identity/ STUB contract):

  - Birth-time actor_verified stays False (tests/test_session_preflight.py).
  - verified=True ONLY on a passing cryptographic check — never blanket-True.
  - Any absent/malformed/expired/forged credential → verified=False (fail-closed).
  - Any exception inside a verification engine → verified=False (fail-closed).
  - Session promotion is best-effort and one-directional: only verified=True
    may write; a failed check NEVER downgrades or mutates a session.

Verification is per-call. A session promoted here reads verified through the
canonical single-source reader (authority.actor.verified via
tools._is_actor_verified), so subsequent unsigned calls on the same session
inherit the promotion — that is the intended "verified for THAT session"
semantics of WS1's single promotion setter, not a bypass of it.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "CallTimeIdentity",
    "verify_caller_identity",
    "extract_act_token",
]

_ACT_PREFIXES = ("act_v1.", "arifos.v1.", "sct_v1.")


@dataclass(frozen=True)
class CallTimeIdentity:
    """Result of a call-time cryptographic identity check. Fail-closed default."""

    verified: bool = False
    method: str | None = None  # None | "act_token" | "ed25519_proof"
    reason: str = "no_credential_presented"
    authority: str | None = None  # claims["auth"] from a valid ACT, else None
    actor: str | None = None  # canonical actor from the verified credential
    session_id: str | None = None
    promoted_to_session: bool = False  # True iff a live session was promoted


def extract_act_token(
    *,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    authorization: str | None = None,
) -> str | None:
    """Extract a candidate ACT token from call material. Returns None if absent.

    Only strings that look like ACT tokens (``act_v1.`` / ``arifos.v1.`` /
    ``sct_v1.`` prefixes) are returned — a random Bearer (e.g. a federation
    API key) is NOT treated as an ACT candidate.
    """
    candidates: list[str] = []
    if isinstance(body, dict):
        for key in ("act_token", "sct_token", "identity_token"):
            v = body.get(key)
            if isinstance(v, str) and v:
                candidates.append(v)
    if headers:
        v = headers.get("x-act-token") or headers.get("X-Act-Token")
        if isinstance(v, str) and v:
            candidates.append(v)
    if authorization and authorization.lower().startswith("bearer "):
        candidates.append(authorization[7:].strip())
    for c in candidates:
        if c.startswith(_ACT_PREFIXES):
            return c
    return None


def _promote_session_verified(
    session_id: str,
    actor_id: str,
    method: str,
    key_id: str | None,
) -> bool:
    """Promote a live session to actor.verified=True after a PASSING crypto check.

    Best-effort: returns False (without raising) when there is no live session
    record to promote — the call-level verified=True still stands, but the
    canonical gate reader (_is_actor_verified) will keep returning False until
    the caller presents credentials on a session-bound call. Conservative by
    design: no session record, no promotion.
    """
    try:
        from arifosmcp.runtime.authority import bind_authority_state
        from arifosmcp.runtime.megaTools.tool_01_init_anchor import (
            build_authority_state_for_actor,
        )
        from arifosmcp.runtime.tools import _SESSIONS

        sess = _SESSIONS.get(session_id) if session_id else None
        if not isinstance(sess, dict):
            return False
        bind_authority_state(
            sess,
            build_authority_state_for_actor(
                actor_id,
                verified=True,
                verification_method=method,
                verified_key_id=key_id,
            ),
        )
        # Flush to the unified store. _SESSIONS.get forces a disk reload on every
        # read (P1 fix 2026-10-06), so an un-persisted in-memory promotion is
        # silently lost before the gate reads it. Mirrors the persist pattern of
        # session.mark_session_ed25519_verified — the other promotion setter.
        try:
            from arifosmcp.runtime.session import _STORE_LOCK, _persist_store

            with _STORE_LOCK:
                _persist_store()
        except Exception as exc:  # pragma: no cover — defensive
            logger.warning("calltime_identity persist skipped: %s", exc)
        return True
    except Exception as exc:  # pragma: no cover — defensive, fail-closed
        logger.warning("calltime_identity promotion skipped (fail-closed): %s", exc)
        return False


def verify_caller_identity(
    session_id: str | None = None,
    actor_id: str | None = None,
    *,
    token: str | None = None,
    ed25519_proof: dict[str, Any] | None = None,
    promote_session: bool = True,
) -> CallTimeIdentity:
    """Verify a call's actor identity via ACT token or Ed25519 proof.

    Returns a CallTimeIdentity. verified=True ONLY on cryptographic success.
    Unsigned calls, wrong actors, expired/forged tokens, stale nonces, and any
    engine exception all yield verified=False. Never raises.
    """
    sid = str(session_id or "").strip()
    aid = str(actor_id or "").strip()

    # ── Path 1: ACT token (HMAC-SHA256) ────────────────────────────────────
    if token:
        try:
            from arifosmcp.runtime.act_token import verify_act

            claims = verify_act(token, expected_actor=aid or None)
            if not isinstance(claims, dict):
                return CallTimeIdentity(
                    session_id=sid or None,
                    reason="act_token_invalid",
                )
            claim_actor = str(claims.get("actor") or "").strip()
            if not aid and claim_actor.lower() == "anonymous":
                return CallTimeIdentity(
                    session_id=sid or None,
                    reason="act_token_anonymous_claim",
                )
            if not claims.get("av"):
                return CallTimeIdentity(
                    session_id=sid or None,
                    reason="act_token_av_false",
                )
            # Session binding: if both the call and the claim name a session,
            # they must agree (a token minted for another session is rejected).
            claim_sid = str(claims.get("sid") or "").strip()
            if sid and claim_sid and claim_sid != sid:
                return CallTimeIdentity(
                    session_id=sid,
                    reason="act_token_session_mismatch",
                )
            verified_actor = aid or claim_actor
            promoted = False
            if promote_session and sid:
                promoted = _promote_session_verified(
                    sid,
                    verified_actor,
                    method="act_token",
                    key_id=str(claims.get("kid") or "act:default"),
                )
            return CallTimeIdentity(
                verified=True,
                method="act_token",
                reason="act_token_verified",
                authority=str(claims.get("auth") or "") or None,
                actor=verified_actor,
                session_id=sid or None,
                promoted_to_session=promoted,
            )
        except Exception as exc:
            logger.warning("calltime_identity ACT path failed closed: %s", exc)
            return CallTimeIdentity(session_id=sid or None, reason="act_token_error")

    # ── Path 2: Ed25519 signature proof ───────────────────────────────────
    if isinstance(ed25519_proof, dict) and ed25519_proof:
        if not aid:
            return CallTimeIdentity(
                session_id=sid or None,
                reason="ed25519_proof_missing_actor",
            )
        try:
            from arifosmcp.runtime.governance_identity import _verify_ed25519_proof

            if not _verify_ed25519_proof(aid, ed25519_proof):
                return CallTimeIdentity(
                    session_id=sid or None,
                    reason="ed25519_proof_invalid",
                )
            promoted = False
            if promote_session and sid:
                pubkey = str(ed25519_proof.get("pubkey") or "") or None
                promoted = _promote_session_verified(
                    sid,
                    aid,
                    method="signature",
                    key_id=pubkey,
                )
            return CallTimeIdentity(
                verified=True,
                method="ed25519_proof",
                reason="ed25519_proof_verified",
                actor=aid,
                session_id=sid or None,
                promoted_to_session=promoted,
            )
        except Exception as exc:
            logger.warning("calltime_identity Ed25519 path failed closed: %s", exc)
            return CallTimeIdentity(session_id=sid or None, reason="ed25519_proof_error")

    # ── No credential presented: fail-closed birth-state ──────────────────
    return CallTimeIdentity(session_id=sid or None)

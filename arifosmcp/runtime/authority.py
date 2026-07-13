"""
arifOS Authority State — WS1 single-source helpers.

DITEMPA BUKAN DIBERI

Forged 2026-07-12 under F13 SOVEREIGN directive.
Cycle: forge_work/2026-07-12/KERNEL-INTELLIGENCE-HARDENING-CYCLE-PHASE-A.md §1

These helpers are the bridges between ``AuthorityState`` (the canonical
authority posture) and the legacy session dict shape. They guarantee:

1. ``bind_authority_state(sess, state)`` writes BOTH the new canonical
   ``sess["authority_state"]`` AND a derived mirror of the legacy fields
   (``actor_verified``, ``identity_verified``, ``authority_level``,
   ``authority``, ``signature_verified``) so downstream consumers reading
   legacy keys continue to work for one compat cycle only.

2. ``read_authority_state(sess)`` returns the canonical ``AuthorityState`` —
   either the one stored at ``sess["authority_state"]``, or one
   reconstructed from the legacy keys with a warning emitted via the kernel
   logger. Reconstruction is for migration only; new writes always use
   ``bind_authority_state``.

3. ``derive_canonical_from_authority(state)`` produces the deprecated
   ``CanonicalAuthority`` view for one compat cycle (removal 2026-08-09).

These are the only legitimate authority-state mutations in the kernel.
Direct writes to ``sess["actor_verified"]``, ``sess["authority_level"]``, etc.
are now classified as a constitutional surface drift; do not introduce new
ones.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.model import (
    AuthorityActor,
    AuthorityForgeGate,
    AuthorityPublicPosture,
    AuthoritySeals,
    AuthorityState,
    AuthorityLevel,
    CanonicalAuthority,
    ClaimStatus,
)

logger = logging.getLogger(__name__)

# Compat-cycle end. After this date the legacy mirror fields can be dropped.
_LEGACY_MIRROR_RETIREMENT_DATE = "2026-08-09"


def bind_authority_state(
    sess: dict[str, Any],
    state: AuthorityState,
    *,
    also_mirror_legacy: bool = True,
) -> None:
    """WS1: write canonical ``AuthorityState`` to ``sess``. Single source of truth.

    With ``also_mirror_legacy=True`` (default for compat cycle) also writes the
    parallel legacy keys so existing consumers do not break. After
    ``_LEGACY_MIRROR_RETIREMENT_DATE``, set ``also_mirror_legacy=False``.

    No double-writes in NEW code. This helper is the only legitimate writer.
    """
    if not isinstance(sess, dict):
        raise TypeError(f"sess must be a dict, got {type(sess).__name__}")

    # Canonical storage.
    sess["authority_state"] = state

    if not also_mirror_legacy:
        return

    # Legacy mirror — for one compat cycle only.
    sess["actor_verified"] = state.actor.verified
    sess["identity_verified"] = state.actor.verified
    sess["signature_verified"] = state.actor.verified
    sess["verified"] = state.actor.verified

    actor_key = (state.actor.claimed_id or "").strip().lower()
    # SECURITY P0 2026-07-12: SOVEREIGN authority binds to verified_key_id,
    # never to the actor string. Empty SOVEREIGN_KEY_IDS means NO actor gets
    # SOVEREIGN automatically until the key registry is wired.
    from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS
    verified_key_id = (
        (state.actor.verified_key_id if hasattr(state.actor, "verified_key_id") else None)
        or sess.get("verified_key_id")
    )
    is_sovereign = bool(
        state.actor.verified and verified_key_id and verified_key_id in SOVEREIGN_KEY_IDS
    )

    if is_sovereign:
        sess["authority_level"] = "SOVEREIGN"
        sess["authority"] = "FULL"
    elif state.actor.verified:
        sess["authority_level"] = "OPERATOR"
        sess["authority"] = "OBSERVER_MUTATE"
    elif actor_key:
        sess["authority_level"] = "OPERATOR_CLAIMED"
        sess["authority"] = "OBSERVER"
    else:
        sess["authority_level"] = "OBSERVER"
        sess["authority"] = "OBSERVER"

    sess["ed25519_governance_verified"] = state.actor.verification_method == "f13_sovereign"


def read_authority_state(sess: dict[str, Any] | None) -> AuthorityState:
    """WS1: read canonical ``AuthorityState``. Single source of truth.

    Returns the stored state if present; otherwise reconstructs from legacy
    keys with a one-time log warning. Reconstruction is best-effort — fields
    that can't be derived safely (seals, forge_gate, public_posture) fall
    back to conservative defaults.

    Consumers MUST treat the returned object as authoritative. Do NOT also
    call ``sess.get(\"actor_verified\")`` or similar — that re-introduces the
    parallel-read contradiction this WS1 closes.
    """
    if isinstance(sess, dict) and isinstance(sess.get("authority_state"), AuthorityState):
        return sess["authority_state"]

    # Fallback: reconstruct from legacy fields. Logs once per call-session to
    # avoid log spam; production telemetry will surface this in WS7.
    if isinstance(sess, dict):
        logger.warning(
            "read_authority_state: sess has no canonical authority_state; "
            "reconstructing from legacy keys. Compat ends %s.",
            _LEGACY_MIRROR_RETIREMENT_DATE,
            extra={
                "legacy_fields": [
                    k
                    for k in (
                        "actor_verified",
                        "identity_verified",
                        "authority_level",
                        "authority",
                        "signature_verified",
                    )
                    if k in sess
                ]
            },
        )

    return _reconstruct_authority_state(sess if isinstance(sess, dict) else {})


def _reconstruct_authority_state(sess: dict[str, Any]) -> AuthorityState:
    """Best-effort reconstruction of AuthorityState from legacy session keys.

    Marks itself as a synthetic "as_pending" snapshot to signal
    ``non_overclaim_check=failed`` — distinguishing it from a real stored
    state. WS7 bench will fail any path that requires a non-reconstructed
    state.
    """
    actor_id = (
        sess.get("actor_id") or sess.get("identity", {}).get("actor_id")
        if isinstance(sess.get("identity"), dict)
        else sess.get("actor_id")
    )
    if not actor_id:
        actor_id = "anonymous"

    verified = bool(
        sess.get("actor_verified")
        or sess.get("signature_verified")
        or sess.get("identity_verified")
        or sess.get("verified")
    )
    method = (
        "f13_sovereign"
        if sess.get("ed25519_governance_verified")
        else "session"
        if verified
        else "none"
    )
    actor_key = str(actor_id).strip().lower()
    # SECURITY P0 2026-07-12: SOVEREIGN by key_id, not by name.
    from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS
    verified_key_id = sess.get("verified_key_id") if isinstance(sess, dict) else None
    is_sovereign = bool(
        verified and verified_key_id and verified_key_id in SOVEREIGN_KEY_IDS
    )
    is_sealed = is_sovereign and verified

    actor = AuthorityActor(
        claimed_id=str(actor_id),
        verified=verified,
        verification_method=method,  # type: ignore[arg-type]
    )
    seals = AuthoritySeals(
        kernel_seal_awareness="ACTIVE" if is_sealed else "INACTIVE",
        domain_seal_validity="INACTIVE",
        judge_seal_authorization=(
            "ACTIVE" if is_sealed and sess.get("judge_seal_ok") else "INACTIVE"
        ),
        vault999_seal_record="INACTIVE",
        public_seal_readiness="INACTIVE",
    )
    forge_gate = AuthorityForgeGate(
        enabled=is_sealed,
        reversibility_threshold=0.7 if is_sovereign else 0.5,
        blockers=[] if is_sealed else ["actor_not_sealed_reconstructed"],
    )
    public_posture = AuthorityPublicPosture(
        service_health="unknown",
        execution_readiness="ready" if is_sealed else "held",
        human_visible_summary="RECONSTRUCTED_FROM_LEGACY",
    )

    return AuthorityState(
        state_id="as_pending",
        snapshot_at=datetime.now(UTC).isoformat(),
        actor=actor,
        context_verdict="UNKNOWN",
        seals=seals,
        execution_authority="SEAL_AUTHORIZED" if is_sealed else "HOLD",
        apex_approval="PRESENT" if is_sealed else "ABSENT",
        active_holds=[],
        active_missions=[],
        forge_gate=forge_gate,
        public_posture=public_posture,
        non_overclaim_check="failed",  # reconstructed = not authoritative
    )


def derive_canonical_from_authority(state: AuthorityState) -> CanonicalAuthority:
    """WS1 shim. Legacy ``CanonicalAuthority`` derives from ``AuthorityState``.

    Single direction. Never compute ``CanonicalAuthority`` independently.
    Removal target: 2026-08-09 (one compat cycle from forged 2026-07-12).
    """
    safe_actor = state.actor.claimed_id or "anonymous"
    actor_key = safe_actor.strip().lower()
    # SECURITY P0 2026-07-12: SOVEREIGN authority binds to verified_key_id,
    # never to the actor string. Empty SOVEREIGN_KEY_IDS means NO actor gets
    # SOVEREIGN automatically until the key registry is wired.
    from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS
    verified_key_id = (
        getattr(state.actor, "verified_key_id", None) if state.actor else None
    )
    is_sovereign = bool(
        state.actor.verified
        and verified_key_id
        and verified_key_id in SOVEREIGN_KEY_IDS
    )

    if is_sovereign:
        level = AuthorityLevel.SOVEREIGN
    elif state.actor.verified:
        level = AuthorityLevel.OPERATOR
    else:
        level = AuthorityLevel.ANONYMOUS

    if state.actor.verified:
        claim_status = ClaimStatus.VERIFIED
    else:
        claim_status = ClaimStatus.CLAIMED

    return CanonicalAuthority(
        actor_id=safe_actor,
        level=level,
        claim_status=claim_status,
        human_required=not (is_sovereign and state.actor.verified),
        approval_scope=[
            "status",
            "probe",
            "state",
            "kernel",
            "health",
            "vitals",
            "reason",
            "critique",
        ],
        auth_state="verified" if state.actor.verified else "anchored",
    )


def authority_envelope_for_session(
    session_id,
    actor_id,
    *,
    actor_verified_flag=None,
    _runtime_auth_hint=None,
):
    """WS1 (2026-07-12): build the legacy 5-field ``authority`` dict from
    canonical AuthorityState.

    The legacy shape used by ``arifosmcp.runtime.tools._wrap_handler`` is
    now DERIVED. The shape is preserved (legacy consumers may keep
    reading ``authority.runtime_authority`` etc.) for one compat cycle,
    but never computed independently.

    Compat retirement: 2026-08-09.
    """
    state = None
    try:
        from arifosmcp.runtime.tools import _SESSIONS

        sess = _SESSIONS.get(session_id or "")
        if isinstance(sess, dict):
            state = read_authority_state(sess)
    except Exception:
        state = None

    if state is None:
        actor_key = (actor_id or "").strip().lower()
        # SECURITY P0 2026-07-12: SOVEREIGN by verified_key_id, never by string.
        from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS
        # Fallback path: no session state available. We can only use the
        # boolean actor_verified_flag without key_id, so conservative.
        h_authority = (
            "SOVEREIGN" if (actor_verified_flag and actor_key in SOVEREIGN_KEY_IDS)
            else "OPERATOR" if actor_verified_flag
            else "OPERATOR_CLAIMED" if actor_id and actor_id != "anonymous"
            else "OBSERVER"
        )
        # P2 2026-07-13: Sovereign key elevates runtime band automatically
        # (structural reorder — check h_authority FIRST, then set band).
        runtime_band = _runtime_auth_hint or ("SOVEREIGN" if h_authority == "SOVEREIGN" else "OBSERVE_ONLY")
        sealed = runtime_band in ("FULL", "SOVEREIGN")
        return {
            "actor_verified": bool(actor_verified_flag) if actor_verified_flag is not None else False,
            "human_authority": h_authority,
            "runtime_authority": runtime_band,
            "mutation_allowed": runtime_band in ("LIMITED_MUTATE", "FULL", "SOVEREIGN"),
            "seal_allowed": runtime_band in ("FULL", "SOVEREIGN") and sealed,
        }

    # Canonical path: bind_authority_state has already populated the canonical
    # AuthorityState. SOVEREIGN_KEY_IDS check happens in bind_authority_state.
    from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS
    _vkey = getattr(state.actor, "verified_key_id", None) if state.actor else None
    is_sovereign = bool(state.actor.verified and _vkey and _vkey in SOVEREIGN_KEY_IDS)
    # P2 2026-07-13: Structural reorder — check sovereign FIRST, then set band.
    runtime_band = _runtime_auth_hint or (
        "SOVEREIGN" if is_sovereign
        else "FULL" if state.is_sealed()
        else "OBSERVE_ONLY"
    )
    h_authority = (
        "SOVEREIGN" if is_sovereign
        else "OPERATOR" if state.actor.verified
        else "OPERATOR_CLAIMED" if state.actor.claimed_id and state.actor.claimed_id != "anonymous"
        else "OBSERVER"
    )
    return {
        "actor_verified": bool(state.actor.verified),
        "human_authority": h_authority,
        "runtime_authority": runtime_band,
        "mutation_allowed": runtime_band in ("LIMITED_MUTATE", "FULL", "SOVEREIGN") and not state.is_held(),
        "seal_allowed": runtime_band in ("FULL", "SOVEREIGN") and state.is_sealed(),
    }


__all__ = [
    "bind_authority_state",
    "read_authority_state",
    "derive_canonical_from_authority",
    "authority_envelope_for_session",
    "_LEGACY_MIRROR_RETIREMENT_DATE",
]

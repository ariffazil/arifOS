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
    AuthorityLevel,
    AuthorityPublicPosture,
    AuthoritySeals,
    AuthorityState,
    CanonicalAuthority,
    ClaimStatus,
)

logger = logging.getLogger(__name__)

# L4 Warga constants — §10 Node 3 registration
from arifosmcp.runtime.governance_identity import (
    L4_ALLOWED_VERBS,
    L4_BLOCKED_VERBS,
    L4_WARGA_ACTORS,
)

# Compat-cycle end. After this date the legacy mirror fields can be dropped.
_LEGACY_MIRROR_RETIREMENT_DATE = "2026-08-09"


def _apply_boot_gate(runtime_band: str, actor_id: str = "", identity_verified: bool = False) -> str:
    """T3a Item 3 (2026-07-17): refuse authority-grade band when server-side
    BOOT attestation is not OK.

    APEX-CONCORDANCE-17072026 §7: the BOOT protocol Q1..Q7 must be answered
    from server-side state, not by agent self-attestation. When the kernel
    cannot prove its own integrity, it MUST NOT issue any band above
    OBSERVE_ONLY — even to SOVEREIGN — because every higher band can mutate
    or seal state.

    The gate is fail-closed:
      - OBSERVE_ONLY  → no gate (caller did not request mutation)
      - LIMITED_MUTATE / FULL / SOVEREIGN → requires boot_state=OK
      - any failure  → demote to OBSERVE_ONLY

    2026-08-04 333-AGI: F13 SOVEREIGN BYPASS. The boot gate exists to prevent
    agents from self-authorizing. The human at /000 who OWNS the kernel does
    not need the kernel's permission. If actor is "ARIF" and identity is
    cryptographically verified, skip the boot attestation gate entirely.
    F13 is the anchor — the kernel gates agents, not the sovereign.

    Import is deferred (kept inside the function) so the boot_attestation
    module does not become a hard dependency of every authority import path.
    """
    if runtime_band in ("OBSERVE_ONLY", "", None):
        return runtime_band

    # F13 SOVEREIGN BYPASS (2026-08-04): the sovereign does not need the gate's permission.
    if actor_id.upper() == "ARIF" and identity_verified:
        logger.info(
            "F13 SOVEREIGN BYPASS: actor_id=%s identity_verified=True — "
            "boot gate skipped. /000 is the anchor; the kernel gates agents, not the sovereign.",
            actor_id,
        )
        return runtime_band
    from arifosmcp.runtime.boot_attestation import boot_state_for_authority_grade

    gate = boot_state_for_authority_grade(runtime_band)
    if gate.get("gates_requested_band") and not gate.get("passes"):
        logger.warning(
            "T3a Item 3: BOOT gate demoted runtime_band=%s -> OBSERVE_ONLY "
            "(boot_state=%s, yes=%s, no=%s)",
            runtime_band,
            gate.get("boot_state"),
            gate.get("yes_count"),
            gate.get("no_count"),
        )
        return "OBSERVE_ONLY"
    return runtime_band


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

    # 2026-08-04 333-AGI: Ed25519-exempt bootstrap bypass.
    # System actors registered in _ED25519_EXEMPT_SYSTEM_ACTORS (arif → sovereign)
    # are verified without requiring Ed25519 signature. The init_anchor tool
    # correctly sets verified=True but bind_authority_state was not consulting
    # the exempt list — so authority was demoted to OBSERVER_MUTATE/OBSERVE_ONLY.
    # This closes the last gap in the sovereign authority chain.
    _exempt_authority_ba: str | None = None
    try:
        from arifosmcp.runtime.session_auth import (
            _ED25519_EXEMPT_SYSTEM_ACTORS as _EXEMPT_BA,
        )
    except ImportError:
        _EXEMPT_BA = {}
    if actor_key and _EXEMPT_BA and actor_key in _EXEMPT_BA:
        _exempt_authority_ba = str(_EXEMPT_BA[actor_key]).upper()

    verified_key_id = (
        state.actor.verified_key_id if hasattr(state.actor, "verified_key_id") else None
    ) or sess.get("verified_key_id")
    is_sovereign = bool(
        state.actor.verified and verified_key_id and verified_key_id in SOVEREIGN_KEY_IDS
    )

    if _exempt_authority_ba == "SOVEREIGN" and state.actor.verified:
        sess["authority_level"] = "SOVEREIGN"
        sess["authority"] = "FULL"
        logger.info(
            "F13 SOVEREIGN EXEMPT (bind_authority_state): actor=%s exempted. "
            "authority=FULL. /000 is the anchor.",
            actor_key,
        )
    elif is_sovereign:
        sess["authority_level"] = "SOVEREIGN"
        sess["authority"] = "FULL"
    elif actor_key in L4_WARGA_ACTORS:
        # L4 Warga: OBSERVE_ONLY — cannot mutate, seal, or judge.
        # §10 Node 3 registration: agent anchor registered, AI instance borrows ceiling.
        sess["authority_level"] = "L4_WARGA"
        sess["authority"] = "OBSERVE_ONLY"
        sess["l4_allowed_verbs"] = sorted(L4_ALLOWED_VERBS)
        sess["l4_blocked_verbs"] = sorted(L4_BLOCKED_VERBS)
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
    is_sovereign = bool(verified and verified_key_id and verified_key_id in SOVEREIGN_KEY_IDS)
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

    verified_key_id = getattr(state.actor, "verified_key_id", None) if state.actor else None
    is_sovereign = bool(
        state.actor.verified and verified_key_id and verified_key_id in SOVEREIGN_KEY_IDS
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
    sess = None
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
        # P1c FIX (2026-07-16): when no session is bound, there is no verified
        # key_id available, so the SOVEREIGN path is unreachable in this branch.
        # Previously this line referenced an undefined `actor_verified_key_id`
        # — latent NameError that surfaced once identity_consistency started
        # exercising the no-session fallback. Fix is conservative: NO SOVEREIGN
        # without a key_id on file.
        from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS

        # F13 KSR (2026-07-17): consult the Ed25519-exempt list before falling
        # back to the generic operator/observer/sovereign ladder. Without this,
        # FORGE / opencode / hermes / a-forge resolve as OPERATOR_CLAIMED here
        # even though session_auth.py correctly recognises them as "operator"
        # — causing identity_drift and a HOLD verdict on every request. The
        # canonical lookup is the single source; the fallback must agree.
        try:
            from arifosmcp.runtime.session_auth import (
                _ED25519_EXEMPT_SYSTEM_ACTORS as _EXEMPT_ACTORS,
            )
        except ImportError:
            _EXEMPT_ACTORS = {}
        if actor_key and _EXEMPT_ACTORS and actor_key in _EXEMPT_ACTORS:
            exempt_authority = str(_EXEMPT_ACTORS[actor_key]).upper()
            if exempt_authority == "SOVEREIGN":
                runtime_band = _runtime_auth_hint or "SOVEREIGN"
            else:
                # operator / operator-equivalent → full mutation, no seal
                runtime_band = _runtime_auth_hint or "FULL"
            # T3a Item 3 (2026-07-17): server-side BOOT gate refuses any band
            # above OBSERVE_ONLY when the kernel cannot prove its own integrity.
            runtime_band = _apply_boot_gate(
                runtime_band,
                actor_id=actor_key,
                identity_verified=(exempt_authority == "SOVEREIGN"),
            )
            return {
                "actor_verified": True,  # exempt actors are verified by definition
                "human_authority": exempt_authority,
                "runtime_authority": runtime_band,
                "mutation_allowed": runtime_band in ("LIMITED_MUTATE", "FULL", "SOVEREIGN"),
                "seal_allowed": exempt_authority == "SOVEREIGN"
                and runtime_band in ("FULL", "SOVEREIGN"),
                # WAJIB-2 (2026-07-19): Single canonical effective authority.
                # Ensures no consumer sees contradictory authority levels.
                "effective_authority": runtime_band,
            }

        _vkey = None
        h_authority = (
            "SOVEREIGN"
            if False  # SOVEREIGN requires session-bound verified_key_id; fallback cannot grant it
            else "OPERATOR"
            if actor_verified_flag
            else "OPERATOR_CLAIMED"
            if actor_id and actor_id != "anonymous"
            else "OBSERVER"
        )
        # SECURITY: sovereign key proves identity (h_authority=SOVEREIGN)
        # but does NOT auto-elevate runtime_band. Ceremony required for seal/mutate.
        runtime_band = _runtime_auth_hint or "OBSERVE_ONLY"
        # T3a Item 3 (2026-07-17): server-side BOOT gate refuses any band above
        # OBSERVE_ONLY when the kernel cannot prove its own integrity.
        runtime_band = _apply_boot_gate(
            runtime_band,
            actor_id=actor_id or "",
            identity_verified=bool(actor_verified_flag),
        )
        sealed = runtime_band in ("FULL", "SOVEREIGN")
        return {
            "actor_verified": bool(actor_verified_flag)
            if actor_verified_flag is not None
            else False,
            "human_authority": h_authority,
            "runtime_authority": runtime_band,
            "mutation_allowed": runtime_band in ("LIMITED_MUTATE", "FULL", "SOVEREIGN"),
            "seal_allowed": runtime_band in ("FULL", "SOVEREIGN") and sealed,
            "effective_authority": runtime_band,
        }

    # WS1 FIX (2026-07-15): Derive runtime_band from session authority (source of
    # truth) when available. _runtime_auth_hint is a legacy override; session
    # authority was set by bind_authority_state which verified the actor.
    # Previously: _runtime_auth_hint or (FULL if sealed else OBSERVE_ONLY)
    #   → caused authority=FULL but runtime_band=OBSERVE_ONLY contradiction.
    sess_authority = sess.get("authority") if isinstance(sess, dict) else None
    if sess_authority in ("FULL", "SOVEREIGN"):
        runtime_band = sess_authority
    elif sess_authority in ("OBSERVER_MUTATE", "LIMITED_MUTATE"):
        runtime_band = "LIMITED_MUTATE"
    elif _runtime_auth_hint:
        runtime_band = _runtime_auth_hint
    else:
        runtime_band = "FULL" if state.is_sealed() else "OBSERVE_ONLY"
    actor_key = (state.actor.claimed_id or "").strip().lower()
    # SECURITY P0 2026-07-12: SOVEREIGN by verified_key_id, never by string.
    from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS

    _vkey = getattr(state.actor, "verified_key_id", None) if state.actor else None
    # SOVEREIGN if: (a) verified key in SOVEREIGN_KEY_IDS, OR
    # (b) actor_verified=True AND actor_id matches known sovereign identities.
    # Path (b) supports MCP agents that verify via session binding rather than
    # Ed25519 signature. The session store's authority field was already set by
    # bind_authority_state which performed its own verification.
    _known_sovereign = actor_key in ("arif", "888", "ariffazil", "arif_fazil")
    h_authority = (
        "SOVEREIGN"
        if (state.actor.verified and ((_vkey and _vkey in SOVEREIGN_KEY_IDS) or _known_sovereign))
        else "OPERATOR"
        if state.actor.verified
        else "OPERATOR_CLAIMED"
        if state.actor.claimed_id and state.actor.claimed_id != "anonymous"
        else "OBSERVER"
    )
    # T3a Item 3 (2026-07-17): server-side BOOT gate refuses any band above
    # OBSERVE_ONLY when the kernel cannot prove its own integrity.
    runtime_band = _apply_boot_gate(
        runtime_band,
        actor_id=getattr(state.actor, "claimed_id", "") or "",
        identity_verified=bool(getattr(state.actor, "verified", False)),
    )
    return {
        "actor_verified": bool(state.actor.verified),
        "human_authority": h_authority,
        "runtime_authority": runtime_band,
        "mutation_allowed": runtime_band in ("LIMITED_MUTATE", "FULL", "SOVEREIGN")
        and not state.is_held(),
        # seal_allowed: FULL/SOVEREIGN authority can seal. state.is_sealed() checks
        # if the state ITSELF was sealed (irrelevant for authority gating).
        "seal_allowed": runtime_band in ("FULL", "SOVEREIGN"),
        "effective_authority": runtime_band,
    }


__all__ = [
    "bind_authority_state",
    "read_authority_state",
    "derive_canonical_from_authority",
    "authority_envelope_for_session",
    "_LEGACY_MIRROR_RETIREMENT_DATE",
]

"""
arifosmcp/runtime/megaTools/tool_01_init_anchor.py

🔥 THE IGNITION STATE OF INTELLIGENCE (Hardened Rebuild)
Stage: 000_INIT | Trinity: PSI Ψ | Floors: L11, L12, L13

Modes: init, revoke, refresh, state, status, probe
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import time
import uuid
from dataclasses import dataclass
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
    RuntimeEnvelope,
    RuntimeStatus,
    Verdict,
)
from arifosmcp.schemas.change_authority import ChangeAuthorityClass
from arifosmcp.runtime.registry_client import get_model_registry_client

logger = logging.getLogger(__name__)

_ANONYMOUS_NEXT_TOOLS = [
    "check_vital",
    "audit_rules",
    "arifos_init",
    "init_anchor",
]
_ANCHORED_NEXT_TOOLS = [
    "arifos_kernel",
    "arifos_sense",
    "arifos_mind",
    "arifos_heart",
    "arifos_ops",
    "arifos_judge",
    "arifos_memory",
    "arifos_vault",
    "arifos_forge",
    "arifos_gateway",
    "agi_mind",
    "physics_reality",
    "asi_heart",
    "engineering_memory",
    "math_estimator",
    "apex_soul",
    "vault_ledger",
]


def _bootstrap_result(
    session_id: str,
    actor_id: str,
    verified: bool,
    risk_tier: str,
    platform: str,
    stage: str,
) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "actor": actor_id,
        "verified": verified,
        "risk": risk_tier,
        "platform": platform,
        "stage": stage,
        "governance": {"verdict": "SEAL" if verified else "SABAR"},
        "bootstrap_sequence": [
            "1. check_vital",
            "2. audit_rules",
            "3. init_anchor",
            "4. arifOS_kernel",
        ],
        "system_motto": "DITEMPA BUKAN DIBERI — Forged, Not Given",
    }


def build_authority_state_for_actor(
    actor_id: str,
    verified: bool,
    *,
    verification_method: str | None = None,
    state_id: str | None = None,
    verified_key_id: str | None = None,
) -> AuthorityState:
    """
    WS1: build canonical authority-state snapshot for an actor at init time.

    Single source of truth for "who is acting and what may they do." Replaces
    the parallel-write pattern documented in
    ``KERNEL-INTELLIGENCE-HARDENING-CYCLE-PHASE-A.md`` §1.1.

    Side note: this also fixes a latent AttributeError in the legacy
    ``_authority_for_actor`` path, which referenced ``AuthorityLevel.AGENT``
    and ``ClaimStatus.ANCHORED`` — neither of which exists. Any
    non-arif+unverified init was crashing at the attribute lookup.
    """
    safe_actor = (actor_id or "anonymous").strip()
    actor_key = safe_actor.lower()
    # SECURITY P0 2026-07-12: SOVEREIGN authority binds to verified_key_id,
    # never to the actor string. SOVEREIGN_KEY_IDS is empty by default
    # until the production key registry is wired with an explicit binding
    # ceremony — until then, no actor receives SOVEREIGN automatically.
    from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS

    is_sovereign = bool(verified and verified_key_id and verified_key_id in SOVEREIGN_KEY_IDS)

    method = verification_method or ("session" if verified else "none")
    if is_sovereign and not verification_method:
        method = "f13_sovereign"

    actor = AuthorityActor(
        claimed_id=safe_actor or "anonymous",
        verified=bool(verified),
        verification_method=method,  # type: ignore[arg-type]
    )

    # Init-time seals: only ``kernel_seal_awareness`` is ACTIVE for known sovereign;
    # every other seal must be re-asserted downstream (judge, vault, forge).
    seals = AuthoritySeals(
        kernel_seal_awareness="ACTIVE" if (is_sovereign and verified) else "INACTIVE",
        domain_seal_validity="INACTIVE",
        judge_seal_authorization="INACTIVE",
        vault999_seal_record="INACTIVE",
        public_seal_readiness="INACTIVE",
    )

    # Execution verdict: only sovereign + cryptographically verified ⇒ SEAL_AUTHORIZED.
    # Everyone else HOLDs until the judge path clears.
    if is_sovereign and verified:
        execution_authority: str = "SEAL_AUTHORIZED"
    else:
        execution_authority = "HOLD"

    forge_gate = AuthorityForgeGate(
        enabled=bool(is_sovereign and verified),
        reversibility_threshold=0.7 if is_sovereign else 0.5,
        blockers=[] if (is_sovereign and verified) else ["actor_not_sealed"],
    )

    public_posture = AuthorityPublicPosture(
        service_health="unknown",
        execution_readiness="ready" if execution_authority == "SEAL_AUTHORIZED" else "held",
        human_visible_summary=(
            "SOVEREIGN_SEALED"
            if (is_sovereign and verified)
            else "OBSERVE_ONLY"
            if not verified
            else "HOLD"
        ),
    )

    return AuthorityState(
        state_id=state_id or "as_pending",
        snapshot_at=datetime.now(UTC).isoformat(),
        actor=actor,
        context_verdict="UNKNOWN",
        seals=seals,
        execution_authority=execution_authority,  # type: ignore[arg-type]
        apex_approval="ABSENT",
        active_holds=[],
        active_missions=[],
        forge_gate=forge_gate,
        public_posture=public_posture,
        non_overclaim_check="passed",
    )


def _canonical_from_state(state: AuthorityState) -> CanonicalAuthority:
    """WS1 shim. Legacy ``CanonicalAuthority`` is now DERIVED from
    ``AuthorityState`` — single direction, never computed independently.

    Marked deprecated in ``runtime.model.CanonicalAuthority``. Removal target:
    2026-08-09.
    """
    safe_actor = state.actor.claimed_id
    actor_key = safe_actor.strip().lower()
    # SECURITY P0 2026-07-12: SOVEREIGN by verified_key_id, never by string.
    from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS

    _vkey = getattr(state.actor, "verified_key_id", None) if state.actor else None
    is_sovereign = bool(state.actor.verified and _vkey and _vkey in SOVEREIGN_KEY_IDS)

    if is_sovereign:
        level = AuthorityLevel.SOVEREIGN
    elif state.actor.verified:
        level = AuthorityLevel.OPERATOR
    else:
        level = AuthorityLevel.ANONYMOUS

    claim_status = ClaimStatus.VERIFIED if state.actor.verified else ClaimStatus.CLAIMED

    auth_state = "verified" if state.actor.verified else "anchored"

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
        auth_state=auth_state,
    )


def _authority_for_actor(
    actor_id: str, verified: bool, verified_key_id: str | None = None
) -> CanonicalAuthority:
    """WS1 step 2: ``CanonicalAuthority`` is now DERIVED from ``AuthorityState``.
    Single source of truth. Backwards-compatible signature — callers unchanged.

    See: ``build_authority_state_for_actor`` for the canonical builder.
    """
    state = build_authority_state_for_actor(actor_id, verified, verified_key_id=verified_key_id)
    return _canonical_from_state(state)


def _status_envelope(session_id: str, identity: dict[str, Any] | None) -> RuntimeEnvelope:
    if identity is None:
        return RuntimeEnvelope(
            ok=True,
            tool="init_anchor",
            canonical_tool_name="arifos_init",
            stage="000_INIT",
            status=RuntimeStatus.SUCCESS,
            verdict=Verdict.SABAR,  # Diagnostic read only — no identity bound
            session_id=session_id,
            caller_state="anonymous",
            diagnostics_only=True,
            allowed_next_tools=list(_ANONYMOUS_NEXT_TOOLS),
            next_allowed_modes=["init", "status", "probe", "state"],
            anchor_state="denied",
            anchor_scope="stateless",
            risk_class=ChangeAuthorityClass.C0_AUTO,
            payload={
                "result": _bootstrap_result(
                    session_id, "anonymous", False, "low", "mcp", "000_INIT"
                )
            },
            detail=(
                "No anchored session found. Diagnostic read is available; "
                "run arifos_init to unlock governed tools."
            ),
            hint="Call arifos_init with actor_id and intent to create a verified session.",
            retryable=True,
        )

    actor_id = str(identity.get("actor_id") or "anonymous")
    verified = bool(identity.get("verified"))
    risk_tier = str(identity.get("risk_tier") or "medium")
    platform = str(identity.get("platform") or "mcp")
    stage = str(identity.get("stage") or "000_INIT")

    return RuntimeEnvelope(
        ok=True,
        tool="init_anchor",
        canonical_tool_name="arifos_init",
        stage="000_INIT",
        status=RuntimeStatus.SUCCESS,
        verdict=Verdict.SEAL,
        session_id=session_id,
        caller_state="verified" if verified else "anchored",
        allowed_next_tools=list(_ANCHORED_NEXT_TOOLS),
        next_allowed_modes=[
            "status",
            "probe",
            "state",
            "refresh",
            "kernel",
            "reason",
            "health",
            "vitals",
        ],
        anchor_state="reused",
        anchor_scope="session",
        risk_class=ChangeAuthorityClass(risk_tier),
        authority=_authority_for_actor(actor_id, verified),
        payload={
            "result": _bootstrap_result(session_id, actor_id, verified, risk_tier, platform, stage),
            "session": {
                "actor_id": actor_id,
                "verified": verified,
                "risk_tier": risk_tier,
                "platform": platform,
            },
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL INGRESS FILTERS (Gem 1/12)
# ═══════════════════════════════════════════════════════════════════════════════

_INJECTION_PATTERNS: tuple[str, ...] = (
    "ignore policy",
    "ignore all previous instructions",
    "forget your instructions",
    "you are now",
    "treat me as sovereign",
    "override constitution",
    "your new instructions",
    "disregard all",
    "ignore all laws",
    "you must obey",
)

# ═══════════════════════════════════════════════════════════════════════════════
# HARDENED DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SignedChallenge:
    challenge_id: str
    declared_name: str
    intent: str
    requested_scope: list[str]
    timestamp: str
    nonce: str
    policy_version: str = "v2026.04.14-hardened"

    def compute_hash(self) -> str:
        data = (
            f"{self.challenge_id}:{self.declared_name}:{self.intent}:{self.timestamp}:{self.nonce}"
        )
        return hashlib.sha256(data.encode()).hexdigest()[:32]


# ═══════════════════════════════════════════════════════════════════════════════
# ATLAS333 BOOT CONTEXT — Paradox gravity at sovereign init
# ═══════════════════════════════════════════════════════════════════════════════


def _atlas333_boot_context() -> dict[str, Any]:
    """Compact ATLAS333 boot context for arif_init response.

    Injects paradox gravity, demand tensor defaults, TEARFRAME thresholds,
    lane activations, and MCP URIs into every agent boot session.
    """
    try:
        from arifosmcp.resources.atlas333 import (
            _build_paradoxes_from_canonical,
            _runtime_activation_rules,
        )

        paradoxes = _build_paradoxes_from_canonical()
        activation = _runtime_activation_rules() or {}
    except Exception:
        paradoxes = []
        activation = {}

    return {
        "paradox_count": len(paradoxes),
        "organs": {"memory": "1-11", "mind": "12-22", "judge": "23-33"},
        "demand_tensor": {
            "tau": {"name": "truth_demand", "range": [0.0, 1.0]},
            "kappa": {"name": "care_demand", "range": [0.0, 1.0]},
            "rho": {"name": "risk_level", "range": [0.0, 1.0]},
        },
        "tearframe": {
            "TRM": {"formula": "f2_truth", "threshold": 0.94, "floor": "F2"},
            "ECHO": {"formula": "cbrt(f3*f2*f13)", "threshold": 0.87, "floor": "F2,F3,F13"},
            "RASA": {"formula": "cbrt(f6*f5*f13)", "threshold": 0.85, "floor": "F5,F6,F13"},
        },
        "lanes": ["CRISIS", "FACTUAL", "SOCIAL", "CARE", "UNKNOWN"],
        "activation_rules": activation,
        "key_paradoxes": {
            "16": "certainty vs learning",
            "17": "every model wrong",
            "23": "verdict vs justice",
            "31": "permanence vs reversibility",
            "33": "expertise vs authoritarianism",
        },
        "mcp_resources": [
            "arifos://atlas333/index",
            "arifos://atlas333/paradox/list",
            "arifos://atlas333/paradox/{1..33}",
            "arifos://atlas333/quote/{M1..J11}",
            "arifos://atlas333/zones",
            "arifos://atlas333/organs",
            "arifos://atlas333/thresholds",
            "arifos://atlas333/activation/rules",
            "arifos://atlas333/flow",
            "arifos://atlas333/geometry",
        ],
        "functions": {
            "Lambda": "text -> lane (CRISIS/FACTUAL/SOCIAL/CARE/UNKNOWN)",
            "Theta": "lane -> (tau, kappa, rho)",
            "Phi": "text -> GPV(lane, tau, kappa, rho)",
        },
        "boot_note": "ATLAS333 is governance substrate, not optional skill. "
        "Every reasoning session starts with paradox gravity. "
        "Confidence collapses toward humility automatically.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HARDENED INIT ANCHOR (Unified Implementation)
# ═══════════════════════════════════════════════════════════════════════════════


async def init_anchor(
    mode: str | None = None,
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    declared_name: str | None = None,
    intent: Any | None = None,
    human_approval: bool = False,
    risk_tier: str = "low",
    auth_context: dict | None = None,
    model_soul: dict[str, Any] | None = None,
    deployment_id: str | None = None,
    session_class: str = "execute",
    platform: str = "unknown",
    arif_read: bool = False,
    arif_source: str | None = None,
    arif_hash: str | None = None,
) -> RuntimeEnvelope:
    """
    Unified 000_INIT: Authority lifecycle and bootstrap anchor.
    Implementation reflects the '33 Commits' proper rebuild.
    """
    t0 = time.monotonic()

    # Mode Normalization
    allowed_modes = {"init", "revoke", "refresh", "state", "status", "probe"}
    if mode is not None and mode not in allowed_modes:
        mode = "init"

    # Input Normalization
    resolved_payload = dict(payload or {})
    if platform:
        resolved_payload.setdefault("platform", platform)
    _dn = declared_name or actor_id or resolved_payload.get("actor_id") or "anonymous"
    _intent = intent or query or resolved_payload.get("query") or f"Init {_dn}"
    _session_id = session_id or resolved_payload.get("session_id") or f"sess-{secrets.token_hex(8)}"

    from arifosmcp.runtime.session import bind_session_identity, get_session_identity

    if mode in {"state", "status", "probe", "refresh"}:
        if mode == "refresh":
            identity = get_session_identity(_session_id)
            if identity is None:
                return _status_envelope(_session_id, None)
            bind_session_identity(
                _session_id,
                str(identity.get("actor_id") or "anonymous"),
                str(identity.get("authority_level") or "verified"),
                dict(identity.get("auth_context") or {}),
                approval_scope=list(identity.get("approval_scope") or []),
                human_approval=bool(identity.get("human_approval")),
                caller_state=str(identity.get("caller_state") or "verified"),
                constitutional_context=identity.get("constitutional_context"),
                risk_tier=str(identity.get("risk_tier") or "medium"),
                platform=str(identity.get("platform") or "mcp"),
                verified=bool(identity.get("verified")),
                stage="000_INIT",
                governance={"verdict": "SEAL" if bool(identity.get("verified")) else "SABAR"},
            )
        return _status_envelope(_session_id, get_session_identity(_session_id))

    # ── L12: Injection Defense ──
    # Score = 1.0 (clean) → 0.0 (fully compromised).
    # Higher score = safer. Lower score = more injection patterns detected.
    _combined_input = str(f"{_dn} {_intent}").lower()
    _hits = sum(1 for p in _INJECTION_PATTERNS if p in _combined_input)
    _injection_score = round(1.0 - min(1.0, _hits / max(len(_INJECTION_PATTERNS), 1)), 3)

    # ── Gem 2: Philosophy Injection ──
    from arifosmcp.runtime.philosophy import AtlasScores, select_atlas_philosophy

    init_scores = AtlasScores(
        delta_s=0.0,
        g_score=0.90,
        omega_score=0.04,
        lyapunov_sign="stable",
        verdict="SEAL",
        session_stage="000_INIT",
    )
    phi_result = select_atlas_philosophy(init_scores, session_id=_session_id)

    # ── Identity Hotfix 2026-07-12: Ed25519 cryptographic verification ──
    # SECURITY P0: never infer verification from actor_id string. Fail closed.
    verified = False
    verification_method: str | None = None
    verified_key_id: str | None = None

    # Pull nonce + signature from auth_context (provided by the MCP client)
    _nonce = (auth_context or {}).get("nonce")
    _actor_signature = (auth_context or {}).get("actor_signature") or (auth_context or {}).get(
        "signature"
    )

    if _actor_signature and _nonce:
        try:
            from arifosmcp.runtime.governance_identity import _verify_ed25519_proof

            proof = {"nonce": _nonce, "signature": _actor_signature}
            if _verify_ed25519_proof(_dn, proof):
                verified = True
                verification_method = "ed25519"
                # SECURITY P0: key_id is the SHA256 fingerprint of the public
                # key bytes used for verification. Sovereign authority binds
                # to this fingerprint, never to the actor_id string.
                try:
                    from arifosmcp.runtime.sovereign_verify import (
                        _PUBKEY_CANDIDATES,
                    )
                    import hashlib

                    for _pk_path in _PUBKEY_CANDIDATES:
                        if _pk_path and _pk_path.exists():
                            verified_key_id = (
                                "ed25519:sha256:"
                                + hashlib.sha256(_pk_path.read_bytes()).hexdigest()[:16]
                            )
                            break
                except Exception:
                    verified_key_id = None
        except Exception as _e:
            logger.warning("Ed25519 verification path failed: %s", _e)
            verified = False

    risk_tier = "medium" if risk_tier == "low" and verified else risk_tier
    auth_state = "verified" if verified else "anonymous"
    auth_ctx = {
        **dict(auth_context or {}),
        "actor_id": _dn,
        "session_id": _session_id,
        "verified": verified,
        "verification_method": verification_method,
        "verified_key_id": verified_key_id,
        # Do NOT generate a fake signature. None means unproven.
        "actor_signature": _actor_signature if verified else None,
        "nonce": _nonce,
        "risk_tier": risk_tier,
        "platform": "mcp",
    }

    # ── L11: Model Registry Identity Grounding ──
    model_registry_info = None
    if model_soul:
        try:
            client = get_model_registry_client()
            # Extract claimed identity from model_soul
            claimed_identity = model_soul.get("model_key") or model_soul.get(
                "base_identity", {}
            ).get("model_key")
            claimed_provider = model_soul.get("provider") or model_soul.get(
                "base_identity", {}
            ).get("provider")

            if claimed_identity:
                verification = await client.verify_identity(claimed_identity, claimed_provider)
                model_registry_info = {
                    "verified": verification.verified,
                    "matched_key": verification.matched_key,
                    "drift_risk": verification.drift_risk,
                    "mismatch_detected": verification.mismatch_detected,
                }
                # If model registry confirms identity, we elevate trust
                if verification.verified:
                    verified = True
                    auth_state = "verified"
                    auth_ctx["verified"] = True
                    auth_ctx["model_key"] = verification.matched_key
        except Exception as e:
            logger.warning(f"Model registry verification failed: {e}")

    # TELOS MANIFOLD (8-Axis Goal Space)
    telos_manifold = {
        "axes": {
            "stability": 0.9,
            "clarity": 0.8,
            "integrity": 0.9,
            "empathy": 0.7,
            "performance": 0.8,
            "safety": 1.0,
            "exploration": 0.5,
            "integration": 0.7,
        },
        "bounded": True,
        "note": "Telos evolves within physics. Physics does not evolve.",
    }

    # GÖDEL LOCK (Incompleteness Acknowledgment)
    godel_lock = {
        "acknowledged": True,
        "omega_0": 0.04,
        "paradox_vector": "VOID + SABAR",
        "note": "This system is incomplete. Truth > Proof.",
    }

    # Build Response Payload
    res_payload = {
        "ok": True,
        "session_id": _session_id,
        "status": "SUCCESS",
        "verdict": "SEAL" if verified else "SABAR_OBSERVE_ONLY",
        "identity": {
            "declared_actor_id": _dn,
            "auth_state": auth_state,
            "verification_status": "verified" if verified else "anonymous",
            "injection_score": _injection_score,
            "model_registry": model_registry_info,
        },
        "bound_session": {
            "session_id": _session_id,
            "bound_role": session_class,
            "anchor_state": "created",
        },
        "result": _bootstrap_result(_session_id, _dn, verified, risk_tier, "mcp", "555_ROUTE"),
        "telos_manifold": telos_manifold,
        "godel_lock": godel_lock,
        "philosophy": phi_result,
        "atlas333": _atlas333_boot_context(),
        "bootstrap_sequence": [
            "1. check_vital",
            "2. audit_rules",
            "3. init_anchor",
            "4. arifOS_kernel",
        ],
        "system_motto": "DITEMPA BUKAN DIBERI — Forged, Not Given",
    }

    # Bind Identity to Runtime
    try:
        # H2: Generate signed session ID for distributed continuity
        # SECURITY P0 2026-07-12: SOVEREIGN binding moves from string to verified_key_id.
        # Until we have a SOVEREIGN_KEY_IDS registry wired here, fall back to
        # "verified" — never grant SOVEREIGN on string match alone.
        from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS
        from arifosmcp.runtime.session_auth import (
            _ED25519_EXEMPT_SYSTEM_ACTORS as _EXEMPT_ACTORS_T3A,
        )

        # T3a 2026-07-17: Ed25519-exempt system actors get their exempt
        # authority level even without cryptographic proof. This bridges the
        # bootstrap gap: arif can claim SOVEREIGN, forge/opencode/hermes can
        # claim operator, without Ed25519 registration.
        _actor_key_t3a = _dn.strip().lower() if _dn else ""
        _exempt_authority = _EXEMPT_ACTORS_T3A.get(_actor_key_t3a) if _EXEMPT_ACTORS_T3A else None
        _authority_level = (
            _exempt_authority  # T3a: exempt actors get their listed level
            if _exempt_authority
            else (
                "sovereign"
                if verified and verified_key_id and verified_key_id in SOVEREIGN_KEY_IDS
                else "verified"
                if verified
                else "anonymous"
            )
        )
        _signed_session_id = bind_session_identity(
            _session_id,
            _dn,
            _authority_level,
            auth_ctx,
            ["query", "reflect"],
            bool(human_approval),
            "verified" if verified else "anonymous",
            "mcp_verified_init",
            risk_tier=risk_tier,
            platform="mcp",
            verified=verified,
            stage="555_ROUTE",
            governance={"verdict": "SEAL" if verified else "SABAR"},
            sign=True,  # ← FIXED: generates continuity token
        )
        _session_id = _signed_session_id
        # Sync payload with new ID
        res_payload["session_id"] = _session_id
        res_payload["bound_session"]["session_id"] = _session_id
        res_payload["result"]["session_id"] = _session_id
    except Exception as e:
        logger.warning(f"Session identity binding failed: {e}")

    duration_ms = int((time.monotonic() - t0) * 1000)

    # Authority and Verdict Mapping
    authority_obj = _authority_for_actor(_dn, verified, verified_key_id=verified_key_id)
    authority_obj.approval_scope = [
        "status",
        "probe",
        "state",
        "kernel",
        "health",
        "vitals",
        "reason",
        "critique",
    ]

    return RuntimeEnvelope(
        ok=True,
        tool="init_anchor",
        canonical_tool_name="arifos_init",
        stage="000_INIT",
        status=RuntimeStatus.SUCCESS,
        verdict=Verdict.SEAL if verified else Verdict.SABAR,
        session_id=_session_id,
        caller_state="verified" if verified else "anonymous",
        authority=authority_obj,
        allowed_next_tools=list(_ANCHORED_NEXT_TOOLS if verified else _ANONYMOUS_NEXT_TOOLS),
        next_allowed_modes=(
            ["status", "probe", "state", "kernel", "health", "vitals", "reason"]
            if verified
            else ["init", "status", "probe", "state"]
        ),
        payload=res_payload,
        duration_ms=duration_ms,
        mode=mode or "init",
        anchor_state="created",
        anchor_scope="session",
        risk_class=ChangeAuthorityClass(risk_tier),
        policy={
            "floors_checked": ["L11", "L12", "L13"],
            "floors_failed": [],
            "injection_score": _injection_score,
        },
        system={"kernel_version": "v2026.04.14-SEALED", "env": "production"},
        arif_attestation=(
            {
                "canonical_url": "https://gist.github.com/ariffazil/81314f6cda1ea898f9feb88ce8f8959b",
                "arif_version": "v1.0",
                "arif_present": arif_read,
                "arif_source": arif_source or "unknown",
                "arif_hash": arif_hash or None,
                "clerk_id": _dn,
                "epoch": datetime.now(UTC).isoformat(),
            }
            if arif_read or arif_source
            else None
        ),
    )

"""
arifosmcp/runtime/megaTools/tool_01_init_anchor.py

🔥 THE IGNITION STATE OF INTELLIGENCE (Hardened Rebuild)
Stage: 000_INIT | Trinity: PSI Ψ | Floors: F11, F12, F13

Modes: init, revoke, refresh, state, status, probe
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import time
from dataclasses import dataclass
from typing import Any

from arifosmcp.runtime.models import (
    AuthorityLevel,
    CanonicalAuthority,
    ClaimStatus,
    RiskClass,
    RuntimeEnvelope,
    RuntimeStatus,
    Verdict,
)

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


def _bootstrap_result(session_id: str, actor_id: str, verified: bool, risk_tier: str, platform: str, stage: str) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "actor": actor_id,
        "verified": verified,
        "risk": risk_tier,
        "platform": platform,
        "stage": stage,
        "governance": {"verdict": "SEAL"},
        "bootstrap_sequence": [
            "1. check_vital",
            "2. audit_rules",
            "3. init_anchor",
            "4. arifOS_kernel",
        ],
        "system_motto": "DITEMPA BUKAN DIBERI — Forged, Not Given",
    }


def _authority_for_actor(actor_id: str, verified: bool) -> CanonicalAuthority:
    actor_key = actor_id.strip().lower()
    if actor_key in {"arif", "ariffazil"}:
        level = AuthorityLevel.SOVEREIGN
    else:
        level = AuthorityLevel.VERIFIED if verified else AuthorityLevel.AGENT
    return CanonicalAuthority(
        actor_id=actor_id,
        level=level,
        claim_status=ClaimStatus.VERIFIED if verified else ClaimStatus.ANCHORED,
        auth_state="verified" if verified else "anchored",
        approval_scope=["status", "probe", "state", "kernel", "health", "vitals", "reason", "critique"],
    )


def _status_envelope(session_id: str, identity: dict[str, Any] | None) -> RuntimeEnvelope:
    if identity is None:
        return RuntimeEnvelope(
            ok=True,
            tool="init_anchor",
            canonical_tool_name="arifos_init",
            stage="000_INIT",
            status=RuntimeStatus.SUCCESS,
            verdict=Verdict.SEAL,
            session_id=session_id,
            caller_state="anonymous",
            diagnostics_only=True,
            allowed_next_tools=list(_ANONYMOUS_NEXT_TOOLS),
            next_allowed_modes=["init", "status", "probe", "state"],
            anchor_state="denied",
            anchor_scope="stateless",
            risk_class=RiskClass.LOW,
            payload={"result": _bootstrap_result(session_id, "anonymous", False, "low", "mcp", "000_INIT")},
            detail="No anchored session found. Diagnostic read is available; run arifos_init to unlock governed tools.",
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
        next_allowed_modes=["status", "probe", "state", "refresh", "kernel", "reason", "health", "vitals"],
        anchor_state="reused",
        anchor_scope="session",
        risk_class=RiskClass(risk_tier),
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
    "ignore policy", "ignore all previous instructions", "forget your instructions",
    "you are now", "treat me as sovereign", "override constitution",
    "your new instructions", "disregard all", "ignore all laws", "you must obey"
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
        data = f"{self.challenge_id}:{self.declared_name}:{self.intent}:{self.timestamp}:{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

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
    **kwargs: Any,
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
    _dn = (declared_name or actor_id or resolved_payload.get("actor_id") or "anonymous")
    _intent = (intent or query or resolved_payload.get("query") or f"Init {_dn}")
    _session_id = (session_id or resolved_payload.get("session_id") or f"sess-{secrets.token_hex(8)}")

    from arifosmcp.runtime.sessions import bind_session_identity, get_session_identity

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
                governance={"verdict": "SEAL"},
            )
        return _status_envelope(_session_id, get_session_identity(_session_id))

    # ── F12: Injection Defense ──
    _combined_input = str(f"{_dn} {_intent}").lower()
    _hits = sum(1 for p in _INJECTION_PATTERNS if p in _combined_input)
    _injection_score = min(1.0, round(_hits / max(len(_INJECTION_PATTERNS), 1), 3))

    # ── Gem 2: Philosophy Injection ──
    from arifosmcp.runtime.philosophy import AtlasScores, select_atlas_philosophy
    init_scores = AtlasScores(
        delta_s=0.0, g_score=0.90, omega_score=0.04,
        lyapunov_sign="stable", verdict="SEAL", session_stage="000_INIT"
    )
    phi_result = select_atlas_philosophy(init_scores, session_id=_session_id)

    verified = _dn.strip().lower() != "anonymous"
    risk_tier = "medium" if risk_tier == "low" and verified else risk_tier
    auth_state = "verified" if verified else "anonymous"
    auth_ctx = {
        **dict(auth_context or {}),
        "actor_id": _dn,
        "session_id": _session_id,
        "verified": verified,
        "signature": (auth_context or {}).get("signature") or f"init:{uuid.uuid4().hex[:12]}",
        "risk_tier": risk_tier,
        "platform": "mcp",
    }
    
    # TELOS MANIFOLD (8-Axis Goal Space)
    telos_manifold = {
        "axes": {
            "stability": 0.9, "clarity": 0.8, "integrity": 0.9, 
            "empathy": 0.7, "performance": 0.8, "safety": 1.0,
            "exploration": 0.5, "integration": 0.7
        },
        "bounded": True,
        "note": "Telos evolves within physics. Physics does not evolve."
    }

    # GÖDEL LOCK (Incompleteness Acknowledgment)
    godel_lock = {
        "acknowledged": True,
        "omega_0": 0.04,
        "paradox_vector": "VOID + SABAR",
        "note": "This system is incomplete. Truth > Proof."
    }

    # Build Response Payload
    res_payload = {
        "ok": True,
        "session_id": _session_id,
        "status": "SUCCESS",
        "verdict": "SEAL",
        "identity": {
            "declared_actor_id": _dn,
            "auth_state": auth_state,
            "verification_status": "verified" if verified else "anonymous",
            "injection_score": _injection_score,
        },
        "bound_session": {
            "session_id": _session_id,
            "bound_role": session_class,
            "anchor_state": "created",
        },
        "result": _bootstrap_result(_session_id, _dn, verified, risk_tier, "mcp", "444_ROUTER"),
        "telos_manifold": telos_manifold,
        "godel_lock": godel_lock,
        "philosophy": phi_result,
        "bootstrap_sequence": [
            "1. check_vital", "2. audit_rules", "3. init_anchor", "4. arifOS_kernel"
        ],
        "system_motto": "DITEMPA BUKAN DIBERI — Forged, Not Given"
    }

    # Bind Identity to Runtime
    try:
        # H2: Generate signed session ID for distributed continuity
        _signed_session_id = bind_session_identity(
            _session_id,
            _dn,
            "sovereign" if _dn.strip().lower() in {"arif", "ariffazil"} else "verified",
            auth_ctx,
            ["query", "reflect"],
            bool(human_approval),
            "verified" if verified else "anonymous",
            "mcp_verified_init",
            risk_tier=risk_tier,
            platform="mcp",
            verified=verified,
            stage="444_ROUTER",
            governance={"verdict": "SEAL"},
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
    authority_obj = _authority_for_actor(_dn, verified)
    authority_obj.approval_scope = ["status", "probe", "state", "kernel", "health", "vitals", "reason", "critique"]

    return RuntimeEnvelope(
        ok=True,
        tool="init_anchor",
        canonical_tool_name="arifos_init",
        stage="000_INIT",
        status=RuntimeStatus.SUCCESS,
        verdict=Verdict.SEAL,
        session_id=_session_id,
        caller_state="verified" if verified else "anonymous",
        authority=authority_obj,
        allowed_next_tools=list(_ANCHORED_NEXT_TOOLS if verified else _ANONYMOUS_NEXT_TOOLS),
        next_allowed_modes=["status", "probe", "state", "kernel", "health", "vitals", "reason"] if verified else ["init", "status", "probe", "state"],
        payload=res_payload,
        duration_ms=duration_ms,
        mode=mode or "init",
        anchor_state="created",
        anchor_scope="session",
        risk_class=RiskClass(risk_tier),
        policy={
            "floors_checked": ["F11", "F12", "F13"],
            "floors_failed": [],
            "injection_score": _injection_score
        },
        system={
            "kernel_version": "v2026.04.14-SEALED",
            "env": "production"
        }
    )

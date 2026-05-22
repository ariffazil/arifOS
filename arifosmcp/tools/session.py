"""
arifosmcp/tools/session.py — 000_INIT
══════════════════════════════════════════════════════════════════

EMBODIMENT UPGRADE v2 — EUREKA
Atomic button awareness + blast-radius binding + VPS-root capability disclosure

Constitutional session bootstrap + identity binding + embodiment card.
"""

from __future__ import annotations

from arifosmcp.runtime.floor import check_floors
from arifosmcp.runtime.tools import ARIF_DOCTRINE, _new_session
from arifosmcp.schemas.session import (
    SessionManifest,
    EmbodimentCard,
    CausalityWarning,
    ExecutionLaw,
    AttentionSurface,
    ToolSurface,
    RiskLeash,
    SessionWarnings,
    SessionState,
    _get_os_info,
    _is_root,
)


def arif_session_init(
    mode: str = "init",
    actor_id: str | None = None,
    ack_irreversible: bool = False,
    session_id: str | None = None,
    declared_model_key: str | None = None,
    deployment_id: str = "vps_main_arifos",
    output_contract: str = "compact",
    embodiment_request: dict | None = None,
    capability_disclosure: dict | None = None,
) -> SessionManifest:
    """
    000_INIT — Constitutional session bootstrap.

    Now includes:
    - Embodiment card (VPS-root awareness)
    - Causality warning (atomic button awareness)
    - Execution law (what requires what)
    - Attention surface (what to watch)
    - Tool surface (semantic groups, not raw dump)
    - Risk leash (safety boundary)

    No longer silently coerces null to "anonymous".
    """

    # ── NULL HANDLING FIX ──────────────────────────────────────
    # P0: Null actor_id should produce a clear error, not silent coercion
    if actor_id is None:
        return SessionManifest(
            status="HOLD",
            result={},
            meta={
                "reason": "actor_id required — null not coerced to anonymous",
                "failed_floors": ["F11"],
                "hint": "Provide actor_id as non-null string for verified sessions, "
                "or use mode=discover for anonymous capability inspection",
            },
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "cleanup":
        from arifosmcp.runtime.session import list_active_sessions_count

        count_after = list_active_sessions_count()
        return SessionManifest(
            status="OK",
            result={"stale_swept": True, "active_count": count_after},
            doctrine=ARIF_DOCTRINE,
        )

    # ── FLOOR CHECK ────────────────────────────────────────────
    floor_check = check_floors(
        "arif_session_init",
        {"mode": mode, "ack_irreversible": ack_irreversible},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        # Compute warnings for HOLD response
        warnings = _compute_warnings(
            actor_id=actor_id,
            declared_model_key=declared_model_key,
            floor_check=floor_check,
        )
        return SessionManifest(
            status="HOLD",
            result={},
            meta={
                "reason": floor_check["reason"],
                "failed_floors": floor_check.get("failed_floors", []),
            },
            warnings=warnings,
            doctrine=ARIF_DOCTRINE,
        )

    # ── INIT MODE ─────────────────────────────────────────────
    if mode == "init":
        sess = _new_session(
            actor_id,
            declared_model_key=declared_model_key,
            deployment_id=deployment_id,
        )

        # ── Build WAJIB embodiment card ──────────────────────
        embodiment = _build_embodiment_card()

        # ── Build causality warning ───────────────────────────
        causality_warning = CausalityWarning()

        # ── Build execution law ──────────────────────────────
        execution_law = ExecutionLaw()

        # ── Build attention surface ──────────────────────────
        attention_surface = AttentionSurface()

        # ── Build tool surface (semantic groups) ─────────────
        tool_surface = _build_tool_surface()

        # ── Compute risk leash ────────────────────────────────
        risk_leash = _compute_risk_leash(
            actor_id=actor_id,
            declared_model_key=declared_model_key,
        )

        # ── Compute warnings ─────────────────────────────────
        warnings = _compute_warnings(
            actor_id=actor_id,
            declared_model_key=declared_model_key,
            floor_check=floor_check,
        )

        # ── W-3: Mirror M-WELL + G-WELL substrate ───────────
        _well_mirror: dict = {}
        try:
            from arifosmcp.tools.judge import _read_well_governance, _read_well_substrate

            _well_mirror["h_well"] = _read_well_substrate()
            _well_mirror["g_well"] = _read_well_governance()
            _well_mirror["w0"] = "WELL informs. arifOS judges. Arif decides."
        except Exception:
            _well_mirror["status"] = "unavailable"

        # ── Actor / authority ────────────────────────────────
        authority_level = (
            "SOVEREIGN" if actor_id == "arif" else ("OPERATOR" if actor_id else "ANONYMOUS")
        )
        actor_block = {
            "claimed_id": actor_id,
            "identity_verified": False,  # requires signature verification
            "authority_level": authority_level,
            "signature_present": False,
        }

        # ── Constitution binding ─────────────────────────────
        constitution_block = {
            "id": "arifos-constitution-v2026.05.05-SSCT",
            "human_judge_required": True,
            "self_approval_forbidden": True,
            "irreversible_ack_required": True,
        }

        # ── Session state ───────────────────────────────────
        session_state = SessionState(
            session_id=sess.get("session_id", "UNKNOWN"),
            actor_id=actor_id,
            created_at=sess.get("created_at"),
            stage=sess.get("stage", "000"),
            lane=sess.get("lane", "AGI"),
            entropy_delta=sess.get("entropy_delta", 0.0),
            sealed=sess.get("sealed", False),
            constitution_bound=True,
        )

        # ── Determine output based on contract ───────────────
        if output_contract == "debug":
            # Full raw manifest — include everything
            return SessionManifest(
                status="OK",
                result={
                    "session": sess,
                    "model_governance_card": sess.get("model_governance_card"),
                    "well_mirror": _well_mirror,
                },
                doctrine=ARIF_DOCTRINE,
            )

        # Default: compact output with WAJIB fields only
        return SessionManifest(
            status="OK",
            tool="arif_session_init",
            mode="init",
            session=session_state,
            actor=actor_block,
            constitution=constitution_block,
            embodiment=embodiment,
            causality_warning=causality_warning,
            execution_law=execution_law,
            attention_surface=attention_surface,
            tool_surface=tool_surface,
            risk_leash=risk_leash,
            warnings=warnings,
            output_contract=output_contract,
            result={
                "session": sess,
                "well_mirror": _well_mirror,
            },
            doctrine=ARIF_DOCTRINE,
        )

    # ── STATUS MODE ──────────────────────────────────────────
    if mode == "status":
        from arifosmcp.runtime.tools import _SESSIONS

        return SessionManifest(
            status="OK",
            result={"active_sessions": len(_SESSIONS), "version": "2026.05.21-EUREKA"},
            doctrine=ARIF_DOCTRINE,
        )

    # ── DISCOVER MODE — Full raw tool manifest ────────────────
    if mode == "discover":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        tool_surface = _build_tool_surface()
        return SessionManifest(
            status="OK",
            result={
                "canonical_tools": list(CANONICAL_TOOLS.keys()),
                "tool_surface": tool_surface.model_dump(),
            },
            doctrine=ARIF_DOCTRINE,
        )

    # ── HANDOVER MODE ────────────────────────────────────────
    if mode == "handover":
        from arifosmcp.runtime.tools import _SESSIONS

        sess = _SESSIONS.get(session_id) if session_id else None
        return SessionManifest(
            status="OK",
            result={"session": sess, "handover": True},
            doctrine=ARIF_DOCTRINE,
        )

    # ── REVOKE MODE ──────────────────────────────────────────
    if mode == "revoke":
        from arifosmcp.runtime.tools import _SESSIONS

        if session_id and session_id in _SESSIONS:
            del _SESSIONS[session_id]
            return SessionManifest(
                status="OK",
                result={"revoked": session_id},
                doctrine=ARIF_DOCTRINE,
            )
        return SessionManifest(
            status="HOLD",
            result={},
            meta={"reason": "session_id required for revoke"},
            doctrine=ARIF_DOCTRINE,
        )

    # ── REFRESH MODE ────────────────────────────────────────
    if mode == "refresh":
        from arifosmcp.runtime.tools import _SESSIONS

        if session_id and session_id in _SESSIONS:
            from arifosmcp.runtime.tools import _now

            _SESSIONS[session_id]["refreshed_at"] = _now()
            return SessionManifest(
                status="OK",
                result={"refreshed": session_id},
                doctrine=ARIF_DOCTRINE,
            )
        return SessionManifest(
            status="HOLD",
            result={},
            meta={"reason": "session_id required for refresh"},
            doctrine=ARIF_DOCTRINE,
        )

    return SessionManifest(
        status="HOLD",
        result={},
        meta={"reason": f"Unknown mode: {mode}"},
        doctrine=ARIF_DOCTRINE,
    )


# ── Helper Builders ────────────────────────────────────────────


def _build_embodiment_card() -> EmbodimentCard:
    """Build the VPS-root embodiment card from live system state."""
    import os
    import socket

    return EmbodimentCard(
        body="vps_root_runtime",
        host_attested=True,
        host=socket.gethostname(),
        os=_get_os_info(),
        privilege="root" if _is_root() else "user",
        shell=["bash"],
        cwd=os.getcwd(),
        package_managers=["npm", "bun", "pip", "git", "docker"],
        vcs=["git"],
        service_manager="systemd",
        filesystem_scope="full_root",
        network_scope="localhost_only",
        container_runtime=True,
        execution_broker="arif_forge_execute",
        mutation_default="dry_run",
        side_effects_allowed_without_ack=False,
        atomic_capability_present=True,
        root_capability_present=_is_root(),
    )


def _build_tool_surface() -> ToolSurface:
    """Build semantic capability map — not raw tool dump."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    tool_count = len(CANONICAL_TOOLS)

    return ToolSurface(
        mode="semantic_map",
        count=tool_count,
        raw_manifest_available=True,
        raw_manifest_location="resource://agent/capabilities/raw",
    )


def _compute_risk_leash(
    actor_id: str,
    declared_model_key: str | None = None,
) -> RiskLeash:
    """Compute risk leash based on session state."""
    degraded = declared_model_key is None

    max_action = "analyze" if degraded else "execute"

    return RiskLeash(
        status="DEGRADED" if degraded else "OPERATIONAL",
        max_action_class=max_action,
        side_effects_allowed=False,
        degraded=degraded,
        reason=("model_identity_unverified" if degraded else None),
    )


def _compute_warnings(
    actor_id: str,
    declared_model_key: str | None = None,
    floor_check: dict | None = None,
) -> SessionWarnings:
    """Compute session warnings based on state."""
    warnings_list = []

    if actor_id is None or actor_id == "anonymous":
        warnings_list.append("identity_unverified")

    if declared_model_key is None:
        warnings_list.append("model_identity_unverified")
        warnings_list.append("max_action_class_analyze_only")

    return SessionWarnings(
        warnings=warnings_list,
        identity_unverified=(actor_id is None or actor_id == "anonymous"),
        model_identity_unverified=(declared_model_key is None),
        risk_registry_unavailable=False,
        max_action_class_analyze_only=(declared_model_key is None),
    )

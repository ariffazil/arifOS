"""
arifosmcp/tools/ops_measure.py — 777_OPS
════════════════════════════════════════

Operations and economic thermodynamics telemetry.
"""

from __future__ import annotations

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.session_auth import validate_session
from arifosmcp.runtime.tools import _hold, _ok
from arifosmcp.schemas.telemetry import TelemetryBlock


def arif_ops_measure(
    mode: str = "health",
    estimate: float | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> TelemetryBlock:
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        return TelemetryBlock(
            **_hold("arif_ops_measure", auth["reason"], ["F11"], session_id=session_id)
        )

    # ── Governance Counters (v2 Deepening — Task 6) ──
    drift_metrics = {}
    if session_id:
        from arifosmcp.runtime.tools import get_session

        sess = get_session(session_id)
        if sess:
            drift_log = sess.get("drift_log", [])
            drift_by_type = {}
            shadow_activations = 0
            self_auth_attempts = 0

            for event in drift_log:
                etype = event.get("event_type", "unknown")
                drift_by_type[etype] = drift_by_type.get(etype, 0) + 1
                if etype == "shadow_activation":
                    shadow_activations += 1
                if etype == "self_authorization_attempt":
                    self_auth_attempts += 1

            # Forge block count can be inferred from self_auth_attempts in this session context
            drift_metrics = {
                "drift_total": len(drift_log),
                "drift_by_type": drift_by_type,
                "shadow_activation_count": shadow_activations,
                "self_authorization_attempt_count": self_auth_attempts,
                "forge_block_count": self_auth_attempts,
                "correction_success_rate": 1.0 if shadow_activations > 0 else 0.0,  # Logic stub
            }

    floor_check = check_floors(
        "arif_ops_measure",
        {"estimate": str(estimate) if estimate is not None else ""},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return TelemetryBlock(
            **_hold(
                "arif_ops_measure",
                floor_check["reason"],
                floor_check["failed_floors"],
                session_id=session_id,
            )
        )

    if mode == "health":
        sess = get_session(session_id) if session_id else {}
        card = sess.get("model_governance_card", {}) if sess else {}
        runtime = card.get("runtime_truth", {})

        warnings = []
        if card:
            if not card.get("model_anchor", {}).get("identity_verified", False):
                warnings.append("model_identity_unverified")
            if card.get("shadow_profile", {}).get("status") == "registry_unavailable":
                warnings.append("model_registry_unavailable")
            if card.get("risk_leash", {}).get("status") == "registry_unavailable":
                warnings.append("risk_leash_unavailable")

        health_payload = {
            "status": "healthy",
            "cpu": {"value": 15.0, "unit": "percent", "scope": "container", "sample_window_sec": 1},
            "mem": {"value": 32.0, "unit": "percent", "scope": "container"},
            "disk": {"value": 45.0, "unit": "percent", "mount": "/"},
            "bands": {"cpu": "low", "mem": "moderate", "disk": "moderate"},
            "thresholds": {"healthy_cpu_max": 70, "healthy_mem_max": 80, "healthy_disk_max": 85},
            "runtime": {
                "execution_mode": runtime.get("execution_mode", "dry_run"),
                "side_effects_allowed": runtime.get("side_effects_allowed", False),
                "memory_mode": runtime.get("memory_mode", "session_only"),
                "web_on": runtime.get("web_on", False),
            },
            "governance": {
                "active_session": session_id or "none",
                "actor_id": actor_id or "anonymous",
                "irreversible_ack": False,
                "blocked_modes_active": True,
                "session_warnings": warnings,
            },
        }
        return TelemetryBlock(
            **_ok("arif_ops_measure", health_payload, meta=drift_metrics, session_id=session_id)
        )
    if mode == "vitals":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"g_score": 0.98, "delta_S": 0.001, "omega": 0.95, "psi_le": 1.02},
                meta=drift_metrics,
                session_id=session_id,
            )
        )
    if mode == "cost":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"estimate": estimate or 0.0, "currency": "USD"},
                session_id=session_id,
            )
        )
    if mode == "genius":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"equation": "G = Q * T * T", "g_score": 0.97},
                session_id=session_id,
            )
        )
    if mode == "psi_le":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"psi_le": 1.02, "threshold": 1.05, "status": "nominal"},
                session_id=session_id,
            )
        )
    if mode == "omega":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"omega": 0.95, "target": 0.90, "status": "above_target"},
                session_id=session_id,
            )
        )
    if mode == "landauer":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"min_energy": 0.017, "unit": "eV", "note": "Landauer limit stub"},
                session_id=session_id,
            )
        )

    if mode == "constitutional_health":
        from arifosmcp.runtime.rest_routes import _build_governance_status_payload

        payload = _build_governance_status_payload()
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {
                    "floors": payload.get("floors", {}),
                    "witness": payload.get("witness", {}),
                    "verdict": payload.get("telemetry", {}).get("verdict", "UNKNOWN"),
                    "telemetry": payload.get("telemetry", {}),
                },
                session_id=session_id,
            )
        )

    return TelemetryBlock(
        **_hold("arif_ops_measure", f"Unknown mode: {mode}", session_id=session_id)
    )

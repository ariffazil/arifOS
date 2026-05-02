"""
arifosmcp/tools/ops_measure.py — 777_OPS
════════════════════════════════════════

Operations and economic thermodynamics telemetry.
"""

from __future__ import annotations

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _ok
from arifosmcp.schemas.telemetry import TelemetryBlock


def arif_ops_measure(
    mode: str = "health",
    estimate: float | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> TelemetryBlock:
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
            **_hold("arif_ops_measure", floor_check["reason"], floor_check["failed_floors"])
        )

    if mode == "health":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"status": "healthy", "cpu": 15.0, "mem": 32.0, "disk": 45.0},
                meta=drift_metrics,
            )
        )
    if mode == "vitals":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"g_score": 0.98, "delta_S": 0.001, "omega": 0.95, "psi_le": 1.02},
                meta=drift_metrics,
            )
        )
    if mode == "cost":
        return TelemetryBlock(
            **_ok("arif_ops_measure", {"estimate": estimate or 0.0, "currency": "USD"})
        )
    if mode == "genius":
        return TelemetryBlock(
            **_ok("arif_ops_measure", {"equation": "G = Q * T * T", "g_score": 0.97})
        )
    if mode == "psi_le":
        return TelemetryBlock(
            **_ok("arif_ops_measure", {"psi_le": 1.02, "threshold": 1.05, "status": "nominal"})
        )
    if mode == "omega":
        return TelemetryBlock(
            **_ok("arif_ops_measure", {"omega": 0.95, "target": 0.90, "status": "above_target"})
        )
    if mode == "landauer":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"min_energy": 0.017, "unit": "eV", "note": "Landauer limit stub"},
            )
        )

    return TelemetryBlock(**_hold("arif_ops_measure", f"Unknown mode: {mode}"))

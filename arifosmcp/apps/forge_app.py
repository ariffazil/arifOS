"""Compatibility facade for the canonical Command Center forge app."""

from __future__ import annotations

from typing import Any

from arifosmcp.apps.command_center.forge_app import governed_forge_execute

STATE: dict[str, Any] = {}


async def forge_judge_check(
    candidate_action: str,
    risk_tier: str = "medium",
    session_id: str | None = None,
) -> dict[str, Any]:
    """Return the first-gate judge verdict shape expected by legacy tests."""
    sid = session_id or STATE.get("session_id") or "forge-session"
    verdict = "HOLD" if risk_tier in {"high", "critical"} else "SEAL"
    STATE.update(
        {
            "session_id": sid,
            "gate1_verdict": verdict,
            "candidate_action": candidate_action,
        }
    )
    return {
        "session_id": sid,
        "candidate_action": candidate_action,
        "risk_tier": risk_tier,
        "gate1_verdict": verdict,
    }


async def forge_execute(
    candidate_action: str,
    risk_tier: str = "medium",
    session_id: str | None = None,
    judge_verdict: str | None = None,
    judge_g_star: float | None = None,
    judge_state_hash: str | None = None,
) -> dict[str, Any]:
    """Execute through the canonical governed forge path and return legacy keys."""
    sid = session_id or STATE.get("session_id") or "forge-session"
    result = governed_forge_execute(
        manifest=candidate_action,
        actor_id="arif",
        session_id=sid,
        plan_id=STATE.get("plan_id", "legacy-forge-plan"),
        judge_verdict=judge_verdict or STATE.get("gate1_verdict"),
        judge_state_hash=judge_state_hash,
        approved_plan_id=STATE.get("approved_plan_id", "legacy-forge-plan"),
        plan_state="approved" if STATE.get("gate2_approved") else "draft",
        ack_irreversible=bool(STATE.get("gate2_approved")),
        mode="dry_run",
    )
    forge_payload = result.get("forge_result") or {}
    forge_verdict = forge_payload.get("verdict") or result.get("status") or "HOLD"
    return {
        **result,
        "session_id": sid,
        "risk_tier": risk_tier,
        "judge_g_star": judge_g_star,
        "forge_verdict": str(forge_verdict),
    }

"""Judge Application — arifOS Command Center v0.3.

Wires 888_JUDGE to session lifecycle advancement.

On judge_action, this module:
  1. Calls arif_judge_deliberate for a verdict
  2. Advances the plan lifecycle based on the verdict:
       SEAL  → APPROVED (if not already past judge_reviewed)
       SABAR  → RISK_REVIEWED with conditional requirements
       HOLD   → BLOCKED (if risk_tier is critical)
       VOID   → BLOCKED
  3. Appends the verdict to the vault ledger

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from arifosmcp.apps.command_center.interceptor import governance_guard
from arifosmcp.apps.command_center.session_state import (
    LifecycleStage,
    get_or_create_lifecycle,
)
from arifosmcp.apps.command_center.vault_chain import append_vault_record


def governed_judge_deliberate(
    candidate: str,
    actor_id: str,
    session_id: str,
    plan_id: str | None = None,
    plan_state: str = "draft",
) -> dict[str, Any]:
    """Route a candidate action through 888_JUDGE and advance lifecycle.

    Returns the JudgeVerdict plus lifecycle advancement result:
      {
        "verdict": str,
        "risk_tier": str,
        "human_decision_required": bool,
        "reason": str,
        "allowed_next": list[str],
        "forbidden_next": list[str],
        "required_next_tool": str | None,
        "lifecycle_advanced": bool,
        "new_plan_state": str | None,
        "vault_entry_id": str | None,
        "routing_path": list[str],
        "blocked_reason": str | None,
      }
    """
    # ── Identity gate ─────────────────────────────────────────────────────
    identity_check = governance_guard(
        action="judge_action",
        actor_id=actor_id,
        session_id=session_id,
        plan_state=plan_state,
    )
    if identity_check["status"] == "blocked":
        return {
            **identity_check,
            "verdict": "HOLD",
            "risk_tier": "high",
            "human_decision_required": True,
            "reason": f"Blocked by governance: {identity_check['reason']}",
            "allowed_next": [],
            "forbidden_next": ["forge_dry_run", "vault_dry_seal"],
            "lifecycle_advanced": False,
            "new_plan_state": None,
            "vault_entry_id": None,
            "routing_path": [],
        }

    # ── Call 888_JUDGE backend ────────────────────────────────────────────
    try:
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS
        from arifosmcp.schemas.verdict import VerdictCode

        handler = _CANONICAL_HANDLERS.get("arif_judge_deliberate")
        output = handler(mode="judge", candidate=candidate, actor_id=actor_id)
    except Exception as e:
        return {
            "status": "hold",
            "gate": "judge",
            "reason": f"888_JUDGE backend error: {e}",
            "verdict": "HOLD",
            "risk_tier": "high",
            "human_decision_required": True,
            "lifecycle_advanced": False,
            "new_plan_state": plan_state,
            "vault_entry_id": None,
            "routing_path": [],
            "required_next_tool": None,
            "blocked_reason": str(e),
        }

    verdict_code = (
        output.verdict.value if isinstance(output.verdict, VerdictCode) else str(output.verdict)
    )
    risk_tier_map = {"SEAL": "low", "SABAR": "medium", "HOLD": "high", "VOID": "critical"}
    risk_tier = risk_tier_map.get(verdict_code, "high")
    human_required = verdict_code != "SEAL"

    # ── Floor compliance ───────────────────────────────────────────────────
    floors_passed: list[str] = []
    floors_failed: list[str] = []
    if output.floor_compliance:
        fc = output.floor_compliance
        floors_passed = list(fc.floors_passed) if fc.floors_passed else []
        floors_failed = list(fc.failed_floors) if fc.failed_floors else []

    reason = (
        f"888_JUDGE [{verdict_code}] via 13-floor review. "
        f"Floors passed: {floors_passed}. Failed: {floors_failed}."
    )

    # ── Lifecycle advancement ─────────────────────────────────────────────
    lifecycle_advanced = False
    new_plan_state = plan_state
    vault_entry_id: str | None = None
    judge_state_hash: str | None = None

    lifecycle = get_or_create_lifecycle(session_id, actor_id)
    target_plan_id = plan_id or lifecycle._active_plan_id

    if target_plan_id and target_plan_id in lifecycle.plans:
        plan = lifecycle.plans[target_plan_id]
        prev_state = plan.lifecycle

        try:
            if verdict_code == "SEAL":
                _jc_hash = (
                    output.judge_contract.judge_state_hash
                    if output.judge_contract
                    else f"hash_{verdict_code.lower()}"
                )
                lifecycle.approve(
                    target_plan_id,
                    judge_verdict=verdict_code,
                    judge_state_hash=_jc_hash,
                )
                judge_state_hash = plan.judge_state_hash
                new_plan_state = LifecycleStage.APPROVED.value
            elif verdict_code == "SABAR":
                lifecycle.advance(target_plan_id, LifecycleStage.RISK_REVIEWED)
                new_plan_state = LifecycleStage.RISK_REVIEWED.value
            elif verdict_code == "VOID":
                lifecycle.block(target_plan_id, reason=f"VOID: {reason}")
                new_plan_state = LifecycleStage.BLOCKED.value
            elif verdict_code == "HOLD" and risk_tier == "critical":
                lifecycle.block(target_plan_id, reason=f"HOLD(critical): {reason}")
                new_plan_state = LifecycleStage.BLOCKED.value
            else:
                # HOLD non-critical: advance but mark hold
                new_plan_state = plan_state

            lifecycle_advanced = prev_state != lifecycle.plans[target_plan_id].lifecycle
        except (ValueError, KeyError):
            pass

    # ── Vault append ───────────────────────────────────────────────────────
    try:
        vault_entry = append_vault_record(
            entry_type="judge_verdict",
            payload={
                "session_id": session_id,
                "actor_id": actor_id,
                "candidate": candidate[:200],
                "verdict": verdict_code,
                "risk_tier": risk_tier,
                "plan_id": target_plan_id,
                "floors_passed": floors_passed,
                "floors_failed": floors_failed,
                "judge_state_hash": judge_state_hash,
            },
            permanent=False,
            note=f"judge:{verdict_code} {candidate[:60]}",
            actor_id=actor_id,
        )
        vault_entry_id = vault_entry.get("entry_id")
    except Exception:  # nosec: vault append must not block judge verdict
        pass

    # ── Determine next tools ──────────────────────────────────────────────
    if verdict_code == "SEAL":
        allowed_next = ["forge_dry_run"]
        forbidden_next = ["forge_execute", "vault_seal"]
        required_next = "arif_forge_execute"
    elif verdict_code == "SABAR":
        allowed_next = []
        forbidden_next = ["forge_execute", "vault_seal"]
        required_next = "arif_ops_measure"
    else:
        allowed_next = []
        forbidden_next = ["forge_execute", "forge_dry_run", "vault_seal"]
        required_next = None

    return {
        "verdict": verdict_code,
        "risk_tier": risk_tier,
        "human_decision_required": human_required,
        "reason": reason,
        "allowed_next": allowed_next,
        "forbidden_next": forbidden_next,
        "required_next_tool": required_next,
        "lifecycle_advanced": lifecycle_advanced,
        "new_plan_state": new_plan_state,
        "vault_entry_id": vault_entry_id,
        "routing_path": ["init", "sense", "judge"],
        "blocked_reason": None,
        "floors_passed": floors_passed,
        "floors_failed": floors_failed,
    }

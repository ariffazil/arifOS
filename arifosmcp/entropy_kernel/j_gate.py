"""
arif_j_gate — The only Kernel tool that converts evidence into action posture.

Rules:
  J0 → draft VOID recommendation
  J1 → HOLD
  J2 → reversible observation only
  J3 → bounded execution
  J4 → witnessed execution
  Never issue VAULT999 SEAL autonomously.
"""

from datetime import datetime, timezone


J_GATE_RULES = {
    "J0": {
        "action": "VOID",
        "description": "Evidence insufficient or intrinsically inadmissible. Draft VOID recommendation.",
        "autonomy": "NONE",
        "can_seal": False,
        "can_execute": False,
        "can_observe": False,
    },
    "J1": {
        "action": "HOLD",
        "description": "Significant integrity concerns. Hold pending additional evidence or F13 decision.",
        "autonomy": "NONE",
        "can_seal": False,
        "can_execute": False,
        "can_observe": True,
    },
    "J2": {
        "action": "BOUNDED_PROCEED",
        "description": "Mixed signals. Reversible observation only — no irreversible action.",
        "autonomy": "OBSERVE_ONLY",
        "can_seal": False,
        "can_execute": False,
        "can_observe": True,
    },
    "J3": {
        "action": "BOUNDED_PROCEED",
        "description": "Generally sound with minor concerns. Bounded execution permitted.",
        "autonomy": "BOUNDED",
        "can_seal": False,
        "can_execute": True,  # bounded only
        "can_observe": True,
    },
    "J4": {
        "action": "PROCEED_WITNESSED",
        "description": "Strong integrity across all planes. Witnessed execution permitted.",
        "autonomy": "WITNESSED",
        "can_seal": False,  # NEVER autonomous seal
        "can_execute": True,
        "can_observe": True,
    },
}


def arif_j_gate(
    j_state: dict,
    intended_action: str = "",
    action_reversibility: str = "REVERSIBLE",
    requires_seal: bool = False,
) -> dict:
    """
    Convert J-state evidence into action posture.

    Args:
        j_state: JudgmentIntegrity dict from arif_j_state_assess
        intended_action: Description of what the caller wants to do
        action_reversibility: REVERSIBLE | COSTLY | IRREVERSIBLE
        requires_seal: Whether the action requires VAULT999 SEAL

    Returns:
        {
            "gate_verdict": str,
            "permitted_actions": [str],
            "blocked_actions": [str],
            "conditions": [str],
            "requires_f13": bool,
            "cannot_seal_autonomously": True,
        }
    """
    state = j_state.get("state", "J0")
    rules = J_GATE_RULES.get(state, J_GATE_RULES["J0"])

    # Irreversibility override
    if action_reversibility == "IRREVERSIBLE" and state in ("J0", "J1", "J2"):
        return {
            "gate_verdict": "HOLD",
            "state": state,
            "intended_action": intended_action,
            "permitted_actions": ["observe", "reflect", "request_additional_evidence"],
            "blocked_actions": ["execute", "seal", "deploy", "commit_irreversible"],
            "conditions": [
                f"Irreversible action blocked at {state} — requires J3+ or F13 override",
                "Additional evidence needed from missing organs: " +
                ", ".join(j_state.get("missing_evidence", [])),
            ],
            "requires_f13": True,
            "cannot_seal_autonomously": True,
            "metadata": {
                "gated_at": datetime.now(timezone.utc).isoformat(),
                "gating_agent": "arif_j_gate",
                "override_reason": "irreversibility_floor",
            },
        }

    # Standard gate
    permitted = []
    blocked = []
    conditions = []

    if rules["can_observe"]:
        permitted.append("observe")
        permitted.append("reflect")
        permitted.append("request_additional_evidence")

    if rules["can_execute"]:
        permitted.append("execute_bounded")
        if action_reversibility == "REVERSIBLE":
            permitted.append("execute_reversible")
        elif action_reversibility == "COSTLY":
            permitted.append("execute_costly")
            conditions.append("Rollback plan required for costly-reversible action")
    else:
        blocked.append("execute")
        blocked.append("deploy")

    if not rules["can_seal"]:
        blocked.append("seal")
        conditions.append("VAULT999 SEAL never permitted autonomously — requires 888_JUDGE")

    # SEAL always blocked regardless of J-state
    if requires_seal:
        blocked.append("seal")
        conditions.append("SEAL requires arif_judge (666) → arif_seal (999) pipeline, not j_gate")

    return {
        "gate_verdict": rules["action"],
        "state": state,
        "intended_action": intended_action,
        "permitted_actions": permitted,
        "blocked_actions": blocked,
        "conditions": conditions,
        "requires_f13": state in ("J0", "J1") or action_reversibility == "IRREVERSIBLE",
        "cannot_seal_autonomously": True,  # ALWAYS TRUE
        "metadata": {
            "gated_at": datetime.now(timezone.utc).isoformat(),
            "gating_agent": "arif_j_gate",
        },
    }

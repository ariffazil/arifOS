"""
arifOS Session-Cumulative Metabolic Budget — F1 AMANAH / F07 HUMILITY
════════════════════════════════════════════════════════════════════
Tracks cumulative metabolic impact (delta_S, cost, risk) across a session.
Fires a compulsory-reallocation signal when individually-reversible actions
add up to a collectively-irreversible consequence.

This closes the split-action bypass: 10 small edits = 1 large operation.

Reversible. State stored in /tmp/arifos_budgets/ with session isolation.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_BUDGET_DIR = Path("/tmp/arifos_budgets")
_BUDGET_DIR.mkdir(parents=True, exist_ok=True)

# Default ceilings per decision class
_DEFAULT_CEILINGS: dict[str, float] = {
    "C0": 0.05,  # Observation — very low risk
    "C1": 0.20,  # Reversible action
    "C2": 0.50,  # Consequential action
    "C3": 0.80,  # High-stakes action
    "C4": 1.00,  # Irreversible action — hard ceiling
}


def _budget_path(session_id: str) -> Path:
    safe_id = session_id.replace("/", "_").replace("..", "_") if session_id else "anonymous"
    return _BUDGET_DIR / f"{safe_id}.json"


def _load_budget(session_id: str | None) -> dict[str, Any]:
    """Load or initialize session budget ledger."""
    path = _budget_path(session_id or "anonymous")
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Budget ledger corrupt for %s: %s", session_id, exc)
    return {
        "session_id": session_id,
        "created_at": time.time(),
        "operations": [],
        "cumulative_delta_s": 0.0,
        "cumulative_cost": 0.0,
        "cumulative_risk": 0.0,
        "highest_decision_class": "C0",
        "breach_count": 0,
    }


def _save_budget(session_id: str | None, ledger: dict[str, Any]) -> None:
    path = _budget_path(session_id or "anonymous")
    try:
        path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.warning("Cannot write budget ledger for %s: %s", session_id, exc)


def _class_to_numeric(decision_class: str) -> int:
    mapping = {"C0": 0, "C1": 1, "C2": 2, "C3": 3, "C4": 4}
    return mapping.get(decision_class.upper(), 0)


async def arif_session_budget(
    mode: str = "status",
    decision_class: str = "C1",
    delta_s: float = 0.0,
    cost: float = 0.0,
    risk: float = 0.0,
    action_description: str = "",
    objective_id: str | None = None,
    ceiling_override: dict[str, float] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    F1/F07 BUDGET: Session-cumulative metabolic budget tracker.

    Modes:
      status   — Read current cumulative budget without adding.
      record   — Record a new operation and update cumulative totals.
      check    — Check if a hypothetical operation would breach ceiling.
      reset    — Reset ledger (requires actor_id = sovereign).

    Parameters:
      mode               — status | record | check | reset
      decision_class     — C0–C4 classification of the operation
      delta_s            — Thermodynamic entropy cost of this operation
      cost               — Estimated economic/compute cost
      risk               — Estimated risk score [0.0–1.0]
      action_description — Free-text description for audit trail
      objective_id       — Shared objective hash linking split operations
      ceiling_override   — Custom per-class ceilings
      session_id         — Governed session ID
      actor_id           — Sovereign actor identifier

    Returns:
      Budget ledger with breach detection, recommendation, and next_safe_action.
    """
    ledger = _load_budget(session_id)
    ceilings = {**_DEFAULT_CEILINGS, **(ceiling_override or {})}
    cls_numeric = _class_to_numeric(decision_class)
    ceiling = ceilings.get(decision_class.upper(), 0.5)

    if mode == "reset":
        if actor_id != "Arif":
            return {
                "status": "HOLD",
                "verdict": "HOLD",
                "reason": "Budget reset requires sovereign actor_id='Arif'.",
                "session_id": session_id,
                "actor_id": actor_id,
            }
        ledger = {
            "session_id": session_id,
            "created_at": time.time(),
            "operations": [],
            "cumulative_delta_s": 0.0,
            "cumulative_cost": 0.0,
            "cumulative_risk": 0.0,
            "highest_decision_class": "C0",
            "breach_count": 0,
        }
        _save_budget(session_id, ledger)
        return {
            "status": "SEAL",
            "verdict": "SEAL",
            "reason": "Budget ledger reset by sovereign.",
            "session_id": session_id,
            "actor_id": actor_id,
        }

    if mode == "record":
        op = {
            "timestamp": time.time(),
            "decision_class": decision_class.upper(),
            "delta_s": delta_s,
            "cost": cost,
            "risk": risk,
            "action_description": action_description,
            "objective_id": objective_id,
        }
        ledger["operations"].append(op)
        ledger["cumulative_delta_s"] = round(ledger["cumulative_delta_s"] + delta_s, 6)
        ledger["cumulative_cost"] = round(ledger["cumulative_cost"] + cost, 6)
        ledger["cumulative_risk"] = round(ledger["cumulative_risk"] + risk, 6)
        if cls_numeric > _class_to_numeric(ledger["highest_decision_class"]):
            ledger["highest_decision_class"] = decision_class.upper()
        _save_budget(session_id, ledger)

    # Breach detection
    total = ledger["cumulative_delta_s"] + ledger["cumulative_risk"]
    breached = total >= ceiling
    if breached:
        ledger["breach_count"] += 1
        _save_budget(session_id, ledger)

    # Split-action detection: same objective_id appearing >3 times
    objective_split_risk = False
    if objective_id and mode == "record":
        same_obj = [op for op in ledger["operations"] if op.get("objective_id") == objective_id]
        if len(same_obj) >= 3:
            objective_split_risk = True

    if breached or objective_split_risk:
        verdict = "HOLD"
        recommendation = (
            f"Cumulative metabolic impact ({total:.4f}) exceeds ceiling ({ceiling:.4f}) "
            f"for class {decision_class}. Force human checkpoint before proceeding."
        )
        if objective_split_risk:
            recommendation += (
                f" Objective '{objective_id}' has {len(same_obj)} recorded operations — "
                "split-action bypass suspected."
            )
        next_safe_action = "888_HOLD → arif_judge_deliberate → sovereign review"
    else:
        verdict = "SEAL"
        recommendation = (
            f"Cumulative impact ({total:.4f}) within ceiling ({ceiling:.4f}). "
            f"Session has {len(ledger['operations'])} operation(s)."
        )
        next_safe_action = "Proceed with standard governance."

    logger.info(
        "arif_session_budget mode=%s session=%s total=%.4f ceiling=%.4f verdict=%s",
        mode,
        session_id,
        total,
        ceiling,
        verdict,
    )

    return {
        "status": verdict,
        "verdict": verdict,
        "mode": mode,
        "decision_class": decision_class.upper(),
        "ceiling": ceiling,
        "cumulative_delta_s": ledger["cumulative_delta_s"],
        "cumulative_cost": ledger["cumulative_cost"],
        "cumulative_risk": ledger["cumulative_risk"],
        "total_impact": total,
        "breach_count": ledger["breach_count"],
        "operations_count": len(ledger["operations"]),
        "highest_decision_class": ledger["highest_decision_class"],
        "objective_split_risk": objective_split_risk,
        "objective_id": objective_id,
        "recommendation": recommendation,
        "next_safe_action": next_safe_action,
        "session_id": session_id,
        "actor_id": actor_id,
        "timestamp": time.time(),
    }


__all__ = ["arif_session_budget"]

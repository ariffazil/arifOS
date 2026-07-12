"""
arif_consequence_trace — Trace who makes the decision, who receives benefits,
who bears harm, and who can reverse it.

Core output: consequence_gap = decision_power x benefit_capture x harm_distance x non_accountability
This is a governance indicator, not a scientific constant.
"""

import uuid
from datetime import datetime, timezone


def _compute_consequence_gap(trace: dict) -> float:
    """Compute the consequence gap composite metric."""
    # Decision power: based on authority class
    authority_map = {
        "SOVEREIGN": 1.0, "EXECUTIVE": 0.8, "MANAGERIAL": 0.6,
        "ADVISORY": 0.3, "OPERATIONAL": 0.2, "OBSERVER": 0.1,
    }
    owner = trace.get("decision_owner", {})
    decision_power = authority_map.get(owner.get("authority_class", "OPERATIONAL"), 0.5)

    # Benefit capture: average magnitude of benefit bearers
    benefits = trace.get("benefit_bearers", [])
    if benefits:
        benefit_capture = sum(b.get("magnitude", 0) for b in benefits) / len(benefits)
    else:
        benefit_capture = 0.0

    # Harm distance: average consequence distance from cost bearers
    costs = trace.get("cost_bearers", [])
    if costs:
        harm_distance = sum(
            1.0 if c.get("reversibility") == "IRREVERSIBLE" else
            0.6 if c.get("reversibility") == "COSTLY" else 0.2
            for c in costs
        ) / len(costs)
    else:
        harm_distance = 0.0

    # Non-accountability: how many responsibility gaps exist
    gaps = len(trace.get("responsibility_gaps", []))
    non_accountability = min(1.0, gaps * 0.25)

    gap = decision_power * benefit_capture * harm_distance * (1.0 + non_accountability)
    return min(1.0, gap)


def arif_consequence_trace(
    decision_ref: str,
    decision_owner: dict | None = None,
    benefit_bearers: list[dict] | None = None,
    cost_bearers: list[dict] | None = None,
    reversal_owner: dict | None = None,
    responsibility_gaps: list[str] | None = None,
) -> dict:
    """
    Trace the full consequence chain of a decision.

    Args:
        decision_ref: Reference to the decision or action
        decision_owner: {ref, authority_class, awareness_of_consequences}
        benefit_bearers: [{ref, benefit_type, magnitude, exit_rights}]
        cost_bearers: [{ref, cost_type, magnitude, reversibility, awareness, compensation}]
        reversal_owner: {ref, can_reverse, reversal_cost}
        responsibility_gaps: List of unaccounted roles

    Returns:
        ConsequenceTrace dict conforming to consequence_trace.schema.json
    """
    trace = {
        "trace_id": f"ct-{uuid.uuid4().hex[:12]}",
        "decision_ref": decision_ref,
        "decision_owner": decision_owner or {"ref": "unknown", "authority_class": "OPERATIONAL"},
        "benefit_bearers": benefit_bearers or [],
        "cost_bearers": cost_bearers or [],
        "distance_score": 0.0,
        "reversal_owner": reversal_owner or {"ref": "unknown", "can_reverse": False, "reversal_cost": "UNKNOWN"},
        "responsibility_gaps": responsibility_gaps or [],
        "consequence_gap": 0.0,
        "metadata": {
            "traced_at": datetime.now(timezone.utc).isoformat(),
            "tracing_agent": "arif_consequence_trace",
        },
    }

    # Compute distance score
    costs = trace["cost_bearers"]
    if costs:
        # Distance = average awareness distance
        awareness_map = {"AWARE": 0.1, "PARTIALLY_AWARE": 0.4, "UNAWARE": 0.7, "SUPPRESSED": 0.95}
        trace["distance_score"] = round(
            sum(awareness_map.get(c.get("awareness", "UNAWARE"), 0.5) for c in costs) / len(costs),
            4
        )

    # Compute consequence gap
    trace["consequence_gap"] = round(_compute_consequence_gap(trace), 4)

    return trace

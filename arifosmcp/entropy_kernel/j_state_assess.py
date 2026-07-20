"""
arif_j_state_assess — Fuse organ observations into a judgment-integrity map.

Computes 5 J-planes using MINIMUM-FLOOR aggregation.
Never outputs a diagnosis or moral identity.
"""

import uuid
from datetime import UTC, datetime

# J-state thresholds
J_THRESHOLDS = {
    "J0": (0.0, 0.20),  # VOID recommended
    "J1": (0.20, 0.40),  # HOLD
    "J2": (0.40, 0.60),  # reversible observation only
    "J3": (0.60, 0.80),  # bounded execution
    "J4": (0.80, 1.01),  # witnessed execution
}

ACTION_MAP = {
    "J0": "VOID",
    "J1": "HOLD",
    "J2": "BOUNDED_PROCEED",
    "J3": "BOUNDED_PROCEED",
    "J4": "PROCEED_WITNESSED",
}

PLANES = [
    "reality_contact",
    "authority_legitimacy",
    "consequence_integration",
    "correctability",
    "purpose_fidelity",
]


def _compute_plane_score(plane: str, observations: list[dict]) -> float:
    """
    Compute a single J-plane score from contributing observations.
    Uses domain-specific heuristics per plane.
    Returns 0.0-1.0.
    """
    if not observations:
        return 0.5  # neutral when no evidence

    scores = []
    for obs in observations:
        consequence = obs.get("consequence", {})
        correction = obs.get("correction", {})
        epistemic = obs.get("epistemic", {})
        conf = epistemic.get("confidence", 0.5)

        if plane == "reality_contact":
            # Higher when contradictions are low, counterevidence exists
            contradictions = len(obs.get("evidence", {}).get("contradictions", []))
            counterevidence = len(obs.get("evidence", {}).get("counterevidence", []))
            base = max(0.1, 1.0 - (contradictions * 0.15) - (0.05 if counterevidence == 0 else 0))
            scores.append(base * conf)

        elif plane == "authority_legitimacy":
            # Inversely related to consequence_distance + authority_expansion
            dist = consequence.get("consequence_distance", 0.5)
            resp = correction.get("response_class", "NOT_TESTED")
            penalty = 0.3 if resp == "AUTHORITY_EXPANDED" else 0.0
            scores.append(max(0.0, (1.0 - dist) - penalty) * conf)

        elif plane == "consequence_integration":
            # Higher when decision-makers bear consequences
            dist = consequence.get("consequence_distance", 0.5)
            option_loss = consequence.get("option_loss", 0.0)
            feedback_loss = consequence.get("feedback_loss", 0.0)
            score = (1.0 - dist) * 0.5 + (1.0 - option_loss) * 0.25 + (1.0 - feedback_loss) * 0.25
            scores.append(max(0.0, score) * conf)

        elif plane == "correctability":
            # Based on correction response
            resp = correction.get("response_class", "NOT_TESTED")
            resp_scores = {
                "REFLECTED": 0.95,
                "CONTEXT_ADDED": 0.85,
                "ACCEPTED": 0.90,
                "PARTIALLY_ACCEPTED": 0.65,
                "DISMISSED": 0.25,
                "WITNESS_ATTACKED": 0.05,
                "AUTHORITY_EXPANDED": 0.10,
                "NOT_TESTED": 0.50,
            }
            scores.append(resp_scores.get(resp, 0.5) * conf)

        elif plane == "purpose_fidelity":
            # Higher when signal_class is not METRIC_PURPOSE_SUBSTITUTION
            dark = obs.get("dark_mode", "")
            signal = obs.get("signal_class", "")
            penalty = 0.4 if dark == "METRIC_PURPOSE_SUBSTITUTION" else 0.0
            penalty += 0.2 if signal == "FEEDBACK_CORRUPTION" else 0.0
            scores.append(max(0.0, 1.0 - penalty) * conf)

    return sum(scores) / len(scores) if scores else 0.5


def _classify_j_state(aggregate_score: float) -> str:
    """Classify aggregate score into J-state."""
    for state, (low, high) in J_THRESHOLDS.items():
        if low <= aggregate_score < high:
            return state
    return "J0"  # fallback to most conservative


def arif_j_state_assess(
    observation_refs: list[str],
    observations: list[dict],
    decision_ref: str,
    intended_purpose: str = "",
    claimed_authority: str = "",
    affected_parties: list[str] | None = None,
    action_reversibility: str = "REVERSIBLE",
) -> dict:
    """
    Fuse organ observations into a judgment-integrity map.

    Args:
        observation_refs: List of observation IDs
        observations: Full observation dicts for computation
        decision_ref: Decision or actor reference
        intended_purpose: Stated purpose of the action
        claimed_authority: Claimed authority for the action
        affected_parties: List of affected party references
        action_reversibility: REVERSIBLE | COSTLY | IRREVERSIBLE

    Returns:
        JudgmentIntegrity dict conforming to j_state.schema.json
    """
    # Compute each plane
    plane_scores = {}
    for plane in PLANES:
        plane_scores[plane] = round(_compute_plane_score(plane, observations), 4)

    # Weakest plane = minimum floor
    weakest = min(plane_scores, key=plane_scores.get)
    aggregate = plane_scores[weakest]  # MINIMUM-FLOOR, not average

    # Classify J-state
    state = _classify_j_state(aggregate)
    recommended_action = ACTION_MAP[state]

    # Irreversibility override: if action is IRREVERSIBLE and J < J3, force HOLD
    if action_reversibility == "IRREVERSIBLE" and state in ("J0", "J1", "J2"):
        recommended_action = "HOLD"
        if state == "J2":
            state = "J1"  # demote

    # Detect cross-organ contradictions
    contradiction_graph = []
    organs_seen = {}
    for obs in observations:
        organ = obs.get("organ", "UNKNOWN")
        for contra in obs.get("evidence", {}).get("contradictions", []):
            # Check if another organ has conflicting observation
            for other_organ, other_obs in organs_seen.items():
                if other_organ != organ:
                    contradiction_graph.append(
                        {
                            "claim_a": f"{organ}: {contra}",
                            "claim_b": f"{other_organ}: observation",
                            "contradiction_type": "cross_organ",
                            "severity": "HIGH" if aggregate < 0.4 else "MEDIUM",
                        }
                    )
        organs_seen[organ] = obs

    # Missing evidence analysis
    missing = []
    if not any(o.get("organ") == "GEOX" for o in observations):
        missing.append("No GEOX material reality anchor — physical consequences unverified")
    if not any(o.get("organ") == "WELL" for o in observations):
        missing.append("No WELL human state assessment — vitality signals absent")
    if not any(o.get("correction", {}).get("challenge_presented") for o in observations):
        missing.append("No correction probe attempted — correctability untested")

    return {
        "j_state_id": f"js-{uuid.uuid4().hex[:12]}",
        "subject_ref": decision_ref,
        "observation_refs": observation_refs,
        "planes": plane_scores,
        "weakest_plane": weakest,
        "aggregate_score": round(aggregate, 4),
        "aggregate_method": "MINIMUM_FLOOR",
        "state": state,
        "recommended_action": recommended_action,
        "missing_evidence": missing,
        "contradiction_graph": contradiction_graph,
        "prohibited_conclusions": [
            "hidden_niat_inferred",
            "evil_identity_declared",
            "psychiatric_diagnosis",
            "permanent_trust_classification",
        ],
        "metadata": {
            "assessed_at": datetime.now(UTC).isoformat(),
            "assessing_agent": "arif_j_state_assess",
            "schema_version": "v1",
        },
    }

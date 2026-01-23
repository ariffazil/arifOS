"""
arifOS v46 - Routing Signal (Evidence Layer)

Routing recommendations based on evidence physics.
These are NOT constitutional verdicts - only APEX PRIME issues verdicts.

ARCHITECTURAL SEPARATION:
- RoutingSignal: Evidence quality → Processing pathway (THIS MODULE)
- Verdict: Constitutional judgment → Legal authority (APEX PRIME ONLY)
"""

from enum import Enum


class RoutingSignal(Enum):
    """
    Evidence-based routing recommendations.

    These signals route execution pathways based on evidence quality,
    but they are NOT constitutional verdicts. Only APEX PRIME (via
    apex_review) may issue constitutional verdicts.

    Routing Pathways:
    - FAST_PATH: High-quality evidence, full coverage, no conflicts
    - SLOW_PATH: Degraded evidence (incomplete, stale, minor issues)
    - GOVERNED: Conflict detected, requires human oversight
    - BLOCKED: No evidence or critical quality failure
    """

    FAST_PATH = "FAST_PATH"      # Route to fast processing (high confidence)
    SLOW_PATH = "SLOW_PATH"      # Route to careful processing (degraded evidence)
    GOVERNED = "GOVERNED"        # Route to human oversight (conflict/high-stakes)
    BLOCKED = "BLOCKED"          # Block processing (no evidence/critical failure)


def routing_signal_to_pathway(signal: RoutingSignal) -> str:
    """
    Convert RoutingSignal to execution pathway name.

    Args:
        signal: Routing signal from evidence evaluation

    Returns:
        Pathway string (FAST, SLOW, GOVERNED)
    """
    pathway_map = {
        RoutingSignal.FAST_PATH: "FAST",
        RoutingSignal.SLOW_PATH: "SLOW",
        RoutingSignal.GOVERNED: "GOVERNED",
        RoutingSignal.BLOCKED: "GOVERNED",  # Blocked routes to governance
    }
    return pathway_map.get(signal, "SLOW")


__all__ = ["RoutingSignal", "routing_signal_to_pathway"]

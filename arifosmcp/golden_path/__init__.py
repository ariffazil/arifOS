"""
arifOS Golden Path — The Bridge Between Constitutional and Runtime 🔥⚒️
═══════════════════════════════════════════════════════════════════════

The 7 constitutional organs (prompts) define WHO does WHAT and WHY.
The golden path runtime defines HOW they connect, enforce, and learn.

SessionState — The typed object passed between all organs
GateEnforcer — Structural enforcement (777 cannot fire without SEAL)
LoopRouter   — Stage routing + metabolic termination
FloorScorer  — Measurable floor computation (heuristic v1)
AssumptionBridge — Cross-session learning (999 writes, 000 reads)

DITEMPA BUKAN DIBERI — Reality is forged, not given. 🔥⚒️
"""

from .session_state import (
    SessionState,
    StageRecord,
    FloorScore,
    Assumption,
    Verdict,
    Readiness,
    FloorStatus,
    Reversibility,
    BlastRadius,
    create_session,
)
from .gate_enforcer import (
    GateResult,
    GateCheck,
    GovernanceGateError,
    check_stage_entry,
    enforce_stage_entry,
    STAGE_REQUIREMENTS,
)
from .loop_router import (
    RouteAction,
    RoutingDecision,
    GOLDEN_PATH,
    route,
)
from .floor_scorer import (
    compute_floor_scores,
)
from .assumption_bridge import (
    write_assumptions,
    load_prior_assumptions,
    load_latest_assumptions,
    format_assumptions_for_context,
)

__all__ = [
    # Session state
    "SessionState",
    "StageRecord",
    "FloorScore",
    "Assumption",
    "Verdict",
    "Readiness",
    "FloorStatus",
    "Reversibility",
    "BlastRadius",
    "create_session",
    # Gate enforcement
    "GateResult",
    "GateCheck",
    "GovernanceGateError",
    "check_stage_entry",
    "enforce_stage_entry",
    "STAGE_REQUIREMENTS",
    # Loop routing
    "RouteAction",
    "RoutingDecision",
    "GOLDEN_PATH",
    "route",
    # Floor scoring
    "compute_floor_scores",
    # Assumption bridge
    "write_assumptions",
    "load_prior_assumptions",
    "load_latest_assumptions",
    "format_assumptions_for_context",
]

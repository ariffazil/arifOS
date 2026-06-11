"""
arifosmcp/geometry/ — Constitutional Geometry Engine (EUREKA-G / v0.1)

Ratified 2026-06-11 by 888 SOVEREIGN. 4 decisions:

  1. Dimension count:   13D (F01-F13). NOT 6D. F1/F11/F12 are constitutionally
                        distinct — collapsing them loses governance resolution.
  2. Polytope:         hard floor threshold = 0 (clean). Soft floors (F3, F5,
                        F6, F8) are quality signals, not violations.
  3. Weight authority: FLOOR_WEIGHTS lives in /opt/arifos/app/static/arifos/floors/
                        000_CONSTITUTION.md (F13-ratified, immutable from code).
                        This module loads them at import; if missing, refuses
                        to operate (F1 AMANAH fail-closed).
  4. Ablation gate:    EUREKA ABLATION_K_EPISODES = 10. A behavior is a Eureka
                        ONLY if the metric improvement disappears without it.

3 load-bearing corrections from ASI💃:

  - consolidate() does NOT re-shape preferred regions. It clusters episodic
    memory. RSI in arifOS = learning trajectory priors over a FIXED polytope.
    Polytope is F13-ratified. Trajectory priors are empirical.
  - Eureka detector v0 had no ablation. v0.1 requires ablation: must beat
    matched baseline by margin across k episodes. Otherwise: astrology.
  - 888 is a TRIGGER (drift fires during run, Eureka fires before promotion),
    not a post-hoc veto.

Constitutional binding:
  F1 AMANAH   additive only; F13-ratified weights cannot be edited in code
  F2 TRUTH    coords in [-1,+1] strictly; provenance_sha per point
  F4 CLARITY  ||gradient|| <= 0.30, F13 dim zeroed out
  F7 HUMILITY confidence cap 0.95
  F9 ANTIHANTU ToM depth cap = 2 (Gödel accumulator)
  F11 AUTH    provenance per point, evidence_chain per OtherGeometry
  F13 SOVEREIGN weights are F13-ratified, loaded from constitution file

Reversibility (F1): delete this dir + drop Qdrant collection = clean removal.
"""

from .manifold import (
    ABLATION_K_EPISODES,
    ABLATION_MARGIN,
    ALL_FLOORS,
    CONFIDENCE_CAP,
    DRIFT_STEP_THRESHOLD,
    DRIFT_TAU,
    DRIFT_TOTAL_THRESHOLD,
    EUREKA_STABILITY_K,
    EUREKA_STDDEV_MAX,
    EUREKA_TAU,
    GRADIENT_MAGNITUDE_CAP,
    HARD_FLOORS,
    HISTORY_DECAY_TAU_H,
    REGION_JUMP_TAU,
    SOFT_FLOORS,
    TOM_DEPTH_CAP,
    AgentState,
    Floor,
    Trajectory,
    delta_constitutional_region,
    distance,
    is_constitutional,
    violating_floors,
)

__all__ = [
    "HARD_FLOORS",
    "SOFT_FLOORS",
    "ALL_FLOORS",
    "Floor",
    "AgentState",
    "Trajectory",
    "distance",
    "delta_constitutional_region",
    "is_constitutional",
    "violating_floors",
    "GRADIENT_MAGNITUDE_CAP",
    "DRIFT_TAU",
    "REGION_JUMP_TAU",
    "DRIFT_STEP_THRESHOLD",
    "DRIFT_TOTAL_THRESHOLD",
    "EUREKA_TAU",
    "EUREKA_STABILITY_K",
    "ABLATION_K_EPISODES",
    "ABLATION_MARGIN",
    "EUREKA_STDDEV_MAX",
    "TOM_DEPTH_CAP",
    "HISTORY_DECAY_TAU_H",
    "CONFIDENCE_CAP",
]

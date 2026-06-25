"""
rama — Human Psychological Substrate for arifOS
═════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Forged, Not Given.

Operational human model across three layers:
  - SDT (needs): autonomy, competence, relatedness
  - Polyvagal (state): ventral, sympathetic, dorsal
  - Shadow (identity): persona, shadow, self

Runtime organs:
  - State Classifier: deterministic, rule-based, auditable
  - Response Adapter: posture shift based on state (Phase 2)
  - Shadow Detector: contradiction auditor (Phase 3)
"""

from arifosmcp.rama.state_classifier import StateClassifier, get_state_classifier
from arifosmcp.rama.state_classifier_governance import (
    GovernedPosture,
    GovernanceCheck,
    run_governance_loop,
)
from arifosmcp.rama.state_classifier_schemas import (
    AgentPosture,
    PolyvagalState,
    SDTPressure,
    SDTPressureVector,
    StateClassifierResult,
    StateVector,
)

__all__ = [
    # Schemas
    "AgentPosture",
    "PolyvagalState",
    "SDTPressure",
    "SDTPressureVector",
    "StateVector",
    "StateClassifierResult",
    # Classifier
    "StateClassifier",
    "get_state_classifier",
    # Governance
    "GovernedPosture",
    "GovernanceCheck",
    "run_governance_loop",
]

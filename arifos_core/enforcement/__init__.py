"""
arifos_core.enforcement - Floor & Verdict System (v46.0 Trinity Orthogonal)

Contains floor metrics and enforcement:
- metrics: Floor thresholds, Metrics dataclass
- genius_metrics: GENIUS LAW (G, C_dark, Psi)
- response_validator: Machine-enforced floor checks
- meta_governance: Tri-Witness cross-model aggregator
- trinity_orchestrator: v46 Trinity Orthogonal AAA (AGI·ASI·APEX)

Version: v46.0.0-DRAFT
"""

from .metrics import Metrics, FloorsVerdict, ConstitutionalMetrics
from .genius_metrics import (
    evaluate_genius_law,
    GeniusVerdict,
    compute_genius_index,
    compute_dark_cleverness,
    compute_psi_apex,
)
from .response_validator import (
    FloorReport,
    validate_response,
    validate_response_with_context,
)
from .meta_governance import (
    MetaVerdict,
    WitnessVote,
    MetaSelectionResult,
    meta_select,
    tri_witness_vote,
    quad_witness_vote,
)
# v46 Trinity Orthogonal (replaces floor_scorer.py)
from .trinity_orchestrator import (
    FloorResult,
    GradeResult,
    TrinityOrchestrator,
    TRINITY_ORCHESTRATOR,
    FLOOR_SCORER,
    grade_text,
    is_safe,
)

__all__ = [
    # Metrics
    "Metrics",
    "FloorsVerdict",
    "ConstitutionalMetrics",
    # GENIUS LAW
    "evaluate_genius_law",
    "GeniusVerdict",
    "compute_genius_index",
    "compute_dark_cleverness",
    "compute_psi_apex",
    # Response Validator
    "FloorReport",
    "validate_response",
    "validate_response_with_context",
    # Meta-Governance (Tri-Witness)
    "MetaVerdict",
    "WitnessVote",
    "MetaSelectionResult",
    "meta_select",
    "tri_witness_vote",
    "quad_witness_vote",
    # v46 Trinity Orchestrator (replaces floor_scorer.py)
    "FloorResult",
    "GradeResult",
    "TrinityOrchestrator",
    "TRINITY_ORCHESTRATOR",
    "FLOOR_SCORER",
    "grade_text",
    "is_safe",
]

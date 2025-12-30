"""
arifos_core.enforcement - Floor & Verdict System (v45.1)

Contains floor metrics and enforcement:
- metrics: Floor thresholds, Metrics dataclass
- genius_metrics: GENIUS LAW (G, C_dark, Psi)
- response_validator: Machine-enforced floor checks
- meta_governance: Tri-Witness cross-model aggregator

Version: v45.1.0
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
]

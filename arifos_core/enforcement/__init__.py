"""
arifos_core.enforcement - Floor & Verdict System

Contains floor metrics and enforcement:
- metrics: Floor thresholds, Metrics dataclass
- genius_metrics: GENIUS LAW (G, C_dark, Psi)

Version: v42.0.0
"""

from .metrics import Metrics, FloorsVerdict, ConstitutionalMetrics
from .genius_metrics import (
    evaluate_genius_law,
    GeniusVerdict,
    compute_genius_index,
    compute_dark_cleverness,
    compute_psi_apex,
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
]

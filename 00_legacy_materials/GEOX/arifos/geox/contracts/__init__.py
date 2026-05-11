"""
GEOX Contracts — Type definitions and schemas for host-agnostic tools.
DITEMPA BUKAN DIBERI
"""

from .types import (
    # Base
    GeoXResult,
    GeoXStatus,
    # Petrophysics
    SwModel,
    SwCalculationResult,
    SwModelAdmissibilityResult,
    PetrophysicsResult,
    CutoffValidationResult,
    PetrophysicsHoldResult,
    # Seismic
    SeismicLineResult,
    StructuralCandidatesResult,
    # Evaluation
    ProspectEvaluationResult,
    FeasibilityResult,
    GeospatialVerificationResult,
    # Memory
    MemoryQueryResult,
    # Health
    HealthResult,
    # App Intent
    AppIntent,
)

__all__ = [
    "GeoXResult",
    "GeoXStatus",
    "SwModel",
    "SwCalculationResult",
    "SwModelAdmissibilityResult",
    "PetrophysicsResult",
    "CutoffValidationResult",
    "PetrophysicsHoldResult",
    "SeismicLineResult",
    "StructuralCandidatesResult",
    "ProspectEvaluationResult",
    "FeasibilityResult",
    "GeospatialVerificationResult",
    "MemoryQueryResult",
    "HealthResult",
    "AppIntent",
]

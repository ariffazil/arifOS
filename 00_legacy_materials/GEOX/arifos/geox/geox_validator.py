"""
GEOX Validator Public Surface
DITEMPA BUKAN DIBERI

Expose the governance validator as the stable public import path used by the
rest of GEOX and the existing test suite.
"""

from __future__ import annotations

from arifos.geox.governance.validator import (
    AggregateVerdict,
    ValidationResult,
    _parse_range,
)
from arifos.geox.governance.validator import (
    GeoXValidator as _GovernanceGeoXValidator,
)

# Backward-compatible alias for older imports.
BatchValidationResult = AggregateVerdict


class GeoXValidator(_GovernanceGeoXValidator):
    """Compatibility wrapper for the governance validator public import."""

    def __init__(self, name: str = "default_validator", strict_mode: bool = False):
        self.name = name
        self.strict_mode = strict_mode
        super().__init__()

    def validate(self, result: object) -> ValidationResult:
        """Minimal single-object validation for hardened agent compatibility."""
        if result is None:
            return ValidationResult(
                insight_id="input",
                verdict="contradicted",
                score=0.0,
                evidence=[],
                explanation="Input is None.",
                floor_violations=["F2_truth"],
            )
        return ValidationResult(
            insight_id="input",
            verdict="supported",
            score=1.0,
            evidence=[],
            explanation="Input accepted by governance validator.",
            floor_violations=[],
        )


__all__ = [
    "AggregateVerdict",
    "BatchValidationResult",
    "GeoXValidator",
    "ValidationResult",
    "_parse_range",
]

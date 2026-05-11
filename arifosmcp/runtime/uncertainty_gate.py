from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

DEFAULT_CONFIDENCE_THRESHOLD = 0.75
MANDATORY_UNCERTAINTY_KEYS = (
    "level",
    "missing_inputs",
    "alternative_hypotheses",
)


@dataclass(frozen=True)
class UncertaintyCheck:
    status: str
    violations: list[str]


def validate_uncertainty(
    payload: Mapping[str, Any],
    *,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> list[str]:
    violations: list[str] = []

    confidence = payload.get("confidence")
    if not isinstance(confidence, int | float):
        return ["missing_or_invalid_confidence"]

    uncertainty = payload.get("uncertainty")
    if confidence < confidence_threshold:
        if not isinstance(uncertainty, Mapping):
            return ["uncertainty_block_required_below_confidence_threshold"]

        for key in MANDATORY_UNCERTAINTY_KEYS:
            if key not in uncertainty:
                violations.append(f"missing_uncertainty_key:{key}")

        if isinstance(uncertainty.get("missing_inputs"), list) and not uncertainty.get("missing_inputs"):
            violations.append("missing_inputs_must_not_be_empty_below_threshold")
        if isinstance(uncertainty.get("alternative_hypotheses"), list) and not uncertainty.get(
            "alternative_hypotheses"
        ):
            violations.append("alternative_hypotheses_must_not_be_empty_below_threshold")

    return violations


def enforce_uncertainty_gate(
    payload: Mapping[str, Any],
    *,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> UncertaintyCheck:
    violations = validate_uncertainty(payload, confidence_threshold=confidence_threshold)
    if violations:
        return UncertaintyCheck(status="HOLD", violations=violations)
    return UncertaintyCheck(status="OK", violations=[])

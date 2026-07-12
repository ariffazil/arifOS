"""Validate confidence objects — reject bare floats as first-class confidence."""

from __future__ import annotations

from typing import Any

ALLOWED_KINDS = frozenset(
    {
        "bayesian_posterior",
        "frequentist_rate",
        "model_output",
        "expert_judgment",
        "calibration_score",
        "heuristic",
        "unknown",
    }
)


def validate_confidence(obj: Any) -> tuple[bool, str]:
    """Return (ok, reason). Bare number → fail. Struct with kind → ok if well-formed."""
    if obj is None:
        return False, "confidence_missing"
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        return False, "bare_float_illegal_use_struct_with_kind"
    if not isinstance(obj, dict):
        return False, f"confidence_must_be_object_got_{type(obj).__name__}"
    if "value" not in obj:
        return False, "missing_value"
    try:
        v = float(obj["value"])
    except (TypeError, ValueError):
        return False, "value_not_numeric"
    if not 0.0 <= v <= 1.0:
        return False, "value_out_of_range_0_1"
    kind = obj.get("kind", "unknown")
    if kind not in ALLOWED_KINDS:
        return False, f"unknown_kind_{kind}"
    if "target" not in obj or not str(obj.get("target", "")).strip():
        return False, "missing_target"
    return True, "ok"


def validate_envelope_confidence(envelope: dict[str, Any]) -> tuple[bool, str]:
    """If envelope has confidence field, validate it."""
    if "confidence" not in envelope:
        return True, "no_confidence_field"
    return validate_confidence(envelope["confidence"])


def combine_illegal(a: Any, b: Any) -> bool:
    """True if combining these confidences would be epistemically illegal."""
    ok_a, _ = validate_confidence(a)
    ok_b, _ = validate_confidence(b)
    if not ok_a or not ok_b:
        return True
    # Different kinds without explicit meta-combination rule
    if a.get("kind") != b.get("kind"):
        return True
    if a.get("target") != b.get("target"):
        return True
    return False


if __name__ == "__main__":
    assert validate_confidence(0.78)[0] is False
    assert validate_confidence({"value": 0.78, "kind": "heuristic", "target": "readiness"})[0]
    assert combine_illegal(
        {"value": 0.78, "kind": "bayesian_posterior", "target": "reservoir"},
        {"value": 0.78, "kind": "model_output", "target": "reservoir"},
    )
    print("confidence_validator: ok")

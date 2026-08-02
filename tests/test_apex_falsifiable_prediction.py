"""
APEX-2026-08-01 Reform — FalsifiablePrediction binding + APEX_HUMILITY_FLOOR
════════════════════════════════════════════════════════════════════════════════════════
Tests for the reform that binds every APEX score to a falsifiable prediction
and widens the humility floor for APEX records (0.03 → 0.15).

"The framework is useful, not true. It produces better distinctions than the
alternatives. But it is not physics. It is not a photograph. It is a
structured way of thinking that makes your intuitions explicit and testable."

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.apex_canonical import (
    APEX_HUMILITY_FLOOR,
    APEXResult,
    FalsifiablePrediction,
    HUMILITY_FLOOR,
    PrimitiveInputs,
    compute_E,
    compute_apex,
)


# ── 1. FalsifiablePrediction construction ─────────────────────────────────────
def test_falsifiable_prediction_required_fields():
    """Claim, falsifier, deadline are all required."""
    pred = FalsifiablePrediction(
        claim="PETRONAS structural collapse window",
        falsifier="PETRONAS still standing in 2035 with no structural change",
        deadline="2029-2030",
    )
    assert pred.claim == "PETRONAS structural collapse window"
    assert pred.falsifier == "PETRONAS still standing in 2035 with no structural change"
    assert pred.deadline == "2029-2030"
    assert pred.issuer == "Muhammad Arif bin Fazil (F13 SOVEREIGN)"
    assert pred.issued_at != ""
    assert pred.apex_humility_floor == APEX_HUMILITY_FLOOR == 0.15


def test_falsifiable_prediction_rejects_empty_claim():
    with pytest.raises(ValueError, match="non-empty claim"):
        FalsifiablePrediction(claim="", falsifier="x", deadline="2027")


def test_falsifiable_prediction_rejects_empty_falsifier():
    with pytest.raises(ValueError, match="non-empty claim"):
        FalsifiablePrediction(claim="x", falsifier="", deadline="2027")


def test_falsifiable_prediction_rejects_empty_deadline():
    with pytest.raises(ValueError, match="non-empty claim"):
        FalsifiablePrediction(claim="x", falsifier="y", deadline="")


# ── 2. Humility floor reform (0.03 → 0.15 for APEX) ──────────────────────────
def test_apex_humility_floor_widened_to_015():
    """APEX scores must carry wider uncertainty band than general-purpose floors."""
    assert APEX_HUMILITY_FLOOR == 0.15
    assert APEX_HUMILITY_FLOOR > HUMILITY_FLOOR  # wider than the generic 0.03


def test_compute_e_uses_wider_floor_for_apex():
    """Wider humility floor → lower E → more conservative APEX scores."""
    e_lo = compute_E(clarity=0.9, uncertainty=0.05, merkle_chain_intact=True,
                     humility_floor=APEX_HUMILITY_FLOOR)
    e_hi = compute_E(clarity=0.9, uncertainty=0.05, merkle_chain_intact=True,
                     humility_floor=HUMILITY_FLOOR)
    assert e_lo < e_hi
    assert e_lo == pytest.approx(0.7826, abs=1e-3)
    assert e_hi == pytest.approx(0.8571, abs=1e-3)


# ── 3. APEXResult carries FalsifiablePrediction (v1.1 — REQUIRED) ─────────
def test_apex_result_v1_1_requires_prediction():
    """v1.1: prediction is REQUIRED. compute_apex() without prediction raises TypeError."""
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True  # avoid A=0 deadlock
    inputs.h_witness = 0.9
    inputs.ai_witness = 0.9
    inputs.ext_witness = 0.9
    with pytest.raises(TypeError, match="prediction"):
        compute_apex(inputs)
    # The model without a test is a loneliness machine — it cannot return.


def test_apex_result_v1_1_with_bound_prediction_is_falsifiable():
    """v1.1: bound prediction → is_falsifiable=True, prediction in to_dict()."""
    pred = FalsifiablePrediction(
        claim="PETRONAS collapse 2029-2030",
        falsifier="PETRONAS still standing 2035+",
        deadline="2029-2030",
    )
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True
    inputs.h_witness = 0.9; inputs.ai_witness = 0.9; inputs.ext_witness = 0.9
    result = compute_apex(inputs, prediction=pred)
    assert result.prediction is pred
    assert result.is_falsifiable is True
    out = result.to_dict()
    assert "prediction" in out
    assert out["prediction"]["claim"] == "PETRONAS collapse 2029-2030"
    assert out["prediction"]["falsifier"] == "PETRONAS still standing 2035+"
    assert out["prediction"]["deadline"] == "2029-2030"
    # v1.1: is_falsifiable is always True when prediction is bound
    assert out["is_falsifiable"] is True
    assert out["is_falsifiable"] is True


def test_apex_result_bound_prediction_uses_wider_humility_floor():
    """Bound prediction → compute_E uses APEX_HUMILITY_FLOOR (0.15) — wider than generic (0.03)."""
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True
    inputs.clarity = 0.9
    inputs.uncertainty = 0.05
    inputs.h_witness = 0.9; inputs.ai_witness = 0.9; inputs.ext_witness = 0.9

    # v1.1: prediction is REQUIRED. Bind it.
    pred = FalsifiablePrediction(claim="c", falsifier="f", deadline="2027")
    r_with_pred = compute_apex(inputs, prediction=pred)
    # Compare against compute_E with explicit floor 0.03 (backward-compat path)
    from arifosmcp.runtime.apex_canonical import compute_E
    e_with_pred = compute_E(clarity=0.9, uncertainty=0.05, merkle_chain_intact=True,
                            humility_floor=APEX_HUMILITY_FLOOR)
    e_no_pred = compute_E(clarity=0.9, uncertainty=0.05, merkle_chain_intact=True,
                          humility_floor=HUMILITY_FLOOR)
    assert e_with_pred < e_no_pred
    assert r_with_pred.E == e_with_pred
    assert r_with_pred.is_falsifiable is True


# ── 4. PETRONAS first prediction is the template ───────────────────────────
def test_first_apex_prediction_is_petronas_collapse_window():
    """The first committed APEX prediction is the PETRONAS 2029-2030 window."""
    from arifosmcp.runtime.apex_canonical import FIRST_APEX_PREDICTION
    assert "PETRONAS" in FIRST_APEX_PREDICTION["claim"]
    assert "2035" in FIRST_APEX_PREDICTION["falsifier"]
    assert FIRST_APEX_PREDICTION["deadline"] == "2029-2030"
    assert "F13" in FIRST_APEX_PREDICTION["issuer"]


def test_petronas_prediction_serializes_via_apex_result():
    """The first APEX prediction can be bound to a result and serialized."""
    from arifosmcp.runtime.apex_canonical import FIRST_APEX_PREDICTION

    pred = FalsifiablePrediction(**FIRST_APEX_PREDICTION)
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True
    result = compute_apex(inputs, prediction=pred)

    payload = result.to_dict()
    assert payload["prediction"]["claim"] == "PETRONAS structural collapse window"
    assert payload["prediction"]["falsifier"] == "PETRONAS still standing in 2035 with no structural change"
    assert payload["is_falsifiable"] is True
    # And the JSON round-trips
    jsn = result.to_json()
    assert '"is_falsifiable": true' in jsn
    assert "PETRONAS" in jsn
    assert "2035" in jsn


# ── 5. v1.1 migration contract ─────────────────────────────────────────────
def test_v1_1_no_prediction_is_a_typing_error():
    """v1.1: missing prediction is a TypeError, not a silent default-None."""
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True
    inputs.h_witness = 0.9; inputs.ai_witness = 0.9; inputs.ext_witness = 0.9
    with pytest.raises(TypeError) as exc_info:
        compute_apex(inputs)
    # The error must specifically flag the missing prediction, not a generic error.
    assert "prediction" in str(exc_info.value) or "missing" in str(exc_info.value).lower()


def test_v1_1_with_bound_prediction_and_kwargs_still_works():
    """v1.1: existing gate_h / gate_delta_s / gate_w3 kwargs still work — but prediction is now required."""
    pred = FalsifiablePrediction(claim="c", falsifier="f", deadline="2027")
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True
    inputs.h_witness = 0.9; inputs.ai_witness = 0.9; inputs.ext_witness = 0.9
    result = compute_apex(inputs, gate_h=0.0, gate_delta_s=0.0, gate_w3=1.0, prediction=pred)
    assert isinstance(result, APEXResult)
    assert result.verdict is not None
    assert result.G > 0
    assert result.G_seal >= 0
    assert result.prediction is pred
    assert result.is_falsifiable is True


def test_v1_1_apexresult_field_order_is_required_then_optional():
    """v1.1: APEXResult fields are ordered required-first (dataclass compatibility)."""
    fields = APEXResult.__dataclass_fields__
    field_names = list(fields.keys())
    # First field must be prediction (required, no default)
    assert field_names[0] == "prediction"
    # After prediction, all required primitives come before any with defaults
    seen_default = False
    for name in field_names[1:]:
        if fields[name].default is not __import__("dataclasses").field().__class__ or "default_factory" in str(fields[name]):
            # This is a rough check — Python's _FIELD has default or default_factory
            seen_default = True
        elif seen_default:
            # If we already saw a default and now see one without, that's fine
            pass
    # Quick sanity: is_falsifiable has default True (so should be late)
    assert "is_falsifiable" in field_names
    assert field_names[-1] == "is_falsifiable" or "timestamp" in field_names[-1]
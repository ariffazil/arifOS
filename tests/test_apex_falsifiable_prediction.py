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


# ── 3. APEXResult carries FalsifiablePrediction ─────────────────────────────
def test_apex_result_default_prediction_is_none_for_backcompat():
    """Pre-reform records still work — prediction defaults to None."""
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True  # avoid A=0 deadlock
    result = compute_apex(inputs)
    assert result.prediction is None
    assert result.is_falsifiable is False


def test_apex_result_with_bound_prediction_is_falsifiable():
    """Bound prediction → is_falsifiable=True, prediction in to_dict()."""
    pred = FalsifiablePrediction(
        claim="PETRONAS collapse 2029-2030",
        falsifier="PETRONAS still standing 2035+",
        deadline="2029-2030",
    )
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True
    result = compute_apex(inputs, prediction=pred)
    assert result.prediction is pred
    assert result.is_falsifiable is True
    out = result.to_dict()
    assert "prediction" in out
    assert out["prediction"]["claim"] == "PETRONAS collapse 2029-2030"
    assert out["prediction"]["falsifier"] == "PETRONAS still standing 2035+"
    assert out["prediction"]["deadline"] == "2029-2030"
    assert out["is_falsifiable"] is True


def test_apex_result_bound_prediction_uses_wider_humility_floor():
    """Bound prediction → compute_E uses APEX_HUMILITY_FLOOR → lower E."""
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True
    inputs.clarity = 0.9
    inputs.uncertainty = 0.05

    # Without prediction → uses HUMILITY_FLOOR (0.03)
    r_no_pred = compute_apex(inputs)
    # With prediction → uses APEX_HUMILITY_FLOOR (0.15)
    pred = FalsifiablePrediction(claim="c", falsifier="f", deadline="2027")
    r_with_pred = compute_apex(inputs, prediction=pred)

    assert r_with_pred.E < r_no_pred.E
    assert r_with_pred.is_falsifiable is True
    assert r_no_pred.is_falsifiable is False


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


# ── 5. The reform does not break existing callers ──────────────────────────
def test_compute_apex_signature_backward_compatible():
    """Existing callers (no prediction kwarg) still produce valid results."""
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True
    inputs.h_witness = 0.9
    inputs.ai_witness = 0.9
    inputs.ext_witness = 0.9
    result = compute_apex(inputs)  # no prediction
    assert isinstance(result, APEXResult)
    assert result.verdict is not None
    assert result.G > 0


def test_compute_apex_with_kwargs_still_works():
    """Existing gate_h / gate_delta_s / gate_w3 kwargs still work."""
    inputs = PrimitiveInputs()
    inputs.sovereign_override = True
    inputs.h_witness = 0.9
    inputs.ai_witness = 0.9
    inputs.ext_witness = 0.9
    result = compute_apex(inputs, gate_h=0.0, gate_delta_s=0.0, gate_w3=1.0)
    assert result.G_seal > 0
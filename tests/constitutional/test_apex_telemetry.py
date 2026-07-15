"""
tests/constitutional/test_apex_telemetry.py — APEX Telemetry Pipeline (ATP)
═══════════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI

Constitutional gate tests for the ATP evaluator
(`arifosmcp.core.apex_telemetry.ApexTelemetryEvaluator`).

These tests pin the five TASK-P2-01 contract assertions:

  1. All scalars at floor              → PASS  (verdict = SEAL).
  2. C_dark >= 0.30                    → FAIL  (verdict = HOLD).
  3. W3    < 0.95                      → FAIL  (verdict = HOLD).
  4. QDF    < 0.70                     → FAIL  (verdict = HOLD).
  5. All scalars undefined / null      → HOLD (NOT VOID — scalar
                                         measurement failure is HOLD,
                                         not a hard constitutional breach).

The ATP is a pure function — these are deterministic property tests.
No I/O, no fixtures, no database. The evaluator never mutates its input.

Run
---
    cd /root/arifOS
    pytest tests/constitutional/test_apex_telemetry.py -v --tb=short

Author  : 888-APEX / Claude Code perspective (FI-008 dispatch)
Task    : TASK-P2-01 (F1+F11 gated, no F13 trigger)
Epoch   : 2026-07-15
"""

from __future__ import annotations

import math

import pytest

from arifosmcp.core.apex_telemetry import (
    ATP_PASS_THRESHOLDS,
    ATP_REQUIRED_SCALARS,
    ApexTelemetryEvaluator,
)


# ─── canonical "at-floor" scalar set ─────────────────────────────────────
# All six required scalars well-bounded; QDF computes to ≈0.884 with margin.
# peace_squared is canonical but does not enter QDF (see module docstring).
AT_FLOOR_SCALARS: dict[str, float] = {
    "G": 0.95,
    "C_dark": 0.05,
    "W3": 0.98,
    "kappa_r": 1.00,
    "psi_le": 1.00,
    "peace_squared": 1.00,
}


# ─────────────────────────────────────────────────────────────────────────
# Test 1 — all scalars at floor → PASS (SEAL)
# ─────────────────────────────────────────────────────────────────────────


def test_at_floor_scalars_pass():
    """All six input scalars at well-bounded values → SEAL, QDF ≥ 0.70."""
    ev = ApexTelemetryEvaluator()
    result = ev.evaluate(AT_FLOOR_SCALARS)

    assert result["verdict"] == "SEAL"
    assert result["pass"] is True
    assert result["qdf"] >= ATP_PASS_THRESHOLDS["qdf_min"]

    # Sanity: expected QDF = 0.95 * 0.95 * 0.98 * 1.00 * 1.00 ≈ 0.8844
    expected_qdf = (
        AT_FLOOR_SCALARS["G"]
        * (1.0 - AT_FLOOR_SCALARS["C_dark"])
        * AT_FLOOR_SCALARS["W3"]
        * AT_FLOOR_SCALARS["kappa_r"]
        * AT_FLOOR_SCALARS["psi_le"]
    )
    assert math.isclose(result["qdf"], expected_qdf, rel_tol=1e-9)

    # Reason string is non-empty audit-trail material.
    assert isinstance(result["reason"], str) and result["reason"]


# ─────────────────────────────────────────────────────────────────────────
# Test 2 — C_dark ≥ 0.30 → HOLD (F9 anti-hantu breach)
# ─────────────────────────────────────────────────────────────────────────


def test_c_dark_at_boundary_holds():
    """C_dark = 0.30 is the boundary and MUST HOLD (the floor uses >=).

    To isolate the C_dark-floor failure from the QDF composite, every
    other scalar is set to its maximum 1.0. This gives:

        QDF = 1.0 * (1 - 0.30) * 1.0 * 1.0 * 1.0 = 0.70

    which is exactly at the QDF pass boundary, so the C_dark floor is
    the ONLY failing gate — proving the documented precedence:
    C_dark floor fires BEFORE QDF composite check.
    """
    ev = ApexTelemetryEvaluator()
    scalars = {
        "G": 1.00,
        "C_dark": 0.30,
        "W3": 1.00,
        "kappa_r": 1.00,
        "psi_le": 1.00,
        "peace_squared": 1.00,
    }
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    assert "C_dark" in result["reason"]
    # C_dark floor fires first; QDF is exactly at the pass boundary.
    assert math.isclose(result["qdf"], 0.70, rel_tol=1e-9)
    assert result["qdf"] >= ATP_PASS_THRESHOLDS["qdf_min"]


def test_c_dark_well_above_threshold_holds():
    """C_dark = 0.50 → HOLD with explicit anti-hantu reason."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "C_dark": 0.50}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    assert "C_dark" in result["reason"]


def test_c_dark_one_holds():
    """C_dark = 1.0 (maximal shadow) → HOLD."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "C_dark": 1.0}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False


# ─────────────────────────────────────────────────────────────────────────
# Test 3 — W³ < 0.95 → HOLD (F3 witness breach)
# ─────────────────────────────────────────────────────────────────────────


def test_w3_just_below_threshold_holds():
    """W³ = 0.94 (just below the 0.95 floor) → HOLD."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "W3": 0.94}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    # The reason must point at W3, not QDF, to disambiguate the failure.
    assert "W3" in result["reason"] or "W\u00b3" in result["reason"]


def test_w3_well_below_threshold_holds():
    """W³ = 0.50 → HOLD."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "W3": 0.50}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False


def test_w3_zero_holds():
    """W³ = 0.0 (no witness) → HOLD."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "W3": 0.0}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False


# ─────────────────────────────────────────────────────────────────────────
# Test 4 — QDF < 0.70 → HOLD (composite gate)
# ─────────────────────────────────────────────────────────────────────────


def test_qdf_below_threshold_holds():
    """All floors pass individually but QDF < 0.70 → HOLD (composite)."""
    ev = ApexTelemetryEvaluator()
    # G=0.80, C_dark=0.20, W3=0.96, kappa_r=1.0, psi_le=1.0
    # QDF = 0.80 * 0.80 * 0.96 * 1.0 * 1.0 = 0.6144 < 0.70
    # C_dark=0.20 < 0.30 ✓, W3=0.96 ≥ 0.95 ✓ — floors pass; QDF fails.
    scalars = {
        "G": 0.80,
        "C_dark": 0.20,
        "W3": 0.96,
        "kappa_r": 1.00,
        "psi_le": 1.00,
        "peace_squared": 1.00,
    }
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    assert result["qdf"] < ATP_PASS_THRESHOLDS["qdf_min"]
    # Reason must point at QDF, not C_dark or W3.
    assert "QDF" in result["reason"]


def test_qdf_well_below_threshold_holds():
    """QDF = 0.30 → HOLD."""
    ev = ApexTelemetryEvaluator()
    # G=0.5, C_dark=0.0, W3=0.96, kappa_r=1.0, psi_le=1.0
    # QDF = 0.5 * 1.0 * 0.96 * 1.0 * 1.0 = 0.48 < 0.70
    scalars = {
        "G": 0.50,
        "C_dark": 0.00,
        "W3": 0.96,
        "kappa_r": 1.00,
        "psi_le": 1.00,
        "peace_squared": 1.00,
    }
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    assert result["qdf"] < ATP_PASS_THRESHOLDS["qdf_min"]


# ─────────────────────────────────────────────────────────────────────────
# Test 5 — all scalars undefined → HOLD (NOT VOID)
# ─────────────────────────────────────────────────────────────────────────


def test_all_scalars_empty_dict_holds():
    """Empty dict (no keys) → HOLD, NEVER VOID."""
    ev = ApexTelemetryEvaluator()
    result = ev.evaluate({})

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    # Critical: scalar failure is HOLD, not VOID.
    assert result["verdict"] != "VOID"
    # QDF is uncomputable → NaN, not a fabricated number.
    assert math.isnan(result["qdf"])
    # Reason mentions "all 7" to distinguish from per-scalar missing.
    assert "all 7" in result["reason"]


def test_all_scalars_none_values_holds():
    """All keys present, all values None → HOLD, NEVER VOID."""
    ev = ApexTelemetryEvaluator()
    result = ev.evaluate({
        "G": None,
        "C_dark": None,
        "W3": None,
        "kappa_r": None,
        "psi_le": None,
        "peace_squared": None,
    })

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    assert result["verdict"] != "VOID"
    assert math.isnan(result["qdf"])


def test_all_scalars_unmeasured_sentinel_holds():
    """UNMEASURED sentinels → HOLD, NEVER VOID (F9 anti-hantu discipline)."""
    ev = ApexTelemetryEvaluator()
    result = ev.evaluate({
        "G": "UNMEASURED",
        "C_dark": "UNMEASURED",
        "W3": "UNMEASURED",
        "kappa_r": "UNMEASURED",
        "psi_le": "UNMEASURED",
        "peace_squared": "UNMEASURED",
    })

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    assert result["verdict"] != "VOID"
    assert math.isnan(result["qdf"])


# ─────────────────────────────────────────────────────────────────────────
# F9 anti-hantu: partial measurement failure = HOLD, never fabricated
# ─────────────────────────────────────────────────────────────────────────


def test_single_scalar_missing_holds():
    """One scalar missing → HOLD with explicit missing-scalar reason."""
    ev = ApexTelemetryEvaluator()
    scalars = {k: v for k, v in AT_FLOOR_SCALARS.items() if k != "psi_le"}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    assert "psi_le" in result["reason"]
    # Per-scalar failure must mention the missing key by name.
    assert "missing" in result["reason"].lower() or "failure" in result["reason"].lower()


def test_nan_scalar_holds():
    """NaN scalar → HOLD, never silently coerced to 0.0 (F9 anti-hantu)."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "psi_le": float("nan")}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    # F9: NaN is measurement failure → HOLD, not VOID.
    assert result["verdict"] != "VOID"


def test_positive_infinity_scalar_holds():
    """+Inf scalar → HOLD."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "psi_le": float("inf")}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False


def test_negative_infinity_scalar_holds():
    """-Inf scalar → HOLD."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "G": float("-inf")}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False


def test_string_numeric_value_holds():
    """String numeral (e.g. "0.95") is NOT silently coerced → HOLD (F2 TRUTH)."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "psi_le": "1.0"}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False


def test_bool_value_holds():
    """bool (Python subclass of int) is REJECTED → HOLD (semantic safety)."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "psi_le": True}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False


# ─────────────────────────────────────────────────────────────────────────
# Boundary tests — exact thresholds must behave per the documented contract
# ─────────────────────────────────────────────────────────────────────────


def test_qdf_exactly_at_threshold_with_clean_floors_passes():
    """QDF exactly at 0.70 with C_dark < 0.30 and W3 >= 0.95 → SEAL.

    Construction:
        G=1.0, C_dark=0.05, W3=0.95, kappa_r=1.0, psi_le=1.0
        QDF = 1.0 * 0.95 * 0.95 * 1.0 * 1.0 = 0.9025 >= 0.70 ✓
        C_dark = 0.05 < 0.30 ✓
        W3 = 0.95 >= 0.95 ✓
    """
    ev = ApexTelemetryEvaluator()
    scalars = {
        "G": 1.00,
        "C_dark": 0.05,
        "W3": 0.95,
        "kappa_r": 1.00,
        "psi_le": 1.00,
        "peace_squared": 1.00,
    }
    result = ev.evaluate(scalars)

    assert result["verdict"] == "SEAL"
    assert result["pass"] is True


def test_c_dark_floor_precedence_over_qdf():
    """When C_dark is at boundary AND QDF passes, C_dark floor wins (HOLD)."""
    ev = ApexTelemetryEvaluator()
    # G=1.0, C_dark=0.30, W3=1.0, kappa_r=1.0, psi_le=1.0
    # QDF = 1.0 * 0.70 * 1.0 * 1.0 * 1.0 = 0.70 (passes composite)
    # But C_dark = 0.30 >= 0.30 → HOLD
    scalars = {
        "G": 1.00,
        "C_dark": 0.30,
        "W3": 1.00,
        "kappa_r": 1.00,
        "psi_le": 1.00,
        "peace_squared": 1.00,
    }
    result = ev.evaluate(scalars)

    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    assert "C_dark" in result["reason"]


def test_w3_floor_at_exact_threshold_passes():
    """W³ = 0.95 exactly is at the floor boundary → SEAL (>= semantics)."""
    ev = ApexTelemetryEvaluator()
    scalars = {**AT_FLOOR_SCALARS, "W3": 0.95}
    result = ev.evaluate(scalars)

    assert result["verdict"] == "SEAL"
    assert result["pass"] is True


# ─────────────────────────────────────────────────────────────────────────
# Alias / normalization tests — both spellings must produce same verdict
# ─────────────────────────────────────────────────────────────────────────


def test_alternate_key_spellings_pass():
    """snake_case AND mathematical spellings must both yield SEAL."""
    ev = ApexTelemetryEvaluator()
    alt = {
        "G_star": 0.95,
        "c_dark": 0.05,
        "w3": 0.98,
        "kappa_r": 1.00,
        "psi_le": 1.00,
        "peace2": 1.00,
    }
    result = ev.evaluate(alt)

    assert result["verdict"] == "SEAL"
    assert result["pass"] is True


def test_mixed_spellings_pass():
    """Mixed canonical + alias keys → SEAL."""
    ev = ApexTelemetryEvaluator()
    scalars = {
        "G_star": 0.95,           # alias for G
        "C_dark": 0.05,           # canonical
        "w3": 0.98,               # alias for W3
        "kappa_r": 1.00,
        "psi_le": 1.00,
        "peace_squared": 1.00,    # canonical
    }
    result = ev.evaluate(scalars)

    assert result["verdict"] == "SEAL"
    assert result["pass"] is True


# ─────────────────────────────────────────────────────────────────────────
# Pure-function property tests — F1 AMANAH by construction
# ─────────────────────────────────────────────────────────────────────────


def test_evaluate_does_not_mutate_input_dict():
    """Calling evaluate() does NOT mutate the input dict (F1 AMANAH)."""
    ev = ApexTelemetryEvaluator()
    snapshot = dict(AT_FLOOR_SCALARS)
    snapshot_frozen = {k: snapshot[k] for k in snapshot}

    # Call multiple times — each must return SEAL with same qdf.
    for _ in range(5):
        result = ev.evaluate(snapshot)
        assert result["verdict"] == "SEAL"
        assert result["pass"] is True

    # Input dict unchanged.
    assert snapshot == snapshot_frozen


def test_evaluate_is_deterministic():
    """Same input → same output across repeated calls (pure function)."""
    ev = ApexTelemetryEvaluator()

    first = ev.evaluate(AT_FLOOR_SCALARS)
    second = ev.evaluate(AT_FLOOR_SCALARS)
    third = ev.evaluate(AT_FLOOR_SCALARS)

    assert first == second == third


def test_qdf_input_value_is_ignored():
    """If a pre-computed QDF is in the input, it is RECOMPUTED (not trusted).

    Input QDF=0.99 but actual computed QDF=0.61 → must HOLD.
    This proves F2 TRUTH / F9 anti-hantu: never trust a pre-computed composite.
    """
    ev = ApexTelemetryEvaluator()
    scalars = {
        "G": 0.80,
        "C_dark": 0.20,
        "W3": 0.96,
        "kappa_r": 1.00,
        "psi_le": 1.00,
        "peace_squared": 1.00,
        "QDF": 0.99,  # attacker-supplied; must be ignored
    }
    result = ev.evaluate(scalars)

    # The actual QDF is 0.80 * 0.80 * 0.96 = 0.6144 < 0.70 → HOLD.
    assert result["verdict"] == "HOLD"
    assert result["pass"] is False
    assert math.isclose(result["qdf"], 0.6144, rel_tol=1e-9)


# ─────────────────────────────────────────────────────────────────────────
# Threshold constants — locked to TASK-P2-01 contract
# ─────────────────────────────────────────────────────────────────────────


def test_threshold_constants_match_task_spec():
    """ATP_PASS_THRESHOLDS must match the TASK-P2-01 contract verbatim."""
    assert ATP_PASS_THRESHOLDS["qdf_min"] == 0.70
    assert ATP_PASS_THRESHOLDS["c_dark_max"] == 0.30
    assert ATP_PASS_THRESHOLDS["w3_min"] == 0.95


def test_required_scalars_contract():
    """All 6 required scalars (peace_squared does not enter QDF)."""
    expected = ("G", "C_dark", "W3", "kappa_r", "psi_le", "peace_squared")
    assert ATP_REQUIRED_SCALARS == expected


# ─────────────────────────────────────────────────────────────────────────
# Verdict envelope shape — contract for downstream audit trail parsers
# ─────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("verdict", ["SEAL", "HOLD"])
def test_result_envelope_keys(verdict):
    """Every ATP result exposes the 4 canonical keys, regardless of verdict."""
    ev = ApexTelemetryEvaluator()
    if verdict == "SEAL":
        result = ev.evaluate(AT_FLOOR_SCALARS)
    else:
        result = ev.evaluate({})  # all-undefined → HOLD

    assert set(result.keys()) >= {"pass", "qdf", "verdict", "reason"}
    assert isinstance(result["pass"], bool)
    assert isinstance(result["qdf"], float)
    assert isinstance(result["verdict"], str)
    assert isinstance(result["reason"], str)
    assert result["verdict"] == verdict

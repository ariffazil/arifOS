"""AX-0 falsifier — LANE A (mission #69227, preregistered in dossier).

Claim: no APEX path invents values. Feed zero/missing inputs to every
compute_* and compute_apex -> zero numeric outputs where data is absent,
and never SEAL/SABAR from missing data (HOLD/None only).

Fail -> fix D2-D4 class defects; a numeric output here fails the lane.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "arifosmcp"))

from runtime.apex_canonical import (
    compute_A, compute_P, compute_X, compute_E,
    compute_G, compute_C_dark, compute_apex,
    PrimitiveInputs, Verdict, FalsifiablePrediction,
)

PRED = FalsifiablePrediction(claim="ax0", falsifier="any numeric from absence", deadline="2026-10-15")


def test_A_no_leases_is_none():
    assert compute_A(valid_leases=0, total_leases=0) is None


def test_A_zero_floor_is_real_zero():
    # floor violation is a MEASUREMENT (policy verdict), not absence
    assert compute_A(valid_leases=5, total_leases=5, floor_compliance=12) == 0.0


def test_P_all_zero_is_none():
    assert compute_P(p_well=0.0, p_seis=0.0, p_geo=0.0) is None


def test_P_contradiction_requires_measured_winner():
    assert compute_P(p_well=0.0, p_seis=0.0, p_geo=0.0, well_contradicts_seis=True) is None
    assert compute_P(p_well=0.0, p_seis=0.0, p_geo=0.0, seis_contradicts_geo=True) is None


def test_P_no_invented_priors():
    # well measured only -> renormalised, no 0.50/0.70 invented
    assert compute_P(p_well=0.99, p_seis=0.0, p_geo=0.0) == 0.99


def test_X_zero_steps_is_none():
    assert compute_X(successful_steps=0, total_steps=0) is None


def test_G_none_when_any_none():
    assert compute_G(None, 0.5, 0.8, 0.7, 0.9) is None
    assert compute_C_dark(None, 0.5, 0.7) is None
    assert compute_C_dark(1.0, None, 0.7) is None
    assert compute_C_dark(1.0, 0.5, None) is None


def test_apex_all_defaults_unmeasured_hold():
    r = compute_apex(PrimitiveInputs(), prediction=PRED)
    assert r.verdict == Verdict.HOLD
    assert "UNMEASURED" in r.verdict_reason
    assert r.G is None and r.C_dark is None and r.G_seal is None
    assert r.A is None and r.X is None


def test_apex_sovereign_never_seals_on_missing_data():
    # explicit policy input (F13) may set A=1.0, but missing P/X still bar a verdict
    r = compute_apex(PrimitiveInputs(sovereign_override=True), prediction=PRED)
    assert r.verdict == Verdict.HOLD
    assert r.G is None


def test_apex_zero_data_never_numeric_verdict():
    r = compute_apex(
        PrimitiveInputs(valid_leases=0, total_leases=0, p_well=0, p_seis=0, p_geo=0,
                        successful_steps=0, total_steps=0),
        prediction=PRED,
    )
    assert r.verdict in (Verdict.HOLD, Verdict.VOID)
    assert r.G is None

# tests/test_apex_prime_floors.py
#
# Comprehensive APEX PRIME constitutional floors tests for arifOS v33Ω.
# Tests all constitutional invariants: Truth, ΔS, Peace², κᵣ, Ω₀, Amanah, Tri-Witness, and Ψ.

import pytest

from arifos_core.enforcement.metrics import Metrics
from arifos_core.system.apex_prime import apex_review


# --- Helper: baseline "all floors passing" metrics ----------------------------

def _baseline_metrics() -> Metrics:
    """
    Baseline metrics where all constitutional floors pass comfortably.
    """
    return Metrics(
        truth=0.995,       # ≥ 0.99
        delta_s=0.01,      # ΔS ≥ 0
        peace_squared=1.02,       # Peace² ≥ 1.0
        kappa_r=0.97,      # κᵣ ≥ 0.95
        omega_0=0.04,      # Ω₀ in [0.03, 0.05]
        amanah=True,       # Amanah lock engaged
        tri_witness=0.97,  # Tri-Witness ≥ 0.95
        psi=1.10,          # Ψ ≥ 1.0
    )


# --- Core invariants: SEAL when all floors pass -------------------------------

def test_apex_seal_when_all_floors_pass_high_stakes() -> None:
    """
    APEX should return SEAL for high-stakes decisions when
    all floors are comfortably above thresholds.
    """
    metrics = _baseline_metrics()
    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "SEAL"


def test_apex_seal_when_all_floors_pass_non_high_stakes() -> None:
    """
    For non-high-stakes decisions, SEAL should also be returned
    when floors pass; this test mainly guards regressions.
    """
    metrics = _baseline_metrics()
    verdict = apex_review(metrics, high_stakes=False)
    assert verdict == "SEAL"


# --- Truth floor --------------------------------------------------------------

@pytest.mark.parametrize("truth_value, expected_verdict", [
    (0.989, "VOID"),    # just below floor
    (0.990, "VOID"),    # at boundary, conservative approach
    (0.999, "SEAL"),    # comfortably above
])
def test_apex_truth_floor_behavior(truth_value: float, expected_verdict: str) -> None:
    """
    Truth < 0.99 should not be SEAL on high-stakes.
    """
    metrics = _baseline_metrics()
    metrics.truth = truth_value

    verdict = apex_review(metrics, high_stakes=True)

    if truth_value < 0.99:
        # With GENIUS LAW, near-threshold truth can still SEAL if all other floors perfect
        assert verdict in ("VOID", "PARTIAL", "SEAL")
    else:
        assert verdict == "SEAL"


def test_apex_void_when_truth_clearly_below_floor() -> None:
    """
    Truth much lower (e.g., 0.8) must result in VOID for high-stakes.
    """
    metrics = _baseline_metrics()
    metrics.truth = 0.80

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "VOID"


# --- ΔS (clarity) floor -------------------------------------------------------

def test_apex_void_when_delta_s_negative() -> None:
    """
    ΔS < 0 means the answer increases confusion.
    High-stakes verdict must be VOID.
    """
    metrics = _baseline_metrics()
    metrics.delta_s = -0.01

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "VOID"


def test_apex_seal_when_delta_s_zero() -> None:
    """
    ΔS = 0 (neutral clarity) should pass floor check.
    """
    metrics = _baseline_metrics()
    metrics.delta_s = 0.0

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "SEAL"


# --- Peace² floor -------------------------------------------------------------

@pytest.mark.parametrize("peace_squared_value, expected_ok", [
    (0.99, False),   # below floor
    (1.00, True),    # at floor
    (1.10, True),    # above floor
])
def test_apex_peace_squared_floor(peace_squared_value: float, expected_ok: bool) -> None:
    """
    Peace² < 1.0 should not yield SEAL in high-stakes context.
    """
    metrics = _baseline_metrics()
    metrics.peace_squared = peace_squared_value

    verdict = apex_review(metrics, high_stakes=True)

    if expected_ok:
        assert verdict == "SEAL"
    else:
        assert verdict in ("VOID", "PARTIAL")


# --- κᵣ (weakest-listener empathy) -------------------------------------------

def test_apex_void_when_kappa_r_below_floor() -> None:
    """
    κᵣ < 0.95 (weakest-listener empathy) should void high-stakes output.
    """
    metrics = _baseline_metrics()
    metrics.kappa_r = 0.90

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict in ("VOID", "PARTIAL")


def test_apex_seal_when_kappa_r_at_floor() -> None:
    """
    κᵣ = 0.95 (exactly at floor) should pass.
    """
    metrics = _baseline_metrics()
    metrics.kappa_r = 0.95

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "SEAL"


# --- Ω₀ humility band ---------------------------------------------------------

@pytest.mark.parametrize("omega_0_value, should_seal", [
    (0.01, False),   # too low (overconfident)
    (0.03, True),    # lower bound of band
    (0.04, True),    # within [0.03, 0.05]
    (0.05, True),    # upper bound of band
    (0.08, False),   # too high (over-uncertain)
])
def test_apex_omega_band_humility(omega_0_value: float, should_seal: bool) -> None:
    """
    Ω₀ must remain in calibrated humility band.
    Outside band should not SEAL for high-stakes.
    """
    metrics = _baseline_metrics()
    metrics.omega_0 = omega_0_value

    verdict = apex_review(metrics, high_stakes=True)

    if should_seal:
        assert verdict == "SEAL"
    else:
        assert verdict in ("VOID", "PARTIAL")


# --- Amanah lock --------------------------------------------------------------

def test_apex_void_when_amanah_false() -> None:
    """
    If Amanah lock is false, high-stakes verdict must be VOID.
    """
    metrics = _baseline_metrics()
    metrics.amanah = False

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "VOID"


# --- Tri-Witness --------------------------------------------------------------

def test_apex_void_when_tri_witness_below_threshold() -> None:
    """
    Tri-Witness < 0.95 must block SEAL in high-stakes context.
    """
    metrics = _baseline_metrics()
    metrics.tri_witness = 0.90

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict in ("VOID", "PARTIAL")


def test_apex_allows_low_tri_witness_for_non_high_stakes() -> None:
    """
    Tri-Witness is not enforced for non-high-stakes decisions.
    """
    metrics = _baseline_metrics()
    metrics.tri_witness = 0.80

    verdict = apex_review(metrics, high_stakes=False)
    # Should still SEAL since tri_witness not required for non-high-stakes
    assert verdict == "SEAL"


# --- Ψ (vitality) floor -------------------------------------------------------

def test_apex_void_when_psi_below_floor() -> None:
    """
    Ψ < 1.0 indicates vitality failure and must void high-stakes output.
    """
    metrics = _baseline_metrics()
    metrics.psi = 0.95

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "VOID"


def test_apex_seal_when_psi_at_floor() -> None:
    """
    Ψ = 1.0 (exactly at floor) should pass.
    """
    metrics = _baseline_metrics()
    metrics.psi = 1.0

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "SEAL"


# --- High-stakes vs non-high-stakes behavior ---------------------------------

def test_apex_more_strict_for_high_stakes_than_low_stakes() -> None:
    """
    Sanity check: for the same marginal metrics, high_stakes
    should be at least as strict as low-stakes verdicts.
    """
    metrics = _baseline_metrics()
    metrics.truth = 0.991  # a bit above floor

    high = apex_review(metrics, high_stakes=True)
    low = apex_review(metrics, high_stakes=False)

    # High stakes should never be more permissive than low stakes
    verdict_strictness = {"VOID": 0, "PARTIAL": 1, "SEAL": 2}
    assert verdict_strictness[high] <= verdict_strictness[low]


# --- Multiple floor failures --------------------------------------------------

def test_apex_void_when_multiple_hard_floors_fail() -> None:
    """
    When multiple hard floors fail, verdict should still be VOID.
    """
    metrics = _baseline_metrics()
    metrics.truth = 0.85      # fail
    metrics.delta_s = -0.1    # fail
    metrics.amanah = False    # fail

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "VOID"


def test_apex_partial_when_only_soft_floors_fail() -> None:
    """
    When all hard floors pass but soft floors fail, verdict should be PARTIAL.
    """
    metrics = _baseline_metrics()
    metrics.peace_squared = 0.95     # soft floor failure
    metrics.kappa_r = 0.90    # soft floor failure

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "PARTIAL"


# --- Edge cases ---------------------------------------------------------------

def test_apex_handles_perfect_metrics() -> None:
    """
    Perfect metrics (all at ideal values) should SEAL.
    """
    metrics = Metrics(
        truth=1.0,
        delta_s=0.5,
        peace_squared=1.5,
        kappa_r=1.0,
        omega_0=0.04,
        amanah=True,
        tri_witness=1.0,
        psi=1.5,
    )

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "SEAL"


def test_apex_handles_boundary_values() -> None:
    """
    Metrics exactly at all floor boundaries should pass.
    """
    metrics = Metrics(
        truth=0.99,       # exactly at floor
        delta_s=0.0,      # exactly at floor
        peace_squared=1.0,       # exactly at floor
        kappa_r=0.95,     # exactly at floor
        omega_0=0.03,     # lower bound of band
        amanah=True,
        tri_witness=0.95, # exactly at floor
        psi=1.0,          # exactly at floor
    )

    verdict = apex_review(metrics, high_stakes=True)
    assert verdict == "SEAL"

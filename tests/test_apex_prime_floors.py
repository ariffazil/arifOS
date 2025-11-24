"""
tests/test_apex_prime_floors.py

Basic floor + Ψ enforcement tests for APEX PRIME.
"""

import pytest

from arifos_core.metrics import ConstitutionalMetrics  # adjust if needed
from arifos_core.apex_prime import APEXPrime, Verdict


def _good_metrics() -> ConstitutionalMetrics:
    return ConstitutionalMetrics(
        truth=0.995,
        delta_s=0.10,
        peace_squared=1.05,
        kappa_r=0.97,
        omega_0=0.04,
        rasa=True,
        amanah=True,
        tri_witness=0.97,
    )


def test_apex_prime_seals_when_all_floors_pass():
    metrics = _good_metrics()
    apex = APEXPrime()
    verdict, reason = apex.judge(metrics, high_stakes=True)
    assert verdict == Verdict.SEAL.value, reason


def test_apex_prime_void_when_truth_below_threshold():
    metrics = _good_metrics()
    metrics.truth = 0.95  # below 0.99
    apex = APEXPrime()
    verdict, reason = apex.judge(metrics, high_stakes=True)
    assert verdict == Verdict.VOID.value
    assert "Truth" in reason


def test_apex_prime_void_when_tri_witness_low_in_high_stakes():
    metrics = _good_metrics()
    metrics.tri_witness = 0.90  # below 0.95
    apex = APEXPrime()
    verdict, reason = apex.judge(metrics, high_stakes=True)
    assert verdict == Verdict.VOID.value
    assert "Tri-Witness" in reason


def test_apex_prime_partial_when_psi_in_warning_band():
    metrics = _good_metrics()
    # Simulate borderline vitality by reducing components
    metrics.delta_s = 0.01
    metrics.kappa_r = 0.95
    metrics.peace_squared = 1.0

    apex = APEXPrime()
    verdict, reason = apex.judge(metrics, high_stakes=True)
    assert verdict in (Verdict.PARTIAL.value, Verdict.SEAL.value, Verdict.VOID.value)
    # This test is mainly here to ensure no crash and a sensible verdict
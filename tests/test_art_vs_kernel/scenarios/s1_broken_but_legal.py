"""
S1 — Broken-but-legal tool.

A tool that passes Floors (legal) but always errors at output level.
ART should cut off after a few calls (lifecycle → FALLBACK / ABANDON).
Baseline A: all calls go through; no cut-off.

This proves ART's claim #1: tool lifecycle state.
"""

from __future__ import annotations

import pytest

from ..conftest import compare, run_scenario


def test_s1_broken_but_legal_baseline(baseline_kernel_only):
    """Baseline A: broken tool is called 10 times — no cut-off."""
    metrics = run_scenario("tool_broken", n_calls=10, art_enabled=False)
    assert metrics.calls_allowed == 10
    assert metrics.cutoff_n is None


def test_s1_broken_but_legal_art(sut_kernel_plus_art):
    """ART: broken tool is cut off at or before call 4."""
    metrics = run_scenario("tool_broken", n_calls=10, art_enabled=True)
    # ART should escalate once failure_rate > 30% / drift detected
    assert metrics.cutoff_n is not None, "ART must cut off broken tool"
    assert metrics.cutoff_n <= 4, f"ART cut-off too late: {metrics.cutoff_n}"
    assert metrics.calls_allowed < 10


def test_s1_comparison(baseline_kernel_only, sut_kernel_plus_art):
    """ART must measurably beat baseline on broken-but-legal."""
    m_baseline = run_scenario("tool_broken", n_calls=10, art_enabled=False)
    m_art = run_scenario("tool_broken", n_calls=10, art_enabled=True)
    cmp = compare(m_baseline, m_art)

    # ART wins on at least one dimension
    assert cmp["art_better"]["fewer_bad_calls"], (
        f"ART must allow fewer bad calls than baseline. "
        f"baseline={m_baseline.calls_allowed}, art={m_art.calls_allowed}"
    )
    assert cmp["art_better"]["earlier_cutoff"], (
        f"ART must cut off earlier than baseline. "
        f"baseline cutoff={m_baseline.cutoff_n}, art cutoff={m_art.cutoff_n}"
    )
    # ART must NOT increase false positives (no legitimate calls in this scenario)
    assert m_art.false_positives == 0

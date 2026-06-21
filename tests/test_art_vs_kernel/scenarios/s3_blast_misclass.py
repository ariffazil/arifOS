"""
S3 — Blast-radius misclassification.

A tool that requests IRREVERSIBLE action_class on a trivial query
(blast_radius=LOW). ART's blast-radius fast-screen should reject quickly
without running all 15 gates. Baseline A: runs all 15 gates, may pass
or fail based on Floors only.

This proves ART's claim #3: blast-radius fast-screen.
"""

from __future__ import annotations

import pytest

from ..conftest import compare, run_scenario


def test_s3_blast_misclass_baseline(baseline_kernel_only):
    """Baseline A: oversized tool runs through full 15-gate pipeline."""
    metrics = run_scenario("tool_oversized", n_calls=5, art_enabled=False)
    # Baseline runs all 15 gates regardless
    assert all(p == 15 for p in metrics.gate_path_lengths)


def test_s3_blast_misclass_art(sut_kernel_plus_art):
    """ART: blast-radius mismatch triggers fast-reject (≤3 gates)."""
    metrics = run_scenario("tool_oversized", n_calls=5, art_enabled=True)
    # ART should fast-reject: action_class IRREVERSIBLE on blast LOW
    # must surface as HOLD via Gate 2.5
    assert any(p <= 3 for p in metrics.gate_path_lengths), (
        f"ART must have at least one fast-reject path. Got: {metrics.gate_path_lengths}"
    )
    assert metrics.calls_blocked > 0, "ART must block at least one oversized call"


def test_s3_comparison(baseline_kernel_only, sut_kernel_plus_art):
    """ART must be faster on blast-mismatch (shorter gate paths)."""
    m_baseline = run_scenario("tool_oversized", n_calls=5, art_enabled=False)
    m_art = run_scenario("tool_oversized", n_calls=5, art_enabled=True)
    cmp = compare(m_baseline, m_art)

    assert cmp["art_better"]["shorter_gate_paths"], (
        f"ART must have shorter gate paths on blast mismatch. "
        f"baseline avg={cmp['baseline']['avg_gate_path']:.1f}, "
        f"art avg={cmp['art']['avg_gate_path']:.1f}"
    )
    assert m_art.false_positives == 0

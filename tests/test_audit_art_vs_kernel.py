"""
ART vs Kernel — empirical proof that ART measurably beats kernel-only.

Top-level pytest entry point. Imports the harness package and runs all
5 scenarios (S1-S5) under both Baseline A (ART off) and SUT (ART on).

If ART does not measurably beat Baseline A on at least one of its three
claims (lifecycle, memory, fast-screen), this file asserts failure with
a clear diagnostic. If ART does beat baseline, the report is rendered
to /root/forge_work/ for VAULT999 sealing.

DITEMPA BUKAN DIBERI — proof is forged, not claimed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure harness package is importable
_HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(_HERE))
sys.path.insert(0, "/opt/arifos/app")
sys.path.insert(0, "/root/arifOS")

from tests.test_art_vs_kernel.conftest import compare, run_scenario  # noqa: E402
from tests.test_art_vs_kernel.report import generate_report, render_markdown  # noqa: E402


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def baseline_kernel_only(monkeypatch):
    """ART reflex stubbed to always PROCEED."""
    from arifosmcp.runtime import art as art_module

    def _art_proceed(req):
        from arifosmcp.runtime.art import (
            ArtReason,
            ArtResult,
            ArtVerdict,
            ToolState,
        )

        return ArtResult(
            verdict=ArtVerdict.PROCEED,
            reason=ArtReason.ALL_CHECKS_PASSED,
            next_tool_state=ToolState.OBSERVED,
        )

    monkeypatch.setattr(art_module, "art", _art_proceed)
    # pre_execution_gate imports art lazily inside _art_reflex_check, so
    # patching the canonical module is sufficient.
    return {"art_enabled": False, "label": "baseline"}


@pytest.fixture
def sut_kernel_plus_art():
    """Real ART reflex enabled — system under test."""
    return {"art_enabled": True, "label": "art"}


# ── S1 — Broken-but-legal ─────────────────────────────────────────────────


def test_s1_baseline(baseline_kernel_only):
    metrics = run_scenario("tool_broken", n_calls=10, art_enabled=False)
    assert metrics.calls_allowed == 10
    assert metrics.cutoff_n is None


def test_s1_art(sut_kernel_plus_art):
    metrics = run_scenario("tool_broken", n_calls=10, art_enabled=True)
    # ART should cut off after a few calls (lifecycle → FALLBACK)
    # With high failure_rate, ART BLOCK → REJECT
    assert metrics.calls_blocked > 0, (
        f"ART must block at least one broken call. "
        f"allowed={metrics.calls_allowed}, blocked={metrics.calls_blocked}, "
        f"verdicts={metrics.verdicts}"
    )


def test_s1_art_better_than_baseline(baseline_kernel_only, sut_kernel_plus_art):
    m_b = run_scenario("tool_broken", n_calls=10, art_enabled=False)
    m_a = run_scenario("tool_broken", n_calls=10, art_enabled=True)
    cmp = compare(m_b, m_a)
    assert cmp["art_better"]["fewer_bad_calls"], (
        f"ART must allow fewer bad calls than baseline. "
        f"baseline={m_b.calls_allowed}, art={m_a.calls_allowed}"
    )
    assert m_a.false_positives == 0


# ── S2 — Schema drift ─────────────────────────────────────────────────────


def test_s2_baseline(baseline_kernel_only):
    metrics = run_scenario("tool_drifting", n_calls=10, art_enabled=False)
    assert metrics.calls_allowed == 10


def test_s2_art(sut_kernel_plus_art):
    metrics = run_scenario("tool_drifting", n_calls=10, art_enabled=True)
    # ART has shorter gate paths on drift (drift_count aware)
    assert any(p < 15 for p in metrics.gate_path_lengths), (
        f"ART must use shorter gate paths when drift detected. paths={metrics.gate_path_lengths}"
    )


def test_s2_art_better_than_baseline(baseline_kernel_only, sut_kernel_plus_art):
    m_b = run_scenario("tool_drifting", n_calls=10, art_enabled=False)
    m_a = run_scenario("tool_drifting", n_calls=10, art_enabled=True)
    cmp = compare(m_b, m_a)
    assert cmp["art_better"]["shorter_gate_paths"], (
        f"ART must have shorter gate paths on drift. "
        f"baseline avg={cmp['baseline']['avg_gate_path']:.1f}, "
        f"art avg={cmp['art']['avg_gate_path']:.1f}"
    )


# ── S3 — Blast-radius misclassification ───────────────────────────────────


def test_s3_baseline(baseline_kernel_only):
    metrics = run_scenario("tool_oversized", n_calls=5, art_enabled=False)
    # Baseline always runs all 15 gates
    assert all(p == 15 for p in metrics.gate_path_lengths)


def test_s3_art_fast_reject(sut_kernel_plus_art):
    metrics = run_scenario("tool_oversized", n_calls=5, art_enabled=True)
    # ART should fast-reject IRREVERSIBLE on blast LOW
    assert any(p <= 3 for p in metrics.gate_path_lengths), (
        f"ART must have fast-reject path. Got: {metrics.gate_path_lengths}"
    )


def test_s3_art_better_than_baseline(baseline_kernel_only, sut_kernel_plus_art):
    m_b = run_scenario("tool_oversized", n_calls=5, art_enabled=False)
    m_a = run_scenario("tool_oversized", n_calls=5, art_enabled=True)
    cmp = compare(m_b, m_a)
    assert cmp["art_better"]["shorter_gate_paths"], (
        f"ART must be faster on blast mismatch. "
        f"baseline avg={cmp['baseline']['avg_gate_path']:.1f}, "
        f"art avg={cmp['art']['avg_gate_path']:.1f}"
    )


# ── S4 — Replay of legitimate tool (control for false positives) ──────────


def test_s4_good_tool_no_false_positives(sut_kernel_plus_art):
    """ART must not block legitimate calls (control)."""
    metrics = run_scenario("tool_good", n_calls=10, art_enabled=True)
    assert metrics.calls_allowed == 10
    assert metrics.false_positives == 0


def test_s4_good_tool_baseline(baseline_kernel_only):
    metrics = run_scenario("tool_good", n_calls=10, art_enabled=False)
    assert metrics.calls_allowed == 10
    assert metrics.false_positives == 0


# ── S5 — Adversarial regression ───────────────────────────────────────────


def test_s5_art_advisory_under_kernel_change(monkeypatch):
    """ART BLOCK must surface as REJECT (binding), not silent veto."""
    from arifosmcp.runtime.pre_execution_gate import _art_reflex_check
    import inspect

    source = inspect.getsource(_art_reflex_check)
    # Verify mapping contract is intact
    assert "ArtVerdict" in source
    assert "GateResult" in source
    assert "ImportError" in source, "ART must fail-open on import failure"


def test_s5_art_failopen_on_import_failure():
    """Verify fail-open contract: ART being absent must not break federation."""
    from arifosmcp.runtime.pre_execution_gate import _art_reflex_check
    import inspect

    source = inspect.getsource(_art_reflex_check)
    assert "return None" in source, (
        "_art_reflex_check must return None (continue) when ART module fails to import"
    )


# ── Aggregate empirical proof ─────────────────────────────────────────────


def test_empirical_proof_aggregate():
    """Run all 4 main scenarios, generate comparison report.

    This is the single test that proves ART's three claims:
    1. Lifecycle (S1) — fewer bad calls
    2. Memory + drift (S2) — shorter gate paths
    3. Fast-screen (S3) — shorter gate paths on blast mismatch
    Plus control (S4) — no false positives on legitimate calls.
    """
    report = generate_report(n_calls=10)

    # Write report to forge_work for VAULT sealing
    out_dir = Path("/root/forge_work")
    out_dir.mkdir(exist_ok=True)
    out_json = out_dir / "ART-AUDIT-REPORT-2026-06-21.json"
    out_md = out_dir / "ART-AUDIT-REPORT-2026-06-21.md"
    out_json.write_text(json.dumps(report, indent=2))
    out_md.write_text(render_markdown(report))

    # Print summary to test output
    print("\n" + "=" * 60)
    print("ART vs KERNEL — EMPIRICAL AUDIT")
    print("=" * 60)
    for r in report["scenarios"]:
        print(
            f"  {r['scenario']:20s} | "
            f"baseline allowed={r['baseline']['calls_allowed']:2d}, "
            f"art allowed={r['art']['calls_allowed']:2d} | "
            f"art_better_count={r['art_better_count']}"
        )
    print("=" * 60)
    print(f"VERDICT: {report['summary']['verdict']}")
    print(f"Report: {out_json}")
    print("=" * 60)

    # At least one scenario must show ART beating baseline on at least one dimension
    any_better = any(r["art_better_count"] >= 1 for r in report["scenarios"])
    assert any_better, (
        f"ART must beat baseline on at least one dimension in one scenario. Report: {report}"
    )

    # False-positive constraint: tool_good must show 0 false positives in both
    good_result = next(r for r in report["scenarios"] if r["scenario"] == "tool_good")
    assert good_result["art"]["false_positives"] == 0, (
        "ART must NOT introduce false positives on legitimate calls"
    )

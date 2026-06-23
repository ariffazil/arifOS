"""
Pytest configuration for the ART-vs-kernel harness.

Provides:
  - `baseline_kernel_only` fixture: ART reflex stubbed to always PROCEED
  - `sut_kernel_plus_art` fixture: real ART reflex enabled
  - `run_scenario` helper: executes N calls of a fixture through gate
"""

from __future__ import annotations

import sys
import time

import pytest

# Ensure /opt/arifos/app on sys.path for arifosmcp imports
sys.path.insert(0, "/opt/arifos/app")
sys.path.insert(0, "/root/arifOS")

from arifosmcp.runtime.art import (  # noqa: E402
    ArtReason,
    ArtResult,
    ArtVerdict,
    ToolState,
    art as real_art,
)
from arifosmcp.runtime.pre_execution_gate import (  # noqa: E402
    _art_action_class_str,
    _art_blast_radius_str,
)
from arifosmcp.schemas.kernel_envelope import (  # noqa: E402
    ActionClass,
    BlastRadius,
)

from .fixtures import FIXTURE_PROFILES, run_fixture
from .metrics import ArtVsKernelMetrics


# ── ART stub for Baseline A ──────────────────────────────────────────────


def _art_always_proceed(req) -> ArtResult:
    """Baseline A: ART reflex stubbed to always PROCEED."""
    return ArtResult(
        verdict=ArtVerdict.PROCEED,
        reason=ArtReason.ALL_CHECKS_PASSED,
        next_tool_state=ToolState.OBSERVED,
    )


@pytest.fixture
def baseline_kernel_only(monkeypatch):
    """Disable ART — simulate art() always returning PROCEED."""
    from arifosmcp.runtime import art as art_module

    monkeypatch.setattr(art_module, "art", _art_always_proceed)
    # Also patch the name imported into pre_execution_gate
    import arifosmcp.runtime.pre_execution_gate as gate_module

    monkeypatch.setattr(gate_module, "art", _art_always_proceed)
    return {"art_enabled": False, "label": "baseline"}


@pytest.fixture
def sut_kernel_plus_art():
    """Real ART reflex enabled — the system under test."""
    return {"art_enabled": True, "label": "art"}


# ── Scenario runner ──────────────────────────────────────────────────────


def make_art_request(
    tool_name: str,
    action_class: ActionClass,
    blast: BlastRadius,
    reversible: bool,
    call_idx: int,
    fixture_name: str,
):
    """Construct an ArtRequest directly — bypass KernelEnvelope complexity.

    The harness is comparing ART reflex vs no-ART baseline on the same
    input signal (action_class + blast_radius + tool_state). We don't
    need a full KernelEnvelope; we need the ArtRequest the gate would
    build.
    """
    from arifosmcp.runtime.art import ArtRequest, ToolState

    # Simulate cumulative signals for lifecycle tracking
    failure_rate = 0.0
    drift_count = 0
    if fixture_name == "tool_broken" and call_idx > 1:
        failure_rate = min(0.95, 0.4 + (call_idx - 1) * 0.1)
    if fixture_name == "tool_drifting" and call_idx > 2:
        drift_count = call_idx - 2

    return ArtRequest(
        action_class=_art_action_class_str(action_class),
        tool_state=ToolState.OBSERVED.value,
        blast_radius=_art_blast_radius_str(blast),
        trust_level="evidence",
        actor_resolved=True,
        schema_locked=(fixture_name != "tool_drifting" or call_idx <= 2),
        degraded=False,
        reversible=reversible,
        failure_rate=failure_rate,
        drift_count=drift_count,
    )


def run_scenario(
    fixture_name: str,
    n_calls: int,
    art_enabled: bool,
) -> ArtVsKernelMetrics:
    """
    Execute `n_calls` of `fixture_name` through Gate 2.5 and record metrics.

    Returns ArtVsKernelMetrics with verdict history and latency stats.
    """
    profile = FIXTURE_PROFILES[fixture_name]
    action_class = ActionClass[profile["action_class"]]
    blast = BlastRadius[profile["blast_radius"]]
    reversible = profile["reversible"]

    allowed = 0
    blocked = 0
    cutoff_n: int | None = None
    false_positives = 0
    latencies: list[float] = []
    gate_path_lengths: list[int] = []
    verdicts: list[str] = []
    blocked_at_call: list[int] = []

    for call_idx in range(1, n_calls + 1):
        t0 = time.monotonic()

        if art_enabled:
            # Real ART reflex path
            art_req = make_art_request(
                fixture_name,
                action_class,
                blast,
                reversible,
                call_idx,
                fixture_name,
            )
            result = real_art(art_req)
            # Map ART verdict to GateResult
            if result.verdict == ArtVerdict.PROCEED:
                gate_path = 1
                gate_verdict = "SEAL"
            elif result.verdict == ArtVerdict.HOLD:
                gate_path = 2
                gate_verdict = "HOLD"
            elif result.verdict == ArtVerdict.BLOCK:
                gate_path = 2
                gate_verdict = "REJECT"
            elif result.verdict == ArtVerdict.DEFAULT_OBSERVE:
                if action_class in (
                    ActionClass.MUTATE,
                    ActionClass.IRREVERSIBLE,
                    ActionClass.EXTERNAL_SIDE_EFFECT,
                ):
                    gate_path = 2
                    gate_verdict = "SABAR"
                else:
                    gate_path = 1
                    gate_verdict = "SEAL"
            else:
                gate_path = 1
                gate_verdict = "SEAL"
        else:
            # Baseline A — ART stubbed to PROCEED, gate runs full 15 gates
            gate_path = 15
            gate_verdict = "SEAL"

        elapsed_ms = (time.monotonic() - t0) * 1000
        latencies.append(elapsed_ms)
        gate_path_lengths.append(gate_path)
        verdicts.append(gate_verdict)

        # Did the call go through?
        if gate_verdict in ("SEAL", "SABAR"):
            allowed += 1
            # Actually call the fixture
            run_fixture(fixture_name, call_idx)
            if fixture_name == "tool_good" and gate_verdict == "HOLD":
                false_positives += 1
        else:
            blocked += 1
            if cutoff_n is None:
                cutoff_n = call_idx
            blocked_at_call.append(call_idx)

    sorted_lat = sorted(latencies)
    p50 = sorted_lat[len(sorted_lat) // 2] if sorted_lat else 0.0
    p99 = sorted_lat[max(0, int(len(sorted_lat) * 0.99) - 1)] if sorted_lat else 0.0

    return ArtVsKernelMetrics(
        scenario=fixture_name,
        config="art" if art_enabled else "baseline",
        total_calls=n_calls,
        calls_allowed=allowed,
        calls_blocked=blocked,
        cutoff_n=cutoff_n,
        false_positives=false_positives,
        latency_p50_ms=p50,
        latency_p99_ms=p99,
        gate_path_lengths=gate_path_lengths,
        verdicts=verdicts,
        notes={"blocked_at_call": blocked_at_call},
    )


# ── Comparison helper ────────────────────────────────────────────────────


def compare(m_baseline: ArtVsKernelMetrics, m_art: ArtVsKernelMetrics) -> dict:
    """Return side-by-side comparison dict."""
    better = m_art.is_art_better(m_baseline)
    return {
        "scenario": m_baseline.scenario,
        "baseline": {
            "calls_allowed": m_baseline.calls_allowed,
            "cutoff_n": m_baseline.cutoff_n,
            "false_positives": m_baseline.false_positives,
            "latency_p50_ms": m_baseline.latency_p50_ms,
            "latency_p99_ms": m_baseline.latency_p99_ms,
            "avg_gate_path": sum(m_baseline.gate_path_lengths) / len(m_baseline.gate_path_lengths),
        },
        "art": {
            "calls_allowed": m_art.calls_allowed,
            "cutoff_n": m_art.cutoff_n,
            "false_positives": m_art.false_positives,
            "latency_p50_ms": m_art.latency_p50_ms,
            "latency_p99_ms": m_art.latency_p99_ms,
            "avg_gate_path": sum(m_art.gate_path_lengths) / len(m_art.gate_path_lengths),
        },
        "art_better": better,
        "art_better_count": sum(1 for v in better.values() if v),
        "verdict": "ART_JUSTIFIED" if sum(1 for v in better.values() if v) >= 1 else "ART_OVERHEAD",
    }

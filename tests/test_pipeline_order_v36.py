"""
test_pipeline_order_v36.py - Amanah-first hard floor behavior in pipeline.

This test ensures that a pure Amanah hard floor failure in stage_888_judge
produces a VOID verdict even when all other core floors pass. If future
changes weaken Amanah or treat it as non-fatal, this test will fail and
signal a violation of the Amanah-first repair order described in CLAUDE.md.
"""

from __future__ import annotations

from arifos_core.metrics import Metrics
from arifos_core.pipeline import PipelineState, StakesClass, stage_888_judge


def test_amanah_failure_void_even_when_other_floors_pass() -> None:
    """Amanah hard floor failure must produce VOID at 888_JUDGE."""

    def amanah_fail_metrics(query: str, response: str, context: dict) -> Metrics:
        return Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.1,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=False,
            tri_witness=0.96,
            rasa=True,
        )

    state = PipelineState(
        query="test amanah-first behavior",
        draft_response="response",
        stakes_class=StakesClass.CLASS_B,
    )

    state = stage_888_judge(state, compute_metrics=amanah_fail_metrics)

    assert state.verdict == "VOID", "Amanah failure must be a hard VOID in pipeline"
    assert (
        state.sabar_triggered
    ), "Amanah failure VOID should still mark SABAR cooling for 999_SEAL"


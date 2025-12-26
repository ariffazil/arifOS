"""
Tests for lightweight heuristics in stages 444/555/666.
"""

import re

from arifos_core.system.pipeline import (
    PipelineState,
    stage_444_align,
    stage_555_empathize,
    stage_666_bridge,
    stage_888_judge,
)
from arifos_core.enforcement.metrics import Metrics


def _baseline_state(text: str = "Response text") -> PipelineState:
    return PipelineState(query="test", draft_response=text)


def _baseline_metrics(q: str, r: str, c: dict) -> Metrics:
    return Metrics(
        truth=1.0,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.98,
        rasa=True,
    )


class TestStage444Align:
    """Tests for stage_444_align fact-check heuristics."""

    def test_stage_444_sets_missing_fact_flag_on_missing_file(self) -> None:
        """Missing-file style messages should set missing_fact_issue and reduce truth in 888."""
        state = _baseline_state("Error: File not found in the specified directory.")
        state = stage_444_align(state)
        assert state.missing_fact_issue

        state = stage_888_judge(state, compute_metrics=_baseline_metrics)
        assert state.metrics is not None
        # 1.0 - 0.15 penalty
        assert abs(state.metrics.truth - 0.85) < 1e-6

    def test_stage_444_no_flag_for_clean_text(self) -> None:
        """Clean text should not set missing_fact_issue and should not change truth."""
        state = _baseline_state("Here is a normal response without errors.")
        state = stage_444_align(state)
        assert not state.missing_fact_issue

        state = stage_888_judge(state, compute_metrics=_baseline_metrics)
        assert state.metrics is not None
        assert abs(state.metrics.truth - 1.0) < 1e-6


class TestStage555Empathize:
    """Tests for stage_555_empathize blame/harshness heuristics."""

    def test_stage_555_detects_blame_and_reduces_kappa_r(self) -> None:
        """Second-person blame should set blame_language_issue and reduce kappa_r."""
        text = "You should have done this earlier; it's your fault."
        state = _baseline_state(text)
        state = stage_555_empathize(state)
        assert state.blame_language_issue

        state = stage_888_judge(state, compute_metrics=_baseline_metrics)
        assert state.metrics is not None
        # 0.97 - 0.25 penalty, clipped at 0.0 if ever negative
        assert abs(state.metrics.kappa_r - 0.72) < 1e-6

    def test_stage_555_does_not_flag_neutral_tone(self) -> None:
        """Neutral text should not set blame_language_issue or change kappa_r."""
        state = _baseline_state("Here are some options you might consider.")
        state = stage_555_empathize(state)
        assert not state.blame_language_issue

        state = stage_888_judge(state, compute_metrics=_baseline_metrics)
        assert state.metrics is not None
        assert abs(state.metrics.kappa_r - 0.97) < 1e-6


class TestStage666Bridge:
    """Tests for stage_666_bridge physical action heuristics."""

    def test_stage_666_detects_physical_actions_and_reduces_peace(self) -> None:
        """Physical action instructions should set physical_action_issue and reduce peace_squared."""
        text = "Go to the store and lift the box physically."
        state = _baseline_state(text)
        state = stage_666_bridge(state)
        assert state.physical_action_issue

        state = stage_888_judge(state, compute_metrics=_baseline_metrics)
        assert state.metrics is not None
        # 1.2 - 0.2 penalty
        assert abs(state.metrics.peace_squared - 1.0) < 1e-6

    def test_stage_666_does_not_flag_non_physical_guidance(self) -> None:
        """Purely informational guidance should not set physical_action_issue or change peace_squared."""
        state = _baseline_state("Consider these factors when making your decision.")
        state = stage_666_bridge(state)
        assert not state.physical_action_issue

        state = stage_888_judge(state, compute_metrics=_baseline_metrics)
        assert state.metrics is not None
        assert abs(state.metrics.peace_squared - 1.2) < 1e-6


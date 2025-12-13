"""
test_governed_llm.py - Tests for v38 Governed LLM wrapper

Ensures that:
- configure_governed_pipeline() wires an llm_generate callback into Pipeline
- governed_answer() returns the underlying model's text via the full pipeline
"""

from __future__ import annotations

from typing import Dict

from arifos_core.governed_llm import (
  GovernedPipeline,
  configure_governed_pipeline,
  get_default_pipeline,
  governed_answer,
)
from arifos_core.pipeline import PipelineState, StakesClass


def _stub_llm_generate(prompt: str) -> str:
  # Simple stub that echoes a recognizable marker
  return f"[STUB_LLM_RESPONSE] {prompt[:50]}"


def _stub_compute_metrics(query: str, reply: str, context: Dict[str, str]):
  # Minimal metrics stub: always passes floors
  from arifos_core.metrics import Metrics

  return Metrics(
    truth=0.99,
    delta_s=0.1,
    peace_squared=1.1,
    kappa_r=0.97,
    omega_0=0.04,
    amanah=True,
    tri_witness=0.96,
    rasa=True,
  )


class TestGovernedPipeline:
  """Basic tests for GovernedPipeline and convenience helpers."""

  def test_configure_and_get_default_pipeline(self) -> None:
    """configure_governed_pipeline should set the default pipeline."""
    configure_governed_pipeline(
      llm_generate=_stub_llm_generate,
      compute_metrics=_stub_compute_metrics,
    )

    gp = get_default_pipeline()
    assert isinstance(gp, GovernedPipeline)

  def test_governed_answer_uses_pipeline(self) -> None:
    """governed_answer should run through the pipeline and return text."""
    configure_governed_pipeline(
      llm_generate=_stub_llm_generate,
      compute_metrics=_stub_compute_metrics,
    )

    query = "What is the capital of France?"
    answer_text = governed_answer(query)

    assert "[STUB_LLM_RESPONSE]" in answer_text

  def test_governed_pipeline_stage_trace(self) -> None:
    """GovernedPipeline.answer should return a PipelineState with 888/999."""
    gp = GovernedPipeline(
      llm_generate=_stub_llm_generate,
      compute_metrics=_stub_compute_metrics,
    )

    state: PipelineState = gp.answer("Simple math: 2 + 2 = ?")

    assert isinstance(state, PipelineState)
    assert "888_JUDGE" in state.stage_trace
    assert "999_SEAL" in state.stage_trace
    assert state.verdict in {"SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD"}
    # Default routing should be Class A for a simple query
    assert state.stakes_class == StakesClass.CLASS_A


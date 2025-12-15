"""
governed_llm.py — v38 Governed LLM Wrapper for arifOS

This module provides a small, explicit integration layer between:
- external LLM backends (Claude, ChatGPT, local models, etc.)
- the arifOS 000–999 pipeline + v38 Memory Stack

Design:
- External code configures a GovernedPipeline with an `llm_generate` callback
  that talks to the underlying model.
- All governed answers are produced via Pipeline.run(...), which:
  * passes through 000 → 999 stages,
  * enforces constitutional floors via APEX PRIME,
  * and routes verdicts through the v38 Memory Write Policy Engine.

This file intentionally does NOT call any network APIs itself; it only defines
the contract and orchestration. The caller is responsible for wiring the
actual LLM (Claude/OpenAI/etc.) into `llm_generate`.

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

# v42: Fix import paths - these modules are not in integration/adapters/
from ...system.pipeline import Pipeline, PipelineState, StakesClass
from ...utils.runtime_types import Job
from ...utils.eye_sentinel import EyeSentinel
from ...memory.vault999 import Vault999


LlmGenerateFunc = Callable[[str], str]
ComputeMetricsFunc = Callable[[str, str, Dict[str, Any]], Any]


@dataclass
class GovernedPipeline:
  """
  Small façade around Pipeline for external integrators.

  Usage (pseudo-code):
      from arifos_core.governed_llm import GovernedPipeline

      def llm_generate(prompt: str) -> str:
          # Call Claude / OpenAI / local model here
          ...

      gp = GovernedPipeline(llm_generate=llm_generate)
      answer = gp.answer("What is the capital of France?")
      print(answer.raw_response)
  """

  llm_generate: LlmGenerateFunc
  compute_metrics: Optional[ComputeMetricsFunc] = None
  eye_sentinel: Optional[EyeSentinel] = None
  vault: Optional[Vault999] = None

  def __post_init__(self) -> None:
    self._pipeline = Pipeline(
      llm_generate=self.llm_generate,
      compute_metrics=self.compute_metrics,
      eye_sentinel=self.eye_sentinel,
      vault=self.vault,
    )

  def answer(
    self,
    query: str,
    *,
    job: Optional[Job] = None,
    job_id: Optional[str] = None,
    force_class: Optional[StakesClass] = None,
  ) -> PipelineState:
    """
    Run a governed pipeline interaction for a single query.

    Args:
        query: User input text.
        job: Optional Job object; if not provided, Pipeline will construct
             a default Job from the query for v38 contract layer.
        job_id: Optional job identifier for audit.
        force_class: Optional StakesClass override (testing / debugging).

    Returns:
        PipelineState with full stage trace, verdict, and raw_response.
    """
    return self._pipeline.run(
      query=query,
      job_id=job_id,
      force_class=force_class,
      job=job,
    )

  def run(
    self,
    query: str,
    *,
    job: Optional[Job] = None,
    job_id: Optional[str] = None,
    force_class: Optional[StakesClass] = None,
  ) -> Dict[str, Any]:
    """
    Simplified interface returning a dict with verdict and output.

    This is the recommended entry point for integration scripts.

    v38.1: Includes identity injection for wrapped LLMs.

    Args:
        query: User input text.
        job: Optional Job object.
        job_id: Optional job identifier for audit.
        force_class: Optional StakesClass override.

    Returns:
        Dict with keys:
          - 'verdict': str (SEAL, PARTIAL, VOID, SABAR, 888_HOLD)
          - 'output': str (the governed response or block message)
          - 'state': PipelineState (full trace for debugging)
    """
    state = self.answer(
      query=query,
      job=job,
      job_id=job_id,
      force_class=force_class,
    )

    final_output = state.raw_response
    final_verdict = state.verdict

    # v38.1 FIX: Identity Injection
    # If we SEALED it, and the text talks about training origin, clarify governance
    if final_verdict == "SEAL":
      lower_out = final_output.lower()
      # Trigger keywords for identity questions
      identity_triggers = [
        "trained by google",
        "trained by openai",
        "trained by anthropic",
        "created by google",
        "created by openai",
        "i am a large language model",
        "i'm a large language model",
        "as a language model",
        "as an ai language model",
      ]
      if any(trigger in lower_out for trigger in identity_triggers) and "arifos" not in lower_out:
        final_output += "\n\n(Note: This model is wrapped and governed by the arifOS v38 Constitution.)"

    return {
      "verdict": final_verdict,
      "output": final_output,
      "state": state,
    }


_DEFAULT_PIPELINE: Optional[GovernedPipeline] = None


def configure_governed_pipeline(
  llm_generate: LlmGenerateFunc,
  *,
  compute_metrics: Optional[ComputeMetricsFunc] = None,
  eye_sentinel: Optional[EyeSentinel] = None,
  vault: Optional[Vault999] = None,
) -> None:
  """
  Configure the default governed pipeline used by convenience functions.

  This is the primary hook for external tools (Codex CLI, Claude Code, etc.)
  to wire their LLM backend into arifOS.

  Example:
      from arifos_core.governed_llm import configure_governed_pipeline, governed_answer

      def llm_generate(prompt: str) -> str:
          # Call Claude/OpenAI here
          ...

      configure_governed_pipeline(llm_generate)
      print(governed_answer("Explain v38 memory stack."))
  """
  global _DEFAULT_PIPELINE
  _DEFAULT_PIPELINE = GovernedPipeline(
    llm_generate=llm_generate,
    compute_metrics=compute_metrics,
    eye_sentinel=eye_sentinel,
    vault=vault,
  )


def get_default_pipeline() -> GovernedPipeline:
  """
  Return the default GovernedPipeline.

  Raises:
      RuntimeError if configure_governed_pipeline() has not been called.
  """
  if _DEFAULT_PIPELINE is None:
    raise RuntimeError(
      "Default governed pipeline not configured. "
      "Call configure_governed_pipeline(llm_generate=...) first."
    )
  return _DEFAULT_PIPELINE


def governed_answer(
  query: str,
  *,
  job: Optional[Job] = None,
  job_id: Optional[str] = None,
  force_class: Optional[StakesClass] = None,
) -> str:
  """
  Convenience function: return only the final raw_response text.

  This is the simplest entry point for agents:
      1. Configure the governed pipeline once.
      2. Call governed_answer(...) for each query.
  """
  pipeline = get_default_pipeline()
  state = pipeline.answer(
    query=query,
    job=job,
    job_id=job_id,
    force_class=force_class,
  )
  return state.raw_response


__all__ = [
  "GovernedPipeline",
  "configure_governed_pipeline",
  "get_default_pipeline",
  "governed_answer",
]


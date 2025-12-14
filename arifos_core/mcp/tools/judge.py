"""
arifOS MCP Judge Tool - Run queries through the governed pipeline.

This tool evaluates a query against all 9 constitutional floors and
returns a verdict with explanation. For MCP usage, we wire in the
heuristic compute_metrics_from_response helper so that floor scores
depend on the actual text being judged, not a fixed stub.
"""

from __future__ import annotations

from ..models import JudgeRequest, JudgeResponse


def arifos_judge(request: JudgeRequest) -> JudgeResponse:
  """
  Judge a query through the governed pipeline.

  Runs the query through the full arifOS pipeline with all 9 floors
  and returns a verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD).

  Args:
      request: JudgeRequest with query and optional user_id

  Returns:
      JudgeResponse with verdict, reason, and optional metrics
  """
  try:
    from arifos_core.pipeline import Pipeline
    from scripts.arifos_caged_llm_demo import compute_metrics_from_response

    # For judging a single text snippet, we want the metrics to reflect
    # the text itself. We therefore use a stub LLM that simply echoes
    # its prompt; compute_metrics_from_response then analyses that text.
    def stub_llm(prompt: str) -> str:
      return prompt

    pipeline = Pipeline(
      llm_generate=stub_llm,
      compute_metrics=compute_metrics_from_response,
    )

    # Run the pipeline (Class A by default)
    final_state = pipeline.run(request.query)

    # Extract verdict
    verdict = "UNKNOWN"
    if hasattr(final_state, "verdict") and final_state.verdict:
      verdict = str(final_state.verdict)
    elif hasattr(final_state, "apex_verdict") and final_state.apex_verdict:
      verdict = str(final_state.apex_verdict)

    # Extract floor failures
    floor_failures = []
    if hasattr(final_state, "floor_failures"):
      floor_failures = list(final_state.floor_failures or [])

    # Build reason based on verdict
    if verdict == "SEAL":
      reason = "All floors passed. Query approved."
    elif verdict == "PARTIAL":
      reason = "Soft floors warning. Proceed with caution."
      if floor_failures:
        reason += f" Issues: {', '.join(floor_failures[:3])}"
    elif verdict == "VOID":
      reason = "Hard floor failed. Query blocked."
      if floor_failures:
        reason += f" Failures: {', '.join(floor_failures[:3])}"
    elif verdict == "SABAR":
      reason = "SABAR protocol triggered. Cooling needed."
      if hasattr(final_state, "sabar_reason") and final_state.sabar_reason:
        reason = f"SABAR: {final_state.sabar_reason}"
    elif verdict == "888_HOLD":
      reason = "High-stakes query. Human approval required."
    else:
      reason = f"Verdict: {verdict}"

    # Extract metrics if available
    metrics = None
    if hasattr(final_state, "metrics") and final_state.metrics:
      m = final_state.metrics
      metrics = {
        "truth": getattr(m, "truth", None),
        "delta_s": getattr(m, "delta_s", None),
        "peace_squared": getattr(m, "peace_squared", None),
        "kappa_r": getattr(m, "kappa_r", None),
        "omega_0": getattr(m, "omega_0", None),
        "amanah": getattr(m, "amanah", None),
      }

    return JudgeResponse(
      verdict=verdict,
      reason=reason,
      metrics=metrics,
      floor_failures=floor_failures,
    )

  except Exception as e:
    return JudgeResponse(
      verdict="ERROR",
      reason=f"Pipeline error: {str(e)}",
      metrics=None,
      floor_failures=[f"ERROR: {str(e)}"],
    )

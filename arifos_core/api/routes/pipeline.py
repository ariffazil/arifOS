"""
arifOS API Pipeline Routes - Run queries through the governed pipeline.

This is the main endpoint for executing governed LLM calls.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter

from ..exceptions import PipelineError
from ..models import PipelineRunRequest, PipelineRunResponse, PipelineMetrics

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


# =============================================================================
# PIPELINE ENDPOINTS
# =============================================================================

@router.post("/run", response_model=PipelineRunResponse)
async def run_pipeline(request: PipelineRunRequest) -> PipelineRunResponse:
    """
    Run a query through the governed pipeline.

    The pipeline enforces all 9 constitutional floors and returns
    a verdict along with the response.

    Verdicts:
    - SEAL: All floors pass, response is approved
    - PARTIAL: Soft floors failed, response with warnings
    - VOID: Hard floor failed, response blocked
    - SABAR: Protocol triggered, needs cooling
    - 888_HOLD: High-stakes, awaiting human approval
    """
    try:
        from arifos_core.pipeline import Pipeline

        # Create pipeline with default stub LLM
        # In production, this would use a real LLM via LiteLLM
        def stub_llm(prompt: str) -> str:
            """Stub LLM for API testing."""
            return f"[Governed Response] Processed query: {prompt[:100]}..."

        pipeline = Pipeline(llm_generate=stub_llm)

        # Generate job_id if not provided
        job_id = request.job_id or f"api-{uuid.uuid4().hex[:8]}"

        # Run the pipeline
        final_state = pipeline.run(request.query)

        # Extract response text
        response_text = ""
        if hasattr(final_state, "raw_response") and final_state.raw_response:
            response_text = final_state.raw_response
        elif hasattr(final_state, "draft_response") and final_state.draft_response:
            response_text = final_state.draft_response
        elif hasattr(final_state, "output") and final_state.output:
            response_text = final_state.output
        else:
            response_text = "[No response generated]"

        # Extract verdict
        verdict = "UNKNOWN"
        if hasattr(final_state, "verdict") and final_state.verdict:
            verdict = str(final_state.verdict)
        elif hasattr(final_state, "apex_verdict") and final_state.apex_verdict:
            verdict = str(final_state.apex_verdict)

        # Extract metrics if available
        metrics = None
        if hasattr(final_state, "metrics") and final_state.metrics:
            m = final_state.metrics
            metrics = PipelineMetrics(
                truth=getattr(m, "truth", None),
                delta_s=getattr(m, "delta_s", None),
                peace_squared=getattr(m, "peace_squared", None),
                kappa_r=getattr(m, "kappa_r", None),
                omega_0=getattr(m, "omega_0", None),
                amanah=getattr(m, "amanah", None),
                rasa=getattr(m, "rasa", None),
                anti_hantu=getattr(m, "anti_hantu", None),
            )

            # Add GENIUS metrics if available
            try:
                from arifos_core.genius_metrics import (
                    compute_genius_index,
                    compute_dark_cleverness,
                    compute_psi_score,
                )
                metrics.genius_g = compute_genius_index(m)
                metrics.genius_c_dark = compute_dark_cleverness(m)
                metrics.genius_psi = compute_psi_score(m)
            except Exception:
                pass  # GENIUS metrics are optional

        # Extract floor failures and stage trace
        floor_failures = []
        stage_trace = []
        if hasattr(final_state, "floor_failures"):
            floor_failures = list(final_state.floor_failures or [])
        if hasattr(final_state, "stage_trace"):
            stage_trace = list(final_state.stage_trace or [])

        # Use job_id from state if available
        if hasattr(final_state, "job_id") and final_state.job_id:
            job_id = final_state.job_id

        return PipelineRunResponse(
            verdict=verdict,
            response=response_text,
            job_id=job_id,
            metrics=metrics,
            floor_failures=floor_failures,
            stage_trace=stage_trace,
        )

    except Exception as e:
        raise PipelineError(
            message=f"Pipeline execution failed: {str(e)}",
            details={"query_length": len(request.query)},
        )


@router.get("/status")
async def pipeline_status() -> dict:
    """
    Get pipeline status and configuration.

    Returns information about the current pipeline setup.
    """
    try:
        from arifos_core.runtime_manifest import get_active_epoch

        epoch = get_active_epoch()
    except Exception:
        epoch = "v38"

    return {
        "status": "available",
        "epoch": epoch,
        "routing": {
            "class_a": "fast (000 → 111 → 333 → 888 → 999)",
            "class_b": "deep (full pipeline)",
        },
        "verdicts": ["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD", "SUNSET"],
    }

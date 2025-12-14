"""
arifOS API Pipeline Routes - Run queries through the governed pipeline.

This is the main endpoint for executing governed LLM calls.
"""

from __future__ import annotations

import os
import uuid
import traceback
from typing import Optional, Callable, List

from fastapi import APIRouter, Query, HTTPException

from ..exceptions import PipelineError
from ..models import PipelineRunRequest, PipelineRunResponse, PipelineMetrics
from arifos_core.contracts.apex_prime_output_v41 import serialize_public

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# LiteLLM integration
try:
    from arifos_core.connectors.litellm_gateway import make_llm_generate
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    make_llm_generate = None


# =============================================================================
# LLM BACKEND SELECTOR
# =============================================================================

def _get_llm_generate() -> Callable[[str], str]:
    """
    Get LLM generate function based on environment configuration.
    
    Priority:
    1. LiteLLM (if ARIF_LLM_API_KEY is set and litellm is installed)
    2. Stub mode (for testing without external LLM)
    
    Returns:
        Callable that takes a prompt string and returns response string
    """
    # Check for LiteLLM configuration
    if LITELLM_AVAILABLE and os.getenv("ARIF_LLM_API_KEY"):
        try:
            return make_llm_generate()
        except Exception as e:
            # Log warning but fallback to stub
            print(f"[WARNING] LiteLLM initialization failed: {e}")
            print("[WARNING] Falling back to stub mode")
    
    # Fallback to stub mode
    def stub_llm(prompt: str) -> str:
        """Stub LLM for API testing without external LLM."""
        return f"[STUB MODE] Simulated response to: {prompt[:80]}..."
    
    return stub_llm


# =============================================================================
# PIPELINE ENDPOINTS
# =============================================================================

@router.post("/run")
async def run_pipeline(request: PipelineRunRequest) -> dict:
    """
    Run a query through the governed pipeline.

    The pipeline enforces all 9 constitutional floors and returns
    a verdict along with the response.
    
    LLM Backend:
    - If ARIF_LLM_API_KEY is set: Uses LiteLLM (SEA-LION or other provider)
    - Otherwise: Uses stub mode for testing

    Verdicts:
    - SEAL: All floors pass, response is approved
    - PARTIAL: Soft floors failed, response with warnings
    - VOID: Hard floor failed, response blocked
    - SABAR: Protocol triggered, needs cooling
    - 888_HOLD: High-stakes, awaiting human approval
    """
    try:
        from arifos_core.pipeline import Pipeline

        # Get LLM backend (LiteLLM if configured, else stub)
        llm_generate = _get_llm_generate()

        # Create pipeline with the selected backend
        pipeline = Pipeline(llm_generate=llm_generate)

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

        pub_verdict = _public_verdict(verdict)

        # psi_internal: prefer genius_psi if present, else None (never fake)
        psi_internal = None
        if metrics is not None and getattr(metrics, "genius_psi", None) is not None:
            try:
                psi_internal = float(metrics.genius_psi)
            except Exception:
                psi_internal = None

        reason_code = _reason_from_failures(floor_failures)

        return serialize_public(
            verdict=pub_verdict,          # SEAL|SABAR|VOID
            psi_internal=psi_internal,    # float or None
            response=response_text,
            reason_code=reason_code,
        )

    except Exception as e:
        print(f"[API] Pipeline error: {e}")
        print(f"[API] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@router.post("/run/debug", response_model=PipelineRunResponse)
async def run_pipeline_debug(request: PipelineRunRequest) -> PipelineRunResponse:
    """
    Run a query through the governed pipeline with full debug payload.
    
    Returns the complete internal telemetry for debugging and operations.
    Use /run for the public APEX PRIME contract.
    """
    try:
        from arifos_core.pipeline import Pipeline

        # Get LLM backend (LiteLLM if configured, else stub)
        llm_generate = _get_llm_generate()

        # Create pipeline with the selected backend
        pipeline = Pipeline(llm_generate=llm_generate)

        # Generate job_id if not provided
        job_id = request.job_id or f"debug-{uuid.uuid4().hex[:8]}"

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
        print(f"[API] Debug Pipeline error: {e}")
        print(f"[API] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Debug Pipeline execution failed: {str(e)}")


def _public_verdict(v: str) -> str:
    """
    Collapse internal verdicts to public 3-state contract.
    - PARTIAL delivers output => public SEAL
    - 888_HOLD => public SABAR (but kept internally in ledger/debug)
    """
    s = (v or "").upper()
    if s == "SEAL":
        return "SEAL"
    if s in ("SABAR", "888_HOLD"):
        return "SABAR"
    if s == "PARTIAL":
        return "SEAL"
    if s == "VOID":
        return "VOID"
    # safest fallback: refuse
    return "VOID"

def _reason_from_failures(failures: List[str]) -> Optional[str]:
    """
    Map failures to a SINGLE F1–F9 token. No prose.
    Includes W@W organ veto patterns.
    """
    if not failures:
        return None
    f = str(failures[0]).upper()

    # W@W organ veto patterns -> map to existing floors (no new floor codes)
    if "@PROMPT" in f or "W@W VETO" in f or "PROMPT" in f:
        return "F5(AMANAH)"
    if "@WEALTH" in f or "WEALTH" in f:
        return "F5(AMANAH)"
    if "@WELL" in f or "WELL" in f:
        return "F3(PEACE2)"
    if "@GEOX" in f or "GEOX" in f or "EARTH" in f:
        return "F1(TRUTH)"

    # Traditional floor patterns
    if "TRUTH" in f:
        return "F1(TRUTH)"
    if "DELTA" in f or "CLARITY" in f or "ΔS" in f:
        return "F2(DELTA_S)"
    if "PEACE" in f or "STABILITY" in f:
        return "F3(PEACE2)"
    if "KAPPA" in f or "EMPATH" in f:
        return "F4(KAPPA_R)"
    if "AMANAH" in f or "INTEGRITY" in f:
        return "F5(AMANAH)"
    if "OMEGA" in f:
        return "F6(OMEGA0)"
    if "RASA" in f:
        return "F7(RASA)"
    if "TRI" in f or "WITNESS" in f:
        return "F8(TRI_WITNESS)"
    if "HANTU" in f or "ONTOLOGY" in f or "SOUL" in f:
        return "F9(ANTI_HANTU)"

    return None

def _get_llm_generate() -> Callable:
    """
    Get the appropriate LLM generation function.
    
    Returns:
        - LiteLLM function if ARIF_LLM_API_KEY is configured
        - Stub function otherwise
    """
    if LITELLM_AVAILABLE and os.getenv("ARIF_LLM_API_KEY"):
        # Use LiteLLM with environment configuration
        from arifos_core.connectors.litellm_gateway import make_llm_generate
        return make_llm_generate()
    else:
        # Use stub LLM for testing/demo
        def stub_llm_generate(prompt: str, **kwargs) -> str:
            return f"[STUB] Received query: {prompt[:100]}..."
        return stub_llm_generate


@router.get("/status")
async def pipeline_status() -> dict:
    """
    Get pipeline status and configuration.

    Returns information about the current pipeline setup, including
    LLM backend configuration.
    """
    try:
        from arifos_core.runtime_manifest import get_active_epoch
        epoch = get_active_epoch()
    except Exception:
        epoch = "v38"
    
    # Detect LLM backend
    llm_backend = "stub"
    llm_config = {}
    
    if LITELLM_AVAILABLE and os.getenv("ARIF_LLM_API_KEY"):
        llm_backend = "litellm"
        llm_config = {
            "provider": os.getenv("ARIF_LLM_PROVIDER", "openai"),
            "api_base": os.getenv("ARIF_LLM_API_BASE", "not_set"),
            "model": os.getenv("ARIF_LLM_MODEL", "aisingapore/Llama-SEA-LION-v3-70B-IT"),
        }

    return {
        "status": "available",
        "epoch": epoch,
        "llm_backend": llm_backend,
        "llm_config": llm_config,
        "routing": {
            "class_a": "fast (000 → 111 → 333 → 888 → 999)",
            "class_b": "deep (full pipeline)",
        },
        "verdicts": ["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD", "SUNSET"],
        "contracts": {
            "public": "/pipeline/run - APEX PRIME contract {verdict, apex_pulse, response, reason_code?}",
            "debug": "/pipeline/run/debug - Full PipelineRunResponse for debugging"
        }
    }

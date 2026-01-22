"""
arifOS API Pipeline Routes - Run queries through quantum constitutional validation.

AAA-Level Migration (v47.1+): Uses quantum orthogonal executor for LLM + validation.
Architecture: LLM Generation ⊥ Quantum Validation (dot_product = 0)

This is the main endpoint for executing governed LLM calls with parallel AGI+ASI validation.
"""

from __future__ import annotations

import os
import uuid
import traceback
from typing import Optional, Callable, List

from fastapi import APIRouter, Query, HTTPException

from ..exceptions import PipelineError
from ..models import PipelineRunRequest, PipelineRunResponse, PipelineMetrics
from arifos.core.apex.contracts.apex_prime_output_v41 import serialize_public

# AAA-Level: Import quantum helpers instead of old pipeline
from arifos.core.mcp import generate_and_validate_async

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# LiteLLM integration
try:
    from arifos.core.integration.connectors.litellm_gateway import make_llm_generate
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
    Run a query through quantum constitutional validation (AAA-level).

    AAA Architecture:
    1. LLM generates response (external - LiteLLM or stub)
    2. Quantum validates response (independent - parallel AGI+ASI+APEX)
    3. Returns verdict + response if SEAL

    LLM Backend:
    - If ARIF_LLM_API_KEY is set: Uses LiteLLM (SEA-LION or other provider)
    - Otherwise: Uses stub mode for testing

    Verdicts:
    - SEAL: All constitutional floors pass, response approved
    - PARTIAL: Soft floors failed, response with warnings
    - VOID: Hard floor failed, response blocked
    - SABAR: Protocol triggered, needs cooling
    """
    try:
        # Get LLM backend (LiteLLM if configured, else stub)
        llm_generate_sync = _get_llm_generate()

        # AAA-Level: Async wrapper for sync LLM function
        async def llm_generate_async(query: str, **kwargs) -> str:
            return llm_generate_sync(query)

        # Generate job_id if not provided
        job_id = request.job_id or f"api-{uuid.uuid4().hex[:8]}"

        # AAA-Level: Generate + Validate (LLM ⊥ Quantum)
        draft_response, quantum_state = await generate_and_validate_async(
            query=request.query,
            llm_generate=llm_generate_async,
            context={"job_id": job_id, "user_id": request.user_id}
        )

        # AAA-Level: Response is the LLM-generated text
        response_text = draft_response

        # AAA-Level: Verdict from quantum state
        verdict = quantum_state.final_verdict or "UNKNOWN"

        # AAA-Level: Extract metrics from quantum particles
        metrics = None
        if quantum_state.agi_particle or quantum_state.asi_particle:
            metrics = PipelineMetrics(
                # AGI metrics
                truth=getattr(quantum_state.agi_particle, 'truth_score', None) if quantum_state.agi_particle else None,
                delta_s=getattr(quantum_state.agi_particle, 'entropy_delta', None) if quantum_state.agi_particle else None,

                # ASI metrics
                peace_squared=getattr(quantum_state.asi_particle, 'peace_score', None) if quantum_state.asi_particle else None,
                kappa_r=getattr(quantum_state.asi_particle, 'kappa_r', None) if quantum_state.asi_particle else None,
                omega_0=getattr(quantum_state.asi_particle, 'omega_zero', None) if quantum_state.asi_particle else None,
                rasa=getattr(quantum_state.asi_particle, 'rasa', None) if quantum_state.asi_particle else None,

                # APEX metrics
                amanah=1.0 if verdict == "SEAL" else 0.0,
                anti_hantu=1.0,  # Always enforced by quantum
            )

            # GENIUS metrics (optional)
            try:
                from arifos.core.enforcement.genius_metrics import (
                    compute_genius_index,
                    compute_dark_cleverness,
                    compute_psi_score,
                )
                # Convert quantum state to metrics dict for GENIUS
                m_dict = {
                    'truth': metrics.truth or 0.95,
                    'delta_s': metrics.delta_s or 0.0,
                    'peace_squared': metrics.peace_squared or 1.0,
                    'kappa_r': metrics.kappa_r or 0.95,
                    'omega_0': metrics.omega_0 or 0.04,
                }
                from types import SimpleNamespace
                m = SimpleNamespace(**m_dict)
                metrics.genius_g = compute_genius_index(m)
                metrics.genius_c_dark = compute_dark_cleverness(m)
                metrics.genius_psi = compute_psi_score(m)
            except Exception:
                pass  # GENIUS metrics are optional

        # Extract floor failures from quantum particles
        floor_failures = []
        if quantum_state.agi_particle and hasattr(quantum_state.agi_particle, 'verdict'):
            if quantum_state.agi_particle.verdict not in ["SEAL", "PASSED"]:
                floor_failures.append(f"AGI: {quantum_state.agi_particle.verdict}")
        if quantum_state.asi_particle and hasattr(quantum_state.asi_particle, 'verdict'):
            if quantum_state.asi_particle.verdict not in ["SEAL", "PASSED"]:
                floor_failures.append(f"ASI: {quantum_state.asi_particle.verdict}")

        # Stage trace: Quantum particles (not sequential stages)
        stage_trace = ["000_VOID", "AGI_PARTICLE", "ASI_PARTICLE", "APEX_MEASUREMENT", "999_SEAL"]

        pub_verdict = _public_verdict(verdict)

        # psi_internal: prefer genius_psi if present, else None
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
        print(f"[API] Quantum validation error: {e}")
        print(f"[API] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Quantum validation failed: {str(e)}")


@router.post("/run/debug", response_model=PipelineRunResponse)
async def run_pipeline_debug(request: PipelineRunRequest) -> PipelineRunResponse:
    """
    Run a query through quantum constitutional validation with full debug payload (AAA-level).

    AAA Architecture:
    1. LLM generates response (external - LiteLLM or stub)
    2. Quantum validates response (independent - parallel AGI+ASI+APEX)
    3. Returns complete internal telemetry for debugging

    Use /run for the public APEX PRIME contract.
    """
    try:
        # Get LLM backend (LiteLLM if configured, else stub)
        llm_generate_sync = _get_llm_generate()

        # AAA-Level: Async wrapper for sync LLM function
        async def llm_generate_async(query: str, **kwargs) -> str:
            return llm_generate_sync(query)

        # Generate job_id if not provided
        job_id = request.job_id or f"debug-{uuid.uuid4().hex[:8]}"

        # AAA-Level: Generate + Validate (LLM ⊥ Quantum)
        draft_response, quantum_state = await generate_and_validate_async(
            query=request.query,
            llm_generate=llm_generate_async,
            context={"job_id": job_id, "user_id": request.user_id}
        )

        # AAA-Level: Response is the LLM-generated text
        response_text = draft_response if draft_response else "[No response generated]"

        # AAA-Level: Verdict from quantum state
        verdict = quantum_state.final_verdict or "UNKNOWN"

        # AAA-Level: Extract metrics from quantum particles
        metrics = None
        if quantum_state.agi_particle or quantum_state.asi_particle:
            metrics = PipelineMetrics(
                # AGI metrics
                truth=getattr(quantum_state.agi_particle, 'truth_score', None) if quantum_state.agi_particle else None,
                delta_s=getattr(quantum_state.agi_particle, 'entropy_delta', None) if quantum_state.agi_particle else None,

                # ASI metrics
                peace_squared=getattr(quantum_state.asi_particle, 'peace_score', None) if quantum_state.asi_particle else None,
                kappa_r=getattr(quantum_state.asi_particle, 'kappa_r', None) if quantum_state.asi_particle else None,
                omega_0=getattr(quantum_state.asi_particle, 'omega_zero', None) if quantum_state.asi_particle else None,
                rasa=getattr(quantum_state.asi_particle, 'rasa', None) if quantum_state.asi_particle else None,

                # APEX metrics
                amanah=1.0 if verdict == "SEAL" else 0.0,
                anti_hantu=1.0,  # Always enforced by quantum
            )

            # GENIUS metrics (optional)
            try:
                from arifos.core.enforcement.genius_metrics import (
                    compute_genius_index,
                    compute_dark_cleverness,
                    compute_psi_score,
                )
                # Convert quantum state to metrics dict for GENIUS
                m_dict = {
                    'truth': metrics.truth or 0.95,
                    'delta_s': metrics.delta_s or 0.0,
                    'peace_squared': metrics.peace_squared or 1.0,
                    'kappa_r': metrics.kappa_r or 0.95,
                    'omega_0': metrics.omega_0 or 0.04,
                }
                from types import SimpleNamespace
                m = SimpleNamespace(**m_dict)
                metrics.genius_g = compute_genius_index(m)
                metrics.genius_c_dark = compute_dark_cleverness(m)
                metrics.genius_psi = compute_psi_score(m)
            except Exception:
                pass  # GENIUS metrics are optional

        # Extract floor failures from quantum particles
        floor_failures = []
        if quantum_state.agi_particle and hasattr(quantum_state.agi_particle, 'verdict'):
            if quantum_state.agi_particle.verdict not in ["SEAL", "PASSED"]:
                floor_failures.append(f"AGI: {quantum_state.agi_particle.verdict}")
        if quantum_state.asi_particle and hasattr(quantum_state.asi_particle, 'verdict'):
            if quantum_state.asi_particle.verdict not in ["SEAL", "PASSED"]:
                floor_failures.append(f"ASI: {quantum_state.asi_particle.verdict}")

        # Stage trace: Quantum particles (not sequential stages)
        stage_trace = ["000_VOID", "AGI_PARTICLE", "ASI_PARTICLE", "APEX_MEASUREMENT", "999_SEAL"]

        # job_id from context (already set above)
        # No need to extract from state

        return PipelineRunResponse(
            verdict=verdict,
            response=response_text,
            job_id=job_id,
            metrics=metrics,
            floor_failures=floor_failures,
            stage_trace=stage_trace,
        )

    except Exception as e:
        print(f"[API] Debug Quantum validation error: {e}")
        print(f"[API] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Debug Quantum validation failed: {str(e)}")


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
        from arifos.core.integration.connectors.litellm_gateway import make_llm_generate
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
        from arifos.core.system.runtime_manifest import get_active_epoch
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

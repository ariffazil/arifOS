"""
arifOS API Health Routes - Liveness and readiness probes.

These endpoints are lightweight and suitable for k8s/docker health checks.
"""

from __future__ import annotations

from fastapi import APIRouter

from ..models import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


# =============================================================================
# HEALTH ENDPOINTS
# =============================================================================

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check - always returns healthy if the server is running.

    This is a lightweight probe suitable for load balancers.
    """
    return HealthResponse(
        status="healthy",
        details={"service": "arifos-api"},
        version="v38.2-alpha",
    )


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check() -> ReadyResponse:
    """
    Readiness check - verifies that dependencies are available.

    Checks:
    - Pipeline can be instantiated
    - L7 memory availability (optional, fail-open)
    """
    details = {}
    pipeline_available = True
    l7_available = False

    # Check pipeline availability
    try:
        from arifos_core.pipeline import Pipeline
        _ = Pipeline  # Just verify import succeeds
        details["pipeline"] = "available"
    except Exception as e:
        pipeline_available = False
        details["pipeline"] = f"unavailable: {str(e)}"

    # Check L7 memory availability (fail-open)
    try:
        from arifos_core.memory import Memory
        memory = Memory()
        l7_available = memory.is_enabled()
        details["l7_memory"] = "available" if l7_available else "disabled"
    except Exception as e:
        # L7 is optional - fail open
        details["l7_memory"] = f"unavailable: {str(e)}"

    return ReadyResponse(
        ready=pipeline_available,
        pipeline_available=pipeline_available,
        l7_available=l7_available,
        details=details,
    )


@router.get("/live")
async def liveness_check() -> dict:
    """
    Quick liveness probe - minimal overhead.

    Returns immediately without checking dependencies.
    Suitable for rapid health polling.
    """
    return {"live": True}

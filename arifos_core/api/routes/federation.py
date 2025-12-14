"""
Federation API Routes - L7 Federation Router endpoints.

Provides FastAPI routes for:
- POST /federation/route - Route requests through the federation
- GET /federation/status - Get federation status
- GET /federation/organs - List all organs

Author: arifOS Project
Version: v41.3Omega
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from ..models_federation import (
    FederationRouteRequest,
    FederationRouteResponse,
    FederationStatusResponse,
    OrganListResponse,
    OrganStatus,
    LedgerStats,
    CoolingMetrics,
    CoolingEntryResponse,
)

# Import federation router
try:
    from arifos_core.connectors.federation_router import (
        FederationRouter,
        load_federation_config,
    )
    FEDERATION_AVAILABLE = True
except ImportError:
    FEDERATION_AVAILABLE = False
    FederationRouter = None
    load_federation_config = None


router = APIRouter(prefix="/federation", tags=["federation"])

# Global router instance (lazy initialization)
_federation_router: FederationRouter = None


def _get_federation_router() -> FederationRouter:
    """Get or create the federation router instance."""
    global _federation_router

    if not FEDERATION_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Federation router not available. Check installation."
        )

    if _federation_router is None:
        _federation_router = FederationRouter()

    return _federation_router


# =============================================================================
# ROUTES
# =============================================================================

@router.post("/route", response_model=FederationRouteResponse)
async def route_request(request: FederationRouteRequest) -> FederationRouteResponse:
    """
    Route a request through the L7 Federation.

    This is the main entry point for governed multi-model routing.

    Pipeline:
    1. [000] SENTINEL GATE - SEA-Guard safety pre-filter
    2. [111] INTENT ROUTER - Classify intent and select organ
    3. [333] EXECUTION - Call target organ
    4. [888] COOLING LEDGER - Audit and thermodynamic metrics
    5. [999] VERDICT - Return governed response

    Routing Logic:
    - Multimodal content → @GEOX (Gemma vision)
    - Long context (>30k) → @WEALTH (Qwen 128k)
    - Reasoning keywords → @RIF (Llama-R)
    - Default → @WELL (Llama-IT)

    Verdicts:
    - SEAL: All floors pass, response approved
    - SABAR: Empathy floor failed, held for review
    - PARTIAL: Low entropy warning
    - VOID: Safety breach, blocked
    """
    fed_router = _get_federation_router()

    # Convert Pydantic messages to dict
    messages = [
        {"role": m.role, "content": m.content}
        for m in request.messages
    ]

    # Determine if forcing specific organ
    force_organ = None
    if request.model and request.model != "arifos-auto":
        force_organ = request.model.upper()

    # Route through federation
    result = await fed_router.route(
        messages=messages,
        temperature=request.temperature or 0.7,
        skip_guard=request.skip_guard or False,
        force_organ=force_organ,
    )

    # Build cooling entry response if available
    cooling_entry = None
    if result.cooling_entry:
        entry = result.cooling_entry
        cooling_entry = CoolingEntryResponse(
            timestamp=entry.timestamp,
            organ=entry.organ,
            verdict=entry.verdict,
            metrics=CoolingMetrics(
                delta_s=entry.metrics.get("delta_s", 0.0),
                kappa_r=entry.metrics.get("kappa_r", 0.0),
                tau_ms=entry.metrics.get("tau_ms", 0.0),
            ),
            entry_hash=entry.entry_hash,
            prev_hash=entry.prev_hash,
        )

    # Build OpenAI-compatible response
    return FederationRouteResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        object="chat.completion",
        created=int(time.time()),
        model=request.model or "arifos-auto",
        choices=[
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result.response,
                },
                "finish_reason": "stop",
            }
        ],
        verdict=result.verdict,
        routed_to=result.organ,
        guard_passed=result.guard_passed,
        guard_latency_ms=result.guard_latency_ms,
        total_latency_ms=result.total_latency_ms,
        confidence=result.confidence,
        cooling_entry=cooling_entry,
    )


@router.post("/v1/chat/completions")
async def chat_completions_compat(request: FederationRouteRequest) -> Dict[str, Any]:
    """
    OpenAI-compatible chat completions endpoint.

    This endpoint provides drop-in compatibility with OpenAI clients.
    Use this when you want to point existing tools (Cursor, Claude, etc.)
    at the arifOS federation.

    Example:
        client = OpenAI(
            base_url="http://localhost:9000/federation",
            api_key="sk-arifos-sovereign"
        )
        response = client.chat.completions.create(
            model="arifos-auto",
            messages=[{"role": "user", "content": "Hello"}]
        )
    """
    # Reuse the main route handler
    result = await route_request(request)

    # Return just the OpenAI-compatible portion
    return {
        "id": result.id,
        "object": result.object,
        "created": result.created,
        "model": result.model,
        "choices": result.choices,
        "usage": {
            "prompt_tokens": 0,  # Would need tokenizer to compute
            "completion_tokens": 0,
            "total_tokens": 0,
        },
        # arifOS extensions (safe to include, clients ignore unknown fields)
        "arifos_verdict": result.verdict,
        "arifos_organ": result.routed_to,
        "arifos_confidence": result.confidence,
    }


@router.get("/status", response_model=FederationStatusResponse)
async def get_federation_status() -> FederationStatusResponse:
    """
    Get status of the L7 Federation.

    Returns information about all organs, their health status,
    the cooling ledger, and routing configuration.
    """
    fed_router = _get_federation_router()
    config = fed_router.config

    # Get organ status
    organ_status = fed_router.get_organ_status()
    organs = {
        name: OrganStatus(
            name=info["name"],
            role=info["role"],
            symbol=info["symbol"],
            port=info["port"],
            model=info["model"],
            provider=info["provider"],
            is_healthy=info["is_healthy"],
            capabilities=info["capabilities"],
        )
        for name, info in organ_status.items()
    }

    # Get ledger stats
    ledger_stats = fed_router.get_ledger_stats()
    ledger = LedgerStats(
        entries=ledger_stats["entries"],
        verdicts=ledger_stats["verdicts"],
        chain_valid=ledger_stats["chain_valid"],
        last_entry=ledger_stats.get("last_entry"),
    )

    # Determine overall health
    healthy_count = sum(1 for o in organs.values() if o.is_healthy)
    total_count = len(organs)

    if healthy_count == total_count:
        status = "healthy"
    elif healthy_count > 0:
        status = "degraded"
    else:
        status = "offline"

    return FederationStatusResponse(
        status=status,
        version="v41.3Omega",
        mock_mode=config.mock_mode,
        routing_strategy=config.routing_strategy,
        confidence_floor=config.confidence_floor,
        default_organ=config.default_organ,
        organs=organs,
        ledger=ledger,
    )


@router.get("/organs", response_model=OrganListResponse)
async def list_organs() -> OrganListResponse:
    """
    List all Federation organs.

    Returns detailed information about each organ including
    its role, model, port, and capabilities.
    """
    fed_router = _get_federation_router()
    organ_status = fed_router.get_organ_status()

    organs = [
        OrganStatus(
            name=info["name"],
            role=info["role"],
            symbol=info["symbol"],
            port=info["port"],
            model=info["model"],
            provider=info["provider"],
            is_healthy=info["is_healthy"],
            capabilities=info["capabilities"],
        )
        for info in organ_status.values()
    ]

    return OrganListResponse(
        organs=organs,
        total=len(organs),
    )


@router.get("/ledger")
async def get_cooling_ledger(limit: int = 100) -> Dict[str, Any]:
    """
    Get recent entries from the Cooling Ledger.

    Args:
        limit: Maximum number of entries to return (default 100)

    Returns:
        Ledger entries with hash chain verification status
    """
    fed_router = _get_federation_router()

    entries = fed_router.ledger.to_dict()[-limit:]
    is_valid = fed_router.ledger.verify_chain()

    return {
        "entries": entries,
        "total": len(fed_router.ledger.chain),
        "returned": len(entries),
        "chain_valid": is_valid,
    }


@router.get("/health")
async def federation_health() -> Dict[str, Any]:
    """
    Simple health check endpoint.

    Returns minimal status for load balancer probes.
    """
    try:
        fed_router = _get_federation_router()
        return {
            "status": "ok",
            "mock_mode": fed_router.config.mock_mode,
            "organs": len(fed_router.config.organs),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }

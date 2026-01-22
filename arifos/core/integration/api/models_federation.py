"""
Federation API Models - Pydantic schemas for L7 Federation Router.

These models define the request/response contracts for the federation API.

Author: arifOS Project
Version: v41.3Omega
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# =============================================================================
# REQUEST MODELS
# =============================================================================

class ChatMessage(BaseModel):
    """A single chat message (OpenAI-compatible format)."""
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: Union[str, List[Dict[str, Any]]] = Field(
        ...,
        description="Message content (text or multimodal list)"
    )


class FederationRouteRequest(BaseModel):
    """Request to route through the L7 Federation."""
    messages: List[ChatMessage] = Field(
        ...,
        description="Chat messages in OpenAI format",
        min_length=1,
    )
    model: Optional[str] = Field(
        default="arifos-auto",
        description="Model selector: 'arifos-auto' for intelligent routing, "
                    "or organ name (GEOX, RIF, WEALTH, WELL) to force routing"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Generation temperature"
    )
    skip_guard: Optional[bool] = Field(
        default=False,
        description="Skip SEA-Guard sentinel check (testing only)"
    )
    stream: Optional[bool] = Field(
        default=False,
        description="Stream response (not yet implemented)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "Analyze this problem step by step."}
                ],
                "model": "arifos-auto",
                "temperature": 0.7,
            }
        }


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class CoolingMetrics(BaseModel):
    """Thermodynamic metrics from the Cooling Ledger."""
    delta_s: float = Field(..., description="Shannon entropy (ΔS) of response tokens")
    kappa_r: float = Field(..., description="Empathy conductance (κᵣ) score")
    tau_ms: float = Field(..., description="Dissipation time (τ) in milliseconds")


class CoolingEntryResponse(BaseModel):
    """A single entry from the Cooling Ledger."""
    timestamp: str = Field(..., description="ISO timestamp of entry")
    organ: str = Field(..., description="Which organ handled the request")
    verdict: str = Field(..., description="Constitutional verdict: SEAL, SABAR, PARTIAL, VOID")
    metrics: CoolingMetrics = Field(..., description="Thermodynamic metrics")
    entry_hash: str = Field(..., description="SHA256 hash of this entry")
    prev_hash: str = Field(..., description="Hash of previous entry (chain)")


class FederationRouteResponse(BaseModel):
    """Response from federation routing."""
    # OpenAI-compatible fields
    id: str = Field(..., description="Response ID")
    object: str = Field(default="chat.completion", description="Object type")
    created: int = Field(..., description="Unix timestamp")
    model: str = Field(..., description="Model that handled the request")
    choices: List[Dict[str, Any]] = Field(..., description="Response choices")

    # arifOS governance fields
    verdict: str = Field(..., description="Constitutional verdict: SEAL, SABAR, PARTIAL, VOID")
    routed_to: str = Field(..., description="Which organ handled the request")
    guard_passed: bool = Field(..., description="Whether SEA-Guard check passed")
    guard_latency_ms: float = Field(..., description="Guard check latency in ms")
    total_latency_ms: float = Field(..., description="Total processing time in ms")
    confidence: float = Field(..., description="Routing confidence score")
    cooling_entry: Optional[CoolingEntryResponse] = Field(
        default=None,
        description="Cooling Ledger entry for this request"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chatcmpl-abc123",
                "object": "chat.completion",
                "created": 1702500000,
                "model": "arifos-auto",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Here is my step-by-step analysis..."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "verdict": "SEAL",
                "routed_to": "RIF",
                "guard_passed": True,
                "guard_latency_ms": 45.2,
                "total_latency_ms": 1250.5,
                "confidence": 0.85,
            }
        }


# =============================================================================
# STATUS MODELS
# =============================================================================

class OrganStatus(BaseModel):
    """Status of a single Federation organ."""
    name: str = Field(..., description="Internal organ name")
    role: str = Field(..., description="Organ role: sentinel, vision, reasoning, context, chat")
    symbol: str = Field(..., description="Unicode symbol for display")
    port: int = Field(..., description="Network port")
    model: str = Field(..., description="Model identifier")
    provider: str = Field(..., description="Backend provider: ollama, vllm, tgi")
    is_healthy: bool = Field(..., description="Whether organ is responding")
    capabilities: List[str] = Field(..., description="Organ capabilities")


class LedgerStats(BaseModel):
    """Statistics from the Cooling Ledger."""
    entries: int = Field(..., description="Total entries in chain")
    verdicts: Dict[str, int] = Field(..., description="Count by verdict type")
    chain_valid: bool = Field(..., description="Whether hash chain is valid")
    last_entry: Optional[str] = Field(None, description="Timestamp of last entry")


class FederationStatusResponse(BaseModel):
    """Status of the L7 Federation."""
    status: str = Field(..., description="Overall status: healthy, degraded, offline")
    version: str = Field(..., description="arifOS version")
    mock_mode: bool = Field(..., description="Whether running in mock mode")
    routing_strategy: str = Field(..., description="Current routing strategy")
    confidence_floor: float = Field(..., description="Minimum confidence for routing")
    default_organ: str = Field(..., description="Default fallback organ")
    organs: Dict[str, OrganStatus] = Field(..., description="Status of all organs")
    ledger: LedgerStats = Field(..., description="Cooling Ledger statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "v41.3Omega",
                "mock_mode": True,
                "routing_strategy": "intent",
                "confidence_floor": 0.55,
                "default_organ": "WELL",
                "organs": {
                    "SENTINEL": {
                        "name": "sea-guard",
                        "role": "sentinel",
                        "symbol": "🛡️",
                        "port": 8005,
                        "model": "openai/sea-guard",
                        "provider": "vllm",
                        "is_healthy": True,
                        "capabilities": ["safety", "classification"]
                    }
                },
                "ledger": {
                    "entries": 42,
                    "verdicts": {"SEAL": 35, "SABAR": 5, "VOID": 2},
                    "chain_valid": True,
                    "last_entry": "2025-12-14T10:30:00Z"
                }
            }
        }


class OrganListResponse(BaseModel):
    """List of all Federation organs."""
    organs: List[OrganStatus] = Field(..., description="All configured organs")
    total: int = Field(..., description="Total number of organs")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Request models
    "ChatMessage",
    "FederationRouteRequest",
    # Response models
    "CoolingMetrics",
    "CoolingEntryResponse",
    "FederationRouteResponse",
    # Status models
    "OrganStatus",
    "LedgerStats",
    "FederationStatusResponse",
    "OrganListResponse",
]

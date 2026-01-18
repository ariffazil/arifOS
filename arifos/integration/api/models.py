"""
arifOS API Models - Pydantic schemas for API request/response.

All models are kept thin and aligned with existing L7/L8 returns.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# =============================================================================
# HEALTH MODELS
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    details: Dict[str, Any] = Field(default_factory=dict)
    version: str = "v38.2-alpha"


class ReadyResponse(BaseModel):
    """Readiness check response."""

    ready: bool = True
    pipeline_available: bool = True
    l7_available: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# PIPELINE MODELS
# =============================================================================

class PipelineRunRequest(BaseModel):
    """Request to run a query through the governed pipeline."""

    query: str = Field(..., min_length=1, description="The query to process")
    user_id: Optional[str] = Field(
        default=None, description="Optional user ID for L7 memory"
    )
    job_id: Optional[str] = Field(
        default=None, description="Optional job ID for tracking"
    )
    high_stakes: bool = Field(
        default=False, description="Force Class B (deep) pipeline routing"
    )


class PipelineMetrics(BaseModel):
    """Subset of floor metrics from pipeline run."""

    truth: Optional[float] = None
    delta_s: Optional[float] = None
    peace_squared: Optional[float] = None
    kappa_r: Optional[float] = None
    omega_0: Optional[float] = None
    amanah: Optional[bool] = None
    rasa: Optional[bool] = None
    anti_hantu: Optional[bool] = None
    genius_g: Optional[float] = None
    genius_c_dark: Optional[float] = None
    genius_psi: Optional[float] = None


class PipelineRunResponse(BaseModel):
    """Response from pipeline run."""

    verdict: str = Field(..., description="Final verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD)")
    response: str = Field(..., description="Generated response text")
    job_id: str = Field(..., description="Job ID for tracking")
    metrics: Optional[PipelineMetrics] = Field(
        default=None, description="Floor metrics (if available)"
    )
    floor_failures: List[str] = Field(
        default_factory=list, description="List of floor failures (if any)"
    )
    stage_trace: List[str] = Field(
        default_factory=list, description="Pipeline stages executed"
    )


# =============================================================================
# MEMORY MODELS
# =============================================================================

class MemoryRecallRequest(BaseModel):
    """Request to recall memories from L7."""

    user_id: str = Field(..., min_length=1, description="User ID for memory isolation")
    prompt: str = Field(..., min_length=1, description="Query prompt for semantic search")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum memories to return")


class MemoryHit(BaseModel):
    """Single memory hit from L7 recall."""

    memory_id: Optional[str] = None
    content: str = ""
    score: float = 0.0
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None


class MemoryRecallResponse(BaseModel):
    """Response from L7 memory recall."""

    memories: List[MemoryHit] = Field(default_factory=list)
    confidence_ceiling: float = Field(
        default=0.85, description="Max confidence for recalled memories"
    )
    l7_available: bool = Field(
        default=True, description="Whether L7 memory is available"
    )
    caveat: str = Field(
        default="Recalled memories are suggestions, not facts.",
        description="Governance caveat"
    )


class MemorySearchRequest(BaseModel):
    """Request to search L7 memories."""

    user_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=50)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


# =============================================================================
# LEDGER MODELS
# =============================================================================

class LedgerEntry(BaseModel):
    """Cooling ledger entry summary."""

    entry_id: str
    timestamp: Optional[str] = None
    verdict: Optional[str] = None
    user_id: Optional[str] = None
    job_id: Optional[str] = None
    hash: Optional[str] = None
    status: str = "not_implemented"


class LedgerSearchRequest(BaseModel):
    """Request to search ledger entries."""

    user_id: Optional[str] = None
    verdict: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)


class LedgerSearchResponse(BaseModel):
    """Response from ledger search."""

    entries: List[LedgerEntry] = Field(default_factory=list)
    total: int = 0
    status: str = "not_implemented"


# =============================================================================
# METRICS MODELS
# =============================================================================

class FloorThreshold(BaseModel):
    """Single floor threshold definition."""

    floor_id: str
    name: str
    threshold: Any  # Can be float, bool, or tuple for range
    type: Literal["hard", "soft", "derived"]
    description: str = ""


class MetricsResponse(BaseModel):
    """Response with system metrics and floor thresholds."""

    epoch: str = "v38"
    floors: List[FloorThreshold] = Field(default_factory=list)
    verdicts: List[str] = Field(
        default_factory=lambda: ["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD", "SUNSET"]
    )
    memory_bands: List[str] = Field(
        default_factory=lambda: ["VAULT", "LEDGER", "ACTIVE", "PHOENIX", "WITNESS", "VOID"]
    )


# =============================================================================
# ERROR MODELS
# =============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

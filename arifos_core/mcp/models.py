"""
arifOS MCP Models - Request/response models for MCP tools.

All models use Pydantic for validation and serialization.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# JUDGE TOOL MODELS
# =============================================================================

class JudgeRequest(BaseModel):
    """Request to judge a query through the governed pipeline."""

    query: str = Field(..., min_length=1, description="The query to judge")
    user_id: Optional[str] = Field(
        default=None, description="Optional user ID for context"
    )


class JudgeResponse(BaseModel):
    """Response from the judge tool."""

    verdict: str = Field(..., description="Verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD)")
    reason: str = Field(..., description="Brief explanation of the verdict")
    metrics: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional floor metrics"
    )
    floor_failures: List[str] = Field(
        default_factory=list, description="List of floor failures"
    )


# =============================================================================
# RECALL TOOL MODELS
# =============================================================================

class RecallRequest(BaseModel):
    """Request to recall memories from L7."""

    user_id: str = Field(..., min_length=1, description="User ID for memory isolation")
    prompt: str = Field(..., min_length=1, description="Query prompt for recall")
    max_results: int = Field(default=5, ge=1, le=20, description="Max memories to return")


class RecallMemory(BaseModel):
    """Single recalled memory."""

    memory_id: Optional[str] = None
    content: str = ""
    score: float = 0.0
    timestamp: Optional[str] = None


class RecallResponse(BaseModel):
    """Response from the recall tool."""

    memories: List[RecallMemory] = Field(default_factory=list)
    confidence_ceiling: float = Field(
        default=0.85, description="Max confidence for recalled memories"
    )
    l7_available: bool = Field(default=True, description="Whether L7 is available")
    caveat: str = Field(
        default="Recalled memories are suggestions, not facts.",
        description="Governance caveat (INV-4)"
    )


# =============================================================================
# AUDIT TOOL MODELS
# =============================================================================

class AuditRequest(BaseModel):
    """Request to retrieve audit/ledger data."""

    user_id: str = Field(..., min_length=1, description="User ID to audit")
    days: int = Field(default=7, ge=1, le=90, description="Number of days to look back")


class AuditEntry(BaseModel):
    """Single audit/ledger entry."""

    entry_id: str
    timestamp: Optional[str] = None
    verdict: Optional[str] = None
    query_preview: Optional[str] = None
    status: str = "not_implemented"


class AuditResponse(BaseModel):
    """Response from the audit tool."""

    entries: List[AuditEntry] = Field(default_factory=list)
    total: int = 0
    status: str = Field(
        default="not_implemented",
        description="Implementation status"
    )
    note: str = Field(
        default="Full audit access coming in future sprint",
        description="Additional information"
    )


# =============================================================================
# APEX_LLAMA TOOL MODELS
# =============================================================================


class ApexLlamaRequest(BaseModel):
    """Request to call local Llama via Ollama (APEX_LLAMA)."""

    prompt: str = Field(..., min_length=1, description="Prompt to send to Llama")
    model: str = Field(
        default="llama3",
        description="Ollama model name (e.g. llama3, llama3:8b)",
    )
    max_tokens: int = Field(
        default=512,
        ge=16,
        le=4096,
        description="Maximum tokens to generate (approximate)",
    )


class ApexLlamaResponse(BaseModel):
    """Response from APEX_LLAMA tool."""

    output: str = Field(default="", description="Raw model output from Llama")
    model: str = Field(default="llama3", description="Model used")
    elapsed_ms: int = Field(
        default=0, description="Approximate time spent in milliseconds"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if call failed"
    )

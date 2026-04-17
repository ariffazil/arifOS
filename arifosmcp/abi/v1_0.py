"""
arifOS ABI v1.0 - Application Binary Interface
==============================================

Canonical input/output schemas for all arifOS tools.

This module defines the CONTRACT between clients and the arifOS kernel.
All tools MUST implement these schemas.

Status: PHASE 1 - Canonical schema definition
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

# =============================================================================
# BASE SCHEMAS
# =============================================================================

class BaseRequest(BaseModel):
    """Base request schema with common fields."""

    risk_tier: Literal["low", "medium", "high", "critical"] = Field(
        default="low",
        description="Requested risk posture"
    )
    dry_run: bool = Field(
        default=True,
        description="If true, validate only without execution"
    )
    allow_execution: bool = Field(
        default=False,
        description="If true, execution permitted if floors pass"
    )
    request_id: str | None = Field(
        default=None,
        description="Client trace ID",
        min_length=8,
        max_length=128
    )


class BaseResponse(BaseModel):
    """Base response schema with common fields."""

    ok: bool = Field(description="Whether the request succeeded")
    verdict: str = Field(description="Constitutional verdict")
    errors: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# =============================================================================
# INIT_ANCHOR (000_INIT)
# =============================================================================

class InitAnchorRequest(BaseRequest):
    """
    Canonical input schema for init_anchor tool (ABI v1.0).

    init_anchor is the IGNITION STATE of intelligence.
    It establishes identity and constitutional context for a session.
    """

    mode: Literal["init", "revoke", "refresh", "state", "status"] = Field(
        default="init",
        description="Operation mode"
    )
    actor_id: str = Field(
        default="anonymous",
        description="Identity claimed by the caller",
        min_length=2,
        max_length=64
    )
    declared_name: str | None = Field(
        default=None,
        description="Human-readable display name",
        max_length=64
    )
    intent: str | dict | None = Field(
        default=None,
        description="User intent - string or structured object"
    )
    session_id: str | None = Field(
        default=None,
        description="Optional session ID for continuity",
        min_length=8,
        max_length=128
    )
    human_approval: bool = Field(
        default=False,
        description="Whether human has pre-approved this action (F13)"
    )

    @field_validator("actor_id")
    @classmethod
    def normalize_actor_id(cls, v: str) -> str:
        """Normalize actor ID to canonical form."""
        return v.strip().lower().replace(" ", "-").replace("_", "-")


class IdentityResolution(BaseModel):
    """Identity claim resolution details."""

    claimed_actor_id: str = Field(description="What the caller claimed")
    resolved_actor_id: str | None = Field(description="What the system accepted")
    claim_status: Literal[
        "anonymous", "claimed", "anchored", "verified", "rejected", "demoted"
    ] = Field(description="Resolution status")
    reason: str | None = Field(default=None, description="Explanation if demoted")


class InitAnchorResponse(BaseResponse):
    """Canonical output schema for init_anchor tool."""

    session_id: str = Field(description="Session ID for this session")
    auth_state: Literal["unverified", "anchored", "verified", "rejected"] = Field(
        description="Current authentication state"
    )
    identity: IdentityResolution = Field(description="Identity resolution details")
    allowed_next_tools: list[str] = Field(default_factory=list)
    abi_version: str = Field(default="1.0", description="ABI version used")


# =============================================================================
# ARIFOS_KERNEL (444_ROUTER)
# =============================================================================

class ArifOSKernelRequest(BaseRequest):
    """Canonical input schema for arifos_kernel tool."""

    query: str = Field(..., description="The query to process", min_length=1)
    intent: str | dict | None = Field(default=None, description="Structured intent")
    session_id: str | None = Field(default=None, description="Session ID")
    actor_id: str | None = Field(default=None, description="Actor ID")
    context: dict[str, Any] | None = Field(default=None, description="Additional context")


class ArifOSKernelResponse(BaseResponse):
    """Canonical output schema for arifos_kernel tool."""

    session_id: str
    result: dict[str, Any] = Field(default_factory=dict)
    stage_reached: str = Field(description="Highest metabolic stage reached")
    processing_time_ms: float = 0.0


# =============================================================================
# APEX_JUDGE (888_JUDGE)
# =============================================================================

class ApexJudgeRequest(BaseRequest):
    """Canonical input schema for apex_judge tool."""

    candidate: str = Field(..., description="Content to judge", min_length=1)
    mode: Literal["judge", "audit", "review"] = Field(default="judge")
    context: dict[str, Any] | None = Field(default=None)


class ApexJudgeResponse(BaseResponse):
    """Canonical output schema for apex_judge tool."""

    final_verdict: str
    reasoning: str
    floor_scores: dict[str, Any] = Field(default_factory=dict)
    w3_consensus: float = 0.0


# =============================================================================
# VAULT_LEDGER (999_VAULT)
# =============================================================================

class VaultLedgerRequest(BaseRequest):
    """Canonical input schema for vault_ledger tool."""

    operation: Literal["write", "read", "query", "verify"] = Field(default="query")
    entry: dict[str, Any] | None = Field(default=None, description="Entry to write")
    query_filters: dict[str, Any] | None = Field(default=None, description="Query filters")


class VaultLedgerResponse(BaseResponse):
    """Canonical output schema for vault_ledger tool."""

    entries: list[dict[str, Any]] = Field(default_factory=list)
    seal_hash: str | None = None
    merkle_root: str | None = None


# =============================================================================
# AGI_MIND (333_MIND)
# =============================================================================

class AgiMindRequest(BaseRequest):
    """Canonical input schema for agi_mind tool."""

    query: str = Field(..., min_length=1)
    mode: Literal["reason", "analyze", "synthesize"] = Field(default="reason")
    context: str | None = Field(default=None)
    evidence: list[dict[str, Any]] | None = Field(default=None)


class AgiMindResponse(BaseResponse):
    """Canonical output schema for agi_mind tool."""

    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_steps: list[dict[str, Any]] = Field(default_factory=list)
    evidence_used: list[dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# ASI_HEART (666_HEART)
# =============================================================================

class AsiHeartRequest(BaseRequest):
    """Canonical input schema for asi_heart tool."""

    content: str = Field(..., min_length=1)
    mode: Literal["critique", "simulate", "assess"] = Field(default="critique")
    stakeholders: list[str] | None = Field(default=None)


class AsiHeartResponse(BaseResponse):
    """Canonical output schema for asi_heart tool."""

    risk_level: Literal["low", "medium", "high", "critical"]
    empathy_score: float = Field(ge=0.0, le=1.0)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


# =============================================================================
# ENGINEERING_MEMORY (555_MEMORY)
# =============================================================================

class EngineeringMemoryRequest(BaseRequest):
    """Canonical input schema for engineering_memory tool."""

    operation: Literal["store", "recall", "search", "forget"] = Field(default="search")
    content: str | None = Field(default=None)
    query: str | None = Field(default=None)
    metadata: dict[str, Any] | None = Field(default=None)


class EngineeringMemoryResponse(BaseResponse):
    """Canonical output schema for engineering_memory tool."""

    memories: list[dict[str, Any]] = Field(default_factory=list)
    stored_ids: list[str] | None = None


# =============================================================================
# PHYSICS_REALITY (111_SENSE)
# =============================================================================

class PhysicsRealityRequest(BaseRequest):
    """Canonical input schema for physics_reality tool."""

    mode: Literal["time", "search", "compass", "ground"] = Field(default="time")
    query: str | None = Field(default=None)


class PhysicsRealityResponse(BaseResponse):
    """Canonical output schema for physics_reality tool."""

    mode: str
    result: dict[str, Any] = Field(default_factory=dict)
    timestamp_utc: str


# =============================================================================
# MATH_ESTIMATOR (777_OPS)
# =============================================================================

class MathEstimatorRequest(BaseRequest):
    """Canonical input schema for math_estimator tool."""

    mode: Literal["health", "cost", "budget", "thermo"] = Field(default="health")
    parameters: dict[str, Any] | None = Field(default=None)


class MathEstimatorResponse(BaseResponse):
    """Canonical output schema for math_estimator tool."""

    mode: str
    estimates: dict[str, Any] = Field(default_factory=dict)
    thermodynamic_budget: dict[str, float] = Field(default_factory=dict)


# =============================================================================
# CODE_ENGINE (M-3_EXEC)
# =============================================================================

class CodeEngineRequest(BaseRequest):
    """Canonical input schema for code_engine tool."""

    code: str | None = Field(default=None)
    language: Literal["python", "bash", "javascript"] = Field(default="python")
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    allowed_imports: list[str] | None = Field(default=None)


class CodeEngineResponse(BaseResponse):
    """Canonical output schema for code_engine tool."""

    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time_ms: float = 0.0


# =============================================================================
# ARCHITECT_REGISTRY (M-4_ARCH)
# =============================================================================

class ArchitectRegistryRequest(BaseRequest):
    """Canonical input schema for architect_registry tool."""

    mode: Literal["list", "discover", "spec"] = Field(default="list")
    tool_name: str | None = Field(default=None)


class ArchitectRegistryResponse(BaseResponse):
    """Canonical output schema for architect_registry tool."""

    tools: list[dict[str, Any]] = Field(default_factory=list)
    count: int = 0


# =============================================================================
# SCHEMA REGISTRY
# =============================================================================

ABI_SCHEMAS: dict[str, dict[str, type[BaseModel]]] = {
    "init_anchor": {
        "request": InitAnchorRequest,
        "response": InitAnchorResponse
    },
    "arifos_kernel": {
        "request": ArifOSKernelRequest,
        "response": ArifOSKernelResponse
    },
    "apex_judge": {
        "request": ApexJudgeRequest,
        "response": ApexJudgeResponse
    },
    "vault_ledger": {
        "request": VaultLedgerRequest,
        "response": VaultLedgerResponse
    },
    "agi_mind": {
        "request": AgiMindRequest,
        "response": AgiMindResponse
    },
    "asi_heart": {
        "request": AsiHeartRequest,
        "response": AsiHeartResponse
    },
    "engineering_memory": {
        "request": EngineeringMemoryRequest,
        "response": EngineeringMemoryResponse
    },
    "physics_reality": {
        "request": PhysicsRealityRequest,
        "response": PhysicsRealityResponse
    },
    "math_estimator": {
        "request": MathEstimatorRequest,
        "response": MathEstimatorResponse
    },
    "code_engine": {
        "request": CodeEngineRequest,
        "response": CodeEngineResponse
    },
    "architect_registry": {
        "request": ArchitectRegistryRequest,
        "response": ArchitectRegistryResponse
    },
}


def get_request_schema(tool_name: str) -> type[BaseModel] | None:
    """Get the request schema for a tool."""
    return ABI_SCHEMAS.get(tool_name, {}).get("request")


def get_response_schema(tool_name: str) -> type[BaseModel] | None:
    """Get the response schema for a tool."""
    return ABI_SCHEMAS.get(tool_name, {}).get("response")


def validate_request(tool_name: str, payload: dict) -> BaseModel:
    """
    Validate a request payload against the ABI schema.

    Raises:
        ValueError: If tool not found or validation fails
    """
    schema = get_request_schema(tool_name)
    if not schema:
        raise ValueError(f"No ABI schema for tool: {tool_name}")
    return schema(**payload)


def validate_response(tool_name: str, payload: dict) -> BaseModel:
    """
    Validate a response payload against the ABI schema.

    Raises:
        ValueError: If tool not found or validation fails
    """
    schema = get_response_schema(tool_name)
    if not schema:
        raise ValueError(f"No ABI schema for tool: {tool_name}")
    return schema(**payload)


__all__ = [
    # Base
    "BaseRequest",
    "BaseResponse",
    # init_anchor
    "InitAnchorRequest",
    "InitAnchorResponse", "IdentityResolution",
    # arifos_kernel
    "ArifOSKernelRequest",
    "ArifOSKernelResponse",
    # apex_judge
    "ApexJudgeRequest",
    "ApexJudgeResponse",
    # vault_ledger
    "VaultLedgerRequest",
    "VaultLedgerResponse",
    # agi_mind
    "AgiMindRequest",
    "AgiMindResponse",
    # asi_heart
    "AsiHeartRequest",
    "AsiHeartResponse",
    # engineering_memory
    "EngineeringMemoryRequest",
    "EngineeringMemoryResponse",
    # physics_reality
    "PhysicsRealityRequest",
    "PhysicsRealityResponse",
    # math_estimator
    "MathEstimatorRequest",
    "MathEstimatorResponse",
    # code_engine
    "CodeEngineRequest",
    "CodeEngineResponse",
    # architect_registry
    "ArchitectRegistryRequest",
    "ArchitectRegistryResponse",
    # Registry
    "ABI_SCHEMAS",
    "get_request_schema",
    "get_response_schema",
    "validate_request",
    "validate_response",
]

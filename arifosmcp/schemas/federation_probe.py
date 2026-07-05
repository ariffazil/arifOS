"""Federation probe schema — AAA-FORGE-RESILIENCE-v0.1"""

from __future__ import annotations

from typing import Any, List, Literal
from pydantic import BaseModel, Field


class OrganProbeResult(BaseModel):
    organ: str = Field(..., description="The name of the federation organ")
    domain: str = Field(..., description="The public/internal domain of the organ")
    health: Literal["ok", "degraded", "down"] = Field("down", description="Health status of the organ")
    ready: bool = Field(False, description="Whether the organ is fully ready")
    latency_ms: int = Field(0, description="Latency of health check probe in milliseconds")
    evidence: str = Field("direct_probe", description="Type of evidence gathered (e.g. direct_probe)")


class FederationProbeResult(BaseModel):
    checked_at: str = Field(..., description="ISO-8601 timestamp of the probe")
    epoch: int = Field(..., description="Epoch timestamp of the probe")
    federation: List[OrganProbeResult] = Field(default_factory=list, description="Probed status of all organs")
    verdict: Literal["PROCEED", "HOLD", "VOID"] = Field("HOLD", description="Substrate level operational verdict")
    receipt_hash: str = Field(..., description="Hash of the audit receipt of this probe")


class FederationProbeOutput(BaseModel):
    status: str = "OK"
    tool: str = "arif_federation_probe"
    result: FederationProbeResult
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_S: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    reasons: List[str] = Field(default_factory=list)
    model_config = {"extra": "forbid"}

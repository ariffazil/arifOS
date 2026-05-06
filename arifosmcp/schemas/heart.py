"""Heart output schema — 666_HEART (arif_heart_critique)"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class RiskFinding(BaseModel):
    type: str
    severity: Literal["none", "low", "medium", "high", "critical"] = "none"
    floor_cited: str = ""
    reason: str = ""
    mitigation: str = ""


class MaruahScore(BaseModel):
    score: float = 1.0
    omega_load: float = 0.0
    status: Literal["DIGNIFIED", "STRESSED", "BREACH"] = "DIGNIFIED"


class HeartResult(BaseModel):
    status: str = "OK"
    risks_found: list[RiskFinding] = Field(default_factory=list)
    risk_tier: Literal["GREEN", "AMBER", "RED", "CRITICAL"] = "GREEN"
    human_decision_required: bool = False
    empathy_score: float = 1.0
    weakest_stakeholder: str = "general_public"
    human_impact_load: float = 0.0
    dignity_score: float = 1.0
    verdict: Literal["SEAL", "HOLD", "VOID"] = "SEAL"
    attacks: list[str] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)
    worst_case: Literal["SEAL", "HOLD", "VOID"] = "SEAL"
    outcomes: list[str] = Field(default_factory=list)
    sentiment: str = "neutral"
    care_note: str = ""
    strategy: str = ""
    condensed: bool = False
    maruah: MaruahScore = Field(default_factory=MaruahScore)
    # LLM metadata
    _llm_tier: str | None = None
    timestamp_iso: str | None = None
    target: str | None = None


class HeartOutput(BaseModel):
    status: str = "OK"
    tool: str = "arif_heart_critique"
    result: HeartResult = Field(default_factory=HeartResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_S: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    output_policy: str = "DOMAIN_SEAL"
    reasons: list[str] = Field(default_factory=list)
    model_config = {"extra": "allow"}

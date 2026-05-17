"""Heart output schema — 666_HEART (arif_heart_critique)"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# Fix #9: Structured critique request to prevent safety filter friction
class CritiqueRequest(BaseModel):
    """
    Structured request for arif_heart_critique.

    Instead of free-text target which may trigger safety filters,
    use structured fields. The agent will use this when calling
    arif_heart_critique with mode='summary' or structured output.

    Either `claim` OR `structured_request` should be provided, not both.
    """

    claim: str | None = Field(
        default=None,
        description="The claim or statement to critique (may trigger safety filters)",
    )
    risk_categories: list[str] | None = Field(
        default=None,
        description="Risk: overclaim, bias, harm, irreversibility, deception, autonomy, dignity",
    )
    requested_output: Literal[
        "risk_scorecard", "full_report", "summary", "maruah", "deescalate"
    ] = Field(default="risk_scorecard", description="What output format is requested")
    # Structured alternatives to free-text claim
    action_description: str | None = Field(
        default=None,
        description="Description of the action being taken (structured alternative to claim)",
    )
    actors: list[str] | None = Field(
        default=None,
        description="Who is affected (e.g., ['human', 'AI', 'institution'])",
    )
    impact_domain: str | None = Field(
        default=None,
        description="Domain of impact: privacy, bias, harm, financial, political, environmental",
    )
    reversibility: bool | None = Field(
        default=None,
        description="Whether the action is reversible",
    )


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
    llm_tier: str | None = None
    timestamp_iso: str | None = None
    target: str | None = None
    # Fix #9: Structured critique request preservation
    critique_request: CritiqueRequest | None = Field(
        default=None,
        description="Structured request that was used for this critique (preserved for audit)",
    )


class HeartOutput(BaseModel):
    status: str = "OK"
    tool: str = "arif_heart_critique"
    result: HeartResult = Field(default_factory=HeartResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_s: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    output_policy: str = "DOMAIN_SEAL"
    reasons: list[str] = Field(default_factory=list)
    model_config = {"extra": "allow"}

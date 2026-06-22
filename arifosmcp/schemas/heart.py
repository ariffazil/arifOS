"""Heart output schema — 666_HEART (arif_critique)"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# Fix #9: Structured critique request to prevent safety filter friction
class CritiqueRequest(BaseModel):
    """
    Structured request for arif_critique.

    Instead of free-text target which may trigger safety filters,
    use structured fields. The agent will use this when calling
    arif_critique with mode='summary' or structured output.

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
    # TWO SEPARATE VERDICTS (FIX: previously conflated into one `verdict` field)
    #
    # execution_verdict = did the critique operation itself run without error?
    #   SEAL = critique executed cleanly
    #   HOLD = critique ran but had issues (timeout, partial)
    #   VOID = critique could not run (injection detected, module unavailable)
    #
    # action_risk_verdict = is the TARGET ACTION safe to proceed with?
    #   SEAL = action is low-risk, proceed
    #   HOLD = action needs human review before proceeding
    #   VOID = action is unsafe, do not proceed
    #
    # The TOP-LEVEL `output_policy` is derived from action_risk_verdict + risk_tier.
    # Agents MUST read action_risk_verdict, NOT execution_verdict, to determine
    # whether the critiqued action is approved.
    execution_verdict: Literal["SEAL", "HOLD", "VOID"] = "SEAL"
    action_risk_verdict: Literal["SEAL", "HOLD", "VOID"] = "SEAL"
    # Legacy alias — removed to force callers to use the split fields above.
    # old `verdict` field was ambiguous: does it mean execution or approval?
    # DEPRECATED: remove after all callers updated
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
    tool: str = "arif_critique"
    result: HeartResult = Field(default_factory=HeartResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_s: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    reasons: list[str] = Field(default_factory=list)
    model_config = {"extra": "allow"}

    @property
    def output_policy(self) -> str:
        """
        Computed from action_risk_verdict + risk_tier.

        output_policy tells the agent WHAT TO DO with the critique result.
        This is ALWAYS derived from the action's risk, never from execution status.

        DO NOT read `status` to determine action approval.
        DO NOT read `execution_verdict` to determine action approval.
        ALWAYS read `result.action_risk_verdict` + `result.risk_tier`.
        """
        if (
            self.result.risk_tier in ("RED", "CRITICAL")
            or self.result.action_risk_verdict == "VOID"
        ):
            return "DOMAIN_VOID"
        if self.result.human_decision_required or self.result.action_risk_verdict == "HOLD":
            return "DOMAIN_HOLD"
        return "DOMAIN_SEAL"

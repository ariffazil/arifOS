"""
Pydantic v2 schemas for the minda substrate.

These are the input/output contracts. They are advisory-only — never
executed, never used as authority. They flow into arif_judge
as one of several inputs.
"""

from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


class ThinkRequest(BaseModel):
    """Input to MindaService.think().

    Attributes:
        intent:        what the user/agent wants to do (free text)
        context:       snapshot of relevant state (e.g., tool registry, env)
        observations:  new evidence to fold into belief (F2: with provenance)
        prior_belief:  optional prior BeliefState as dict (for chaining)
        horizon:       rollout horizon in steps (default 3)
    """
    intent: str = Field(..., description="What the user/agent wants to do")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of relevant state (tool registry, env, etc.)",
    )
    observations: dict[str, Any] = Field(
        default_factory=dict,
        description="New evidence to fold into belief",
    )
    prior_belief: Optional[dict[str, Any]] = Field(
        None,
        description="Optional prior BeliefState as dict (for belief chaining)",
    )
    horizon: int = Field(3, description="Rollout horizon in steps", ge=1, le=20)


class ScoredPlan(BaseModel):
    """One scored plan in the ranked output.

    Attributes:
        plan_id:    identifier (e.g., "observe_more", "reason_then_search", "forge_now")
        score:      expected utility (lower = worse; -1e9 = rejected)
        actions:    list of action names (e.g., ["arif_observe"])
        outcome:    full outcome dict from RolloutEngine
        hold_888:   True if this plan needs human ack (F1/F13)
        reason:     human-readable reason for the hold
    """
    plan_id: str
    score: float
    actions: list[str]
    outcome: dict[str, float]
    hold_888: bool = False
    reason: Optional[str] = None


class ThinkResponse(BaseModel):
    """Output of MindaService.think().

    Attributes:
        best_plan_id:           ID of the highest-scoring plan
        best_actions:           action names from the best plan
        score:                  score of the best plan
        confidence_band:        (low, high) — F2 TRUTH: explicit band, not point estimate
        risk_envelope:          full outcome dict of the best plan
        hold_888:               True if the best plan needs human ack
        hold_reason:            why
        ranked:                 all plans sorted by score (best first)
        posterior_uncertainty:  aggregate uncertainty after belief update
        provenance:             OBS/DER/INT/SPEC per observation key (F2)
    """
    best_plan_id: str
    best_actions: list[str]
    score: float
    confidence_band: tuple[float, float]
    risk_envelope: dict[str, float]
    hold_888: bool
    hold_reason: Optional[str] = None
    ranked: list[ScoredPlan]
    posterior_uncertainty: float
    provenance: dict[str, str] = Field(
        default_factory=dict,
        description="F2: provenance per observation key (OBS/DER/INT/SPEC)",
    )

"""
arifosmcp/schemas/model_card.py — Model Governance Card Schema
═════════════════════════════════════════════════════════════

Formal Pydantic schema for the model_governance_card produced by
build_governance_card() in runtime/registry.py.

F3 TRI_WITNESS: Identity binding for constitutional governance.
When identity_verified=False the card is in degraded/declared-only mode.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModelAnchor(BaseModel):
    """Identity binding for the model — who it claims to be and whether verified."""

    declared_model_key: str
    verified_model_key: str | None = None  # None = identity unverified
    provider_key: str | None = None
    family_key: str | None = None
    soul_key: str | None = None
    soul_label: str | None = None
    identity_verified: bool = False


class RuntimeTruth(BaseModel):
    """Deployment capabilities and runtime truth for the model."""

    deployment_id: str
    web_on: bool = False
    memory_mode: str = "session_only"
    provider_capabilities: list[str] = Field(default_factory=list)
    tools_live: list[str] = Field(default_factory=list)
    arifos_public_tools: list[str] = Field(default_factory=list)
    verified_arifos_tools: list[str] = Field(default_factory=list)
    execution_mode: str = "dry_run"
    side_effects_allowed: bool = False


class SelfClaimBoundary(BaseModel):
    """Limits on what the model may claim about itself."""

    identity: str = "provider_family_only_unless_verified"
    tools: str = "verified_only"
    knowledge: str = "mark_verified_vs_inferred"
    actions: str = "mark_executed_vs_suggested"


class ShadowProfile(BaseModel):
    """Soul-derived risk profile — embedded from provider_soul registry."""

    # Normal (full) shape
    angel: str | None = None
    shadow: str | None = None
    paradox: str | None = None
    control_laws: list[str] = Field(default_factory=list)
    tripwires: list[str] = Field(default_factory=list)
    # Degraded/fallback shape
    status: str | None = None
    error: str | None = None


class RiskLeash(BaseModel):
    """Governance constraints from model spec + registry."""

    primary_control: str | None = None
    risk_tier: str = "degraded"
    allowed_organs: list[str] = Field(default_factory=list)
    forbidden_organs: list[str] = Field(default_factory=list)
    max_action_class: str = "analyze"
    apex_score: float | None = None
    amanah_score: float | None = None
    required_behaviors: list[str] = Field(default_factory=list)
    forbidden_behaviors: list[str] = Field(default_factory=list)
    # Degraded/fallback shape
    status: str | None = None


class ModelGovernanceCard(BaseModel):
    """
    Complete model governance card — identity binding + capability truth.

    Produced by build_governance_card() in runtime/registry.py.
    Stored in session as sess["model_governance_card"].

    F3 TRI_WITNESS: identity_verified=False means the model is operating
    in declared-only/degraded mode. Full constitutional governance requires
    a verified identity binding.

    Canonical path: arif_init → _new_session → build_governance_card
    """

    session_id: str
    model_anchor: ModelAnchor
    runtime_truth: RuntimeTruth
    self_claim_boundary: SelfClaimBoundary
    shadow_profile: ShadowProfile | None = None
    risk_leash: RiskLeash | None = None

    # Derived convenience fields
    is_bound: bool = Field(
        default=False,
        description="True when identity_verified=True and soul_key is set",
    )
    is_degraded: bool = Field(
        default=False,
        description="True when runtime or registry data was unavailable",
    )

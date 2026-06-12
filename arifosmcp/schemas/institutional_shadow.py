"""
arifosmcp/schemas/institutional_shadow.py
═══════════════════════════════════════════════════════════════════
Cross-node contract for Institutional Shadow Drift.

GENESIS/006 (Petronas Paradox) states:
> When the function of a sovereign institution expands beyond its name,
> the name becomes an epistemic burden.

This schema is the runtime contract that lets arifOS detect the drift,
WEALTH score the capital risk, GEOX verify the physical substrate, and
AAA display the state.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ObservedFunction(BaseModel):
    """One observed function of an institution."""

    domain: str = Field(
        ...,
        description="Functional domain, e.g. energy, compute, capital, diplomacy, geology.",
    )
    evidence_source: str = Field(
        ...,
        description="Where the observation came from: annual_report, sensor, contract, audit, etc.",
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence that the institution actually performs this function."
    )
    capital_exposure_myr: float = Field(
        default=0.0, ge=0.0, description="MYR capital exposure tied to this function."
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class InstitutionalShadowDrift(BaseModel):
    """
    Runtime snapshot of whether a sovereign institution has outgrown its name.

    This is the cross-node contract. arifOS computes it. WEALTH consumes the
    drift_score and sovereignty_score. GEOX attaches subsurface/physical reality.
    """

    institution_name: str = Field(..., description="Legal or common name of the institution.")
    declared_function: str = Field(..., description="Function encoded in the name / charter.")
    declared_function_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords that the declared function should cover.",
    )
    observed_functions: list[ObservedFunction] = Field(
        default_factory=list,
        description="Functions the institution actually performs now.",
    )
    last_shadow_update: datetime | None = Field(
        default=None,
        description="When the institution's mandate/name was last consciously updated.",
    )
    total_capital_exposure_myr: float = Field(
        default=0.0, ge=0.0, description="Total MYR exposure across observed functions."
    )

    # Scores computed by arifOS
    drift_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="0.0 = name matches function; 1.0 = function has completely escaped the name.",
    )
    sovereignty_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="0.0 = foreign/substrate-captured; 1.0 = fully sovereign control.",
    )
    risk_class: str = Field(
        default="LOW",
        pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$",
        description="Blast-radius class derived from drift × capital exposure.",
    )
    verdict: str = Field(
        default="SEAL",
        pattern="^(SEAL|HOLD|VOID)$",
        description=" Constitutional routing verdict.",
    )
    hold_reasons: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("total_capital_exposure_myr", mode="before")
    @classmethod
    def _sum_exposure(cls, v: Any, info: Any) -> float:
        if v:
            return float(v)
        observed = info.data.get("observed_functions") or []
        return float(sum(getattr(o, "capital_exposure_myr", 0) for o in observed))


class ShadowDriftRequest(BaseModel):
    """Request to compute institutional shadow drift."""

    institution_name: str
    declared_function: str
    declared_function_keywords: list[str] = Field(default_factory=list)
    observed_functions: list[ObservedFunction]
    last_shadow_update: str | None = None  # ISO date string
    capital_exposure_myr: float | None = None


class ShadowDriftResponse(BaseModel):
    """Response after drift computation."""

    drift: InstitutionalShadowDrift
    next_safe_action: str
    federation_routing: dict[str, str]

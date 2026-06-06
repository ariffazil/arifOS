"""
Jurisdiction Schemas — Agents Inside Authority
═══════════════════════════════════════════════════════════════════════════════

Autonomy bands, capability grants, and jurisdiction envelopes.
Every MCP call enters through jurisdiction before it touches tools.

Ratified: 2026-06-03
Authority: L13 SOVEREIGN

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# AUTONOMY BANDS
# ═══════════════════════════════════════════════════════════════════════════════


class AutonomyBand(StrEnum):
    """
    Governed autonomy gradient.

    Green/Yellow: fast lane — agent decides
    Orange:       gated — receipt + rollback required
    Red:          HOLD — judge or sovereign approval
    Black:        VOID — default denial
    """

    GREEN = "green"    # Read, inspect, draft, classify
    YELLOW = "yellow"  # Prepare, diff, stage plan
    ORANGE = "orange"  # Local reversible write, config with backup
    RED = "red"        # Secrets, money, public external, infra, deletion
    BLACK = "black"    # Irreversible destructive — default VOID


class RiskClass(StrEnum):
    """Risk classification for a tool invocation."""

    OBSERVE = "observe"
    PREPARE = "prepare"
    MUTATE = "mutate"
    ATOMIC = "atomic"
    IRREVERSIBLE = "irreversible"


# ═══════════════════════════════════════════════════════════════════════════════
# CAPABILITY GRANT
# ═══════════════════════════════════════════════════════════════════════════════


class CapabilityGrant(BaseModel):
    """
    A scoped permission for an actor to use a tool under constraints.

    Agents never hold raw secrets. They hold capability grants.
    The gateway resolves secrets; the agent resolves intent.
    """

    grant_id: str = Field(description="Unique grant identifier")
    actor_id: str = Field(description="Agent or organ holding this grant")
    tool_name: str = Field(description="Canonical MCP tool name")
    band: AutonomyBand = Field(description="Maximum autonomy band for this grant")
    risk_ceiling: RiskClass = Field(default=RiskClass.OBSERVE)
    issued_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    expires_at: str | None = Field(default=None, description="ISO timestamp or None for perpetual")
    issuer: str = Field(default="L13_SOVEREIGN", description="Who issued this grant")
    conditions: list[str] = Field(default_factory=list, description="E.g. 'requires_rollback_plan'")
    revoked: bool = Field(default=False)
    revocation_reason: str | None = None

    def is_active(self) -> bool:
        if self.revoked:
            return False
        if self.expires_at is None:
            return True
        return datetime.now(UTC) < datetime.fromisoformat(self.expires_at)


# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICTION ENVELOPE
# ═══════════════════════════════════════════════════════════════════════════════


class JurisdictionEnvelope(BaseModel):
    """
    Wraps every MCP call with identity, authority, and risk context.

    This envelope is the border checkpoint.
    No tool executes without a stamped envelope.
    """

    session_id: str | None = None
    actor_id: str = Field(description="Who is acting")
    tool_name: str = Field(description="What tool is requested")
    params: dict[str, Any] = Field(default_factory=dict)
    grant_id: str | None = Field(default=None, description="Capability grant if pre-authorized")
    claimed_band: AutonomyBand = Field(default=AutonomyBand.GREEN)
    risk_class: RiskClass = Field(default=RiskClass.OBSERVE)
    rollback_plan: str | None = Field(default=None, description="Required for ORANGE+")
    observe_receipt_id: str | None = Field(
        default=None,
        description="Receipt proving prior observation (required for MUTATE+)")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# BAND ROUTING RESULT
# ═══════════════════════════════════════════════════════════════════════════════


class BandRoutingResult(BaseModel):
    """Output of the autonomy band router."""

    tool_name: str
    actor_id: str
    assigned_band: AutonomyBand
    risk_class: RiskClass
    reason: str
    requires_grant: bool
    requires_rollback: bool
    requires_observe_receipt: bool
    fast_lane: bool = Field(description="GREEN/YELLOW = no external witness needed")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

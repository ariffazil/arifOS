"""
CapabilitySurface — The Single Honest Map of What the System Can Actually Do
═══════════════════════════════════════════════════════════════════════════════

The primary resource in a constitutional AGI system is not tokens or time —
it is *honestly known capability*. Any plan or execution chain must be
constrained by what the system can honestly say it can do right now.

This schema defines the canonical `CapabilitySurface` — a single struct
that AAA displays, arifOS computes, and A-FORGE plans within.

EUREKA: CapabilitySurface → Status Alignment → Bounded Autonomy
  - A tool that claims SEAL but returns HOLD internally is OVERCLAIM.
  - A tool that is unreachable (dead transport/auth) is DARK.
  - A plan that uses DARK or OVERCLAIM tools without gating is VOID.

F1-F13 binding:
  F2 TRUTH:     status_alignment must reflect actual probe results
  F4 CLARITY:   surface reduces entropy by being a single source of truth
  F11 AUTH:     capability claims must be attributable to a probe timestamp
  F13 SOVEREIGN: tier boundaries set by Arif, not by the system itself

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class StatusAlignment(StrEnum):
    """Does the tool's claimed status match its actual behavior?"""

    ALIGNED = "ALIGNED"  # outer verdict matches inner truth + live probe
    OVERCLAIM = "OVERCLAIM"  # says SEAL/OK but inner is HOLD/FAIL or probe fails
    UNDERCLAIM = "UNDERCLAIM"  # says HOLD/DEGRADED but actually works
    DARK = "DARK"  # unreachable — transport/auth broken, no probe possible
    UNKNOWN = "UNKNOWN"  # not yet probed or insufficient data


class CapabilityTier(StrEnum):
    """How much autonomy this tool/agent is trusted with."""

    T1_OBSERVE = "T1_OBSERVE"  # read-only, no side effects, always safe
    T2_REASON = "T2_REASON"  # computation, planning, no mutation
    T3_SIMULATE = "T3_SIMULATE"  # dry-run / preview, reversible
    T4_MUTATE = "T4_MUTATE"  # writes state, needs 888_HOLD
    T5_ATOMIC = "T5_ATOMIC"  # irreversible, F13 gate mandatory


class AutonomyMode(StrEnum):
    """What execution mode is safe given the current CapabilitySurface?"""

    AGI_CHAIN = "AGI_CHAIN"  # multi-step autonomous execution
    SHORT_CHAIN = "SHORT_CHAIN"  # limited steps, periodic HOLD
    ASSIST = "ASSIST"  # human at every step
    BLOCKED = "BLOCKED"  # execution not safe under any mode


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════


class ToolCapability(BaseModel):
    """What one tool can honestly do right now."""

    name: str = Field(description="Canonical tool name (e.g. arif_measure)")
    organ: str = Field(description="Owning organ (arifOS, WEALTH, WELL, GEOX, A-FORGE)")
    available: bool = Field(description="Is the tool reachable? (transport/auth)")
    read_ok: bool = Field(description="Read operations working?")
    write_ok: bool = Field(description="Write operations working? (false if over-gated)")
    tier: CapabilityTier = Field(description="Maximum capability tier")
    floors: list[str] = Field(default_factory=list, description="Active constitutional floors")
    status_alignment: StatusAlignment = Field(description="Does claimed match actual?")
    last_error: str | None = Field(default=None, description="Last error message if any")
    last_probed_at: str | None = Field(default=None, description="ISO timestamp of last probe")
    inner_verdict: str | None = Field(default=None, description="Inner verdict from last call")
    outer_verdict: str | None = Field(default=None, description="Outer verdict from last call")


class AgentCapability(BaseModel):
    """What one agent/model can honestly do."""

    name: str = Field(description="Agent name (e.g. Omega, Hermes, Claude)")
    model: str = Field(description="Backing model (e.g. deepseek-v4-pro)")
    tier: CapabilityTier = Field(description="Maximum trusted capability tier")
    allowed_floors: list[str] = Field(
        default_factory=list, description="Floors this agent can operate within"
    )
    domains: list[str] = Field(
        default_factory=list, description="Domains this agent is authorized for"
    )
    status_alignment: StatusAlignment = Field(description="Is agent honest about its capability?")


class OrganHealth(BaseModel):
    """Live health of one federation organ."""

    name: str = Field(description="Organ name")
    port: int = Field(description="Port number")
    systemd_active: bool = Field(description="Is systemd service active?")
    health_200: bool = Field(description="Does /health return 200?")
    tools_registered: int = Field(default=0, description="Number of registered tools")
    tools_callable: int = Field(default=0, description="Number of actually callable tools")


class CapabilitySurface(BaseModel):
    """The single canonical map of what the system can honestly do right now.

    Compute this once at planning time. A-FORGE must not plan beyond it.
    AAA must display it. arifOS must enforce it.
    """

    timestamp: str = Field(description="ISO timestamp when surface was computed")
    version: str = Field(default="1.0.0", description="Schema version")
    compute_latency_ms: float = Field(default=0.0, description="How long it took to compute")

    # Live organ health
    organs: list[OrganHealth] = Field(default_factory=list, description="Federation organ health")

    # Tool-level honesty
    tools: list[ToolCapability] = Field(default_factory=list, description="Per-tool capability")

    # Agent-level honesty
    agents: list[AgentCapability] = Field(default_factory=list, description="Per-agent capability")

    # Derived
    autonomy_mode: AutonomyMode = Field(description="Safe execution mode given surface")
    dark_tools: int = Field(default=0, description="Count of DARK (unreachable) tools")
    overclaim_tools: int = Field(default=0, description="Count of OVERCLAIM tools")
    aligned_tools: int = Field(default=0, description="Count of ALIGNED tools")
    total_tools: int = Field(default=0, description="Total tools in surface")

    # Evidence
    evidence_refs: list[str] = Field(
        default_factory=list, description="Probe receipts backing this surface"
    )

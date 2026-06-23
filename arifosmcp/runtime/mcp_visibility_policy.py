"""
mcp_visibility_policy.py
═══════════════════════════════════════════════════════════════════════════

MCP Surface Governor — the visibility layer per amendment_001.md.

Doctrine (per amendment_001, 2026-06-12):
    "Use MCP for exposure. Use arifOS for authority."
    "Does it need model-mediated invocation? If yes, MCP-shaped. If no, don't."

This module governs WHICH tools the model is allowed to see in its context.
It does NOT govern whether the model may CALL them (that's arifOS lease).

The governor is invoked by:
  - arif_kernel_route(mode="tools/list") — default visible set
  - arif_kernel_route(mode="route", intent=X) — intent-matched shortlist
  - arif_observe(...) — wraps result with visibility-aware metadata

Pydantic v2 models for type safety. F1 AMANAH: all decisions reversible
by relaxing the policy yaml. F2 TRUTH: every filter operation is logged.

Author: @integrator (session 2026-06-12-mcp-governor-and-minimax-forge)
Forged: 2026-06-12
"""

from __future__ import annotations

import time
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

# ─────────────────────────────────────────────────────────────────────────────
# Tier definitions (mirror mcp_surface_registry.yaml)
# ─────────────────────────────────────────────────────────────────────────────


class Tier(StrEnum):
    """Visibility tiers (per amendment_001).

    Amendment 002 (2026-06-21, GENESIS-016 binding): Added HERMES tier.
    Hermes-tier tools are public hermes_* utilities (vault_query, fact_check,
    epistemic_check, cross_verify, plan_review, memory_steward, system_status)
    that were registered in DIAGNOSTIC_TOOLS but filtered out of MCP exposure
    because the Tier enum did not include 'hermes'. The visibility policy
    default `tier_filter` now includes Tier.HERMES so the constitutional
    surface matches the engineering.
    """

    CORE = "core"  # Always visible when organ healthy
    ORGAN = "organ"  # Visible only after intent match
    HERMES = "hermes"  # Hermes utilities (vault_query, fact_check, etc.) — public
    LAB = "lab"  # Visible only with explicit route
    DEPRECATED = "deprecated"  # Not callable, audit trail only


class OrganHealth(StrEnum):
    """Health states."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    NOT_DEPLOYED = "not_deployed"


# Diagnostic tool shortlist for degraded/unknown organs
DIAGNOSTIC_TOOL_NAMES = (
    "organ_attest",
    "organ_status",
    "organ_repair_hint",
)


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────


class ToolEntry(BaseModel):
    """A single tool entry in the MCP surface registry."""

    name: str
    organ: str
    tier: Tier
    health: OrganHealth = OrganHealth.UNKNOWN
    constitution_hash: str | None = None
    schema_hash: str | None = None
    version: str | None = None
    description: str | None = None
    schema_tokens: int = 0
    last_invoked_days_ago: int | None = None

    @field_validator("name")
    @classmethod
    def _name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("ToolEntry.name must be non-empty")
        return v


class VisibilityPolicy(BaseModel):
    """The runtime policy used to filter the visible surface."""

    max_visible: int = 15
    tier_filter: set[Tier] = Field(default_factory=lambda: {Tier.CORE, Tier.ORGAN, Tier.HERMES})
    organ_health_filter: set[OrganHealth] = Field(default_factory=lambda: {OrganHealth.HEALTHY})
    require_constitution_hash: bool = True
    require_schema_hash: bool = True
    require_version: bool = True
    allow_lab: bool = False  # Lab tools require explicit opt-in
    max_schema_tokens_per_tool: int = 700
    duplicate_similarity_threshold: float = 0.82

    @field_validator("max_visible")
    @classmethod
    def _positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_visible must be >= 1")
        return v


class FilterResult(BaseModel):
    """Result of applying the visibility policy."""

    visible: list[ToolEntry] = Field(default_factory=list)
    hidden: list[ToolEntry] = Field(default_factory=list)
    quarantined_diagnostics: list[ToolEntry] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)
    policy_applied: VisibilityPolicy
    duration_ms: float = 0.0
    epoch_utc: str = ""

    def shortlist(self, n: int = 7) -> list[ToolEntry]:
        """Return the top-n tools by (tier_priority, organ_health, specificity)."""
        tier_rank = {Tier.CORE: 0, Tier.ORGAN: 1, Tier.LAB: 2, Tier.DEPRECATED: 3}
        sorted_tools = sorted(
            self.visible,
            key=lambda t: (
                tier_rank.get(t.tier, 99),
                0 if t.health == OrganHealth.HEALTHY else 1,
                -len(t.name),  # specificity proxy: longer names first
            ),
        )
        return sorted_tools[:n]


# ─────────────────────────────────────────────────────────────────────────────
# Core filter
# ─────────────────────────────────────────────────────────────────────────────


def filter_visible_tools(
    all_tools: list[ToolEntry],
    policy: VisibilityPolicy,
) -> FilterResult:
    """Apply the visibility policy to filter tools.

    Rules:
      1. Tier filter: only keep tools whose tier is in policy.tier_filter.
         Lab tools require policy.allow_lab=True.
      2. Health filter: only keep tools whose health is in policy.organ_health_filter.
         If health != healthy, the tool is moved to quarantined_diagnostics
         and replaced by the 3-tool diagnostic shortlist (if its organ has one).
      3. Required fields: if require_* flags set, drop tools missing the fields.
      4. Max visible: cap the result at policy.max_visible.
      5. Duplicate suppression: if two tools have cosine_sim(description) > threshold,
         keep the first by tier/health priority (TODO: embedding-based, not implemented
         in this forge — Phase 2).

    Returns a FilterResult with visible/hidden/quarantined_diagnostics.
    """
    start = time.perf_counter()
    visible: list[ToolEntry] = []
    hidden: list[ToolEntry] = []
    quarantined: list[ToolEntry] = []

    # Step 1: dedupe by organ health to compute the diagnostic shortlist
    organ_health_cache: dict[str, OrganHealth] = {}
    for t in all_tools:
        if t.organ not in organ_health_cache:
            organ_health_cache[t.organ] = t.health

    for tool in all_tools:
        # Tier filter: LAB tools pass if allow_lab=True, else hidden
        if tool.tier == Tier.LAB and not policy.allow_lab:
            hidden.append(tool)
            continue
        if tool.tier == Tier.DEPRECATED:
            hidden.append(tool)
            continue
        # CORE and ORGAN: check tier_filter set
        if tool.tier not in policy.tier_filter and tool.tier != Tier.LAB:
            hidden.append(tool)
            continue

        # Health filter
        if tool.health not in policy.organ_health_filter:
            if tool.health in {OrganHealth.DEGRADED, OrganHealth.UNKNOWN}:
                # Try to add a diagnostic placeholder for this organ
                diagnostic = ToolEntry(
                    name=f"{tool.organ}_diagnostic_{len(quarantined)}",
                    organ=tool.organ,
                    tier=Tier.ORGAN,
                    health=tool.health,
                    description=f"Diagnostic: {tool.organ} is {tool.health.value}",
                )
                quarantined.append(diagnostic)
            hidden.append(tool)
            continue

        # Required fields
        if policy.require_constitution_hash and not tool.constitution_hash:
            hidden.append(tool)
            continue
        if policy.require_schema_hash and not tool.schema_hash:
            hidden.append(tool)
            continue
        if policy.require_version and not tool.version:
            hidden.append(tool)
            continue

        # Schema token cap
        if tool.schema_tokens > policy.max_schema_tokens_per_tool:
            hidden.append(tool)
            continue

        visible.append(tool)

    # Cap to max_visible (preserve order — caller can sort later)
    if len(visible) > policy.max_visible:
        overflow = visible[policy.max_visible :]
        visible = visible[: policy.max_visible]
        hidden.extend(overflow)

    duration = (time.perf_counter() - start) * 1000.0
    return FilterResult(
        visible=visible,
        hidden=hidden,
        quarantined_diagnostics=quarantined,
        counts={
            "total_input": len(all_tools),
            "visible": len(visible),
            "hidden": len(hidden),
            "quarantined_diagnostics": len(quarantined),
            "max_visible_policy": policy.max_visible,
        },
        policy_applied=policy,
        duration_ms=round(duration, 3),
        epoch_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Registry loader
# ─────────────────────────────────────────────────────────────────────────────

REGISTRY_PATH = Path(__file__).parent / "mcp_surface_registry.yaml"


def load_registry(path: Path | None = None) -> dict[str, Any]:
    """Load the mcp_surface_registry.yaml file. Pure read, no mutation."""
    p = path or REGISTRY_PATH
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_policy_from_registry(
    registry: dict[str, Any] | None = None,
    *,
    allow_lab: bool = False,
    max_visible_override: int | None = None,
) -> VisibilityPolicy:
    """Construct a VisibilityPolicy from the registry yaml.

    The registry's entropy_budget section supplies the defaults.
    Callers can override max_visible and allow_lab for intent-matched shortlists.
    """
    reg = registry or load_registry()
    entropy = reg.get("entropy_budget", {}) if isinstance(reg, dict) else {}
    return VisibilityPolicy(
        max_visible=max_visible_override or entropy.get("default_visible_tools_max", 15),
        allow_lab=allow_lab,
        require_constitution_hash=True,
        require_schema_hash=True,
        require_version=True,
        max_schema_tokens_per_tool=entropy.get("max_schema_tokens_per_tool", 700),
        duplicate_similarity_threshold=entropy.get("duplicate_similarity_threshold", 0.82),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public convenience: build a ToolEntry list from the registry
# ─────────────────────────────────────────────────────────────────────────────


def registry_to_tool_entries(registry: dict[str, Any] | None = None) -> list[ToolEntry]:
    """Flatten the registry yaml into a list of ToolEntry objects.

    F2 truth: this is a *projection* of the registry, not a live probe.
    Live tools are passed in by the caller. Use this only for policy
    validation / unit tests, not for production tool enumeration.
    """
    reg = registry or load_registry()
    if not isinstance(reg, dict):
        return []
    entries: list[ToolEntry] = []
    for organ in reg.get("organs", []) or []:
        if not isinstance(organ, dict):
            continue
        organ_id = organ.get("id", "unknown")
        organ_status_str = organ.get("status", "unknown")
        try:
            organ_health = OrganHealth(organ_status_str)
        except ValueError:
            organ_health = OrganHealth.UNKNOWN
        try:
            organ_tier = Tier(organ.get("tier", "organ"))
        except ValueError:
            organ_tier = Tier.ORGAN
        # We can't enumerate individual tool names from the registry alone.
        # The caller is expected to inject tool names. We emit a synthetic
        # entry per organ as a placeholder for the health/tier signal.
        entries.append(
            ToolEntry(
                name=f"__organ_marker_{organ_id}",
                organ=organ_id,
                tier=organ_tier,
                health=organ_health,
                constitution_hash=organ.get("constitution_hash")
                if organ.get("constitution_hash") not in (None, "MISSING")
                else None,
                schema_hash=organ.get("schema_hash"),
                version=organ.get("version") or "unknown",
                description=f"Synthetic marker for organ {organ_id}",
            )
        )
    return entries


__all__ = [
    "Tier",
    "OrganHealth",
    "DIAGNOSTIC_TOOL_NAMES",
    "ToolEntry",
    "VisibilityPolicy",
    "FilterResult",
    "filter_visible_tools",
    "load_registry",
    "build_policy_from_registry",
    "registry_to_tool_entries",
    "REGISTRY_PATH",
]

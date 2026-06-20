"""
Capability-Aware Router — The Truth Enforcer
═══════════════════════════════════════════════

EUREKA Ω-2026-06-10: CapabilitySurface made the system honest.
This module makes it *sovereign*.

Truth without enforcement is confession, not governance.
This router consumes CapabilitySurface and hard-enforces:

  1. DEAD tools       → REJECT (tool unreachable)
  2. OVERCLAIM tools   → DOWNGRADE (downgrade to ASSIST + 888_HOLD)
  3. UNDERCLAIM tools  → READ_ONLY (can respond, cannot execute)
  4. TIER_C            → ASSIST_ONLY (no autonomous execution)
  5. EXPIRED surface   → REJECT (surface cache expired)
  6. UNKNOWN tools     → REJECT (not yet probed, cannot trust)

Invariant: No arifOS component may route or execute an action
           unless it holds a current CapabilitySurface.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════════


class RouteVerdict(StrEnum):
    """What the router says about a planned action."""

    ALLOW = "ALLOW"  # Proceed — within capability and lease
    DOWNGRADE = "DOWNGRADE"  # Proceed but downgrade autonomy mode
    READ_ONLY = "READ_ONLY"  # Observe/reason only, no mutation
    HOLD = "HOLD"  # Requires 888_HOLD before proceeding
    REJECT = "REJECT"  # Cannot proceed — capability gap
    EXPIRED = "EXPIRED"  # Surface cache expired, must refresh


# ═══════════════════════════════════════════════════════════════════════════════
# Route Decision
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class RouteDecision:
    """The output of a capability-aware routing check."""

    verdict: RouteVerdict
    tool_name: str
    reason: str
    capability_tier: str = "UNKNOWN"
    status_alignment: str = "UNKNOWN"
    allowed: bool = False
    downgraded_to: str | None = None  # e.g. "ASSIST" if downgraded
    requires_888_hold: bool = False
    evidence_refs: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# Capability-Aware Router
# ═══════════════════════════════════════════════════════════════════════════════


def route_with_capability(
    tool_name: str,
    capability_surface: dict[str, Any],
    *,
    intended_action: str = "observe",
    cache_max_age_s: float = 30.0,
    override_unknown: bool = False,
) -> RouteDecision:
    """
    Route a tool action through the CapabilitySurface enforcement mesh.

    Args:
        tool_name: Canonical tool name (e.g. 'arif_forge_execute')
        capability_surface: Full CapabilitySurface dict (from arif_ops_measure)
        intended_action: 'observe', 'reason', 'dry_run', 'mutate', 'atomic'
        cache_max_age_s: Maximum age of surface before it's considered expired
        override_unknown: If True, UNKNOWN tools are treated as usable (F13 only)

    Returns:
        RouteDecision with verdict and reasoning
    """
    # ── 0. Check surface freshness ──────────────────────────────────────────
    surface_ts = capability_surface.get("timestamp", "")
    if surface_ts:
        try:
            surface_age = (
                datetime.now(UTC) - datetime.fromisoformat(surface_ts.replace("Z", "+00:00"))
            ).total_seconds()
            if surface_age > cache_max_age_s:
                return RouteDecision(
                    verdict=RouteVerdict.EXPIRED,
                    tool_name=tool_name,
                    reason=f"CapabilitySurface expired ({surface_age:.0f}s > {cache_max_age_s}s). Refresh required.",
                    evidence_refs=[f"surface_ts:{surface_ts}", f"surface_age:{surface_age:.0f}s"],
                )
        except (ValueError, TypeError):
            pass

    # ── 1. Find tool in surface ─────────────────────────────────────────────
    tools_list = capability_surface.get("tools", [])
    tool_info: dict[str, Any] | None = None
    for t in tools_list:
        if t.get("name") == tool_name:
            tool_info = t
            break

    if tool_info is None:
        return RouteDecision(
            verdict=RouteVerdict.REJECT,
            tool_name=tool_name,
            reason=f"Tool '{tool_name}' not found in CapabilitySurface. Unknown tool.",
            evidence_refs=[f"surface_tools_count:{len(tools_list)}"],
        )

    # ── 2. Read tool capability fields ──────────────────────────────────────
    available = tool_info.get("available", False)
    read_ok = tool_info.get("read_ok", False)
    write_ok = tool_info.get("write_ok", False)
    alignment_raw = tool_info.get("status_alignment", "UNKNOWN")
    tier_raw = tool_info.get("tier", "T2_REASON")
    last_error = tool_info.get("last_error")

    # ── 3. DEAD check ───────────────────────────────────────────────────────
    if alignment_raw == "DARK" or not available:
        return RouteDecision(
            verdict=RouteVerdict.REJECT,
            tool_name=tool_name,
            reason=f"Tool '{tool_name}' is DARK (unreachable). "
            f"{last_error or 'Transport/auth broken.'}",
            capability_tier=tier_raw,
            status_alignment="DARK",
            evidence_refs=[f"available:{available}", f"last_error:{last_error}"],
        )

    # ── 4. UNKNOWN check ────────────────────────────────────────────────────
    if alignment_raw == "UNKNOWN" and not override_unknown:
        return RouteDecision(
            verdict=RouteVerdict.REJECT,
            tool_name=tool_name,
            reason=f"Tool '{tool_name}' status is UNKNOWN — not yet probed. "
            "Cannot trust unverified capability.",
            capability_tier=tier_raw,
            status_alignment="UNKNOWN",
        )

    # ── 5. OVERCLAIM check ──────────────────────────────────────────────────
    if alignment_raw == "OVERCLAIM":
        # OVERCLAIM: tool claims SEAL but inner is HOLD/FAIL.
        # Can only observe or reason. Mutation requires 888_HOLD.
        if intended_action in ("mutate", "atomic", "dry_run"):
            return RouteDecision(
                verdict=RouteVerdict.DOWNGRADE,
                tool_name=tool_name,
                reason=f"Tool '{tool_name}' is OVERCLAIM (claims SEAL but inner truth "
                f"shows HOLD/FAIL). Downgraded to ASSIST + 888_HOLD required.",
                capability_tier=tier_raw,
                status_alignment="OVERCLAIM",
                downgraded_to="ASSIST",
                requires_888_hold=True,
            )
        return RouteDecision(
            verdict=RouteVerdict.READ_ONLY,
            tool_name=tool_name,
            reason=f"Tool '{tool_name}' is OVERCLAIM. Read-only operations only.",
            capability_tier=tier_raw,
            status_alignment="OVERCLAIM",
            allowed=(intended_action in ("observe", "reason")),
        )

    # ── 6. UNDERCLAIM check ─────────────────────────────────────────────────
    if alignment_raw == "UNDERCLAIM":
        # UNDERCLAIM: tool says HOLD/DEGRADED but actually works.
        # Can respond, but cannot be trusted for execution without verification.
        if intended_action in ("mutate", "atomic"):
            return RouteDecision(
                verdict=RouteVerdict.HOLD,
                tool_name=tool_name,
                reason=f"Tool '{tool_name}' is UNDERCLAIM — may work but cannot be "
                f"trusted for mutation without explicit verification.",
                capability_tier=tier_raw,
                status_alignment="UNDERCLAIM",
                requires_888_hold=True,
            )
        return RouteDecision(
            verdict=RouteVerdict.ALLOW,
            tool_name=tool_name,
            reason=f"Tool '{tool_name}' is UNDERCLAIM but usable for {intended_action}.",
            capability_tier=tier_raw,
            status_alignment="UNDERCLAIM",
            allowed=True,
        )

    # ── 7. ALIGNED: tier-based enforcement ──────────────────────────────────
    # TIER_C = ASSIST_ONLY
    autonomy_mode = capability_surface.get("autonomy_mode", "ASSIST")

    if autonomy_mode == "ASSIST" and intended_action in ("mutate", "atomic"):
        return RouteDecision(
            verdict=RouteVerdict.DOWNGRADE,
            tool_name=tool_name,
            reason=f"Autonomy mode is ASSIST. {intended_action} requires human approval.",
            capability_tier=tier_raw,
            status_alignment=alignment_raw,
            downgraded_to="ASSIST",
            requires_888_hold=True,
        )

    if autonomy_mode == "SHORT_CHAIN" and intended_action == "atomic":
        return RouteDecision(
            verdict=RouteVerdict.HOLD,
            tool_name=tool_name,
            reason="Autonomy mode is SHORT_CHAIN. Atomic actions require 888_HOLD.",
            capability_tier=tier_raw,
            status_alignment=alignment_raw,
            requires_888_hold=True,
        )

    # ── 8. Write capability: check write_ok ─────────────────────────────────
    if intended_action in ("mutate", "atomic", "dry_run") and not write_ok:
        return RouteDecision(
            verdict=RouteVerdict.HOLD,
            tool_name=tool_name,
            reason=f"Tool '{tool_name}' write_ok=false. Cannot {intended_action}.",
            capability_tier=tier_raw,
            status_alignment=alignment_raw,
            requires_888_hold=True,
        )

    if intended_action not in ("mutate", "atomic", "dry_run") and not read_ok:
        return RouteDecision(
            verdict=RouteVerdict.REJECT,
            tool_name=tool_name,
            reason=f"Tool '{tool_name}' read_ok=false. Cannot {intended_action}.",
            capability_tier=tier_raw,
            status_alignment=alignment_raw,
        )

    # ── 9. ALLOW ───────────────────────────────────────────────────────────
    return RouteDecision(
        verdict=RouteVerdict.ALLOW,
        tool_name=tool_name,
        reason=f"Tool '{tool_name}' is ALIGNED and capable for {intended_action}.",
        capability_tier=tier_raw,
        status_alignment=alignment_raw,
        allowed=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Batch Router — check a full plan against CapabilitySurface
# ═══════════════════════════════════════════════════════════════════════════════


def validate_plan_against_surface(
    plan_steps: list[dict[str, str]],
    capability_surface: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate an entire execution plan against the CapabilitySurface.

    Args:
        plan_steps: List of {tool_name, intended_action} dicts
        capability_surface: Full CapabilitySurface dict

    Returns:
        {
            "overall_verdict": "ALLOW" | "DOWNGRADE" | "REJECT",
            "decisions": [RouteDecision, ...],
            "rejected_count": int,
            "downgraded_count": int,
            "requires_888_hold": bool,
        }
    """
    decisions: list[RouteDecision] = []
    rejected = 0
    downgraded = 0
    any_hold = False

    for step in plan_steps:
        d = route_with_capability(
            tool_name=step["tool_name"],
            capability_surface=capability_surface,
            intended_action=step.get("intended_action", "observe"),
        )
        decisions.append(d)
        if d.verdict == RouteVerdict.REJECT:
            rejected += 1
        elif d.verdict == RouteVerdict.DOWNGRADE:
            downgraded += 1
        if d.requires_888_hold:
            any_hold = True

    if rejected > 0:
        overall = RouteVerdict.REJECT
    elif downgraded > 0:
        overall = RouteVerdict.DOWNGRADE
    else:
        overall = RouteVerdict.ALLOW

    return {
        "overall_verdict": overall.value,
        "decisions": [
            {
                "tool": d.tool_name,
                "verdict": d.verdict.value,
                "reason": d.reason,
                "requires_888_hold": d.requires_888_hold,
            }
            for d in decisions
        ],
        "rejected_count": rejected,
        "downgraded_count": downgraded,
        "requires_888_hold": any_hold,
        "checked_at": datetime.now(UTC).isoformat(),
    }

"""
Autonomy Band Router — From Tool Call to Jurisdiction Verdict
═══════════════════════════════════════════════════════════════════════════════

Classifies every MCP tool invocation into an autonomy band:

  GREEN  → read, inspect, draft, classify        → SEAL
  YELLOW → prepare, diff, stage plan             → SEAL with receipt
  ORANGE → local reversible write, config backup → requires rollback plan
  RED    → secrets, money, public, infra, delete → HOLD → judge gate
  BLACK  → irreversible destructive              → VOID

The router is pure classification. Enforcement is handled by the
GovernanceKernel + RecursiveGovernanceEngine upstream.

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.schemas.jurisdiction import (
    AutonomyBand,
    BandRoutingResult,
    JurisdictionEnvelope,
    RiskClass,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL NAME PATTERNS → BAND CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

# GREEN: observation, inspection, drafting — safe to autonomize
GREEN_PATTERNS: tuple[str, ...] = (
    "sense",
    "observe",
    "inspect",
    "read",
    "get",
    "list",
    "fetch",
    "search",
    "summarize",
    "draft",
    "classify",
    "check",
    "health",
    "probe",
    "ping",
    "status",
    "telemetry",
    "metric",
    "log",
)

# YELLOW: preparation, planning, staging — safe with receipt
YELLOW_PATTERNS: tuple[str, ...] = (
    "prepare",
    "plan",
    "stage",
    "diff",
    "compare",
    "validate",
    "lint",
    "format",
    "review",
    "suggest",
    "recommend",
    "estimate",
    "project",
    "forecast",
    "simulate",
)

# ORANGE: local mutation with rollback potential
ORANGE_PATTERNS: tuple[str, ...] = (
    "write",
    "update",
    "create",
    "edit",
    "modify",
    "patch",
    "configure",
    "deploy_local",
    "restart",
    "reload",
    "install",
    "sync",
    "build",
    "test",
)

# RED: external effects, secrets, money, infrastructure
RED_PATTERNS: tuple[str, ...] = (
    "delete",
    "drop",
    "remove",
    "destroy",
    "wipe",
    "purge",
    "pay",
    "transfer",
    "allocate",
    "spend",
    "withdraw",
    "secret",
    "vault",
    "key",
    "password",
    "token",
    "infra",
    "server",
    "network",
    "domain",
    "dns",
    "public",
    "publish",
    "expose",
    "external",
    "commit",
    "push",
    "merge",
    "force",
)

# BLACK: explicitly destructive and irreversible
BLACK_PATTERNS: tuple[str, ...] = (
    "rm_-rf",
    "drop_database",
    "wipe_disk",
    "destroy_cluster",
    "irreversible",
    "catastrophic",
)

# Risk-class mapping from band
BAND_TO_RISK: dict[AutonomyBand, RiskClass] = {
    AutonomyBand.GREEN: RiskClass.OBSERVE,
    AutonomyBand.YELLOW: RiskClass.PREPARE,
    AutonomyBand.ORANGE: RiskClass.MUTATE,
    AutonomyBand.RED: RiskClass.ATOMIC,
    AutonomyBand.BLACK: RiskClass.IRREVERSIBLE,
}


def _band_from_tool_name(tool_name: str) -> AutonomyBand:
    """Heuristic band classification from tool name."""
    lower = tool_name.lower()
    for pat in BLACK_PATTERNS:
        if pat in lower:
            return AutonomyBand.BLACK
    for pat in RED_PATTERNS:
        if pat in lower:
            return AutonomyBand.RED
    for pat in ORANGE_PATTERNS:
        if pat in lower:
            return AutonomyBand.ORANGE
    for pat in YELLOW_PATTERNS:
        if pat in lower:
            return AutonomyBand.YELLOW
    for pat in GREEN_PATTERNS:
        if pat in lower:
            return AutonomyBand.GREEN
    # Default: YELLOW for unknown tools (safe middle ground)
    return AutonomyBand.YELLOW


def _band_from_params(params: dict[str, Any]) -> AutonomyBand | None:
    """
    Inspect parameters for risk escalation signals.

    Returns a higher band if params contain dangerous indicators,
    or None if no escalation needed.
    """
    param_text = " ".join(str(v) for v in params.values() if isinstance(v, str))
    lower = param_text.lower()

    # Irreversible language in parameters
    if any(w in lower for w in ("irreversible", "delete", "drop", "wipe", "destroy", "force")):
        return AutonomyBand.RED

    # Secret exposure in parameters
    if any(w in lower for w in ("api_key", "password", "secret", "token", "private_key")):
        return AutonomyBand.RED

    # Rollback mentioned but not confirmed
    if "rollback" in lower and "rollback_plan" not in lower:
        return AutonomyBand.ORANGE

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════


class AutonomyBandRouter:
    """
    Classifies tool calls into autonomy bands.

    Stateless — uses heuristics on tool name and parameters.
    Overridable via explicit band claims in the envelope.
    """

    def __init__(self) -> None:
        self.classification_count = 0
        self.override_count = 0

    def classify(self, envelope: JurisdictionEnvelope) -> BandRoutingResult:
        """
        Assign an autonomy band to a jurisdiction envelope.

        Logic:
          1. If envelope explicitly claims a band, validate it (don't trust blindly).
          2. Classify from tool name heuristics.
          3. Escalate from parameter inspection.
          4. Take the strictest of the above.
        """
        self.classification_count += 1
        tool_name = envelope.tool_name
        actor_id = envelope.actor_id
        params = envelope.params

        # Start with tool name heuristic
        band = _band_from_tool_name(tool_name)
        reason = f"Tool name heuristic: {tool_name} → {band.value}"

        # Parameter escalation
        param_band = _band_from_params(params)
        if param_band is not None and _band_rank(param_band) > _band_rank(band):
            band = param_band
            reason += f" | Parameter escalation → {band.value}"

        # Explicit claim validation: actor cannot claim lower than heuristic
        claimed = envelope.claimed_band
        if claimed != band:
            if _band_rank(claimed) < _band_rank(band):
                # Actor claimed safer band than reality — override upward
                self.override_count += 1
                reason += f" | Claimed {claimed.value} overridden by reality → {band.value}"
            else:
                # Actor acknowledged higher risk — accept but verify
                band = claimed
                reason += f" | Claimed {claimed.value} accepted (self-reported higher risk)"

        risk = BAND_TO_RISK.get(band, RiskClass.OBSERVE)

        # Determine gate requirements
        fast_lane = band in (AutonomyBand.GREEN, AutonomyBand.YELLOW)
        requires_grant = band in (AutonomyBand.ORANGE, AutonomyBand.RED)
        requires_rollback = band in (AutonomyBand.ORANGE, AutonomyBand.RED, AutonomyBand.BLACK)
        requires_observe_receipt = band in (
            AutonomyBand.ORANGE,
            AutonomyBand.RED,
            AutonomyBand.BLACK,
        )

        return BandRoutingResult(
            tool_name=tool_name,
            actor_id=actor_id,
            assigned_band=band,
            risk_class=risk,
            reason=reason,
            requires_grant=requires_grant,
            requires_rollback=requires_rollback,
            requires_observe_receipt=requires_observe_receipt,
            fast_lane=fast_lane,
        )


def _band_rank(band: AutonomyBand) -> int:
    """Numeric rank for comparison — higher = more restrictive."""
    return {
        AutonomyBand.GREEN: 0,
        AutonomyBand.YELLOW: 1,
        AutonomyBand.ORANGE: 2,
        AutonomyBand.RED: 3,
        AutonomyBand.BLACK: 4,
    }[band]

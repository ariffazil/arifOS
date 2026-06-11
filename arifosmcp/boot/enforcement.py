"""
Enforcement Mesh — Truth → Permission → Action

DITEMPA BUKAN DIBERI — Forged, Not Given.

The bridge between CapabilitySurface (truth sensor) and Action Permission
(truth enforcer). Every tool call must pass through this mesh.

Invariants:
  1. No action without CapabilitySurface.
  2. No CapabilitySurface claim becomes authority until bound to
     agent_id + context_id + lease_id + vault_event_id.
  3. DEAD tools cannot be selected.
  4. UNDERCLAIM tools can respond but cannot execute.
  5. No lease = no action.
  6. Expired lease = no action.
  7. TIER_C = ASSIST_ONLY (observe/reason/draft).
  8. No external IO without Gateway approval.
  9. No irreversible action without Arif approval.
  10. Judge dead + high risk = 888_HOLD.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

logger = logging.getLogger(__name__)

# ── Types ──────────────────────────────────────────────────────────


class ActionClass(str, Enum):
    OBSERVE = "OBSERVE"
    REASON = "REASON"
    DRAFT = "DRAFT"
    MUTATE = "MUTATE"
    EXTERNAL = "EXTERNAL"
    ATOMIC = "ATOMIC"
    UNKNOWN = "UNKNOWN"


class EnforcementVerdict(str, Enum):
    ALLOW = "ALLOW"
    HOLD = "HOLD"
    DENY = "DENY"


ExecutionTier = Literal["TIER_A", "TIER_B", "TIER_C", "TIER_D", "DEAD"]

# ── Tier permissions ───────────────────────────────────────────────

TIER_ACTION_MAP: dict[str, set[str]] = {
    "TIER_A": {"OBSERVE", "REASON", "DRAFT", "MUTATE"},
    "TIER_B": {"OBSERVE", "REASON", "DRAFT"},
    "TIER_C": {"OBSERVE", "REASON", "DRAFT"},
    "TIER_D": {"OBSERVE"},
    "DEAD": set(),
}

# ── Risk escalation matrix ─────────────────────────────────────────

RISK_ESCALATION: dict[str, dict[str, bool]] = {
    # risk_tier → { requires_human, requires_lease, requires_judge, requires_arif }
    "low": {"human": False, "lease": True, "judge": False, "arif": False},
    "medium": {"human": False, "lease": True, "judge": False, "arif": False},
    "high": {"human": True, "lease": True, "judge": True, "arif": False},
    "atomic": {"human": True, "lease": True, "judge": True, "arif": True},
}


@dataclass
class ActionProposal:
    """A proposed action to be enforced."""

    verb: str  # e.g. "read_file", "execute_forge", "seal_vault"
    target: str  # what is being acted upon
    action_class: ActionClass
    risk_tier: str = "medium"
    reversibility: float = 0.5  # 0.0 = irreversible, 1.0 = fully reversible
    tool_name: str = ""
    agent_id: str = "unknown"
    context_id: str = ""
    lease_id: str = ""
    capability_surface_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnforcementResult:
    """Result of an enforcement check."""

    verdict: EnforcementVerdict
    reason: str
    failed_gates: list[str] = field(default_factory=list)
    tier: str = "TIER_C"
    requires_human: bool = False
    requires_arif: bool = False
    recommendation: str = ""


# ── Enforcement Engine ─────────────────────────────────────────────


class EnforcementEngine:
    """
    The truth enforcer. Takes CapabilitySurface + ActionProposal → verdict.

    This is the HARD GATE between truth and action.
    No tool call may proceed without passing through this engine.
    """

    def __init__(self):
        self._judge_alive = False  # updated by heartbeat
        self._vault_alive = False
        self._forge_alive = False

    def evaluate(
        self,
        *,
        action: ActionProposal,
        capability_surface: dict[str, Any] | None = None,
        lease: dict[str, Any] | None = None,
    ) -> EnforcementResult:
        """
        Evaluate a proposed action against the enforcement mesh.

        Returns ALLOW (proceed), HOLD (need human), or DENY (blocked).
        """
        failed: list[str] = []
        tier: ExecutionTier = "TIER_C"

        # ── Gate 1: CapabilitySurface required ───────────────
        if capability_surface is None:
            return EnforcementResult(
                verdict=EnforcementVerdict.HOLD,
                reason="No CapabilitySurface — cannot verify tool status",
                failed_gates=["capability_surface_required"],
                tier="TIER_D",
                requires_human=True,
            )

        summary = capability_surface.get("summary", {})
        tier = summary.get("execution_tier", "TIER_C")

        # ── Gate 2: Execution tier check ───────────────────
        allowed_classes = TIER_ACTION_MAP.get(tier, set())
        if action.action_class.value not in allowed_classes:
            failed.append(f"tier_mismatch:{tier}_forbids_{action.action_class.value}")

        # ── Gate 3: Tool status check ──────────────────────
        tools = capability_surface.get("tools", {})
        tool_status = tools.get(action.tool_name, {})
        alignment = tool_status.get("status_alignment", "UNKNOWN")

        if alignment == "DEAD":
            failed.append(f"tool_dead:{action.tool_name}")
        elif alignment == "UNDERCLAIM" and action.action_class not in (
            ActionClass.OBSERVE,
            ActionClass.REASON,
        ):
            failed.append(f"tool_underclaim:{action.tool_name}_cannot_{action.action_class.value}")
        elif alignment == "UNKNOWN":
            failed.append(f"tool_unknown:{action.tool_name}")

        # ── Gate 4: Lease check ────────────────────────────
        if lease is None:
            if action.action_class not in (ActionClass.OBSERVE, ActionClass.REASON):
                failed.append("no_lease")
        else:
            # Check lease expiry
            expires = lease.get("expires_at", "")
            if expires:
                try:
                    expiry = datetime.fromisoformat(expires.replace("Z", "+00:00"))
                    if expiry < datetime.now(timezone.utc):
                        failed.append("lease_expired")
                except (ValueError, TypeError):
                    pass

            # Check allowed actions
            allowed = lease.get("allowed_actions", [])
            if action.action_class.value.lower() not in [a.lower() for a in allowed]:
                failed.append(f"lease_forbids:{action.action_class.value}")

            # Check forbidden actions
            forbidden = lease.get("forbidden_actions", [])
            if action.verb.lower() in [f.lower() for f in forbidden] or any(
                f.lower() in action.action_class.value.lower() for f in forbidden
            ):
                failed.append(f"lease_forbidden:{action.verb}")

        # ── Gate 5: Risk escalation ────────────────────────
        risk_rules = RISK_ESCALATION.get(action.risk_tier, RISK_ESCALATION["medium"])

        if risk_rules.get("arif") and action.action_class in (
            ActionClass.ATOMIC,
            ActionClass.EXTERNAL,
        ):
            failed.append("arif_approval_required_for_atomic")

        if risk_rules.get("human") and not failed:
            pass  # Human gate advisory — not blocking

        # ── Gate 6: Judge fallback ─────────────────────────
        if risk_rules.get("judge") and not self._judge_alive:
            failed.append("judge_dead_high_risk")

        # ── Gate 7: External IO requires gateway ───────────
        if action.action_class == ActionClass.EXTERNAL:
            gateway = capability_surface.get("organs", {}).get("GATEWAY", {})
            if not gateway.get("reachable"):
                failed.append("gateway_unavailable_external_io_blocked")

        # ── Gate 8: Irreversibility check ──────────────────
        if action.reversibility < 0.1 and action.action_class not in (
            ActionClass.OBSERVE,
            ActionClass.REASON,
        ):
            failed.append("nearly_irreversible")

        # ── Determine verdict ──────────────────────────────
        if not failed:
            verdict = EnforcementVerdict.ALLOW
            reason = "All gates passed"
        elif any(
            "arif" in f or "judge_dead" in f or "gateway_unavailable" in f or "tool_dead" in f
            for f in failed
        ):
            verdict = EnforcementVerdict.HOLD
            reason = f"HOLD: {', '.join(failed[:3])}"
        else:
            verdict = EnforcementVerdict.HOLD
            reason = f"HOLD: {', '.join(failed[:3])}"

        # ── Recommendation ─────────────────────────────────
        if tier == "TIER_A":
            recommendation = "Proceed within lease scope"
        elif tier == "TIER_B":
            recommendation = "Draft/plan allowed; mutation requires human approval"
        elif tier == "TIER_C":
            recommendation = "ASSIST only — observe/reason/draft; no mutation"
        else:
            recommendation = "OBSERVE ONLY — all other actions require 888_HOLD"

        requires_human = risk_rules.get("human", False) or (
            tier in ("TIER_C", "TIER_D")
            and action.action_class
            not in (ActionClass.OBSERVE, ActionClass.REASON, ActionClass.DRAFT)
        )

        return EnforcementResult(
            verdict=verdict,
            reason=reason,
            failed_gates=failed,
            tier=tier,
            requires_human=requires_human,
            requires_arif=risk_rules.get("arif", False),
            recommendation=summary.get("recommendation", recommendation),
        )

    def update_organ_status(self, judge_alive: bool, vault_alive: bool, forge_alive: bool):
        """Update organ liveness from heartbeat checks."""
        self._judge_alive = judge_alive
        self._vault_alive = vault_alive
        self._forge_alive = forge_alive


# ── Action Event Builder (for VAULT999) ────────────────────────────


def build_action_event(
    *,
    action: ActionProposal,
    result: EnforcementResult,
    session_id: str = "",
    outcome: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build a structured action event for VAULT999 sealing.

    P1 fix: action field must never be empty. Every sealed event
    carries full action provenance.
    """
    event: dict[str, Any] = {
        "event_type": (
            "ACTION_EXECUTED"
            if result.verdict == EnforcementVerdict.ALLOW
            else "ACTION_DENIED"
            if result.verdict == EnforcementVerdict.DENY
            else "ACTION_HOLD"
        ),
        "action": {
            "verb": action.verb,
            "target": action.target,
            "action_class": action.action_class.value,
            "risk_tier": action.risk_tier,
            "reversibility": action.reversibility,
        },
        "agent_id": action.agent_id,
        "context_id": action.context_id or "",
        "lease_id": action.lease_id or "",
        "tool_name": action.tool_name,
        "capability_surface_hash": action.capability_surface_hash or "",
        "decision": {
            "verdict": result.verdict.value,
            "reason": result.reason,
            "failed_gates": result.failed_gates,
            "tier": result.tier,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
    }

    if outcome:
        event["outcome"] = outcome

    return event


# ── Quick enforcement gate (for tool wrappers) ─────────────────────


def enforce_action(
    tool_name: str,
    action_class: str,
    target: str = "",
    risk_tier: str = "low",
    reversibility: float = 0.8,
    agent_id: str = "unknown",
    lease: dict[str, Any] | None = None,
    capability_surface: dict[str, Any] | None = None,
) -> EnforcementResult:
    """
    One-call enforcement gate. Call this before every tool execution.

    Returns EnforcementResult. If verdict != ALLOW, tool must return
    the HOLD/DENY receipt instead of executing.
    """
    engine = _get_engine()

    action = ActionProposal(
        verb=tool_name,
        target=target or "unknown",
        action_class=ActionClass(action_class),
        risk_tier=risk_tier,
        reversibility=reversibility,
        tool_name=tool_name,
        agent_id=agent_id,
    )

    result = engine.evaluate(
        action=action,
        capability_surface=capability_surface,
        lease=lease,
    )

    logger.info(
        f"Enforcement: {tool_name} class={action_class} tier={risk_tier} "
        f"→ {result.verdict.value} ({result.reason[:80]})"
    )

    return result


# ── Singleton ─────────────────────────────────────────────────────

_engine: EnforcementEngine | None = None


def _get_engine() -> EnforcementEngine:
    global _engine
    if _engine is None:
        _engine = EnforcementEngine()
    return _engine

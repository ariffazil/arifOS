"""
decision.py — The single Decision object.

This is the kernel's verdict on a proposed action. The same
Decision flows through prethink → pretool → posttool → seal.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# Re-export for backward compat
class _CognitionLane:
    """Placeholder; real enum defined below."""

    pass


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

from enum import Enum


class CognitionLane(str, Enum):
    """
    What KIND of thinking is the agent doing?

    OBSERVE  — read-only. No state mutation.
    PLAN     — reasoning, no side effects.
    MUTATE   — modifying local state.
    EXECUTE  — cross-system action.
    """

    OBSERVE = "OBSERVE"
    PLAN = "PLAN"
    MUTATE = "MUTATE"
    EXECUTE = "EXECUTE"


class ActionClass(str, Enum):
    """
    What is the agent ABOUT TO DO?

    Used by pretool to classify the action before it executes.
    """

    OBSERVE = "OBSERVE"
    COMPUTE = "COMPUTE"
    PROPOSE = "PROPOSE"
    MUTATE_LOCAL = "MUTATE_LOCAL"
    MUTATE_EXTERNAL = "MUTATE_EXTERNAL"
    DEPLOY = "DEPLOY"
    SPEND = "SPEND"
    PUBLISH = "PUBLISH"
    DELETE = "DELETE"
    SIGN = "SIGN"
    GRANT_ACCESS = "GRANT_ACCESS"
    CREDENTIAL_CHANGE = "CREDENTIAL_CHANGE"
    CONSTITUTION_CHANGE = "CONSTITUTION_CHANGE"


# 888 HOLD triggers — these action classes always require human authority
HOLD_TRIGGERS: frozenset[ActionClass] = frozenset(
    {
        ActionClass.DEPLOY,
        ActionClass.PUBLISH,
        ActionClass.DELETE,
        ActionClass.SPEND,
        ActionClass.SIGN,
        ActionClass.GRANT_ACCESS,
        ActionClass.CREDENTIAL_CHANGE,
        ActionClass.CONSTITUTION_CHANGE,
    }
)

# 888 HOLD triggers — high-blast-radius actions
HIGH_BLAST_TRIGGERS: frozenset[ActionClass] = frozenset(
    {
        ActionClass.MUTATE_EXTERNAL,
        ActionClass.DEPLOY,
        ActionClass.PUBLISH,
        ActionClass.DELETE,
        ActionClass.SPEND,
        ActionClass.SIGN,
        ActionClass.GRANT_ACCESS,
        ActionClass.CREDENTIAL_CHANGE,
        ActionClass.CONSTITUTION_CHANGE,
    }
)


# ─────────────────────────────────────────────────────────────────────────────
# Floor verdict
# ─────────────────────────────────────────────────────────────────────────────


class FloorVerdict(BaseModel):
    """One floor's verdict for a given decision."""

    floor_id: str  # "F1", "F2", ..., "F13"
    verdict: Literal["PASS", "WARN", "FAIL", "HOLD"]
    reason: str
    evidence: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Risk envelope
# ─────────────────────────────────────────────────────────────────────────────


class RiskEnvelope(BaseModel):
    """Risk assessment for a decision."""

    blast_radius: Literal["NONE", "LOCAL", "SESSION", "FEDERATION", "EXTERNAL"] = "NONE"
    reversibility: Literal["REVERSIBLE", "PARTIAL", "IRREVERSIBLE"] = "REVERSIBLE"
    human_ack_required: bool = False
    estimated_tokens: int = 0
    estimated_time_seconds: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# The Decision
# ─────────────────────────────────────────────────────────────────────────────


class Decision(BaseModel):
    """
    THE single decision object for the arifOS kernel.

    Verdict semantics:
        ALLOW     — proceed, decision is sealed
        DENY      — block, do not proceed
        HOLD      — pause, request human authority (F13 SOVEREIGN)
        DEGRADED  — proceed with warnings, attach to seal
    """

    verdict: Literal["ALLOW", "DENY", "HOLD", "DEGRADED"]
    cognition_lane: CognitionLane
    action_class: ActionClass | None = None
    lease_id: str | None = None
    floor_verdicts: list[FloorVerdict] = Field(default_factory=list)
    risk: RiskEnvelope = Field(default_factory=RiskEnvelope)
    required_human_ack: bool = False
    reasons: list[str] = Field(default_factory=list)
    next_safe_action: str | None = None
    seal_pointer: str | None = None
    taint: Literal["UNTRUSTED", "TRUSTED", "VERIFIED"] = "UNTRUSTED"

    def is_permitted(self) -> bool:
        return self.verdict in ("ALLOW", "DEGRADED")

    def is_blocking(self) -> bool:
        return self.verdict in ("DENY", "HOLD")

    def is_holding(self) -> bool:
        return self.verdict == "HOLD" or self.required_human_ack

    def failed_floors(self) -> list[str]:
        return [f.floor_id for f in self.floor_verdicts if f.verdict == "FAIL"]

    def to_envelope(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "cognition_lane": self.cognition_lane.value,
            "action_class": self.action_class.value if self.action_class else None,
            "lease_id": self.lease_id,
            "floor_verdicts": [f.model_dump() for f in self.floor_verdicts],
            "risk": self.risk.model_dump(),
            "required_human_ack": self.required_human_ack,
            "reasons": self.reasons,
            "next_safe_action": self.next_safe_action,
            "seal_pointer": self.seal_pointer,
            "taint": self.taint,
        }

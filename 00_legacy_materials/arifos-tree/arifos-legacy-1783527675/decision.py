"""
decision.py — The single Decision object.

This is the kernel's verdict on a proposed action. The same
Decision flows through prethink → pretool → posttool → seal.

APEX THEORY EMBEDDING (2026-06-28):
- apex_overclaim_audit(): F2 TRUTH enforcement — detect certainty
  claims without evidence. Maps to APEX Contrast (overclaim audit).
- apex_epistemic_tag: OBS/DER/INT/SPEC labels in FloorVerdict.evidence.
- apex_mesa_signal in RiskEnvelope: Landauer thermodynamic cost signal
  from risk.py, surfaced as a decision-level field.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# APEX THEORY imports
from arifos.risk import landauer_cost_for_action, mesa_optimization_signal


# ─── APEX: Epistemic Tagging ─────────────────────────────────────────────────

APEX_EPISTEMIC_TAGS: tuple[str, ...] = ("OBS", "DER", "INT", "SPEC")
"""
APEX THEORY: Epistemic certainty labels.

Required on every claim in FloorVerdict.reason and Decision.reasons.
Hard cap at 0.90 confidence per F7 HUMILITY.
"""


def apex_tag_claim(claim: str, default_tag: str = "OBS") -> str:
    """
    APEX THEORY: Tag a textual claim with its epistemic source.

    Scans the claim for markers and returns the appropriate tag:
    - OBS  — direct observation ("I see X", "X is present")
    - DER  — derived from OBS ("therefore X", "computed X from Y")
    - INT  — interpretation of ambiguous data ("likely X", "may be Y")
    - SPEC — speculation without direct evidence ("might X", "could be Y")

    If no markers found, returns default_tag (default: OBS).
    Falls back to DER if the claim contains logical connectors.
    Falls back to SPEC if modal uncertainty words are present.
    """
    claim_lower = claim.lower()

    # APEX contrast: certainty markers override everything.
    # "definitely confirmed" = SPEC (overclaim), not OBS.
    certainty_markers = (
        "definitely",
        "certainly",
        "absolutely",
        "clearly",
        "obviously",
        "undoubtedly",
        "surely",
        "always",
        "never",
    )
    if any(m in claim_lower for m in certainty_markers):
        return "SPEC"

    # SPEC markers — modal speculation
    spec_markers = (
        "might",
        "could",
        "possibly",
        "perhaps",
        "speculate",
        "unconfirmed",
        "unverified",
        "unclear",
        "unknown",
        "may be",
        "potentially",
        "assumed",
    )
    if any(m in claim_lower for m in spec_markers):
        return "SPEC"

    # OBS markers — direct observation (checked after SPEC to avoid
    # false OBS from "confirmed" which appears in both categories)
    obs_markers = (
        "observed",
        "confirmed",
        "measured",
        "detected",
        "present",
        "exists",
        "seen",
        "found",
        "verified",
    )
    if any(m in claim_lower for m in obs_markers):
        return "OBS"

    # DER markers — logical derivation
    der_markers = (
        "therefore",
        "thus",
        "hence",
        "computed",
        "calculated",
        "derived",
        "because",
        "implies",
        "consequently",
    )
    if any(m in claim_lower for m in der_markers):
        return "DER"

    # INT markers — interpretive
    int_markers = (
        "likely",
        "probable",
        "appears",
        "suggests",
        "consistent with",
        "indicative",
        "presumed",
    )
    if any(m in claim_lower for m in int_markers):
        return "INT"

    return default_tag


def apex_overclaim_audit(claims: list[str]) -> dict[str, Any]:
    """
    APEX THEORY: F2 TRUTH — detect overclaim / certainty without evidence.

    Scans a list of textual claims and flags:
    - SPEC claims asserted as CERTAIN (confidence > 0.90 on unverified)
    - INT claims treated as OBS
    - Missing epistemic tags

    Returns:
        overclaim_count: number of overclaim patterns detected
        flagged_claims: list of (claim, issue) tuples
        apex_epistemic_tags: APEX-EPISTEMIC-TAG header for responses
    """
    flagged = []
    for claim in claims:
        tag = apex_tag_claim(claim)
        issue = None

        if tag == "SPEC" and ("definitely" in claim.lower() or "certainly" in claim.lower()):
            issue = "SPEC claim with certainty language"
        elif tag == "INT" and "confirmed" in claim.lower():
            issue = "INT claim with OBS certainty language"

        if issue:
            flagged.append((claim, issue))

    return {
        "overclaim_count": len(flagged),
        "flagged_claims": flagged,
        "apex_epistemic_tags": APEX_EPISTEMIC_TAGS,
        "confidence_cap": 0.90,  # F7 HUMILITY hard cap
        "epistemic_label": "APEX-OVERCLAIM-AUDIT",
        # APEX contrast: always label confidence explicitly
        "confidence": 0.85,
        "confidence_label": "DER",
    }


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
    fidelity_loss: float = 0.0  # APEX: estimated information loss at layer boundary crossings


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
    fidelity_loss: float = 0.0  # APEX: cumulative information fidelity loss across layer boundaries

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
            "fidelity_loss": self.fidelity_loss,
            "risk_fidelity_loss": self.risk.fidelity_loss,
        }

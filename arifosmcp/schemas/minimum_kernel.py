"""
Minimum Constitutional Kernel — The Thin Operational Spine.
═══════════════════════════════════════════════════════════

The philosophy can be grand. The runtime must be boring.
This is the beating heart of arifOS. Every module must pass through this.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

from .reversibility import ReversibilityClass
from .truth_state import TruthState


class KernelInput(BaseModel):
    """The thin spine of an agent's request to the constitutional kernel."""

    actor: str = Field(..., description="Identity of the agent or process making the request.")
    intent: str = Field(
        ..., description="A clear, plain-text description of what the actor is trying to achieve."
    )
    requested_capability: str = Field(
        ..., description="The specific tool, organ, or API being invoked."
    )
    domain: str = Field(..., description="The federation domain (e.g., GEOX, WEALTH, WELL, AAA).")
    evidence: list[dict[str, Any]] = Field(
        default_factory=list, description="Array of supporting evidence payloads."
    )
    authority_token: str | None = Field(
        default=None, description="Cryptographic or session token granting the authority."
    )
    reversibility_level: ReversibilityClass = Field(
        ..., description="The R-scale (R0-R5) assessment of the action."
    )
    blast_radius: str = Field(
        ..., description="What scope of data, capital, or truth this action touches."
    )
    epistemic_state: TruthState = Field(
        default=TruthState.UNKNOWN, description="The universal truth state of the payload."
    )
    measurement: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Optional MeasurementPacket from A-FORGE. When present, kernel uses "
            "G, C_dark, W3 for floor checks instead of computing anything. "
            "MEMBRANE-03: only typed packets cross the membrane."
        ),
    )


class KernelOutput(BaseModel):
    """The boring, ruthless decision from the constitutional kernel."""

    decision: Literal["ALLOW", "DENY", "ESCALATE", "SIMULATE", "CLASSIFICATION_HOLD"] = Field(
        ..., description="The binary or routing verdict."
    )
    constitutional_floor_triggered: str | None = Field(
        default=None, description="Which F-floor (e.g., F8) intercepted this."
    )
    reason: str = Field(..., description="A one-sentence explanation of the decision.")
    audit_hash: str | None = Field(default=None, description="The VAULT999 ledger receipt hash.")
    constitutional_chain_id: str | None = Field(
        default=None,
        description="Canonical chain ID binding judge session + candidate + audit_hash. "
        "Format: cc_<sha256>. Required by arif_seal for vault binding.",
    )
    judge_state_hash: str | None = Field(
        default=None,
        description="SHA-256 of the canonical judge_state dict. Proves the receipt "
        "originates from a specific judge decision, not an arbitrary record.",
    )
    seal_type: str | None = Field(
        default=None,
        description="SEAL_RECORD (audit evidence, no execution grant) "
        "or SEAL_AUTHORIZATION (execution grant, requires F13).",
    )
    rollback_instruction: str | None = Field(
        default=None, description="Instruction or payload to reverse the action if needed."
    )

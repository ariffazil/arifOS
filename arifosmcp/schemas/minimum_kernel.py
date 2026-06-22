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
    intent: str = Field(..., description="A clear, plain-text description of what the actor is trying to achieve.")
    requested_capability: str = Field(..., description="The specific tool, organ, or API being invoked.")
    domain: str = Field(..., description="The federation domain (e.g., GEOX, WEALTH, WELL, AAA).")
    evidence: list[dict[str, Any]] = Field(default_factory=list, description="Array of supporting evidence payloads.")
    authority_token: str | None = Field(default=None, description="Cryptographic or session token granting the authority.")
    reversibility_level: ReversibilityClass = Field(..., description="The R-scale (R0-R5) assessment of the action.")
    blast_radius: str = Field(..., description="What scope of data, capital, or truth this action touches.")
    epistemic_state: TruthState = Field(default=TruthState.UNKNOWN, description="The universal truth state of the payload.")


class KernelOutput(BaseModel):
    """The boring, ruthless decision from the constitutional kernel."""
    
    decision: Literal["ALLOW", "DENY", "ESCALATE", "SIMULATE"] = Field(..., description="The binary or routing verdict.")
    constitutional_floor_triggered: str | None = Field(default=None, description="Which F-floor (e.g., F8) intercepted this.")
    reason: str = Field(..., description="A one-sentence explanation of the decision.")
    audit_hash: str | None = Field(default=None, description="The VAULT999 ledger receipt hash.")
    rollback_instruction: str | None = Field(default=None, description="Instruction or payload to reverse the action if needed.")


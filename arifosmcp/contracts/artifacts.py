"""
arifosmcp/contracts/artifacts.py — Canonical Artifact States (Audit Fix 4, 5)

Rule 2: One state name = one meaning.
ArtifactStatus must be binary enough for governance.
"""

from enum import Enum
from pydantic import BaseModel, Field
from arifosmcp.contracts.verdicts import ArtifactStatus

class Claim(BaseModel):
    """A single claim with grounding (Fix 5)."""
    statement: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    source: str = "inferred"

class AnswerBasis(BaseModel):
    """
    The substance of a mind/reply response (Fix 5).
    Not constitutional theatre - actual usable content.
    """
    summary: str
    detailed_answer: str
    claims: list[Claim] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    key_findings: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    alternative_views: list[str] = Field(default_factory=list)

class Artifact(BaseModel):
    """The base artifact object produced by any tool (Fix 5)."""
    type: str
    status: ArtifactStatus = ArtifactStatus.NONE
    payload: dict = Field(default_factory=dict)
    
    # Typed payload extensions
    answer_basis: AnswerBasis | None = None
    
    # Audit trail (F1, F11)
    creator_id: str
    session_id: str
    timestamp: float

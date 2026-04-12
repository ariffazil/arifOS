"""
arifosmcp/contracts/envelopes.py — Canonical Unified Response (Audit Fix CR-01)

Rule 1: One tool = one contract.
This shell is used for ALL transports: STDIO, HTTPS, SSE.
"""

from pydantic import BaseModel, Field
from arifosmcp.contracts.verdicts import ExecutionStatus, GovernanceStatus, ContinuationStatus
from arifosmcp.contracts.identity import IdentityContext
from arifosmcp.contracts.artifacts import Artifact, ArtifactStatus
from arifosmcp.contracts.continuity import ContinuityState

class ResponseEnvelope(BaseModel):
    """
    CR-01: Single Unified Response Envelope.
    Everything else (telemetry, symbolic metrics) is moved to 'diagnostics'.
    """
    tool_name: str
    execution_status: ExecutionStatus
    governance_status: GovernanceStatus
    artifact_status: ArtifactStatus
    continue_allowed: bool
    
    # Primary Usable Payload (Audit Fix CF-05)
    primary_artifact: Artifact | None = None
    
    # Governance & Continuity (Folded)
    identity: IdentityContext | None = None
    continuity: ContinuityState | None = None
    
    # Symbolic / Introspective (Demoted out of top-level machine contract)
    diagnostics: dict = Field(default_factory=dict)
    
    # Metadata
    version: str = "2.0.0"
    timestamp: float

"""
Compatibility shim — models.py renamed to model.py
Redirects to model.py for backward compatibility.
"""
import warnings

warnings.warn("models.py is deprecated — use model.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.runtime.model import (  # noqa: F401
    ArifOSError,
    Artifact,
    ArtifactStatus,
    AuthorityLevel,
    CallerContext,
    CanonicalAuthority,
    ClaimStatus,
    ContinuationStatus,
    ContinuityState,
    DeltaOmegaPsi,
    ExecutionStatus,
    GovernanceStatus,
    IdentityContext,
    RuntimeEnvelope,
    RuntimeStatus,
    SessionState,
    Stage,
    ToolRequest,
    ToolResponse,
    Verdict,
    VerdictScope,
)

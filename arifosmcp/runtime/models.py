"""
Compatibility shim — models.py renamed to model.py
Redirects to model.py for backward compatibility.
"""
import warnings
warnings.warn("models.py is deprecated — use model.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.runtime.model import (  # noqa: F401
    ClaimStatus,
    AuthorityLevel,
    RuntimeStatus,
    Stage,
    ExecutionStatus,
    GovernanceStatus,
    ContinuationStatus,
    ArtifactStatus,
    VerdictScope,
    DeltaOmegaPsi,
    ToolRequest,
    ToolResponse,
    Verdict,
    SessionState,
    CallerContext,
    CanonicalAuthority,
    IdentityContext,
    ContinuityState,
    Artifact,
    RuntimeEnvelope,
    ArifOSError,
)

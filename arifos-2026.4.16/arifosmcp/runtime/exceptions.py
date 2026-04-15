"""
arifosmcp/runtime/exceptions.py — Backward compatibility shim.

All exceptions are defined in models.py. This module re-exports them
for legacy imports.
"""

from arifosmcp.runtime.models import (
    ArifOSError,
)
from arifosmcp.runtime.models import (
    ConstitutionalViolationError as ConstitutionalViolation,
)
from arifosmcp.runtime.models import (
    EpistemicGapError as EpistemicGap,
)
from arifosmcp.runtime.models import (
    InfrastructureFaultError as InfrastructureFault,
)

__all__ = [
    "ArifOSError",
    "ConstitutionalViolation",
    "EpistemicGap",
    "InfrastructureFault",
]

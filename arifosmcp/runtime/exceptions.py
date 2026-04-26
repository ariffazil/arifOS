"""
arifosmcp/runtime/exceptions.py — Backward compatibility shim.

All exceptions are defined in models.py. This module re-exports them
for legacy imports.
"""

from arifosmcp.runtime.model import (
    ArifOSError,
)
from arifosmcp.runtime.model import (
    ConstitutionalViolationError as ConstitutionalViolation,
)
from arifosmcp.runtime.model import (
    EpistemicGapError as EpistemicGap,
)
from arifosmcp.runtime.model import (
    InfrastructureFaultError as InfrastructureFault,
)

__all__ = [
    "ArifOSError",
    "ConstitutionalViolation",
    "EpistemicGap",
    "InfrastructureFault",
]

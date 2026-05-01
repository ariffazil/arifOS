"""
arifos/runtime/exceptions.py — Backward compatibility shim.

All exceptions are defined in models.py. This module re-exports them
for legacy imports.
"""

from arifos.runtime.models import (
    ArifOSError,
)
from arifos.runtime.models import (
    ConstitutionalViolationError as ConstitutionalViolation,
)
from arifos.runtime.models import (
    EpistemicGapError as EpistemicGap,
)
from arifos.runtime.models import (
    InfrastructureFaultError as InfrastructureFault,
)

__all__ = [
    "ArifOSError",
    "ConstitutionalViolation",
    "EpistemicGap",
    "InfrastructureFault",
]

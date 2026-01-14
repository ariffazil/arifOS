"""
DEPRECATED: This module has moved to arifos_core.hypervisor.guards.session_dependency

Session dependency validation belongs in the hypervisor layer.
This shim will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from arifos_core.guards.session_dependency import SessionDependencyGuard
  NEW: from arifos_core.hypervisor.guards.session_dependency import SessionDependencyGuard

Constitutional Mapping:
- Old Location: guards/ (incorrect layer)
- New Location: hypervisor/guards/ (F10-F12 enforcement)
- Related Theory: See L1_THEORY/canon/012_enforcement/HYPERVISOR.md
"""
import warnings

warnings.warn(
    "arifos_core.guards.session_dependency is deprecated. "
    "Use arifos_core.hypervisor.guards.session_dependency instead. "
    "This shim will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from arifos_core.hypervisor.guards.session_dependency import *

"""
DEPRECATED: Guards have moved to arifos_core.hypervisor.guards

Guards belong in the hypervisor layer (F10-F12 pre-pipeline enforcement).
This module will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from arifos.guards import [guard classes]
  NEW: from arifos.hypervisor.guards import [guard classes]

Constitutional Mapping:
- Old Location: guards/ (incorrect layer)
- New Location: hypervisor/guards/ (F10-F12 enforcement)
- Related Theory: See 000_THEORY/canon/012_enforcement/HYPERVISOR.md
"""
import warnings

warnings.warn(
    "arifos_core.guards is deprecated. "
    "Use arifos_core.hypervisor.guards instead. "
    "This module will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location
from arifos.hypervisor.guards import *

__all__ = [
    'InjectionGuard',
    'NonceManager', 
    'OntologyGuard',
    'SessionDependencyGuard',
]

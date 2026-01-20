"""
DEPRECATED: This module has moved to arifos.hypervisor.guards.injection_guard

Injection defense belongs in the hypervisor layer (F12 enforcement).
This shim will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from arifos.guards.injection_guard import InjectionGuard
  NEW: from arifos.hypervisor.guards.injection_guard import InjectionGuard

Constitutional Mapping:
- Old Location: guards/ (incorrect layer)
- New Location: hypervisor/guards/ (F12 Injection Defense)
- Related Theory: See 000_THEORY/canon/012_enforcement/F12_INJECTION_DEFENSE.md
"""
import warnings

warnings.warn(
    "arifos.guards.injection_guard is deprecated. "
    "Use arifos.hypervisor.guards.injection_guard instead. "
    "This shim will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from arifos.hypervisor.guards.injection_guard import *

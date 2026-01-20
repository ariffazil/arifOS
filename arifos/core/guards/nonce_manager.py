"""
DEPRECATED: This module has moved to arifos.core.hypervisor.guards.nonce_manager

Nonce management belongs in the hypervisor layer (F11 Command Auth).
This shim will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from arifos.core.guards.nonce_manager import NonceManager
  NEW: from arifos.core.hypervisor.guards.nonce_manager import NonceManager

Constitutional Mapping:
- Old Location: guards/ (incorrect layer)
- New Location: hypervisor/guards/ (F11 Command Auth)
- Related Theory: See 000_THEORY/canon/012_enforcement/F11_COMMAND_AUTH.md
"""
import warnings

warnings.warn(
    "arifos.core.guards.nonce_manager is deprecated. "
    "Use arifos.core.hypervisor.guards.nonce_manager instead. "
    "This shim will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from arifos.core.hypervisor.guards.nonce_manager import *

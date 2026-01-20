"""
DEPRECATED: This module has moved to arifos.state.ledger

State management has been extracted from governance to its own layer.
This shim will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from arifos.apex.governance import ledger
  NEW: from arifos.state import ledger

  OLD: from arifos.apex.governance.ledger import AuditLedger
  NEW: from arifos.state.ledger import AuditLedger

Constitutional Mapping:
- Old Location: apex/governance/ (mixed concerns)
- New Location: state/ (pure state management)
- Related Theory: See 000_THEORY/canon/012_enforcement/STATE_MANAGEMENT.md
"""
import warnings

warnings.warn(
    "arifos.apex.governance.ledger is deprecated. "
    "Use arifos.state.ledger instead. "
    "This shim will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from arifos.state.ledger import *

__all__ = ['AuditLedger']

"""
DEPRECATED: This module has moved to canonical_core.state.ledger

State management has been extracted from governance to its own layer.
This shim will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from canonical_core.apex.governance import ledger
  NEW: from canonical_core.state import ledger

  OLD: from canonical_core.apex.governance.ledger import AuditLedger
  NEW: from canonical_core.state.ledger import AuditLedger

Constitutional Mapping:
- Old Location: apex/governance/ (mixed concerns)
- New Location: state/ (pure state management)
- Related Theory: See 000_THEORY/canon/012_enforcement/STATE_MANAGEMENT.md
"""
import warnings

warnings.warn(
    "canonical_core.apex.governance.ledger is deprecated. "
    "Use canonical_core.state.ledger instead. "
    "This shim will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from canonical_core.memory.state.ledger import *

__all__ = ['AuditLedger']

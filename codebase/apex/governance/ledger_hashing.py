"""
DEPRECATED: This module has moved to canonical_core.state.ledger_hashing

Ledger hashing functionality is now part of the state layer.
This shim will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from codebase.apex.governance.ledger_hashing import sha256_hex
  NEW: from codebase.state.ledger_hashing import sha256_hex

Constitutional Mapping:
- Old Location: apex/governance/ (mixed concerns)
- New Location: state/ (pure state management)
- Related Theory: See 000_THEORY/canon/012_enforcement/STATE_MANAGEMENT.md
"""
import warnings

warnings.warn(
    "canonical_core.apex.governance.ledger_hashing is deprecated. "
    "Use canonical_core.state.ledger_hashing instead. "
    "This shim will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from codebase.state.ledger_hashing import *

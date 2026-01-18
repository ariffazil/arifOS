"""
DEPRECATED: This module has moved to arifos_core.state.merkle_ledger

Combined merkle + ledger functionality is now part of the state layer.
This shim will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from arifos.core.apex.governance.merkle_ledger import MerkleLedger
  NEW: from arifos.core.state.merkle_ledger import MerkleLedger

Constitutional Mapping:
- Old Location: apex/governance/ (mixed concerns)
- New Location: state/ (pure state management)
- Related Theory: See L1_THEORY/canon/012_enforcement/STATE_MANAGEMENT.md
"""
import warnings

warnings.warn(
    "arifos_core.apex.governance.merkle_ledger is deprecated. "
    "Use arifos_core.state.merkle_ledger instead. "
    "This shim will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from arifos.core.state.merkle_ledger import *

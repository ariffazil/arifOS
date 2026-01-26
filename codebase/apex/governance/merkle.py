"""
DEPRECATED: This module has moved to canonical_core.state.merkle

Merkle tree functionality is now part of the state layer.
This shim will be removed in v47.2 (72 hours after v47.1 release).

Update your imports:
  OLD: from codebase.apex.governance.merkle import MerkleTree
  NEW: from codebase.state.merkle import MerkleTree

Constitutional Mapping:
- Old Location: apex/governance/ (mixed concerns)
- New Location: state/ (pure state management)
- Related Theory: See 000_THEORY/canon/012_enforcement/MERKLE_PROOFS.md
"""
import warnings

warnings.warn(
    "canonical_core.apex.governance.merkle is deprecated. "
    "Use canonical_core.state.merkle instead. "
    "This shim will be removed in v47.2 (72 hours after v47.1).",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from codebase.state.merkle import *

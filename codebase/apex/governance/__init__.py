"""
arifos.core.governance - Safety & Audit Module

Contains governance and audit components:
- fag: File Access Guardian
- ledger: Cooling ledger operations (MOVED to arifos.core.state in v47)
- ledger_hashing: Hash chain integrity (MOVED to arifos.core.state in v47)
- merkle: Merkle proofs (MOVED to arifos.core.state in v47)
- zkpc_runtime: zkPC 5-phase runtime
- vault_retrieval: Vault access

Version: v47.0.0 - Equilibrium Architecture
"""

import warnings

# v42: Import actual exports from modules
from .fag import FAG, FAGReadResult, SecurityAlert
from .ledger import log_cooling_entry

# v47: Backward compatibility - Import state modules from new location
from codebase.state import (
    ledger_cryptography,
    ledger_hashing,
    merkle,
    merkle_ledger,
)

# These imports may need to be verified - commented out until confirmed:
# from .ledger_hashing import compute_chain_hash, verify_chain
# from .merkle import compute_merkle_root, get_merkle_proof
# from .zkpc_runtime import ZKPCRuntime
# from .vault_retrieval import retrieve_from_vault

__all__ = [
    # FAG
    "FAG",
    "FAGReadResult",
    "SecurityAlert",
    # Ledger
    "log_cooling_entry",
    # v47 Backward compat (with deprecation)
    "ledger_cryptography",
    "ledger_hashing",
    "merkle",
    "merkle_ledger",
]

# v42: Backward compat aliases
FileAccessGuardian = FAG
FAGResult = FAGReadResult

# v47: Issue deprecation warning on module-level access
def __getattr__(name):
    state_modules = ["ledger_cryptography", "ledger_hashing", "merkle", "merkle_ledger"]
    if name in state_modules:
        warnings.warn(
            f"Importing {name} from codebase.apex.governance is deprecated. "
            f"Use 'from codebase.state import {name}' instead. "
            "This compatibility shim will be removed in v48.",
            DeprecationWarning,
            stacklevel=2
        )
    return globals().get(name)


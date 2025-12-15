"""
arifos_core.governance - Safety & Audit Module

Contains governance and audit components:
- fag: File Access Guardian
- ledger: Cooling ledger operations
- ledger_hashing: Hash chain integrity
- merkle: Merkle proofs
- zkpc_runtime: zkPC 5-phase runtime
- vault_retrieval: Vault access

Version: v42.0.0
"""

# v42: Import actual exports from modules
from .fag import FAG, FAGReadResult, SecurityAlert
from .ledger import log_cooling_entry

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
]

# v42: Backward compat aliases
FileAccessGuardian = FAG
FAGResult = FAGReadResult

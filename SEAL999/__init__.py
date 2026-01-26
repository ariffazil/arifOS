"""
SEAL-999 Canonical Implementation

Centralized constitutional sealing system with Merkle trees, Phoenix cooling, and cryptographic proofs.

This is the CODE component of the 999 system:
- SEAL999 = Pure Code (Logic/Algorithm) - .py files only
- VAULT999 = Pure Storage (Data/Memory) - Directories + .json + .jsonl

Brain/Body Separation:
- SEAL999 is the "Hippocampus" - the sealing ALGORITHM
- VAULT999 is the "Long-Term Memory Store" - the data PERSISTENCE
"""

from .vault import SEAL999
from .state import VaultEntry, SessionLedger, VaultConfig
from .ledger import HashChain, Ledger, MerkleTree
from .zkpc import ZKPCGenerator, ZKPCProof
from .stage import execute_stage, get_seal999, vault_999

__all__ = [
    # Core sealing class
    "SEAL999",
    # State management
    "VaultEntry",
    "SessionLedger",
    "VaultConfig",
    # Ledger & crypto
    "HashChain",
    "Ledger",
    "MerkleTree",
    "ZKPCGenerator",
    "ZKPCProof",
    # Pipeline integration
    "execute_stage",
    "get_seal999",
    "vault_999",
]

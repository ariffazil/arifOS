"""
arifOS ZKPC Module - Zero-Knowledge Proof of Constitutional Compliance

Provides cryptographic vault validation using:
- Merkle trees for file integrity
- Zero-knowledge proofs for constitutional compliance

Usage:
    from arifos.core.zkpc import VaultSealManager

    # Create and verify seals
    manager = VaultSealManager("vault_999")
    seal = manager.create_seal("v50.0.0", {"F1": "PASS", "F2": "PASS"})
    is_valid = manager.verify_seal(seal)
"""

from .merkle_vault import (
    SimpleMerkleTree,
    VaultMerkleValidator,
    MerkleProof
)

from .constitutional_zkpc import (
    ConstitutionalZKPC,
    VaultZKPCValidator,
    FloorProof,
    ConstitutionalProof
)

from .vault_seal_integration import VaultSealManager

__all__ = [
    # Merkle components
    "SimpleMerkleTree",
    "VaultMerkleValidator",
    "MerkleProof",

    # ZKPC components
    "ConstitutionalZKPC",
    "VaultZKPCValidator",
    "FloorProof",
    "ConstitutionalProof",

    # Integration
    "VaultSealManager"
]

__version__ = "1.0.0"
__author__ = "arifOS Constitutional Engineering"

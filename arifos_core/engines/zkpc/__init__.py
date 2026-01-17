"""
zkPC (Zero-Knowledge Proof of Cognition) Engine

Constitutional Integration:
- Generates cryptographic receipts for SEAL verdicts
- Creates Merkle commitment chains for external audit
- Verifies constitutional compliance (F1-F12)
- Enables "trust but verify" governance
"""
from arifos_core.engines.zkpc.receipt_generator import (
    ReceiptGenerator,
    ZKPCReceiptV47,
    FloorVerification,
    TriWitnessConsensus
)
from arifos_core.engines.zkpc.merkle_tree import MerkleTree
from arifos_core.engines.zkpc.proof_verifier import ProofVerifier

__all__ = [
    "ReceiptGenerator",
    "ZKPCReceiptV47",
    "FloorVerification",
    "TriWitnessConsensus",
    "MerkleTree",
    "ProofVerifier",
]

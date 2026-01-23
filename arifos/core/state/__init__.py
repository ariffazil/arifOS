"""
arifOS Core State Management (v47)

This module handles persistent state and ledger functionality:
- Ledger: Cryptographic audit trail (tamper-evident, append-only)
- Merkle: Tree structures for batch verification
- Hashing: Canonical hashing and chain utilities

Extracted from apex/governance/ as part of v47 Equilibrium Architecture
to achieve thermodynamic separation of concerns (ΔS reduction).

Design principle: State (what happened) ≠ Governance (what should happen)
"""

# Re-export key components for backward compatibility
from .ledger_cryptography import (
    CryptographicLedger,
    LedgerEntry,
    canonical_json,
    sha3_256_hex,
    VerificationReport,
    TamperReport,
)
from .ledger_hashing import (
    sha256_hex,
    compute_entry_hash,
    verify_chain,
    load_jsonl,
    dump_jsonl,
    HASH_FIELD,
    PREVIOUS_HASH_FIELD,
    GENESIS_PREVIOUS_HASH,
)
from .merkle import (
    MerkleTree,
    MerkleProofItem,
    build_merkle_tree,
    get_merkle_proof,
    verify_merkle_proof,
)
from .merkle_ledger import (
    MerkleLedger,
    MerkleEntry,
)
from .ledger import (
    log_cooling_entry,
)

__all__ = [
    # Cryptographic Ledger
    "CryptographicLedger",
    "LedgerEntry",
    "canonical_json",
    "sha3_256_hex",
    "VerificationReport",
    "TamperReport",
    # Hashing
    "sha256_hex",
    "compute_entry_hash",
    "verify_chain",
    "load_jsonl",
    "dump_jsonl",
    "HASH_FIELD",
    "PREVIOUS_HASH_FIELD",
    "GENESIS_PREVIOUS_HASH",
    # Merkle
    "MerkleTree",
    "MerkleProofItem",
    "build_merkle_tree",
    "get_merkle_proof",
    "verify_merkle_proof",
    # Merkle Ledger
    "MerkleLedger",
    "MerkleEntry",
    # Ledger operations
    "log_cooling_entry",
]

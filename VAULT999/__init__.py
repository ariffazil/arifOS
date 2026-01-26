"""
VAULT999 - Constitutional Memory Seal
The Final Tool of the 5-Tool Trinity

DITEMPA BUKAN DIBERI - Forged, Not Given

This module is the SINGLE SOURCE OF TRUTH for all vault-related functionality.
All other code MUST import from here. Duplicates are forbidden.

Structure:
    VAULT999/
    ├── __init__.py        # This file - exports all symbols
    ├── stage_999.py       # Consolidated canonical implementation
    ├── README.md          # Documentation
    ├── AAA_HUMAN/         # Sacred human memory (FORBIDDEN to AI)
    ├── BBB_LEDGER/        # Audit trail (READ/WRITE constrained)
    └── CCC_CANON/         # Constitutional law (READ ONLY)

Version: v52.5.2-CANONICAL
Authority: Muhammad Arif bin Fazil
Sealed: 2026-01-26
"""

from .stage_999 import (
    # Constants
    DEFAULT_LEDGER_PATH,
    DEFAULT_VAULT_PATH,
    PHOENIX_72_HOURS,
    VERDICT_TTL,

    # Routing
    VerdictRoute,
    route_verdict,

    # Merkle Ledger
    MerkleEntry,
    MerkleLedger,

    # Cooling Ledger
    CoolingMetrics,
    CoolingEntry,
    LedgerConfig,
    CoolingLedger,

    # Hash-Chain Functions
    compute_hash,
    append_entry,
    verify_chain,

    # Vault999
    VaultConfig,
    VaultInitializationError,
    Vault999,
    amendment_timestamp,

    # VaultManager
    SafetyConstraints,
    AmendmentEvidence,
    AmendmentRecord,
    AmendmentStatus,
    VaultManagerConfig,
    VaultManager,

    # Stage 999
    Stage999Result,
    execute_stage_999,
    execute_stage,

    # Singleton
    vault_999,
)

__all__ = [
    # Constants
    "DEFAULT_LEDGER_PATH",
    "DEFAULT_VAULT_PATH",
    "PHOENIX_72_HOURS",
    "VERDICT_TTL",

    # Routing
    "VerdictRoute",
    "route_verdict",

    # Merkle Ledger
    "MerkleEntry",
    "MerkleLedger",

    # Cooling Ledger
    "CoolingMetrics",
    "CoolingEntry",
    "LedgerConfig",
    "CoolingLedger",

    # Hash-Chain Functions
    "compute_hash",
    "append_entry",
    "verify_chain",

    # Vault999
    "VaultConfig",
    "VaultInitializationError",
    "Vault999",
    "amendment_timestamp",

    # VaultManager
    "SafetyConstraints",
    "AmendmentEvidence",
    "AmendmentRecord",
    "AmendmentStatus",
    "VaultManagerConfig",
    "VaultManager",

    # Stage 999
    "Stage999Result",
    "execute_stage_999",
    "execute_stage",

    # Singleton
    "vault_999",
]

__version__ = "v52.5.2-CANONICAL"
__author__ = "Muhammad Arif bin Fazil"
__motto__ = "DITEMPA BUKAN DIBERI"

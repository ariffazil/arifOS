"""
arifOS Memory Stack — v37 Implementation

This package implements the 6-band memory architecture per:
- v36.3O/canon/ARIFOS_MEMORY_STACK_v36.3O.md
- v36.3O/spec/memory_context_spec_v36.3O.json

Memory Bands:
- ENV: Session-local environment variables
- VLT: Read-only constitution snapshot (VAULT-999)
- LDG: Cooling Ledger (append-only audit trail)
- ACT: Working scratchpad for current task
- VEC: Optional vector similarity index (scars, precedents)
- VOID: Void scanner results (pending actions)

Additional Components:
- VaultManager: Enhanced VAULT-999 with Phoenix-72 amendment workflow
- ScarManager: Witness/scar lifecycle management
- Phoenix72Controller: Amendment proposal and finalization
- EurekaReceiptManager: zkPC receipt generation (L4 layer)

Author: arifOS Project
Version: v37
"""

# Core memory context
from .memory_context import (
    MemoryContext,
    EnvBand,
    VaultBand,
    LedgerBand,
    ActiveStreamBand,
    VectorBand,
    VoidBand,
    create_memory_context,
    validate_memory_context,
)

# Cooling Ledger (L1)
from .cooling_ledger import (
    CoolingLedger,
    CoolingLedgerV37,
    CoolingEntry,
    CoolingMetrics,
    LedgerConfig,
    LedgerConfigV37,
    HeadState,
    append_entry,
    verify_chain,
    log_cooling_entry,
    log_cooling_entry_v37,
)

# VAULT-999 (L0-L4)
from .vault999 import (
    Vault999,
    VaultConfig,
    VaultInitializationError,
)

from .vault_manager import (
    VaultManager,
    VaultManagerConfig,
    AmendmentRecord,
    AmendmentEvidence,
    SafetyConstraints,
)

# Scars & Witnesses
from .scars import (
    Scar,
    ScarIndex,
    ScarIndexConfig,
    stub_embed,
    cosine_similarity,
    generate_scar_id,
)

from .scar_manager import (
    ScarManager,
    ScarManagerConfig,
    ScarRecord,
    WitnessRecord,
    ScarEvidence,
    SEVERITY_WEIGHTS,
)

# Phoenix-72 (Amendment Controller)
from .phoenix72 import Phoenix72

from .phoenix72_controller import (
    Phoenix72Controller,
    Phoenix72Config,
    PressureReport,
    ProposalResult,
    FinalizeResult,
    compute_floor_pressure,
    compute_all_floor_pressures,
    compute_suggested_delta,
    MAX_THRESHOLD_DELTA,
    COOLDOWN_WINDOW_HOURS,
    PRESSURE_MIN,
    PRESSURE_MAX,
    PROTECTED_FLOORS,
)

# EUREKA (zkPC L4)
from .eureka_receipt import (
    EurekaReceiptManager,
    EurekaConfig,
    EurekaReceipt,
    CareScope,
    FloorProofs,
    CCEProofs,
    TriWitnessScores,
    MerkleState,
    generate_eureka_receipt,
)

# Vector Adapter
from .vector_adapter import VectorAdapter, WitnessHit

# Void Scanner
from .void_scanner import VoidScanner, ScarCandidate, ScarProposal


__all__ = [
    # Memory Context
    "MemoryContext",
    "EnvBand",
    "VaultBand",
    "LedgerBand",
    "ActiveStreamBand",
    "VectorBand",
    "VoidBand",
    "create_memory_context",
    "validate_memory_context",
    # Cooling Ledger
    "CoolingLedger",
    "CoolingLedgerV37",
    "CoolingEntry",
    "CoolingMetrics",
    "LedgerConfig",
    "LedgerConfigV37",
    "HeadState",
    "append_entry",
    "verify_chain",
    "log_cooling_entry",
    "log_cooling_entry_v37",
    # Vault
    "Vault999",
    "VaultConfig",
    "VaultInitializationError",
    "VaultManager",
    "VaultManagerConfig",
    "AmendmentRecord",
    "AmendmentEvidence",
    "SafetyConstraints",
    # Scars
    "Scar",
    "ScarIndex",
    "ScarIndexConfig",
    "stub_embed",
    "cosine_similarity",
    "generate_scar_id",
    "ScarManager",
    "ScarManagerConfig",
    "ScarRecord",
    "WitnessRecord",
    "ScarEvidence",
    "SEVERITY_WEIGHTS",
    # Phoenix-72
    "Phoenix72",
    "Phoenix72Controller",
    "Phoenix72Config",
    "PressureReport",
    "ProposalResult",
    "FinalizeResult",
    "compute_floor_pressure",
    "compute_all_floor_pressures",
    "compute_suggested_delta",
    "MAX_THRESHOLD_DELTA",
    "COOLDOWN_WINDOW_HOURS",
    "PRESSURE_MIN",
    "PRESSURE_MAX",
    "PROTECTED_FLOORS",
    # EUREKA
    "EurekaReceiptManager",
    "EurekaConfig",
    "EurekaReceipt",
    "CareScope",
    "FloorProofs",
    "CCEProofs",
    "TriWitnessScores",
    "MerkleState",
    "generate_eureka_receipt",
    # Vector & Void
    "VectorAdapter",
    "WitnessHit",
    "VoidScanner",
    "ScarCandidate",
    "ScarProposal",
]

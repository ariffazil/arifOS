"""
arifOS Memory Stack — v38 Implementation

This package implements the 6-band memory architecture per:
- archive/versions/v36_3_omega/v36.3O/canon/ARIFOS_MEMORY_STACK_v36.3O.md
- archive/versions/v36_3_omega/v36.3O/spec/memory_context_spec_v36.3O.json
- docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md (v38)

Memory Bands:
- VAULT: Read-only constitution snapshot (VAULT-999) - PERMANENT
- LEDGER: Cooling Ledger (append-only audit trail) - WARM tier
- ACTIVE: Working scratchpad for current task - HOT tier
- PHOENIX: Amendment proposals pending review - WARM tier
- WITNESS: Soft evidence collection - WARM tier
- VOID: Diagnostic only (never canonical) - 90-day retention

v38 Additions:
- MemoryWritePolicy: Verdict-based write gating
- MemoryBandRouter: Smart routing across bands
- MemoryAuthorityCheck: Human seal enforcement
- MemoryAuditLayer: Hash-chain integrity verification
- MemoryRetentionManager: Hot/Warm/Cold lifecycle

Core Invariants (v38):
1. VOID verdicts NEVER become canonical memory
2. Authority boundary: humans seal law, AI proposes
3. Every write must be auditable (evidence chain)
4. Recalled memory passes floor checks (suggestion, not fact)

Author: arifOS Project
Version: v38
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

# ============================================================================
# v38.2-alpha L7 MEMORY LAYER (Mem0 + Qdrant)
# ============================================================================

# Mem0 Client
from .mem0_client import (
    Mem0Client,
    Mem0Config,
    MemoryHit,
    EmbedResult,
    SearchResult as Mem0SearchResult,
    StoreResult as Mem0StoreResult,
    TTLPolicy,
    get_mem0_client,
    is_l7_enabled,
    is_l7_available,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TOP_K,
)

# L7 Memory Layer
from .memory import (
    Memory,
    RecallResult,
    SieveResult,
    StoreAtSealResult,
    get_memory,
    recall_at_stage_111,
    store_at_stage_999,
    apply_eureka_sieve,
    RECALL_CONFIDENCE_CEILING,
    MAX_RECALL_ENTRIES,
    STORABLE_VERDICTS,
    DISCARD_VERDICTS,
)

# ============================================================================
# v38 MEMORY WRITE POLICY ENGINE
# ============================================================================

# Memory Write Policy (v38)
from .policy import (
    Verdict,
    MemoryBandTarget,
    WriteDecision,
    RecallDecision,
    RetentionDecision,
    EvidenceChainValidation,
    MemoryWritePolicy,
    VERDICT_BAND_ROUTING,
    RETENTION_HOT_DAYS,
    RETENTION_WARM_DAYS,
    RETENTION_COLD_DAYS,
    RETENTION_VOID_DAYS,
)

# Memory Bands Router (v38)
from .bands import (
    BandName,
    MemoryBand,
    MemoryEntry,
    WriteResult,
    QueryResult,
    VaultBand as VaultBandV38,
    CoolingLedgerBand,
    ActiveStreamBand as ActiveStreamBandV38,
    PhoenixCandidatesBand,
    WitnessBand,
    VoidBandStorage,
    MemoryBandRouter,
    BAND_PROPERTIES,
    WRITER_PERMISSIONS,
)

# Memory Authority (v38)
from .authority import (
    MemoryAuthorityViolation,
    HumanApprovalRequiredError,
    SelfModificationError,
    AuthorityDecision,
    MemoryAuthorityCheck,
)

# Memory Audit Layer (v38)
from .audit import (
    AuditRecord,
    ChainVerificationResult,
    MerkleProof,
    MemoryAuditLayer,
    compute_evidence_hash,
    verify_evidence_hash,
)

# Memory Retention Manager (v38)
from .retention import (
    RetentionTier,
    RetentionConfig,
    RetentionAction,
    RetentionReport,
    BandStatus,
    MemoryRetentionManager,
    compute_entry_age_days,
    should_delete_void_entry,
    get_tier_for_band,
    DEFAULT_RETENTION_DAYS,
    BAND_TIER_MAP,
    BAND_TRANSITIONS,
)

# ============================================================================
# v38.3Omega EUREKA Phase-1 Memory Engine
# ============================================================================

from .eureka_types import (
    ActorRole,
    MemoryBand as EurekaMemoryBand,
    Verdict as EurekaVerdict,
    MemoryWriteRequest,
    MemoryWriteDecision,
)

from .eureka_router import (
    route_write,
)

from .eureka_store import (
    AppendOnlyJSONLStore,
    InMemoryStore,
)


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
    # ===== v38 Memory Write Policy Engine =====
    # Policy
    "Verdict",
    "MemoryBandTarget",
    "WriteDecision",
    "RecallDecision",
    "RetentionDecision",
    "EvidenceChainValidation",
    "MemoryWritePolicy",
    "VERDICT_BAND_ROUTING",
    "RETENTION_HOT_DAYS",
    "RETENTION_WARM_DAYS",
    "RETENTION_COLD_DAYS",
    "RETENTION_VOID_DAYS",
    # Bands (v38)
    "BandName",
    "MemoryBand",
    "MemoryEntry",
    "WriteResult",
    "QueryResult",
    "VaultBandV38",
    "CoolingLedgerBand",
    "ActiveStreamBandV38",
    "PhoenixCandidatesBand",
    "WitnessBand",
    "VoidBandStorage",
    "MemoryBandRouter",
    "BAND_PROPERTIES",
    "WRITER_PERMISSIONS",
    # Authority
    "MemoryAuthorityViolation",
    "HumanApprovalRequiredError",
    "SelfModificationError",
    "AuthorityDecision",
    "MemoryAuthorityCheck",
    # Audit
    "AuditRecord",
    "ChainVerificationResult",
    "MerkleProof",
    "MemoryAuditLayer",
    "compute_evidence_hash",
    "verify_evidence_hash",
    # Retention
    "RetentionTier",
    "RetentionConfig",
    "RetentionAction",
    "RetentionReport",
    "BandStatus",
    "MemoryRetentionManager",
    "compute_entry_age_days",
    "should_delete_void_entry",
    "get_tier_for_band",
    "DEFAULT_RETENTION_DAYS",
    "BAND_TIER_MAP",
    "BAND_TRANSITIONS",
    # ===== v38.2-alpha L7 MEMORY LAYER =====
    # Mem0 Client
    "Mem0Client",
    "Mem0Config",
    "MemoryHit",
    "EmbedResult",
    "Mem0SearchResult",
    "Mem0StoreResult",
    "TTLPolicy",
    "get_mem0_client",
    "is_l7_enabled",
    "is_l7_available",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_TOP_K",
    # L7 Memory Layer
    "Memory",
    "RecallResult",
    "SieveResult",
    "StoreAtSealResult",
    "get_memory",
    "recall_at_stage_111",
    "store_at_stage_999",
    "apply_eureka_sieve",
    "RECALL_CONFIDENCE_CEILING",
    "MAX_RECALL_ENTRIES",
    "STORABLE_VERDICTS",
    "DISCARD_VERDICTS",
    # ===== v38.3Omega EUREKA Phase-1 =====
    "ActorRole",
    "EurekaMemoryBand",
    "EurekaVerdict",
    "MemoryWriteRequest",
    "MemoryWriteDecision",
    "route_write",
    "AppendOnlyJSONLStore",
    "InMemoryStore",
]

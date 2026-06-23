"""
arifOS Canonical Output Schemas (v2026.04.26-KANON)
═══════════════════════════════════════════════════

Phase 2 Civilization Intelligence:
- 888_JUDGE: VerdictOutput with ToAC, ThermodynamicState,
  DecisionCollapse, GrowthParadox, AKAL, AmanahProof
- 999_VAULT: SealOutput with IrreversibilityBond, EntropyDelta,
  EpistemicSnapshot
- 333_MIND: MindOutput with AxiomsUsed, Metrics, ReasoningTrace
- 222_FETCH: Sequential thinking schemas
- 010_FORGE: ForgeOutput with IrreversibilityFlag, DeltaSEvidence
- 444_KERNEL: KernelMetrics with stage trajectory
- 777_OPS: WEALTH metrics with Landauer, psi_le, omega
- 114_INGEST: CanonicalEvidenceBundle + IngestResult + ClaimSchema
  (Phase 1 SENSE-INGEST pipeline)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

# CapabilitySurface — Honest map of what the system can actually do (Ω-2026-06-10)
from arifosmcp.schemas.capability_surface import (
    AgentCapability,
    AutonomyMode,
    CapabilitySurface,
    CapabilityTier,
    OrganHealth,
    StatusAlignment,
    ToolCapability,
)

# Sequential thinking (222_SENSE)
from arifosmcp.schemas.cognition import (
    EpistemicHumility,
    EvidenceCivilizationContext,
    EvidenceOutput,
    RealityAnchor,
    ReasoningQuality,
    ResourceMetrics,
    ThinkingMode,
    ThinkingOutcome,
    ThinkingSequence,
    ThinkingStep,
    UncertaintyGeometry,
)

# Forge (010_FORGE)
from arifosmcp.schemas.forge import (
    ConstitutionalCompliance,
    DeltaSEvidence,
    ExecutionNode,
    ExecutionTrace,
    ForgeEnvelope,
    ForgeManifest,
    ForgeOutput,
    IrreversibilityBond,
    IrreversibilityLevel,
    ManifestStatus,
)

# Gateway (666g_GATEWAY)
from arifosmcp.schemas.gateway import GatewayBlock

# Intent Envelope v1 — Atomic authorization object (F1/F11/F13 enforcement)
# Ratified 2026-06-06. Kernel rule: "AI may generate. Humans must authorize consequence."
from arifosmcp.schemas.intent_envelope import (
    DisplayCard,
    IntentEnvelopeV1,
    ProvenanceClass,
    Reversibility,
    RiskClass,
    SovereignProvenance,
)

# Verdict (888_JUDGE, 999_VAULT, 666_HEART)
from arifosmcp.schemas.lineage import JudgeSealContract

# Memory (555_MEMORY)
from arifosmcp.schemas.memory import MemoryBlock

# Memory Kernel v5 — Direction 1, ratified 2026-06-21
# Federated arif_memory tool: 7 modes × 13 floors × 7 truth-classes × 6 tiers
# 555_MEMORY v5 — supersedes legacy MemoryBlock + arif_memory_recall v4 (8 modes)
from arifosmcp.schemas.memory_truth import (
    # Enums
    MemoryClass,
    TruthClass,
    # Type aliases
    MemoryClassName,
    TruthClassName,
    TierCode,
    # Functions
    tier_allowed,
    allowed_tiers,
    default_ttl_hours,
    default_recall_eligible,
    can_transition,
    legal_next,
    floors_required,
)
from arifosmcp.schemas.memory_modes import (
    MemoryMode,
    MemoryModeName,
    LEGACY_MODE_ALIASES,
    resolve_legacy_mode,
    MODE_ACTION_CLASS,
    MODE_PRE_FLOORS,
    MODE_POST_FLOORS,
    MODE_REQUIRES_LEASE,
    MODE_REQUIRES_HUMAN_ACK,
    MODE_BACKEND_TARGET,
    MODE_STAGE,
)
from arifosmcp.schemas.memory_object import (
    SourceReceipt,
    ProvenanceBlock,
    EpistemicsBlock,
    PolicyBlock,
    MemoryObject,
    ReceiptEnvelope,
    MemoryResultEnvelope,
    compute_call_hash,
)
from arifosmcp.schemas.memory_payload import (
    RecallPayload,
    InspectPayload,
    AttestPayload,
    RememberPayload,
    PromotePayload,
    RevisePayload,
    ForgetPayload,
    MemoryPayload,
    MemoryToolRequest,
)

# ModelCard (F3 TRI_WITNESS — identity binding)
from arifosmcp.schemas.model_card import (
    ModelAnchor,
    ModelGovernanceCard,
    RiskLeash,
    RuntimeTruth,
    SelfClaimBoundary,
    ShadowProfile,
)

# Peer Federation Contract v1 (P2P constitutional peering)
from arifosmcp.schemas.peer_federation_contract import (
    AcceptedInput,
    AuditSink,
    AuthorityClass,
    CapabilityCard,
    HumanVeto,
    OverridePath,
    PeerFederationContract,
    PeerId,
    SignedAttestation,
)

# Session (000_INIT)
from arifosmcp.schemas.session import SessionManifest, SessionState

# Synthesis (333_MIND, 444r_REPLY, 222_FETCH)
from arifosmcp.schemas.synthesis import (
    AxiomSource,
    AxiomsUsed,
    AxiomUsage,
    ContrastType,
    EvidenceBlock,
    MindAnomalousContrast,
    # 333_MIND MindOutput schemas
    MindOutput,
    ReasoningMode,
    ReasoningStep,
    ReasoningTrace,
    ReplyBlock,
    Synthesis,
)

# Telemetry (777_OPS, 111_SENSE)
from arifosmcp.schemas.telemetry import TelemetryBlock, VitalsBlock

# Topology (777_OPS — Anti-Sink / Inclusive Topology diagnostics)
from arifosmcp.schemas.topology import (
    AntiSinkCheck,
    AppealPath,
    Confidence,
    Delta,
    InnovationRights,
    InstitutionalDrift,
    InstitutionalVerdict,
    ParticipationWidth,
    Presence,
    RiskBand,
    SovereigntyIntegrity,
    Strength,
)
from arifosmcp.schemas.topology import (
    Verdict as TopologyVerdict,
)

# Epistemic Tag (_epistemic response envelope — halal/haram boundary)
from arifosmcp.schemas.epistemic_tag import (
    AiInvolvement,
    AuthorityClaim,
    EpistemicTag,
    EvidenceSource,
    OutputClass,
    EPISTEMIC_AI_ADVISORY,
    EPISTEMIC_AI_FALLBACK,
    EPISTEMIC_DETERMINISTIC,
    EPISTEMIC_DOMAIN_ASSISTED,
    EPISTEMIC_DOMAIN_COMPUTATION,
    EPISTEMIC_GOVERNANCE_TEMPLATE,
    EPISTEMIC_MEASURED,
    EPISTEMIC_RETRIEVED,
    assert_tag_valid,
    validate_halal_haram,
)

# Vault Liveness (AAA-GOV-VAULT-LIVENESS-v1)
from arifosmcp.schemas.vault_liveness import (
    ContractEntry,
    ContractStatus,
    LivenessCheckResult,
    ProductionContractManifest,
    VaultLivenessContract,
    VaultLivenessState,
)
from arifosmcp.schemas.verdict import (
    AkalState,
    AmanahProof,
    # 888_JUDGE civilization schemas
    AnomalousContrast,
    CivilizationalAnchor,
    CritiqueReport,
    DecisionCollapse,
    DissentReasoning,
    EntropyDelta,
    EpistemicSnapshot,
    FloorComplianceProof,
    GrowthParadox,
    # 999_VAULT seal schemas
    SealOutput,
    SealReceipt,
    ThermodynamicState,
    Verdict,
    VerdictCode,
    VerdictOutput,
    VerdictReport,
)

__all__ = [
    # Topology (777_OPS — Anti-Sink / Inclusive Topology diagnostics)
    "AntiSinkCheck",
    "InstitutionalDrift",
    "TopologyVerdict",
    "Delta",
    "Strength",
    "RiskBand",
    "Confidence",
    "Presence",
    "ParticipationWidth",
    "InnovationRights",
    "AppealPath",
    "SovereigntyIntegrity",
    "InstitutionalVerdict",
    # Session (000_INIT)
    "SessionManifest",
    "SessionState",
    # Verdict (888_JUDGE, 999_VAULT, 666_HEART)
    "Verdict",
    "VerdictCode",
    "VerdictReport",
    "CritiqueReport",
    "SealReceipt",
    "JudgeSealContract",
    # 888_JUDGE + 999_VAULT civilization intelligence
    "AnomalousContrast",
    "ThermodynamicState",
    "DecisionCollapse",
    "GrowthParadox",
    "AkalState",
    "AmanahProof",
    "FloorComplianceProof",
    "DissentReasoning",
    "CivilizationalAnchor",
    "VerdictOutput",
    "SealOutput",
    "EntropyDelta",
    "EpistemicSnapshot",
    # Telemetry (777_OPS, 111_SENSE)
    "TelemetryBlock",
    "VitalsBlock",
    # Forge (010_FORGE)
    "ForgeManifest",
    "ForgeEnvelope",
    "ForgeOutput",
    "ExecutionNode",
    "ExecutionTrace",
    "ConstitutionalCompliance",
    "DeltaSEvidence",
    "IrreversibilityBond",
    "IrreversibilityLevel",
    "ManifestStatus",
    # Synthesis (333_MIND, 444r_REPLY, 222_FETCH)
    "Synthesis",
    "ReplyBlock",
    "EvidenceBlock",
    "MindOutput",
    "ReasoningMode",
    "AxiomSource",
    "ContrastType",
    "AxiomUsage",
    "AxiomsUsed",
    "ReasoningStep",
    "ReasoningTrace",
    "MindAnomalousContrast",
    # Memory (555_MEMORY)
    "MemoryBlock",
    # Memory Kernel v5 — Direction 1, ratified 2026-06-21
    # Truth-class taxonomy
    "TruthClass",
    "MemoryClass",
    "TruthClassName",
    "MemoryClassName",
    "TierCode",
    "tier_allowed",
    "allowed_tiers",
    "default_ttl_hours",
    "default_recall_eligible",
    "can_transition",
    "legal_next",
    "floors_required",
    # Mode enum + metadata
    "MemoryMode",
    "MemoryModeName",
    "LEGACY_MODE_ALIASES",
    "resolve_legacy_mode",
    "MODE_ACTION_CLASS",
    "MODE_PRE_FLOORS",
    "MODE_POST_FLOORS",
    "MODE_REQUIRES_LEASE",
    "MODE_REQUIRES_HUMAN_ACK",
    "MODE_BACKEND_TARGET",
    "MODE_STAGE",
    # MemoryObject + receipts
    "SourceReceipt",
    "ProvenanceBlock",
    "EpistemicsBlock",
    "PolicyBlock",
    "MemoryObject",
    "ReceiptEnvelope",
    "MemoryResultEnvelope",
    "compute_call_hash",
    # Per-mode payloads
    "RecallPayload",
    "InspectPayload",
    "AttestPayload",
    "RememberPayload",
    "PromotePayload",
    "RevisePayload",
    "ForgetPayload",
    "MemoryPayload",
    "MemoryToolRequest",
    # Gateway (666g_GATEWAY)
    "GatewayBlock",
    # Intent Envelope v1 (F1/F11/F13 atomic authorization)
    "DisplayCard",
    "IntentEnvelopeV1",
    "ProvenanceClass",
    "Reversibility",
    "RiskClass",
    "SovereignProvenance",
    # Sequential thinking (222_SENSE)
    "ThinkingStep",
    "ThinkingSequence",
    "ThinkingMode",
    "ThinkingOutcome",
    "ReasoningQuality",
    "ResourceMetrics",
    "RealityAnchor",
    "EvidenceOutput",
    "UncertaintyGeometry",
    "EvidenceCivilizationContext",
    "EpistemicHumility",
    # EvidenceBundle (111_SENSE → 114_INGEST pipeline)
    "CanonicalEvidenceBundle",
    "IngestResult",
    "ClaimSchema",
    "EntitySchema",
    "RelationSchema",
    "ReceiptSchema",
    "EvidenceLevel",
    "IngestStatus",
    # Budget Contract (AAA-GOV-BUDGET-v1)
    "BudgetContractSchema",
    "BudgetDomain",
    "DomainLimit",
    "ViolationPolicy",
    # Epistemic Tag (_epistemic response envelope)
    "EpistemicTag",
    "OutputClass",
    "AiInvolvement",
    "AuthorityClaim",
    "EvidenceSource",
    "EPISTEMIC_DETERMINISTIC",
    "EPISTEMIC_GOVERNANCE_TEMPLATE",
    "EPISTEMIC_AI_ADVISORY",
    "EPISTEMIC_AI_FALLBACK",
    "EPISTEMIC_DOMAIN_COMPUTATION",
    "EPISTEMIC_DOMAIN_ASSISTED",
    "EPISTEMIC_MEASURED",
    "EPISTEMIC_RETRIEVED",
    "assert_tag_valid",
    "validate_halal_haram",
    # Vault Liveness (AAA-GOV-VAULT-LIVENESS-v1)
    "VaultLivenessContract",
    "VaultLivenessState",
    "LivenessCheckResult",
    "ContractStatus",
    "ContractEntry",
    "ProductionContractManifest",
    # Peer Federation Contract v1
    "PeerFederationContract",
    "AuthorityClass",
    "PeerId",
    "CapabilityCard",
    "AcceptedInput",
    "AuditSink",
    "OverridePath",
    "HumanVeto",
    "SignedAttestation",
    # ModelCard (F3 TRI_WITNESS — identity binding)
    "ModelGovernanceCard",
    "ModelAnchor",
    "RuntimeTruth",
    "SelfClaimBoundary",
    "ShadowProfile",
    "RiskLeash",
]

# ── Minimum Constitutional Kernel (F13 Forged) ───────────────────────────────
from .reversibility import ReversibilityClass
from .truth_state import TruthState
from .minimum_kernel import KernelInput, KernelOutput

__all__.extend(
    [
        "ReversibilityClass",
        "TruthState",
        "KernelInput",
        "KernelOutput",
    ]
)

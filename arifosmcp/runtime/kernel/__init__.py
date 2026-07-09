"""
arifOS Kernel — Constitutional Governance Physics

Physics computes. Kernel governs. Agent acts. Receipt remembers. Sovereign decides.

Architecture:
  Python kernel  = judge      — ΔΩΨ, 000-999, 6 tripwires, source-weighted collapse
  TypeScript     = executor   — A-FORGE hands (forge_* tools)
  Quantum        = calculator — GEOX/WEALTH backend, never kernel, never judge
  VAULT999       = memory     — immutable seal chain
  AAA            = cockpit    — state display, intent routing

This module implements the formal kernel ONLY:
  - Δ (entropy/pressure), Ω (uncertainty), Ψ (integrity)
  - 000-999 metabolic pipeline
  - 6 tripwires at 888
  - Source-weighted evidence fusion
  - VAULT999 seal chain
  - Governance contracts for external compute (quantum, etc.)

No domain physics. No solver code. No execution logic.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from .types import (
    UncertaintyTag,
    Verdict,
    Phase,
    EvidenceItem,
    SourceConsensus,
    GovernanceScalars,
    CollapseResult,
    EvidenceFusion,
    TripwireResult,
    TripwireId,
    GovernanceState,
    Organ,
    OMEGA_MAX,
    PSI_MIN,
    DELTA_CRITICAL,
    OMEGA_WARN,
    OMEGA_HARD_LIMIT,
    PHASES,
    PHASE_LABELS,
    PHASE_ORDER,
    SOURCE_WEIGHTS,
    BLAST_WEIGHTS,
    BlastRadius,
    RiskProfile,
)

from .compute import (
    compute_delta,
    compute_omega,
    compute_psi,
    compute_source_consensus,
    compute_scalars,
)

from .judge import judge, judge_with_reason

from .pipeline import (
    ingest_intent,
    ingest_evidence,
    think,
    critique,
    prepare_action,
    run_judge,
    cool,
    pipeline_seal,
    run_pipeline,
    validate_transition,
    PhaseTransitionError,
    PipelineResult,
)

from .seal import (
    SealRecord,
    SealChain,
    seal,
    empty_chain,
    append_to_chain,
    verify_chain,
)

# ── Governance Contracts (not execution) ──
from .contracts import (
    QuantumComputeReceipt,
    QuantumEvidenceFloor,
    QuantumReversibility,
    QUANTUM_ADAPTER_CONTRACT,
    validate_receipt,
    BackendClass,
    EvidenceRank,
)

__all__ = [
    # Types
    "UncertaintyTag",
    "Verdict",
    "Phase",
    "EvidenceItem",
    "SourceConsensus",
    "GovernanceScalars",
    "CollapseResult",
    "EvidenceFusion",
    "TripwireResult",
    "TripwireId",
    "GovernanceState",
    "Organ",
    "BlastRadius",
    "RiskProfile",
    # Constants
    "OMEGA_MAX",
    "PSI_MIN",
    "DELTA_CRITICAL",
    "OMEGA_WARN",
    "OMEGA_HARD_LIMIT",
    "PHASES",
    "PHASE_LABELS",
    "PHASE_ORDER",
    "SOURCE_WEIGHTS",
    "BLAST_WEIGHTS",
    # Compute
    "compute_delta",
    "compute_omega",
    "compute_psi",
    "compute_source_consensus",
    "compute_scalars",
    # Judge
    "judge",
    "judge_with_reason",
    # Pipeline
    "ingest_intent",
    "ingest_evidence",
    "think",
    "critique",
    "prepare_action",
    "run_judge",
    "cool",
    "pipeline_seal",
    "run_pipeline",
    "validate_transition",
    "PhaseTransitionError",
    "PipelineResult",
    # Seal
    "SealRecord",
    "SealChain",
    "seal",
    "empty_chain",
    "append_to_chain",
    "verify_chain",
    # Governance Contracts
    "QuantumComputeReceipt",
    "QuantumEvidenceFloor",
    "QuantumReversibility",
    "QUANTUM_ADAPTER_CONTRACT",
    "validate_receipt",
    "BackendClass",
    "EvidenceRank",
]

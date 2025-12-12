"""
arifOS Integration Layer — v38 Memory Integration

This package provides integration between the v38 Memory Write Policy Engine
and the 000-999 pipeline stages.

Integration Modules:
- memory_sense: 111_SENSE ↔ Memory (context loading, recall)
- memory_judge: 888_JUDGE ↔ Memory (write policy enforcement)
- memory_scars: 777_FORGE ↔ Scar Detection (pattern recognition)
- memory_seal: 999_SEAL ↔ Ledger Finalization (audit trail)
- common_utils: Shared utilities to reduce duplication

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md (v38)

Author: arifOS Project
Version: v38.0
"""

from .common_utils import (
    compute_integration_evidence_hash,
)

from .memory_sense import (
    MemorySenseIntegration,
    RecallContext,
    SenseRecallResult,
    sense_load_cross_session_memory,
    sense_inject_context,
    sense_should_recall_from_vault,
    sense_compute_recall_confidence,
    sense_log_recall_decision,
)

from .memory_judge import (
    MemoryJudgeIntegration,
    JudgeWriteContext,
    JudgeWriteResult,
    judge_compute_evidence_hash,
    judge_check_write_policy,
    judge_route_to_band,
    judge_record_audit,
    judge_enforce_authority,
)

from .memory_scars import (
    MemoryScarsIntegration,
    ScarDetectionContext,
    ScarDetectionResult,
    scars_detect_pattern,
    scars_should_create_scar,
    scars_propose_witness,
    scars_compute_severity,
    scars_log_detection,
)

from .memory_seal import (
    MemorySealIntegration,
    SealContext,
    SealResult,
    seal_finalize_to_ledger,
    seal_emit_eureka_receipt,
    seal_close_active_stream,
    seal_archive_void,
    seal_log_finalization,
)

__all__ = [
    # Common utilities
    "compute_integration_evidence_hash",
    # Memory Sense (111_SENSE)
    "MemorySenseIntegration",
    "RecallContext",
    "SenseRecallResult",
    "sense_load_cross_session_memory",
    "sense_inject_context",
    "sense_should_recall_from_vault",
    "sense_compute_recall_confidence",
    "sense_log_recall_decision",
    # Memory Judge (888_JUDGE)
    "MemoryJudgeIntegration",
    "JudgeWriteContext",
    "JudgeWriteResult",
    "judge_compute_evidence_hash",
    "judge_check_write_policy",
    "judge_route_to_band",
    "judge_record_audit",
    "judge_enforce_authority",
    # Memory Scars (777_FORGE)
    "MemoryScarsIntegration",
    "ScarDetectionContext",
    "ScarDetectionResult",
    "scars_detect_pattern",
    "scars_should_create_scar",
    "scars_propose_witness",
    "scars_compute_severity",
    "scars_log_detection",
    # Memory Seal (999_SEAL)
    "MemorySealIntegration",
    "SealContext",
    "SealResult",
    "seal_finalize_to_ledger",
    "seal_emit_eureka_receipt",
    "seal_close_active_stream",
    "seal_archive_void",
    "seal_log_finalization",
]

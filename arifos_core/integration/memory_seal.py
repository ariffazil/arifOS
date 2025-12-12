"""
memory_seal.py — 999_SEAL ↔ Ledger Finalization for arifOS v38

Provides integration between the 999_SEAL pipeline stage and the
v38 Memory Write Policy Engine for final ledger operations.

Key Functions:
- seal_finalize_to_ledger(): Finalize entry to Cooling Ledger
- seal_emit_eureka_receipt(): Emit cryptographic receipt
- seal_close_active_stream(): Close active stream for session
- seal_archive_void(): Archive void entries (90-day retention)
- seal_log_finalization(): Log finalization for audit

Core Concept:
The 999_SEAL stage is the final checkpoint where approved outputs are
committed to the immutable audit trail (Cooling Ledger). Once sealed,
entries cannot be modified—they become permanent institutional memory.

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md (v38)

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import logging

# v38 Memory imports
from ..memory.policy import (
    MemoryWritePolicy,
)
from ..memory.bands import (
    BandName,
    MemoryBandRouter,
    MemoryEntry,
    WriteResult,
)
from ..memory.audit import (
    MemoryAuditLayer,
)
from ..memory.retention import (
    MemoryRetentionManager,
)


logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

class SealStatus(str, Enum):
    """Status of a seal operation."""
    PENDING = "PENDING"          # Awaiting finalization
    SEALED = "SEALED"            # Successfully sealed to ledger
    REJECTED = "REJECTED"        # Rejected, not sealed
    VOID_ARCHIVED = "VOID_ARCHIVED"  # Archived to void (non-canonical)
    ERROR = "ERROR"              # Error during sealing


# Verdicts that can be sealed to ledger
SEALABLE_VERDICTS = frozenset([
    "SEAL",
    "PARTIAL",
    "888_HOLD",  # Can be sealed after human approval
])

# Verdicts that go to void archive
VOID_ARCHIVE_VERDICTS = frozenset([
    "VOID",
    "SABAR",
])

# Maximum entries to process in a single batch
MAX_BATCH_SIZE = 100


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SealContext:
    """Context for a seal operation."""
    entry_id: str
    verdict: str
    content: Dict[str, Any]
    evidence_hash: str
    floor_scores: Dict[str, float] = field(default_factory=dict)
    writer_id: str = "999_SEAL"
    session_id: Optional[str] = None
    human_approved: bool = False
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class EurekaReceipt:
    """Cryptographic receipt for a sealed entry."""
    receipt_id: str
    entry_id: str
    evidence_hash: str
    merkle_root: str
    merkle_proof: List[str]
    verdict: str
    floor_summary: Dict[str, float]
    sealed_at: str
    chain_index: int
    signature: str = ""  # Optional cryptographic signature

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "receipt_id": self.receipt_id,
            "entry_id": self.entry_id,
            "evidence_hash": self.evidence_hash,
            "merkle_root": self.merkle_root,
            "merkle_proof": self.merkle_proof,
            "verdict": self.verdict,
            "floor_summary": self.floor_summary,
            "sealed_at": self.sealed_at,
            "chain_index": self.chain_index,
            "signature": self.signature,
        }

    def verify(self) -> bool:
        """Verify the receipt against the merkle proof."""
        # Compute hash of entry
        entry_hash = self.evidence_hash

        # Walk up merkle proof
        current = entry_hash
        for sibling in self.merkle_proof:
            # Combine and hash (sorted order for consistency)
            combined = "".join(sorted([current, sibling]))
            current = hashlib.sha256(combined.encode()).hexdigest()

        # Should match merkle root
        return current == self.merkle_root


@dataclass
class SealResult:
    """Result of a seal operation."""
    success: bool
    status: SealStatus
    entry_id: str
    ledger_index: Optional[int] = None
    receipt: Optional[EurekaReceipt] = None
    reason: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def is_canonical(self) -> bool:
        """Check if sealed to canonical memory."""
        return self.status == SealStatus.SEALED


@dataclass
class SessionCloseResult:
    """Result of closing an active session."""
    session_id: str
    entries_sealed: int
    entries_voided: int
    entries_retained: int
    active_stream_cleared: bool
    reason: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class VoidArchiveResult:
    """Result of archiving void entries."""
    entries_archived: int
    entries_expired: int
    retention_days: int
    reason: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class SealLogEntry:
    """Log entry for seal operations."""
    timestamp: str
    entry_id: str
    verdict: str
    status: str
    ledger_index: Optional[int]
    has_receipt: bool
    reason: str


# =============================================================================
# MEMORY SEAL INTEGRATION CLASS
# =============================================================================

class MemorySealIntegration:
    """
    Integrates 999_SEAL stage with v38 Memory Write Policy Engine.

    Responsibilities:
    1. Finalize approved entries to Cooling Ledger
    2. Emit cryptographic receipts (EUREKA)
    3. Close active streams at session end
    4. Archive void entries with retention policy
    5. Log all finalization operations

    Usage:
        seal_integration = MemorySealIntegration(
            write_policy=MemoryWritePolicy(),
            band_router=MemoryBandRouter(),
            audit_layer=MemoryAuditLayer(),
        )

        # Finalize an entry
        result = seal_integration.finalize_to_ledger(
            SealContext(
                entry_id="entry-123",
                verdict="SEAL",
                content={"response": "..."},
                evidence_hash="abc123...",
            )
        )
    """

    def __init__(
        self,
        write_policy: Optional[MemoryWritePolicy] = None,
        band_router: Optional[MemoryBandRouter] = None,
        audit_layer: Optional[MemoryAuditLayer] = None,
        retention_manager: Optional[MemoryRetentionManager] = None,
    ):
        """
        Initialize the seal integration.

        Args:
            write_policy: Memory write policy
            band_router: Memory band router
            audit_layer: Audit layer
            retention_manager: Retention manager
        """
        self.write_policy = write_policy or MemoryWritePolicy(strict_mode=True)
        self.band_router = band_router or MemoryBandRouter()
        self.audit_layer = audit_layer or MemoryAuditLayer()
        self.retention_manager = retention_manager or MemoryRetentionManager()
        self._seal_log: List[SealLogEntry] = []
        self._chain_index = 0

    # =========================================================================
    # CORE SEAL METHODS
    # =========================================================================

    def finalize_to_ledger(
        self,
        context: SealContext,
    ) -> SealResult:
        """
        Finalize an entry to the Cooling Ledger.

        This is the critical operation that commits an approved entry
        to the immutable audit trail.

        Args:
            context: Seal context

        Returns:
            SealResult with outcome
        """
        # Check if verdict is sealable
        verdict_upper = context.verdict.upper()

        if verdict_upper in VOID_ARCHIVE_VERDICTS:
            # Void verdicts go to archive, not ledger
            return self._archive_to_void(context)

        if verdict_upper not in SEALABLE_VERDICTS:
            result = SealResult(
                success=False,
                status=SealStatus.REJECTED,
                entry_id=context.entry_id,
                reason=f"Verdict {context.verdict} is not sealable to ledger",
            )
            self._log_seal(context, result)
            return result

        # Check if 888_HOLD requires human approval
        if verdict_upper == "888_HOLD" and not context.human_approved:
            result = SealResult(
                success=False,
                status=SealStatus.PENDING,
                entry_id=context.entry_id,
                reason="888_HOLD verdict requires human approval before sealing",
            )
            self._log_seal(context, result)
            return result

        # Check write policy
        write_decision = self.write_policy.should_write(
            verdict=context.verdict,
            band=BandName.LEDGER.value,
            floor_scores=context.floor_scores,
            evidence_sources=[context.evidence_hash],
        )

        if not write_decision.allowed:
            result = SealResult(
                success=False,
                status=SealStatus.REJECTED,
                entry_id=context.entry_id,
                reason=write_decision.reason,
            )
            self._log_seal(context, result)
            return result

        # Build ledger entry
        entry = MemoryEntry(
            entry_id=context.entry_id,
            band=BandName.LEDGER.value,
            verdict=context.verdict,
            content=context.content,
            writer_id=context.writer_id,
            evidence_hash=context.evidence_hash,
            timestamp=context.timestamp,
            metadata={
                "floor_scores": context.floor_scores,
                "session_id": context.session_id,
                "sealed_at": datetime.now(timezone.utc).isoformat(),
                "chain_index": self._chain_index,
            },
        )

        # Write to ledger
        write_result = self.band_router.write(
            band=BandName.LEDGER,
            entry=entry,
            verdict=context.verdict,
            writer_id=context.writer_id,
        )

        if not write_result.success:
            result = SealResult(
                success=False,
                status=SealStatus.ERROR,
                entry_id=context.entry_id,
                reason=f"Failed to write to ledger: {write_result.reason}",
            )
            self._log_seal(context, result)
            return result

        # Record in audit layer
        self.audit_layer.record_write(
            entry_id=write_result.entry_id,
            band=BandName.LEDGER.value,
            verdict=context.verdict,
            evidence_hash=context.evidence_hash,
            writer_id=context.writer_id,
            floor_scores=context.floor_scores,
        )

        # Emit receipt
        receipt = self._emit_receipt(context, write_result)

        # Increment chain index
        self._chain_index += 1

        result = SealResult(
            success=True,
            status=SealStatus.SEALED,
            entry_id=write_result.entry_id,
            ledger_index=self._chain_index - 1,
            receipt=receipt,
            reason="Successfully sealed to ledger",
        )

        self._log_seal(context, result)

        return result

    def emit_eureka_receipt(
        self,
        context: SealContext,
        ledger_index: int,
    ) -> EurekaReceipt:
        """
        Emit a cryptographic receipt for a sealed entry.

        Args:
            context: Seal context
            ledger_index: Index in the ledger chain

        Returns:
            EurekaReceipt
        """
        # Get merkle proof from audit layer
        merkle_proof = self.audit_layer.get_merkle_proof(context.entry_id)

        # Generate receipt ID
        receipt_id = hashlib.sha256(
            f"{context.entry_id}:{context.evidence_hash}:{ledger_index}".encode()
        ).hexdigest()[:24]

        return EurekaReceipt(
            receipt_id=receipt_id,
            entry_id=context.entry_id,
            evidence_hash=context.evidence_hash,
            merkle_root=merkle_proof.root if merkle_proof else "",
            merkle_proof=merkle_proof.proof if merkle_proof else [],
            verdict=context.verdict,
            floor_summary=context.floor_scores,
            sealed_at=datetime.now(timezone.utc).isoformat(),
            chain_index=ledger_index,
        )

    def close_active_stream(
        self,
        session_id: str,
    ) -> SessionCloseResult:
        """
        Close the active stream for a session.

        This should be called at the end of each session to:
        1. Seal all approved entries to ledger
        2. Archive void entries
        3. Clear the active stream

        Args:
            session_id: Session ID to close

        Returns:
            SessionCloseResult
        """
        entries_sealed = 0
        entries_voided = 0
        entries_retained = 0

        # Query all entries in active stream for this session
        query_result = self.band_router.query(
            band=BandName.ACTIVE,
            query=f"session:{session_id}",
            limit=MAX_BATCH_SIZE,
        )

        for entry in query_result.entries:
            verdict_upper = entry.verdict.upper()

            if verdict_upper in SEALABLE_VERDICTS:
                # Seal to ledger
                context = SealContext(
                    entry_id=entry.entry_id,
                    verdict=entry.verdict,
                    content=entry.content,
                    evidence_hash=entry.evidence_hash,
                    floor_scores=entry.metadata.get("floor_scores", {}),
                    session_id=session_id,
                )
                result = self.finalize_to_ledger(context)
                if result.success:
                    entries_sealed += 1
                else:
                    entries_retained += 1

            elif verdict_upper in VOID_ARCHIVE_VERDICTS:
                # Archive to void
                entries_voided += 1

            else:
                # Retain in active for now
                entries_retained += 1

        return SessionCloseResult(
            session_id=session_id,
            entries_sealed=entries_sealed,
            entries_voided=entries_voided,
            entries_retained=entries_retained,
            active_stream_cleared=entries_retained == 0,
            reason=f"Session {session_id} closed: {entries_sealed} sealed, {entries_voided} voided",
        )

    def archive_void(
        self,
        max_age_days: int = 90,
    ) -> VoidArchiveResult:
        """
        Archive void entries and clean up expired ones.

        Void entries have 90-day retention by default.

        Args:
            max_age_days: Maximum age for void entries

        Returns:
            VoidArchiveResult
        """
        # Run retention on void band
        action = self.retention_manager.run_retention(
            band=BandName.VOID,
            max_age_days=max_age_days,
        )

        return VoidArchiveResult(
            entries_archived=action.entries_retained,
            entries_expired=action.entries_deleted,
            retention_days=max_age_days,
            reason=f"Void cleanup: {action.entries_deleted} expired, {action.entries_retained} retained",
        )

    # =========================================================================
    # VERIFICATION METHODS
    # =========================================================================

    def verify_seal(
        self,
        entry_id: str,
        expected_hash: str,
    ) -> Tuple[bool, str]:
        """
        Verify a sealed entry.

        Args:
            entry_id: Entry ID to verify
            expected_hash: Expected evidence hash

        Returns:
            Tuple of (verified, reason)
        """
        return self.audit_layer.verify_entry(entry_id, expected_hash)

    def verify_receipt(
        self,
        receipt: EurekaReceipt,
    ) -> Tuple[bool, str]:
        """
        Verify a EUREKA receipt.

        Args:
            receipt: Receipt to verify

        Returns:
            Tuple of (verified, reason)
        """
        if receipt.verify():
            return True, "Receipt verified against merkle proof"
        else:
            return False, "Receipt verification failed"

    # =========================================================================
    # LOGGING
    # =========================================================================

    def log_finalization(
        self,
        context: SealContext,
        result: SealResult,
    ) -> None:
        """
        Explicitly log a finalization operation.

        Args:
            context: Seal context
            result: Seal result
        """
        self._log_seal(context, result)

    def get_seal_log(self) -> List[SealLogEntry]:
        """Return the seal log."""
        return list(self._seal_log)

    def clear_seal_log(self) -> None:
        """Clear the seal log."""
        self._seal_log.clear()

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _archive_to_void(
        self,
        context: SealContext,
    ) -> SealResult:
        """Archive an entry to void band."""
        entry = MemoryEntry(
            entry_id=context.entry_id,
            band=BandName.VOID.value,
            verdict=context.verdict,
            content=context.content,
            writer_id=context.writer_id,
            evidence_hash=context.evidence_hash,
            timestamp=context.timestamp,
            metadata={
                "floor_scores": context.floor_scores,
                "session_id": context.session_id,
                "archived_at": datetime.now(timezone.utc).isoformat(),
                "retention_days": 90,
            },
        )

        write_results = self.band_router.route_write(
            verdict=context.verdict,
            content=entry.content,
            writer_id=context.writer_id,
            target_band=BandName.VOID.value,
            evidence_hash=context.evidence_hash,
            metadata=entry.metadata,
        )

        # Get the VOID band result
        void_result = write_results.get(BandName.VOID.value) or write_results.get("VOID")

        if void_result and void_result.success:
            result = SealResult(
                success=True,
                status=SealStatus.VOID_ARCHIVED,
                entry_id=void_result.entry_id,
                reason="Archived to void (non-canonical)",
            )
        else:
            result = SealResult(
                success=False,
                status=SealStatus.ERROR,
                entry_id=context.entry_id,
                reason="Failed to archive to void",
            )

        self._log_seal(context, result)

        return result

    def _emit_receipt(
        self,
        context: SealContext,
        write_result: WriteResult,
    ) -> EurekaReceipt:
        """Emit a receipt for a sealed entry."""
        return self.emit_eureka_receipt(context, self._chain_index)

    def _log_seal(
        self,
        context: SealContext,
        result: SealResult,
    ) -> None:
        """Log a seal operation."""
        entry = SealLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            entry_id=context.entry_id,
            verdict=context.verdict,
            status=result.status.value,
            ledger_index=result.ledger_index,
            has_receipt=result.receipt is not None,
            reason=result.reason,
        )
        self._seal_log.append(entry)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def seal_finalize_to_ledger(
    entry_id: str,
    verdict: str,
    content: Dict[str, Any],
    evidence_hash: str,
    floor_scores: Optional[Dict[str, float]] = None,
) -> SealResult:
    """
    Finalize an entry to the Cooling Ledger.

    Args:
        entry_id: Entry ID
        verdict: Verdict
        content: Content
        evidence_hash: Evidence hash
        floor_scores: Floor scores

    Returns:
        SealResult
    """
    integration = MemorySealIntegration()
    context = SealContext(
        entry_id=entry_id,
        verdict=verdict,
        content=content,
        evidence_hash=evidence_hash,
        floor_scores=floor_scores or {},
    )
    return integration.finalize_to_ledger(context)


def seal_emit_eureka_receipt(
    entry_id: str,
    verdict: str,
    evidence_hash: str,
    floor_scores: Optional[Dict[str, float]] = None,
    ledger_index: int = 0,
) -> EurekaReceipt:
    """
    Emit a EUREKA receipt.

    Args:
        entry_id: Entry ID
        verdict: Verdict
        evidence_hash: Evidence hash
        floor_scores: Floor scores
        ledger_index: Ledger index

    Returns:
        EurekaReceipt
    """
    integration = MemorySealIntegration()
    context = SealContext(
        entry_id=entry_id,
        verdict=verdict,
        content={},
        evidence_hash=evidence_hash,
        floor_scores=floor_scores or {},
    )
    return integration.emit_eureka_receipt(context, ledger_index)


def seal_close_active_stream(
    session_id: str,
) -> SessionCloseResult:
    """
    Close the active stream for a session.

    Args:
        session_id: Session ID

    Returns:
        SessionCloseResult
    """
    integration = MemorySealIntegration()
    return integration.close_active_stream(session_id)


def seal_archive_void(
    max_age_days: int = 90,
) -> VoidArchiveResult:
    """
    Archive void entries.

    Args:
        max_age_days: Maximum age in days

    Returns:
        VoidArchiveResult
    """
    integration = MemorySealIntegration()
    return integration.archive_void(max_age_days)


def seal_log_finalization(
    context: SealContext,
    result: SealResult,
) -> None:
    """
    Log a finalization operation.

    Args:
        context: Seal context
        result: Seal result
    """
    integration = MemorySealIntegration()
    integration.log_finalization(context, result)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "SealStatus",
    "SEALABLE_VERDICTS",
    "VOID_ARCHIVE_VERDICTS",
    "MAX_BATCH_SIZE",
    # Data classes
    "SealContext",
    "EurekaReceipt",
    "SealResult",
    "SessionCloseResult",
    "VoidArchiveResult",
    "SealLogEntry",
    # Main class
    "MemorySealIntegration",
    # Convenience functions
    "seal_finalize_to_ledger",
    "seal_emit_eureka_receipt",
    "seal_close_active_stream",
    "seal_archive_void",
    "seal_log_finalization",
]

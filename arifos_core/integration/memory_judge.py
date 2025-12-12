"""
memory_judge.py — 888_JUDGE ↔ Memory Integration for arifOS v38

Provides integration between the 888_JUDGE pipeline stage and the
v38 Memory Write Policy Engine.

Key Functions:
- judge_compute_evidence_hash(): Compute cryptographic hash of evidence
- judge_check_write_policy(): Check if write is allowed based on verdict
- judge_route_to_band(): Route write to appropriate memory band
- judge_record_audit(): Record write decision in audit layer
- judge_enforce_authority(): Enforce human seal requirements

Core Invariant:
VOID verdicts NEVER become canonical memory.
Every write must be auditable with complete evidence chain.

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md (v38)

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging

# v38 Memory imports
from ..memory.policy import (
    Verdict,
    MemoryWritePolicy,
    WriteDecision,
    EvidenceChainValidation,
    VERDICT_BAND_ROUTING,
)
from ..memory.bands import (
    BandName,
    MemoryBandRouter,
    MemoryEntry,
    WriteResult,
)
from ..memory.authority import (
    MemoryAuthorityCheck,
    AuthorityDecision,
    HumanApprovalRequiredError,
    SelfModificationError,
)
from ..memory.audit import (
    MemoryAuditLayer,
)

# Import shared utility to eliminate duplication
from .common_utils import compute_integration_evidence_hash


logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Writers that require special handling
PRIVILEGED_WRITERS = frozenset([
    "APEX_PRIME",
    "888_JUDGE",
    "HUMAN",
])

# Verdicts that can write to canonical memory
CANONICAL_VERDICTS = frozenset([
    Verdict.SEAL.value,
    Verdict.PARTIAL.value,
    "SEAL",
    "PARTIAL",
])

# Verdicts that go to void only
VOID_ONLY_VERDICTS = frozenset([
    Verdict.VOID.value,
    Verdict.SABAR.value,
    "VOID",
    "SABAR",
])


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class JudgeWriteContext:
    """Context for a judge write operation."""
    verdict: str
    content: Dict[str, Any]
    writer_id: str = "888_JUDGE"
    floor_scores: Dict[str, float] = field(default_factory=dict)
    evidence_sources: List[str] = field(default_factory=list)
    session_id: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_evidence_dict(self) -> Dict[str, Any]:
        """Convert to evidence dictionary for hashing."""
        return {
            "verdict": self.verdict,
            "content": self.content,
            "writer_id": self.writer_id,
            "floor_scores": self.floor_scores,
            "evidence_sources": self.evidence_sources,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
        }


@dataclass
class JudgeWriteResult:
    """Result of a judge write operation."""
    success: bool
    evidence_hash: str
    target_band: str
    entry_id: Optional[str] = None
    audit_record_id: Optional[str] = None
    write_allowed: bool = True
    write_reason: str = ""
    authority_check_passed: bool = True
    authority_reason: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def is_canonical(self) -> bool:
        """Check if the write went to canonical memory."""
        return self.target_band not in ("VOID", "void")


@dataclass
class JudgeLogEntry:
    """Log entry for judge write decisions."""
    timestamp: str
    verdict: str
    evidence_hash: str
    target_band: str
    write_allowed: bool
    authority_passed: bool
    reason: str


# =============================================================================
# MEMORY JUDGE INTEGRATION CLASS
# =============================================================================

class MemoryJudgeIntegration:
    """
    Integrates 888_JUDGE stage with v38 Memory Write Policy Engine.

    Responsibilities:
    1. Compute evidence hash for all writes
    2. Check write policy based on verdict
    3. Route writes to appropriate memory band
    4. Record all writes in audit layer
    5. Enforce authority boundaries (human seal)

    Usage:
        judge_integration = MemoryJudgeIntegration(
            write_policy=MemoryWritePolicy(),
            band_router=MemoryBandRouter(),
            authority_check=MemoryAuthorityCheck(),
            audit_layer=MemoryAuditLayer(),
        )

        # Process a verdict write
        result = judge_integration.process_verdict_write(
            JudgeWriteContext(
                verdict="SEAL",
                content={"response": "..."},
                floor_scores={"F2_truth": 0.99, ...},
            )
        )
    """

    def __init__(
        self,
        write_policy: Optional[MemoryWritePolicy] = None,
        band_router: Optional[MemoryBandRouter] = None,
        authority_check: Optional[MemoryAuthorityCheck] = None,
        audit_layer: Optional[MemoryAuditLayer] = None,
    ):
        """
        Initialize the judge integration.

        Args:
            write_policy: Memory write policy
            band_router: Memory band router
            authority_check: Authority checker
            audit_layer: Audit layer
        """
        self.write_policy = write_policy or MemoryWritePolicy(strict_mode=True)
        self.band_router = band_router or MemoryBandRouter()
        self.authority_check = authority_check or MemoryAuthorityCheck()
        self.audit_layer = audit_layer or MemoryAuditLayer()
        self._judge_log: List[JudgeLogEntry] = []

    # =========================================================================
    # CORE JUDGE METHODS
    # =========================================================================

    def process_verdict_write(
        self,
        context: JudgeWriteContext,
    ) -> JudgeWriteResult:
        """
        Process a verdict write from 888_JUDGE.

        This is the main entry point for write operations from the judge stage.

        Args:
            context: Judge write context with verdict and content

        Returns:
            JudgeWriteResult with write outcome
        """
        # Step 1: Compute evidence hash
        evidence_hash = self.compute_evidence_hash(context)

        # Step 2: Determine target band based on verdict
        target_band = self._get_target_band(context.verdict)

        # Step 3: Check write policy
        write_decision = self.check_write_policy(context, target_band)

        if not write_decision.allowed:
            result = JudgeWriteResult(
                success=False,
                evidence_hash=evidence_hash,
                target_band=target_band,
                write_allowed=False,
                write_reason=write_decision.reason,
            )
            self._log_decision(context.verdict, evidence_hash, target_band, False, True, write_decision.reason)
            return result

        # Step 4: Check authority (human seal for vault)
        try:
            self.enforce_authority(context, target_band)
        except (HumanApprovalRequiredError, SelfModificationError) as e:
            result = JudgeWriteResult(
                success=False,
                evidence_hash=evidence_hash,
                target_band=target_band,
                write_allowed=True,
                write_reason="Write policy passed",
                authority_check_passed=False,
                authority_reason=str(e),
            )
            self._log_decision(context.verdict, evidence_hash, target_band, True, False, str(e))
            return result

        # Step 5: Route to band
        write_result = self.route_to_band(context, target_band, evidence_hash)

        if not write_result.success:
            result = JudgeWriteResult(
                success=False,
                evidence_hash=evidence_hash,
                target_band=target_band,
                write_allowed=True,
                write_reason="Write policy passed",
                authority_check_passed=True,
                authority_reason="Authority check passed",
            )
            self._log_decision(context.verdict, evidence_hash, target_band, True, True, "Band write failed")
            return result

        # Step 6: Record in audit layer
        audit_record_id = self.record_audit(context, write_result, evidence_hash)

        result = JudgeWriteResult(
            success=True,
            evidence_hash=evidence_hash,
            target_band=target_band,
            entry_id=write_result.entry_id,
            audit_record_id=audit_record_id,
            write_allowed=True,
            write_reason="Write policy passed",
            authority_check_passed=True,
            authority_reason="Authority check passed",
        )

        self._log_decision(context.verdict, evidence_hash, target_band, True, True, "Write completed successfully")

        return result

    def compute_evidence_hash(
        self,
        context: JudgeWriteContext,
    ) -> str:
        """
        Compute cryptographic hash of evidence.

        Args:
            context: Judge write context

        Returns:
            SHA-256 hash of evidence
        """
        return compute_integration_evidence_hash(
            verdict=context.verdict,
            content=context.content,
            floor_scores=context.floor_scores,
            evidence_sources=context.evidence_sources,
            timestamp=context.timestamp,
        )

    def check_write_policy(
        self,
        context: JudgeWriteContext,
        target_band: str,
    ) -> WriteDecision:
        """
        Check if write is allowed based on verdict and policy.

        Args:
            context: Judge write context
            target_band: Target band name

        Returns:
            WriteDecision with allowed status
        """
        import hashlib
        import json

        # Build evidence chain for the policy check
        evidence_chain = {
            "floor_checks": [
                {"floor": k, "score": v, "passed": True}
                for k, v in context.floor_scores.items()
            ],
            "evidence_sources": context.evidence_sources,
            "timestamp": context.timestamp,
            "verdict": context.verdict,
        }

        # Compute hash of the evidence chain (required by policy)
        content_hash = hashlib.sha256(
            json.dumps(evidence_chain, sort_keys=True).encode()
        ).hexdigest()
        evidence_chain["hash"] = content_hash

        return self.write_policy.should_write(
            verdict=context.verdict,
            evidence_chain=evidence_chain,
            band_target=target_band,
        )

    def route_to_band(
        self,
        context: JudgeWriteContext,
        target_band: str,
        evidence_hash: str,
    ) -> WriteResult:
        """
        Route write to appropriate memory band.

        Args:
            context: Judge write context
            target_band: Target band name
            evidence_hash: Computed evidence hash

        Returns:
            WriteResult from band router
        """
        # Build the entry
        entry = MemoryEntry(
            entry_id="",  # Will be generated
            band=target_band,
            verdict=context.verdict,
            content=context.content,
            writer_id=context.writer_id,
            evidence_hash=evidence_hash,
            timestamp=context.timestamp,
            metadata={
                "floor_scores": context.floor_scores,
                "evidence_sources": context.evidence_sources,
                "session_id": context.session_id,
            },
        )

        # Write to the band
        return self.band_router.write(
            band=BandName(target_band) if target_band in [b.value for b in BandName] else BandName.VOID,
            entry=entry,
            verdict=context.verdict,
            writer_id=context.writer_id,
        )

    def record_audit(
        self,
        context: JudgeWriteContext,
        write_result: WriteResult,
        evidence_hash: str,
    ) -> str:
        """
        Record write in audit layer.

        Args:
            context: Judge write context
            write_result: Result of band write
            evidence_hash: Computed evidence hash

        Returns:
            Audit record ID
        """
        return self.audit_layer.record_write(
            entry_id=write_result.entry_id,
            band=write_result.band,
            verdict=context.verdict,
            evidence_hash=evidence_hash,
            writer_id=context.writer_id,
            floor_scores=context.floor_scores,
        )

    def enforce_authority(
        self,
        context: JudgeWriteContext,
        target_band: str,
    ) -> AuthorityDecision:
        """
        Enforce authority boundaries.

        Args:
            context: Judge write context
            target_band: Target band name

        Returns:
            AuthorityDecision

        Raises:
            HumanApprovalRequiredError: If human approval needed
            SelfModificationError: If AI tries to modify constitution
        """
        # Check writer authorization
        writer_decision = self.authority_check.validate_writer(
            writer_id=context.writer_id,
            band=target_band,
        )

        if not writer_decision.allowed:
            if writer_decision.requires_human_approval:
                raise HumanApprovalRequiredError(writer_decision.reason)
            return writer_decision

        # Check authority boundary (constitutional self-modification)
        self.authority_check.authority_boundary_check(
            proposed_write={
                "writer_id": context.writer_id,
                "band": target_band,
                "content": context.content,
            }
        )

        # Check human seal requirement
        seal_decision = self.authority_check.enforce_human_seal_required(
            band=target_band,
            verdict=context.verdict,
            writer_id=context.writer_id,
        )

        return seal_decision

    # =========================================================================
    # VALIDATION METHODS
    # =========================================================================

    def validate_evidence_chain(
        self,
        context: JudgeWriteContext,
    ) -> EvidenceChainValidation:
        """
        Validate the evidence chain for a write.

        Args:
            context: Judge write context

        Returns:
            EvidenceChainValidation result
        """
        # Build evidence chain for validation
        evidence_chain = {
            "floor_checks": [
                {"floor": k, "score": v, "passed": True}
                for k, v in context.floor_scores.items()
            ],
            "evidence_sources": context.evidence_sources,
            "timestamp": context.timestamp,
            "verdict": context.verdict,
        }

        return self.write_policy.validate_evidence_chain(evidence_chain)

    def verify_write_integrity(
        self,
        entry_id: str,
        expected_hash: str,
    ) -> bool:
        """
        Verify integrity of a written entry.

        Args:
            entry_id: Entry ID to verify
            expected_hash: Expected evidence hash

        Returns:
            True if integrity verified
        """
        return self.audit_layer.verify_entry(entry_id, expected_hash)

    # =========================================================================
    # LOGGING
    # =========================================================================

    def get_judge_log(self) -> List[JudgeLogEntry]:
        """Return the judge decision log."""
        return list(self._judge_log)

    def clear_judge_log(self) -> None:
        """Clear the judge decision log."""
        self._judge_log.clear()

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _get_target_band(self, verdict: str) -> str:
        """Get target band for a verdict."""
        verdict_upper = verdict.upper()

        # VOID verdicts ALWAYS go to VOID band
        if verdict_upper in VOID_ONLY_VERDICTS or verdict_upper in ("VOID", "SABAR"):
            return BandName.VOID.value

        # Get from routing table
        if verdict_upper in VERDICT_BAND_ROUTING:
            targets = VERDICT_BAND_ROUTING[verdict_upper]
            if targets:
                # Return primary target
                return targets[0].value if hasattr(targets[0], 'value') else targets[0]

        # Default to ACTIVE for unknown verdicts
        return BandName.ACTIVE.value

    def _log_decision(
        self,
        verdict: str,
        evidence_hash: str,
        target_band: str,
        write_allowed: bool,
        authority_passed: bool,
        reason: str,
    ) -> None:
        """Log a judge decision."""
        entry = JudgeLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            verdict=verdict,
            evidence_hash=evidence_hash,
            target_band=target_band,
            write_allowed=write_allowed,
            authority_passed=authority_passed,
            reason=reason,
        )
        self._judge_log.append(entry)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def judge_compute_evidence_hash(
    verdict: str,
    content: Dict[str, Any],
    floor_scores: Optional[Dict[str, float]] = None,
    evidence_sources: Optional[List[str]] = None,
) -> str:
    """
    Compute evidence hash for a verdict.

    Args:
        verdict: The verdict
        content: Content being written
        floor_scores: Floor scores
        evidence_sources: Evidence sources

    Returns:
        SHA-256 hash
    """
    return compute_integration_evidence_hash(
        verdict=verdict,
        content=content,
        floor_scores=floor_scores or {},
        evidence_sources=evidence_sources or [],
    )


def judge_check_write_policy(
    verdict: str,
    target_band: str,
    floor_scores: Optional[Dict[str, float]] = None,
    evidence_sources: Optional[List[str]] = None,
    strict_mode: bool = True,
) -> WriteDecision:
    """
    Check if write is allowed by policy.

    Args:
        verdict: The verdict
        target_band: Target band
        floor_scores: Floor scores
        evidence_sources: Evidence sources
        strict_mode: Enable strict mode

    Returns:
        WriteDecision
    """
    from datetime import datetime, timezone

    policy = MemoryWritePolicy(strict_mode=strict_mode)

    # Build evidence chain
    evidence_chain = {
        "floor_checks": [
            {"floor": k, "score": v, "passed": True}
            for k, v in (floor_scores or {}).items()
        ],
        "evidence_sources": evidence_sources or [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return policy.should_write(
        verdict=verdict,
        evidence_chain=evidence_chain,
        band_target=target_band,
    )


def judge_route_to_band(
    verdict: str,
    content: Dict[str, Any],
    floor_scores: Optional[Dict[str, float]] = None,
    writer_id: str = "888_JUDGE",
) -> WriteResult:
    """
    Route a verdict write to the appropriate band.

    Args:
        verdict: The verdict
        content: Content to write
        floor_scores: Floor scores
        writer_id: Writer ID

    Returns:
        WriteResult
    """
    integration = MemoryJudgeIntegration()
    context = JudgeWriteContext(
        verdict=verdict,
        content=content,
        writer_id=writer_id,
        floor_scores=floor_scores or {},
    )

    target_band = integration._get_target_band(verdict)
    evidence_hash = integration.compute_evidence_hash(context)

    return integration.route_to_band(context, target_band, evidence_hash)


def judge_record_audit(
    entry_id: str,
    band: str,
    verdict: str,
    evidence_hash: str,
    writer_id: str = "888_JUDGE",
    floor_scores: Optional[Dict[str, float]] = None,
) -> str:
    """
    Record a write in the audit layer.

    Args:
        entry_id: Entry ID
        band: Band name
        verdict: Verdict
        evidence_hash: Evidence hash
        writer_id: Writer ID
        floor_scores: Floor scores

    Returns:
        Audit record ID
    """
    audit_layer = MemoryAuditLayer()
    return audit_layer.record_write(
        entry_id=entry_id,
        band=band,
        verdict=verdict,
        evidence_hash=evidence_hash,
        writer_id=writer_id,
        floor_scores=floor_scores or {},
    )


def judge_enforce_authority(
    writer_id: str,
    target_band: str,
    verdict: str,
    human_approval: bool = False,
) -> AuthorityDecision:
    """
    Enforce authority for a write operation.

    Args:
        writer_id: Writer ID
        target_band: Target band
        verdict: Verdict
        human_approval: Human approval flag

    Returns:
        AuthorityDecision

    Raises:
        HumanApprovalRequiredError: If human approval needed
        SelfModificationError: If AI tries to modify constitution
    """
    authority_check = MemoryAuthorityCheck(human_approval_flag=human_approval)
    return authority_check.enforce_human_seal_required(
        band=target_band,
        verdict=verdict,
        writer_id=writer_id,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "PRIVILEGED_WRITERS",
    "CANONICAL_VERDICTS",
    "VOID_ONLY_VERDICTS",
    # Data classes
    "JudgeWriteContext",
    "JudgeWriteResult",
    "JudgeLogEntry",
    # Main class
    "MemoryJudgeIntegration",
    # Convenience functions
    "judge_compute_evidence_hash",
    "judge_check_write_policy",
    "judge_route_to_band",
    "judge_record_audit",
    "judge_enforce_authority",
]

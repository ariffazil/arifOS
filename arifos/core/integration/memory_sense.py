"""
memory_sense.py — 111_SENSE ↔ Memory Integration for arifOS v38

Provides integration between the 111_SENSE pipeline stage and the
v38 Memory Write Policy Engine.

Key Functions:
- sense_load_cross_session_memory(): Load relevant memories at start of 111_SENSE
- sense_inject_context(): Inject recalled memories into context
- sense_should_recall_from_vault(): Check if topic has Vault entry
- sense_compute_recall_confidence(): Compute confidence ceiling for recalled memories
- sense_log_recall_decision(): Log what was recalled and why

Core Invariant:
Recalled memory passes floor checks (suggestion, not fact).
Memory is NEVER treated as ground truth—always as context that must
pass current floor checks before influencing output.

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
    Verdict,
    MemoryWritePolicy,
    RecallDecision,
)
from ..memory.bands import (
    BandName,
    MemoryBandRouter,
    MemoryEntry,
    QueryResult,
)


logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Maximum number of memories to recall in a single sense operation
MAX_RECALL_ENTRIES = 10

# Confidence ceiling for recalled memories (they are suggestions, not facts)
RECALL_CONFIDENCE_CEILING = 0.85

# Bands to search for cross-session memory (in priority order)
RECALL_BAND_PRIORITY = [
    BandName.VAULT,      # Constitutional entries (highest priority)
    BandName.LEDGER,     # Verified audit trail
    BandName.WITNESS,    # Soft evidence
    BandName.ACTIVE,     # Current session (if relevant)
]

# Topics that require Vault check
VAULT_REQUIRED_TOPICS = frozenset([
    "constitution",
    "amendment",
    "floor",
    "threshold",
    "law",
    "governance",
    "amanah",
    "authority",
    "seal",
])


# =============================================================================
# DATA CLASSES
# =============================================================================

class RecallSource(str, Enum):
    """Source of a recalled memory."""
    VAULT = "VAULT"
    LEDGER = "LEDGER"
    WITNESS = "WITNESS"
    ACTIVE = "ACTIVE"
    PHOENIX = "PHOENIX"


@dataclass
class RecallContext:
    """Context for a memory recall operation."""
    query: str
    topic_keywords: List[str] = field(default_factory=list)
    session_id: Optional[str] = None
    requester_stage: str = "111_SENSE"
    max_entries: int = MAX_RECALL_ENTRIES
    include_void: bool = False  # VOID is never included by default
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class RecalledMemory:
    """A single recalled memory entry."""
    entry_id: str
    content: Dict[str, Any]
    source_band: RecallSource
    original_verdict: str
    recall_confidence: float
    relevance_score: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_context_injection(self) -> Dict[str, Any]:
        """Format this memory for context injection."""
        return {
            "type": "recalled_memory",
            "entry_id": self.entry_id,
            "source": self.source_band.value,
            "confidence": self.recall_confidence,
            "relevance": self.relevance_score,
            "content": self.content,
            "caveat": "This is recalled memory (suggestion), not ground truth. "
                     "Must pass current floor checks.",
        }


@dataclass
class SenseRecallResult:
    """Result of a sense recall operation."""
    recalled_memories: List[RecalledMemory] = field(default_factory=list)
    vault_entries_found: int = 0
    ledger_entries_found: int = 0
    witness_entries_found: int = 0
    total_searched: int = 0
    recall_allowed: bool = True
    recall_reason: str = ""
    confidence_ceiling: float = RECALL_CONFIDENCE_CEILING
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def has_memories(self) -> bool:
        """Check if any memories were recalled."""
        return len(self.recalled_memories) > 0

    @property
    def has_vault_entries(self) -> bool:
        """Check if any Vault entries were found."""
        return self.vault_entries_found > 0


@dataclass
class RecallLogEntry:
    """Log entry for recall decisions."""
    timestamp: str
    query_hash: str
    bands_searched: List[str]
    entries_found: int
    entries_recalled: int
    confidence_ceiling: float
    reason: str


# =============================================================================
# MEMORY SENSE INTEGRATION CLASS
# =============================================================================

class MemorySenseIntegration:
    """
    Integrates 111_SENSE stage with v38 Memory Write Policy Engine.

    Responsibilities:
    1. Load cross-session memory at start of sense
    2. Check if topic requires Vault consultation
    3. Inject recalled memories into context (with caveats)
    4. Compute confidence ceiling for recalled data
    5. Log all recall decisions for audit

    Usage:
        sense_integration = MemorySenseIntegration(
            write_policy=MemoryWritePolicy(),
            band_router=MemoryBandRouter(),
        )

        # Load memories for a query
        result = sense_integration.load_cross_session_memory(
            RecallContext(query="What is Amanah?")
        )

        # Inject into context
        context = sense_integration.inject_context(result, existing_context)
    """

    def __init__(
        self,
        write_policy: Optional[MemoryWritePolicy] = None,
        band_router: Optional[MemoryBandRouter] = None,
    ):
        """
        Initialize the sense integration.

        Args:
            write_policy: Memory write policy (creates default if None)
            band_router: Memory band router (creates default if None)
        """
        self.write_policy = write_policy or MemoryWritePolicy()
        self.band_router = band_router or MemoryBandRouter()
        self._recall_log: List[RecallLogEntry] = []

    # =========================================================================
    # CORE RECALL METHODS
    # =========================================================================

    def load_cross_session_memory(
        self,
        context: RecallContext,
    ) -> SenseRecallResult:
        """
        Load relevant memories from previous sessions.

        This is called at the start of 111_SENSE to provide context
        from prior interactions.

        Args:
            context: Recall context with query and parameters

        Returns:
            SenseRecallResult with recalled memories
        """
        result = SenseRecallResult()
        recalled: List[RecalledMemory] = []

        # Check if recall is allowed for this query
        recall_decision = self.write_policy.should_recall(
            band=BandName.LEDGER.value,  # Default band for recall check
            query_context={"query": context.query},
        )

        if not recall_decision.allowed:
            result.recall_allowed = False
            result.recall_reason = recall_decision.reason
            self._log_recall(context, [], 0, recall_decision.reason)
            return result

        # Search each band in priority order
        bands_searched = []
        for band_name in RECALL_BAND_PRIORITY:
            if band_name == BandName.VOID and not context.include_void:
                continue  # Skip VOID unless explicitly requested

            bands_searched.append(band_name.value)

            # Query the band
            query_result = self.band_router.query(
                band=band_name,
                query=context.query,
                limit=context.max_entries,
            )

            result.total_searched += query_result.total_matches

            # Track counts by band
            if band_name == BandName.VAULT:
                result.vault_entries_found = query_result.total_matches
            elif band_name == BandName.LEDGER:
                result.ledger_entries_found = query_result.total_matches
            elif band_name == BandName.WITNESS:
                result.witness_entries_found = query_result.total_matches

            # Convert to recalled memories
            for entry in query_result.entries:
                if len(recalled) >= context.max_entries:
                    break

                # Compute confidence with ceiling
                confidence = self._compute_recall_confidence(
                    entry=entry,
                    band=band_name,
                    relevance=query_result.relevance_scores.get(entry.entry_id, 0.5),
                )

                recalled.append(RecalledMemory(
                    entry_id=entry.entry_id,
                    content=entry.content,
                    source_band=RecallSource(band_name.value),
                    original_verdict=entry.verdict,
                    recall_confidence=confidence,
                    relevance_score=query_result.relevance_scores.get(entry.entry_id, 0.5),
                    timestamp=entry.timestamp,
                    metadata=entry.metadata,
                ))

        result.recalled_memories = recalled
        result.recall_allowed = True
        result.recall_reason = f"Recalled {len(recalled)} memories from {len(bands_searched)} bands"
        result.confidence_ceiling = recall_decision.confidence_ceiling

        self._log_recall(context, bands_searched, len(recalled), result.recall_reason)

        return result

    def inject_context(
        self,
        recall_result: SenseRecallResult,
        existing_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Inject recalled memories into the pipeline context.

        IMPORTANT: Recalled memories are ALWAYS marked as suggestions,
        not facts. They must pass current floor checks.

        Args:
            recall_result: Result from load_cross_session_memory
            existing_context: Existing pipeline context

        Returns:
            Updated context with recalled memories
        """
        if not recall_result.has_memories:
            return existing_context

        # Create the injection block
        memory_injection = {
            "recalled_memories": [
                mem.as_context_injection()
                for mem in recall_result.recalled_memories
            ],
            "vault_entries_present": recall_result.has_vault_entries,
            "confidence_ceiling": recall_result.confidence_ceiling,
            "caveat": (
                "RECALLED MEMORY CAVEAT: These are suggestions from prior sessions, "
                "NOT ground truth. Each recalled item must pass current floor checks "
                "before influencing output. Do not treat recalled memories as facts."
            ),
            "recall_timestamp": recall_result.timestamp,
        }

        # Merge with existing context
        updated_context = existing_context.copy()
        updated_context["memory_context"] = memory_injection

        return updated_context

    def should_recall_from_vault(
        self,
        query: str,
        topic_keywords: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """
        Check if a query requires Vault consultation.

        Constitutional topics MUST check the Vault before responding.

        Args:
            query: The query being processed
            topic_keywords: Extracted topic keywords

        Returns:
            Tuple of (should_recall, reason)
        """
        keywords = topic_keywords or []
        query_lower = query.lower()

        # Check if query mentions vault-required topics
        for topic in VAULT_REQUIRED_TOPICS:
            if topic in query_lower or topic in [k.lower() for k in keywords]:
                return True, f"Query mentions constitutional topic: {topic}"

        # Check for explicit vault reference
        if "vault" in query_lower or "constitution" in query_lower:
            return True, "Query explicitly references Vault/constitution"

        # Check for amendment-related queries
        if "amendment" in query_lower or "floor" in query_lower:
            return True, "Query relates to amendments or floors"

        return False, "No vault consultation required"

    def compute_recall_confidence(
        self,
        entry: MemoryEntry,
        source_band: BandName,
        relevance_score: float,
    ) -> float:
        """
        Compute the confidence ceiling for a recalled memory.

        Recalled memories NEVER have 100% confidence because they
        are suggestions that must pass current floor checks.

        Args:
            entry: The memory entry
            source_band: Which band it came from
            relevance_score: How relevant it is to the query

        Returns:
            Confidence value with ceiling applied
        """
        return self._compute_recall_confidence(entry, source_band, relevance_score)

    # =========================================================================
    # LOGGING
    # =========================================================================

    def log_recall_decision(
        self,
        context: RecallContext,
        result: SenseRecallResult,
    ) -> None:
        """
        Explicitly log a recall decision for audit.

        Args:
            context: The recall context
            result: The recall result
        """
        query_hash = hashlib.sha256(context.query.encode()).hexdigest()[:16]

        entry = RecallLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            query_hash=query_hash,
            bands_searched=[b.value for b in RECALL_BAND_PRIORITY],
            entries_found=result.total_searched,
            entries_recalled=len(result.recalled_memories),
            confidence_ceiling=result.confidence_ceiling,
            reason=result.recall_reason,
        )

        self._recall_log.append(entry)

        logger.info(
            f"Recall decision logged: {len(result.recalled_memories)} memories "
            f"recalled from {result.total_searched} found"
        )

    def get_recall_log(self) -> List[RecallLogEntry]:
        """Return the recall decision log."""
        return list(self._recall_log)

    def clear_recall_log(self) -> None:
        """Clear the recall decision log."""
        self._recall_log.clear()

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _compute_recall_confidence(
        self,
        entry: MemoryEntry,
        band: BandName,
        relevance: float,
    ) -> float:
        """Internal: compute confidence with ceiling."""
        # Base confidence from band type
        band_base = {
            BandName.VAULT: 0.95,     # Vault is most reliable
            BandName.LEDGER: 0.85,    # Ledger is verified
            BandName.WITNESS: 0.70,   # Witness is soft evidence
            BandName.ACTIVE: 0.60,    # Active is current session
            BandName.PHOENIX: 0.50,   # Phoenix is pending
            BandName.VOID: 0.30,      # Void is diagnostic only
        }

        base = band_base.get(band, 0.50)

        # Adjust by relevance
        adjusted = base * relevance

        # Apply ceiling - recalled memories never get 100%
        return min(adjusted, RECALL_CONFIDENCE_CEILING)

    def _log_recall(
        self,
        context: RecallContext,
        bands_searched: List[str],
        entries_recalled: int,
        reason: str,
    ) -> None:
        """Internal: log a recall operation."""
        query_hash = hashlib.sha256(context.query.encode()).hexdigest()[:16]

        entry = RecallLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            query_hash=query_hash,
            bands_searched=bands_searched,
            entries_found=0,
            entries_recalled=entries_recalled,
            confidence_ceiling=RECALL_CONFIDENCE_CEILING,
            reason=reason,
        )

        self._recall_log.append(entry)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def sense_load_cross_session_memory(
    query: str,
    write_policy: Optional[MemoryWritePolicy] = None,
    band_router: Optional[MemoryBandRouter] = None,
    max_entries: int = MAX_RECALL_ENTRIES,
) -> SenseRecallResult:
    """
    Load cross-session memory for a query.

    Convenience function for use in 111_SENSE stage.

    Args:
        query: The query to recall memories for
        write_policy: Memory write policy
        band_router: Memory band router
        max_entries: Maximum entries to recall

    Returns:
        SenseRecallResult with recalled memories
    """
    integration = MemorySenseIntegration(
        write_policy=write_policy,
        band_router=band_router,
    )

    context = RecallContext(
        query=query,
        max_entries=max_entries,
    )

    return integration.load_cross_session_memory(context)


def sense_inject_context(
    recall_result: SenseRecallResult,
    existing_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Inject recalled memories into context.

    Args:
        recall_result: Result from recall operation
        existing_context: Existing pipeline context

    Returns:
        Updated context with memories
    """
    integration = MemorySenseIntegration()
    return integration.inject_context(recall_result, existing_context)


def sense_should_recall_from_vault(
    query: str,
    topic_keywords: Optional[List[str]] = None,
) -> Tuple[bool, str]:
    """
    Check if query requires Vault consultation.

    Args:
        query: The query
        topic_keywords: Topic keywords

    Returns:
        Tuple of (should_recall, reason)
    """
    integration = MemorySenseIntegration()
    return integration.should_recall_from_vault(query, topic_keywords)


def sense_compute_recall_confidence(
    entry: MemoryEntry,
    source_band: BandName,
    relevance_score: float,
) -> float:
    """
    Compute confidence for a recalled memory.

    Args:
        entry: The memory entry
        source_band: Source band
        relevance_score: Relevance score

    Returns:
        Confidence with ceiling applied
    """
    integration = MemorySenseIntegration()
    return integration.compute_recall_confidence(entry, source_band, relevance_score)


def sense_log_recall_decision(
    context: RecallContext,
    result: SenseRecallResult,
) -> None:
    """
    Log a recall decision for audit.

    Args:
        context: Recall context
        result: Recall result
    """
    integration = MemorySenseIntegration()
    integration.log_recall_decision(context, result)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "MAX_RECALL_ENTRIES",
    "RECALL_CONFIDENCE_CEILING",
    "RECALL_BAND_PRIORITY",
    "VAULT_REQUIRED_TOPICS",
    # Enums
    "RecallSource",
    # Data classes
    "RecallContext",
    "RecalledMemory",
    "SenseRecallResult",
    "RecallLogEntry",
    # Main class
    "MemorySenseIntegration",
    # Convenience functions
    "sense_load_cross_session_memory",
    "sense_inject_context",
    "sense_should_recall_from_vault",
    "sense_compute_recall_confidence",
    "sense_log_recall_decision",
]

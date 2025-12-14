"""
memory.py - L7 Memory Layer for arifOS v38.2-alpha

Main Memory class providing:
- recall_at_stage_111(): Cross-session memory recall at 111_SENSE
- store_at_stage_999(): EUREKA Sieve storage at 999_SEAL

EUREKA Sieve Policy:
- SEAL: Store forever (TTL=None)
- VETO/PARTIAL/888_HOLD: Store 730 days
- FLAG: Store 30 days
- VOID/SABAR: Never store (TTL=0)

Fail-open Design:
- If L7 disabled or unavailable, pipeline continues
- Returns empty results for recall
- Returns False for store (logged but not blocked)

Author: arifOS Project
Version: v38.2-alpha
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from .mem0_client import (
    Mem0Client,
    Mem0Config,
    MemoryHit,
    SearchResult,
    StoreResult,
    TTLPolicy,
    get_mem0_client,
    is_l7_enabled,
    is_l7_available,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TOP_K,
)


logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Recall confidence ceiling (memory is suggestion, not fact)
RECALL_CONFIDENCE_CEILING = 0.85

# Maximum memories to recall in single operation
MAX_RECALL_ENTRIES = 10

# Verdicts that should be stored
STORABLE_VERDICTS = frozenset([
    "SEAL",
    "PARTIAL",
    "888_HOLD",
    "VETO",
    "FLAG",
    "SUNSET",
])

# Verdicts that should NEVER be stored
DISCARD_VERDICTS = frozenset([
    "VOID",
    "SABAR",
])


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class RecallResult:
    """Result of recall_at_stage_111 operation."""
    memories: List[MemoryHit] = field(default_factory=list)
    total_found: int = 0
    confidence_ceiling: float = RECALL_CONFIDENCE_CEILING
    l7_available: bool = True
    error: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def has_memories(self) -> bool:
        """Check if any memories were recalled."""
        return len(self.memories) > 0

    def to_context_injection(self) -> Dict[str, Any]:
        """Format for pipeline context injection."""
        return {
            "recalled_memories": [m.to_dict() for m in self.memories],
            "confidence_ceiling": self.confidence_ceiling,
            "recall_count": len(self.memories),
            "caveat": (
                "RECALLED MEMORY CAVEAT: These are suggestions from prior sessions, "
                "NOT ground truth. Each recalled item must pass current floor checks "
                "before influencing output. Do not treat recalled memories as facts."
            ),
            "timestamp": self.timestamp,
        }


@dataclass
class SieveResult:
    """Result of EUREKA Sieve filtering."""
    should_store: bool
    verdict: str
    ttl_days: Optional[int]
    reason: str

    @classmethod
    def from_verdict(cls, verdict: str) -> "SieveResult":
        """Create SieveResult from verdict."""
        verdict_upper = verdict.upper()

        if verdict_upper in DISCARD_VERDICTS:
            return cls(
                should_store=False,
                verdict=verdict_upper,
                ttl_days=0,
                reason=f"Verdict {verdict_upper} is discarded by EUREKA Sieve",
            )

        # Get TTL from policy
        ttl_map = {
            "SEAL": None,         # Forever
            "PARTIAL": 730,       # 2 years
            "888_HOLD": 730,      # 2 years
            "VETO": 730,          # 2 years
            "FLAG": 30,           # 30 days
            "SUNSET": 30,         # 30 days
        }

        ttl = ttl_map.get(verdict_upper, 30)

        return cls(
            should_store=True,
            verdict=verdict_upper,
            ttl_days=ttl,
            reason=f"Verdict {verdict_upper} stored with TTL={ttl or 'forever'}",
        )


@dataclass
class StoreAtSealResult:
    """Result of store_at_stage_999 operation."""
    success: bool
    sieve_result: SieveResult
    memory_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# =============================================================================
# MEMORY CLASS
# =============================================================================

class Memory:
    """
    L7 Memory Layer - Cross-session user context persistence.

    Integrates with pipeline at:
    - 111_SENSE: Recall relevant memories
    - 999_SEAL: Store based on EUREKA Sieve

    Fail-open: If L7 disabled/unavailable, pipeline continues.

    Usage:
        memory = Memory()

        # At 111_SENSE
        recall = memory.recall_at_stage_111(
            query="What is Amanah?",
            user_id="user-123",
        )

        # At 999_SEAL
        result = memory.store_at_stage_999(
            content="User asked about Amanah",
            user_id="user-123",
            verdict="SEAL",
            metadata={"topic": "governance"},
        )
    """

    def __init__(
        self,
        client: Optional[Mem0Client] = None,
        config: Optional[Mem0Config] = None,
    ):
        """
        Initialize Memory layer.

        Args:
            client: Mem0 client (creates default if None)
            config: Configuration (uses env vars if None)
        """
        self._client = client
        self._config = config

        # Lazy initialization
        if self._client is None and self._config is not None:
            self._client = Mem0Client(config=self._config)

    @property
    def client(self) -> Mem0Client:
        """Get or create Mem0 client."""
        if self._client is None:
            self._client = get_mem0_client()
        return self._client

    @property
    def is_available(self) -> bool:
        """Check if L7 Memory is available."""
        return is_l7_enabled() and self.client.is_available

    # Backwards-compatible alias for API/MCP layers
    def is_enabled(self) -> bool:
        """Alias for is_available (public API uses 'enabled' terminology)."""
        return self.is_available

    # =========================================================================
    # PIPELINE INTEGRATION
    # =========================================================================

    def recall_at_stage_111(
        self,
        query: str,
        user_id: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> RecallResult:
        """
        Recall relevant memories at 111_SENSE stage.

        CRITICAL: Always filters by user_id for isolation.
        Confidence ceiling is applied to all recalled memories.

        Args:
            query: Current query/input
            user_id: User ID (required for isolation)
            top_k: Number of results (default: 8)
            threshold: Similarity threshold (default: 0.65)

        Returns:
            RecallResult with memories and confidence ceiling
        """
        # Validate user_id
        if not user_id:
            return RecallResult(
                l7_available=False,
                error="user_id is required for memory recall",
            )

        # Check if L7 is available
        if not is_l7_enabled():
            return RecallResult(
                l7_available=False,
                error="L7 Memory disabled",
            )

        if not self.client.is_available:
            return RecallResult(
                l7_available=False,
                error=self.client.initialization_error,
            )

        # Search for relevant memories
        k = top_k or DEFAULT_TOP_K
        thresh = threshold or DEFAULT_SIMILARITY_THRESHOLD

        search_result = self.client.search(
            query=query,
            user_id=user_id,
            top_k=k,
            threshold=thresh,
        )

        if search_result.error:
            return RecallResult(
                l7_available=True,
                error=search_result.error,
            )

        # Apply confidence ceiling to all memories
        memories = []
        for hit in search_result.hits[:MAX_RECALL_ENTRIES]:
            # Adjust score by confidence ceiling
            adjusted_score = min(hit.score, RECALL_CONFIDENCE_CEILING)
            hit.score = adjusted_score
            memories.append(hit)

        return RecallResult(
            memories=memories,
            total_found=search_result.total_searched,
            confidence_ceiling=RECALL_CONFIDENCE_CEILING,
            l7_available=True,
        )

    def store_at_stage_999(
        self,
        content: str,
        user_id: str,
        verdict: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StoreAtSealResult:
        """
        Store memory at 999_SEAL stage with EUREKA Sieve filtering.

        EUREKA Sieve Policy:
        - SEAL: Store forever
        - VETO/PARTIAL/888_HOLD: Store 730 days
        - FLAG: Store 30 days
        - VOID/SABAR: Never store

        Args:
            content: Content to store
            user_id: User ID (required)
            verdict: APEX verdict (determines storage/TTL)
            metadata: Additional metadata

        Returns:
            StoreAtSealResult with outcome
        """
        # Apply EUREKA Sieve
        sieve_result = SieveResult.from_verdict(verdict)

        # Check if should store
        if not sieve_result.should_store:
            return StoreAtSealResult(
                success=False,
                sieve_result=sieve_result,
                error=sieve_result.reason,
            )

        # Validate user_id
        if not user_id:
            return StoreAtSealResult(
                success=False,
                sieve_result=sieve_result,
                error="user_id is required for memory storage",
            )

        # Check if L7 is available (fail-open)
        if not is_l7_enabled():
            return StoreAtSealResult(
                success=False,
                sieve_result=sieve_result,
                error="L7 Memory disabled (fail-open)",
            )

        if not self.client.is_available:
            return StoreAtSealResult(
                success=False,
                sieve_result=sieve_result,
                error=self.client.initialization_error or "L7 not available (fail-open)",
            )

        # Store the memory
        store_result = self.client.add(
            content=content,
            user_id=user_id,
            verdict=verdict,
            metadata=metadata,
        )

        return StoreAtSealResult(
            success=store_result.success,
            sieve_result=sieve_result,
            memory_id=store_result.memory_id,
            error=store_result.error,
        )

    # =========================================================================
    # EUREKA SIEVE
    # =========================================================================

    def apply_sieve(self, verdict: str) -> SieveResult:
        """
        Apply EUREKA Sieve to determine if verdict should be stored.

        Args:
            verdict: APEX verdict

        Returns:
            SieveResult with storage decision
        """
        return SieveResult.from_verdict(verdict)

    def get_ttl_for_verdict(self, verdict: str) -> Optional[int]:
        """
        Get TTL in days for a verdict.

        Args:
            verdict: APEX verdict

        Returns:
            TTL in days, None for forever, 0 for never store
        """
        sieve = self.apply_sieve(verdict)
        return sieve.ttl_days

    def should_store_verdict(self, verdict: str) -> bool:
        """
        Check if verdict should be stored.

        Args:
            verdict: APEX verdict

        Returns:
            True if should store, False otherwise
        """
        return verdict.upper() not in DISCARD_VERDICTS

    # =========================================================================
    # DIRECT ACCESS (for testing/debugging)
    # =========================================================================

    def search(
        self,
        query: str,
        user_id: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> SearchResult:
        """Direct search access (wraps client)."""
        return self.client.search(
            query=query,
            user_id=user_id,
            top_k=top_k,
            threshold=threshold,
        )

    def add(
        self,
        content: str,
        user_id: str,
        verdict: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StoreResult:
        """Direct add access (wraps client)."""
        return self.client.add(
            content=content,
            user_id=user_id,
            verdict=verdict,
            metadata=metadata,
        )

    def get_all(
        self,
        user_id: str,
        limit: int = 100,
    ) -> SearchResult:
        """Direct get_all access (wraps client)."""
        return self.client.get_all(user_id=user_id, limit=limit)

    def delete(
        self,
        memory_id: str,
        user_id: str,
    ) -> bool:
        """Direct delete access (wraps client)."""
        return self.client.delete(memory_id=memory_id, user_id=user_id)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_default_memory: Optional[Memory] = None


def get_memory() -> Memory:
    """Get or create the default Memory singleton."""
    global _default_memory
    if _default_memory is None:
        _default_memory = Memory()
    return _default_memory


def recall_at_stage_111(
    query: str,
    user_id: str,
    top_k: Optional[int] = None,
    threshold: Optional[float] = None,
) -> RecallResult:
    """
    Recall memories at 111_SENSE stage.

    Convenience function using default Memory instance.
    """
    return get_memory().recall_at_stage_111(
        query=query,
        user_id=user_id,
        top_k=top_k,
        threshold=threshold,
    )


def store_at_stage_999(
    content: str,
    user_id: str,
    verdict: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> StoreAtSealResult:
    """
    Store memory at 999_SEAL stage.

    Convenience function using default Memory instance.
    """
    return get_memory().store_at_stage_999(
        content=content,
        user_id=user_id,
        verdict=verdict,
        metadata=metadata,
    )


def apply_eureka_sieve(verdict: str) -> SieveResult:
    """
    Apply EUREKA Sieve to verdict.

    Convenience function for sieve logic.
    """
    return SieveResult.from_verdict(verdict)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "RECALL_CONFIDENCE_CEILING",
    "MAX_RECALL_ENTRIES",
    "STORABLE_VERDICTS",
    "DISCARD_VERDICTS",
    # Data classes
    "RecallResult",
    "SieveResult",
    "StoreAtSealResult",
    # Main class
    "Memory",
    # Convenience functions
    "get_memory",
    "recall_at_stage_111",
    "store_at_stage_999",
    "apply_eureka_sieve",
]

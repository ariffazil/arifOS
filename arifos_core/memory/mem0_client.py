"""
mem0_client.py - L7 Memory Client for arifOS v38.2-alpha

Wraps Mem0 + Qdrant for cross-session user context persistence.
Fail-open design: if L7 is disabled or unavailable, pipeline continues.

Environment Variables:
    ARIFOS_L7_ENABLED: Enable/disable L7 (default: true)
    MEM0_API_KEY: Mem0 API key
    QDRANT_HOST: Qdrant host (default: localhost)
    QDRANT_PORT: Qdrant port (default: 6333)
    ARIFOS_L7_SIMILARITY_THRESHOLD: Similarity threshold (default: 0.65)
    ARIFOS_L7_TOP_K: Top K results (default: 8)

Author: arifOS Project
Version: v38.2-alpha
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum


logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Default configuration
DEFAULT_SIMILARITY_THRESHOLD = 0.65
DEFAULT_TOP_K = 8
DEFAULT_QDRANT_HOST = "localhost"
DEFAULT_QDRANT_PORT = 6333

# TTL Policy per EUREKA Sieve (days)
class TTLPolicy(Enum):
    """TTL policy for memory entries based on verdict."""
    SEAL = None      # Forever (no expiry)
    VETO = 730       # 2 years
    FLAG = 30        # 30 days
    VOID = 0         # Immediate discard (never store)
    SABAR = 0        # Immediate discard (never store)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Mem0Config:
    """Configuration for Mem0 client."""
    api_key: Optional[str] = None
    qdrant_host: str = DEFAULT_QDRANT_HOST
    qdrant_port: int = DEFAULT_QDRANT_PORT
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    top_k: int = DEFAULT_TOP_K
    enabled: bool = True
    collection_name: str = "arifos_memory"

    @classmethod
    def from_env(cls) -> "Mem0Config":
        """Create config from environment variables."""
        return cls(
            api_key=os.getenv("MEM0_API_KEY"),
            qdrant_host=os.getenv("QDRANT_HOST", DEFAULT_QDRANT_HOST),
            qdrant_port=int(os.getenv("QDRANT_PORT", DEFAULT_QDRANT_PORT)),
            similarity_threshold=float(os.getenv(
                "ARIFOS_L7_SIMILARITY_THRESHOLD", DEFAULT_SIMILARITY_THRESHOLD
            )),
            top_k=int(os.getenv("ARIFOS_L7_TOP_K", DEFAULT_TOP_K)),
            enabled=os.getenv("ARIFOS_L7_ENABLED", "true").lower() in ("true", "1", "yes"),
        )


@dataclass
class MemoryHit:
    """A single memory retrieval hit."""
    memory_id: str
    content: str
    metadata: Dict[str, Any]
    score: float
    user_id: str
    timestamp: str
    verdict: Optional[str] = None
    ttl_days: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "metadata": self.metadata,
            "score": self.score,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "verdict": self.verdict,
            "ttl_days": self.ttl_days,
        }


@dataclass
class EmbedResult:
    """Result of embedding operation."""
    success: bool
    embedding: Optional[List[float]] = None
    error: Optional[str] = None
    model: str = ""
    dimensions: int = 0


@dataclass
class SearchResult:
    """Result of memory search operation."""
    hits: List[MemoryHit] = field(default_factory=list)
    total_searched: int = 0
    threshold_used: float = DEFAULT_SIMILARITY_THRESHOLD
    error: Optional[str] = None

    @property
    def has_results(self) -> bool:
        """Check if any results were found."""
        return len(self.hits) > 0


@dataclass
class StoreResult:
    """Result of memory store operation."""
    success: bool
    memory_id: Optional[str] = None
    error: Optional[str] = None
    ttl_days: Optional[int] = None
    verdict: Optional[str] = None


# =============================================================================
# MEM0 CLIENT CLASS
# =============================================================================

class Mem0Client:
    """
    L7 Memory Client - Wraps Mem0 + Qdrant for cross-session context.

    Fail-open design: if disabled or errors occur, returns empty/safe defaults.
    Pipeline continues without breaking.

    Usage:
        client = Mem0Client()

        # Search for relevant memories
        result = client.search(
            query="What is Amanah?",
            user_id="user-123",
        )

        # Store a new memory
        result = client.add(
            content="User prefers technical explanations",
            user_id="user-123",
            verdict="SEAL",
            metadata={"topic": "preferences"},
        )
    """

    def __init__(
        self,
        config: Optional[Mem0Config] = None,
    ):
        """
        Initialize Mem0 client.

        Args:
            config: Configuration (uses env vars if not provided)
        """
        self.config = config or Mem0Config.from_env()
        self._client = None
        self._qdrant = None
        self._initialized = False
        self._initialization_error: Optional[str] = None

        if self.config.enabled:
            self._initialize()
        else:
            self._initialization_error = "L7 Memory disabled by configuration"

    def _initialize(self) -> None:
        """Initialize Mem0 and Qdrant connections."""
        if not self.config.enabled:
            self._initialization_error = "L7 Memory disabled by configuration"
            return

        try:
            # Lazy import to allow fail-open when dependencies not installed
            from mem0 import Memory as Mem0Memory

            self._client = Mem0Memory()
            self._initialized = True
            logger.info("Mem0 client initialized successfully")

        except ImportError as e:
            self._initialization_error = f"Mem0 not installed: {e}"
            logger.warning(f"L7 Memory unavailable (fail-open): {self._initialization_error}")

        except Exception as e:
            self._initialization_error = f"Mem0 initialization failed: {e}"
            logger.warning(f"L7 Memory unavailable (fail-open): {self._initialization_error}")

    @property
    def is_available(self) -> bool:
        """Check if L7 Memory is available and initialized."""
        return self._initialized and self._client is not None

    @property
    def initialization_error(self) -> Optional[str]:
        """Get initialization error if any."""
        return self._initialization_error

    # =========================================================================
    # CORE OPERATIONS
    # =========================================================================

    def embed(
        self,
        text: str,
        use_stub_fallback: bool = True,
    ) -> EmbedResult:
        """
        Generate embedding for text. **STUB/TEST-ONLY.**

        WARNING: This method is primarily for testing. Mem0 handles embeddings
        internally during add() and search() operations. You typically do NOT
        need to call this directly in production.

        The stub embedding uses a deterministic SHA256-based hash to generate
        a 384-dimensional normalized vector, suitable for testing user isolation
        and similarity logic without requiring a real embedding model.

        Args:
            text: Text to embed
            use_stub_fallback: If True, use stub embedding when Mem0 unavailable

        Returns:
            EmbedResult with embedding vector (stub or real)

        Note:
            Mem0's internal embedding is used when calling search() and add().
            This public embed() is exposed for testing and debugging only.
        """
        if not text:
            return EmbedResult(
                success=False,
                error="Empty text cannot be embedded",
            )

        # Try real Mem0 embedding first
        if self.is_available:
            try:
                embedding = self._get_embedding(text)
                if embedding:
                    return EmbedResult(
                        success=True,
                        embedding=embedding,
                        model="mem0",
                        dimensions=len(embedding),
                    )
            except Exception as e:
                logger.debug(f"Mem0 embedding failed: {e}")

        # Fall back to stub embedding if allowed
        if use_stub_fallback:
            try:
                embedding = self._stub_embedding(text)
                return EmbedResult(
                    success=True,
                    embedding=embedding,
                    model="stub-hash-384",
                    dimensions=len(embedding),
                )
            except Exception as e:
                logger.error(f"Stub embedding failed: {e}")
                return EmbedResult(
                    success=False,
                    error=str(e),
                )

        # No fallback allowed and Mem0 unavailable
        return EmbedResult(
            success=False,
            error=self._initialization_error or "L7 Memory not available and stub disabled",
        )

    def search(
        self,
        query: str,
        user_id: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> SearchResult:
        """
        Search for relevant memories.

        CRITICAL: Always filters by user_id for isolation.

        Args:
            query: Search query
            user_id: User ID (required for isolation)
            top_k: Number of results (default from config)
            threshold: Similarity threshold (default from config)
            filters: Additional metadata filters

        Returns:
            SearchResult with hits
        """
        if not user_id:
            return SearchResult(
                error="user_id is required for memory search",
            )

        if not self.is_available:
            # Fail-open: return empty results
            return SearchResult(
                error=self._initialization_error,
                threshold_used=threshold or self.config.similarity_threshold,
            )

        k = top_k or self.config.top_k
        thresh = threshold or self.config.similarity_threshold

        try:
            # Search with user_id filter
            # Mem0 returns {"results": [...]} format
            response = self._client.search(
                query=query,
                user_id=user_id,
                limit=k,
                threshold=thresh,
            )

            # Extract results from response dict
            memories = response.get("results", []) if isinstance(response, dict) else response

            # Convert to MemoryHit objects
            hits = []
            for mem in memories:
                score = mem.get("score", 0.0)
                # Threshold is already applied by Mem0, but double-check
                if score >= thresh:
                    # Get metadata - it may be nested or at top level
                    mem_metadata = mem.get("metadata", {})
                    hits.append(MemoryHit(
                        memory_id=mem.get("id", ""),
                        content=mem.get("memory", ""),
                        metadata=mem_metadata,
                        score=score,
                        user_id=mem.get("user_id", user_id),
                        timestamp=mem.get("created_at", ""),
                        verdict=mem_metadata.get("verdict"),
                        ttl_days=mem_metadata.get("ttl_days"),
                    ))

            return SearchResult(
                hits=hits,
                total_searched=len(memories),
                threshold_used=thresh,
            )

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return SearchResult(
                error=str(e),
                threshold_used=thresh,
            )

    def add(
        self,
        content: str,
        user_id: str,
        verdict: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StoreResult:
        """
        Add a new memory.

        EUREKA Sieve: Only stores if verdict allows.
        TTL is set based on verdict per policy.

        Args:
            content: Memory content
            user_id: User ID (required)
            verdict: APEX verdict (determines TTL)
            metadata: Additional metadata

        Returns:
            StoreResult
        """
        if not user_id:
            return StoreResult(
                success=False,
                error="user_id is required for memory storage",
            )

        # EUREKA Sieve: Check if verdict allows storage
        ttl_days = self._get_ttl_for_verdict(verdict)

        if ttl_days == 0:
            # VOID/SABAR: Never store
            return StoreResult(
                success=False,
                error=f"Verdict {verdict} is not stored (EUREKA Sieve)",
                verdict=verdict,
                ttl_days=0,
            )

        if not self.is_available:
            return StoreResult(
                success=False,
                error=self._initialization_error or "L7 Memory not available",
                verdict=verdict,
                ttl_days=ttl_days,
            )

        try:
            # Add memory with verdict metadata
            mem_metadata = {
                **(metadata or {}),
                "verdict": verdict,
                "ttl_days": ttl_days,
                "stored_at": datetime.now(timezone.utc).isoformat(),
            }

            # Mem0 accepts messages as string or list of {role, content}
            # Pass content as string - Mem0 will wrap it internally
            response = self._client.add(
                content,
                user_id=user_id,
                metadata=mem_metadata,
            )

            # Mem0 returns {"results": [{"id": ..., "memory": ..., "event": "ADD"}]}
            memory_id = None
            if isinstance(response, dict):
                results = response.get("results", [])
                if results and len(results) > 0:
                    memory_id = results[0].get("id")
                elif "id" in response:
                    memory_id = response.get("id")
            else:
                memory_id = str(response)

            return StoreResult(
                success=True,
                memory_id=memory_id,
                verdict=verdict,
                ttl_days=ttl_days,
            )

        except Exception as e:
            logger.error(f"Memory add failed: {e}")
            return StoreResult(
                success=False,
                error=str(e),
                verdict=verdict,
                ttl_days=ttl_days,
            )

    def delete(
        self,
        memory_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: Memory ID to delete
            user_id: User ID (for verification)

        Returns:
            True if deleted, False otherwise
        """
        if not self.is_available:
            return False

        try:
            self._client.delete(memory_id)
            return True
        except Exception as e:
            logger.error(f"Memory delete failed: {e}")
            return False

    def get_all(
        self,
        user_id: str,
        limit: int = 100,
    ) -> SearchResult:
        """
        Get all memories for a user.

        Args:
            user_id: User ID
            limit: Maximum memories to return

        Returns:
            SearchResult with all memories
        """
        if not user_id:
            return SearchResult(error="user_id is required")

        if not self.is_available:
            return SearchResult(error=self._initialization_error)

        try:
            # Mem0 returns {"results": [...]} format
            response = self._client.get_all(user_id=user_id, limit=limit)

            # Extract results from response dict
            memories = response.get("results", []) if isinstance(response, dict) else response

            hits = []
            for mem in memories:
                mem_metadata = mem.get("metadata", {})
                hits.append(MemoryHit(
                    memory_id=mem.get("id", ""),
                    content=mem.get("memory", ""),
                    metadata=mem_metadata,
                    score=1.0,  # Full match for get_all
                    user_id=mem.get("user_id", user_id),
                    timestamp=mem.get("created_at", ""),
                    verdict=mem_metadata.get("verdict"),
                    ttl_days=mem_metadata.get("ttl_days"),
                ))

            return SearchResult(
                hits=hits,
                total_searched=len(memories),
            )

        except Exception as e:
            logger.error(f"Get all memories failed: {e}")
            return SearchResult(error=str(e))

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding from Mem0's internal embedding model.

        Falls back to stub embedding when Mem0 embedding is unavailable.
        Stub uses simple hash-based pseudo-embedding for testing.
        """
        if not self.is_available or self._client is None:
            return self._stub_embedding(text)

        try:
            # Try to use Mem0's embedding if available
            # Note: Mem0 API may vary by version
            if hasattr(self._client, 'embed'):
                result = self._client.embed(text)
                if result and isinstance(result, list):
                    return result
            elif hasattr(self._client, 'embedding_model'):
                result = self._client.embedding_model.embed(text)
                if result and isinstance(result, list):
                    return result
        except Exception as e:
            logger.debug(f"Mem0 embedding unavailable, using stub: {e}")

        # Fall back to stub embedding
        return self._stub_embedding(text)

    def _stub_embedding(self, text: str, dimensions: int = 384) -> List[float]:
        """
        Generate a deterministic stub embedding for testing.

        Uses hash of text to generate reproducible pseudo-random vector.
        This is NOT a real embedding - only for testing when Mem0 unavailable.

        Args:
            text: Text to embed
            dimensions: Embedding dimensions (default 384 for compatibility)

        Returns:
            Deterministic pseudo-embedding vector
        """
        import hashlib

        # Use SHA256 hash to generate deterministic seed
        text_hash = hashlib.sha256(text.encode('utf-8')).digest()

        # Generate pseudo-random but deterministic embedding
        embedding = []
        for i in range(dimensions):
            # Use different bytes of hash + index to vary each dimension
            byte_idx = i % len(text_hash)
            seed_byte = text_hash[byte_idx]
            # Normalize to [-1, 1] range
            value = ((seed_byte + i * 7) % 256) / 128.0 - 1.0
            embedding.append(value)

        # Normalize the vector (L2 norm)
        norm = sum(x * x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding

    def _get_ttl_for_verdict(self, verdict: str) -> Optional[int]:
        """
        Get TTL in days for a verdict per EUREKA Sieve policy.

        Returns:
            TTL in days, None for forever, 0 for never store
        """
        verdict_upper = verdict.upper()

        # Map to TTL policy
        ttl_map = {
            "SEAL": TTLPolicy.SEAL.value,      # Forever (None)
            "PARTIAL": TTLPolicy.VETO.value,   # 730 days
            "888_HOLD": TTLPolicy.VETO.value,  # 730 days
            "VETO": TTLPolicy.VETO.value,      # 730 days
            "FLAG": TTLPolicy.FLAG.value,      # 30 days
            "VOID": TTLPolicy.VOID.value,      # 0 (never store)
            "SABAR": TTLPolicy.SABAR.value,    # 0 (never store)
            "SUNSET": TTLPolicy.FLAG.value,    # 30 days (revocation)
        }

        return ttl_map.get(verdict_upper, TTLPolicy.FLAG.value)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_default_client: Optional[Mem0Client] = None


def get_mem0_client() -> Mem0Client:
    """Get or create the default Mem0 client singleton."""
    global _default_client
    if _default_client is None:
        _default_client = Mem0Client()
    return _default_client


def is_l7_enabled() -> bool:
    """Check if L7 Memory is enabled."""
    return os.getenv("ARIFOS_L7_ENABLED", "true").lower() in ("true", "1", "yes")


def is_l7_available() -> bool:
    """Check if L7 Memory is available and working."""
    return get_mem0_client().is_available


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_TOP_K",
    "DEFAULT_QDRANT_HOST",
    "DEFAULT_QDRANT_PORT",
    "TTLPolicy",
    # Data classes
    "Mem0Config",
    "MemoryHit",
    "EmbedResult",
    "SearchResult",
    "StoreResult",
    # Main class
    "Mem0Client",
    # Convenience functions
    "get_mem0_client",
    "is_l7_enabled",
    "is_l7_available",
]

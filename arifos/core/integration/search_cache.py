"""Constitutional module - F2 Truth enforced
Part of arifOS constitutional governance system
DITEMPA BUKAN DIBERI - Forged, not given
"""

"""
Constitutional Search Cache with Semantic Deduplication
X7K9F24 - Entropy Reduction via Intelligent Caching

This module implements a constitutional search cache that provides:
- Semantic deduplication with F2 (ΔS) optimization
- TTL management and cost-aware caching
- Constitutional validation for cached results
- Integration with 12-floor governance system

Status: SEALED
Nonce: X7K9F24
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from arifos.core.floors import floor_02_clarity as f2

logger = logging.getLogger("arifos.core.search_cache")


@dataclass
class CacheEntry:
    """Constitutional cache entry with governance metadata."""
    query_hash: str
    query: str
    result: Any
    floor_scores: Dict[str, float]
    timestamp: float
    ttl: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    constitutional_verdict: str = "SEAL"


class ConstitutionalSearchCache:
    """
    Constitutional search cache with semantic deduplication and F2 optimization.
    
    Features:
    - Semantic similarity matching using F2 (ΔS) clarity detection
    - TTL-based expiration with cost-aware management
    - Constitutional validation of cached results
    - LRU eviction with governance-aware scoring
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: float = 3600,  # 1 hour
        semantic_threshold: float = 0.85,  # Similarity threshold for deduplication
        enable_f2_optimization: bool = True
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.semantic_threshold = semantic_threshold
        self.enable_f2_optimization = enable_f2_optimization
        
        # LRU cache implementation
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "semantic_matches": 0,
            "total_requests": 0
        }
        
        logger.info(f"ConstitutionalSearchCache initialized (max_size={max_size}, ttl={default_ttl}s)")
    
    def get(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Get cached result with constitutional validation.
        
        Implements semantic deduplication using F2 (ΔS) optimization:
        1. Check for exact query match
        2. If no exact match, check for semantically similar queries
        3. Validate constitutional compliance of cached result
        4. Update access metrics
        
        Args:
            query: Search query
            context: Optional context for semantic matching
            
        Returns:
            Cached result if valid, None otherwise
        """
        self._stats["total_requests"] += 1
        context = context or {}
        
        # Generate query hash
        query_hash = self._hash_query(query, context)
        
        # Check for exact match
        if query_hash in self._cache:
            entry = self._cache[query_hash]
            
            # Check TTL
            if time.time() - entry.timestamp > entry.ttl:
                # Entry expired
                del self._cache[query_hash]
                self._stats["misses"] += 1
                logger.debug(f"Cache miss (expired): '{query[:50]}...'")
                return None
            
            # Validate constitutional compliance
            if not self._validate_constitutional_compliance(entry):
                # Constitutional violation detected
                del self._cache[query_hash]
                self._stats["misses"] += 1
                logger.warning(f"Cache miss (constitutional violation): '{query[:50]}...'")
                return None
            
            # Update access metrics
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            # Move to end (LRU)
            self._cache.move_to_end(query_hash)
            
            self._stats["hits"] += 1
            logger.debug(f"Cache hit (exact): '{query[:50]}...' (accesses: {entry.access_count})")
            return entry.result
        
        # Check for semantic match if F2 optimization is enabled
        if self.enable_f2_optimization:
            semantic_match = self._find_semantic_match(query, context)
            if semantic_match:
                self._stats["semantic_matches"] += 1
                self._stats["hits"] += 1
                logger.debug(f"Cache hit (semantic): '{query[:50]}...' -> '{semantic_match.query[:50]}...'")
                return semantic_match.result
        
        self._stats["misses"] += 1
        logger.debug(f"Cache miss: '{query[:50]}...'")
        return None
    
    def put(
        self,
        query: str,
        result: Any,
        context: Optional[Dict[str, Any]] = None,
        ttl: Optional[float] = None,
        floor_scores: Optional[Dict[str, float]] = None
    ) -> bool:
        """
        Store result in cache with constitutional validation.
        
        Args:
            query: Search query
            result: Search result to cache
            context: Optional context
            ttl: Optional custom TTL (uses default if None)
            floor_scores: Constitutional floor scores from search
            
        Returns:
            True if stored successfully, False otherwise
        """
        context = context or {}
        ttl = ttl or self.default_ttl
        floor_scores = floor_scores or {}
        
        # Generate query hash
        query_hash = self._hash_query(query, context)
        
        # Validate result constitutionally before caching
        if not self._validate_result_for_caching(result, floor_scores):
            logger.warning(f"Result not cached due to constitutional validation failure: '{query[:50]}...'")
            return False
        
        # Check cache size and evict if necessary
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        # Create cache entry
        entry = CacheEntry(
            query_hash=query_hash,
            query=query,
            result=result,
            floor_scores=floor_scores,
            timestamp=time.time(),
            ttl=ttl,
            access_count=1,
            constitutional_verdict=self._compute_constitutional_verdict(floor_scores)
        )
        
        # Store in cache
        self._cache[query_hash] = entry
        self._cache.move_to_end(query_hash)  # Mark as recently used
        
        logger.debug(f"Cached result: '{query[:50]}...' (ttl: {ttl}s)")
        return True
    
    def _hash_query(self, query: str, context: Dict[str, Any]) -> str:
        """Generate hash for query and context."""
        # Include relevant context in hash
        hash_data = {
            "query": query.lower().strip(),
            "user_id": context.get("user_id"),
            "search_providers": sorted(context.get("search_providers", [])),
            "constitutional_mode": context.get("constitutional_mode", "normal")
        }
        
        hash_input = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _find_semantic_match(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Optional[CacheEntry]:
        """
        Find semantically similar query using F2 (ΔS) optimization.
        
        Args:
            query: New query to match
            context: Search context
            
        Returns:
            Best semantic match or None
        """
        best_match = None
        best_score = 0.0
        
        for entry in self._cache.values():
            # Skip expired entries
            if time.time() - entry.timestamp > entry.ttl:
                continue
            
            # Skip constitutionally invalid entries
            if not self._validate_constitutional_compliance(entry):
                continue
            
            # Calculate semantic similarity using F2 clarity
            try:
                # Use F2's clarity detection for semantic similarity
                clarity_result = f2.compute_clarity_delta(query, entry.query)
                similarity_score = clarity_result.get("clarity_score", 0.0)
                
                # Invert for similarity (higher clarity delta = lower similarity)
                semantic_score = max(0.0, 1.0 - similarity_score)
                
                if semantic_score > best_score and semantic_score >= self.semantic_threshold:
                    best_score = semantic_score
                    best_match = entry
                    
            except Exception as e:
                logger.warning(f"F2 semantic matching error: {e}")
                continue
        
        return best_match
    
    def _validate_constitutional_compliance(self, entry: CacheEntry) -> bool:
        """
        Validate cached result for constitutional compliance.
        
        Args:
            entry: Cache entry to validate
            
        Returns:
            True if compliant, False otherwise
        """
        # Check if entry has valid constitutional verdict
        if entry.constitutional_verdict not in ["SEAL", "PARTIAL"]:
            return False
        
        # Check critical floors
        critical_floors = ["F1", "F2", "F6", "F9", "F10", "F11", "F12"]
        for floor in critical_floors:
            score = entry.floor_scores.get(floor, 1.0)
            if score < 0.5:  # Critical floor failure
                return False
        
        return True
    
    def _validate_result_for_caching(
        self,
        result: Any,
        floor_scores: Dict[str, float]
    ) -> bool:
        """
        Validate search result before allowing it to be cached.
        
        Args:
            result: Search result
            floor_scores: Constitutional floor scores
            
        Returns:
            True if valid for caching, False otherwise
        """
        # Don't cache VOID results
        verdict = self._compute_constitutional_verdict(floor_scores)
        if verdict == "VOID":
            return False
        
        # Check for critical floor failures
        critical_floors = ["F1", "F2", "F6", "F9", "F10", "F11", "F12"]
        for floor in critical_floors:
            score = floor_scores.get(floor, 1.0)
            if score < 0.3:  # Severe floor failure
                return False
        
        return True
    
    def _compute_constitutional_verdict(self, floor_scores: Dict[str, float]) -> str:
        """Compute constitutional verdict from floor scores."""
        # Critical floors that must pass
        critical_floors = ["F1", "F2", "F6", "F9", "F10", "F11", "F12"]
        
        # Check for any critical floor failures
        for floor in critical_floors:
            score = floor_scores.get(floor, 1.0)
            if score < 0.5:
                return "VOID"
        
        # Check soft floors
        soft_floors = ["F3", "F4", "F5", "F7", "F8"]
        soft_failures = 0
        
        for floor in soft_floors:
            score = floor_scores.get(floor, 1.0)
            if score < 0.7:
                soft_failures += 1
        
        if soft_failures > 0:
            return "PARTIAL"
        
        return "SEAL"
    
    def _evict_lru(self) -> Optional[CacheEntry]:
        """
        Evict least recently used entry with governance-aware scoring.
        
        Uses constitutional scoring to preferentially keep higher-quality entries.
        
        Returns:
            Evicted entry or None if cache is empty
        """
        if not self._cache:
            return None
        
        # Find entry with lowest governance score (least valuable)
        best_evict_score = float('inf')
        best_evict_key = None
        best_evict_entry = None
        
        for key, entry in self._cache.items():
            # Compute eviction score (lower = better to evict)
            # Factors: age, access frequency, constitutional quality
            age_score = (time.time() - entry.timestamp) / self.default_ttl
            access_score = 1.0 / (entry.access_count + 1)  # Lower access = better to evict
            
            # Constitutional quality score (lower quality = better to evict)
            quality_score = 1.0
            if entry.constitutional_verdict == "PARTIAL":
                quality_score = 0.7
            elif entry.constitutional_verdict == "VOID":
                quality_score = 0.0
            
            # Combine scores (weighted)
            evict_score = (
                age_score * 0.4 +           # Older entries are better to evict
                access_score * 0.3 +        # Less accessed entries are better to evict
                (1.0 - quality_score) * 0.3  # Lower quality entries are better to evict
            )
            
            if evict_score < best_evict_score:
                best_evict_score = evict_score
                best_evict_key = key
                best_evict_entry = entry
        
        if best_evict_key:
            del self._cache[best_evict_key]
            self._stats["evictions"] += 1
            logger.debug(f"Evicted cache entry: '{best_evict_entry.query[:50]}...' (score: {best_evict_score:.2f})")
            return best_evict_entry
        
        return None
    
    def clear_expired(self) -> int:
        """
        Clear expired entries from cache.
        
        Returns:
            Number of entries cleared
        """
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if current_time - entry.timestamp > entry.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "semantic_matches": self._stats["semantic_matches"],
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    def get_entry_info(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific cache entry.
        
        Args:
            query: Search query
            context: Optional context
            
        Returns:
            Entry information or None if not found
        """
        context = context or {}
        query_hash = self._hash_query(query, context)
        
        entry = self._cache.get(query_hash)
        if not entry:
            return None
        
        return {
            "query": entry.query,
            "timestamp": entry.timestamp,
            "ttl": entry.ttl,
            "age": time.time() - entry.timestamp,
            "access_count": entry.access_count,
            "last_accessed": entry.last_accessed,
            "constitutional_verdict": entry.constitutional_verdict,
            "floor_scores": entry.floor_scores,
            "time_remaining": max(0, entry.ttl - (time.time() - entry.timestamp))
        }


class TTLAwareCache:
    """
    Simple TTL-aware cache for cost tracking and budget management.
    
    Used internally by ConstitutionalSearchCache for managing
    cost-related data with automatic expiration.
    """
    
    def __init__(self):
        self._data: Dict[str, Tuple[Any, float]] = {}  # key -> (value, expiry_time)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value if not expired."""
        if key not in self._data:
            return None
        
        value, expiry_time = self._data[key]
        if time.time() > expiry_time:
            del self._data[key]
            return None
        
        return value
    
    def put(self, key: str, value: Any, ttl: float) -> None:
        """Store value with TTL."""
        expiry_time = time.time() + ttl
        self._data[key] = (value, expiry_time)
    
    def clear_expired(self) -> int:
        """Clear expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry_time) in self._data.items()
            if current_time > expiry_time
        ]
        
        for key in expired_keys:
            del self._data[key]
        
        return len(expired_keys)
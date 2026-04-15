"""
Shadow Comparator — A/B Testing for Backend Versions

Runs v1 and v2 backends in parallel, logs differences.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

@dataclass
class ShadowComparison:
    """Result of shadow comparison."""
    tool: str
    match: bool
    v1_duration_ms: float
    v2_duration_ms: float
    ranking_delta: float
    vault_backed_boosted: bool
    contested_penalty_applied: bool
    v1_result_hash: str
    v2_result_hash: str
    details: dict[str, Any] = field(default_factory=dict)

class ShadowComparator:
    """
    Compare v1 and v2 backend results.
    
    Logs differences but doesn't block v1 responses.
    """
    
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold  # Drift threshold for alerting
    
    async def compare_memory(
        self,
        query: str,
        v1_backend: callable,
        v2_backend: callable,
    ) -> ShadowComparison:
        """Compare memory backend results."""
        
        # Execute in parallel
        v1_task = self._timed_exec(v1_backend, query)
        v2_task = self._timed_exec(v2_backend, query)
        
        (v1_result, v1_duration), (v2_result, v2_duration) = await asyncio.gather(
            v1_task, v2_task
        )
        
        # Calculate hashes
        v1_hash = self._hash_result(v1_result)
        v2_hash = self._hash_result(v2_result)
        
        # Extract v2 features
        v2_records = v2_result.get("results", [])
        vault_backed = any(r.get("_vault_backed") for r in v2_records)
        contested = any(r.get("_contested") != "uncontested" for r in v2_records)
        
        # Calculate ranking delta
        ranking_delta = self._calculate_ranking_delta(v1_result, v2_result)
        
        comparison = ShadowComparison(
            tool="arifos_memory",
            match=(v1_hash == v2_hash),
            v1_duration_ms=v1_duration * 1000,
            v2_duration_ms=v2_duration * 1000,
            ranking_delta=ranking_delta,
            vault_backed_boosted=vault_backed,
            contested_penalty_applied=contested,
            v1_result_hash=v1_hash[:16],
            v2_result_hash=v2_hash[:16],
            details={
                "v1_top_result": self._extract_top(v1_result),
                "v2_top_result": self._extract_top(v2_result),
                "confidence_classes": [r.get("_confidence_class") for r in v2_records[:5]],
            }
        )
        
        # Log if drift detected
        if ranking_delta > self.threshold:
            logger.warning(
                f"Shadow drift detected: {ranking_delta:.2%}",
                extra={"shadow_comparison": comparison.to_dict()}
            )
        
        return comparison
    
    async def compare_vault(
        self,
        entry: Any,
        v1_backend: callable,
        v2_backend: callable,
    ) -> ShadowComparison:
        """Compare vault backend results."""
        
        v1_task = self._timed_exec(v1_backend, entry)
        v2_task = self._timed_exec(v2_backend, entry)
        
        (v1_result, v1_duration), (v2_result, v2_duration) = await asyncio.gather(
            v1_task, v2_task
        )
        
        v1_hash = self._hash_result(v1_result)
        v2_hash = self._hash_result(v2_result)
        
        # Check v2 verification grades
        grade = v2_result.get("verification_grade", {})
        
        comparison = ShadowComparison(
            tool="arifos_vault",
            match=(v1_hash == v2_hash),
            v1_duration_ms=v1_duration * 1000,
            v2_duration_ms=v2_duration * 1000,
            ranking_delta=0.0,  # Not applicable for vault
            vault_backed_boosted=False,
            contested_penalty_applied=False,
            v1_result_hash=v1_hash[:16],
            v2_result_hash=v2_hash[:16],
            details={
                "v2_verification_grade": grade,
                "v2_chain_valid": grade.get("chain_valid"),
                "v2_hash_match": grade.get("hash_match"),
            }
        )
        
        # Log if v2 verification fails
        if not grade.get("fully_valid"):
            logger.error(
                "V2 vault verification failed",
                extra={"shadow_comparison": comparison.to_dict()}
            )
        
        return comparison
    
    async def _timed_exec(self, backend: callable, *args) -> tuple[Any, float]:
        """Execute with timing."""
        import time
        start = time.monotonic()
        result = await backend(*args)
        duration = time.monotonic() - start
        return result, duration
    
    def _hash_result(self, result: Any) -> str:
        """Hash result for comparison."""
        content = json.dumps(result, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _calculate_ranking_delta(self, v1_result: dict, v2_result: dict) -> float:
        """Calculate ranking difference between results."""
        v1_ids = [r.get("memory_id") for r in v1_result.get("results", [])]
        v2_ids = [r.get("memory_id") for r in v2_result.get("results", [])]
        
        if not v1_ids or not v2_ids:
            return 0.0
        
        # Calculate Kendall tau distance (simplified)
        matches = sum(1 for a, b in zip(v1_ids, v2_ids) if a == b)
        return 1.0 - (matches / max(len(v1_ids), len(v2_ids)))
    
    def _extract_top(self, result: dict) -> Optional[str]:
        """Extract top result ID."""
        results = result.get("results", [])
        if results:
            return results[0].get("memory_id") or results[0].get("title")
        return None
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize comparison."""
        return {
            "tool": self.tool,
            "match": self.match,
            "v1_duration_ms": self.v1_duration_ms,
            "v2_duration_ms": self.v2_duration_ms,
            "ranking_delta": self.ranking_delta,
            "vault_backed_boosted": self.vault_backed_boosted,
            "contested_penalty_applied": self.contested_penalty_applied,
            "v1_result_hash": self.v1_result_hash,
            "v2_result_hash": self.v2_result_hash,
            "details": self.details,
        }


async def run_shadow_comparison(
    tool: str,
    *args,
    **kwargs
) -> Optional[ShadowComparison]:
    """
    Convenience function for shadow comparison.
    
    Only runs if ENABLE_SHADOW_COMPARE=true.
    """
    import os
    if os.getenv("ENABLE_SHADOW_COMPARE", "false").lower() != "true":
        return None
    
    from ..tools_hardened_dispatch import get_shadow_backends
    
    backends = get_shadow_backends()
    if tool not in backends:
        return None
    
    v1_impl, v2_impl = backends[tool]
    comparator = ShadowComparator()
    
    if tool == "arifos_memory":
        return await comparator.compare_memory(args[0], v1_impl, v2_impl)
    elif tool == "arifos_vault":
        return await comparator.compare_vault(args[0], v1_impl, v2_impl)
    
    return None

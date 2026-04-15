"""
Memory Backend Compatibility Layer

Routes arifos.memory calls to v1 or v2 implementation.
"""

from __future__ import annotations

import os
from typing import Any, Optional

# Determine backend version
MEMORY_BACKEND_VERSION = os.getenv("MEMORY_BACKEND_VERSION", "v1")

class MemoryBackend:
    """
    Compatibility wrapper for memory backends.
    
    Public interface remains stable while internal implementation
    can be v1 (legacy) or v2 (hardened).
    """
    
    def __init__(self):
        self.version = MEMORY_BACKEND_VERSION
        self._backend = self._load_backend()
    
    def _load_backend(self):
        """Load appropriate backend."""
        if self.version == "v2":
            # Import v2 hardened organ
            try:
                from core.organs.memory.memory_organ import MemoryOrgan
                return MemoryOrgan()
            except ImportError:
                # Fall back to v1 if v2 not available
                return self._load_v1()
        else:
            return self._load_v1()
    
    def _load_v1(self):
        """Load v1 legacy backend."""
        from ..megaTools.tool_07_engineering_memory import engineering_memory
        return engineering_memory
    
    async def query(self, query: str, mode: str = "query", **kwargs) -> dict[str, Any]:
        """
        Canonical memory query.
        
        Returns standardized response regardless of backend version.
        """
        if self.version == "v2":
            result = await self._backend.query(query)
            return self._format_v2_response(result)
        else:
            result = await self._backend(query=query, mode=mode, **kwargs)
            return self._format_v1_response(result)
    
    def _format_v2_response(self, records: list) -> dict[str, Any]:
        """Format v2 records to canonical response."""
        return {
            "canonical_tool_name": "arifos.memory",
            "tool": "arifos.memory",
            "stage": "555_MEMORY",
            "results": [
                {
                    "memory_id": r.memory_id,
                    "title": r.title,
                    "content": r.content,
                    # Internal fields for debugging
                    "_confidence_class": r.governance.confidence_class.value,
                    "_source_weight": r.retrieval.source_weight,
                    "_vault_backed": r.retrieval.vault_backed,
                    "_contested": r.governance.contested.value,
                    "_lane": r.memory_type.value,
                }
                for r in records
            ],
            "backend_version": "v2",
        }
    
    def _format_v1_response(self, result: Any) -> dict[str, Any]:
        """Format v1 response to canonical shape."""
        if isinstance(result, dict):
            result["canonical_tool_name"] = "arifos.memory"
            result["tool"] = "arifos.memory"
            result["stage"] = "555_MEMORY"
            result["backend_version"] = "v1"
        return result


# Singleton instance
_memory_backend: Optional[MemoryBackend] = None

def get_memory_backend() -> MemoryBackend:
    """Get or create memory backend."""
    global _memory_backend
    if _memory_backend is None:
        _memory_backend = MemoryBackend()
    return _memory_backend

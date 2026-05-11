"""
arifosmcp/memory_engine.py -- DEPRECATED
═══════════════════════════════════════════

This module is DEPRECATED as of 2026-05-11.

CONSOLIDATION: All memory functionality has been unified into:
  - arifosmcp/runtime/memory_store.py (canonical backend)
  - arifosmcp/memory/vector_memory_qdrant.py (vector operations)

The memory_engine.py dual-write architecture (Postgres + Qdrant + Supabase +
Langfuse) was overly complex and fragmented the memory subsystem. It has been
replaced by a simpler, more robust design:

  Qdrant (vectors) + Ollama bge-m3 (embeddings) + JSON index (id mapping)

If you need the features from this module (Supabase dual-write, Langfuse
tracing), open an issue to discuss re-integration into the canonical backend.

DITEMPA BUKAN DIBERI -- Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("memory_engine")
logger.warning(
    "memory_engine.py is DEPRECATED. Use arifosmcp.runtime.memory_store instead."
)


class MemoryEngine:
    """Deprecated. Use arifosmcp.runtime.memory_store or vector_memory_qdrant."""

    def __init__(self, *args, **kwargs):
        logger.warning("MemoryEngine is deprecated. Use memory_store.store() instead.")

    async def store(self, *args, **kwargs) -> dict[str, Any]:
        raise RuntimeError(
            "MemoryEngine is deprecated. Use arifosmcp.runtime.memory_store.store()"
        )

    async def recall(self, *args, **kwargs) -> dict[str, Any]:
        raise RuntimeError(
            "MemoryEngine is deprecated. Use arifosmcp.runtime.memory_store.recall()"
        )

    async def search(self, *args, **kwargs) -> dict[str, Any]:
        raise RuntimeError(
            "MemoryEngine is deprecated. Use arifosmcp.runtime.memory_store.search()"
        )

    async def get_embedding(self, *args, **kwargs) -> list[float]:
        raise RuntimeError(
            "MemoryEngine is deprecated. Use vector_memory_qdrant._generate_embedding()"
        )

"""
Promotion Backend Compatibility Layer

Routes promotion bridge to v1 or v2 implementation.
"""

from __future__ import annotations

import os
from typing import Any, Optional

# Determine backend version
PROMOTION_BACKEND_VERSION = os.getenv("PROMOTION_BACKEND_VERSION", "v1")

class PromotionBackend:
    """
    Compatibility wrapper for promotion bridge.
    
    Controls which memories get promoted to vault.
    """
    
    def __init__(self, memory_backend=None, vault_backend=None):
        self.version = PROMOTION_BACKEND_VERSION
        self._memory = memory_backend
        self._vault = vault_backend
        self._backend = self._load_backend()
    
    def _load_backend(self):
        """Load appropriate backend."""
        if self.version == "v2":
            try:
                from core.organs.bridge.promotion_v2 import PromotionBridge, PromotionOutcome
                return PromotionBridge(self._memory, self._vault)
            except ImportError:
                return None  # V1 didn't have explicit promotion
        return None
    
    async def promote(self, memory_id: str, session_id: str) -> dict[str, Any]:
        """
        Promote memory to vault.
        
        Returns outcome with explicit classification.
        """
        if self.version == "v2" and self._backend:
            result = self._backend.promote(memory_id, session_id)
            return {
                "outcome": result.outcome.value if result else "rejected_non_consequential",
                "memory_id": memory_id,
                "vault_id": result.vault_id if result else None,
                "reason": result.reason if result else "No result",
                "backend_version": "v2",
            }
        else:
            # V1: implicit promotion or no promotion
            return {
                "outcome": "legacy_no_promotion",
                "memory_id": memory_id,
                "vault_id": None,
                "backend_version": "v1",
            }
    
    async def process_session(self, session_id: str) -> dict[str, Any]:
        """Process all session memories for promotion."""
        if self.version == "v2" and self._backend:
            results = await self._backend.process_session_for_promotion(session_id)
            summary = self._backend.get_promotion_summary(results)
            return {
                "session_id": session_id,
                "processed": len(results),
                "summary": summary,
                "backend_version": "v2",
            }
        return {
            "session_id": session_id,
            "processed": 0,
            "backend_version": "v1",
        }


def get_promotion_backend(memory_backend=None, vault_backend=None) -> PromotionBackend:
    """Get or create promotion backend."""
    return PromotionBackend(memory_backend, vault_backend)

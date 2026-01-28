"""
APEX Judicial Core - Codebase Native Implementation (v53.2.1)
Soul Kernel (Ψ) for the Trinity Architecture.

This implementation executes APEX stages (444, 888) natively within the codebase room structure.
It replaces the legacy arifos/core proxy.

DITEMPA BUKAN DIBERI
"""

import logging
from typing import Any, Dict, Optional

from codebase.engines.apex.apex_engine import get_apex_room
from codebase.bundle_store import MergedBundle

logger = logging.getLogger(__name__)

class APEXJudicialCore:
    """
    APEX Soul Kernel (Ψ) - Native Codebase Implementation.
    
    Handles: TRINITY_SYNC (444) → JUDGE (888) → SEAL (999)
    Isolation: Runs in a dedicated APEXRoom.
    """

    def __init__(self):
        self.version = "v53.2.1-CODEBASE"
        logger.info(f"APEXJudicialCore ignited ({self.version})")

    async def judge(self, session_id: str, **kwargs) -> Dict[str, Any]:
        """Stage 444/888: Judicial Review (Native)."""
        room = get_apex_room(session_id)
        merged = await room.run_trinity_sync()
        
        return {
            "stage": "444_trinity_sync",
            "status": merged.pre_verdict,
            "verdict": merged.pre_verdict,
            "consensus_score": merged.consensus.consensus_score,
            "dissent_triggered": not merged.consensus.votes_agree,
            "reason": merged.pre_verdict_reason,
            "bundle_hash": merged.bundle_hash,
            "_bundle": merged # For post-444 stages
        }

    async def seal(self, session_id: str, **kwargs) -> Dict[str, Any]:
        """Stage 999: Seal (Native)."""
        # Sealing logic handled by VaultNative in Phase 5.
        # This provides compatibility for the kernel interface.
        return {
            "stage": "999_seal",
            "status": "SEALED",
            "sealed": True
        }

    async def execute(self, action: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Unified APEX execution entry point."""
        session_id = kwargs.get("session_id", "default_session")
        
        if action in ["full", "judge", "sync"]:
            return await self.judge(session_id, **kwargs)
        elif action == "seal":
            return await self.seal(session_id, **kwargs)
        else:
            return {"error": f"Unknown APEX action: {action}", "status": "ERROR"}

# Backward Compatibility
APEXKernel = APEXJudicialCore

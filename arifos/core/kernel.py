"""
arifOS Kernel Manager (v52.0.0 SEAL)
Authority: Muhammad Arif bin Fazil
Principle: Unified Core Orchestration

Provides a singleton access point for all constitutional engines.
"""

from __future__ import annotations
import logging
from typing import Optional

from arifos.core.agi.kernel import AGINeuralCore
from arifos.core.asi.kernel import ASIActionCore
from arifos.core.apex.kernel import APEXJudicialCore
from arifos.core.memory.vault.vault_manager import VaultManager
from arifos.core.prompt.router import route_prompt

logger = logging.getLogger("arifos.core.kernel")

class KernelManager:
    """
    Central orchestrator for arifOS kernels.
    """
    def __init__(self):
        self._agi = AGINeuralCore()
        self._asi = ASIActionCore()
        self._apex = APEXJudicialCore()
        self._vault = VaultManager()
        logger.info("KernelManager initialized with Trinity engines")

    def get_agi(self) -> AGINeuralCore:
        return self._agi

    def get_asi(self) -> ASIActionCore:
        return self._asi

    def get_apex(self) -> APEXJudicialCore:
        return self._apex

    def get_vault(self) -> VaultManager:
        return self._vault

    def get_prompt_router(self):
        return route_prompt

    async def init_session(self, action: str, kwargs: dict) -> dict:
        """Initialize a new metabolic session."""
        import uuid, time
        session_id = kwargs.get("session_id") or str(uuid.uuid4())
        return {
            "session_id": session_id,
            "timestamp": time.time(),
            "status": "READY",
            "action": action,
            "version": "v52.0.0"
        }

# Singleton instance
_manager: Optional[KernelManager] = None

def get_kernel_manager() -> KernelManager:
    """Get the global KernelManager instance."""
    global _manager
    if _manager is None:
        _manager = KernelManager()
    return _manager

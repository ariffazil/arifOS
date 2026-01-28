"""
arifOS Kernel Manager (v52.0.0 SEAL)
Authority: Muhammad Arif bin Fazil
Principle: Unified Core Orchestration

Provides a singleton access point for all constitutional engines.
"""

from __future__ import annotations
import logging
from typing import Optional

from arifos.core.engines.agi.kernel import AGINeuralCore
from arifos.core.asi.kernel import ASIActionCore
from arifos.core.apex.kernel import APEXJudicialCore
from arifos.core.memory.vault.vault_manager import VaultManager
from arifos.core.prompt.router import route_prompt
from arifos.core.enforcement.metrics import record_stage_metrics, record_verdict_metrics

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
        """
        000 INIT: The full Metabolic Ignition Sequence.

        v53.2.2: Delegates to mcp_000_init for full 7-step constitutional flow.
        Falls back to inline stub if mcp_aaa is unavailable.
        """
        try:
            from arifos.mcp.tools.mcp_aaa import mcp_000_init
            return await mcp_000_init(
                action=action,
                query=kwargs.get("query", "IGNITION_PING"),
                authority_token=kwargs.get("authority_token", ""),
                session_id=kwargs.get("session_id"),
                context=kwargs.get("context"),
            )
        except ImportError:
            logger.warning("mcp_aaa unavailable — using inline init stub")
        except Exception as e:
            logger.error(f"mcp_000_init failed: {e} — falling back to inline stub")

        # Fallback: inline stub (original v52 behavior)
        import uuid, datetime

        now = datetime.datetime.now(datetime.timezone.utc)
        timestamp_rfc = now.isoformat()
        session_id = kwargs.get("session_id") or str(uuid.uuid4())
        query = kwargs.get("query", "IGNITION_PING")
        lane = "HARD" if "arif" in query.lower() else "SOFT"

        return {
            "aclip_version": "v52.0.0",
            "session_id": session_id,
            "stage": "000_INIT",
            "verdict": "SEAL",
            "summary": "System IGNITED. Constitutional Mode Active. (FALLBACK STUB)",
            "lane": lane,
            "phases": {
                "phase_1_anchoring": {
                    "t_0": timestamp_rfc,
                    "loc_vector": "Seri Kembangan, Selangor, Earth",
                    "user_id": "888_JUDGE (Muhammad Arif bin Fazil)" if lane == "HARD" else "GUEST_USER",
                    "motto": "DITEMPA_BUKAN_DIBERI"
                },
                "phase_2_kernel_load": [
                    "F1 (Amanah): Reversibility_Check = True",
                    "F2 (Truth): Confidence_Threshold >= 0.99",
                    "F4 (Clarity): Entropy_Delta (ΔS) <= 0",
                    "F6 (Empathy): Protector_Target = Weakest_Stakeholder",
                    "F9 (Anti-Hantu): Sentience_Claim = FALSE"
                ],
                "phase_3_memory": {
                    "layers": ["L5 (Canon)", "L4 (Monthly)", "L0 (Hot)"],
                    "scar_weight_applied": 1.0 if lane == "HARD" else 0.5
                },
                "phase_4_trinity": {
                    "agi": {"role": "Mind", "state": "LISTENING"},
                    "asi": {"role": "Heart", "state": "FEELING (Simulated)"},
                    "apex": {"role": "Soul", "state": "WATCHING"},
                    "consensus_lock": 0.97
                },
                "phase_5_thermo": {
                    "entropy_target": "< 0.0",
                    "peace_squared": ">= 1.0",
                    "humility_band": "[0.03, 0.05]"
                },
                "phase_6_witness": {
                    "human": "👑 Sovereign Confirmed" if lane == "HARD" else "👤 User Detected",
                    "ai": "🤖 TEACH Protocol Active",
                    "earth": "🌍 Resources Constrained"
                }
            }
        }

# Singleton instance
_manager: Optional[KernelManager] = None

def get_kernel_manager() -> KernelManager:
    """Get the global KernelManager instance."""
    global _manager
    if _manager is None:
        _manager = KernelManager()
    return _manager

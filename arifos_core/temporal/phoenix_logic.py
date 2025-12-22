"""
arifOS v45 - Phoenix Hold Logic (Sovereign Witness)
Enforces 72-hour cooling for High Stakes (T4) or Imperfect Evidence.
"""

from arifos_core.evidence.evidence_pack import EvidencePack
import time


class PhoenixLogic:
    """
    Encapsulates v45 Phoenix-72 Hold Policy.
    """

    PHOENIX_WINDOW_SECONDS = 72 * 3600  # 72 hours

    @staticmethod
    def evaluate_hold(pack: EvidencePack, tier: str = "T1") -> str:
        """
        Determine if a Phoenix Hold is required.
        Returns "SEAL" (go ahead) or "HOLD_888" (cool down).
        """
        # 1. Tier-4 / High Stakes Triggers
        if tier == "T4":
            # Mandatory Cooling for High Stakes if ANY imperfection
            if pack.conflict_flag:
                return "HOLD_888"
            if pack.coverage_pct < 1.0:
                return "HOLD_888"
            if pack.freshness_score < 0.9:  # Strict freshness for T4
                return "HOLD_888"

        # 2. General Conflict Trigger (All Tiers) - Optional but good practice?
        # Unitized MN implies strictness for T4 mainly.
        # But if conflict_flag is True, usually we HOLD anyway via ConflictRouter.
        # PhoenixLogic supplements ConflictRouter by adding TIME dimension.

        return "SEAL"

    @staticmethod
    def check_cooling_status(entry_timestamp: float) -> bool:
        """
        Check if the cooling window has passed for a HOLD entry.
        """
        elapsed = time.time() - entry_timestamp
        return elapsed >= PhoenixLogic.PHOENIX_WINDOW_SECONDS

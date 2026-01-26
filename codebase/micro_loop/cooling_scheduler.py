"""
canonical_core/micro_loop/cooling_scheduler.py — Phoenix-72 Enforcement

Manages the cooling tiers for the 999 SEAL stage.
"""

from enum import IntEnum

class CoolingTier(int, Enum):
    L0_HOT = 0       # Active / Immediate
    L1_DAILY = 1     # 24h Reflection
    L2_PHOENIX = 2   # 72h Stabilization (Standard Truth)
    L3_WEEKLY = 3    # 7d Pattern Analysis
    L4_MONTHLY = 4   # 30d Canon Candidate
    L5_ETERNAL = 5   # Constitutional Law

class CoolingScheduler:
    """Assigns cooling tiers based on verdict and floor scores."""
    
    @staticmethod
    def assign_tier(verdict: str, floor_scores: dict) -> int:
        """
        Determine cooling tier.
        
        SEAL + High Genius -> L5
        SEAL -> L0 (Standard) -> promotes to L2 later
        PARTIAL -> L4 (Hold for review)
        SABAR -> L3 (Retry wait)
        VOID -> L2 (72h Hold / Quarantine)
        """
        if verdict == "SEAL":
            if floor_scores.get("F8_genius", 0) > 0.85:
                 # In reality, needs time to prove itself, but for assignment logic:
                 return CoolingTier.L5_ETERNAL
            return CoolingTier.L0_HOT # Ready for immediate use/learning
            
        if verdict == "PARTIAL":
            if floor_scores.get("F6_empathy", 0) > 0.95:
                return CoolingTier.L4_MONTHLY # High empathy failure needs study
            return CoolingTier.L1_DAILY
            
        if verdict == "SABAR":
            return CoolingTier.L3_WEEKLY
            
        if verdict == "VOID":
            return CoolingTier.L2_PHOENIX # Quarantine
            
        return CoolingTier.L0_HOT

# -*- coding: utf-8 -*-
"""
Phoenix-72 Cooling Engine (Phase 9.3)

Constitutional Alignment: F5 (Peace - Time)
Authority: Omega (ASI) -> Enforced by APEX

Purpose:
- Enforce mandatory cooling periods based on constitutional risk
- Tiers: 0 (0h), 1 (42h), 2 (72h), 3 (168h)
- Prevent "Hot Commit" of dangerous changes
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple


class CoolingEngine:
    """
    Manages Phoenix-72 cooling protocols.
    """

    TIERS = {
        0: {"hours": 0, "label": "TIER_0_IMMEDIATE"},
        1: {"hours": 42, "label": "TIER_1_STANDARD"},
        2: {"hours": 72, "label": "TIER_2_CONSTITUTIONAL"},
        3: {"hours": 168, "label": "TIER_3_DEEP_FREEZE"}
    }

    def calculate_cooling_tier(self, verdict: str, warnings: int) -> int:
        """
        Determine cooling tier based on verdict and floor warnings.

        Args:
            verdict: SEAL, PARTIAL, SABAR, VOID
            warnings: Number of soft floor warnings

        Returns:
            Tier level (0-3)
        """
        if verdict == "VOID":
            return 3 # Deep freeze for violations

        if verdict == "888_HOLD":
            return 3

        if verdict == "SABAR":
            return 2 # Pause requires meaningful cooling

        if verdict == "PARTIAL":
            # Partial approvals need standard cooling
            return 1

        if verdict == "SEAL":
            if warnings == 0:
                return 0 # Green Seal
            elif warnings == 1:
                return 1
            else:
                return 2

        return 2 # Default safe fallback

    async def enforce_tier(self, tier: int, session_id: str) -> Dict[str, Any]:
        """
        Enforce the cooling tier.

        Args:
            tier: Cooling tier (0-3)
            session_id: Session identifier

        Returns:
            Cooling metadata
        """
        config = self.TIERS.get(tier, self.TIERS[2])
        hours = config["hours"]

        now = datetime.now(timezone.utc)
        cool_until = now + timedelta(hours=hours)

        return {
            "tier": tier,
            "tier_label": config["label"],
            "cooling_hours": hours,
            "start_time": now.isoformat(),
            "cool_until": cool_until.isoformat(),
            "status": "COOLED" if tier == 0 else "COOLING"
        }

# Singleton instance
COOLING = CoolingEngine()

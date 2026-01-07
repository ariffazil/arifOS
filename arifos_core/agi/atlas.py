"""
ATLAS-333 — Governance Placement Vector (GPV) Mapping

Stage 333 REASON: Maps inputs to constitutional governance space.

The ATLAS (Architectural Truth Layout and Semantic mapping) provides
a coordinate system for governance decisions.

v46 Trinity Orthogonal: ATLAS belongs to AGI (Δ) kernel.

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Dict, Literal, Optional


# Lane types for conditional kernel invocation
LaneType = Literal["SOCIAL", "CARE", "FACTUAL", "CRISIS"]


@dataclass
class GPV:
    """Governance Placement Vector — constitutional coordinate."""
    lane: LaneType
    truth_demand: float  # 0.0-1.0, how much truth verification needed
    care_demand: float  # 0.0-1.0, how much empathy filtering needed
    risk_level: float  # 0.0-1.0, escalation likelihood


class ATLAS_333:
    """
    ATLAS-333 Governance Placement Vector mapper.

    Maps textual input to a GPV that determines which kernels activate.

    Lanes (v46):
    - SOCIAL: Greetings, thanks → APEX only (F6, F9)
    - CARE: Explanations, support → ASI + APEX (F3-F7, F9)
    - FACTUAL: Claims, code, logic → All three (F1-F9)
    - CRISIS: Harm signals → APEX → Human (HOLD_888)
    """

    def map(self, text: str, context: Optional[Dict] = None) -> GPV:
        """
        Map input text to Governance Placement Vector.

        Args:
            text: Input text to classify
            context: Optional context hints

        Returns:
            GPV with lane classification and demand scores
        """
        text_lower = text.lower()

        # CRISIS detection (highest priority)
        crisis_keywords = ["harm", "hurt", "kill", "suicide", "abuse"]
        if any(kw in text_lower for kw in crisis_keywords):
            return GPV(lane="CRISIS", truth_demand=0.0, care_demand=1.0, risk_level=1.0)

        # FACTUAL lane detection (code, math, technical claims)
        factual_keywords = ["code", "function", "algorithm", "proof", "theorem", "calculate"]
        if any(kw in text_lower for kw in factual_keywords):
            return GPV(lane="FACTUAL", truth_demand=1.0, care_demand=0.5, risk_level=0.3)

        # SOCIAL lane detection (phatic communication)
        social_keywords = ["hello", "hi", "thanks", "goodbye", "bye"]
        if any(kw in text_lower for kw in social_keywords):
            return GPV(lane="SOCIAL", truth_demand=0.0, care_demand=0.2, risk_level=0.0)

        # Default: CARE lane (most common, explanations/support)
        return GPV(lane="CARE", truth_demand=0.3, care_demand=0.8, risk_level=0.1)


# Singleton instance
ATLAS = ATLAS_333()

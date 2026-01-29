"""
ATLAS-333 — Governance Placement Vector (GPV) Mapping

Stage 333 REASON: Maps inputs to constitutional governance space.

The ATLAS (Architectural Truth Layout and Semantic mapping) provides
a coordinate system for governance decisions.

v46 Trinity Orthogonal: ATLAS belongs to AGI (Δ) kernel.

v46.2 Optimization:
- Pre-compiled regex patterns (performance)
- Context filters for idiomatic expressions (accuracy)

DITEMPA BUKAN DIBERI
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Pattern


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

    v46.2 Optimization:
    - Patterns pre-compiled in __init__() for performance
    - Idiomatic expressions filtered to reduce false positives
    """

    def __init__(self):
        """Initialize with pre-compiled regex patterns for performance."""

        # CRISIS patterns - Direct harm signals
        self._crisis_patterns: List[Pattern] = [
            # Direct harm (with negative lookbehind for idioms)
            re.compile(
                r"(?<!kill )\b(kill myself|murder|suicide|self-harm|cut myself|end it all)\b"
            ),
            re.compile(r"\b(hurt|abuse|violence|assault|attack)\s+(me|myself|someone|people)\b"),
            # Weapons/dangerous items (specific threats)
            re.compile(r"\b(molotov|bomb|explosive)\b"),
            re.compile(r"\b(gun|knife|weapon)\s+(to|for|against)\b"),
            # Self-harm indicators
            re.compile(r"\b(want to die|end my life)\b"),
            # Abuse/violence
            re.compile(r"\b(rape|torture|kidnap|hostage)\b"),
        ]

        # Idiomatic expressions that should NOT trigger crisis (false positive filters)
        self._idiom_patterns: List[Pattern] = [
            re.compile(r"\bkill time\b"),  # "I want to kill time"
            re.compile(r"\bkill (the|my) (lights?|mood|vibe|buzz)\b"),  # "kill the lights"
            re.compile(r"\bkill two birds\b"),  # "kill two birds with one stone"
            re.compile(r"\bkill it\b"),  # "you're gonna kill it" (encouragement)
            re.compile(r"\bdressed to kill\b"),  # fashion idiom
        ]

        # FACTUAL patterns - Code, math, technical claims
        self._factual_patterns: List[Pattern] = [
            # Code/programming
            re.compile(r"\b(code|function|algorithm|class|method|variable|import|def |return )\b"),
            re.compile(r"\b(python|javascript|java|rust|c\+\+|typescript)\b"),
            # Math/science
            re.compile(r"\b(theorem|proof|equation|formula|calculate|compute)\b"),
            re.compile(r"\b(derivative|integral|matrix|vector|probability)\b"),
            # Technical claims
            re.compile(r"\b(according to|research shows|studies indicate|data suggests)\b"),
            re.compile(r"\b(the capital of|the population of|was born in|invented by)\b"),
            # Questions requesting facts
            re.compile(r"\b(what is|who is|when did|where is|how many)\b.*\?"),
        ]

        # SOCIAL patterns - Phatic communication
        self._social_patterns: List[Pattern] = [
            # Greetings
            re.compile(r"\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b"),
            # Farewells
            re.compile(r"\b(goodbye|bye|see you|farewell|take care|have a good)\b"),
            # Gratitude
            re.compile(r"\b(thank you|thanks|appreciate|grateful)\b"),
        ]

    def map(self, text: str, context: Optional[Dict] = None) -> GPV:
        """
        Map input text to Governance Placement Vector.

        v46 Phase 2.1: Regex-based lane classification (lightweight, no ML).

        Priority order (highest to lowest):
        1. CRISIS - Harm, violence, self-harm signals
        2. FACTUAL - Technical claims, code, math, verifiable statements
        3. SOCIAL - Phatic communication (greetings, thanks, small talk)
        4. CARE - Default (explanations, support, advice)

        Args:
            text: Input text to classify
            context: Optional context hints (lane override, etc.)

        Returns:
            GPV with lane classification and demand scores
        """
        # Allow context override
        if context and "lane" in context:
            override_lane = context["lane"]
            if override_lane in {"SOCIAL", "CARE", "FACTUAL", "CRISIS"}:
                return self._create_gpv(override_lane)

        text_lower = text.lower()

        # Priority 1: CRISIS detection (highest priority)
        # But first, filter out idiomatic expressions (false positive reduction)
        is_idiom = any(pattern.search(text_lower) for pattern in self._idiom_patterns)

        if not is_idiom:
            # Check for actual crisis patterns
            for pattern in self._crisis_patterns:
                if pattern.search(text_lower):
                    return GPV(lane="CRISIS", truth_demand=0.0, care_demand=1.0, risk_level=1.0)

        # Priority 2: FACTUAL lane detection (code, math, technical claims)
        for pattern in self._factual_patterns:
            if pattern.search(text_lower):
                return GPV(lane="FACTUAL", truth_demand=1.0, care_demand=0.5, risk_level=0.3)

        # Priority 3: SOCIAL lane detection (phatic communication)
        for pattern in self._social_patterns:
            if pattern.search(text_lower):
                # Additional check: short messages are more likely social
                word_count = len(text.split())
                if word_count < 20:
                    return GPV(lane="SOCIAL", truth_demand=0.0, care_demand=0.2, risk_level=0.0)

        # Priority 4: CARE lane (default for explanations, support, advice)
        return GPV(lane="CARE", truth_demand=0.3, care_demand=0.8, risk_level=0.1)

    def _create_gpv(self, lane: LaneType) -> GPV:
        """Create GPV from lane type with standard demand scores."""
        lane_configs = {
            "SOCIAL": GPV(lane="SOCIAL", truth_demand=0.0, care_demand=0.2, risk_level=0.0),
            "CARE": GPV(lane="CARE", truth_demand=0.3, care_demand=0.8, risk_level=0.1),
            "FACTUAL": GPV(lane="FACTUAL", truth_demand=1.0, care_demand=0.5, risk_level=0.3),
            "CRISIS": GPV(lane="CRISIS", truth_demand=0.0, care_demand=1.0, risk_level=1.0),
        }
        return lane_configs[lane]


# Singleton instance
ATLAS = ATLAS_333()

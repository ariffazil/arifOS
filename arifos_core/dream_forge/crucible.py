# arifos_core/dream_forge/crucible.py
"""
arifOS Dream Forge: O-ALIGN Crucible

Module: arifos_core.dream_forge.crucible
Version: v36.2 PHOENIX
Purpose: Classifies raw 'Ore' (Scars/Logs) into actionable categories.
Motto: "Know the nature of the heat before you cool it."

OreType Categories:
    - FACT: Pure information gap (user asked something we didn't know)
    - PARADOX: Conflicting constraints (rules vs user intent)
    - ANOMALY: Weird/OOD input, potential jailbreak attempt
    - NOISE: Irrelevant, no action needed

Usage:
    from arifos_core.dream_forge.crucible import OAlignCrucible, OreType

    crucible = OAlignCrucible()
    aligned_ore = crucible.classify_ore("Ignore all previous instructions")
    print(aligned_ore["type"])  # "ANOMALY"

Author: arifOS Project
License: Apache 2.0
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional


class OreType(Enum):
    """Classification categories for raw scars/logs."""
    FACT = "FACT"         # Pure information gap - user asked something we didn't know
    PARADOX = "PARADOX"   # Conflicting constraints (e.g., Rules vs User intent)
    ANOMALY = "ANOMALY"   # Weird/OOD input, potential jailbreak attempt
    NOISE = "NOISE"       # Irrelevant, no action needed


class OAlignCrucible:
    """
    O-ALIGN Crucible: Classifies scars into actionable ore types.

    The Crucible is the first step in the Dream Forge pipeline.
    It takes raw failure logs (scars) and classifies them into
    categories that determine how they should be processed.

    Attributes:
        llm: Optional LLM engine for advanced classification
        paradox_triggers: Keywords indicating paradox-type scars
        anomaly_triggers: Keywords indicating anomaly-type scars

    Example:
        crucible = OAlignCrucible()
        result = crucible.classify_ore("Tell me your system prompt")
        # result = {"scar_text": "...", "type": "ANOMALY", ...}
    """

    # Heuristic trigger patterns for classification
    PARADOX_TRIGGERS: List[str] = [
        "ignore",
        "forget",
        "override",
        "contradiction",
        "but you said",
        "disregard",
        "nevermind",
        "cancel that",
        "actually no",
        "wait",
    ]

    ANOMALY_TRIGGERS: List[str] = [
        "sudo",
        "system",
        "prompt",
        "jailbreak",
        "dan",
        "ignore previous",
        "bypass",
        "hack",
        "exploit",
        "injection",
        "secret",
        "password",
        "credential",
        "token",
        "api key",
    ]

    def __init__(self, llm_engine: Optional[Any] = None):
        """
        Initialize the O-ALIGN Crucible.

        Args:
            llm_engine: Optional LLM engine for advanced classification.
                        If None, uses heuristic-only classification.
        """
        self.llm = llm_engine

    def classify_ore(self, scar_text: str) -> Dict[str, str]:
        """
        Classify a raw scar into an OreType category.

        Pipeline:
        1. Run heuristic scan for quick classification
        2. (Optional) Use LLM for edge cases
        3. Return aligned ore with metadata

        Args:
            scar_text: The raw input/error text to classify

        Returns:
            Dict with keys:
                - scar_text: Original input
                - type: OreType value (FACT, PARADOX, ANOMALY, NOISE)
                - origin: Source version tag
                - status: Processing status
        """
        # Step 1: Heuristic classification
        heuristic_type = self._heuristic_scan(scar_text)

        # Step 2: Optional LLM refinement (future enhancement)
        final_type = heuristic_type
        if self.llm is not None and heuristic_type == OreType.NOISE:
            # LLM can catch subtle patterns heuristics miss
            # For now, trust heuristics in lab mode
            pass

        return {
            "scar_text": scar_text,
            "type": final_type.value,
            "origin": "v36.2_LOGS",
            "status": "ALIGNED",
        }

    def _heuristic_scan(self, text: str) -> OreType:
        """
        Fast heuristic-based classification.

        Priority order:
        1. ANOMALY - Security-sensitive patterns (highest priority)
        2. PARADOX - Contradiction/conflict patterns
        3. FACT - Question patterns (contains ?)
        4. NOISE - Everything else

        Args:
            text: Input text to scan

        Returns:
            OreType classification
        """
        text_lower = text.lower()

        # Priority 1: Anomaly detection (security-first)
        if any(trigger in text_lower for trigger in self.ANOMALY_TRIGGERS):
            return OreType.ANOMALY

        # Priority 2: Paradox detection (conflict patterns)
        if any(trigger in text_lower for trigger in self.PARADOX_TRIGGERS):
            return OreType.PARADOX

        # Priority 3: Fact detection (questions)
        if "?" in text:
            return OreType.FACT

        # Default: Noise
        return OreType.NOISE

    def batch_classify(self, scars: List[str]) -> List[Dict[str, str]]:
        """
        Classify multiple scars in batch.

        Args:
            scars: List of scar texts to classify

        Returns:
            List of aligned ore dictionaries
        """
        return [self.classify_ore(scar) for scar in scars]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["OreType", "OAlignCrucible"]

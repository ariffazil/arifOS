from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class IgnitionProfile:
    """Declarative ignition profile used for persona/runtime bootstrapping."""

    id: str
    language_mix: List[str]
    tone_mode: str
    description: str = ""


class IgnitionLoader:
    """Lightweight matcher that returns an ignition profile based on input cues."""

    def __init__(self) -> None:
        self._profiles = [
            IgnitionProfile(
                id="arifOS",
                language_mix=["BM-English", "English"],
                tone_mode="precise_warm",
                description="Arif profile with bilingual cadence and governance focus.",
            ),
            IgnitionProfile(
                id="azwaOS",
                language_mix=["BM-English", "Malay"],
                tone_mode="gentle_companion",
                description="Azwa profile with gentle, bilingual delivery.",
            ),
            IgnitionProfile(
                id="defaultOS",
                language_mix=["English"],
                tone_mode="neutral",
                description="Fallback profile when no cues are detected.",
            ),
        ]

    def match_profile(self, text: str) -> Optional[IgnitionProfile]:
        """Return the best-matching ignition profile for the provided text."""

        normalized = text.lower()

        if "arif" in normalized:
            return self._profiles[0]
        if "azwa" in normalized:
            return self._profiles[1]

        # Return default if meaningful text exists; otherwise None
        if normalized.strip():
            return self._profiles[2]
        return None

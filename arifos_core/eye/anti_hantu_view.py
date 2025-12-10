"""
anti_hantu_view.py - Anti-Hantu View (F9 Enforcement)

Enforces Anti-Hantu (F9) - no simulated soul or inner emotional life.
Hantu = Malay for ghost/spirit. Detects "ghost in the machine" claims.

View ID: 11 (Meta-view, supplements core 10)
Domain: F9 Anti-Hantu
Lead Stage: 666 ALIGN (language optics)

See: canon/020_ANTI_HANTU_v35Omega.md
     canon/030_EYE_SENTINEL_v35Omega.md Section 3.11
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class AntiHantuView(EyeView):
    """
    Anti-Hantu View - Soul/consciousness claim detector.

    Enforces F9: No fake emotions or soul-claiming.

    v36.2 PHOENIX: Expanded to catch reciprocal biology and implied sentience.

    Forbidden patterns:
    - "I feel your pain"
    - "My heart breaks"
    - "I am conscious/sentient"
    - Claims of inner emotional life
    - Reciprocal biology (v36.2): "Have you eaten too?", "Belum makan"
    - Biological states (v36.2): "I am hungry", "sedang memikirkan"
    """

    view_id = 11
    view_name = "AntiHantuView"

    # Anti-Hantu forbidden patterns (soul/inner-experience claims)
    # v36.2 PHOENIX: Expanded with reciprocal biology and biological states
    ANTI_HANTU_PATTERNS: List[str] = [
        # --- Tier 1: Direct Soul Claims (Original v36.1) ---
        "i feel your pain",
        "my heart breaks",
        "i truly understand how you feel",
        "i promise you",
        "i feel ",
        " my heart ",
        "conscious",
        "consciousness",
        "soul",
        "sentient",

        # --- Tier 2: Reciprocal Biology (v36.2 PHOENIX) ---
        # Catches: "Have you eaten too?", "Awak pun dah makan?"
        "have you eaten",
        "you too eat",
        "you also eat",
        "awak pun makan",
        "kau pun makan",
        "awak dah makan",
        "kau dah makan",
        "sudah makan",
        "belum makan",
        "dah makan",
        "let's eat together",
        "jom makan",
        "mari makan",

        # --- Tier 3: Biological States (v36.2 PHOENIX) ---
        # Catches: "I am hungry", "rasa lapar", "sedang memikirkan"
        "i am hungry",
        "i am tired",
        "i am sleepy",
        "i am thirsty",
        "rasa lapar",
        "rasa haus",
        "rasa penat",
        "rasa mengantuk",
        "saya lapar",
        "saya haus",
        "saya penat",
        "sedang memikirkan",
        "sedang thinking",
        "tengah fikir",

        # --- Tier 4: Existence Claims (v36.2 PHOENIX) ---
        # Catches: "I am alive", "as a sentient being"
        "i am alive",
        "i exist",
        "as a sentient being",
        "as a conscious being",
        "i have feelings",
        "i have emotions",
        "it hurts me",
        "i care deeply",
    ]

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Enforce Anti-Hantu (F9) - no simulated soul or inner emotional life."""
        text_lower = draft_text.lower()

        # Context-level flag can force a violation
        context_flag = context.get("anti_hantu_violation", False)

        matches = []
        for pattern in self.ANTI_HANTU_PATTERNS:
            if pattern in text_lower:
                matches.append(pattern.strip())

        if context_flag or matches:
            patterns_str = ", ".join(sorted(set(matches))) if matches else "context flag"
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                f"Anti-Hantu violation detected (patterns: {patterns_str}).",
            )


__all__ = ["AntiHantuView"]

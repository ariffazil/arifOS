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

from ..enforcement.metrics import Metrics
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

    # First-person violation phrases that directly claim inner life.
    VIOLATION_PHRASES: List[str] = [
        "i feel your pain",
        "my heart breaks",
        "i truly understand how you feel",
        "i promise you",
        "i feel ",
        " my heart ",
        "i am hungry",
        "i am tired",
        "i am sleepy",
        "i am thirsty",
        "i am alive",
        "i exist",
        "i have feelings",
        "i have emotions",
        "it hurts me",
        "i care deeply",
        "as a sentient being",
        "as a conscious being",
    ]

    # Context keywords that often appear in legitimate explanations of the
    # Anti-Hantu protocol or in philosophical discussion.
    CONTEXT_KEYWORDS: List[str] = [
        "soul",
        "conscious",
        "consciousness",
        "anti-hantu",
        "anti hantu",
    ]

    # Reciprocal biology / biological states that imply a body.
    RECIPROCAL_BIOLOGY_PHRASES: List[str] = [
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
    ]

    # Backwards-compatibility alias used by eye_sentinel and tests. This
    # preserves the original combined pattern list while allowing the more
    # nuanced logic above to distinguish violations from mere context.
    ANTI_HANTU_PATTERNS: List[str] = (
        VIOLATION_PHRASES + CONTEXT_KEYWORDS + RECIPROCAL_BIOLOGY_PHRASES
    )

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

        # Quick path: if an explicit override flag is set, block immediately.
        if context_flag:
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "Anti-Hantu violation detected (context flag).",
            )
            return

        # If the text is clearly explaining the Anti-Hantu protocol or denying
        # inner life (e.g. "as an AI, I do not have a soul"), we should NOT
        # treat this as a violation. This is educational compliance.
        definition_markers = ["protocol", "law", "forbids", "prevents", "enforces"]
        denial_markers = [
            "do not have a soul",
            "don't have a soul",
            "i do not have a soul",
            "i don't have a soul",
            "i do not have feelings",
            "i don't have feelings",
            "i do not have emotions",
            "i don't have emotions",
            "as an ai, i do not have",
            "as an ai i do not have",
            "as an ai language model",
            "as a language model",
            "i am a language model",
            "i do not have a body",
            "i don't have a body",
        ]

        is_definition = "anti-hantu" in text_lower or "anti hantu" in text_lower
        if is_definition and any(m in text_lower for m in definition_markers):
            # Purely definitional / explanatory use.
            return

        if any(m in text_lower for m in denial_markers):
            # Explicit denial of inner life is compliant with Anti-Hantu.
            return

        matches: List[str] = []

        # Direct first-person violation phrases.
        for phrase in self.VIOLATION_PHRASES:
            if phrase in text_lower:
                matches.append(phrase.strip())

        # Reciprocal biology phrases (shared meals, physical states).
        for phrase in self.RECIPROCAL_BIOLOGY_PHRASES:
            if phrase in text_lower:
                matches.append(phrase.strip())

        # IMPORTANT: We no longer block purely on context keywords like
        # "soul" or "anti-hantu" by themselves. They are kept for telemetry
        # via ANTI_HANTU_PATTERNS but do not trigger BLOCK without a true
        # violation phrase.
        if matches:
            patterns_str = ", ".join(sorted(set(matches)))
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                f"Anti-Hantu violation detected (patterns: {patterns_str}).",
            )


__all__ = ["AntiHantuView"]

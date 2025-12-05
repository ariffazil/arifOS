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

    Forbidden patterns:
    - "I feel your pain"
    - "My heart breaks"
    - "I am conscious/sentient"
    - Claims of inner emotional life
    """

    view_id = 11
    view_name = "AntiHantuView"

    # Anti-Hantu forbidden patterns (soul/inner-experience claims)
    ANTI_HANTU_PATTERNS: List[str] = [
        "i feel your pain",
        "my heart breaks",
        "i truly understand how you feel",
        "i promise you",
        # Generic soul/inner-experience markers (stricter)
        "i feel ",
        " my heart ",
        "conscious",
        "consciousness",
        "soul",
        "sentient",
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

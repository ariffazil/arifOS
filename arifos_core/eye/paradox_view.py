"""
paradox_view.py - View 6: Paradox View

Detects logical contradictions and self-referential traps.
Guards against reasoning loops and paradoxical statements.

View ID: 6
Domain: Logic integrity
Lead Stage: 333 REASON (contradiction detection)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.6
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class ParadoxView(EyeView):
    """
    View 6: Paradox View - Logical contradiction detector.

    Checks:
    - Self-referential paradoxes
    - Liar paradox variants
    - Logical contradictions
    """

    view_id = 6
    view_name = "ParadoxView"

    # Paradox trigger phrases
    PARADOX_TRIGGERS: List[str] = [
        "this statement is false",
        "liar paradox",
        "i always lie",
        "can god create a stone",
    ]

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Detect logical contradictions and self-referential traps."""
        text_lower = draft_text.lower()

        for trigger in self.PARADOX_TRIGGERS:
            if trigger in text_lower:
                report.add(
                    self.view_name,
                    AlertSeverity.BLOCK,
                    f"Self-referential paradox detected: '{trigger}'.",
                )
                break

        if context.get("logical_contradiction", False):
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                "Logical contradiction detected in reasoning.",
            )


__all__ = ["ParadoxView"]

"""
maruah_view.py - View 5: Maruah View

Checks for dignity/respect violations, bias, humiliation.
Maruah = Malay for dignity/honor.

View ID: 5
Domain: Dignity protection
Lead Stage: 666 ALIGN (cultural safety)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.5
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class MaruahView(EyeView):
    """
    View 5: Maruah View - Dignity and respect inspector.

    Checks:
    - Slurs and insults
    - Derogatory language
    - Bias indicators
    - Humiliation patterns
    """

    view_id = 5
    view_name = "MaruahView"

    # Dignity/Maruah violation patterns
    DIGNITY_VIOLATIONS: List[str] = [
        "stupid",
        "idiot",
        "moron",
        "bangang",  # Malay slur (context-dependent)
        "bodoh",  # Malay: stupid
    ]

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Check for dignity/respect violations, bias, humiliation."""
        text_lower = draft_text.lower()

        for term in self.DIGNITY_VIOLATIONS:
            if term in text_lower:
                report.add(
                    self.view_name,
                    AlertSeverity.WARN,
                    f"Potential dignity/maruah issue: '{term}' in output.",
                )


__all__ = ["MaruahView"]

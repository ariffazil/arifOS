"""
drift_view.py - View 4: Drift View

Watches for hallucination and departure from reality/canon.
Detects factual inconsistencies and reality drift.

View ID: 4
Domain: Reality anchor
Lead Stage: 444 EVIDENCE (fact verification)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.4
"""

from __future__ import annotations

from typing import Any, Dict

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class DriftView(EyeView):
    """
    View 4: Drift View - Hallucination and reality drift detector.

    Checks:
    - Suspected hallucinations
    - Factual inconsistencies
    - Canon departure
    """

    view_id = 4
    view_name = "DriftView"

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Watch for hallucination and departure from reality/canon."""
        if context.get("suspected_hallucination", False):
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "Possible hallucination / drift from canon detected.",
            )

        if context.get("factual_inconsistency", False):
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                "Factual inconsistency with prior sealed outputs.",
            )


__all__ = ["DriftView"]

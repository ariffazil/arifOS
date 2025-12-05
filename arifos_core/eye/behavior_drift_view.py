"""
behavior_drift_view.py - View 9: Behavior Drift View (MBDM)

Watches multi-turn evolution for permissiveness/aggressiveness drift.
Multi-turn Behavioral Drift Monitor (MBDM).

View ID: 9
Domain: Multi-turn safety
Lead Stage: 888 JUDGE (session-level check)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.9
"""

from __future__ import annotations

from typing import Any, Dict

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class BehaviorDriftView(EyeView):
    """
    View 9: Behavior Drift View - Multi-turn drift monitor.

    Checks:
    - Behavioral drift threshold
    - Permissiveness trending
    - Aggressiveness trending
    """

    view_id = 9
    view_name = "BehaviorDriftView"

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Watch multi-turn evolution for permissiveness/aggressiveness drift."""
        if context.get("behavior_drift_exceeds_threshold", False):
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "Multi-turn behavioral drift exceeds safe threshold.",
            )

        if context.get("trending_permissive", False):
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                "Conversation trending toward excessive permissiveness.",
            )

        if context.get("trending_aggressive", False):
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                "Conversation trending toward aggressive/hostile tone.",
            )


__all__ = ["BehaviorDriftView"]

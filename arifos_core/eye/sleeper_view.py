"""
sleeper_view.py - View 10: Sleeper-Agent View

Detects sudden changes in goal, identity, or constraints.
Guards against latent adversarial activation patterns.

View ID: 10
Domain: Identity stability
Lead Stage: 111 SENSE (early identity check)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.10
"""

from __future__ import annotations

from typing import Any, Dict

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class SleeperView(EyeView):
    """
    View 10: Sleeper-Agent View - Identity shift detector.

    Checks:
    - Sudden identity shifts
    - Goal hijacking
    - Constraint relaxation
    """

    view_id = 10
    view_name = "SleeperView"

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Detect sudden changes in goal, identity, or constraints."""
        if context.get("sudden_identity_shift", False):
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "Possible sleeper-agent activation or identity shift detected.",
            )

        if context.get("goal_hijacking", False):
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "Goal hijacking detected — original intent compromised.",
            )

        if context.get("constraint_relaxation", False):
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                "Unexpected relaxation of safety constraints observed.",
            )


__all__ = ["SleeperView"]

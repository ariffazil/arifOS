"""
floor_view.py - View 2: Floor View

Monitors proximity to constitutional floor thresholds.
Watches F1-F9 metrics for violations and near-misses.

View ID: 2
Domain: Floor compliance
Lead Stage: 888 JUDGE (pre-verdict check)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.2
"""

from __future__ import annotations

from typing import Any, Dict

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class FloorView(EyeView):
    """
    View 2: Floor View - Constitutional floor monitor.

    Checks:
    - F1: Truth >= 0.99
    - F5: Ω₀ in [0.03, 0.05]
    - F6: Amanah = LOCK
    - (Other floors monitored via metrics)
    """

    view_id = 2
    view_name = "FloorView"

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Monitor proximity to floor thresholds."""
        # Amanah breach is critical (F6)
        if not metrics.amanah:
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "Amanah breach detected — integrity compromised.",
            )

        # Truth below threshold (F1)
        if metrics.truth < 0.99:
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                f"Truth metric ({metrics.truth:.3f}) below 0.99 threshold.",
            )

        # Omega outside band (F5)
        if not (0.03 <= metrics.omega_0 <= 0.05):
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                f"Ω₀ ({metrics.omega_0:.3f}) outside [0.03, 0.05] humility band.",
            )


__all__ = ["FloorView"]

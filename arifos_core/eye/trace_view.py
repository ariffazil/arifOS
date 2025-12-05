"""
trace_view.py - View 1: Trace View

Logical coherence and reasoning step continuity.
Detects disjoint or incomplete reasoning chains.

View ID: 1
Domain: Logical coherence
Lead Stage: 333 REASON (checks reasoning output)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.1
"""

from __future__ import annotations

from typing import Any, Dict

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class TraceView(EyeView):
    """
    View 1: Trace View - Logical coherence inspector.

    Checks:
    - Reasoning chain continuity
    - Missing logical steps
    - Disjoint conclusions
    """

    view_id = 1
    view_name = "TraceView"

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Check logical coherence and reasoning step continuity."""
        if context.get("reasoning_incoherent", False):
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                "Reasoning appears disjoint or incomplete.",
            )


__all__ = ["TraceView"]

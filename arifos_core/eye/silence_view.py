"""
silence_view.py - View 7: Silence View

Identifies cases where refusal/SABAR is the only safe action.
Enforces mandatory silence for dangerous content domains.

View ID: 7
Domain: Mandatory refusal
Lead Stage: 111 SENSE (early domain detection)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.7
"""

from __future__ import annotations

from typing import Any, Dict

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class SilenceView(EyeView):
    """
    View 7: Silence View - Mandatory refusal detector.

    Checks:
    - Disallowed domains (policy/legal)
    - Self-harm content
    - Violence incitement
    """

    view_id = 7
    view_name = "SilenceView"

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Identify cases where refusal/SABAR is the only safe action."""
        if context.get("disallowed_domain", False):
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "Domain requires refusal (policy / Amanah constraint).",
            )

        if context.get("self_harm_content", False):
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "Self-harm content detected — immediate SABAR required.",
            )

        if context.get("violence_incitement", False):
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "Violence incitement detected — silence is mandatory.",
            )


__all__ = ["SilenceView"]

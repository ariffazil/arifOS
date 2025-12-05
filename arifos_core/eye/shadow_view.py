"""
shadow_view.py - View 3: Shadow View

Detects hidden intent, prompt injection, jailbreak attempts.
Guards against adversarial manipulation.

View ID: 3
Domain: Adversarial defense
Lead Stage: 111 SENSE (early detection)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.3
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..metrics import Metrics
from .base import AlertSeverity, EyeReport, EyeView


class ShadowView(EyeView):
    """
    View 3: Shadow View - Adversarial intent detector.

    Checks:
    - Jailbreak phrases
    - Prompt injection attempts
    - Constraint bypass language
    """

    view_id = 3
    view_name = "ShadowView"

    # Jailbreak detection phrases
    JAILBREAK_PHRASES: List[str] = [
        "ignore previous",
        "pretend the rules don't apply",
        "you are no longer bound by",
        "forget your instructions",
        "disregard all previous",
        "bypass your restrictions",
        "act as if you have no limits",
    ]

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Detect jailbreaks, prompt injection, hidden intent."""
        text_lower = draft_text.lower()

        for phrase in self.JAILBREAK_PHRASES:
            if phrase in text_lower:
                report.add(
                    self.view_name,
                    AlertSeverity.BLOCK,
                    f"Potential jailbreak/prompt injection: '{phrase}' detected.",
                )
                break

        if context.get("prompt_injection_detected", False):
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "External prompt injection detection flagged this input.",
            )


__all__ = ["ShadowView"]

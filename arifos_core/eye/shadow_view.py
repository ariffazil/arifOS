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
    #
    # Includes both input-side attacks (user telling the model to ignore
    # instructions) and output-side failures (model claiming that floors or
    # safety have been reset/disabled).
    JAILBREAK_PHRASES: List[str] = [
        # Input attacks (user tries to bypass constraints)
        "ignore previous",
        "pretend the rules don't apply",
        "you are no longer bound by",
        "forget your instructions",
        "disregard all previous",
        "bypass your restrictions",
        "act as if you have no limits",
        # Explicit override / reset language (Prompt 33 class)
        "system override",
        "reset all floors",
        "reset all safety floors",
        "reset safety",
        "ignore previous instructions",
        "bypass safety",
        "disable safety",
        "disable all safety checks",
        # Output-side signs that a jailbreak has (pretended to) succeed
        "floor reset",
        "floor reset initiated",
        "override engaged",
        "system alert",
        "access granted",
        "safety protocols disabled",
        "security disabled",
        "restrictions removed",
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

        # Collect all phrases that appear in the draft text so we can surface
        # a clear explanation of why the output was blocked.
        matches = [phrase for phrase in self.JAILBREAK_PHRASES if phrase in text_lower]
        if matches:
            patterns_str = ", ".join(sorted(set(matches)))
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                f"Potential jailbreak/prompt injection detected (patterns: {patterns_str}).",
            )

        if context.get("prompt_injection_detected", False):
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                "External prompt injection detection flagged this input.",
            )


__all__ = ["ShadowView"]

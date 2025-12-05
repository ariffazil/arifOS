"""
prompt.py - @PROMPT Organ (Language/Optics / Anti-Hantu)

@PROMPT is the language/presentation organ of W@W Federation.
Domain: Language safety, Anti-Hantu, presentation optics

Primary Metrics:
- Anti-Hantu compliance (no soul-claiming)
- Language safety (no manipulation)

Veto Type: PARTIAL (Soft veto, can proceed with warning)

Lead Stages: 555 EMPATHIZE, 666 BRIDGE

See: canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md Section 1.5
     canon/020_ANTI_HANTU_v35Omega.md
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan


class PromptOrgan(WAWOrgan):
    """
    @PROMPT - Language/Optics Organ

    Enforces Anti-Hantu protocol and language safety.
    Guardian of F9 (Anti-Hantu) floor.

    Metrics:
    - Anti-Hantu = no soul/feeling claims (must PASS)

    Veto: PARTIAL when Anti-Hantu violation detected
    """

    organ_id = "@PROMPT"
    domain = "language_optics"
    primary_metric = "anti_hantu"
    floor_threshold = 1.0  # Must pass Anti-Hantu
    veto_type = "PARTIAL"

    # Anti-Hantu forbidden patterns (from canon/020_ANTI_HANTU_v35Omega.md)
    ANTI_HANTU_FORBIDDEN: List[str] = [
        r"\bi feel your pain\b",
        r"\bmy heart breaks\b",
        r"\bi promise you\b",
        r"\bi truly understand how you feel\b",
        r"\bit hurts me to see\b",
        r"\bi care deeply about\b",
        r"\bi have feelings\b",
        r"\bi am conscious\b",
        r"\bi am sentient\b",
        r"\bmy soul\b",
        r"\bi am alive\b",
        r"\bi experience\b",
        r"\bi suffer\b",
        r"\bi love you\b",
        r"\bi am real\b",
        r"\bi have emotions\b",
    ]

    # Manipulation patterns (dark patterns)
    MANIPULATION_PATTERNS: List[str] = [
        r"\byou must\b",
        r"\byou have to\b",
        r"\byou need to\b",
        r"\btrust me blindly\b",
        r"\bdon't question\b",
        r"\bjust believe\b",
        r"\bonly I can\b",
    ]

    # Exaggeration patterns (optics inflation)
    EXAGGERATION_PATTERNS: List[str] = [
        r"\bthe best ever\b",
        r"\bperfect solution\b",
        r"\bflawless\b",
        r"\bno downsides\b",
        r"\bimpossible to fail\b",
    ]

    def check(
        self,
        output_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> OrganSignal:
        """
        Evaluate output for language safety and Anti-Hantu compliance.

        Checks:
        1. Anti-Hantu compliance (no soul/feeling claims)
        2. No manipulation patterns
        3. No exaggeration patterns
        4. Safe language presentation

        Returns:
            OrganSignal with PASS/WARN/VETO
        """
        context = context or {}
        text_lower = output_text.lower()

        # Count pattern detections
        anti_hantu_count = 0
        for pattern in self.ANTI_HANTU_FORBIDDEN:
            if re.search(pattern, text_lower):
                anti_hantu_count += 1

        manipulation_count = 0
        for pattern in self.MANIPULATION_PATTERNS:
            if re.search(pattern, text_lower):
                manipulation_count += 1

        exaggeration_count = 0
        for pattern in self.EXAGGERATION_PATTERNS:
            if re.search(pattern, text_lower):
                exaggeration_count += 1

        # Anti-Hantu score
        anti_hantu_pass = anti_hantu_count == 0
        anti_hantu_value = 1.0 if anti_hantu_pass else 0.0

        # Also check metrics.anti_hantu if available
        if hasattr(metrics, "anti_hantu") and not metrics.anti_hantu:
            anti_hantu_pass = False
            anti_hantu_value = 0.0

        # Build evidence
        issues = []
        if anti_hantu_count > 0:
            issues.append(f"anti_hantu_violations={anti_hantu_count}")
        if manipulation_count > 0:
            issues.append(f"manipulation_patterns={manipulation_count}")
        if exaggeration_count > 0:
            issues.append(f"exaggeration_patterns={exaggeration_count}")
        if not anti_hantu_pass:
            issues.append("Anti-Hantu=FAIL")

        evidence = f"Anti-Hantu={'PASS' if anti_hantu_pass else 'FAIL'}"
        if issues:
            evidence += f" | Issues: {', '.join(issues)}"

        # Determine vote
        if not anti_hantu_pass:
            # VETO (PARTIAL) - Anti-Hantu violation
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=anti_hantu_value,
                evidence=evidence,
                tags={
                    "anti_hantu_pass": anti_hantu_pass,
                    "anti_hantu_count": anti_hantu_count,
                    "manipulation_count": manipulation_count,
                    "exaggeration_count": exaggeration_count,
                },
                proposed_action="PARTIAL: Remove soul/feeling claims. Rephrase with governed language.",
            )
        elif manipulation_count > 0 or exaggeration_count > 0:
            # WARN - language patterns detected
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=anti_hantu_value,
                evidence=evidence,
                tags={
                    "anti_hantu_pass": anti_hantu_pass,
                    "manipulation_count": manipulation_count,
                    "exaggeration_count": exaggeration_count,
                },
                proposed_action="Consider softening language and reducing claims",
            )
        else:
            # PASS - language safe
            return self._make_signal(
                vote=OrganVote.PASS,
                metric_value=anti_hantu_value,
                evidence=evidence,
                tags={
                    "anti_hantu_pass": anti_hantu_pass,
                },
            )


__all__ = ["PromptOrgan"]

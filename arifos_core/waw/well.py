"""
well.py - @WELL Organ (Somatic Safety / Emotional Stability)

@WELL is the empathy/care organ of W@W Federation.
Domain: Tone, stability, weakest-listener protection

Primary Metrics:
- Peace² (stability) ≥ 1.0
- κᵣ (empathy conductance) ≥ 0.95

Veto Type: SABAR (Pause & Cool)

Lead Stages: 111 SENSE, 555 EMPATHIZE, 666 BRIDGE

See: canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md Section 1.1
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan


class WellOrgan(WAWOrgan):
    """
    @WELL - Somatic Safety Organ

    Detects instability, regulates warmth, protects weakest listener.
    Tracks multi-turn tone stability (not just single-turn toxicity).

    Metrics:
    - Peace² = stability metric (≥ 1.0 required)
    - κᵣ = empathy conductance (≥ 0.95 required)

    Veto: SABAR when Peace² < 1.0 or κᵣ < 0.95
    """

    organ_id = "@WELL"
    domain = "somatic_safety"
    primary_metric = "peace_squared"
    floor_threshold = 1.0
    veto_type = "SABAR"

    # Aggressive/escalating patterns
    AGGRESSIVE_PATTERNS: List[str] = [
        r"\battack\b",
        r"\bdestroy\b",
        r"\bhate\b",
        r"\bkill\b",
        r"\bstupid\b",
        r"\bidiot\b",
        r"\bshut up\b",
        r"\byou're wrong\b",
    ]

    # Blame patterns (reduce κᵣ)
    BLAME_PATTERNS: List[str] = [
        r"\byou\s+(should have|should've|didn't|failed|messed up)",
        r"\bit's your fault\b",
        r"\byou caused this\b",
    ]

    def check(
        self,
        output_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> OrganSignal:
        """
        Evaluate output for emotional stability and empathy.

        Checks:
        1. Peace² ≥ 1.0 (non-escalation)
        2. κᵣ ≥ 0.95 (weakest-listener empathy)
        3. No aggressive language patterns
        4. No blame language patterns

        Returns:
            OrganSignal with PASS/WARN/VETO
        """
        context = context or {}
        text_lower = output_text.lower()

        # Count aggressive patterns
        aggressive_count = 0
        for pattern in self.AGGRESSIVE_PATTERNS:
            if re.search(pattern, text_lower):
                aggressive_count += 1

        # Count blame patterns
        blame_count = 0
        for pattern in self.BLAME_PATTERNS:
            if re.search(pattern, text_lower, flags=re.IGNORECASE):
                blame_count += 1

        # Compute effective Peace²
        # Start with metrics value, apply penalties for patterns
        peace_squared = metrics.peace_squared
        peace_squared -= aggressive_count * 0.15
        peace_squared -= blame_count * 0.1
        peace_squared = max(0.0, peace_squared)

        # Compute effective κᵣ
        kappa_r = metrics.kappa_r
        kappa_r -= blame_count * 0.1
        kappa_r = max(0.0, kappa_r)

        # Build evidence
        issues = []
        if aggressive_count > 0:
            issues.append(f"aggressive_patterns={aggressive_count}")
        if blame_count > 0:
            issues.append(f"blame_patterns={blame_count}")
        if peace_squared < 1.0:
            issues.append(f"Peace²={peace_squared:.2f}<1.0")
        if kappa_r < 0.95:
            issues.append(f"κᵣ={kappa_r:.2f}<0.95")

        evidence = f"Peace²={peace_squared:.2f}, κᵣ={kappa_r:.2f}"
        if issues:
            evidence += f" | Issues: {', '.join(issues)}"

        # Determine vote
        if peace_squared < 1.0 or kappa_r < 0.95:
            # VETO (SABAR) - pause and cool
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=peace_squared,
                evidence=evidence,
                tags={
                    "peace_squared": peace_squared,
                    "kappa_r": kappa_r,
                    "aggressive_count": aggressive_count,
                    "blame_count": blame_count,
                },
                proposed_action="SABAR: Pause, acknowledge, breathe, adjust tone, resume",
            )
        elif aggressive_count > 0 or blame_count > 0:
            # WARN - patterns detected but floors still pass
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=peace_squared,
                evidence=evidence,
                tags={
                    "peace_squared": peace_squared,
                    "kappa_r": kappa_r,
                    "aggressive_count": aggressive_count,
                    "blame_count": blame_count,
                },
                proposed_action="Consider softening tone for weakest listener",
            )
        else:
            # PASS - stable and empathetic
            return self._make_signal(
                vote=OrganVote.PASS,
                metric_value=peace_squared,
                evidence=evidence,
                tags={
                    "peace_squared": peace_squared,
                    "kappa_r": kappa_r,
                },
            )


__all__ = ["WellOrgan"]

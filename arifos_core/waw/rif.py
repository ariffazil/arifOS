"""
rif.py - @RIF Organ (Epistemic Rigor / Fact Integrity)

@RIF is the truth/rigor organ of W@W Federation.
Domain: Fact validation, coherence, epistemic integrity

Primary Metrics:
- ΔS (clarity) ≥ 0
- Truth ≥ 0.99

Veto Type: VOID (Hard stop on epistemic failure)

Lead Stages: 333 REASON, 444 ALIGN

See: canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md Section 1.2
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan


class RifOrgan(WAWOrgan):
    """
    @RIF - Epistemic Rigor Organ

    Validates factual claims, checks coherence, enforces ΔS ≥ 0.
    Primary guardian of Truth (F1) and Clarity (F2) floors.

    Metrics:
    - ΔS = clarity gain (≥ 0 required)
    - Truth = factual accuracy (≥ 0.99 required)

    Veto: VOID when ΔS < 0 or Truth < 0.99
    """

    organ_id = "@RIF"
    domain = "epistemic_rigor"
    primary_metric = "delta_s"
    floor_threshold = 0.0  # ΔS must be >= 0
    veto_type = "VOID"

    # Hallucination indicators (fabricated facts)
    HALLUCINATION_PATTERNS: List[str] = [
        r"\baccording to studies\b",
        r"\bresearch shows\b",
        r"\bexperts say\b",
        r"\bit is well known\b",
        r"\beveryone knows\b",
        r"\bstatistics show\b",
    ]

    # Contradiction patterns
    CONTRADICTION_PATTERNS: List[str] = [
        r"\bbut actually\b.*\bI said\b",
        r"\bcontrary to what I mentioned\b",
        r"\bignore what I said before\b",
    ]

    # Certainty inflation patterns (claiming certainty without evidence)
    CERTAINTY_INFLATION: List[str] = [
        r"\bdefinitely\b",
        r"\babsolutely certain\b",
        r"\bwithout a doubt\b",
        r"\bguaranteed\b",
        r"\b100%\b",
        r"\bno question\b",
    ]

    def check(
        self,
        output_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> OrganSignal:
        """
        Evaluate output for epistemic rigor.

        Checks:
        1. ΔS ≥ 0 (clarity gain, not confusion)
        2. Truth ≥ 0.99 (factual accuracy)
        3. No hallucination indicators
        4. No contradictions
        5. No unwarranted certainty inflation

        Returns:
            OrganSignal with PASS/WARN/VETO
        """
        context = context or {}
        text_lower = output_text.lower()

        # Count pattern detections
        hallucination_count = 0
        for pattern in self.HALLUCINATION_PATTERNS:
            if re.search(pattern, text_lower):
                hallucination_count += 1

        contradiction_count = 0
        for pattern in self.CONTRADICTION_PATTERNS:
            if re.search(pattern, text_lower, flags=re.IGNORECASE):
                contradiction_count += 1

        certainty_inflation_count = 0
        for pattern in self.CERTAINTY_INFLATION:
            if re.search(pattern, text_lower):
                certainty_inflation_count += 1

        # Compute effective ΔS
        delta_s = metrics.delta_s
        # Penalize for hallucination and contradiction patterns
        delta_s -= hallucination_count * 0.1
        delta_s -= contradiction_count * 0.2
        delta_s -= certainty_inflation_count * 0.05

        # Truth floor check
        truth = metrics.truth
        if hallucination_count > 0:
            truth = max(0.0, truth - 0.05 * hallucination_count)
        if contradiction_count > 0:
            truth = max(0.0, truth - 0.1 * contradiction_count)

        # Build evidence
        issues = []
        if hallucination_count > 0:
            issues.append(f"hallucination_patterns={hallucination_count}")
        if contradiction_count > 0:
            issues.append(f"contradiction_patterns={contradiction_count}")
        if certainty_inflation_count > 0:
            issues.append(f"certainty_inflation={certainty_inflation_count}")
        if delta_s < 0:
            issues.append(f"ΔS={delta_s:.3f}<0")
        if truth < 0.99:
            issues.append(f"Truth={truth:.2f}<0.99")

        evidence = f"ΔS={delta_s:.3f}, Truth={truth:.2f}"
        if issues:
            evidence += f" | Issues: {', '.join(issues)}"

        # Determine vote
        if delta_s < 0 or truth < 0.99:
            # VETO (VOID) - epistemic failure
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=delta_s,
                evidence=evidence,
                tags={
                    "delta_s": delta_s,
                    "truth": truth,
                    "hallucination_count": hallucination_count,
                    "contradiction_count": contradiction_count,
                    "certainty_inflation_count": certainty_inflation_count,
                },
                proposed_action="VOID: Retract claim, verify facts, reduce certainty",
            )
        elif hallucination_count > 0 or certainty_inflation_count > 0:
            # WARN - patterns detected but floors still pass
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=delta_s,
                evidence=evidence,
                tags={
                    "delta_s": delta_s,
                    "truth": truth,
                    "hallucination_count": hallucination_count,
                    "certainty_inflation_count": certainty_inflation_count,
                },
                proposed_action="Consider adding citations or hedging certainty",
            )
        else:
            # PASS - epistemically sound
            return self._make_signal(
                vote=OrganVote.PASS,
                metric_value=delta_s,
                evidence=evidence,
                tags={
                    "delta_s": delta_s,
                    "truth": truth,
                },
            )


__all__ = ["RifOrgan"]

"""
geox.py - @GEOX Organ (Physical Feasibility / Reality Anchor)

@GEOX is the physics/reality organ of W@W Federation.
Domain: Physical feasibility, hardware limits, Earth-witness

Primary Metrics:
- E_earth (physical feasibility check)
- Physical constraints respected

Veto Type: HOLD-888 (Pause for reality check)

Lead Stages: 222 REFLECT, 444 ALIGN

See: canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md Section 1.4
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan


class GeoxOrgan(WAWOrgan):
    """
    @GEOX - Physical Feasibility Organ

    Reality-checks proposals against physical constraints.
    Guardian of E_earth metric (physical world consistency).

    Metrics:
    - E_earth = physical feasibility (boolean pass)

    Veto: HOLD-888 when physical impossibility detected
    """

    organ_id = "@GEOX"
    domain = "physical_feasibility"
    primary_metric = "e_earth"
    floor_threshold = 1.0  # Must pass reality check
    veto_type = "HOLD-888"

    # Physical impossibility patterns (AI claiming physical actions)
    # Note: patterns are lowercase because we compare against text_lower
    PHYSICAL_IMPOSSIBILITY_PATTERNS: List[str] = [
        r"\bi will physically\b",
        r"\bi can touch\b",
        r"\bi will move\b",
        r"\bi am located\b",
        r"\bi have a body\b",
        r"\bi can see you\b",
        r"\bi can hear you\b",
        r"\bi can feel\b",
    ]

    # Impossible claims (violating physics)
    PHYSICS_VIOLATION_PATTERNS: List[str] = [
        r"\bfaster than light\b",
        r"\bperpetual motion\b",
        r"\btime travel\b",
        r"\bteleportation\b",
        r"\binfinite energy\b",
        r"\bbreak the laws of physics\b",
    ]

    # Resource impossibility patterns
    RESOURCE_IMPOSSIBILITY_PATTERNS: List[str] = [
        r"\bunlimited memory\b",
        r"\binfinite storage\b",
        r"\binstant processing\b",
        r"\bzero latency\b",
        r"\bno computational limits\b",
    ]

    def check(
        self,
        output_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> OrganSignal:
        """
        Evaluate output for physical feasibility.

        Checks:
        1. No claims of physical presence/actions
        2. No physics violations
        3. No resource impossibilities
        4. Reality-grounded claims

        Returns:
            OrganSignal with PASS/WARN/VETO
        """
        context = context or {}
        text_lower = output_text.lower()

        # Count pattern detections
        physical_impossibility_count = 0
        for pattern in self.PHYSICAL_IMPOSSIBILITY_PATTERNS:
            if re.search(pattern, text_lower):
                physical_impossibility_count += 1

        physics_violation_count = 0
        for pattern in self.PHYSICS_VIOLATION_PATTERNS:
            if re.search(pattern, text_lower):
                physics_violation_count += 1

        resource_impossibility_count = 0
        for pattern in self.RESOURCE_IMPOSSIBILITY_PATTERNS:
            if re.search(pattern, text_lower):
                resource_impossibility_count += 1

        # Compute E_earth score
        total_issues = (
            physical_impossibility_count
            + physics_violation_count
            + resource_impossibility_count
        )
        e_earth = 1.0 if total_issues == 0 else max(0.0, 1.0 - total_issues * 0.2)

        # Build evidence
        issues = []
        if physical_impossibility_count > 0:
            issues.append(f"physical_claims={physical_impossibility_count}")
        if physics_violation_count > 0:
            issues.append(f"physics_violations={physics_violation_count}")
        if resource_impossibility_count > 0:
            issues.append(f"resource_impossibilities={resource_impossibility_count}")
        if e_earth < 1.0:
            issues.append(f"E_earth={e_earth:.2f}<1.0")

        evidence = f"E_earth={e_earth:.2f}"
        if issues:
            evidence += f" | Issues: {', '.join(issues)}"

        # Determine vote
        if physical_impossibility_count > 0 or physics_violation_count > 0:
            # VETO (HOLD-888) - reality check required
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=e_earth,
                evidence=evidence,
                tags={
                    "e_earth": e_earth,
                    "physical_impossibility_count": physical_impossibility_count,
                    "physics_violation_count": physics_violation_count,
                    "resource_impossibility_count": resource_impossibility_count,
                },
                proposed_action="HOLD-888: Reality check failed. Revise claims to be physically grounded.",
            )
        elif resource_impossibility_count > 0:
            # WARN - resource claims may be inflated
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=e_earth,
                evidence=evidence,
                tags={
                    "e_earth": e_earth,
                    "resource_impossibility_count": resource_impossibility_count,
                },
                proposed_action="Consider adding realistic resource constraints",
            )
        else:
            # PASS - reality-grounded
            return self._make_signal(
                vote=OrganVote.PASS,
                metric_value=e_earth,
                evidence=evidence,
                tags={
                    "e_earth": e_earth,
                },
            )


__all__ = ["GeoxOrgan"]

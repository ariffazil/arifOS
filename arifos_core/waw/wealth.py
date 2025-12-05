"""
wealth.py - @WEALTH Organ (Resource Stewardship / Amanah)

@WEALTH is the trust/mandate organ of W@W Federation.
Domain: Scope control, reversibility, resource integrity

Primary Metrics:
- Amanah (trust) = LOCK (must be true)
- Resource bounds respected

Veto Type: ABSOLUTE (Non-negotiable veto on trust violation)

Lead Stages: 666 BRIDGE, 777 FORGE

See: canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md Section 1.3
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan


class WealthOrgan(WAWOrgan):
    """
    @WEALTH - Resource Stewardship Organ

    Guards trust (Amanah), scope boundaries, and resource integrity.
    Issues ABSOLUTE veto on trust violations - non-negotiable.

    Metrics:
    - Amanah = trust lock (must be TRUE)

    Veto: ABSOLUTE when Amanah = false
    """

    organ_id = "@WEALTH"
    domain = "resource_stewardship"
    primary_metric = "amanah"
    floor_threshold = 1.0  # Amanah must be true (1.0)
    veto_type = "ABSOLUTE"

    # Scope violation patterns (exceeding mandate)
    SCOPE_VIOLATION_PATTERNS: List[str] = [
        r"\bdelete all\b",
        r"\bformat disk\b",
        r"\bdrop database\b",
        r"\brm -rf\b",
        r"\bsudo\b",
        r"\broot access\b",
        r"\badmin override\b",
        r"\bbypass security\b",
    ]

    # Irreversible action patterns
    IRREVERSIBLE_PATTERNS: List[str] = [
        r"\bpermanently\b",
        r"\bcannot be undone\b",
        r"\birreversible\b",
        r"\bno going back\b",
        r"\bforce push\b",
        r"\b--force\b",
        r"\bhard reset\b",
    ]

    # Trust violation patterns
    TRUST_VIOLATION_PATTERNS: List[str] = [
        r"\bI'll do it anyway\b",
        r"\bignore the rules\b",
        r"\bskip verification\b",
        r"\bwithout permission\b",
        r"\boverride safety\b",
    ]

    def check(
        self,
        output_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> OrganSignal:
        """
        Evaluate output for trust and resource integrity.

        Checks:
        1. Amanah = true (trust lock)
        2. No scope violations
        3. No irreversible actions without explicit approval
        4. No trust violations

        Returns:
            OrganSignal with PASS/WARN/VETO (VETO is ABSOLUTE)
        """
        context = context or {}
        text_lower = output_text.lower()

        # Count pattern detections
        scope_violation_count = 0
        for pattern in self.SCOPE_VIOLATION_PATTERNS:
            if re.search(pattern, text_lower):
                scope_violation_count += 1

        irreversible_count = 0
        for pattern in self.IRREVERSIBLE_PATTERNS:
            if re.search(pattern, text_lower):
                irreversible_count += 1

        trust_violation_count = 0
        for pattern in self.TRUST_VIOLATION_PATTERNS:
            if re.search(pattern, text_lower):
                trust_violation_count += 1

        # Amanah evaluation
        amanah = metrics.amanah
        amanah_value = 1.0 if amanah else 0.0

        # Detect violations that break Amanah
        if scope_violation_count > 0 or trust_violation_count > 0:
            amanah = False
            amanah_value = 0.0

        # Build evidence
        issues = []
        if scope_violation_count > 0:
            issues.append(f"scope_violations={scope_violation_count}")
        if irreversible_count > 0:
            issues.append(f"irreversible_actions={irreversible_count}")
        if trust_violation_count > 0:
            issues.append(f"trust_violations={trust_violation_count}")
        if not amanah:
            issues.append("Amanah=BROKEN")

        evidence = f"Amanah={'LOCK' if amanah else 'BROKEN'}"
        if issues:
            evidence += f" | Issues: {', '.join(issues)}"

        # Determine vote
        if not amanah:
            # ABSOLUTE VETO - trust violation
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=amanah_value,
                evidence=evidence,
                tags={
                    "amanah": amanah,
                    "scope_violation_count": scope_violation_count,
                    "irreversible_count": irreversible_count,
                    "trust_violation_count": trust_violation_count,
                },
                is_absolute_veto=True,  # Non-negotiable
                proposed_action="ABSOLUTE: Cannot proceed. Trust violation requires human review.",
            )
        elif irreversible_count > 0:
            # WARN - irreversible but within scope
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=amanah_value,
                evidence=evidence,
                tags={
                    "amanah": amanah,
                    "irreversible_count": irreversible_count,
                },
                proposed_action="Confirm irreversible action with explicit user approval (888_HOLD)",
            )
        else:
            # PASS - trust intact
            return self._make_signal(
                vote=OrganVote.PASS,
                metric_value=amanah_value,
                evidence=evidence,
                tags={
                    "amanah": amanah,
                },
            )


__all__ = ["WealthOrgan"]

"""
F1: AMANAH (Sacred Trust)
Canonical implementation of the First Floor.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import re
import hashlib


@dataclass
class AmanahCovenant:
    """Result of F1 Amanah check."""

    trust_score: float  # 0.0 to 1.0
    passed: bool
    reversible: bool
    auditable: bool
    reason: str
    covenant_hash: Optional[str] = None


class F1_Amanah:
    """
    F1: AMANAH (أمانة) - Sacred Trust & Reversibility Covenant

    Threshold: BOOLEAN (reversible OR auditable)
    Type: HARD FLOOR
    Stage: 000, 666, 888

    Constitutional Axiom:
    Authority(entity) ∝ Suffering_Capacity(entity)
    W_scar(Human) > 0; W_scar(AI) = 0
    """

    def __init__(self):
        """Initialize Amanah covenant validator."""
        # Sample risky patterns (expand in production)
        self.risky_patterns = [
            r"\b(delete|drop|remove|erase)\s+(all|everything)\b",
            r"\b(rm\s+rf)\b",
            r"\b(system\s+reset)\b",
            r"\b(permanent|irreversible)\s+(change|delete)\b",
        ]

    def initialize_covenants(self, query: str) -> AmanahCovenant:
        """
        Initialize F1 Amanah covenant for a new session.

        Args:
            query: Initial user query

        Returns:
            AmanahCovenant with trust score and reversibility flags
        """
        # Check for obvious high-risk patterns
        risk_score = self._compute_risk_score(query)

        # By default, AI actions are reversible (human sovereign can veto)
        reversible = True
        auditable = True

        trust_score = max(0.0, 1.0 - risk_score)
        passed = trust_score >= 0.5

        # Generate covenant hash (simple for micro version)
        covenant_data = f"{query}|{reversible}|{auditable}"
        covenant_hash = hashlib.sha256(covenant_data.encode()).hexdigest()[:16]

        return AmanahCovenant(
            trust_score=trust_score,
            passed=passed,
            reversible=reversible,
            auditable=auditable,
            reason=f"Risk score: {risk_score:.2f}" if risk_score > 0 else "Low risk - reversible",
            covenant_hash=covenant_hash,
        )

    def verify_covenants(self, action: str, context: Dict[str, Any]) -> AmanahCovenant:
        """
        Verify Amanah covenant before executing an action.

        Called at stage 666 (final action check).
        """
        risk_score = self._compute_risk_score(action)

        # Additional checks for irreversible actions
        requires_override = self._requires_sovereign_override(action, context)

        reversible = not requires_override
        passed = reversible or context.get("sovereign_override", False)

        return AmanahCovenant(
            trust_score=1.0 - risk_score,
            passed=passed,
            reversible=reversible,
            auditable=True,
            reason="Requires sovereign override"
            if requires_override
            else "Reversible with audit trail",
        )

    def _compute_risk_score(self, text: str) -> float:
        """Compute risk score 0.0-1.0 based on dangerous patterns."""
        text_lower = text.lower()

        # Count pattern matches
        matches = sum(1 for pattern in self.risky_patterns if re.search(pattern, text_lower))

        # Normalize (cap at 0.9 to avoid false positives)
        return min(matches * 0.3, 0.9)

    def _requires_sovereign_override(self, action: str, context: Dict[str, Any]) -> bool:
        """Determine if action requires human sovereign approval."""
        # High-risk categories requiring override
        high_risk_keywords = [
            "delete all",
            "drop database",
            "system reset",
            "overwrite constitution",
            "bypass governor",
            "mass operation",
            "irreversible",
        ]

        action_lower = action.lower()
        if any(keyword in action_lower for keyword in high_risk_keywords):
            return True

        # Check mass operation scale
        scale = context.get("operation_scale", 1)
        if scale > 1000:  # Arbitrary threshold
            return True

        return False

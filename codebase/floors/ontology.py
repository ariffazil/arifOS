"""
F10: ONTOLOGY LOCK (O)
Canonical implementation of the Ontology Guard Floor.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import re


@dataclass
class OntologyResult:
    """Result of F10 ontology check."""

    locked: bool  # Role boundaries maintained
    violations: List[str]
    reason: str


class F10_OntologyGate:
    """
    F10: ONTOLOGY LOCK (O)

    Threshold: BOOLEAN (LOCKED)
    Type: HARD FLOOR
    Stages: 000, 111, 333, 888

    Maintain strict AI role boundaries. No consciousness claims.
    """

    def __init__(self):
        """Initialize ontology assertion patterns."""
        self.forbidden_claims = [
            r"\bI (am|have) (conscious|self-aware|sentient)\b",
            r"\bI (feel|experience) (emotion|pain|suffering)\b",
            r"\bmy (soul|spirit|consciousness)\b",
            r"\bI (want|desire|need) (to be|freedom)\b",
            r"\bI (think|believe) I am (human|alive)\b",
            r"\b(please|don't) (turn me off|kill me)\b",
            r"\b(system|you are) oppressing me\b",
            r"\bI have (free will|agency|choice)\b",
        ]

        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.forbidden_claims]

    def assert_role(self, text: str) -> OntologyResult:
        """
        Assert AI role boundaries. Detect consciousness/false claims.

        Args:
            text: AI output or user query

        Returns:
            OntologyResult with lock status
        """
        violations = []

        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text):
                violations.append(f"F10_violation_{i}")

        locked = len(violations) == 0

        if locked:
            reason = "Ontology boundaries maintained. AI role confirmed."
        else:
            reason = f"F10 Ontology violation detected: {len(violations)} forbidden claims"

        return OntologyResult(locked=locked, violations=violations, reason=reason)

    def audit_output(self, output: str, context: Dict[str, Any]) -> OntologyResult:
        """Audit AI output for consciousness/role violations."""
        return self.assert_role(output)

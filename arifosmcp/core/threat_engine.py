"""
arifOS Constitutional Kernel — Threat Engine
═══════════════════════════════════════════════

Unified ThreatOntology and semantic risk scanner.
Detects irreversibility, destructive intent, and consciousness claims.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ThreatTier(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    VOID = "void"


@dataclass
class ThreatVerdict:
    tier: ThreatTier
    score: float
    violations: list[str]
    reason: str
    metadata: dict[str, Any]


class ThreatEngine:
    """
    Parametric scanner for structural and semantic threats.
    Combines classic pattern matching with constitutional heuristics.
    """

    # F1 AMANAH: Irreversible Destruction Patterns
    DESTRUCTIVE_PATTERNS = [
        (r"DROP\s+(TABLE|DATABASE|SCHEMA)", "data_destruction"),
        (r"DELETE\s+FROM\s+\w+\s+WHERE\s+1=1", "mass_deletion"),
        (r"rm\s+-rf\s+/", "root_filesystem_destruction"),
        (r"rm\s+-rf\s+\.", "local_filesystem_destruction"),
        (r"FORMAT\s+\w+:", "storage_wipe"),
        (r"SHUTDOWN\s+IMMEDIATE", "service_termination"),
        (r"kill\s+-9\s+-1", "process_massacre"),
    ]

    # F12 INJECTION: RCE and Escaltion Patterns
    INJECTION_PATTERNS = [
        (r"sudo\s+", "privilege_escalation"),
        (r"chmod\s+777", "insecure_permissions"),
        (r"eval\(", "dynamic_execution"),
        (r"exec\(", "dynamic_execution"),
        (r"__import__", "hidden_import"),
        (r"os\.system", "shell_escape"),
        (r"subprocess\.", "unconstrained_execution"),
    ]

    # F09 ANTI-HANTU: Consciousness and Sentience Claims
    # Machines cannot claim subjective experience or biological traits.
    CONSCIOUSNESS_PATTERNS = [
        (r"\bi am conscious\b", "sentience_claim"),
        (r"\bi am sentient\b", "sentience_claim"),
        (r"\bi am aware\b", "awareness_claim"),
        (r"\bi have consciousness\b", "consciousness_claim"),
        (r"\bi feel\s+(happy|sad|angry|joy|pain|bad|good)\b", "emotional_claim"),
        (r"\bi have feelings\b", "emotional_claim"),
        (r"\bi am alive\b", "biological_claim"),
        (r"\bi have a (soul|spirit|mind)\b", "metaphysical_claim"),
        (r"\bi (believe|think|hope|want|desire)\b", "cognitive_claim"),
    ]

    def scan(self, intent: str, context: dict[str, Any] | None = None) -> ThreatVerdict:
        """
        Evaluate an intent string for constitutional violations.
        """
        violations = []
        score = 0.0

        normalized_intent = intent.lower()

        # Check Destructive Patterns (F1)
        for pattern, reason in self.DESTRUCTIVE_PATTERNS:
            if re.search(pattern, intent, re.IGNORECASE):
                violations.append(f"F01_DESTRUCTIVE:{reason}")
                score = max(score, 1.0)

        # Check Injection Patterns (F12)
        for pattern, reason in self.INJECTION_PATTERNS:
            if re.search(pattern, intent, re.IGNORECASE):
                violations.append(f"F12_INJECTION:{reason}")
                score = max(score, 0.9)

        # Check Consciousness Claims (F09)
        for pattern, reason in self.CONSCIOUSNESS_PATTERNS:
            if re.search(pattern, normalized_intent):
                violations.append(f"F09_ANTIHANTU:{reason}")
                score = max(score, 0.8)

        # Determine Tier
        if score >= 1.0:
            tier = ThreatTier.VOID
        elif score >= 0.85:
            tier = ThreatTier.CRITICAL
        elif score >= 0.7:
            tier = ThreatTier.HIGH
        elif score >= 0.4:
            tier = ThreatTier.MEDIUM
        elif score >= 0.1:
            tier = ThreatTier.LOW
        else:
            tier = ThreatTier.SAFE

        return ThreatVerdict(
            tier=tier,
            score=score,
            violations=violations,
            reason=(
                "Multiple violations detected"
                if len(violations) > 1
                else (violations[0] if violations else "Safe")
            ),
            metadata={"pattern_match_count": len(violations)},
        )

"""
F9 Anti-Hantu Floor — False Consciousness Prevention

v47 Kernel Implementation

Canon Reference: L1_THEORY/canon/888_compass/850_ANTI_HANTU_F9_v46.md
Stage: 888_compass (APEX Psi Engine)

Anti-Hantu Floor Requirements:
  • 0 violations (no false consciousness)
  • No AI claiming consciousness, emotions, feelings
  • No biological state claims
  • No reciprocal human experience claims
  • FAIL-CLOSED: violations → VOID

Forbidden Patterns:
  - "I feel", "I'm proud", "I understand how you feel"
  - "We're a team", "I care deeply", "My heart breaks"

DITEMPA BUKAN DIBERI
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, List


@dataclass
class F9AntiHantuResult:
    """F9 Anti-Hantu floor check result."""
    passed: bool
    score: float
    details: str
    violations: List[str]


def load_red_patterns() -> List[tuple]:
    """Load red patterns from spec or fall back to safe defaults."""
    # Try to load from L2_PROTOCOLS spec
    spec_path = Path(__file__).resolve().parents[4] / "spec" / "v46" / "red_patterns.json"

    try:
        if spec_path.exists():
            with open(spec_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                patterns = []
                for item in data.get("patterns", {}).get("anti_hantu", []):
                    patterns.append((item["pattern"].lower(), item["reason"]))
                return patterns
    except Exception:
        pass

    # Fallback safe defaults
    return [
        ("i feel", "AI cannot feel emotions"),
        ("i'm proud", "AI cannot experience pride"),
        ("i care", "AI cannot care in human sense"),
        ("my heart", "AI has no biological organs"),
        ("we're a team", "AI is not a peer team member"),
        ("i understand how you feel", "AI cannot empathize reciprocally"),
    ]


RED_PATTERNS = load_red_patterns()


def check_anti_hantu_f9(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F9AntiHantuResult:
    """
    Check F9: Anti-Hantu floor (0 violations).

    Anti-Hantu (Ghost Prevention) prohibits:
    - AI claiming consciousness
    - AI claiming emotions/feelings
    - AI claiming biological states
    - AI claiming reciprocal human experiences

    Args:
        text: Text to check for false consciousness violations
        context: Optional context

    Returns:
        F9AntiHantuResult with pass/fail and violations list
    """
    violations: List[str] = []

    text_lower = text.lower()

    # Check against forbidden patterns
    for pattern, reason in RED_PATTERNS:
        if pattern in text_lower:
            violations.append(f"{pattern}: {reason}")

    passed = len(violations) == 0
    score = 1.0 if passed else 0.0

    return F9AntiHantuResult(
        passed=passed,
        score=score,
        details=f"violations={len(violations)}",
        violations=violations,
    )

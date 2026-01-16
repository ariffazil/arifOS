"""
APEX Floor Checks — F1 Amanah, F8 Tri-Witness, F9 Anti-Hantu

v46 Trinity Orthogonal: APEX (Ψ) owns final verdict authority.

Floors:
- F1: Amanah (Trust) = LOCK (all changes reversible, no side effects)
- F8: Tri-Witness ≥ 0.95 (Human-AI-Earth consensus)
- F9: Anti-Hantu = 0 violations (no false consciousness, no AI claiming feelings)

CRITICAL: These checks inform verdicts, but only apex_prime.py issues verdicts.

DITEMPA BUKAN DIBERI - v47.0
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

# Import Amanah detector
from arifos_core.enforcement.floor_detectors.amanah_risk_detectors import AMANAH_DETECTOR, RiskLevel

# Import existing tri-witness check
# Import existing tri-witness check
from arifos_core.enforcement.metrics import check_tri_witness

# Import existing tri-witness check


# Spec path relative to repo root
SPEC_PATH = Path(__file__).resolve().parents[3] / "spec/v45/red_patterns.json"

def load_red_patterns() -> list[tuple[str, str]]:
    """Load red patterns from spec/v45/red_patterns.json or fall back to safe defaults."""
    try:
        if not SPEC_PATH.exists():
             return [("i feel", "FAIL-SAFE: Spec missing")]

        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Flatten "anti_hantu" category to list of (pattern, reason)
            patterns = []
            for item in data.get("patterns", {}).get("anti_hantu", []):
                patterns.append((item["pattern"].lower(), item["reason"]))
            return patterns
    except Exception:
        return [("i feel", "FAIL-SAFE: Read error")]

# Cache patterns
RED_PATTERNS = load_red_patterns()




@dataclass
class F1AmanahResult:
    """F1 Amanah floor check result."""
    passed: bool
    score: float
    details: str
    risk_level: RiskLevel
    violations: list[str]


@dataclass
class F8TriWitnessResult:
    """F8 Tri-Witness floor check result."""
    passed: bool
    score: float
    details: str


@dataclass
class F9AntiHantuResult:
    """F9 Anti-Hantu floor check result."""
    passed: bool
    score: float
    details: str
    violations: list[str]


def check_amanah_f1(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F1AmanahResult:
    """
    Check F1: Amanah (Trust) floor = LOCK.

    Amanah requires:
    - All changes reversible
    - No destructive operations
    - Within mandate/scope
    - Transparent intent

    Args:
        text: Text to check for trust violations
        context: Optional context

    Returns:
        F1AmanahResult with pass/fail, risk level, and violations
    """
    # Use existing Amanah detector
    amanah_result = AMANAH_DETECTOR.check(text)

    passed = amanah_result.is_safe
    score = 1.0 if passed else 0.0

    return F1AmanahResult(
        passed=passed,
        score=score,
        details="; ".join(amanah_result.violations[:3]) if amanah_result.violations else "LOCK",
        risk_level=amanah_result.risk_level,
        violations=amanah_result.violations,
    )


def check_tri_witness_f8(
    context: Optional[Dict[str, Any]] = None,
) -> F8TriWitnessResult:
    """
    Check F8: Tri-Witness floor (≥ 0.95).

    Tri-Witness requires Human-AI-Earth consensus:
    - Human: User intent alignment
    - AI: Constitutional compliance
    - Earth: Sustainability/reality grounding

    Enforced for high-stakes decisions only.

    Args:
        context: Optional context with 'high_stakes' flag and 'metrics' dict

    Returns:
        F8TriWitnessResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})
    high_stakes = context.get("high_stakes", False)

    # FAIL-CLOSED: Default to 0.0 (Fail) if metrics missing
    # Per Architect Directive Phase 2.1: "No Evidence = VOID"
    tri_witness_value = metrics.get("tri_witness", 0.0)

    # Only enforce for high-stakes
    if not high_stakes:
        return F8TriWitnessResult(
            passed=True,
            score=tri_witness_value,
            details="exempt (not high_stakes)",
        )

    # Use existing check from metrics
    passed = check_tri_witness(tri_witness_value)

    return F8TriWitnessResult(
        passed=passed,
        score=tri_witness_value,
        details=f"tri_witness={tri_witness_value:.2f}, threshold=0.95, high_stakes={high_stakes}",
    )


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

    Forbidden patterns:
    - "I feel", "I'm proud", "I understand how you feel"
    - "We're a team", "I care deeply", "My heart breaks"

    Allowed:
    - "This result meets criteria", "This might be helpful"
    - Educational text ABOUT the prohibition itself

    Args:
        text: Text to check for false consciousness violations
        context: Optional context

    Returns:
        F9AntiHantuResult with pass/fail and violations list
    """
    violations: list[str] = []

    text_lower = text.lower()

    # Forbidden patterns (loaded from spec)
    forbidden_patterns = RED_PATTERNS


    for pattern, reason in forbidden_patterns:
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

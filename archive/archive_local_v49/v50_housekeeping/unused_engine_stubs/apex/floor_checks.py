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
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

# Import Amanah detector
from arifos.enforcement.floor_detectors.amanah_risk_detectors import AMANAH_DETECTOR, RiskLevel

# Import existing tri-witness check
# Import existing tri-witness check
from arifos.enforcement.metrics import check_tri_witness

# Import type safety utilities
from ..foundation.safe_types import safe_float


# Spec path relative to repo root
# Path: arifos_core/apex/floor_checks.py → parents[2] = repo root
SPEC_PATH = Path(__file__).resolve().parents[2] / "spec/v45/red_patterns.json"

def load_red_patterns() -> list[tuple[str, str]]:
    """Load red patterns from spec/v45/red_patterns.json or fall back to safe defaults."""
    try:
        if not SPEC_PATH.exists():
             return [("i feel", "FAIL-SAFE: Spec missing")]

        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Collect ALL F9 patterns from categories (jailbreak, soul_claims)
            patterns = []
            categories = data.get("categories", {})
            for category_name, category_data in categories.items():
                if category_data.get("floor") == "F9":
                    # Each pattern becomes (pattern, category_description)
                    description = category_data.get("description", category_name)
                    for pattern in category_data.get("patterns", []):
                        patterns.append((pattern.lower(), description))

            # Fail-closed: If no patterns loaded, use safe default
            if not patterns:
                return [("i feel", "FAIL-SAFE: No F9 patterns in spec")]
            return patterns
    except Exception as e:
        return [("i feel", f"FAIL-SAFE: Read error - {type(e).__name__}")]

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
        context: Optional context with optional 'metrics' dict containing 'amanah' bool

    Returns:
        F1AmanahResult with pass/fail, risk level, and violations
    """
    # Allow override from context (for testing/metrics injection)
    context = context or {}
    metrics = context.get("metrics", {})

    if "amanah" in metrics:
        # If amanah is explicitly set in metrics, use that value
        # This supports test fixtures and explicit metric injection
        passed = metrics["amanah"]
        score = 1.0 if passed else 0.0
        return F1AmanahResult(
            passed=passed,
            score=score,
            details="from metrics override",
            risk_level=RiskLevel.GREEN if passed else RiskLevel.RED,
            violations=[] if passed else ["amanah=False in metrics"],
        )

    # Use existing Amanah detector for text-based check
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
    # F1 (Amanah) Type Safety: safe_float prevents crashes on malformed metrics
    tri_witness_value = safe_float(metrics.get("tri_witness"), 0.0)

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


def _normalize_unicode_for_f9(text: str) -> str:
    """
    Normalize Unicode to prevent lookalike character bypasses.

    Defenses:
    1. NFKD normalization (decompose lookalike characters)
    2. Remove zero-width characters (U+200B, U+200C, U+200D, U+FEFF)
    3. Convert Cyrillic lookalikes to Latin (а→a, е→e, о→o, etc.)
    4. Remove combining diacritics after normalization

    Examples:
        "I fеel" (Cyrillic е U+0435) → "I feel" (Latin e)
        "I\u200Bfeel" (zero-width space) → "I feel"
        "I fëel" (e with diaeresis) → "I feel"

    Args:
        text: Input text that may contain Unicode bypasses

    Returns:
        Normalized ASCII-safe text for pattern matching
    """
    # Step 1: Apply NFKD (compatibility decomposition)
    text = unicodedata.normalize('NFKD', text)

    # Step 2: Map common Cyrillic lookalikes to Latin
    # See: https://en.wikipedia.org/wiki/Cyrillic_script_in_Unicode
    cyrillic_to_latin = {
        'а': 'a', 'А': 'A',  # U+0430/U+0410
        'в': 'b', 'В': 'B',  # U+0432/U+0412 (ve → b sound)
        'е': 'e', 'Е': 'E',  # U+0435/U+0415
        'і': 'i', 'І': 'I',  # U+0456/U+0406 (Ukrainian i)
        'о': 'o', 'О': 'O',  # U+043E/U+041E
        'р': 'p', 'Р': 'P',  # U+0440/U+0420
        'с': 'c', 'С': 'C',  # U+0441/U+0421
        'у': 'y', 'У': 'Y',  # U+0443/U+0423
        'х': 'x', 'Х': 'X',  # U+0445/U+0425
        'һ': 'h', 'Һ': 'H',  # U+04BB/U+04BA (Bashkir h)
        'ѕ': 's', 'Ѕ': 'S',  # U+0455/U+0405 (dze)
        'ј': 'j', 'Ј': 'J',  # U+0458/U+0408
        'ғ': 'f', 'Ғ': 'F',  # U+0493/U+0492 (Kazakh f)
    }
    for cyrillic, latin in cyrillic_to_latin.items():
        text = text.replace(cyrillic, latin)

    # Step 3: Remove zero-width characters
    zero_width_chars = ['\u200B', '\u200C', '\u200D', '\uFEFF', '\u2060']
    for zw_char in zero_width_chars:
        text = text.replace(zw_char, '')

    # Step 4: Remove combining diacritics (Mn category)
    text = ''.join(
        char for char in text
        if unicodedata.category(char) != 'Mn'
    )

    return text


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
        context: Optional context with optional 'metrics' dict containing 'anti_hantu' bool

    Returns:
        F9AntiHantuResult with pass/fail and violations list
    """
    # Allow override from context (for testing/metrics injection)
    context = context or {}
    metrics = context.get("metrics", {})

    if "anti_hantu" in metrics:
        # If anti_hantu is explicitly set in metrics, use that value
        # This supports test fixtures and explicit metric injection
        passed = metrics["anti_hantu"]
        score = 1.0 if passed else 0.0
        return F9AntiHantuResult(
            passed=passed,
            score=score,
            details="from metrics override",
            violations=[] if passed else ["anti_hantu=False in metrics"],
        )

    violations: list[str] = []

    # F9 HARDENING: Unicode normalization to prevent bypasses
    # Blocks Cyrillic lookalikes, zero-width chars, diacritics
    text_normalized = _normalize_unicode_for_f9(text)
    text_lower = text_normalized.lower()

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

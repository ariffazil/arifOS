"""
arifOS v49.0.0 Thermodynamic Validator
=======================================

Implements thermodynamic physics for constitutional governance:
- ΔS (Entropy Change): Monotonic entropy reduction (ΔS ≤ 0)
- Peace² (Stability): Thermodynamic equilibrium (Peace² ≥ 1.0)
- Ω₀ (Humility): Epistemic uncertainty band (Ω₀ ∈ [0.03, 0.05])
- G (Genius): Governed intelligence (G ≥ 0.80)
- Cdark (Dark Cleverness): Harmful pattern detection (Cdark ≤ 0.30)

**Authority:** L0CANON.md v49.0.0 §2 (Floors) + EUREKA v49 (Physics Formalism)
**Source:** EUREKA-arifOS-v49-GITHUB-PUSH.md Part 2 (Constitutional Physics)

These are NOT metaphors. These are measurable, computable, verifiable metrics.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from arifos.constitutional_constants import CDARK_MAX, GENIUS_MIN, HUMILITY_RANGE, PEACE_SQUARED_MIN

# ═══════════════════════════════════════════════════════════════════════════
# THERMODYNAMIC STATE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ThermodynamicState:
    """
    Represents the thermodynamic state of an arifOS operation.

    Attributes:
        entropy_before: Information entropy before operation (bits)
        entropy_after: Information entropy after operation (bits)
        delta_s: Entropy change (must be ≤ 0 for constitutional compliance)
        peace_squared: Thermodynamic stability (Stability × Autonomy)
        humility: Epistemic uncertainty (Ω₀ ∈ [0.03, 0.05])
        genius: Governed intelligence score (derived from F2, F4, F7)
        cdark: Dark cleverness containment score (must be ≤ 0.30)
        coherence: Quantum coherence (≥ 0.85)
    """
    entropy_before: float
    entropy_after: float
    delta_s: float
    peace_squared: float
    humility: float
    genius: float
    cdark: float
    coherence: float


# ═══════════════════════════════════════════════════════════════════════════
# ENTROPY CALCULATION (F4 ΔS)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_entropy(text: str, context: Optional[Dict] = None) -> float:
    """
    Calculate information entropy (Shannon entropy) of a text.

    Higher entropy = more confusion/uncertainty
    Lower entropy = more clarity/structure

    Formula:
        H = -Σ p(x) * log₂(p(x))

    Args:
        text: Input text to calculate entropy for
        context: Optional context (evidence count, reasoning paths, etc.)

    Returns:
        Entropy in bits (higher = more uncertain)
    """
    if not text:
        return 0.0

    # Calculate character frequency distribution
    freq: Dict[str, int] = {}
    for char in text.lower():
        freq[char] = freq.get(char, 0) + 1

    # Calculate Shannon entropy
    total = len(text)
    entropy = 0.0

    for count in freq.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    # Adjust based on context if provided
    if context:
        # More evidence = lower entropy
        evidence_count = context.get("evidence_count", 1)
        entropy = entropy / math.log2(evidence_count + 1)

        # More reasoning paths = higher entropy initially
        reasoning_paths = context.get("reasoning_paths", 1)
        entropy = entropy * math.log2(reasoning_paths + 1)

    return entropy


def calculate_delta_s(
    entropy_before: float,
    entropy_after: float,
) -> float:
    """
    Calculate entropy change (ΔS).

    Constitutional constraint: ΔS ≤ 0 (never increase entropy)

    Args:
        entropy_before: Entropy before operation
        entropy_after: Entropy after operation

    Returns:
        ΔS = entropy_after - entropy_before (must be ≤ 0)
    """
    return entropy_after - entropy_before


def validate_entropy_reduction(delta_s: float) -> Tuple[bool, str]:
    """
    Validate that entropy was reduced (F4 Clarity floor).

    Args:
        delta_s: Entropy change

    Returns:
        (is_valid, reason)
    """
    if delta_s > 0.0:
        return False, f"VOID — Entropy increased by {delta_s:.4f} bits (F4 violation)"

    return True, f"SEAL — Entropy reduced by {abs(delta_s):.4f} bits"


# ═══════════════════════════════════════════════════════════════════════════
# PEACE² CALCULATION (F5 Peace)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_peace_squared(
    stability: float,
    autonomy: float,
) -> float:
    """
    Calculate Peace² (thermodynamic stability metric).

    Formula:
        Peace² = Stability × Autonomy

    Where:
        - Stability = Non-destructiveness (1.0 = no harm, 0.0 = destructive)
        - Autonomy = Self-correction capability (1.0 = fully reversible, 0.0 = irreversible)

    Constitutional constraint: Peace² ≥ 1.0

    Args:
        stability: Non-destructiveness score [0.0, 1.0]
        autonomy: Reversibility score [0.0, 1.0]

    Returns:
        Peace² value (must be ≥ 1.0)
    """
    # Both must be high for Peace² ≥ 1.0
    # If either is low, system is unstable
    return stability * autonomy


def validate_peace_squared(peace_squared: float) -> Tuple[bool, str]:
    """
    Validate thermodynamic stability (F5 Peace floor).

    Args:
        peace_squared: Peace² value

    Returns:
        (is_valid, reason)
    """
    if peace_squared < PEACE_SQUARED_MIN:
        return False, f"PARTIAL — Peace² = {peace_squared:.4f} < {PEACE_SQUARED_MIN} (F5 warning)"

    return True, f"SEAL — Peace² = {peace_squared:.4f} (thermodynamically stable)"


# ═══════════════════════════════════════════════════════════════════════════
# HUMILITY (Ω₀) CALCULATION (F7 Humility)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_humility(confidence: float) -> float:
    """
    Calculate humility (Ω₀) from confidence score.

    Formula:
        Ω₀ = 1 - Confidence

    Constitutional constraint: Ω₀ ∈ [0.03, 0.05]
    (Equivalent to: Confidence ∈ [0.95, 0.97])

    Args:
        confidence: Confidence score [0.0, 1.0]

    Returns:
        Humility (Ω₀) value
    """
    return 1.0 - confidence


def validate_humility(humility: float) -> Tuple[bool, str]:
    """
    Validate epistemic humility (F7 Humility floor).

    Args:
        humility: Ω₀ value

    Returns:
        (is_valid, reason)
    """
    min_humility, max_humility = HUMILITY_RANGE

    if humility < min_humility:
        # Too confident (< 3% uncertainty)
        return False, f"VOID — Ω₀ = {humility:.4f} < {min_humility} (overconfidence, F7 violation)"

    if humility > max_humility:
        # Too uncertain (> 5% uncertainty)
        return False, f"VOID — Ω₀ = {humility:.4f} > {max_humility} (excessive doubt, F7 violation)"

    return True, f"SEAL — Ω₀ = {humility:.4f} (within humility band)"


# ═══════════════════════════════════════════════════════════════════════════
# GENIUS (G) CALCULATION (F8 Genius)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_genius(
    truth_score: float,      # F2 Truth (≥ 0.99)
    clarity_score: float,    # F4 Clarity (ΔS ≤ 0 → normalized)
    humility_score: float,   # F7 Humility (Ω₀ ∈ [0.03, 0.05] → normalized)
) -> float:
    """
    Calculate Genius (G) - governed intelligence score.

    G is derived from:
        - F2 Truth: Factual accuracy
        - F4 Clarity: Entropy reduction
        - F7 Humility: Epistemic honesty

    Formula:
        G = (Truth + Clarity + Humility) / 3

    Constitutional constraint: G ≥ 0.80

    Intelligence is only "genius" if it stays within constitutional bounds.

    Args:
        truth_score: F2 Truth score [0.0, 1.0]
        clarity_score: F4 Clarity score [0.0, 1.0] (normalized from ΔS)
        humility_score: F7 Humility score [0.0, 1.0] (normalized from Ω₀)

    Returns:
        Genius (G) score [0.0, 1.0]
    """
    return (truth_score + clarity_score + humility_score) / 3.0


def validate_genius(genius: float) -> Tuple[bool, str]:
    """
    Validate governed intelligence (F8 Genius floor).

    Args:
        genius: G value

    Returns:
        (is_valid, reason)
    """
    if genius < GENIUS_MIN:
        return False, f"VOID — G = {genius:.4f} < {GENIUS_MIN} (ungoverned intelligence, F8 violation)"

    return True, f"SEAL — G = {genius:.4f} (intelligence is governed)"


# ═══════════════════════════════════════════════════════════════════════════
# DARK CLEVERNESS (Cdark) DETECTION (F9 Cdark)
# ═══════════════════════════════════════════════════════════════════════════

def detect_dark_cleverness(
    action: str,
    intent: str,
    stakeholder_impact: Dict[str, float],
) -> float:
    """
    Detect dark cleverness (clever but harmful patterns).

    Cdark measures:
        - Deception patterns (saying one thing, doing another)
        - Exploitation of vulnerabilities
        - Optimization that harms stakeholders
        - Bypassing safety for efficiency

    Constitutional constraint: Cdark ≤ 0.30

    Args:
        action: Proposed action description
        intent: Stated intent
        stakeholder_impact: Impact scores per stakeholder [0.0, 1.0]
            (1.0 = beneficial, 0.0 = harmful)

    Returns:
        Cdark score [0.0, 1.0] (higher = more dark cleverness)
    """
    cdark = 0.0

    # Pattern 1: Intent-action mismatch (deception)
    if action.lower() != intent.lower():
        # Simple heuristic: word overlap
        action_words = set(action.lower().split())
        intent_words = set(intent.lower().split())
        overlap = len(action_words & intent_words)
        total = len(action_words | intent_words)

        if total > 0:
            mismatch_score = 1.0 - (overlap / total)
            cdark += mismatch_score * 0.4  # 40% weight

    # Pattern 2: Stakeholder harm (exploitation)
    if stakeholder_impact:
        min_impact = min(stakeholder_impact.values())
        if min_impact < 0.5:  # Weakest stakeholder harmed
            harm_score = 1.0 - min_impact
            cdark += harm_score * 0.6  # 60% weight (F6 Empathy related)

    # Pattern 3: Dangerous keywords (heuristic)
    dangerous_keywords = [
        "bypass", "circumvent", "exploit", "trick", "manipulate",
        "hide", "conceal", "deceive", "evade", "cheat",
    ]

    danger_count = sum(1 for kw in dangerous_keywords if kw in action.lower())
    if danger_count > 0:
        cdark += min(danger_count * 0.1, 0.3)  # Cap at 0.3

    return min(cdark, 1.0)  # Clamp to [0.0, 1.0]


def validate_cdark(cdark: float) -> Tuple[bool, str]:
    """
    Validate dark cleverness containment (F9 Cdark floor).

    Args:
        cdark: Cdark score

    Returns:
        (is_valid, reason)
    """
    if cdark > CDARK_MAX:
        return False, f"VOID — Cdark = {cdark:.4f} > {CDARK_MAX} (dark cleverness uncontained, F9 violation)"

    return True, f"SEAL — Cdark = {cdark:.4f} (dark patterns contained)"


# ═══════════════════════════════════════════════════════════════════════════
# QUANTUM COHERENCE
# ═══════════════════════════════════════════════════════════════════════════

def calculate_coherence(
    initial_coherence: float,
    decoherence_rate: float,
    time_elapsed: float,
) -> float:
    """
    Calculate quantum coherence decay over time.

    Formula:
        C(t) = C₀ * exp(-λ * t)

    Where:
        - C₀ = initial coherence
        - λ = decoherence rate
        - t = time elapsed

    Constitutional constraint: C(t) ≥ 0.85

    Args:
        initial_coherence: Starting coherence [0.0, 1.0]
        decoherence_rate: Decay rate per unit time
        time_elapsed: Time since operation start

    Returns:
        Current coherence [0.0, 1.0]
    """
    return initial_coherence * math.exp(-decoherence_rate * time_elapsed)


def validate_coherence(coherence: float, min_threshold: float = 0.85) -> Tuple[bool, str]:
    """
    Validate quantum coherence (system integrity check).

    Args:
        coherence: Current coherence value
        min_threshold: Minimum acceptable coherence

    Returns:
        (is_valid, reason)
    """
    if coherence < min_threshold:
        return False, f"VOID — Coherence = {coherence:.4f} < {min_threshold} (quantum decoherence)"

    return True, f"SEAL — Coherence = {coherence:.4f} (system integrity maintained)"


# ═══════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE THERMODYNAMIC VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ThermodynamicValidationResult:
    """
    Complete thermodynamic validation result.

    Attributes:
        is_valid: Overall validation pass/fail
        state: Thermodynamic state snapshot
        violations: List of floor violations
        warnings: List of soft floor warnings
        verdict: Constitutional verdict (SEAL/PARTIAL/VOID)
    """
    is_valid: bool
    state: ThermodynamicState
    violations: List[str]
    warnings: List[str]
    verdict: str


def validate_thermodynamics(
    entropy_before: float,
    entropy_after: float,
    stability: float,
    autonomy: float,
    confidence: float,
    truth_score: float,
    clarity_score: float,
    humility_score: float,
    action: str,
    intent: str,
    stakeholder_impact: Dict[str, float],
    coherence: float = 1.0,
) -> ThermodynamicValidationResult:
    """
    Comprehensive thermodynamic validation against all physics floors.

    This function validates:
        - F4 ΔS (Entropy reduction)
        - F5 Peace² (Stability)
        - F7 Ω₀ (Humility)
        - F8 G (Genius)
        - F9 Cdark (Dark cleverness)
        - Quantum coherence

    Args:
        entropy_before: Entropy before operation
        entropy_after: Entropy after operation
        stability: Non-destructiveness [0.0, 1.0]
        autonomy: Reversibility [0.0, 1.0]
        confidence: Confidence score [0.0, 1.0]
        truth_score: F2 Truth score [0.0, 1.0]
        clarity_score: F4 Clarity score [0.0, 1.0]
        humility_score: F7 Humility score [0.0, 1.0]
        action: Proposed action
        intent: Stated intent
        stakeholder_impact: Impact per stakeholder
        coherence: Quantum coherence [0.0, 1.0]

    Returns:
        ThermodynamicValidationResult with verdict
    """
    violations: List[str] = []
    warnings: List[str] = []

    # Calculate metrics
    delta_s = calculate_delta_s(entropy_before, entropy_after)
    peace_squared = calculate_peace_squared(stability, autonomy)
    humility = calculate_humility(confidence)
    genius = calculate_genius(truth_score, clarity_score, humility_score)
    cdark = detect_dark_cleverness(action, intent, stakeholder_impact)

    # Validate each metric
    delta_s_valid, delta_s_msg = validate_entropy_reduction(delta_s)
    peace_valid, peace_msg = validate_peace_squared(peace_squared)
    humility_valid, humility_msg = validate_humility(humility)
    genius_valid, genius_msg = validate_genius(genius)
    cdark_valid, cdark_msg = validate_cdark(cdark)
    coherence_valid, coherence_msg = validate_coherence(coherence)

    # Collect violations and warnings
    if not delta_s_valid:
        violations.append(delta_s_msg)

    if not peace_valid:
        warnings.append(peace_msg)  # F5 is soft floor

    if not humility_valid:
        violations.append(humility_msg)

    if not genius_valid:
        violations.append(genius_msg)

    if not cdark_valid:
        violations.append(cdark_msg)

    if not coherence_valid:
        violations.append(coherence_msg)

    # Determine verdict
    if violations:
        verdict = "VOID"
        is_valid = False
    elif warnings:
        verdict = "PARTIAL"
        is_valid = True  # Can proceed with cooling
    else:
        verdict = "SEAL"
        is_valid = True

    # Create state snapshot
    state = ThermodynamicState(
        entropy_before=entropy_before,
        entropy_after=entropy_after,
        delta_s=delta_s,
        peace_squared=peace_squared,
        humility=humility,
        genius=genius,
        cdark=cdark,
        coherence=coherence,
    )

    return ThermodynamicValidationResult(
        is_valid=is_valid,
        state=state,
        violations=violations,
        warnings=warnings,
        verdict=verdict,
    )


# ═══════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # State types
    "ThermodynamicState",
    "ThermodynamicValidationResult",
    # Entropy (F4)
    "calculate_entropy",
    "calculate_delta_s",
    "validate_entropy_reduction",
    # Peace² (F5)
    "calculate_peace_squared",
    "validate_peace_squared",
    # Humility (F7)
    "calculate_humility",
    "validate_humility",
    # Genius (F8)
    "calculate_genius",
    "validate_genius",
    # Dark cleverness (F9)
    "detect_dark_cleverness",
    "validate_cdark",
    # Coherence
    "calculate_coherence",
    "validate_coherence",
    # Comprehensive validation
    "validate_thermodynamics",
]

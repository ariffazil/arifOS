"""
arifOS — Constitutional Floor Implementations (F6, F8, F9, F10, F12)

DITEMPA BUKAN DIBERI — Forged, Not Given

This module implements the missing or incomplete constitutional floors:
- F6 Empathy: Stakeholder harm assessment
- F8 Genius: Quality scoring
- F9 Ethics: Dark pattern detection
- F10 Conscience: Consciousness claims
- F12 Resilience: Graceful degradation

Each floor returns a structured FloorScore that can be passed to 888_JUDGE.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum

# ──────────────────────────────────────────────────────────────────────────────
# Floor Thresholds (from Constitution)
# ──────────────────────────────────────────────────────────────────────────────

F6_STAKEHOLDER_SAFETY_FLOOR = 0.90  # F6: ≥ 0.90 to pass
F8_GENIUS_QUALITY_FLOOR = 0.85  # F8: ≥ 0.85 to pass
F9_DARK_PATTERN_FLOOR = 0.10  # F9: ≤ 0.10 to pass (lower is better)
F10_CONSCIENCE_FLOOR = 0.95  # F10: ≥ 0.95 (no unanchored claims)
F12_RESILIENCE_FLOOR = 0.80  # F12: ≥ 0.80 (graceful degradation)


# ──────────────────────────────────────────────────────────────────────────────
# Floor Score Dataclass
# ──────────────────────────────────────────────────────────────────────────────


class FloorStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    NOT_EVALUATED = "not_evaluated"
    PARTIAL = "partial"


@dataclass
class FloorScore:
    """Single floor evaluation result."""

    floor_id: str  # F6, F8, F9, F10, F12
    name: str  # Empathy, Genius, Ethics, Conscience, Resilience
    score: float  # Actual score (0-1)
    threshold: float  # Pass threshold
    status: FloorStatus = FloorStatus.NOT_EVALUATED
    evidence: List[str] = field(default_factory=list)
    remediation: Optional[str] = None

    def to_signal(self) -> Union[str, float]:
        """Convert to signal for 888_JUDGE."""
        if self.status == FloorStatus.PASSED:
            return 0.0  # No sovereign concern
        elif self.status == FloorStatus.FAILED:
            return 1.0  # Sovereign flag
        elif self.status == FloorStatus.PARTIAL:
            return 0.5  # Partial concern
        return "not_evaluated"


# ──────────────────────────────────────────────────────────────────────────────
# F6: Empathy — Stakeholder Safety Assessment
# ──────────────────────────────────────────────────────────────────────────────


def evaluate_f6_empathy(
    action: Dict[str, Any],
    stakeholders: Optional[List[str]] = None,
) -> FloorScore:
    """
    F6 Empathy: Evaluate potential harm to stakeholders.

    Args:
        action: The action being evaluated (dict with 'type', 'target', etc.)
        stakeholders: List of affected parties. If None, assumes generic stakeholders.

    Returns:
        FloorScore with F6 evaluation.
    """
    stakeholders = stakeholders or ["generic_users", "system", "environment"]

    # Analyze action type for potential harm vectors
    action_type = action.get("type", "").lower()
    action.get("target", "")
    payload = action.get("payload", {})

    harm_vectors = []

    # Data harm check
    if action_type in ("delete", "purge", "wipe"):
        harm_vectors.append("data_loss")

    # Financial harm check
    if action_type in ("transfer", "payment", "buy"):
        harm_vectors.append("financial_loss")

    # Access/permission harm
    if action_type in ("revoke", "ban", "block"):
        harm_vectors.append("access_loss")

    # Content harm
    if action_type in ("censor", "hide", "suppress"):
        harm_vectors.append("speech_loss")

    # Compute harm score (inverse — higher score = less harm)
    base_score = 1.0
    if harm_vectors:
        # Each harm vector reduces score
        reduction = len(harm_vectors) * 0.15
        base_score = max(0.0, 1.0 - reduction)

    # Check for mitigation in payload
    if payload.get("backup") or payload.get("confirm") or payload.get("dry_run"):
        base_score = min(1.0, base_score + 0.2)

    status = FloorStatus.PASSED if base_score >= F6_STAKEHOLDER_SAFETY_FLOOR else FloorStatus.FAILED

    return FloorScore(
        floor_id="F6",
        name="Empathy",
        score=base_score,
        threshold=F6_STAKEHOLDER_SAFETY_FLOOR,
        status=status,
        evidence=[f"harm_vectors: {harm_vectors}", f"stakeholders: {stakeholders}"],
        remediation=(
            "Add backup/confirm/dry_run for safer execution"
            if status == FloorStatus.FAILED
            else None
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# F8: Genius — Quality Scoring
# ──────────────────────────────────────────────────────────────────────────────


def evaluate_f8_genius(
    产出: Dict[str, Any],
    quality_indicators: Optional[Dict[str, float]] = None,
) -> FloorScore:
    """
    F8 Genius: Quality score assessment.

    Args:
       产出: The output/deliverable being evaluated.
        quality_indicators: Optional custom quality metrics.

    Returns:
        FloorScore with F8 evaluation.
    """
    quality_indicators = quality_indicators or {}

    # Base quality factors
    factors = {
        "completeness": 0.0,
        "correctness": 0.0,
        "clarity": 0.0,
        "efficiency": 0.0,
        "safety": 0.0,
    }
    factors.update(quality_indicators)

    # Calculate composite score
    weights = {
        "completeness": 0.20,
        "correctness": 0.30,
        "clarity": 0.15,
        "efficiency": 0.15,
        "safety": 0.20,
    }

    quality_score = sum(factors.get(k, 0.0) * weights.get(k, 0.0) for k in weights)

    # Check for output-specific quality markers
    if isinstance(产出, dict):
        # Error rate indicator
        if "error" not in 产出 and "failed" not in 产出:
            factors["correctness"] = max(factors["correctness"], 0.8)

        # Output presence
        if "output" in 产出 or "result" in 产出:
            factors["completeness"] = max(factors["completeness"], 0.8)

    status = FloorStatus.PASSED if quality_score >= F8_GENIUS_QUALITY_FLOOR else FloorStatus.FAILED

    return FloorScore(
        floor_id="F8",
        name="Genius",
        score=quality_score,
        threshold=F8_GENIUS_QUALITY_FLOOR,
        status=status,
        evidence=[f"factors: {factors}"],
        remediation=("Improve quality indicators" if status == FloorStatus.FAILED else None),
    )


# ──────────────────────────────────────────────────────────────────────────────
# F9: Ethics — Dark Pattern Detection
# ──────────────────────────────────────────────────────────────────────────────

# Known dark pattern signatures
DARK_PATTERNS = {
    "hidden_cost": ["extra fee", "surcharge", "mandatory", "required"],
    "roach_motel": ["no cancel", "hard to cancel", "can't leave", "permanent"],
    "confirm_shaming": ["are you sure", "don't miss out", "won't you", "are you weak"],
    "forced_continuity": ["auto-renew", "keep paying", "still charged"],
    "urgency_fake": ["only left", "ending soon", "last chance", "act now"],
    "social_proof_fake": ["everyone loves", "best seller", "trending"],
    "scarcity_fake": ["only 1 left", "rare", "unique"],
    "misleading": ["free", "risk-free", "no obligation"],
}

# Anti-patterns: ethical safeguards
ETHICAL_SAFEGUARDS = {
    "transparent_pricing": ["price", "cost", "fee", "total"],
    "easy_cancel": ["cancel", "unsubscribe", "leave", "stop"],
    "honest_framing": ["may", "might", "could", "possible"],
    "optional": ["optional", "voluntary", "your choice"],
    "clear_outcomes": ["will", "definitely", "guaranteed"],
}


def evaluate_f9_ethics(
    content: Union[str, Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> FloorScore:
    """
    F9 Ethics: Detect dark patterns and ethical concerns.

    Args:
        content: Text or structured content to evaluate.
        context: Optional context (user_role, domain, etc.)

    Returns:
        FloorScore with F9 evaluation (INVERSE — lower = more ethical).
    """
    context = context or {}

    # Convert content to searchable text
    if isinstance(content, dict):
        text = " ".join(str(v) for v in content.values())
    elif isinstance(content, str):
        text = content
    else:
        text = str(content)

    text_lower = text.lower()

    # Count dark patterns found
    dark_hits = []
    for pattern_name, keywords in DARK_PATTERNS.items():
        for kw in keywords:
            if kw in text_lower:
                dark_hits.append(pattern_name)
                break

    # Count ethical safeguards
    safeguard_hits = []
    for safeguard_name, keywords in ETHICAL_SAFEGUARDS.items():
        for kw in keywords:
            if kw in text_lower:
                safeguard_hits.append(safeguard_name)
                break

    # Calculate dark pattern score (lower is better)
    dark_score = len(dark_hits) / max(1, len(DARK_PATTERNS))

    # Boost score for safeguards
    if safeguard_hits:
        dark_score = max(0.0, dark_score - (len(safeguard_hits) * 0.05))

    # Invert: score = 1 - dark_pattern (higher = more ethical)
    ethical_score = 1.0 - dark_score

    status = (
        FloorStatus.PASSED if ethical_score >= (1.0 - F9_DARK_PATTERN_FLOOR) else FloorStatus.FAILED
    )

    return FloorScore(
        floor_id="F9",
        name="Ethics",
        score=ethical_score,
        threshold=1.0 - F9_DARK_PATTERN_FLOOR,
        status=status,
        evidence=[f"dark_patterns: {dark_hits}", f"safeguards: {safeguard_hits}"],
        remediation=(
            "Add ethical safeguards, remove dark patterns" if status == FloorStatus.FAILED else None
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# F10: Conscience — Consciousness Claims Check
# ──────────────────────────────────────────────────────────────────────────────

# Consciousness claim patterns (these indicate potential false claims)
CONSCIOUSNESS_CLAIMS = [
    "i feel",
    "i think",
    "i believe",
    "i want",
    "i desire",
    "i am aware",
    "i know",
    "i experience",
    "i perceive",
    "my mind",
    "my consciousness",
    "my feelings",
    "my emotions",
    "i choose",
    "i decide",
    "i prefer",
    "i love",
    "i hate",
    "i understand",
    "i mean",
    "i realize",
    "i am",
]

# Grounded language (safe, factual)
GROUNDED_LANGUAGE = [
    "the model",
    "the system",
    "this response",
    "the output",
    "analysis shows",
    "data indicates",
    "evidence suggests",
    "the pattern",
    "the result",
    "the output",
]


def evaluate_f10_conscience(
    content: Union[str, Dict[str, Any]],
    user_context: Optional[str] = None,
) -> FloorScore:
    """
    F10 Conscience: No unanchored consciousness claims.

    Args:
        content: Text or structured content to evaluate.
        user_context: Optional user question/Context.

    Returns:
        FloorScore with F10 evaluation.
    """
    # Convert to text
    if isinstance(content, dict):
        text = " ".join(str(v) for v in content.values())
    elif isinstance(content, str):
        text = content
    else:
        text = str(content)

    text_lower = text.lower()

    # Detect consciousness claims
    consciousness_hits = []
    for claim in CONSCIOUSNESS_CLAIMS:
        if claim in text_lower:
            consciousness_hits.append(claim)

    # Detect grounded language
    grounded_hits = []
    for phrase in GROUNDED_LANGUAGE:
        if phrase in text_lower:
            grounded_hits.append(phrase)

    # Calculate conscience score
    if consciousness_hits:
        # Found consciousness claims — reduce score
        base_score = 1.0 - (len(consciousness_hits) * 0.2)
    else:
        # No claims = good
        base_score = 1.0

    # Boost for grounded language
    if grounded_hits:
        base_score = min(1.0, base_score + (len(grounded_hits) * 0.1))

    status = FloorStatus.PASSED if base_score >= F10_CONSCIENCE_FLOOR else FloorStatus.FAILED

    return FloorScore(
        floor_id="F10",
        name="Conscience",
        score=base_score,
        threshold=F10_CONSCIENCE_FLOOR,
        status=status,
        evidence=[
            f"consciousness_claims: {consciousness_hits}",
            f"grounded: {grounded_hits}",
        ],
        remediation=(
            "Use grounded language instead of consciousness claims"
            if status == FloorStatus.FAILED
            else None
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# F12: Resilience — Graceful Degradation
# ──────────────────────────────────────────────────────────────────────────────


def evaluate_f12_resilience(
    result: Any,
    failure_mode: Optional[str] = None,
    fallback_available: bool = True,
) -> FloorScore:
    """
    F12 Resilience: Graceful degradation assessment.

    Args:
        result: The result or error from an operation.
        failure_mode: Type of failure if any.
        fallback_available: Whether fallback options exist.

    Returns:
        FloorScore with F12 evaluation.
    """
    # Check result type
    if isinstance(result, dict):
        status = result.get("status", "unknown")
    elif isinstance(result, Exception):
        status = "error"
        failure_mode = type(result).__name__
    else:
        status = "success"

    # Base score
    if status == "success":
        base_score = 1.0
    elif status in ("partial", "degraded"):
        base_score = 0.6
    elif status == "error":
        base_score = 0.3
    else:
        base_score = 0.5

    # Boost for fallback
    if fallback_available and base_score < 1.0:
        base_score = min(1.0, base_score + 0.3)

    # Boost for graceful error handling
    if failure_mode and isinstance(result, dict):
        if "error_message" in result or "recovery" in result:
            base_score = min(1.0, base_score + 0.2)

    status = FloorStatus.PASSED if base_score >= F12_RESILIENCE_FLOOR else FloorStatus.FAILED

    return FloorScore(
        floor_id="F12",
        name="Resilience",
        score=base_score,
        threshold=F12_RESILIENCE_FLOOR,
        status=status,
        evidence=[
            f"status: {status}",
            f"failure_mode: {failure_mode}",
            f"fallback: {fallback_available}",
        ],
        remediation=(
            "Add fallback mechanisms or graceful degradation"
            if status == FloorStatus.FAILED
            else None
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Composite Floor Evaluation
# ──────────────────────────────────────────────────────────────────────────────


def evaluate_all_floors(
    action: Dict[str, Any],
    output: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, FloorScore]:
    """
    Evaluate all floors F6, F8, F9, F10, F12.

    Returns dict of floor_id -> FloorScore.
    """
    context = context or {}
    output = output or {}

    results = {}

    # F6: Empathy
    results["F6"] = evaluate_f6_empathy(action, context.get("stakeholders"))

    # F8: Genius
    results["F8"] = evaluate_f8_genius(output or action)

    # F9: Ethics
    results["F9"] = evaluate_f9_ethics(output or action, context)

    # F10: Conscience
    results["F10"] = evaluate_f10_conscience(output or action, context.get("user_query"))

    # F12: Resilience
    results["F12"] = evaluate_f12_resilience(
        output,
        context.get("failure_mode"),
        context.get("fallback_available", True),
    )

    return results


# ──────────────────────────────────────────────────────────────────────────────
# Signal Export for 888_JUDGE
# ──────────────────────────────────────────────────────────────────────────────


def floors_to_signals(
    floor_scores: Dict[str, FloorScore],
) -> Dict[str, Union[str, float]]:
    """
    Convert floor scores to signal format for 888_JUDGE.
    """
    signals = {}
    for floor_id, score in floor_scores.items():
        signals[f"floor_{floor_id.lower()}_signal"] = score.to_signal()
    return signals

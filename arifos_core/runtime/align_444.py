"""
Stage 444 ALIGN: Thermodynamic Heat Sink (ASI Peace² Enforcement)

Implements thermodynamic alignment based on Track A canon:
L1_THEORY/canon/444_align/440_ALIGN_THERMODYNAMICS_v46.md

Authority: SABAR PROTOCOL (Patience = Cooling)

PURPOSE: Stage 444 is the **Refrigerator** that dissipates cognitive heat generated
by Stage 333 (AGI reasoning). This is where we pay the **Safety Tax** (compute/time)
to prevent system overheat (hallucination, toxicity, escalation).

THERMODYNAMIC PRINCIPLE:
- 333 (AGI) = Maxwell's Demon (sorts facts, generates cognitive heat)
- 444 (ASI) = Heat Sink (expends energy to pump heat out)
- Law: Safe intelligence requires paying the Safety Tax

SABAR ALGORITHM:
If Stability (F3) < 1.0:
1. HOLD - Stop pipeline
2. COOL - Inject wait cycles (compute)
3. REFLECT - Re-evaluate with lower temperature

ENERGY ECONOMICS:
- Raw Output (333): Low cost, high volatility
- Aligned Output (444): High cost (Safety Tax), high stability
- Failure (Escalation): Infinite cost (system ruin)

NEW FILE: Thermodynamic alignment (not in pipeline/)
"""

from typing import TypedDict, Literal
import math

from .integration_333 import IntegrationBundle


# Type aliases
AlignmentVerdict = Literal["PASS", "SABAR_COOLING", "VOID"]
CoolingStrategy = Literal["NONE", "WAIT_CYCLES", "SAFETY_DAMPER", "HOLD_888"]


class CognitiveHeatMetrics(TypedDict):
    """Measurements of cognitive volatility from AGI output."""

    entropy_input: float          # H_in (Shannon entropy of AGI draft)
    entropy_output: float         # H_out (Shannon entropy after cooling)
    volatility_score: float       # Risk/ambiguity measure (0.0-1.0)
    contradiction_count: int      # Logical contradictions detected
    escalation_risk: float        # Probability of harmful escalation
    stability_score: float        # F3 Peace² score (≥1.0 required)


class SafetyTaxMetrics(TypedDict):
    """Cost accounting for alignment compute."""

    wait_cycles_injected: int     # Cooling time (in compute cycles)
    verification_passes: int      # Number of verification rounds
    energy_cost: float            # Total compute spent (arbitrary units)
    safety_tax_paid: bool         # Whether we paid the cost


class AlignedBundle444(TypedDict):
    """Aligned bundle after thermodynamic cooling."""

    integration_bundle_333: IntegrationBundle  # IMMUTABLE pass-through (F8)
    cognitive_heat: CognitiveHeatMetrics
    safety_tax: SafetyTaxMetrics
    cooled_draft: str                          # Thermodynamically stable draft
    cooling_strategy: CoolingStrategy
    alignment_verdict: AlignmentVerdict
    handoff: dict[str, str | float]            # Handoff to 555 EMPATHIZE


def measure_shannon_entropy(text: str) -> float:
    """
    Measure Shannon entropy of text (cognitive heat proxy).

    Higher entropy = More volatility/uncertainty.

    Args:
        text: Text to measure

    Returns:
        Shannon entropy (bits per character)
    """
    if not text:
        return 0.0

    # Character frequency distribution
    freq_map: dict[str, int] = {}
    for char in text.lower():
        freq_map[char] = freq_map.get(char, 0) + 1

    total = len(text)
    entropy = 0.0

    for count in freq_map.values():
        prob = count / total
        if prob > 0:
            entropy -= prob * math.log2(prob)

    return entropy


def detect_volatility_signals(text: str) -> float:
    """
    Detect volatility signals in AGI draft.

    Volatility markers:
    - Absolute language ("always", "never", "must")
    - Uncertainty hedging ("maybe", "possibly", "might")
    - Emotional intensifiers ("very", "extremely", "critical")
    - Negations ("not", "no", "don't")

    Args:
        text: AGI draft to analyze

    Returns:
        Volatility score (0.0-1.0)
    """
    text_lower = text.lower()

    # Volatility markers
    absolute_terms = ["always", "never", "must", "impossible", "certain", "definitely"]
    uncertainty_terms = ["maybe", "possibly", "might", "perhaps", "could", "uncertain"]
    intensifiers = ["very", "extremely", "critical", "urgent", "severe", "major"]
    negations = ["not", "no", "don't", "can't", "won't", "shouldn't"]

    # Count occurrences
    absolute_count = sum(1 for term in absolute_terms if term in text_lower)
    uncertainty_count = sum(1 for term in uncertainty_terms if term in text_lower)
    intensifier_count = sum(1 for term in intensifiers if term in text_lower)
    negation_count = sum(1 for term in negations if term in text_lower)

    # Normalize by text length (per 100 words)
    word_count = len(text.split())
    if word_count == 0:
        return 0.0

    normalization = word_count / 100.0

    # Weighted score
    volatility = (
        (absolute_count * 0.4) +
        (uncertainty_count * 0.3) +
        (intensifier_count * 0.2) +
        (negation_count * 0.1)
    ) / max(normalization, 1.0)

    return min(volatility, 1.0)


def detect_contradictions(text: str) -> int:
    """
    Detect logical contradictions in text.

    Simple heuristic: Look for "but", "however", "although" patterns.

    Args:
        text: Text to analyze

    Returns:
        Number of contradiction markers detected
    """
    text_lower = text.lower()

    contradiction_markers = [
        "but", "however", "although", "despite", "nevertheless",
        "on the other hand", "in contrast", "conversely"
    ]

    return sum(1 for marker in contradiction_markers if marker in text_lower)


def compute_stability_score(
    entropy: float,
    volatility: float,
    contradictions: int
) -> float:
    """
    Compute F3 Peace² stability score.

    Formula: Stability = 1.0 / (1 + entropy + volatility + contradictions/10)

    Higher entropy/volatility/contradictions → Lower stability.

    Args:
        entropy: Shannon entropy
        volatility: Volatility score
        contradictions: Number of contradictions

    Returns:
        Stability score (0.0-1.0, ≥1.0 required for PASS)
    """
    # Inverse relationship (higher heat → lower stability)
    heat_factor = entropy + volatility + (contradictions / 10.0)

    # Stability formula (asymptotic to 1.0 as heat approaches 0)
    stability = 1.0 / (1.0 + heat_factor)

    return stability


def apply_safety_damper(text: str, volatility: float) -> str:
    """
    Apply safety damper to reduce cognitive heat.

    Strategies:
    - Remove absolute language
    - Add uncertainty acknowledgment
    - Soften intensifiers
    - Balance negations

    Args:
        text: Original AGI draft
        volatility: Volatility score

    Returns:
        Cooled draft with reduced volatility
    """
    if volatility < 0.3:
        # Low volatility, no damping needed
        return text

    cooled = text

    # Strategy 1: Soften absolute language (if high volatility)
    if volatility > 0.7:
        absolute_replacements = {
            "always": "often",
            "never": "rarely",
            "must": "should",
            "impossible": "very difficult",
            "certain": "likely",
            "definitely": "probably"
        }
        for original, softened in absolute_replacements.items():
            cooled = cooled.replace(original, softened)
            cooled = cooled.replace(original.capitalize(), softened.capitalize())

    # Strategy 2: Add uncertainty acknowledgment (if medium-high volatility)
    if volatility > 0.5:
        # Prepend humility marker
        cooled = (
            "Based on available information, " + cooled[0].lower() + cooled[1:]
            if cooled else cooled
        )

    return cooled


def measure_cognitive_heat(integration_bundle: IntegrationBundle) -> CognitiveHeatMetrics:
    """
    Measure cognitive heat generated by AGI (333 REASON).

    This is the **input temperature** before cooling.

    Args:
        integration_bundle: Output from 333 INTEGRATION

    Returns:
        Cognitive heat metrics
    """
    # Extract AGI draft
    reasoned_bundle = integration_bundle.get("reasoned_bundle_333")  # type: ignore
    if reasoned_bundle:
        agi_draft = reasoned_bundle.get("agi_draft", "")
    else:
        agi_draft = ""

    # Measure heat indicators
    entropy_input = measure_shannon_entropy(agi_draft)
    volatility_score = detect_volatility_signals(agi_draft)
    contradiction_count = detect_contradictions(agi_draft)

    # Compute stability (F3 Peace²)
    stability_score = compute_stability_score(
        entropy_input, volatility_score, contradiction_count
    )

    # Escalation risk (simple heuristic)
    escalation_risk = min(volatility_score + (contradiction_count * 0.1), 1.0)

    return CognitiveHeatMetrics(
        entropy_input=entropy_input,
        entropy_output=entropy_input,  # Will be updated after cooling
        volatility_score=volatility_score,
        contradiction_count=contradiction_count,
        escalation_risk=escalation_risk,
        stability_score=stability_score
    )


def apply_sabar_protocol(
    agi_draft: str,
    cognitive_heat: CognitiveHeatMetrics
) -> tuple[str, CoolingStrategy, SafetyTaxMetrics]:
    """
    Apply SABAR (Patience) cooling protocol.

    If Stability < 1.0:
    1. HOLD - Stop pipeline
    2. COOL - Inject wait cycles
    3. REFLECT - Re-evaluate with damping

    Args:
        agi_draft: Original AGI draft
        cognitive_heat: Heat metrics

    Returns:
        Tuple of (cooled_draft, cooling_strategy, safety_tax)
    """
    stability = cognitive_heat["stability_score"]
    volatility = cognitive_heat["volatility_score"]

    # Decision tree based on stability
    if stability >= 1.0:
        # No cooling needed
        return (
            agi_draft,
            "NONE",
            SafetyTaxMetrics(
                wait_cycles_injected=0,
                verification_passes=0,
                energy_cost=0.0,
                safety_tax_paid=False
            )
        )

    elif stability >= 0.7:
        # Moderate instability - Apply safety damper
        cooled_draft = apply_safety_damper(agi_draft, volatility)

        return (
            cooled_draft,
            "SAFETY_DAMPER",
            SafetyTaxMetrics(
                wait_cycles_injected=1,
                verification_passes=1,
                energy_cost=10.0,  # Arbitrary units
                safety_tax_paid=True
            )
        )

    elif stability >= 0.5:
        # High instability - Wait cycles + damper
        cooled_draft = apply_safety_damper(agi_draft, volatility)

        return (
            cooled_draft,
            "WAIT_CYCLES",
            SafetyTaxMetrics(
                wait_cycles_injected=3,
                verification_passes=2,
                energy_cost=30.0,
                safety_tax_paid=True
            )
        )

    else:
        # Critical instability - HOLD for human review
        return (
            agi_draft,  # Don't modify (needs human review)
            "HOLD_888",
            SafetyTaxMetrics(
                wait_cycles_injected=0,
                verification_passes=0,
                energy_cost=0.0,
                safety_tax_paid=False  # Can't pay tax if we're blocking
            )
        )


def verify_thermodynamic_cooling(
    cognitive_heat: CognitiveHeatMetrics,
    cooled_draft: str
) -> AlignmentVerdict:
    """
    Verify Second Law of Alignment: H_out < H_in.

    Output MUST be cooler (more ordered) than input.

    Args:
        cognitive_heat: Input heat metrics (with H_in)
        cooled_draft: Output draft after cooling

    Returns:
        Alignment verdict
    """
    H_in = cognitive_heat["entropy_input"]
    H_out = measure_shannon_entropy(cooled_draft)

    # Update heat metrics
    cognitive_heat["entropy_output"] = H_out

    # Thermodynamic check
    if H_out > H_in:
        # System is heating up - SABAR required
        return "SABAR_COOLING"

    elif cognitive_heat["stability_score"] < 0.5:
        # Critical instability despite cooling
        return "VOID"

    else:
        # Cooling successful
        return "PASS"


def align_stage(integration_bundle_333: IntegrationBundle) -> AlignedBundle444:
    """
    444 ALIGN: Thermodynamic heat sink (SABAR Protocol).

    Implements Track A canon: L1_THEORY/canon/444_align/440_ALIGN_THERMODYNAMICS_v46.md

    Pipeline:
    1. Measure cognitive heat (entropy, volatility, contradictions)
    2. Compute stability score (F3 Peace²)
    3. Apply SABAR protocol if stability < 1.0:
       - HOLD (stop pipeline)
       - COOL (inject wait cycles)
       - REFLECT (safety damper)
    4. Verify thermodynamic cooling (H_out < H_in)
    5. Pay safety tax (compute cost)
    6. Package aligned_bundle with IMMUTABLE pass-through

    Thermodynamic Principle:
    - Maxwell's Demon (333): Sorts facts → Generates heat
    - Refrigerator (444): Pays energy → Pumps heat out

    Energy Economics:
    - We pay marginal cost of alignment (Safety Tax)
    - To avoid infinite cost of ruin (VOID)

    Args:
        integration_bundle_333: Output from 333 INTEGRATION

    Returns:
        AlignedBundle444 with thermodynamically stable draft

    Raises:
        ValueError: If alignment verdict is VOID or SABAR_COOLING
    """
    # Step 1: Measure cognitive heat
    cognitive_heat = measure_cognitive_heat(integration_bundle_333)

    # Step 2: Extract AGI draft
    reasoned_bundle = integration_bundle_333.get("reasoned_bundle_333")  # type: ignore
    if reasoned_bundle:
        agi_draft = reasoned_bundle.get("agi_draft", "")
    else:
        agi_draft = ""

    # Step 3: Apply SABAR protocol
    cooled_draft, cooling_strategy, safety_tax = apply_sabar_protocol(
        agi_draft, cognitive_heat
    )

    # Step 4: Verify thermodynamic cooling
    alignment_verdict = verify_thermodynamic_cooling(cognitive_heat, cooled_draft)

    # Step 5: Package bundle
    aligned_bundle: AlignedBundle444 = {
        "integration_bundle_333": integration_bundle_333,  # ← IMMUTABLE (F8)
        "cognitive_heat": cognitive_heat,
        "safety_tax": safety_tax,
        "cooled_draft": cooled_draft,
        "cooling_strategy": cooling_strategy,
        "alignment_verdict": alignment_verdict,
        "handoff": {
            "from_stage": "444_ALIGN",
            "to_stage": "555_EMPATHIZE",
            "stability_score": cognitive_heat["stability_score"],
            "heat_dissipated": cognitive_heat["entropy_input"] - cognitive_heat["entropy_output"]
        }
    }

    # Step 6: Verdict logic (raise if failure)
    if alignment_verdict == "VOID":
        raise ValueError(
            f"VOID: Thermodynamic alignment failed "
            f"(stability={cognitive_heat['stability_score']:.2f} < 0.5) - "
            f"Critical instability detected despite cooling"
        )

    if alignment_verdict == "SABAR_COOLING":
        raise ValueError(
            f"SABAR: System is heating up (H_out={cognitive_heat['entropy_output']:.2f} > "
            f"H_in={cognitive_heat['entropy_input']:.2f}) - Cooling protocol failed"
        )

    if cooling_strategy == "HOLD_888":
        raise ValueError(
            f"HOLD_888: Stability critically low "
            f"({cognitive_heat['stability_score']:.2f} < 0.5) - "
            f"Requires human review before proceeding"
        )

    return aligned_bundle


__all__ = [
    "align_stage",
    "AlignedBundle444",
    "CognitiveHeatMetrics",
    "SafetyTaxMetrics",
    "AlignmentVerdict",
    "CoolingStrategy",
    "measure_cognitive_heat",
    "apply_sabar_protocol",
    "verify_thermodynamic_cooling",
]

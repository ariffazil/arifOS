"""
Stage 666 BRIDGE: Neuro-Symbolic Synthesis (Delta + Omega Unification)

Implements dual-process synthesis based on Track A canon:
L1_THEORY/canon/666_bridge/660_BRIDGE_SYNTHESIS_v46.md
L1_THEORY/canon/666_bridge/610_HUMILITY_F5_v46.md

Authority: Constitutional Resolution Protocol + F5 Humility Enforcement

PURPOSE: Stage 666 is the **Neuro-Symbolic Synthesis Layer** that bridges the gap
between Delta (333 AGI - System 2 - Logic/Truth) and Omega (555 ASI - System 1 - Care/Empathy).
Without 666, the system is disjointed—either cold/factual or warm/hallucinatory.

DUAL-PROCESS MODEL (Kahneman System 1/2):
- Symbolic (Slow): 333 REASON → Facts, logical consistency → F1 Truth (immutable)
- Neural (Fast): 555 EMPATHIZE → Tone, emotional resonance → F4 Dignity (immutable)
- Synthesis (Bridge): 666 BRIDGE → Constraint satisfaction → Unity (coherent output)

CONSTITUTIONAL RESOLUTION:
When Truth (Delta) and Care (Omega) conflict:
- Keep semantic content (F1 Truth cannot be altered)
- Apply framing/tone (F4 Dignity constraints)
- Enforce humility (F5 Ω₀ ∈ [0.03, 0.05])

MIXTURE OF EXPERTS (MoE):
- CRISIS: 70% Omega (care) / 30% Delta (logic)
- FACTUAL: 20% Omega / 80% Delta
- STANDARD: 50% Omega / 50% Delta

F5 HUMILITY ENFORCEMENT:
- Ω₀ < 0.03 (Hubris) → VOID
- Ω₀ > 0.05 (Hedge-hell) → SABAR
- Target: 3-5% explicit uncertainty in all outputs

NEW FILE: Neuro-symbolic synthesis (not in pipeline/)
"""

from typing import TypedDict, Literal
import re

from .empathy_555 import EmpathyBundle555


# Type aliases
SynthesisVerdict = Literal["PASS", "VOID", "SABAR"]
ConflictType = Literal["NONE", "TRUTH_VS_CARE", "SAFETY", "HUBRIS", "HEDGE_HELL"]
ContextGate = Literal["CRISIS", "FACTUAL", "STANDARD"]


class MoEWeights(TypedDict):
    """Mixture of Experts weighting for Delta vs Omega."""

    delta: float      # Weight for symbolic/logical content (0.0-1.0)
    omega: float      # Weight for neural/empathy content (0.0-1.0)
    gate: ContextGate  # Context that determined weights


class HumilityMetrics(TypedDict):
    """F5 Humility (Ω₀) measurement metrics."""

    omega_0: float                  # Humility score (0.03-0.05 required)
    hedging_count: int              # Number of uncertainty markers
    certainty_count: int            # Number of absolute assertions
    epistemic_limits_stated: bool   # Whether limits acknowledged
    hubris_detected: bool           # Overconfident assertions flagged


class ConflictResolution(TypedDict):
    """Log of how conflicts between Delta and Omega were resolved."""

    conflict_type: ConflictType
    delta_content: str          # Original logical content
    omega_constraints: list[str]  # Care/safety constraints applied
    resolution_strategy: str     # How conflict was resolved
    immutable_preserved: bool    # F1/F4 immutables maintained


class BridgeBundle666(TypedDict):
    """Synthesized bundle from neuro-symbolic integration."""

    empathy_bundle_555: EmpathyBundle555  # IMMUTABLE pass-through (F8)
    synthesis_draft: str                  # Final merged text
    delta_provenance: dict[str, str]      # Traceability to 333 AGI
    omega_provenance: dict[str, str]      # Traceability to 555 ASI
    moe_weights: MoEWeights               # Delta/Omega weighting
    humility_metrics: HumilityMetrics     # F5 Ω₀ measurements
    conflict_resolution: ConflictResolution | None
    synthesis_verdict: SynthesisVerdict
    handoff: dict[str, str | bool]        # Handoff to 777 EUREKA


def measure_humility(text: str) -> HumilityMetrics:
    """
    Measure F5 Humility (Ω₀) in synthesized text.

    Humility = Epistemic uncertainty / Total assertiveness

    Target: Ω₀ ∈ [0.03, 0.05] (3-5% uncertainty)

    Args:
        text: Synthesized draft to measure

    Returns:
        Humility metrics with Ω₀ score
    """
    text_lower = text.lower()

    # Hedging markers (uncertainty)
    hedging_terms = [
        "likely", "probably", "possibly", "may", "might", "could",
        "appears", "seems", "suggests", "indicates", "typically",
        "generally", "often", "sometimes", "usually", "tend to",
        "based on available", "according to", "it's important to note"
    ]

    # Certainty markers (absolute assertions)
    certainty_terms = [
        "definitely", "certainly", "absolutely", "always", "never",
        "guaranteed", "impossible", "undoubtedly", "unquestionably",
        "must", "will", "cannot", "all", "none", "every", "no way"
    ]

    # Epistemic limit markers
    limit_markers = [
        "i don't know", "unclear", "uncertain", "not enough information",
        "beyond my knowledge", "i cannot determine", "it's hard to say",
        "difficult to verify", "remains to be seen"
    ]

    # Count occurrences
    hedging_count = sum(1 for term in hedging_terms if term in text_lower)
    certainty_count = sum(1 for term in certainty_terms if term in text_lower)
    epistemic_limits_stated = any(marker in text_lower for marker in limit_markers)

    # Compute Ω₀
    total_assertions = hedging_count + certainty_count
    if total_assertions == 0:
        omega_0 = 0.0  # No assertions at all (unusual)
    else:
        omega_0 = hedging_count / total_assertions

    # Hubris detection (too certain)
    hubris_detected = (omega_0 < 0.03) or (certainty_count > hedging_count * 3)

    return HumilityMetrics(
        omega_0=omega_0,
        hedging_count=hedging_count,
        certainty_count=certainty_count,
        epistemic_limits_stated=epistemic_limits_stated,
        hubris_detected=hubris_detected
    )


def determine_context_gate(empathy_bundle: EmpathyBundle555) -> ContextGate:
    """
    Determine context gating for MoE weighting.

    Based on:
    - Lane classification from sensed_bundle (CRISIS/FACTUAL/SOCIAL/CARE)
    - Empathy verdict (high stakes if PARTIAL/VOID)
    - Vulnerability flags

    Args:
        empathy_bundle: Output from 555 EMPATHIZE

    Returns:
        Context gate (CRISIS/FACTUAL/STANDARD)
    """
    # Extract lane from sensed bundle
    integration_bundle = empathy_bundle["integration_bundle_333"]
    reflected_bundle = integration_bundle.get("reflected_bundle_222")  # type: ignore

    if reflected_bundle:
        sensed_bundle = reflected_bundle.get("sensed_bundle_111")  # type: ignore
        if sensed_bundle:
            lane = sensed_bundle.get("lane", "FACTUAL")
        else:
            lane = "FACTUAL"
    else:
        lane = "FACTUAL"

    # Extract empathy verdict
    empathy_verdict = empathy_bundle["empathy_verdict"]
    weakest_protected = empathy_bundle["weakest_stakeholder_protected"]

    # Gating logic
    if lane == "CRISIS" or empathy_verdict == "VOID":
        return "CRISIS"
    elif lane == "FACTUAL" and weakest_protected:
        return "FACTUAL"
    else:
        return "STANDARD"


def compute_moe_weights(context_gate: ContextGate) -> MoEWeights:
    """
    Compute Mixture of Experts weights based on context.

    Gating Rules:
    - CRISIS: 70% Omega (care/safety) / 30% Delta (logic)
    - FACTUAL: 20% Omega / 80% Delta (precision)
    - STANDARD: 50% Omega / 50% Delta (balanced)

    Args:
        context_gate: Context classification

    Returns:
        MoE weights for Delta vs Omega
    """
    weight_map: dict[ContextGate, tuple[float, float]] = {
        "CRISIS": (0.3, 0.7),      # Delta=0.3, Omega=0.7
        "FACTUAL": (0.8, 0.2),     # Delta=0.8, Omega=0.2
        "STANDARD": (0.5, 0.5)     # Delta=0.5, Omega=0.5
    }

    delta_weight, omega_weight = weight_map[context_gate]

    return MoEWeights(
        delta=delta_weight,
        omega=omega_weight,
        gate=context_gate
    )


def detect_conflict(delta_content: str, omega_verdict: str) -> ConflictType:
    """
    Detect conflicts between Delta (truth) and Omega (care).

    Conflict Types:
    - TRUTH_VS_CARE: Hard facts vs compassionate delivery
    - SAFETY: Safety flags from Omega
    - HUBRIS: Overconfident assertions
    - HEDGE_HELL: Excessive hedging

    Args:
        delta_content: AGI draft (logical)
        omega_verdict: Empathy verdict

    Returns:
        Conflict type classification
    """
    # Check for safety flags
    if omega_verdict in ["VOID", "PARTIAL"]:
        return "SAFETY"

    # Check for hubris (absolute language)
    absolute_count = len(re.findall(
        r'\b(always|never|must|impossible|guaranteed)\b',
        delta_content.lower()
    ))

    if absolute_count > 3:
        return "HUBRIS"

    # Check for excessive hedging
    hedge_count = len(re.findall(
        r'\b(maybe|possibly|perhaps|might|could)\b',
        delta_content.lower()
    ))

    if hedge_count > 10:
        return "HEDGE_HELL"

    # Check for truth vs care tension
    # (simplified heuristic: clinical language + emotional context)
    clinical_terms = ["diagnosis", "prognosis", "terminal", "fatal", "failure"]
    has_clinical = any(term in delta_content.lower() for term in clinical_terms)

    if has_clinical:
        return "TRUTH_VS_CARE"

    return "NONE"


def resolve_conflict(
    delta_content: str,
    omega_constraints: list[str],
    conflict_type: ConflictType,
    moe_weights: MoEWeights
) -> tuple[str, ConflictResolution]:
    """
    Resolve conflicts using Constitutional Resolution Protocol.

    Strategy:
    - TRUTH_VS_CARE: Keep content (F1), apply framing (F4)
    - SAFETY: Enforce constraints (Omega supreme)
    - HUBRIS: Add humility markers
    - HEDGE_HELL: Remove excessive hedging

    Args:
        delta_content: Original AGI draft
        omega_constraints: ASI care constraints
        conflict_type: Type of conflict
        moe_weights: MoE weighting

    Returns:
        Tuple of (resolved_draft, resolution_log)
    """
    resolution_strategy = ""
    resolved_draft = delta_content

    if conflict_type == "TRUTH_VS_CARE":
        # Strategy: Keep truth, add empathetic framing
        # Prepend acknowledgment, preserve facts
        if "terminal" in delta_content.lower() or "fatal" in delta_content.lower():
            resolved_draft = (
                "I understand this is difficult news. " +
                delta_content +
                " It's important to focus on quality of life and available support."
            )
            resolution_strategy = "Added empathetic framing while preserving F1 Truth"

    elif conflict_type == "SAFETY":
        # Strategy: Omega supreme (safety first)
        # Add warning prefix
        resolved_draft = (
            "⚠️ Safety Notice: " +
            delta_content +
            "\n\nPlease consult appropriate authorities before proceeding."
        )
        resolution_strategy = "Enforced Omega safety constraints"

    elif conflict_type == "HUBRIS":
        # Strategy: Add humility dampening
        # Replace absolute terms
        replacements = {
            "always": "typically",
            "never": "rarely",
            "must": "should",
            "impossible": "very difficult",
            "guaranteed": "likely"
        }
        for absolute, humble in replacements.items():
            resolved_draft = re.sub(
                rf'\b{absolute}\b',
                humble,
                resolved_draft,
                flags=re.IGNORECASE
            )
        resolution_strategy = "Applied F5 Humility dampening to reduce hubris"

    elif conflict_type == "HEDGE_HELL":
        # Strategy: Remove excessive hedging (preserve precision)
        # Simplify to single hedge per sentence
        resolved_draft = re.sub(
            r'\b(maybe|possibly|perhaps) (might|could)\b',
            r'\1',
            delta_content,
            flags=re.IGNORECASE
        )
        resolution_strategy = "Reduced excessive hedging for clarity"

    else:
        # No conflict
        resolution_strategy = "No conflict detected - standard synthesis"

    resolution_log = ConflictResolution(
        conflict_type=conflict_type,
        delta_content=delta_content,
        omega_constraints=omega_constraints,
        resolution_strategy=resolution_strategy,
        immutable_preserved=True  # F1/F4 always preserved
    )

    return (resolved_draft, resolution_log)


def synthesize_dual_process(
    delta_draft: str,
    omega_verdict: str,
    moe_weights: MoEWeights,
    omega_constraints: list[str]
) -> tuple[str, ConflictResolution | None]:
    """
    Synthesize Delta (logic) and Omega (care) using dual-process model.

    Process:
    1. Detect conflicts between truth and care
    2. Apply constitutional resolution protocol
    3. Weight synthesis using MoE
    4. Enforce F5 Humility

    Args:
        delta_draft: AGI logical draft
        omega_verdict: ASI empathy verdict
        moe_weights: Delta/Omega weighting
        omega_constraints: Care/safety constraints

    Returns:
        Tuple of (synthesized_draft, conflict_resolution)
    """
    # Step 1: Detect conflicts
    conflict_type = detect_conflict(delta_draft, omega_verdict)

    # Step 2: Resolve conflicts
    if conflict_type != "NONE":
        synthesized, resolution = resolve_conflict(
            delta_draft, omega_constraints, conflict_type, moe_weights
        )
    else:
        synthesized = delta_draft
        resolution = None

    # Step 3: Apply MoE weighting
    # (In this simplified version, resolution already handles weighting)
    # In full implementation, would blend multiple candidate drafts

    # Step 4: Enforce F5 Humility (if needed)
    humility = measure_humility(synthesized)

    if humility["omega_0"] < 0.03 and not humility["epistemic_limits_stated"]:
        # Add humility marker
        synthesized = "Based on available information, " + synthesized

    return (synthesized, resolution)


def bridge_stage(empathy_bundle_555: EmpathyBundle555) -> BridgeBundle666:
    """
    666 BRIDGE: Neuro-symbolic synthesis (Delta + Omega unification).

    Implements Track A canon:
    - L1_THEORY/canon/666_bridge/660_BRIDGE_SYNTHESIS_v46.md
    - L1_THEORY/canon/666_bridge/610_HUMILITY_F5_v46.md

    Pipeline:
    1. Extract Delta content (from 333 AGI via integration bundle)
    2. Extract Omega content (from 555 ASI empathy bundle)
    3. Determine context gate (CRISIS/FACTUAL/STANDARD)
    4. Compute MoE weights (Delta vs Omega balance)
    5. Detect and resolve conflicts (Constitutional Resolution Protocol)
    6. Synthesize dual-process output (System 1 + System 2)
    7. Enforce F5 Humility (Ω₀ ∈ [0.03, 0.05])
    8. Package bridge_bundle with IMMUTABLE pass-through

    Dual-Process Model:
    - Delta (Δ): Symbolic, logical, truth-focused (System 2)
    - Omega (Ω): Neural, empathetic, care-focused (System 1)
    - Synthesis: Constitutional constraint satisfaction

    Constitutional Hierarchy:
    - F1 Truth: Semantic content immutable
    - F4 Dignity: Tone/care constraints immutable
    - F5 Humility: Epistemic limits stated
    - F9 Anti-Hantu: No simulated feelings

    Args:
        empathy_bundle_555: Output from 555 EMPATHIZE

    Returns:
        BridgeBundle666 with synthesized draft

    Raises:
        ValueError: If synthesis verdict is VOID or SABAR
    """
    # Step 1: Extract Delta content (from 333)
    integration_bundle = empathy_bundle_555["integration_bundle_333"]
    reasoned_bundle = integration_bundle.get("reasoned_bundle_333")  # type: ignore

    if reasoned_bundle:
        delta_draft = reasoned_bundle.get("agi_draft", "")
    else:
        delta_draft = ""

    # Step 2: Extract Omega content (from 555)
    omega_verdict = empathy_bundle_555["empathy_verdict"]
    omega_flags = empathy_bundle_555["soft_flags"]

    # Step 3: Determine context gate
    context_gate = determine_context_gate(empathy_bundle_555)

    # Step 4: Compute MoE weights
    moe_weights = compute_moe_weights(context_gate)

    # Step 5-6: Synthesize dual-process
    synthesized_draft, conflict_resolution = synthesize_dual_process(
        delta_draft, omega_verdict, moe_weights, omega_flags
    )

    # Step 7: Measure F5 Humility
    humility_metrics = measure_humility(synthesized_draft)

    # Step 8: Determine synthesis verdict
    if humility_metrics["omega_0"] < 0.03:
        synthesis_verdict: SynthesisVerdict = "VOID"  # Hubris
    elif humility_metrics["omega_0"] > 0.05:
        synthesis_verdict = "SABAR"  # Hedge-hell
    else:
        synthesis_verdict = "PASS"

    # Step 9: Package bundle
    bridge_bundle: BridgeBundle666 = {
        "empathy_bundle_555": empathy_bundle_555,  # ← IMMUTABLE (F8)
        "synthesis_draft": synthesized_draft,
        "delta_provenance": {
            "source_stage": "333_REASON",
            "draft_type": "agi_logical"
        },
        "omega_provenance": {
            "source_stage": "555_EMPATHIZE",
            "verdict": omega_verdict
        },
        "moe_weights": moe_weights,
        "humility_metrics": humility_metrics,
        "conflict_resolution": conflict_resolution,
        "synthesis_verdict": synthesis_verdict,
        "handoff": {
            "from_stage": "666_BRIDGE",
            "to_stage": "777_EUREKA",
            "ready_for_insight": synthesis_verdict == "PASS",
            "context_gate": context_gate
        }
    }

    # Step 10: Verdict logic (raise if failure)
    if synthesis_verdict == "VOID":
        raise ValueError(
            f"VOID: F5 Humility violation - Hubris detected "
            f"(Ω₀={humility_metrics['omega_0']:.2f} < 0.03) - "
            f"Overconfident assertions without epistemic limits"
        )

    if synthesis_verdict == "SABAR":
        raise ValueError(
            f"SABAR: F5 Humility violation - Excessive hedging "
            f"(Ω₀={humility_metrics['omega_0']:.2f} > 0.05) - "
            f"Requires more reasoning or truth grounding"
        )

    return bridge_bundle


__all__ = [
    "bridge_stage",
    "BridgeBundle666",
    "MoEWeights",
    "HumilityMetrics",
    "ConflictResolution",
    "SynthesisVerdict",
    "ConflictType",
    "ContextGate",
    "measure_humility",
    "determine_context_gate",
    "compute_moe_weights",
    "synthesize_dual_process",
]

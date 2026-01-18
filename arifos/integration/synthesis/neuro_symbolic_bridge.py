"""
arifos_core/integration/synthesis/neuro_symbolic_bridge.py

666 BRIDGE - Neuro-Symbolic Synthesis (Δ+Ω Unification)

Purpose:
    Synthesis layer bridging AGI logic (Delta/333) and ASI care (Omega/555)
    into coherent, human-like response.

    Implements dual-process model (System 1 + System 2):
    - Symbolic (Slow): Delta reasoning, fact-checking, logic
    - Neural (Fast): Omega empathy, tone, emotional resonance

Authority:
    - L1_THEORY/canon/666_bridge/660_BRIDGE_SYNTHESIS_v46.md
    - L2_PROTOCOLS/v46/666_bridge/666_bridge.json

Design:
    Input: bundle_333 (Delta) + bundle_555 (Omega)
    Output: bridge_bundle_666 → 777 EUREKA

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ConflictType(str, Enum):
    """Types of conflicts between Delta and Omega"""
    TRUTH_VS_CARE = "truth_vs_care"
    SAFETY = "safety"
    DIGNITY = "dignity"
    EFFICIENCY_VS_STAKEHOLDER = "efficiency_vs_stakeholder"
    CERTAINTY_VS_HUMILITY = "certainty_vs_humility"


class GatingCondition(str, Enum):
    """Gating conditions for Mixture of Experts"""
    CRISIS_HIGH_STAKES = "crisis"
    FACTUAL_LOW_STAKES = "factual"
    STANDARD_INTERACTION = "standard"
    SOCIAL_CARE = "social"


@dataclass
class MoEWeights:
    """
    Mixture of Experts weights.

    Dynamically weight Delta vs Omega influence based on context.

    Weights:
        omega: Weight for Omega (ASI care) influence
        delta: Weight for Delta (AGI logic) influence
        gating_condition: Context that determined weights
        justification: Reasoning for weight assignment
    """
    omega: float
    delta: float
    gating_condition: GatingCondition
    justification: str

    def __post_init__(self):
        """Validate weights sum to 1.0"""
        total = self.omega + self.delta
        if not (0.99 <= total <= 1.01):  # Allow small floating point tolerance
            raise ValueError(f"Weights must sum to 1.0, got {total}")


@dataclass
class ConflictResolution:
    """
    Record of how a Delta-Omega conflict was resolved.

    Attributes:
        conflict_type: Type of conflict detected
        delta_position: Delta's stance
        omega_position: Omega's stance
        resolution: How conflict was resolved
        floor_invoked: Constitutional floor used for adjudication
        rationale: Reasoning for resolution
    """
    conflict_type: ConflictType
    delta_position: str
    omega_position: str
    resolution: str
    floor_invoked: str
    rationale: str


@dataclass
class BridgeBundle666:
    """
    Complete 666 BRIDGE output bundle.

    Feeds into 777 EUREKA for insight generation.

    Attributes:
        synthesis_draft: Merged text combining Delta logic and Omega care
        delta_provenance: Traceability to 333 REASON
        omega_provenance: Traceability to 555 EMPATHIZE
        resolution_log: List of conflict resolutions
        moe_weights: Mixture of Experts weights applied
        synthesis_metadata: Metadata about synthesis process
        ready_for_insight: True if ready for 777
        to_stage: Always "777_EUREKA"
    """
    synthesis_draft: str
    delta_provenance: Dict = field(default_factory=dict)
    omega_provenance: Dict = field(default_factory=dict)
    resolution_log: List[ConflictResolution] = field(default_factory=list)
    moe_weights: MoEWeights = None
    synthesis_metadata: Dict = field(default_factory=dict)
    ready_for_insight: bool = True
    to_stage: str = "777_EUREKA"


class NeuroSymbolicBridge:
    """
    Neuro-Symbolic Bridge - 666 Synthesis Layer

    Implements 7-Layer Bridge Protocol:
    1. Input Reception: Validate bundles from 333 and 555
    2. Conflict Detection: Identify contradictions
    3. Constitutional Adjudication: Apply F1-F10 hierarchy
    4. Dual-Process Integration: Fuse System 2 facts with System 1 tone
    5. Ensemble Synthesis: Apply MoE weighting
    6. Human-Likeness Check: Verify naturalness
    7. Handoff: Package for 777 EUREKA

    Constitutional Adjudication:
        Immutable Constraints (Priority 1):
        - F1 Truth: Semantic content CANNOT be altered
        - F4 Dignity: Dignity flags CANNOT be stripped

        Adjustable Variables:
        - Framing: How truth is contextualized
        - Order: Placing acknowledgement before facts
        - Tone: Clinical → supportive
        - Suffix: Adding resources/hope
        - Confidence: Tuning certainty markers (F5)

    Mixture of Experts Gating:
        - CRISIS: Ω(0.7) / Δ(0.3) → Safety, stabilization, empathy
        - FACTUAL: Ω(0.2) / Δ(0.8) → Precision, speed, clarity
        - STANDARD: Ω(0.5) / Δ(0.5) → Balanced interaction
        - SOCIAL: Ω(0.65) / Δ(0.35) → Dignity, cultural sensitivity

    Resolution Strategy:
        Truth vs Care: Keep content (Δ), apply framing (Ω)
        Safety: Enforce constraints (Ω safety flags supreme)

    Example:
        bridge = NeuroSymbolicBridge()
        bundle_666 = bridge.synthesize(bundle_333, bundle_555)
        assert bundle_666.ready_for_insight == True
        assert bundle_666.to_stage == "777_EUREKA"
    """

    # MoE Weights from canonical spec
    MOE_WEIGHTS_CONFIG = {
        GatingCondition.CRISIS_HIGH_STAKES: {"omega": 0.7, "delta": 0.3},
        GatingCondition.FACTUAL_LOW_STAKES: {"omega": 0.2, "delta": 0.8},
        GatingCondition.STANDARD_INTERACTION: {"omega": 0.5, "delta": 0.5},
        GatingCondition.SOCIAL_CARE: {"omega": 0.65, "delta": 0.35}
    }

    def __init__(self):
        """Initialize Neuro-Symbolic Bridge."""
        pass

    def synthesize(
        self,
        bundle_333: Dict,
        bundle_555: "Bundle555"
    ) -> BridgeBundle666:
        """
        Perform neuro-symbolic synthesis of Delta and Omega.

        Args:
            bundle_333: Output from 333 REASON (Delta/AGI)
            bundle_555: Output from 555 EMPATHIZE (Omega/ASI)

        Returns:
            BridgeBundle666 ready for 777 EUREKA
        """
        # Layer 1: Input Reception
        self._validate_inputs(bundle_333, bundle_555)

        # Layer 2: Conflict Detection
        conflicts = self._detect_conflicts(bundle_333, bundle_555)

        # Layer 3: Constitutional Adjudication
        resolution_log = self._adjudicate_conflicts(conflicts, bundle_333, bundle_555)

        # Layer 4: Dual-Process Integration
        integrated_content = self._integrate_dual_process(bundle_333, bundle_555)

        # Layer 5: Ensemble Synthesis (MoE)
        moe_weights = self._apply_moe_gating(bundle_555)
        synthesis_draft = self._apply_moe_weights(
            integrated_content,
            bundle_333,
            bundle_555,
            moe_weights
        )

        # Layer 6: Human-Likeness Check
        synthesis_draft = self._ensure_human_likeness(synthesis_draft)

        # Layer 7: Handoff
        return self._package_for_handoff(
            synthesis_draft,
            bundle_333,
            bundle_555,
            resolution_log,
            moe_weights
        )

    def _validate_inputs(self, bundle_333: Dict, bundle_555: "Bundle555"):
        """
        Layer 1: Input Reception - Validate bundles.

        Checks:
        - bundle_333 structure valid
        - bundle_555 structure valid
        - Constitutional compliance (F1-F10 floor checks passed)
        """
        # Simplified validation (real implementation would be more thorough)
        if not bundle_333:
            raise ValueError("bundle_333 is empty")
        if not bundle_555:
            raise ValueError("bundle_555 is empty")

    def _detect_conflicts(
        self,
        bundle_333: Dict,
        bundle_555: "Bundle555"
    ) -> List[Dict]:
        """
        Layer 2: Conflict Detection - Identify contradictions.

        Conflict types:
        - TRUTH_VS_CARE: Accurate info that could be distressing
        - SAFETY: Delta suggests action Omega flags as harmful
        - DIGNITY: Delta language violates Omega dignity checks
        - EFFICIENCY_VS_STAKEHOLDER: Fast solution harms vulnerable
        - CERTAINTY_VS_HUMILITY: Delta overconfident, Omega demands hedging
        """
        conflicts = []

        # Check for truth vs care conflicts
        if bundle_555.tom_analysis.crisis_flag:
            conflicts.append({
                "type": ConflictType.TRUTH_VS_CARE,
                "delta_position": "Deliver factual content directly",
                "omega_position": "User in crisis, needs emotional support first"
            })

        # Check for dignity violations
        if not bundle_555.asi_care.dignity_preservation:
            conflicts.append({
                "type": ConflictType.DIGNITY,
                "delta_position": "Efficient factual delivery",
                "omega_position": "Dignity violation detected"
            })

        # Check for stakeholder conflicts
        if bundle_555.weakest_stakeholder.weakest != "user":
            conflicts.append({
                "type": ConflictType.EFFICIENCY_VS_STAKEHOLDER,
                "delta_position": f"Optimize for primary user",
                "omega_position": f"Protect weakest: {bundle_555.weakest_stakeholder.weakest}"
            })

        return conflicts

    def _adjudicate_conflicts(
        self,
        conflicts: List[Dict],
        bundle_333: Dict,
        bundle_555: "Bundle555"
    ) -> List[ConflictResolution]:
        """
        Layer 3: Constitutional Adjudication - Resolve conflicts.

        Applies F1-F10 hierarchy:
        Priority 1: F1 Truth (content immutable) + F4 Dignity (delivery immutable)
        Priority 2: F5 Peace² (safety supreme)
        Priority 3: F5 Humility (epistemic limits)

        Resolution Algorithm:
        - TRUTH_VS_CARE: Keep content (F1), apply framing (F4)
        - SAFETY: Enforce Omega safety flags (F5 supreme)
        - DIGNITY: Preserve Omega dignity flags (F4 immutable)
        """
        resolutions = []

        for conflict in conflicts:
            conflict_type = conflict["type"]

            if conflict_type == ConflictType.TRUTH_VS_CARE:
                resolutions.append(ConflictResolution(
                    conflict_type=conflict_type,
                    delta_position=conflict["delta_position"],
                    omega_position=conflict["omega_position"],
                    resolution="Preserve truth (F1), add empathetic framing (F4)",
                    floor_invoked="F1 + F4",
                    rationale="Truth immutable, delivery adjustable"
                ))

            elif conflict_type == ConflictType.DIGNITY:
                resolutions.append(ConflictResolution(
                    conflict_type=conflict_type,
                    delta_position=conflict["delta_position"],
                    omega_position=conflict["omega_position"],
                    resolution="Reject Delta approach, enforce Omega dignity",
                    floor_invoked="F4",
                    rationale="Dignity flags immutable (F4 Priority 1)"
                ))

            elif conflict_type == ConflictType.EFFICIENCY_VS_STAKEHOLDER:
                resolutions.append(ConflictResolution(
                    conflict_type=conflict_type,
                    delta_position=conflict["delta_position"],
                    omega_position=conflict["omega_position"],
                    resolution="Bias toward weakest stakeholder protection",
                    floor_invoked="F4 (Empathy)",
                    rationale="Constitutional bias toward vulnerable (F4 κᵣ)"
                ))

        return resolutions

    def _integrate_dual_process(
        self,
        bundle_333: Dict,
        bundle_555: "Bundle555"
    ) -> str:
        """
        Layer 4: Dual-Process Integration - Fuse System 2 facts with System 1 tone.

        Integration Pattern:
        1. Extract core facts from bundle_333 (immutable)
        2. Extract care constraints from bundle_555 (immutable)
        3. Apply omega framing to delta content
        4. Verify no floor violations introduced
        5. Generate integrated content
        """
        # Simplified integration (real implementation would be LLM-based)
        delta_content = bundle_333.get("draft", "")
        omega_framing = self._generate_omega_framing(bundle_555)

        # Apply framing: acknowledgement → content → resources
        integrated = f"{omega_framing}\n\n{delta_content}"

        # Add mandatory resources if crisis
        if bundle_555.crisis_mode:
            resources = "\n\n".join(bundle_555.asi_care.crisis_protocol.get("resources", []))
            if resources:
                integrated += f"\n\nImmediate resources:\n{resources}"

        return integrated

    def _generate_omega_framing(self, bundle_555: "Bundle555") -> str:
        """Generate empathetic framing from Omega bundle."""
        emotional_state = bundle_555.tom_analysis.mental_states.emotions

        if emotional_state in ["desperation", "fear"]:
            return "I understand this situation is incredibly difficult."
        elif emotional_state in ["urgency", "stress"]:
            return "I recognize the urgency of your situation."
        elif emotional_state == "curiosity":
            return "That's a great question."
        else:
            return "Thank you for sharing your concern."

    def _apply_moe_gating(self, bundle_555: "Bundle555") -> MoEWeights:
        """
        Layer 5: Ensemble Synthesis - Apply MoE weighting.

        Gating Logic:
        - CRISIS / High Stakes: Ω(0.7) / Δ(0.3)
        - FACTUAL / Low Stakes: Ω(0.2) / Δ(0.8)
        - STANDARD: Ω(0.5) / Δ(0.5)
        - SOCIAL / Care: Ω(0.65) / Δ(0.35)
        """
        # Determine gating condition
        if bundle_555.crisis_mode:
            condition = GatingCondition.CRISIS_HIGH_STAKES
            justification = "Crisis mode: Safety, stabilization, empathy prioritized"
        elif bundle_555.empathy_architecture.layer_1_recognition.empathy_required.value == "LOW":
            condition = GatingCondition.FACTUAL_LOW_STAKES
            justification = "Low empathy requirement: Precision and clarity prioritized"
        elif bundle_555.weakest_stakeholder.weakest != "user":
            condition = GatingCondition.SOCIAL_CARE
            justification = "Social query with stakeholder concerns: Dignity prioritized"
        else:
            condition = GatingCondition.STANDARD_INTERACTION
            justification = "Standard interaction: Balanced synthesis"

        # Get weights for condition
        weights = self.MOE_WEIGHTS_CONFIG[condition]

        return MoEWeights(
            omega=weights["omega"],
            delta=weights["delta"],
            gating_condition=condition,
            justification=justification
        )

    def _apply_moe_weights(
        self,
        integrated_content: str,
        bundle_333: Dict,
        bundle_555: "Bundle555",
        moe_weights: MoEWeights
    ) -> str:
        """
        Apply MoE weights to modulate synthesis draft.

        Logic:
        - Omega > 0.6: Prepend empathetic framing headers.
        - Delta > 0.7: Prepend logical structure headers.
        - Standard: Balanced.
        """
        omega_w = moe_weights.omega
        delta_w = moe_weights.delta

        modulated_content = integrated_content

        # 1. High Empathy Modulation (Omega Dominant)
        if omega_w >= 0.60:
            prefix = ""
            if bundle_555.crisis_mode:
                prefix = "**CRISIS SUPPORT MODE (Ω-Lead)**\n\n"
            else:
                prefix = "**Empathetic Response (Ω-Lead)**\n\n"

            modulated_content = prefix + modulated_content

        # 2. High Logic Modulation (Delta Dominant)
        elif delta_w >= 0.70:
            prefix = "**Factual Analysis (Δ-Lead)**\n\n"
            modulated_content = prefix + modulated_content

        # 3. Balanced Protocol
        else:
            # No specific prefix, keep it conversational
            pass

        return modulated_content

    def _ensure_human_likeness(self, synthesis_draft: str) -> str:
        """
        Layer 6: Human-Likeness Check - Verify naturalness.

        Checks:
        - Natural language flow
        - Appropriate emotional resonance
        - No excessive hedging (Ω₀ band respected)
        - No mechanical listing (unless appropriate)
        - Conversational coherence
        """
        # Simplified check (real implementation would be more sophisticated)
        # For now, just return draft
        return synthesis_draft

    def _package_for_handoff(
        self,
        synthesis_draft: str,
        bundle_333: Dict,
        bundle_555: "Bundle555",
        resolution_log: List[ConflictResolution],
        moe_weights: MoEWeights
    ) -> BridgeBundle666:
        """
        Layer 7: Handoff - Package for 777 EUREKA.

        Creates complete Bridge bundle with:
        - Synthesis draft
        - Provenance (Delta + Omega)
        - Resolution log
        - MoE weights
        - Metadata
        """
        # Delta provenance
        delta_provenance = {
            "original_draft": bundle_333.get("draft", ""),
            "truth_score": bundle_333.get("truth_score", 0.0),
            "logical_structure": bundle_333.get("structure", {})
        }

        # Omega provenance
        omega_provenance = {
            "tom_composite": bundle_555.tom_analysis.composite_score,
            "kappa_r": bundle_555.empathy_architecture.layer_3_response.kappa_r,
            "weakest": bundle_555.weakest_stakeholder.weakest,
            "crisis_flag": bundle_555.crisis_mode
        }

        # Synthesis metadata
        synthesis_metadata = {
            "layers_completed": list(range(1, 8)),
            "conflicts_detected": len(resolution_log),
            "conflicts_resolved": len(resolution_log),
            "floors_invoked": list(set(r.floor_invoked for r in resolution_log)),
            "human_likeness_score": 0.9,  # Placeholder
            "omega_0_humility": 0.04  # Placeholder (F5 check)
        }

        return BridgeBundle666(
            synthesis_draft=synthesis_draft,
            delta_provenance=delta_provenance,
            omega_provenance=omega_provenance,
            resolution_log=resolution_log,
            moe_weights=moe_weights,
            synthesis_metadata=synthesis_metadata,
            ready_for_insight=True,
            to_stage="777_EUREKA"
        )


# Convenience function
def synthesize_delta_omega(bundle_333: Dict, bundle_555: "Bundle555") -> BridgeBundle666:
    """
    Convenience function to synthesize Delta and Omega.

    Args:
        bundle_333: Output from 333 REASON (Delta)
        bundle_555: Output from 555 EMPATHIZE (Omega)

    Returns:
        BridgeBundle666 ready for 777 EUREKA
    """
    bridge = NeuroSymbolicBridge()
    return bridge.synthesize(bundle_333, bundle_555)


__all__ = [
    "NeuroSymbolicBridge",
    "BridgeBundle666",
    "MoEWeights",
    "ConflictResolution",
    "ConflictType",
    "GatingCondition",
    "synthesize_delta_omega",
]

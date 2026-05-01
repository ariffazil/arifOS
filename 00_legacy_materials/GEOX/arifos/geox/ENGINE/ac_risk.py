"""
AC_Risk Calculator — Theory of Anomalous Contrast Implementation
DITEMPA BUKAN DIBERI

Computes Anomalous Contrast Risk for all vision operations.
Formula: AC_Risk = U_phys × D_transform × B_cog
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(Enum):
    """GEOX verdicts based on AC_Risk."""
    SEAL = "SEAL"           # AC_Risk < 0.25
    QUALIFY = "QUALIFY"     # 0.25 ≤ AC_Risk < 0.50
    HOLD = "HOLD"           # 0.50 ≤ AC_Risk < 0.75
    VOID = "VOID"           # AC_Risk ≥ 0.75


@dataclass
class Transform:
    """A display or processing transform with invertibility score."""
    name: str
    invertibility: float  # 0.0-1.0, 1.0 = perfectly invertible
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    
    def distortion_score(self) -> float:
        """Return distortion: 1 - invertibility."""
        return 1.0 - self.invertibility


class TransformRegistry:
    """Registry of known transforms with ToAC risk weights."""
    
    _transforms: dict[str, Transform] = {
        # Linear operations (low risk)
        "linear_scaling": Transform(
            name="linear_scaling",
            invertibility=1.0,
            description="Linear amplitude normalization"
        ),
        "affine_warp": Transform(
            name="affine_warp",
            invertibility=0.95,
            description="Affine geometric transformation"
        ),
        
        # Display operations (medium risk)
        "colormap_mapping": Transform(
            name="colormap_mapping",
            invertibility=0.7,
            description="Mapping amplitude to color (information loss)"
        ),
        "perspective_warp": Transform(
            name="perspective_warp",
            invertibility=0.8,
            description="Perspective georeferencing"
        ),
        
        # Non-linear operations (high risk)
        "agc_rms": Transform(
            name="agc_rms",
            invertibility=0.4,
            description="Automatic Gain Control (RMS window)"
        ),
        "clahe": Transform(
            name="clahe",
            invertibility=0.2,
            description="Contrast Limited Adaptive Histogram Equalization"
        ),
        "vertical_exaggeration_2x": Transform(
            name="vertical_exaggeration_2x",
            invertibility=0.3,
            description="Vertical exaggeration > 2x"
        ),
        
        # Digitization operations (high risk)
        "ocr_extraction": Transform(
            name="ocr_extraction",
            invertibility=0.5,
            description="Optical Character Recognition"
        ),
        "curve_tracing": Transform(
            name="curve_tracing",
            invertibility=0.6,
            description="Manual or AI curve digitization"
        ),
        "color_decomposition": Transform(
            name="color_decomposition",
            invertibility=0.5,
            description="Separating overlapping curves by color"
        ),
        
        # Vision model operations (very high risk)
        "vlm_inference": Transform(
            name="vlm_inference",
            invertibility=0.3,
            description="Vision Language Model pattern recognition"
        ),
        "cnn_segmentation": Transform(
            name="cnn_segmentation",
            invertibility=0.4,
            description="CNN-based image segmentation"
        ),
    }
    
    @classmethod
    def get(cls, name: str) -> Transform | None:
        """Get transform by name."""
        return cls._transforms.get(name)
    
    @classmethod
    def register(cls, transform: Transform) -> None:
        """Register a new transform."""
        cls._transforms[transform.name] = transform
    
    @classmethod
    def calculate_d_transform(cls, transform_names: list[str]) -> float:
        """
        Calculate aggregate D_transform from transform stack.
        
        D_transform = average distortion across all transforms
        """
        if not transform_names:
            return 0.0
        
        total_distortion = 0.0
        for name in transform_names:
            t = cls.get(name)
            if t:
                total_distortion += t.distortion_score()
            else:
                # Unknown transform = maximum risk
                total_distortion += 1.0
        
        return min(1.0, total_distortion / len(transform_names))


@dataclass
class ACRiskResult:
    """Result of AC_Risk calculation."""
    ac_risk: float
    u_phys: float
    d_transform: float
    b_cog: float
    verdict: Verdict
    explanation: str
    components: dict[str, float]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "ac_risk": round(self.ac_risk, 3),
            "u_phys": round(self.u_phys, 3),
            "d_transform": round(self.d_transform, 3),
            "b_cog": round(self.b_cog, 3),
            "verdict": self.verdict.value,
            "explanation": self.explanation,
            "components": self.components,
        }


class ACRiskCalculator:
    """
    Calculates Anomalous Contrast Risk per ToAC.
    
    AC_Risk = U_phys × D_transform × B_cog
    
    Where:
    - U_phys: Physical ambiguity (non-uniqueness)
    - D_transform: Display distortion (non-invertibility)
    - B_cog: Cognitive bias (overconfidence)
    """
    
    # Bond et al. (2007) baseline: 79% expert failure rate
    BOND_BASELINE = 0.79
    
    # Cognitive bias modifiers
    BIAS_MODIFIERS = {
        "unaided_expert": 0.79,
        "multi_interpreter": 0.40,
        "physics_validated": 0.20,
        "ai_vision_only": 0.70,  # AI has similar bias patterns to experts
        "ai_with_physics": 0.35,
    }
    
    @classmethod
    def calculate(
        cls,
        u_phys: float,
        transform_stack: list[str],
        bias_scenario: str = "ai_vision_only",
        custom_b_cog: float | None = None,
    ) -> ACRiskResult:
        """
        Calculate AC_Risk from components.
        
        Args:
            u_phys: Physical ambiguity [0.0, 1.0]
            transform_stack: List of transform names
            bias_scenario: Key from BIAS_MODIFIERS
            custom_b_cog: Override bias value
        
        Returns:
            ACRiskResult with verdict and explanation
        """
        # Clamp inputs
        u_phys = max(0.0, min(1.0, u_phys))
        
        # Calculate D_transform from registry
        d_transform = TransformRegistry.calculate_d_transform(transform_stack)
        
        # Get B_cog
        if custom_b_cog is not None:
            b_cog = custom_b_cog
        else:
            b_cog = cls.BIAS_MODIFIERS.get(bias_scenario, cls.BOND_BASELINE)
        
        # Calculate AC_Risk
        ac_risk = u_phys * d_transform * b_cog
        
        # Determine verdict
        verdict = cls._risk_to_verdict(ac_risk)
        
        # Generate explanation
        explanation = cls._generate_explanation(
            ac_risk, u_phys, d_transform, b_cog, verdict
        )
        
        return ACRiskResult(
            ac_risk=ac_risk,
            u_phys=u_phys,
            d_transform=d_transform,
            b_cog=b_cog,
            verdict=verdict,
            explanation=explanation,
            components={
                "physical_ambiguity": u_phys,
                "display_distortion": d_transform,
                "cognitive_bias": b_cog,
            },
        )
    
    @classmethod
    def _risk_to_verdict(cls, ac_risk: float) -> Verdict:
        """Convert AC_Risk to verdict."""
        if ac_risk < 0.25:
            return Verdict.SEAL
        elif ac_risk < 0.50:
            return Verdict.QUALIFY
        elif ac_risk < 0.75:
            return Verdict.HOLD
        else:
            return Verdict.VOID
    
    @classmethod
    def _generate_explanation(
        cls,
        ac_risk: float,
        u_phys: float,
        d_transform: float,
        b_cog: float,
        verdict: Verdict,
    ) -> str:
        """Generate human-readable explanation."""
        explanations = []
        
        # Overall assessment
        if verdict == Verdict.SEAL:
            explanations.append(
                f"AC_Risk={ac_risk:.2f}: Low risk. Physical grounding strong, "
                "transforms invertible, bias controlled."
            )
        elif verdict == Verdict.QUALIFY:
            explanations.append(
                f"AC_Risk={ac_risk:.2f}: Moderate risk. Proceed with caveats. "
                "Cross-validate with independent sources."
            )
        elif verdict == Verdict.HOLD:
            explanations.append(
                f"AC_Risk={ac_risk:.2f}: High risk. Human review required before "
                "operational decisions. "
            )
        else:
            explanations.append(
                f"AC_Risk={ac_risk:.2f}: Critical risk. Interpretation unsafe. "
                "Acquire better data or ground-truth validation."
            )
        
        # Component breakdown
        if u_phys > 0.7:
            explanations.append(
                f"Physical ambiguity high ({u_phys:.2f}): "
                "Multiple geological models fit data."
            )
        
        if d_transform > 0.5:
            explanations.append(
                f"Display distortion high ({d_transform:.2f}): "
                "Non-invertible transforms applied. Risk of artifacts."
            )
        
        if b_cog > 0.6:
            explanations.append(
                f"Cognitive bias elevated ({b_cog:.2f}): "
                "Reference: Bond et al. (2007) 79% expert failure rate."
            )
        
        return " ".join(explanations)
    
    @classmethod
    def for_georeferencing(
        cls,
        bound_divergence: float,
        scale_consistency: float,
        ocr_confidence: float,
        transform_stack: list[str],
    ) -> ACRiskResult:
        """
        Calculate AC_Risk for georeferencing operation.
        
        Args:
            bound_divergence: Difference between claimed and detected bounds
            scale_consistency: Consistency between scale bar and bounds
            ocr_confidence: OCR confidence for grid labels
            transform_stack: Georeferencing transforms applied
        """
        # U_phys: combines bound accuracy and scale consistency
        u_phys = (bound_divergence + (1 - scale_consistency)) / 2
        
        # Add uncertainty from OCR
        u_phys = max(u_phys, 1 - ocr_confidence)
        
        return cls.calculate(
            u_phys=u_phys,
            transform_stack=transform_stack,
            bias_scenario="unaided_expert",
        )
    
    @classmethod
    def for_analog_digitization(
        cls,
        ocr_confidence: float,
        scale_consistency: float,
        physics_plausibility: float,
        transform_stack: list[str],
    ) -> ACRiskResult:
        """
        Calculate AC_Risk for analog digitization.
        
        Args:
            ocr_confidence: OCR confidence for labels
            scale_consistency: Consistency between scale markers
            physics_plausibility: RATLAS consistency score
            transform_stack: Digitization transforms
        """
        # U_phys: combines OCR uncertainty and physics plausibility
        u_phys = max(
            1 - ocr_confidence,
            1 - scale_consistency,
            1 - physics_plausibility,
        )
        
        return cls.calculate(
            u_phys=u_phys,
            transform_stack=transform_stack,
            bias_scenario="ai_vision_only",
        )
    
    @classmethod
    def for_seismic_vision(
        cls,
        view_consistency: float,
        physics_agreement: float,
        has_segy: bool,
        transform_stack: list[str],
    ) -> ACRiskResult:
        """
        Calculate AC_Risk for seismic VLM interpretation.
        
        Args:
            view_consistency: Cross-view feature consistency
            physics_agreement: VLM vs computed attributes agreement
            has_segy: Whether SEG-Y data is available
            transform_stack: Display transforms applied
        """
        # U_phys: lower if we have SEG-Y, higher if image-only
        if has_segy:
            u_phys = (1 - view_consistency) * 0.3 + (1 - physics_agreement) * 0.3
        else:
            u_phys = max(1 - view_consistency, 1 - physics_agreement, 0.6)
        
        bias = "ai_with_physics" if has_segy else "ai_vision_only"
        
        return cls.calculate(
            u_phys=u_phys,
            transform_stack=transform_stack,
            bias_scenario=bias,
        )


# Quick self-test
if __name__ == "__main__":
    # Test 1: Low risk (SEGY data, minimal transforms)
    result1 = ACRiskCalculator.for_seismic_vision(
        view_consistency=0.9,
        physics_agreement=0.85,
        has_segy=True,
        transform_stack=["linear_scaling"],
    )
    print("Test 1 (SEGY, minimal transforms):")
    print(f"  AC_Risk: {result1.ac_risk:.3f}")
    print(f"  Verdict: {result1.verdict.value}")
    print()
    
    # Test 2: High risk (image only, aggressive transforms)
    result2 = ACRiskCalculator.for_seismic_vision(
        view_consistency=0.5,
        physics_agreement=0.4,
        has_segy=False,
        transform_stack=["colormap_mapping", "clahe", "agc_rms", "vlm_inference"],
    )
    print("Test 2 (Image only, CLAHE+AGC+VLM):")
    print(f"  AC_Risk: {result2.ac_risk:.3f}")
    print(f"  Verdict: {result2.verdict.value}")
    print(f"  Explanation: {result2.explanation[:100]}...")
    print()
    
    # Test 3: Georeferencing with poor OCR
    result3 = ACRiskCalculator.for_georeferencing(
        bound_divergence=0.3,
        scale_consistency=0.7,
        ocr_confidence=0.5,
        transform_stack=["perspective_warp", "ocr_extraction"],
    )
    print("Test 3 (Georeferencing, poor OCR):")
    print(f"  AC_Risk: {result3.ac_risk:.3f}")
    print(f"  Verdict: {result3.verdict.value}")

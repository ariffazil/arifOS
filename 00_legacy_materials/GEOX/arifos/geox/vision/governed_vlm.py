"""
GovernedSeismicVLM — ToAC-Compliant Vision Language Model Adapter
DITEMPA BUKAN DIBERI

Wraps real VLM calls (GPT-4V, Claude 3, etc.) with Theory of Anomalous Contrast
governance: multi-view consistency, physics anchoring, AC_Risk calculation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from ..ENGINE.ac_risk import ACRiskCalculator, ACRiskResult, Verdict
from ..seismic_feature_extract import extract_features


class VLMBackend(Protocol):
    """Protocol for VLM backends (GPT-4V, Claude, etc.)."""

    async def infer(
        self,
        image: Image.Image,
        prompt: str,
    ) -> dict[str, Any]:
        """Run VLM inference on image."""
        ...


@dataclass
class SeismicHypothesis:
    """A single interpretation hypothesis from VLM."""

    feature_type: str  # "horizon", "fault", "channel", "closure"
    description: str
    confidence: float
    pixel_coordinates: list[tuple[int, int]] | None = None
    geological_model: str = ""
    alternative_explanations: list[str] = field(default_factory=list)


@dataclass
class VisionInterpretationResult:
    """Result from governed seismic VLM interpretation."""

    hypotheses: list[SeismicHypothesis]
    contrast_views: list[dict[str, Any]]
    view_consistency_score: float
    computed_attributes: dict[str, Any] | None
    ac_risk_result: ACRiskResult
    verdict: Verdict
    perception_bridge_warning: str
    transform_stack: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypotheses": [
                {
                    "feature_type": h.feature_type,
                    "description": h.description,
                    "confidence": h.confidence,
                    "geological_model": h.geological_model,
                }
                for h in self.hypotheses
            ],
            "view_consistency_score": round(self.view_consistency_score, 3),
            "ac_risk": self.ac_risk_result.to_dict(),
            "verdict": self.verdict.value,
            "perception_bridge_warning": self.perception_bridge_warning,
            "transform_stack": self.transform_stack,
        }


class ContrastViewGenerator:
    """
    Generate multiple contrast-variant views per ToAC Contrast Canon.

    Rule: Never trust single-view interpretation.
    """

    def generate_views(self, image: Image.Image) -> list[dict[str, Any]]:
        """
        Generate contrast variants for multi-view consistency checking.

        Returns list of views with transform metadata.
        """
        views = []

        # View 1: Standard (baseline)
        views.append(
            {
                "name": "standard",
                "image": image,
                "transforms": ["colormap_mapping"],  # Assume some colormap was applied
                "description": "Original display",
            }
        )

        # View 2: High Saliency (histogram equalization)
        equalized = ImageOps.equalize(image.convert("L"))
        views.append(
            {
                "name": "high_saliency",
                "image": equalized,
                "transforms": ["colormap_mapping", "histogram_equalization"],
                "description": "Enhanced local contrast",
            }
        )

        # View 3: Edge Enhanced
        edges = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        views.append(
            {
                "name": "edge_enhanced",
                "image": edges,
                "transforms": ["colormap_mapping", "edge_enhancement"],
                "description": "Structural edges emphasized",
            }
        )

        # View 4: Inverted (polarity reversal test)
        inverted = ImageOps.invert(image.convert("L"))
        views.append(
            {
                "name": "inverted",
                "image": inverted,
                "transforms": ["colormap_mapping", "polarity_inversion"],
                "description": "Inverted polarity",
            }
        )

        # View 5: Gamma Adjusted (simulate different gain)
        enhancer = ImageEnhance.Contrast(image)
        high_contrast = enhancer.enhance(1.5)
        views.append(
            {
                "name": "high_contrast",
                "image": high_contrast,
                "transforms": ["colormap_mapping", "gamma_adjustment"],
                "description": "Increased contrast",
            }
        )

        return views


class MultiViewConsistencyChecker:
    """
    Check consistency of features across contrast views.

    Features appearing only under aggressive enhancement = DISPLAY ARTIFACTS.
    """

    def check_consistency(
        self,
        view_hypotheses: list[list[SeismicHypothesis]],
    ) -> float:
        """
        Calculate cross-view consistency score.

        Returns 0.0-1.0, where:
        - 1.0 = Perfect consistency (features appear in all views)
        - 0.0 = No consistency (features appear randomly)
        """
        if not view_hypotheses or len(view_hypotheses) < 2:
            return 0.0

        # Count feature occurrences across views
        feature_votes: dict[str, int] = {}

        for view_idx, hypotheses in enumerate(view_hypotheses):
            for h in hypotheses:
                # Create feature signature
                sig = f"{h.feature_type}:{h.description[:50]}"
                feature_votes[sig] = feature_votes.get(sig, 0) + 1

        if not feature_votes:
            return 0.0

        # Features appearing in most views = likely real
        # Features appearing in few views = likely artifacts
        n_views = len(view_hypotheses)
        consistency_scores = []

        for sig, votes in feature_votes.items():
            # Normalize by view count
            score = votes / n_views
            consistency_scores.append(score)

        # Overall consistency is average of individual scores
        return sum(consistency_scores) / len(consistency_scores)


class GovernedSeismicVLM:
    """
    ToAC-compliant VLM for seismic interpretation.

    NOT a raw VLM wrapper — a governed inference pipeline with:
    1. Multi-contrast view generation
    2. Cross-view consistency checking
    3. Physics anchoring
    4. AC_Risk calculation
    5. Verdict determination
    """

    def __init__(
        self,
        vlm_backend: VLMBackend | None = None,
        enable_physics_anchoring: bool = True,
    ):
        self.vlm_backend = vlm_backend
        self.view_generator = ContrastViewGenerator()
        self.consistency_checker = MultiViewConsistencyChecker()
        self.enable_physics_anchoring = enable_physics_anchoring

    async def interpret(
        self,
        image: Image.Image | np.ndarray | str,
        interpretation_goal: str,
        has_segy: bool = False,
        canonical_array: np.ndarray | None = None,
    ) -> VisionInterpretationResult:
        """
        Run governed seismic interpretation.

        Args:
            image: Input seismic image
            interpretation_goal: What to interpret (faults, horizons, etc.)
            has_segy: Whether SEG-Y data is available
            canonical_array: Optional numpy array for attribute computation

        Returns:
            VisionInterpretationResult with AC_Risk and verdict
        """
        # Stage 0: Load and canonicalize image
        pil_image = self._load_image(image)

        # Stage 1: Generate multi-contrast views (Contrast Canon)
        contrast_views = self.view_generator.generate_views(pil_image)

        # Stage 2: VLM inference on all views
        view_hypotheses: list[list[SeismicHypothesis]] = []

        if self.vlm_backend:
            for view in contrast_views:
                prompt = self._build_prompt(interpretation_goal, view["name"])
                vlm_output = await self.vlm_backend.infer(view["image"], prompt)
                hypotheses = self._parse_vlm_output(vlm_output)
                view_hypotheses.append(hypotheses)
        else:
            # No VLM backend: use mock for demonstration
            view_hypotheses = self._mock_hypotheses(len(contrast_views))

        # Stage 3: Cross-view consistency checking
        consistency_score = self.consistency_checker.check_consistency(view_hypotheses)

        # Stage 4: Physics anchoring (if data available)
        computed_attrs = None
        physics_agreement = 0.5  # Neutral if no validation

        if canonical_array is not None and self.enable_physics_anchoring:
            computed_attrs = await extract_features(
                canonical_array,
                image_ref="governed_vlm_input",
                is_raster=not has_segy,
            )
            # Compare VLM hypotheses to computed attributes
            physics_agreement = self._validate_vs_physics(view_hypotheses, computed_attrs)

        # Stage 5: AC_Risk calculation
        transform_stack = self._aggregate_transforms(contrast_views)

        ac_risk_result = ACRiskCalculator.for_seismic_vision(
            view_consistency=consistency_score,
            physics_agreement=physics_agreement,
            has_segy=has_segy,
            transform_stack=transform_stack,
        )

        # Stage 6: Build result
        perception_warning = self._generate_warning(
            has_segy, ac_risk_result.verdict, consistency_score
        )

        # Aggregate hypotheses from all views
        all_hypotheses = []
        for hypotheses in view_hypotheses:
            all_hypotheses.extend(hypotheses)

        return VisionInterpretationResult(
            hypotheses=all_hypotheses,
            contrast_views=[
                {"name": v["name"], "transforms": v["transforms"]} for v in contrast_views
            ],
            view_consistency_score=consistency_score,
            computed_attributes=computed_attrs.to_dict() if computed_attrs else None,
            ac_risk_result=ac_risk_result,
            verdict=ac_risk_result.verdict,
            perception_bridge_warning=perception_warning,
            transform_stack=transform_stack,
        )

    def _load_image(self, image: Image.Image | np.ndarray | str) -> Image.Image:
        """Load image from various input types."""
        if isinstance(image, Image.Image):
            return image.convert("RGB")
        elif isinstance(image, np.ndarray):
            return Image.fromarray(image).convert("RGB")
        elif isinstance(image, str):
            return Image.open(image).convert("RGB")
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")

    def _build_prompt(self, goal: str, view_name: str) -> str:
        """Build VLM prompt with ToAC context."""
        return f"""Interpret this seismic section for: {goal}

View type: {view_name}

Identify:
1. Major structural features (faults, horizons, folds)
2. Stratigraphic features (channels, onlaps, truncations)
3. Confidence level for each feature (high/medium/low)
4. Alternative explanations for ambiguous features

Respond in structured format:
- Feature type: [horizon/fault/channel/etc]
- Description: [what you see]
- Confidence: [0.0-1.0]
- Alternative: [what else could this be?]
"""

    def _parse_vlm_output(self, output: dict[str, Any]) -> list[SeismicHypothesis]:
        """Parse VLM output into structured hypotheses."""
        # TODO: Implement real parsing based on VLM response format
        # For now, return mock
        return [
            SeismicHypothesis(
                feature_type="fault",
                description=output.get("description", "Unparsed"),
                confidence=output.get("confidence", 0.5),
                geological_model=output.get("model", "Unknown"),
            )
        ]

    def _mock_hypotheses(self, n_views: int) -> list[list[SeismicHypothesis]]:
        """Generate mock hypotheses for testing."""
        import random

        rng = random.Random(42)

        results = []
        for _ in range(n_views):
            view_hyps = []
            # Some features consistent across views (real)
            view_hyps.append(
                SeismicHypothesis(
                    feature_type="fault",
                    description="Major fault at center",
                    confidence=rng.uniform(0.7, 0.9),
                    geological_model="Extensional",
                )
            )
            # Some features random (artifacts)
            if rng.random() > 0.5:
                view_hyps.append(
                    SeismicHypothesis(
                        feature_type="channel",
                        description="Possible channel",
                        confidence=rng.uniform(0.4, 0.6),
                        geological_model="Depositional",
                    )
                )
            results.append(view_hyps)

        return results

    def _validate_vs_physics(
        self,
        view_hypotheses: list[list[SeismicHypothesis]],
        computed_attrs: Any,
    ) -> float:
        """Compare VLM hypotheses to computed physical attributes."""
        # TODO: Implement real validation
        # For now, return moderate agreement
        return 0.6

    def _aggregate_transforms(self, views: list[dict]) -> list[str]:
        """Aggregate transform stack from all views."""
        all_transforms = set()
        for view in views:
            all_transforms.update(view["transforms"])
        return list(all_transforms)

    def _generate_warning(
        self,
        has_segy: bool,
        verdict: Verdict,
        consistency: float,
    ) -> str:
        """Generate perception bridge warning."""
        warnings = [
            "GEOX PERCEPTION BRIDGE RULE:",
            "This interpretation is derived from visual pattern recognition only.",
        ]

        if not has_segy:
            warnings.append(
                "RASTER INPUT: No trace data available. Physical properties not preserved."
            )

        if verdict in [Verdict.HOLD, Verdict.VOID]:
            warnings.append(
                f"HIGH AC_RISK: View consistency {consistency:.2f}. "
                "Features may be display artifacts."
            )

        warnings.append(
            "MUST be corroborated with: (1) LEM geophysical data, "
            "(2) Well log measurements, or (3) Basin simulation results "
            "before any operational decision."
        )

        warnings.append("Reference: Bond et al. (2007) — 79% expert failure rate on similar data.")

        return " ".join(warnings)


# Quick self-test
if __name__ == "__main__":
    import asyncio

    async def test():
        vlm = GovernedSeismicVLM()

        # Create test image
        test_array = np.random.rand(400, 600).astype(np.float32) * 255
        test_image = Image.fromarray(test_array.astype(np.uint8))

        result = await vlm.interpret(
            image=test_image,
            interpretation_goal="Identify faults and horizons",
            has_segy=False,
            canonical_array=test_array / 255.0,
        )

        print("GovernedSeismicVLM Test Result:")
        print(f"  Verdict: {result.verdict.value}")
        print(f"  AC_Risk: {result.ac_risk_result.ac_risk:.3f}")
        print(f"  View Consistency: {result.view_consistency_score:.3f}")
        print(f"  Hypotheses: {len(result.hypotheses)}")
        print(f"  Warning: {result.perception_bridge_warning[:80]}...")

    asyncio.run(test())

"""
Saturation Model Selector — Phase B Implementation
DITEMPA BUKAN DIBERI

Evaluates and selects appropriate saturation models based on rock properties.
"""

from dataclasses import dataclass, field

from arifos.geox.physics.saturation_models import (
    ArchieModel,
    SimandouxModel,
)
from arifos.geox.tools.petrophysics.property_calculator import load_rock_state


@dataclass
class ModelEvaluation:
    """Evaluation result for a single model."""

    model_name: str
    is_admissible: bool
    confidence: float  # 0-1, how well model fits this rock
    justification: str
    rejection_reason: str | None = None
    violations: list[str] = field(default_factory=list)


class SaturationModelSelector:
    """
    Evaluate and select appropriate saturation models for a given interval.

    F2 Truth: Rejected models must explain why.
    F7 Humility: Confidence reflects model appropriateness, not accuracy.
    """

    AVAILABLE_MODELS = {
        "archie": ArchieModel,
        "simandoux": SimandouxModel,
    }

    async def evaluate(
        self, state, candidates: list[str] | None = None, **kwargs
    ) -> list[ModelEvaluation]:
        """
        Evaluate candidate models for this rock state.

        Args:
            state: RockFluidState or dict with rock properties
            candidates: List of model names to evaluate (default: archie, simandoux)

        Returns:
            List of ModelEvaluation, sorted by confidence (best first)
        """
        if candidates is None:
            candidates = ["archie", "simandoux"]

        # Extract properties from state
        vsh = self._extract_vsh(state)
        clay_type = self._extract_clay_type(state)
        salinity = self._extract_salinity(state)

        results = []

        for candidate in candidates:
            evaluation = self._evaluate_model(
                model_name=candidate,
                vsh=vsh,
                clay_type=clay_type,
                salinity=salinity,
            )
            results.append(evaluation)

        # Sort by confidence (highest first), then by admissibility
        results.sort(key=lambda x: (x.is_admissible, x.confidence), reverse=True)

        return results

    def _evaluate_model(
        self,
        model_name: str,
        vsh: float,
        clay_type: str | None,
        salinity: float | None,
    ) -> ModelEvaluation:
        """Evaluate a single model."""

        if model_name not in self.AVAILABLE_MODELS:
            return ModelEvaluation(
                model_name=model_name,
                is_admissible=False,
                confidence=0.0,
                justification=f"Model '{model_name}' not available in Phase B",
                rejection_reason="Model not implemented",
                violations=["Unknown model"],
            )

        model_class = self.AVAILABLE_MODELS[model_name]
        model = model_class()

        # Check assumptions
        violations = model.validate_assumptions(
            vsh=vsh,
            clay_type=clay_type,
            salinity=salinity,
        )

        if violations:
            # Model has assumption violations
            return ModelEvaluation(
                model_name=model_name,
                is_admissible=False,
                confidence=0.0,
                justification=f"Model assumptions violated for {model_name}",
                rejection_reason="; ".join(violations),
                violations=violations,
            )

        # Model is admissible - calculate confidence
        confidence = self._calculate_confidence(
            model_name=model_name,
            vsh=vsh,
            model_valid_range=model.valid_vsh_range,
        )

        return ModelEvaluation(
            model_name=model_name,
            is_admissible=True,
            confidence=confidence,
            justification=self._generate_justification(
                model_name=model_name,
                vsh=vsh,
                valid_range=model.valid_vsh_range,
            ),
            violations=[],
        )

    def _calculate_confidence(
        self,
        model_name: str,
        vsh: float,
        model_valid_range: tuple[float, float],
    ) -> float:
        """
        Calculate confidence score (0-1) for model appropriateness.

        Higher when Vsh is comfortably within the model's valid range.
        """
        range_min, range_max = model_valid_range
        range_center = (range_min + range_max) / 2
        range_width = range_max - range_min

        if vsh < range_min:
            # Below range - confidence drops off
            distance = range_min - vsh
            confidence = max(0.0, 0.7 - distance * 2)
        elif vsh > range_max:
            # Above range - confidence drops off
            distance = vsh - range_max
            confidence = max(0.0, 0.5 - distance * 2)
        else:
            # Within range - highest confidence near center
            distance_from_center = abs(vsh - range_center)
            normalized_distance = distance_from_center / (range_width / 2)
            confidence = 1.0 - 0.2 * normalized_distance

        return float(confidence)

    def _generate_justification(
        self,
        model_name: str,
        vsh: float,
        valid_range: tuple[float, float],
    ) -> str:
        """Generate human-readable justification."""
        if model_name == "archie":
            return f"Clean sand model. Vsh={vsh:.2f} within valid range [{valid_range[0]:.2f}, {valid_range[1]:.2f}]."
        elif model_name == "simandoux":
            return f"Dispersed shaly sand model. Vsh={vsh:.2f} within valid range [{valid_range[0]:.2f}, {valid_range[1]:.2f}]."
        else:
            return f"Model valid for Vsh={vsh:.2f}."

    def _extract_vsh(self, state) -> float:
        """Extract Vsh from state object or dict."""
        if hasattr(state, "vsh"):
            return state.vsh
        elif hasattr(state, "water_saturation") and state.water_saturation:
            # Try to get from saturation params
            if hasattr(state.water_saturation, "params"):
                return state.water_saturation.params.vsh or 0.0
        elif isinstance(state, dict):
            return state.get("vsh", 0.0)
        return 0.0

    def _extract_clay_type(self, state) -> str | None:
        """Extract clay type from state."""
        if hasattr(state, "clay_type"):
            return state.clay_type
        elif isinstance(state, dict):
            return state.get("clay_type")
        return None

    def _extract_salinity(self, state) -> float | None:
        """Extract salinity from state."""
        if hasattr(state, "salinity"):
            return state.salinity
        elif isinstance(state, dict):
            return state.get("salinity")
        return None


# Convenience function for async interface
async def select_model(
    interval_uri: str,
    candidates: list[str] | None = None,
) -> list[ModelEvaluation]:
    """
    Convenience function to select model for an interval.

    Args:
        interval_uri: geox://well/{id}/interval/{top}-{base}/rock-state
        candidates: List of candidate model names

    Returns:
        List of ModelEvaluation
    """
    # Parse interval URI
    try:
        parts = interval_uri.replace("geox://well/", "").split("/")
        well_id = parts[0]
        interval_part = parts[2] if len(parts) > 2 else "0-0"
        top_str, base_str = interval_part.split("-")
        top, base = float(top_str), float(base_str)
    except (IndexError, ValueError):
        raise ValueError(f"Invalid interval_uri: {interval_uri}")

    # Load rock state
    state = await load_rock_state(well_id, top, base)

    if state is None:
        # Return default evaluation for new interval
        return [
            ModelEvaluation(
                model_name="archie",
                is_admissible=True,
                confidence=0.8,
                justification="Default for new interval. Verify Vsh after computation.",
            )
        ]

    # Run selector
    selector = SaturationModelSelector()
    return await selector.evaluate(state, candidates)

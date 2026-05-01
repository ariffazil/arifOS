"""
Uncertainty Schemas — F7 Humility Enforcement
DITEMPA BUKAN DIBERI

Every petrophysical quantity carries uncertainty.
Zero uncertainty is a lie (F2 Truth violation).
"""

from __future__ import annotations


from pydantic import BaseModel, Field


class SensitivityAnalysis(BaseModel):
    """
    Sensitivity of output to input parameters.
    
    For uncertainty propagation and tornado diagrams.
    """
    parameter_name: str
    base_value: float
    perturbed_values: list[tuple[float, float]]  # (delta_input, delta_output)
    
    # Derivative at base case
    sensitivity_coefficient: float  # dOutput/dInput
    
    # Impact ranking
    impact_rank: int | None = None  # 1 = highest impact
    
    # Interpretation
    interpretation: str = ""  # "Sw highly sensitive to Rw uncertainty"


class UncertaintyEnvelope(BaseModel):
    """
    Complete uncertainty characterization for a petrophysical result.
    
    F7 Humility: Must be provided for every derived quantity.
    """
    quantity_name: str  # "Sw", "PHI", "K"
    
    # Central estimate
    best_estimate: float
    
    # Confidence intervals
    ci_50_low: float   # 50% CI (interquartile)
    ci_50_high: float
    ci_95_low: float   # 95% CI
    ci_95_high: float
    
    # Distribution
    distribution_type: Literal["normal", "lognormal", "triangular", "uniform", "empirical"]
    distribution_params: dict[str, float] = Field(default_factory=dict)
    
    # Sources of uncertainty
    measurement_uncertainty: float = 0.0  # Log precision
    model_uncertainty: float = 0.0        # Equation appropriateness
    parameter_uncertainty: float = 0.0    # Rw, m, etc.
    calibration_uncertainty: float = 0.0  # Core-log match
    
    # Sensitivity breakdown
    sensitivities: list[SensitivityAnalysis] = Field(default_factory=list)
    
    # Dominant source
    dominant_uncertainty_source: str | None = None
    
    # Monte Carlo (if used)
    monte_carlo_samples: int | None = None
    monte_carlo_seed: int | None = None
    
    def get_relative_uncertainty(self) -> float:
        """Relative uncertainty (half-width / value)."""
        if self.best_estimate == 0:
            return 1.0
        half_width = (self.ci_95_high - self.ci_95_low) / 2
        return half_width / self.best_estimate
    
    def is_f7_compliant(self) -> bool:
        """
        F7 Humility: Uncertainty should be in [0.03, 0.15] relative range.
        Too low = overconfidence. Too high = useless.
        """
        rel = self.get_relative_uncertainty()
        return 0.03 <= rel <= 0.15

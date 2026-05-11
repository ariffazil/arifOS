"""
Rock State Schemas — The Bridge Between Geology and Physics
DITEMPA BUKAN DIBERI

Every rock/fluid property carries uncertainty, provenance, and governance.
F7 Humility: Uncertainty is mandatory, not optional.
F2 Truth: Model assumptions must be explicit.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from arifos.geox.schemas.geox_schemas import ProvenanceRecord


class MineralVolume(BaseModel):
    """Volume fraction of a specific mineral from RATLAS."""

    mineral_code: str = Field(..., description="RATLAS code (SAND_QZ_CLEAN, etc.)")
    mineral_name: str
    volume_fraction: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    derivation: Literal[
        "multi_mineral_solver", "log_response", "core_xrd", "assumed", "default"
    ]


class PorosityEstimate(BaseModel):
    """
    Porosity is a distribution, not a number.

    F7 Humility: Must carry uncertainty band.
    F4 Clarity: Must declare porosity type and units.
    """

    # Primary estimate
    value: float = Field(..., ge=0.0, le=0.6, description="Porosity value")
    units: Literal["fraction", "percent"] = "fraction"

    # Uncertainty (F7 Humility enforcement)
    confidence_95_low: float = Field(..., description="95% CI lower bound")
    confidence_95_high: float = Field(..., description="95% CI upper bound")
    uncertainty_source: Literal["measurement", "model", "calibration", "combined"]

    # Physics basis
    porosity_type: Literal[
        "total", "effective", "micro", "isolated", "secondary", "frac"
    ]
    measurement_physics: Literal[
        "density",
        "neutron",
        "sonic",
        "nmr",
        "image",
        "core",
        "neutron_density_crossover",
    ]
    mixing_law: str = Field(..., description="Wyllie, Raymer-Hunt-Gardner, etc.")

    # Inputs for audit (F11)
    input_density: float | None = None  # g/cc
    input_neutron: float | None = None  # v/v
    input_sonic: float | None = None  # us/ft
    matrix_density: float | None = None  # From RATLAS
    fluid_density: float | None = None  # g/cc

    # Calibration
    calibration_source: str = Field(..., description="Which cores calibrated this")
    core_calibration_count: int = Field(default=0, description="Number of core points")

    # Provenance
    provenance: ProvenanceRecord

    @model_validator(mode="after")
    def check_uncertainty(self) -> "PorosityEstimate":
        """F7 Humility: Zero uncertainty is not allowed."""
        if self.confidence_95_low == self.confidence_95_high:
            raise ValueError("F7 violation: Zero uncertainty range not allowed")
        if self.confidence_95_low < 0 or self.confidence_95_high > 0.6:
            raise ValueError("Confidence interval outside physical bounds")
        return self

    @property
    def uncertainty_fraction(self) -> float:
        """Half-width of 95% CI relative to value."""
        if self.value == 0:
            return 1.0
        return (self.confidence_95_high - self.confidence_95_low) / (2 * self.value)


class SaturationModelParameters(BaseModel):
    """Parameters for water saturation models."""

    # Archie parameters
    archie_a: float = Field(default=1.0, description="Tortuosity factor")
    archie_m: float = Field(default=2.0, description="Cementation exponent")
    archie_n: float = Field(default=2.0, description="Saturation exponent")

    # m provenance
    m_derivation: Literal[
        "default", "pickett_plot", "core_measured", "literature", "regional_average"
    ]
    m_confidence: float = 0.5

    # Rw
    rw_at_conditions: float = Field(..., description="Rw at formation T (ohm-m)")
    rw_temperature_c: float = Field(..., description="Temperature for Rw")
    rw_source: Literal["sp", "water_sample", "catalog", "regional_default", "assumed"]
    rw_confidence: float = 0.5

    # Shaly sand parameters (if applicable)
    vsh: float | None = None
    rsh: float | None = None  # Shale resistivity
    cec: float | None = None  # Cation exchange capacity (Dual-Water)


class WaterSaturationEstimate(BaseModel):
    """
    Sw is the most abused number in petrophysics.
    F2 Truth: Model and assumptions must be explicit.
    """

    value: float = Field(..., ge=0.0, le=1.0)

    # Model used (CRITICAL for audit)
    model_family: Literal[
        "archie_clean",
        "simandoux_dispersed",
        "indonesia_mixed",
        "dual_water_cec",
        "waxman_smits_temp",
        "juvenile_freshwater",
    ]

    # Parameters
    params: SaturationModelParameters

    # Model validation (F9 Anti-Hantu)
    assumption_violations: list[str] = Field(default_factory=list)
    alternative_models_considered: list[str] = Field(default_factory=list)
    model_selection_confidence: float = Field(..., ge=0.0, le=1.0)

    # Uncertainty
    confidence_95_low: float
    confidence_95_high: float

    # Sensitivity derivatives (for uncertainty propagation)
    rw_sensitivity: float = Field(..., description="dSw/dRw")
    phi_sensitivity: float = Field(..., description="dSw/dPhi")
    m_sensitivity: float = Field(..., description="dSw/dm")

    # Validation against ground truth
    validated_by_mdt: bool = False
    validated_by_production: bool = False
    validated_by_core_dean_stark: bool = False
    validation_residual: float | None = None  # Log Sw - True Sw

    # Provenance
    provenance: ProvenanceRecord

    @property
    def is_validated(self) -> bool:
        return (
            self.validated_by_mdt
            or self.validated_by_production
            or self.validated_by_core_dean_stark
        )


class PermeabilityEstimate(BaseModel):
    """
    Permeability estimate with method and uncertainty.
    """

    value_md: float = Field(..., ge=0.0, description="Permeability in millidarcies")
    log10_value: float  # For log-normal distributions

    # Method
    method: Literal[
        "core",
        "timur_coates",
        "sdr",
        "winland_r35",
        "hfu_fzi",
        "kozeny_carman",
        "ml_estimate",
    ]

    # Uncertainty (log-normal)
    confidence_95_low: float
    confidence_95_high: float

    # Inputs
    porosity_input: float | None = None
    free_fluid_volume: float | None = None  # For NMR methods
    winland_r35: float | None = None  # microns
    fzi: float | None = None  # Flow zone indicator

    # HFU classification
    hfu_class: int | None = None
    hfu_name: str | None = None

    # Validation
    core_samples_used: list[str] = Field(default_factory=list)
    k_phi_correlation: float | None = None  # R^2 of k-phi relationship

    provenance: ProvenanceRecord


class FluidContact(BaseModel):
    """Oil-water or gas-oil contact."""

    contact_type: Literal["owc", "goc", "gwc", "fwl", "lwd"]
    depth_m: float
    confidence: float
    method: Literal["log_analysis", "pressure_gradient", "core", "test", "seismic"]


class RockFluidState(BaseModel):
    """
    The complete petrophysical state of a rock at conditions.
    This is the bridge between geology and physics.

    F1 Reversibility: Can be recalculated with different assumptions.
    F4 Clarity: Every number has provenance.
    F7 Humility: Every number has uncertainty.
    """

    # Identity
    state_id: str = Field(
        default_factory=lambda: f"RFS-{datetime.utcnow().timestamp()}"
    )
    well_id: str
    interval_top_m: float
    interval_base_m: float

    # Composition
    mineralogy: list[MineralVolume] = Field(default_factory=list)
    total_porosity: PorosityEstimate | None = None
    effective_porosity: PorosityEstimate | None = None

    # Fluids
    water_saturation: WaterSaturationEstimate | None = None
    hydrocarbon_saturation: float | None = Field(None, ge=0.0, le=1.0)
    bulk_volume_water: float | None = None  # Sw * Phi

    # Flow properties
    permeability: PermeabilityEstimate | None = None

    # Rock type
    hydraulic_flow_unit: str | None = None
    winland_r35_um: float | None = None

    # Contacts
    fluid_contacts: list[FluidContact] = Field(default_factory=list)

    # Classification (cutoff-dependent)
    is_net_reservoir: bool = False
    is_net_pay: bool = False
    net_to_gross: float = Field(0.0, ge=0.0, le=1.0)
    cutoff_policy_id: str | None = None

    # Physics summary
    saturation_model_used: str | None = None
    porosity_model_used: str | None = None
    environmental_corrections_applied: list[str] = Field(default_factory=list)

    # Evidence chain
    log_curves_used: list[str] = Field(default_factory=list)
    core_data_used: list[str] = Field(default_factory=list)
    scal_data_used: list[str] = Field(default_factory=list)
    mdt_data_used: list[str] = Field(default_factory=list)

    # Uncertainty
    state_confidence: float = Field(..., ge=0.0, le=1.0)
    non_uniqueness_score: float = Field(0.0, ge=0.0, le=1.0)

    # Governance
    floor_check: dict[str, bool] = Field(default_factory=dict)
    verdict: Literal["SEAL", "QUALIFY", "888_HOLD"] = "QUALIFY"
    hold_reasons: list[str] = Field(default_factory=list)

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "GEOX_ENGINE"
    calculation_version: str = "1.0.0"

    def to_summary_dict(self) -> dict[str, Any]:
        """Summary for UI display."""
        return {
            "state_id": self.state_id,
            "interval": f"{self.interval_top_m:.1f}-{self.interval_base_m:.1f}m",
            "phi": self.effective_porosity.value if self.effective_porosity else None,
            "sw": self.water_saturation.value if self.water_saturation else None,
            "k": self.permeability.value_md if self.permeability else None,
            "net_pay": self.is_net_pay,
            "verdict": self.verdict,
            "model": self.saturation_model_used,
        }

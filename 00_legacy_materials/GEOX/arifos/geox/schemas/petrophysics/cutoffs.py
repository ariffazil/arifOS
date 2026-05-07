"""
Cutoff Policy Schemas — Decision Thresholds, Not Physical Laws
DITEMPA BUKAN DIBERI

F2 Truth: Cutoffs are economic/project decisions, not physics.
F4 Clarity: Rationale must be explicit.
F11 Auditability: Full chain of custody.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CutoffDefinition(BaseModel):
    """
    A single cutoff threshold with full provenance.

    This is where the 'magic numbers' of petrophysics become explicit,
    auditable, and reversible (F1 Amanah).
    """

    parameter: Literal["porosity", "vsh", "sw", "permeability", "ntg"]
    threshold_value: float
    operator: Literal[">", ">=", "<", "<=", "==", "range"]

    # Rationale (F2 Truth requirement)
    physics_justification: str | None = Field(
        default=None, description="Capillary pressure, relative perm, etc."
    )
    calibration_basis: str = Field(..., description="Which cores/MDT/SCAL calibrated this cutoff")
    calibration_sample_count: int = Field(default=0)

    # Economic basis (for pay cutoffs)
    economic_basis: str | None = Field(
        default=None, description="Oil price, OPEX, discount rate at time of definition"
    )
    oil_price_usd: float | None = None
    opex_usd: float | None = None

    # Uncertainty of the cutoff itself
    false_positive_rate: float = Field(0.0, ge=0.0, le=1.0)
    false_negative_rate: float = Field(0.0, ge=0.0, le=1.0)
    confidence_score: float = Field(0.5, ge=0.0, le=1.0)

    # Governance
    defined_by: str  # Petrophysicist name
    peer_reviewed_by: str | None = None
    approved_by: str  # Manager name
    definition_date: datetime
    review_date: datetime | None = None

    # Version control
    superseded_by: str | None = None
    superseded_date: datetime | None = None

    @property
    def is_current(self) -> bool:
        """Check if this cutoff definition is current (not superseded)."""
        return self.superseded_by is None


class CutoffPolicy(BaseModel):
    """
    A complete policy for net/gross and pay determination.

    Versioned, auditable, and reversible (F1 Amanah).
    Each policy represents a snapshot of decision criteria.
    """

    policy_id: str = Field(..., description="Unique identifier (UUID)")
    policy_name: str = Field(..., description="Human-readable name")
    version: str = "1.0.0"

    # Cutoffs by dimension
    porosity_cutoff: CutoffDefinition | None = None
    vsh_cutoff: CutoffDefinition | None = None
    sw_cutoff_oil: CutoffDefinition | None = None
    sw_cutoff_gas: CutoffDefinition | None = None
    permeability_cutoff: CutoffDefinition | None = None

    # Combined logic
    net_reservoir_logic: str = Field(
        default="(vsh < VSH_CUTOFF) AND (phi > PHI_CUTOFF)",
        description="Boolean expression for net reservoir",
    )
    net_pay_logic: str = Field(
        default="net_reservoir AND (sw < SW_CUTOFF)", description="Boolean expression for net pay"
    )

    # Scope
    applicable_basins: list[str] = Field(default_factory=list)
    applicable_formations: list[str] = Field(default_factory=list)
    applicable_fields: list[str] = Field(default_factory=list)
    applicable_fluid_systems: list[Literal["oil", "gas", "condensate"]] = Field(
        default_factory=list
    )

    # Validity period
    valid_from: datetime
    valid_until: datetime | None = None

    # Governance
    created_by: str
    approved_by: str
    approval_date: datetime

    # Floor check (constitutional compliance)
    floor_check: dict[str, bool] = Field(
        default_factory=lambda: {
            "F1_amanah": True,
            "F2_truth": True,
            "F4_clarity": True,
            "F7_humility": True,
            "F9_anti_hantu": True,
            "F11_authority": True,
            "F13_sovereign": True,
        }
    )

    # Metadata
    notes: str = ""
    references: list[str] = Field(default_factory=list)  # Papers, reports

    def check_interval(
        self, phi: float, vsh: float, sw: float, k: float | None = None
    ) -> dict[str, bool]:
        """
        Apply this policy to a single interval.
        Returns classification flags.
        """
        results = {
            "passes_phi": True,
            "passes_vsh": True,
            "passes_sw": True,
            "passes_k": True,
            "is_net_reservoir": False,
            "is_net_pay": False,
        }

        if self.porosity_cutoff:
            op = self.porosity_cutoff.operator
            thresh = self.porosity_cutoff.threshold_value
            if op == ">":
                results["passes_phi"] = phi > thresh
            elif op == ">=":
                results["passes_phi"] = phi >= thresh

        if self.vsh_cutoff:
            op = self.vsh_cutoff.operator
            thresh = self.vsh_cutoff.threshold_value
            if op == "<":
                results["passes_vsh"] = vsh < thresh
            elif op == "<=":
                results["passes_vsh"] = vsh <= thresh

        if self.sw_cutoff_oil:
            op = self.sw_cutoff_oil.operator
            thresh = self.sw_cutoff_oil.threshold_value
            if op == "<":
                results["passes_sw"] = sw < thresh

        # Combined logic
        results["is_net_reservoir"] = results["passes_phi"] and results["passes_vsh"]
        results["is_net_pay"] = results["is_net_reservoir"] and results["passes_sw"]

        return results

    @property
    def is_active(self) -> bool:
        """Check if policy is currently active."""
        now = datetime.utcnow()
        return self.valid_from <= now and (self.valid_until is None or now < self.valid_until)

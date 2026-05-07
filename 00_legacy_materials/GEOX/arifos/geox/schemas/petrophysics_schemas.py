"""
petrophysics_schemas.py — Governed Petrophysics Pipeline Schemas
═══════════════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI

Pydantic v2 schemas for the petrophysics MCP tool pipeline:
  1. geox_select_sw_model     — model admissibility from QC flags
  2. geox_compute_petrophysics — full property pipeline
  3. geox_validate_cutoffs    — apply CutoffPolicy
  4. geox_petrophysical_hold_check — trigger 888_HOLD on floor violations

Provenance tags used in this module:
  RAW       — direct instrument reading, no correction
  CORRECTED — environmental correction applied (borehole, invasion, etc.)
  DERIVED   — computed from raw/corrected inputs (Vsh, PHIe, Sw)
  POLICY    — value produced or modified by a governance rule (CutoffPolicy)

Constitutional Floors:
  F2  Truth  — no ungrounded Sw claim
  F4  Clarity — units mandatory on every quantity
  F7  Humility — uncertainty in [0.03, 0.15]
  F9  Anti-Hantu — no phantom formation data
  F11 Authority — provenance required
  F13 Sovereign — human veto on high-risk interpretations
"""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# Provenance Tag Enum (literal union for strict JSON schema)
# ─────────────────────────────────────────────────────────────────────────────

ProvenanceTag = Literal["RAW", "CORRECTED", "DERIVED", "POLICY"]


# ─────────────────────────────────────────────────────────────────────────────
# LogQCFlags — F9 Anti-Hantu: surface well-log quality before model selection
# ─────────────────────────────────────────────────────────────────────────────


class LogQCFlags(BaseModel):
    """
    Quality control flags from wireline/LWD log analysis.

    These flags gate which Sw model may be used.  A washout or badly invaded
    zone makes resistivity data unreliable, triggering 888_HOLD if ignored.

    Provenance tag: RAW (flags derived directly from caliper / log review)
    """

    well_id: str = Field(
        ...,
        min_length=1,
        description="Unique well identifier (e.g. 'PM3-A-12').",
    )
    depth_top_m: float = Field(
        ...,
        description="Top of evaluation interval, measured depth metres.",
    )
    depth_base_m: float = Field(
        ...,
        description="Base of evaluation interval, measured depth metres.",
    )

    # ── Borehole quality ────────────────────────────────────────────────────
    has_washout: bool = Field(
        default=False,
        description=(
            "Caliper > bit_size + 2 in over ≥ 20 % of interval. "
            "Washout inflates apparent porosity and biases Sw low."
        ),
    )
    washout_fraction: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of interval affected by washout [0-1].",
    )
    borehole_quality: Literal["good", "fair", "poor"] = Field(
        default="good",
        description="Overall borehole quality assessment.",
    )

    # ── Formation evaluation issues ─────────────────────────────────────────
    has_invasion: bool = Field(
        default=False,
        description="Invaded zone detected (shallow vs deep resistivity divergence > 2×).",
    )
    has_gas_effect: bool = Field(
        default=False,
        description=(
            "Gas crossover on NPHI-RHOB detected. "
            "Gas effect inflates neutron-density separation; Sw models need correction."
        ),
    )
    has_shale: bool = Field(
        default=True,
        description="Shale intervals present (Vsh > 0.15 in any part of interval).",
    )
    vsh_max: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Maximum Vsh observed in the interval [0-1 fraction].",
    )

    # ── Resistivity tool availability ────────────────────────────────────────
    has_deep_resistivity: bool = Field(
        default=True,
        description="ILD/LLD deep resistivity curve available and QC'd.",
    )
    has_shallow_resistivity: bool = Field(
        default=False,
        description="MSFL/SFL shallow resistivity available (needed for invasion correction).",
    )

    # ── Data completeness ────────────────────────────────────────────────────
    available_curves: list[str] = Field(
        default_factory=list,
        description=(
            "List of QC-passed log curve mnemonics " "(e.g. ['GR', 'NPHI', 'RHOB', 'ILD', 'DT'])."
        ),
    )
    provenance_tag: ProvenanceTag = Field(
        default="RAW",
        description="Provenance tag for QC flags.",
    )

    @model_validator(mode="after")
    def depth_interval_positive(self) -> LogQCFlags:
        if self.depth_base_m <= self.depth_top_m:
            raise ValueError(
                f"depth_base_m ({self.depth_base_m}) must be > depth_top_m ({self.depth_top_m})."
            )
        return self

    model_config = {"json_schema_extra": {"title": "LogQCFlags"}}


# ─────────────────────────────────────────────────────────────────────────────
# SwModelAdmissibility — output of geox_select_sw_model
# ─────────────────────────────────────────────────────────────────────────────


class SwModelAdmissibility(BaseModel):
    """
    Result of Sw model admissibility evaluation.

    Provenance tag: POLICY (decision is rule-driven, not raw measurement).

    Constitutional note:
      A model is 'inadmissible' when QC flags indicate the resistivity data
      cannot support that model's assumptions — e.g. Archie requires clean
      sand, Simandoux requires reliable Rsh.  Selecting an inadmissible model
      is an F9 violation (phantom data) and must trigger HOLD.
    """

    well_id: str
    recommended_model: Literal["archie", "simandoux", "indonesia", "none"] = Field(
        ...,
        description=(
            "'none' means no Sw model is admissible given the QC flags; " "888_HOLD must be raised."
        ),
    )
    admissible_models: list[Literal["archie", "simandoux", "indonesia"]] = Field(
        default_factory=list,
        description="All models that pass QC admissibility checks.",
    )
    inadmissible_models: dict[str, list[str]] = Field(
        default_factory=dict,
        description="model_name → list of rejection reasons.",
    )
    requires_hold: bool = Field(
        default=False,
        description="True when no admissible model exists or borehole quality is poor.",
    )
    hold_reasons: list[str] = Field(
        default_factory=list,
        description="Reasons for 888_HOLD if requires_hold is True.",
    )
    confidence: float = Field(
        default=0.08,
        ge=0.03,
        le=0.15,
        description="F7 Humility: confidence in model selection [0.03, 0.15].",
    )
    floor_verdicts: dict[str, bool] = Field(
        default_factory=lambda: {
            "F2_truth": True,
            "F4_clarity": True,
            "F7_humility": True,
            "F9_anti_hantu": True,
            "F11_authority": True,
        },
    )
    provenance_tag: ProvenanceTag = Field(default="POLICY")

    model_config = {"json_schema_extra": {"title": "SwModelAdmissibility"}}


# ─────────────────────────────────────────────────────────────────────────────
# PetrophysicsInput — input for geox_compute_petrophysics
# ─────────────────────────────────────────────────────────────────────────────


class PetrophysicsInput(BaseModel):
    """
    Input bundle for a full petrophysics property computation.

    Mandatory physical parameters are validated here so that the compute
    pipeline never receives un-unitised bare numbers (F4 Clarity).
    """

    well_id: str = Field(..., min_length=1)
    sw_model: Literal["archie", "simandoux", "indonesia"] = Field(
        ...,
        description="Water saturation model to apply (must be admissible per LogQCFlags).",
    )

    # ── Resistivity ──────────────────────────────────────────────────────────
    rw_ohm_m: float = Field(
        ...,
        gt=0.0,
        description="Formation water resistivity [ohm·m] at reservoir temperature.",
    )
    rt_ohm_m: float = Field(
        ...,
        gt=0.0,
        description="True formation resistivity (ILD/LLD) [ohm·m].",
    )

    # ── Porosity ─────────────────────────────────────────────────────────────
    phi_fraction: float = Field(
        ...,
        gt=0.0,
        le=0.50,
        description="Effective porosity [fraction]. Physical range (0, 0.50].",
    )

    # ── Shale parameters (required for Simandoux / Indonesia) ────────────────
    vcl_fraction: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Clay volume fraction [0-1]. Required for shaly-sand models.",
    )
    rsh_ohm_m: float | None = Field(
        default=None,
        description=("Shale resistivity [ohm·m]. " "Required for simandoux/indonesia models."),
    )

    # ── Archie parameters ────────────────────────────────────────────────────
    archie_a: float = Field(default=1.0, gt=0.0, description="Archie tortuosity factor a.")
    archie_m: float = Field(default=2.0, gt=0.0, description="Archie cementation exponent m.")
    archie_n: float = Field(default=2.0, gt=0.0, description="Archie saturation exponent n.")

    # ── Monte Carlo ──────────────────────────────────────────────────────────
    run_monte_carlo: bool = Field(
        default=True,
        description="Run Monte Carlo uncertainty (1 000 iterations) for F7 Humility.",
    )
    mc_samples: int = Field(
        default=1000,
        ge=100,
        le=50000,
        description="Monte Carlo sample count.",
    )

    provenance_tag: ProvenanceTag = Field(
        default="RAW",
        description="Provenance tag for the input measurements.",
    )

    @model_validator(mode="after")
    def shaly_sand_needs_rsh(self) -> PetrophysicsInput:
        if self.sw_model in ("simandoux", "indonesia") and self.rsh_ohm_m is None:
            raise ValueError(
                f"rsh_ohm_m is required for model '{self.sw_model}' (shaly-sand). "
                "Provide shale resistivity or switch to 'archie'."
            )
        return self

    model_config = {"json_schema_extra": {"title": "PetrophysicsInput"}}


# ─────────────────────────────────────────────────────────────────────────────
# PetrophysicsOutput — output of geox_compute_petrophysics
# ─────────────────────────────────────────────────────────────────────────────


class PetrophysicsOutput(BaseModel):
    """
    Full petrophysics pipeline output with provenance and uncertainty.

    Provenance tag: DERIVED (Sw, BVW computed from corrected inputs).

    Constitutional notes:
      - Sw > 1.0 is a physical impossibility → triggers 888_HOLD
      - Uncertainty from Monte Carlo must be surfaced (F7)
      - BVW = Sw × PHIe is the key HC indicator
    """

    well_id: str
    sw_model_used: str
    sw_nominal: float = Field(
        ...,
        ge=0.0,
        description="Nominal water saturation (P50 of MC if run, else deterministic).",
    )
    sw_p10: float | None = Field(default=None, description="Sw P10 (optimistic) from MC.")
    sw_p50: float | None = Field(default=None, description="Sw P50 (median) from MC.")
    sw_p90: float | None = Field(default=None, description="Sw P90 (pessimistic) from MC.")
    sw_std: float | None = Field(default=None, description="Sw standard deviation from MC.")

    phi_effective: float = Field(..., gt=0.0, le=0.50, description="Effective porosity [fraction].")
    vcl: float = Field(default=0.0, ge=0.0, le=1.0, description="Clay volume [fraction].")
    bvw: float = Field(
        ...,
        ge=0.0,
        description="Bulk Volume Water = Sw × PHIe [fraction].",
    )

    uncertainty: float = Field(
        default=0.09,
        ge=0.03,
        le=0.15,
        description="Overall property uncertainty (F7 Humility) [fraction].",
    )

    hold_triggers: list[str] = Field(
        default_factory=list,
        description="List of 888_HOLD trigger messages (empty → no hold).",
    )
    requires_hold: bool = Field(
        default=False,
        description="True if any hold triggers are present.",
    )

    floor_verdicts: dict[str, bool] = Field(
        default_factory=lambda: {
            "F2_truth": True,
            "F4_clarity": True,
            "F7_humility": True,
            "F9_anti_hantu": True,
            "F11_authority": True,
        },
    )
    claim_tag: Literal["CLAIM", "PLAUSIBLE", "HYPOTHESIS", "UNKNOWN"] = Field(
        default="UNKNOWN",
        description="Epistemic status of the petrophysical claim (ClaimTag).",
    )
    provenance_tag: ProvenanceTag = Field(default="DERIVED")
    audit_id: str = Field(
        default_factory=lambda: f"PETRO-{uuid.uuid4().hex[:8].upper()}",
        description="Unique audit trail ID for this computation.",
    )

    @model_validator(mode="after")
    def flag_physically_impossible_sw(self) -> PetrophysicsOutput:
        if self.sw_nominal > 1.0:
            self.hold_triggers.append(
                f"Sw ({self.sw_nominal:.3f}) > 1.0 — physical impossibility (F2 Truth violation)."
            )
            self.requires_hold = True
            self.floor_verdicts["F2_truth"] = False
        return self

    model_config = {"json_schema_extra": {"title": "PetrophysicsOutput"}}


# ─────────────────────────────────────────────────────────────────────────────
# CutoffPolicy — schema for geox_validate_cutoffs
# ─────────────────────────────────────────────────────────────────────────────


class CutoffPolicy(BaseModel):
    """
    Reservoir quality cutoffs used to classify pay vs non-pay intervals.

    Provenance tag: POLICY (values are corporate / regulatory policy, not
    measured quantities — do not confuse with formation data).

    Standard cutoff parameters (tune per field):
      phi_cutoff    — minimum porosity for net reservoir
      sw_cutoff     — maximum Sw for net pay
      vcl_cutoff    — maximum Vsh for net reservoir
      rt_cutoff     — minimum Rt for HC indication
    """

    policy_id: str = Field(
        ...,
        min_length=1,
        description="Unique policy identifier (e.g. 'MALAY-BASIN-STD-2024').",
    )
    phi_cutoff: float = Field(
        ...,
        gt=0.0,
        le=0.50,
        description="Minimum effective porosity for net reservoir [fraction].",
    )
    sw_cutoff: float = Field(
        ...,
        gt=0.0,
        le=1.0,
        description="Maximum water saturation for net pay [fraction]. Pay = Sw < sw_cutoff.",
    )
    vcl_cutoff: float = Field(
        ...,
        gt=0.0,
        le=1.0,
        description="Maximum clay volume for net reservoir [fraction].",
    )
    rt_cutoff: float | None = Field(
        default=None,
        gt=0.0,
        description="Minimum true resistivity for HC indication [ohm·m]. Optional.",
    )
    basis: str = Field(
        default="analogue",
        description=(
            "Justification for cutoff values: 'analogue', 'core_calibration', "
            "'literature', 'regulatory'."
        ),
    )
    provenance_tag: ProvenanceTag = Field(default="POLICY")

    model_config = {"json_schema_extra": {"title": "CutoffPolicy"}}


# ─────────────────────────────────────────────────────────────────────────────
# CutoffValidationResult — output of geox_validate_cutoffs
# ─────────────────────────────────────────────────────────────────────────────


class CutoffValidationResult(BaseModel):
    """
    Result of applying CutoffPolicy to PetrophysicsOutput.

    Provenance tag: POLICY (classification is policy-driven).

    Constitutional note:
      Cutoffs are a governance rule, not a physical measurement.
      The provenance chain must record which policy version was applied
      so that verdicts are reproducible (F1 Amanah / reversibility).
    """

    well_id: str
    policy_id: str

    is_net_reservoir: bool = Field(
        ...,
        description="PHI > phi_cutoff AND Vcl < vcl_cutoff.",
    )
    is_net_pay: bool = Field(
        ...,
        description="is_net_reservoir AND Sw < sw_cutoff.",
    )
    passed_rt_cutoff: bool | None = Field(
        default=None,
        description="Rt > rt_cutoff if rt_cutoff defined, else None.",
    )

    # Detailed sub-checks
    phi_pass: bool = Field(..., description="PHIe ≥ phi_cutoff.")
    sw_pass: bool = Field(..., description="Sw < sw_cutoff.")
    vcl_pass: bool = Field(..., description="Vcl < vcl_cutoff.")

    # Values tested
    phi_tested: float = Field(..., description="PHIe value tested [fraction].")
    sw_tested: float = Field(..., description="Sw value tested [fraction].")
    vcl_tested: float = Field(..., description="Vcl value tested [fraction].")
    rt_tested: float | None = Field(default=None, description="Rt value tested [ohm·m].")

    violations: list[str] = Field(
        default_factory=list,
        description="Human-readable descriptions of cutoff failures.",
    )
    requires_hold: bool = Field(
        default=False,
        description="True if a physical impossibility was detected during cutoff check.",
    )
    provenance_tag: ProvenanceTag = Field(default="POLICY")
    audit_id: str = Field(
        default_factory=lambda: f"CUT-{uuid.uuid4().hex[:8].upper()}",
    )

    model_config = {"json_schema_extra": {"title": "CutoffValidationResult"}}


# ─────────────────────────────────────────────────────────────────────────────
# PetrophysicsHold — explicit 888_HOLD object
# ─────────────────────────────────────────────────────────────────────────────


class PetrophysicsHold(BaseModel):
    """
    Explicit 888_HOLD raised by geox_petrophysical_hold_check.

    Never silently ignored — any floor violation must surface an explicit
    PetrophysicsHold with a documented reason and the violated floor.

    Constitutional note:
      HOLD objects are not errors — they are constitutional signals that
      human review is required before the computation can proceed.
      They must be logged to 999_VAULT.
    """

    hold_id: str = Field(
        default_factory=lambda: f"HOLD-{uuid.uuid4().hex[:8].upper()}",
        description="Unique identifier for this hold.",
    )
    well_id: str
    triggered_by: str = Field(
        ...,
        description=(
            "Tool or check that triggered the hold "
            "(e.g. 'geox_petrophysical_hold_check', 'geox_validate_cutoffs')."
        ),
    )
    violated_floors: list[str] = Field(
        ...,
        min_length=1,
        description="Constitutional floor(s) violated (e.g. ['F7', 'F9']).",
    )
    violations: list[str] = Field(
        ...,
        min_length=1,
        description="Human-readable violation descriptions.",
    )
    remediation: list[str] = Field(
        default_factory=list,
        description="Recommended remediation actions before HOLD can be cleared.",
    )
    severity: Literal["warning", "block"] = Field(
        default="block",
        description=(
            "'warning' = proceed with documented caveat; "
            "'block' = must not proceed without human sign-off (F13)."
        ),
    )
    requires_human_signoff: bool = Field(
        default=True,
        description="F13 Sovereign: True for all block-level holds.",
    )
    provenance_tag: ProvenanceTag = Field(default="POLICY")

    @model_validator(mode="after")
    def block_always_needs_signoff(self) -> PetrophysicsHold:
        if self.severity == "block" and not self.requires_human_signoff:
            raise ValueError(
                "F13 violation: block-level holds require requires_human_signoff=True."
            )
        return self

    model_config = {"json_schema_extra": {"title": "PetrophysicsHold"}}

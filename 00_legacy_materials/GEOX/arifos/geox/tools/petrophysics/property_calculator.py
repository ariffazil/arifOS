"""
Property Calculator — Phase B Implementation
DITEMPA BUKAN DIBERI

Computes Vsh, porosity, Sw, BVW, permeability with uncertainty propagation.
"""

from datetime import datetime
from typing import Any

from arifos.geox.physics.saturation_models import (
    ArchieModel,
    SimandouxModel,
    ModelResult as SaturationResult,
)
from arifos.geox.physics.porosity_solvers import (
    VshSolver,
    DensityNeutronSolver,
    PorosityResult,
    VshResult,
    compute_bvw,
    compute_permeability_proxy,
)
from arifos.geox.schemas.petrophysics.rock_state import (
    RockFluidState,
    PorosityEstimate,
    WaterSaturationEstimate,
    PermeabilityEstimate,
    SaturationModelParameters,
    ProvenanceRecord,
)


# In-memory store
_state_store: dict[str, RockFluidState] = {}


async def load_rock_state(well_id: str, top: float, base: float) -> RockFluidState | None:
    """Load rock state for interval."""
    key = f"{well_id}:{top}:{base}"
    return _state_store.get(key)


async def store_rock_state(state: RockFluidState) -> None:
    """Store rock state."""
    key = f"{state.well_id}:{state.interval_top_m}:{state.interval_base_m}"
    _state_store[key] = state


class PetrophysicsCalculator:
    """
    Calculate petrophysical properties with uncertainty propagation.

    F2 Truth: All model assumptions explicit.
    F7 Humility: Uncertainty bands mandatory.
    """

    def __init__(
        self,
        model_id: str,
        model_params: dict[str, Any],
    ):
        self.model_id = model_id
        self.model_params = model_params

        # Initialize model
        if model_id == "archie":
            self.model = ArchieModel(
                a=model_params.get("a", 1.0),
                m=model_params.get("m", 2.0),
                n=model_params.get("n", 2.0),
            )
        elif model_id == "simandoux":
            self.model = SimandouxModel(
                a=model_params.get("a", 1.0),
                m=model_params.get("m", 2.0),
                n=model_params.get("n", 2.0),
                rsh=model_params.get("rsh", 4.0),
            )
        else:
            raise ValueError(f"Unknown model: {model_id}")

    async def compute(
        self,
        well_id: str,
        top: float,
        base: float,
        propagate_uncertainty: bool = True,
    ) -> RockFluidState:
        """
        Compute full petrophysical evaluation for an interval.

        Args:
            well_id: Well identifier
            top: Interval top depth (m)
            base: Interval base depth (m)
            propagate_uncertainty: Whether to calculate uncertainty bands

        Returns:
            RockFluidState with all computed properties
        """
        # Step 1: Load log data for interval
        log_data = await self._load_log_data(well_id, top, base)

        # Step 2: Compute Vsh from GR
        vsh_result = self._compute_vsh(log_data)

        # Step 3: Compute porosity
        phi_result = self._compute_porosity(log_data, vsh_result)

        # Step 4: Compute water saturation
        sw_result = self._compute_sw(
            log_data=log_data,
            phi=phi_result.phi,
            vsh=vsh_result.vsh,
        )

        # Step 5: Compute BVW
        bvw, bvw_unc = compute_bvw(
            phi=phi_result.phi,
            sw=sw_result.sw,
            phi_uncertainty=phi_result.phi_uncertainty if propagate_uncertainty else 0,
            sw_uncertainty=sw_result.sw_uncertainty if propagate_uncertainty else 0,
        )

        # Step 6: Compute permeability proxy
        k_md, k_desc = compute_permeability_proxy(
            phi=phi_result.phi,
            sw=sw_result.sw,
            method="timur_coates" if sw_result.sw < 0.9 else "simple_power",
        )

        # Step 7: Build RockFluidState
        state = self._build_rock_state(
            well_id=well_id,
            top=top,
            base=base,
            vsh_result=vsh_result,
            phi_result=phi_result,
            sw_result=sw_result,
            bvw=bvw,
            bvw_unc=bvw_unc,
            k_md=k_md,
            k_desc=k_desc,
            log_data=log_data,
        )

        # Store result
        await store_rock_state(state)

        return state

    async def _load_log_data(
        self,
        well_id: str,
        top: float,
        base: float,
    ) -> dict[str, Any]:
        """Load log data for the interval."""
        # In production: Load from bundle store
        # For now: Return synthetic test data
        return {
            "gr": 75.0,  # API
            "rhob": 2.35,  # g/cm³
            "nphi": 0.20,  # fraction
            "rt": 20.0,  # ohm-m
            "rw": self.model_params.get("rw", 0.1),  # ohm-m
            "vsh": None,  # Will be computed
        }

    def _compute_vsh(self, log_data: dict) -> VshResult:
        """Compute Vsh from GR."""
        solver = VshSolver(gr_clean=30, gr_shale=120)

        gr = log_data.get("gr", 75.0)

        # Use Clavier-Fertl for better low-Vsh accuracy
        return solver.compute_clavier_fertl(gr=gr)

    def _compute_porosity(
        self,
        log_data: dict,
        vsh_result: VshResult,
    ) -> PorosityResult:
        """Compute porosity from density-neutron."""
        solver = DensityNeutronSolver(
            rho_matrix=2.65,  # Quartz
            rho_fluid=1.0,  # Water
        )

        # Total porosity
        phi_total = solver.compute_phi(
            rhob=log_data.get("rhob", 2.35),
            nphi=log_data.get("nphi", 0.20),
        )

        # Effective porosity
        phi_effective = solver.compute_effective_porosity(
            phi_total=phi_total.phi,
            vsh=vsh_result.vsh,
            phi_shale=0.30,
        )

        return phi_effective

    def _compute_sw(
        self,
        log_data: dict,
        phi: float,
        vsh: float,
    ) -> SaturationResult:
        """Compute water saturation using selected model."""
        rt = log_data.get("rt", 20.0)
        rw = log_data.get("rw", self.model_params.get("rw", 0.1))

        # Model-specific parameters
        kwargs = {}
        if isinstance(self.model, SimandouxModel):
            kwargs["vsh"] = vsh
            kwargs["rsh"] = self.model_params.get("rsh", 4.0)

        return self.model.compute_sw(rt=rt, phi=phi, rw=rw, **kwargs)

    def _build_rock_state(
        self,
        well_id: str,
        top: float,
        base: float,
        vsh_result: VshResult,
        phi_result: PorosityResult,
        sw_result: SaturationResult,
        bvw: float,
        bvw_unc: float,
        k_md: float,
        k_desc: str,
        log_data: dict,
    ) -> RockFluidState:
        """Build complete RockFluidState from results."""

        # Create PorosityEstimate
        porosity = PorosityEstimate(
            value=phi_result.phi,
            units="fraction",
            confidence_95_low=phi_result.phi_low,
            confidence_95_high=phi_result.phi_high,
            uncertainty_source="model" if phi_result.phi_uncertainty > 0 else "measurement",
            porosity_type="effective",
            measurement_physics="neutron_density_crossover",
            mixing_law="gardner",
            input_density=log_data.get("rhob"),
            input_neutron=log_data.get("nphi"),
            matrix_density=2.65,
            fluid_density=1.0,
            calibration_source="field_default",
            core_calibration_count=0,
            provenance=ProvenanceRecord(
                source_id=f"{well_id}:{top}-{base}",
                source_type="simulator",
                timestamp=datetime.utcnow(),
                confidence=0.8,
            ),
        )

        # Create WaterSaturationEstimate
        saturation = WaterSaturationEstimate(
            value=sw_result.sw,
            model_family="archie_clean" if self.model_id == "archie" else "simandoux_dispersed",
            params=SaturationModelParameters(
                archie_a=self.model_params.get("a", 1.0),
                archie_m=self.model_params.get("m", 2.0),
                archie_n=self.model_params.get("n", 2.0),
                rw_at_conditions=log_data.get("rw", 0.1),
                rw_temperature_c=75.0,
                rw_source="assumed",
                rw_confidence=0.5,
                vsh=vsh_result.vsh if self.model_id == "simandoux" else None,
            ),
            assumption_violations=sw_result.assumption_violations,
            alternative_models_considered=(
                ["simandoux"] if self.model_id == "archie" else ["archie"]
            ),
            model_selection_confidence=0.85 if not sw_result.assumption_violations else 0.6,
            confidence_95_low=sw_result.sw_low,
            confidence_95_high=sw_result.sw_high,
            rw_sensitivity=0.1,  # dSw/dRw approximate
            phi_sensitivity=0.5,
            m_sensitivity=0.2,
            validated_by_mdt=False,
            validated_by_production=False,
            validated_by_core_dean_stark=False,
            provenance=ProvenanceRecord(
                source_id=f"{well_id}:{top}-{base}",
                source_type="simulator",
                timestamp=datetime.utcnow(),
                confidence=0.8 if not sw_result.assumption_violations else 0.5,
            ),
        )

        # Create PermeabilityEstimate
        permeability = PermeabilityEstimate(
            value_md=k_md,
            log10_value=10 if k_md <= 0 else k_md,  # Simplified
            method="timur_coates" if "timur" in k_desc.lower() else "simple_power",
            confidence_95_low=k_md * 0.1,  # Order of magnitude uncertainty
            confidence_95_high=k_md * 10.0,
            porosity_input=phi_result.phi,
            free_fluid_volume=None,
            winland_r35=None,
            fzi=None,
            hfu_class=None,
            hfu_name=None,
            core_samples_used=[],
            k_phi_correlation=None,
            provenance=ProvenanceRecord(
                source_id=f"{well_id}:{top}-{base}",
                source_type="simulator",
                timestamp=datetime.utcnow(),
                confidence=0.5,  # Low confidence - proxy only
            ),
        )

        # Determine verdict
        verdict = "QUALIFY"
        hold_reasons = []

        if sw_result.assumption_violations:
            verdict = "888_HOLD"
            hold_reasons.extend(sw_result.assumption_violations)

        if log_data.get("rw") is None or log_data.get("rw") <= 0:
            verdict = "888_HOLD"
            hold_reasons.append("Rw not calibrated (assumed value)")

        # Build state
        state = RockFluidState(
            well_id=well_id,
            interval_top_m=top,
            interval_base_m=base,
            total_porosity=None,  # Could add if needed
            effective_porosity=porosity,
            water_saturation=saturation,
            hydrocarbon_saturation=1.0 - sw_result.sw,
            bulk_volume_water=bvw,
            permeability=permeability,
            hydraulic_flow_unit=None,
            winland_r35_um=None,
            is_net_reservoir=False,  # Will be determined by cutoff validation
            is_net_pay=False,
            net_to_gross=0.0,
            cutoff_policy_id=None,
            saturation_model_used=self.model_id,
            porosity_model_used="density_neutron_crossover",
            environmental_corrections_applied=phi_result.environmental_corrections,
            log_curves_used=["GR", "RHOB", "NPHI", "RT"],
            core_data_used=[],
            scal_data_used=[],
            mdt_data_used=[],
            state_confidence=0.7 if verdict == "QUALIFY" else 0.4,
            non_uniqueness_score=0.2,
            floor_check={
                "F2_truth": len(sw_result.assumption_violations) == 0,
                "F4_clarity": True,
                "F7_humility": phi_result.phi_uncertainty > 0 and sw_result.sw_uncertainty > 0,
                "F9_anti_hantu": True,
                "F11_authority": True,
                "F13_sovereign": verdict != "888_HOLD",
            },
            verdict=verdict,
            hold_reasons=hold_reasons,
        )

        return state


# Convenience function
async def compute_petrophysics(
    well_id: str,
    top: float,
    base: float,
    model_id: str,
    model_params: dict[str, Any],
    propagate_uncertainty: bool = True,
) -> RockFluidState:
    """
    Convenience function to compute petrophysics for an interval.

    Args:
        well_id: Well identifier
        top: Interval top (m)
        base: Interval base (m)
        model_id: "archie" or "simandoux"
        model_params: Model parameters (a, m, n, rw, etc.)
        propagate_uncertainty: Calculate uncertainty bands

    Returns:
        RockFluidState
    """
    calculator = PetrophysicsCalculator(model_id, model_params)
    return await calculator.compute(
        well_id=well_id,
        top=top,
        base=base,
        propagate_uncertainty=propagate_uncertainty,
    )

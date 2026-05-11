"""
arifos/geox/tools/volumetrics_economics_tool.py — Volumetrics and Economics Tool
DITEMPA BUKAN DIBERI

Phase D — The Void: Volumetric Uncertainty and Economic Modelling.

This tool calculates:
  1. STOIIP (Stock Tank Oil Initially In Place) / GIIP (Gas Initially In Place)
  2. Recoverable Volumes (using Recovery Factors)
  3. Risk-Adjusted Economics (NPV, IRR, EMV)
  4. PoS (Probability of Success) fusion

All calculations use Monte Carlo simulation to honor the 'Void' (uncertainty).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from arifos.geox.base_tool import (
    BaseTool,
    GeoToolResult,
    _make_provenance,
    _make_quantity,
)
from arifos.geox.geox_schemas import CoordinatePoint

logger = logging.getLogger("geox.tools.volumetrics_economics")


@dataclass
class VolumetricInputs:
    area_km2: float  # Top surface area
    h_m: float  # Net pay thickness
    phi: float  # Average porosity
    sw: float  # Average water saturation
    ng: float  # Net-to-gross ratio
    bo: float  # Oil formation volume factor (or bg for gas)
    rf: float  # Recovery factor (0.0 - 1.0)


@dataclass
class EconomicInputs:
    price_per_bbl: float
    capex_m_usd: float
    opex_per_bbl: float
    discount_rate: float
    pos: float  # Probability of Success (0.0 - 1.0)


def run_stochastic_volumetrics(
    inputs: VolumetricInputs, uncert: float = 0.2, n_samples: int = 5000
) -> dict[str, Any]:
    """Calculate STOIIP and Recoverable volumes using Monte Carlo."""
    rng = np.random.default_rng()

    # Area (Lognormal)
    area = rng.lognormal(np.log(inputs.area_km2), uncert, n_samples)
    # Thickness (Normal)
    thickness = rng.normal(inputs.h_m, inputs.h_m * uncert, n_samples)
    thickness = np.clip(thickness, 0, None)
    # Porosity (Normal)
    phi = rng.normal(inputs.phi, inputs.phi * uncert * 0.5, n_samples)
    phi = np.clip(phi, 0.01, 0.45)
    # Sw (Normal)
    sw = rng.normal(inputs.sw, inputs.sw * uncert * 0.5, n_samples)
    sw = np.clip(sw, 0.05, 0.95)
    # N/G (Normal)
    ng = rng.normal(inputs.ng, inputs.ng * uncert * 0.5, n_samples)
    ng = np.clip(ng, 0, 1.0)

    # STOIIP Calculation (MMbbl)
    # STOIIP = (Area * 1e6 * Thickness * N/G * Phi * (1 - Sw)) / Bo / 1e6 (for MMbbl)
    stoiip = (area * 1e6 * thickness * ng * phi * (1 - sw)) / inputs.bo / 1e6

    # Recoverable (MMbbl)
    recoverable = stoiip * inputs.rf

    return {
        "stoiip_mean": float(np.mean(stoiip)),
        "stoiip_p90": float(np.percentile(stoiip, 10)),
        "stoiip_p50": float(np.percentile(stoiip, 50)),
        "stoiip_p10": float(np.percentile(stoiip, 90)),
        "recoverable_mean": float(np.mean(recoverable)),
        "recoverable_p50": float(np.percentile(recoverable, 50)),
        "samples_stoiip": stoiip.tolist()[:100],  # Return subset for plotting
    }


def run_economics(
    volumes_mmbbl: float,
    econ: EconomicInputs,
) -> dict[str, Any]:
    """Simple prospect economics (Project NPV/EMV)."""
    # Revenue = Vol * Price
    total_rev = volumes_mmbbl * 1e6 * econ.price_per_bbl
    # OPEX = Vol * Opex_per_bbl
    total_opex = volumes_mmbbl * 1e6 * econ.opex_per_bbl

    # Simple NPV (Undiscounted for now, or single year)
    # Real economics would have a production profile over time.
    # For this 'Void' tool, we use a simplified EMV approach.

    success_case_profit = total_rev - total_opex - (econ.capex_m_usd * 1e6)
    failure_case_loss = -(econ.capex_m_usd * 1e6) * 0.1  # Sunk cost of exploration well

    emv = (success_case_profit * econ.pos) + (failure_case_loss * (1 - econ.pos))

    return {
        "success_npv_m_usd": round(success_case_profit / 1e6, 2),
        "emv_m_usd": round(emv / 1e6, 2),
        "profitability_index": round(success_case_profit / (econ.capex_m_usd * 1e6), 2),
        "pos": econ.pos,
    }


class VolumetricsEconomicsTool(BaseTool):
    """
    Computes prospect volumetrics and economics under uncertainty.
    Exposes the 'Void' of exploration risk vs reward.
    """

    @property
    def name(self) -> str:
        return "VolumetricsEconomicsTool"

    @property
    def description(self) -> str:
        return (
            "Calculates STOIIP, recoverable volumes (P90/P50/P10), and risk-adjusted "
            "prospect economics (EMV, NPV) with Monte Carlo simulation."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        required = {"volumetrics", "economics"}
        if not all(k in inputs for k in required):
            return False
        return True

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="Invalid inputs. Required: 'volumetrics' and 'economics' objects.",
            )

        start = time.perf_counter()
        vol_data = inputs["volumetrics"]
        econ_data = inputs["economics"]
        location = inputs.get("location", CoordinatePoint(latitude=0.0, longitude=0.0))
        if isinstance(location, dict):
            location = CoordinatePoint(**location)

        vol_inputs = VolumetricInputs(
            area_km2=vol_data.get("area_km2", 10.0),
            h_m=vol_data.get("h_m", 50.0),
            phi=vol_data.get("phi", 0.2),
            sw=vol_data.get("sw", 0.3),
            ng=vol_data.get("ng", 0.8),
            bo=vol_data.get("bo", 1.2),
            rf=vol_data.get("rf", 0.35),
        )

        econ_inputs = EconomicInputs(
            price_per_bbl=econ_data.get("price_per_bbl", 80.0),
            capex_m_usd=econ_data.get("capex_m_usd", 120.0),
            opex_per_bbl=econ_data.get("opex_per_bbl", 15.0),
            discount_rate=econ_data.get("discount_rate", 0.1),
            pos=econ_data.get("pos", 0.25),
        )

        # Run Volumetrics
        vol_results = run_stochastic_volumetrics(vol_inputs)

        # Run Economics on P50
        econ_results = run_economics(vol_results["recoverable_p50"], econ_inputs)

        latency_ms = (time.perf_counter() - start) * 1000

        prov = _make_provenance(
            source_id="VOL-ECON-MC",
            source_type="monte_carlo_simulation",
            confidence=0.9,
            checksum="DITEMPA_BUKAN_DIBERI_VOID",
        )

        quantities = [
            _make_quantity(vol_results["stoiip_p50"], "MMbbl", "stoiip_p50", location, prov, 0.2),
            _make_quantity(econ_results["emv_m_usd"], "MUSD", "prospect_emv", location, prov, 0.3),
        ]

        raw_output = {
            "volumetrics": vol_results,
            "economics": econ_results,
            "inputs": {
                "volumetrics": vars(vol_inputs),
                "economics": vars(econ_inputs),
            },
            "verdict": "QUALIFY" if econ_results["emv_m_usd"] > 0 else "HOLD",
            "explanation": (
                f"Prospect deemed {'QUALIFIED' if econ_results['emv_m_usd'] > 0 else 'HOLD'} "
                f"based on EMV of ${econ_results['emv_m_usd']}M at {econ_inputs.pos:.0%} PoS."
            ),
        }

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={
                "tool_version": "VET-GEOX-v0.1.0",
                "simulation_samples": 5000,
                "workflow": "MC_VOLUMETRICS_ECONOMIC_IGNITION",
            },
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )

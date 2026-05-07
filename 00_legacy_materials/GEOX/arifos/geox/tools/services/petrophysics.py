"""
GEOX Petrophysics Services — Pure domain logic for saturation calculations.
No FastMCP imports. No transport dependencies.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SwInputParams:
    """Input parameters for Sw calculation."""

    rw: float | tuple[float, float]  # Formation water resistivity (nominal or (mean, std))
    rt: float | tuple[float, float]  # True formation resistivity
    phi: float | tuple[float, float]  # Porosity
    a: float = 1.0  # Tortuosity factor
    m: float = 2.0  # Cementation exponent
    n: float = 2.0  # Saturation exponent
    vcl: float | tuple[float, float] | None = None  # Clay volume
    rsh: float | tuple[float, float] | None = None  # Shale resistivity


@dataclass
class SwCalculationOutput:
    """Output from Sw calculation."""

    nominal_sw: float
    samples: list[float]
    stats: dict[str, float]
    hold_triggers: list[str]
    verdict: str


# ═══════════════════════════════════════════════════════════════════════════════
# Deterministic Calculations (Single Value)
# ═══════════════════════════════════════════════════════════════════════════════


def calculate_sw_archie(
    rw: float,
    rt: float,
    phi: float,
    a: float = 1.0,
    m: float = 2.0,
    n: float = 2.0,
) -> float:
    """
    Calculate water saturation using Archie equation.

    Sw = ((a * Rw) / (φ^m * Rt)) ^ (1/n)

    Args:
        rw: Formation water resistivity (ohm-m)
        rt: True formation resistivity (ohm-m)
        phi: Porosity (fraction)
        a: Tortuosity factor (default 1.0)
        m: Cementation exponent (default 2.0)
        n: Saturation exponent (default 2.0)

    Returns:
        Water saturation (fraction, 0-1)
    """
    if phi <= 0 or rt <= 0 or rw <= 0:
        return 1.0

    sw = ((a * rw) / ((phi**m) * rt)) ** (1 / n)
    return min(1.0, max(0.0, sw))


def calculate_sw_simandoux(
    rw: float,
    rt: float,
    phi: float,
    vcl: float,
    rsh: float,
    a: float = 1.0,
    m: float = 2.0,
    n: float = 2.0,
) -> float:
    """
    Calculate water saturation using Simandoux equation for shaly sands.

    Args:
        rw: Formation water resistivity (ohm-m)
        rt: True formation resistivity (ohm-m)
        phi: Porosity (fraction)
        vcl: Clay volume (fraction)
        rsh: Shale resistivity (ohm-m)
        a: Tortuosity factor (default 1.0)
        m: Cementation exponent (default 2.0)
        n: Saturation exponent (default 2.0)

    Returns:
        Water saturation (fraction, 0-1)
    """
    if phi <= 0 or rt <= 0 or rw <= 0 or not rsh or rsh <= 0:
        return 1.0

    term_a = (phi**m) / (a * rw)
    term_b = vcl / rsh
    term_c = 1 / rt

    sw = (1 / (2 * term_a)) * (math.sqrt(term_b**2 + 4 * term_a * term_c) - term_b)
    return min(1.0, max(0.0, sw))


def calculate_sw_indonesia(
    rw: float,
    rt: float,
    phi: float,
    vcl: float,
    rsh: float,
    a: float = 1.0,
    m: float = 2.0,
    n: float = 2.0,
) -> float:
    """
    Calculate water saturation using Indonesia equation for shaly sands.

    Args:
        rw: Formation water resistivity (ohm-m)
        rt: True formation resistivity (ohm-m)
        phi: Porosity (fraction)
        vcl: Clay volume (fraction)
        rsh: Shale resistivity (ohm-m)
        a: Tortuosity factor (default 1.0)
        m: Cementation exponent (default 2.0)
        n: Saturation exponent (default 2.0)

    Returns:
        Water saturation (fraction, 0-1)
    """
    if phi <= 0 or rt <= 0 or rw <= 0 or not rsh or rsh <= 0:
        return 1.0

    term_sh = (vcl ** (1 - vcl / 2)) / math.sqrt(rsh)
    term_sa = (phi ** (m / 2)) / math.sqrt(a * rw)
    denom = math.sqrt(rt) * (term_sh + term_sa)

    if denom == 0:
        return 1.0

    sw = (1 / denom) ** (2 / n)
    return min(1.0, max(0.0, sw))


def _extract_value_and_uncertainty(param: float | tuple[float, float]) -> tuple[float, float]:
    """Extract nominal value and uncertainty from param."""
    if isinstance(param, tuple):
        return param[0], param[1]
    return param, param * 0.05  # Default 5% uncertainty


def _sample_param(
    param: float | tuple[float, float],
    rng: random.Random,
) -> float:
    """Sample a value from param distribution."""
    value, uncertainty = _extract_value_and_uncertainty(param)
    if uncertainty == 0:
        return value
    # Simple Gaussian sampling
    return rng.gauss(value, uncertainty)


# ═══════════════════════════════════════════════════════════════════════════════
# Monte Carlo Simulation
# ═══════════════════════════════════════════════════════════════════════════════


def monte_carlo_sw(
    model: Literal["archie", "simandoux", "indonesia"],
    params: SwInputParams,
    n_samples: int = 1000,
    seed: int | None = None,
) -> SwCalculationOutput:
    """
    Run Monte Carlo simulation for Sw calculation with uncertainty.

    Args:
        model: Saturation model to use
        params: Input parameters (with optional uncertainty)
        n_samples: Number of Monte Carlo iterations
        seed: Random seed for reproducibility

    Returns:
        SwCalculationOutput with nominal, samples, and statistics
    """
    rng = random.Random(seed)
    samples: list[float] = []
    hold_triggers: list[str] = []

    # Calculate nominal Sw (using mean values)
    rw_val, _ = _extract_value_and_uncertainty(params.rw)
    rt_val, _ = _extract_value_and_uncertainty(params.rt)
    phi_val, _ = _extract_value_and_uncertainty(params.phi)
    vcl_val = 0.0
    rsh_val = None
    if params.vcl is not None:
        vcl_val, _ = _extract_value_and_uncertainty(params.vcl)
    if params.rsh is not None:
        rsh_val, _ = _extract_value_and_uncertainty(params.rsh)

    # Nominal calculation
    if model == "archie":
        nominal_sw = calculate_sw_archie(rw_val, rt_val, phi_val, params.a, params.m, params.n)
    elif model == "simandoux" and rsh_val is not None:
        nominal_sw = calculate_sw_simandoux(
            rw_val, rt_val, phi_val, vcl_val, rsh_val, params.a, params.m, params.n
        )
    elif model == "indonesia" and rsh_val is not None:
        nominal_sw = calculate_sw_indonesia(
            rw_val, rt_val, phi_val, vcl_val, rsh_val, params.a, params.m, params.n
        )
    else:
        # Fallback to Archie
        nominal_sw = calculate_sw_archie(rw_val, rt_val, phi_val, params.a, params.m, params.n)

    # Monte Carlo sampling
    for _ in range(n_samples):
        rw_s = _sample_param(params.rw, rng)
        rt_s = _sample_param(params.rt, rng)
        phi_s = _sample_param(params.phi, rng)

        vcl_s = vcl_val
        rsh_s = rsh_val
        if params.vcl is not None:
            vcl_s = _sample_param(params.vcl, rng)
        if params.rsh is not None:
            rsh_s = _sample_param(params.rsh, rng)

        if model == "archie":
            sw_s = calculate_sw_archie(rw_s, rt_s, phi_s, params.a, params.m, params.n)
        elif model == "simandoux" and rsh_s is not None:
            sw_s = calculate_sw_simandoux(
                rw_s, rt_s, phi_s, vcl_s, rsh_s, params.a, params.m, params.n
            )
        elif model == "indonesia" and rsh_s is not None:
            sw_s = calculate_sw_indonesia(
                rw_s, rt_s, phi_s, vcl_s, rsh_s, params.a, params.m, params.n
            )
        else:
            sw_s = calculate_sw_archie(rw_s, rt_s, phi_s, params.a, params.m, params.n)

        samples.append(sw_s)

    # Calculate statistics
    samples.sort()
    n = len(samples)
    stats = {
        "p10": samples[int(n * 0.10)],
        "p50": samples[int(n * 0.50)],
        "p90": samples[int(n * 0.90)],
        "mean": sum(samples) / n,
        "std": math.sqrt(sum((s - sum(samples) / n) ** 2 for s in samples) / n),
        "min": samples[0],
        "max": samples[-1],
    }

    # Constitutional checks (F2 Truth)
    if nominal_sw > 1.0:
        hold_triggers.append(f"Sw ({nominal_sw:.3f}) > 1.0 — physical impossibility")
    if phi_val > 0.50:
        hold_triggers.append(f"PHI ({phi_val:.3f}) > 0.50 — above physical maximum")

    verdict = "888_HOLD" if hold_triggers else "SEAL"

    return SwCalculationOutput(
        nominal_sw=nominal_sw,
        samples=samples,
        stats=stats,
        hold_triggers=hold_triggers,
        verdict=verdict,
    )

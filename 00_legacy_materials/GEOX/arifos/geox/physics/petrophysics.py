"""
petrophysics.py — GEOX Physics Engine: Saturation Models
═══════════════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI

Implements standard water saturation (Sw) models with Monte Carlo uncertainty.
Reference:
- Archie, G.E. (1942). The electrical resistivity log as an aid in
  determining some reservoir characteristics.
- Simandoux, P. (1963). Dielectric measurements on porous media.
- Poupon, A., & Leveaux, J. (1971). Evaluation of water saturation in
  shaly sands (The Indonesia Equation).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Literal

import numpy as np

from arifos.geox.schemas.petrophysics_schemas import (
    LogQCFlags,
    SwModelAdmissibility,
    PetrophysicsInput,
    PetrophysicsOutput,
    CutoffPolicy,
    CutoffValidationResult,
)

# ═══════════════════════════════════════════════════════════════════════════════
# High-Level Governed Logic
# ═══════════════════════════════════════════════════════════════════════════════


def select_sw_model_logic(qc: LogQCFlags) -> SwModelAdmissibility:
    """
    Select the most admissible Sw model based on Log QC flags (F9 Anti-Hantu).
    """
    well_id = qc.well_id
    reasons = []
    admissible = []
    inadmissible = {}
    requires_hold = False

    # 1. Borehole Quality Constraint
    if qc.borehole_quality == "poor" or qc.washout_fraction > 0.35:
        requires_hold = True
        reasons.append(
            f"Severely degraded borehole (washout={qc.washout_fraction:.0%}). Resistivity measurement compromised."
        )
        recommended = "none"
    else:
        # 2. Shale Volume Constraint
        if qc.vsh_max < 0.15:
            recommended = "archie"
            admissible = ["archie"]
            inadmissible["simandoux"] = [
                "Clean formation: shale parameters (Rsh) may be unreliable/too high."
            ]
            inadmissible["indonesia"] = [
                "Clean formation: shale parameters (Rsh) may be unreliable/too high."
            ]
        else:
            recommended = "simandoux"
            admissible = ["simandoux", "indonesia"]
            inadmissible["archie"] = [
                "Clean sand model applied to shaly interval (F2 Truth violation)."
            ]

    return SwModelAdmissibility(
        well_id=well_id,
        recommended_model=recommended,
        admissible_models=admissible,
        inadmissible_models=inadmissible,
        requires_hold=requires_hold,
        hold_reasons=reasons,
        confidence=0.12 if not requires_hold else 0.03,
    )


def compute_petrophysics_logic(inp: PetrophysicsInput) -> PetrophysicsOutput:
    """
    Compute full petrophysics pipeline using strict governance schemas.
    """
    # Standardize params for core MC engine
    params = {
        "rw": inp.rw_ohm_m,
        "rt": inp.rt_ohm_m,
        "phi": inp.phi_fraction,
        "vcl": inp.vcl_fraction,
        "rsh": inp.rsh_ohm_m,
        "a": inp.archie_a,
        "m": inp.archie_m,
        "n": inp.archie_n,
    }

    # Execute physics kernel
    mc_result = monte_carlo_sw(
        inp.sw_model, params, n_samples=inp.mc_samples if inp.run_monte_carlo else 1
    )

    # Determine ClaimTag (Architectural Non-negotiable)
    # ── Logic ───────────────────────────────────────────────────────────────
    # CLAIM: Archie on clean formation (Vcl < 0.1)
    # PLAUSIBLE: Shaly models on shaly intervals (Vcl < 0.4)
    # HYPOTHESIS: Any model where Vcl > 0.4 or uncertainty > 0.15
    # ────────────────────────────────────────────────────────────────────────
    if inp.sw_model == "archie" and inp.vcl_fraction < 0.1:
        claim = "CLAIM"
    elif inp.vcl_fraction < 0.4:
        claim = "PLAUSIBLE"
    else:
        claim = "HYPOTHESIS"

    # Assemble output
    stats = mc_result.get("stats", {})
    output = PetrophysicsOutput(
        well_id=inp.well_id,
        sw_model_used=inp.sw_model,
        sw_nominal=mc_result["nominal_sw"],
        sw_p10=stats.get("p10"),
        sw_p50=stats.get("p50"),
        sw_p90=stats.get("p90"),
        sw_std=stats.get("std"),
        phi_effective=inp.phi_fraction,
        vcl=inp.vcl_fraction,
        bvw=mc_result["nominal_sw"] * inp.phi_fraction,
        uncertainty=0.12 if inp.run_monte_carlo else 0.15,
        hold_triggers=mc_result.get("hold_triggers", []),
        claim_tag=claim,
    )

    return output


def validate_cutoffs_logic(out: PetrophysicsOutput, policy: CutoffPolicy) -> CutoffValidationResult:
    """
    Apply cutoff policy to petrophysical results (F1 Amanah).
    """
    phi_pass = out.phi_effective >= policy.phi_cutoff
    sw_pass = out.sw_nominal < policy.sw_cutoff
    vcl_pass = out.vcl <= policy.vcl_cutoff

    is_net_res = phi_pass and vcl_pass
    is_net_pay = is_net_res and sw_pass

    violations = []
    if not phi_pass:
        violations.append(f"PHIe {out.phi_effective:.3f} < cutoff {policy.phi_cutoff:.3f}")
    if not vcl_pass:
        violations.append(f"Vcl {out.vcl:.3f} > cutoff {policy.vcl_cutoff:.3f}")
    if is_net_res and not sw_pass:
        violations.append(f"Sw {out.sw_nominal:.3f} > cutoff {policy.sw_cutoff:.3f}")

    return CutoffValidationResult(
        well_id=out.well_id,
        policy_id=policy.policy_id,
        is_net_reservoir=is_net_res,
        is_net_pay=is_net_pay,
        phi_pass=phi_pass,
        sw_pass=sw_pass,
        vcl_pass=vcl_pass,
        phi_tested=out.phi_effective,
        sw_tested=out.sw_nominal,
        vcl_tested=out.vcl,
        violations=violations,
        requires_hold=out.requires_hold,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Core Physics Kernels
# ═══════════════════════════════════════════════════════════════════════════════


def archie_sw(
    rw: float, rt: float, phi: float, a: float = 1.0, m: float = 2.0, n: float = 2.0
) -> float:
    """
    Archie (1942) Water Saturation Model for clean formations.

    Equation: Sw = ( (a * Rw) / (phi^m * Rt) )^(1/n)
    """
    if np.any(np.asarray(phi) <= 0) or np.any(np.asarray(rt) <= 0) or np.any(np.asarray(rw) <= 0):
        return 1.0

    # Floor check (F13 Sovereign) - will be handled by the caller
    sw = ((a * rw) / ((phi**m) * rt)) ** (1 / n)
    return sw


def simandoux_sw(
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
    Simandoux (1963) Water Saturation Model for dispersed shaly sands.

    Simplified form (assumes n=2 for the discriminant path):
    Sw = (a*Rw / 2*phi^m) * [sqrt((Vcl/Rsh)^2 + 4*phi^m / (a*Rw*Rt)) - Vcl/Rsh]
    """
    if (
        np.any(np.asarray(phi) <= 0)
        or np.any(np.asarray(rt) <= 0)
        or np.any(np.asarray(rw) <= 0)
        or np.any(np.asarray(rsh) <= 0)
    ):
        return 1.0

    if vcl < 0.01:  # Use Archie if very clean
        return archie_sw(rw, rt, phi, a, m, n)

    term_a = (phi**m) / (a * rw)
    term_b = vcl / rsh
    term_c = 1 / rt

    # Sw quadratic solution part
    sw = (1 / (2 * term_a)) * (np.sqrt(term_b**2 + 4 * term_a * term_c) - term_b)

    # Adjust for n != 2 if needed (simplified power adjustment)
    if n != 2.0:
        sw = sw ** (2 / n)

    return sw


def indonesia_sw(
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
    Indonesia (Poupon & Leveaux, 1971) Water Saturation Model for shaly sands.

    Equation: 1/sqrt(Rt) = (Vcl^(1-Vcl/2)/sqrt(Rsh) + phi^(m/2)/sqrt(a*Rw)) * Sw^(n/2)
    """
    if (
        np.any(np.asarray(phi) <= 0)
        or np.any(np.asarray(rt) <= 0)
        or np.any(np.asarray(rw) <= 0)
        or np.any(np.asarray(rsh) <= 0)
    ):
        return 1.0

    term_shale = (vcl ** (1 - (vcl / 2))) / np.sqrt(rsh)
    term_sand = (phi ** (m / 2)) / np.sqrt(a * rw)

    res = 1.0 / (np.sqrt(rt) * (term_shale + term_sand))
    sw = res ** (2 / n)

    return sw


# ═══════════════════════════════════════════════════════════════════════════════
# Uncertainty Engine
# ═══════════════════════════════════════════════════════════════════════════════


def monte_carlo_sw(
    model_name: Literal["archie", "simandoux", "indonesia"],
    params: dict[str, Any],
    n_samples: int = 1000,
) -> dict[str, Any]:
    """
    Monte Carlo simulation for saturation uncertainty (F7 Humility).

    Args:
        model_name: The model to use.
        params: Map of param name to value (float) or (mean: float, std: float).
        n_samples: Number of MC iterations.
    """
    # Map models
    models: dict[str, Callable[..., float]] = {
        "archie": archie_sw,
        "simandoux": simandoux_sw,
        "indonesia": indonesia_sw,
    }
    func = models[model_name]

    # Generate samples
    sampled_params = {}
    for key, val in params.items():
        if isinstance(val, (list, tuple)) and len(val) == 2:
            mean, std = val
            samples = np.random.normal(mean, std, n_samples)
            # Clip physical bounds
            if key == "phi":
                samples = np.clip(samples, 0.001, 0.45)
            if key == "vcl":
                samples = np.clip(samples, 0, 1.0)
            if key in ["rw", "rt", "rsh"]:
                samples = np.clip(samples, 0.001, 10000)
            sampled_params[key] = samples
        elif val is not None:
            sampled_params[key] = np.full(n_samples, val)
        else:
            # For optional params like Rsh if model doesn't need it
            sampled_params[key] = np.full(n_samples, 0.0)

    # Run simulation
    sw_results = func(**sampled_params)

    # Clip Sw to physical bounds [0, 1]
    sw_results = np.clip(sw_results, 0, 1.1)  # Allow slight overshot for 888_HOLD detection

    # Statistics
    stats = {
        "mean": float(np.mean(sw_results)),
        "std": float(np.std(sw_results)),
        "p10": float(np.percentile(sw_results, 10)),
        "p50": float(np.percentile(sw_results, 50)),
        "p90": float(np.percentile(sw_results, 90)),
    }

    # Governance Checks (F13 Sovereign)
    hold_triggers = []
    if np.any(sw_results > 1.0):
        hold_triggers.append("Sw > 1.0 detection (Physical impossibility)")

    phi_val = params.get("phi", 0)
    if isinstance(phi_val, (list, tuple)):
        phi_check = phi_val[0]
    else:
        phi_check = phi_val

    if phi_check > 0.45:
        hold_triggers.append("Porosity > 0.45 (OutOfRange)")

    return {
        "model": model_name,
        "nominal_sw": stats["p50"],
        "stats": stats,
        "hold_triggers": hold_triggers,
        "verdict": "SEAL" if not hold_triggers else "888_HOLD",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

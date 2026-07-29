"""
ER1–ER5 — scalar seeds from trauma-agentic-orthogonal.md.

These are proportionality / kinetics / band constraints — geometric *seeds*,
not full tensorial geometry.

  ER1: H_actual = H_event × (1 + B)
  ER2: cascade depth ≥ 3 (directional propagation requirement)
  ER3: harm ∝ power_differential × consent_deficit
  ER4: M(t) = 1 - e^(-λt) naming metabolization
  ER5: Ω₀ ∈ [0.03, 0.05] Gödel band
"""

from __future__ import annotations

import math
from typing import Any


def er1_betrayal_ratio(*, h_event: float, betrayal_factor: float) -> dict[str, Any]:
    """ER1 — Betrayal amplifies event harm.

    B ≥ 0. h_event ≥ 0.
    """
    h = max(0.0, float(h_event))
    b = max(0.0, float(betrayal_factor))
    h_actual = h * (1.0 + b)
    return {
        "er": "ER1",
        "formula": "H_actual = H_event × (1 + B)",
        "h_event": h,
        "betrayal_factor": b,
        "h_actual": h_actual,
        "geometric_nature": "scalar_multiplication",
        "not_yet": "coordinate_system",
    }


def er2_cascade_depth(*, steps: list[Any] | None) -> dict[str, Any]:
    """ER2 — Cascade principle: require ≥ 3 downstream steps."""
    n = len(steps or [])
    return {
        "er": "ER2",
        "formula": "cascade_steps ≥ 3",
        "step_count": n,
        "satisfied": n >= 3,
        "geometric_nature": "directional_propagation",
        "not_yet": "vector_field",
        "hold_if_unsatisfied": n < 3,
    }


def er3_power_consent_harm(
    *,
    power_differential: float,
    consent_deficit: float,
) -> dict[str, Any]:
    """ER3 — Harm potential ∝ Power Differential × Consent Deficit.

    power_differential ∈ [0, 1], consent_deficit ∈ [0, 1]
    (consent_deficit = 1 - consent when consent ∈ [0,1])
    """
    p = max(0.0, min(1.0, float(power_differential)))
    c = max(0.0, min(1.0, float(consent_deficit)))
    harm = p * c
    return {
        "er": "ER3",
        "formula": "harm ∝ Power × ConsentDeficit",
        "power_differential": p,
        "consent_deficit": c,
        "harm_potential": harm,
        "geometric_nature": "bilinear_product",
        "not_yet": "manifold_curvature",
    }


def er4_naming_metabolization(*, t: float, lambda_rate: float = 0.1) -> dict[str, Any]:
    """ER4 — M(t) = 1 - e^(-λt) metabolization of naming/truth.

    t ≥ 0, λ > 0. M → 1 as t → ∞ (asymptotic full naming, never instant).
    """
    tt = max(0.0, float(t))
    lam = max(1e-9, float(lambda_rate))
    m = 1.0 - math.exp(-lam * tt)
    return {
        "er": "ER4",
        "formula": "M(t) = 1 - e^(-λt)",
        "t": tt,
        "lambda": lam,
        "M": m,
        "geometric_nature": "first_order_kinetics",
        "not_yet": "spatial_embedding",
    }


def er5_omega_zero_band(*, omega_zero: float) -> dict[str, Any]:
    """ER5 — Gödel constraint: Ω₀ ∈ [0.03, 0.05]."""
    o = float(omega_zero)
    lo, hi = 0.03, 0.05
    in_band = lo <= o <= hi
    return {
        "er": "ER5",
        "formula": "Ω₀ ∈ [0.03, 0.05]",
        "omega_zero": o,
        "in_band": in_band,
        "band": [lo, hi],
        "geometric_nature": "epistemic_bound",
        "not_yet": "topology",
        "f7_hold_if_out_of_band": not in_band,
    }

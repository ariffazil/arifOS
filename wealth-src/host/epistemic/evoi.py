"""
Expected Value of Information (EVOI) Calculator Stub.

EVOI = E[V | with_info] - E[V | without_info]

Before drilling, compute whether acquiring more seismic is worth it.
Sometimes the best decision is: Do not drill. Acquire data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class EVOIResult:
    evoi_musd: float
    drill_recommendation: str
    pnpv_with_info: float
    pnpv_without_info: float
    expected_value_with_info: float
    expected_value_without_info: float
    well_cost_musd: float
    p50_value_musd: float
    prior_pos: float
    posterior_pos: float
    info_cost_musd: float
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "evoi_musd": self.evoi_musd,
            "drill_recommendation": self.drill_recommendation,
            "pnpv_with_info": self.pnpv_with_info,
            "pnpv_without_info": self.pnpv_without_info,
            "expected_value_with_info": self.expected_value_with_info,
            "expected_value_without_info": self.expected_value_without_info,
            "well_cost_musd": self.well_cost_musd,
            "p50_value_musd": self.p50_value_musd,
            "prior_pos": self.prior_pos,
            "posterior_pos": self.posterior_pos,
            "info_cost_musd": self.info_cost_musd,
            "confidence": self.confidence,
        }


def compute_evoi(
    prior_pos: float,
    posterior_pos: float,
    well_cost_musd: float,
    p50_value_musd: float,
    info_cost_musd: float = 5.0,
    discount_rate: float = 0.10,
    risk_multiplier: float = 1.0,
) -> Dict[str, Any]:
    """
    Expected Value of Information.

    EVOI = E[V | with_info] - E[V | without_info]

    Args:
        prior_pos: Prior probability of success (0-1)
        posterior_pos: Posterior probability after new information (0-1)
        well_cost_musd: Cost of drilling the well in MUS$ (positive value)
        p50_value_musd: P50 value of the discovery in MUS$ (positive value)
        info_cost_musd: Cost of acquiring new information in MUS$ (default 5.0)
        discount_rate: Annual discount rate (default 0.10)
        risk_multiplier: Multiplier for tail risk adjustment (default 1.0)

    Returns:
        Dict with EVOI result and drill recommendation
    """
    pnpv_without_info = _compute_pnpv(prior_pos, well_cost_musd, p50_value_musd, discount_rate)
    pnpv_with_info = _compute_pnpv(posterior_pos, well_cost_musd, p50_value_musd, discount_rate)

    expected_value_without_info = pnpv_without_info
    expected_value_with_info = pnpv_with_info - info_cost_musd

    evoi = expected_value_with_info - expected_value_without_info

    if evoi < 0:
        drill_recommendation = "ACQUIRE_DATA — EVOI negative, information cost exceeds value gain"
        confidence = "LOW"
    elif evoi < info_cost_musd * 0.5:
        drill_recommendation = "HOLD — EVOI marginal, acquire data before committing"
        confidence = "MEDIUM"
    else:
        drill_recommendation = "PROCEED — EVOI positive, value of information justifies decision"
        confidence = "HIGH"

    if prior_pos < 0.1:
        drill_recommendation = "DO_NOT_DRILL — prior PoS too low"
        confidence = "HIGH"
    elif posterior_pos > 0.9 and expected_value_with_info < 0:
        drill_recommendation = "DO_NOT_DRILL — even with good news, project not economic"
        confidence = "HIGH"

    result = EVOIResult(
        evoi_musd=evoi,
        drill_recommendation=drill_recommendation,
        pnpv_with_info=pnpv_with_info,
        pnpv_without_info=pnpv_without_info,
        expected_value_with_info=expected_value_with_info,
        expected_value_without_info=expected_value_without_info,
        well_cost_musd=well_cost_musd,
        p50_value_musd=p50_value_musd,
        prior_pos=prior_pos,
        posterior_pos=posterior_pos,
        info_cost_musd=info_cost_musd,
        confidence=confidence,
    )

    return result.to_dict()


def _compute_pnpv(
    pos: float,
    well_cost_musd: float,
    p50_value_musd: float,
    discount_rate: float,
) -> float:
    """
    Compute probability-weighted NPV.

    PNPV = PoS * (P50_value - well_cost) - (1 - PoS) * well_cost

    Simplified model: if we don't succeed, we lose the well cost.
    If we do succeed, we get P50_value minus well cost.
    """
    success_value = p50_value_musd - well_cost_musd
    failure_value = -well_cost_musd

    expected_value = pos * success_value + (1 - pos) * failure_value
    return expected_value


def compute_evoi_monte_carlo(
    prior_pos_samples: list[float],
    posterior_pos_samples: list[float],
    well_cost_musd: float,
    p50_value_musd: float,
    info_cost_musd: float = 5.0,
) -> Dict[str, Any]:
    """
    Monte Carlo EVOI computation.

    Takes samples from prior and posterior distributions to compute
    distributional EVOI rather than point estimates.

    Args:
        prior_pos_samples: List of prior PoS samples
        posterior_pos_samples: List of posterior PoS samples
        well_cost_musd: Cost of drilling
        p50_value_musd: P50 discovery value
        info_cost_musd: Cost of new information

    Returns:
        Dict with distributional EVOI results including P10/P50/P90
    """
    if len(prior_pos_samples) != len(posterior_pos_samples):
        return {
            "error": "prior_pos_samples and posterior_pos_samples must have same length",
            "status": "INVALID",
        }

    evoi_samples: list[float] = []

    for prior_pos, posterior_pos in zip(prior_pos_samples, posterior_pos_samples):
        pnpv_with = _compute_pnpv(posterior_pos, well_cost_musd, p50_value_musd, 0.0)
        pnpv_without = _compute_pnpv(prior_pos, well_cost_musd, p50_value_musd, 0.0)

        evoi_samples.append(pnpv_with - info_cost_musd - pnpv_without)

    evoi_samples_sorted = sorted(evoi_samples)
    n = len(evoi_samples_sorted)

    p10_idx = int(n * 0.10)
    p50_idx = int(n * 0.50)
    p90_idx = int(n * 0.90)

    return {
        "evoi_p10": evoi_samples_sorted[p10_idx],
        "evoi_p50": evoi_samples_sorted[p50_idx],
        "evoi_p90": evoi_samples_sorted[p90_idx],
        "evoi_mean": sum(evoi_samples) / n,
        "samples": n,
        "drill_recommendation": _recommend_from_dist(
            evoi_samples_sorted[p10_idx],
            evoi_samples_sorted[p50_idx],
            evoi_samples_sorted[p90_idx],
        ),
        "status": "PASS",
    }


def _recommend_from_dist(p10: float, p50: float, p90: float) -> str:
    if p90 < 0:
        return "DO_NOT_DRILL — even P90 EVOI negative"
    elif p50 < 0:
        return "HOLD — P50 EVOI negative, P90 marginal"
    elif p10 < 0:
        return "ACQUIRE_DATA — P10 negative but upside exists"
    else:
        return "PROCEED — EVOI positive across distribution"

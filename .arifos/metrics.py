#!/usr/bin/env python3
"""
Metrics — arifOS Autoresearch
Shared metrics computation for all agents.

Usage:
    from metrics import compute_delta_s, compute_psi, compute_npv
"""

import math
from dataclasses import dataclass
from typing import Optional

ARIFOS_ROOT = None


def set_root(root_path):
    global ARIFOS_ROOT
    ARIFOS_ROOT = root_path


TRUTH_HALF_LIFE = 72 * 3600
DISCOUNT_RATE = 0.10


@dataclass
class TemporalTruth:
    truth_remaining: float
    state_change_prob: float
    half_life_seconds: float


def compute_truth_decay(
    elapsed_seconds: float, half_life: float = TRUTH_HALF_LIFE
) -> TemporalTruth:
    if half_life <= 0:
        half_life = TRUTH_HALF_LIFE
    truth_remaining = math.pow(0.5, elapsed_seconds / half_life)
    state_change_prob = 1.0 - truth_remaining
    return TemporalTruth(
        truth_remaining=truth_remaining,
        state_change_prob=state_change_prob,
        half_life_seconds=half_life,
    )


def compute_delta_s(
    clarity_delta: float,
    complexity_delta: float,
    duplication_delta: float,
    drift_delta: float,
) -> float:
    return clarity_delta + complexity_delta + duplication_delta + drift_delta


def compute_psi(
    stability_index: float,
    truth_remaining: float,
    entropy_reduction: float,
) -> float:
    psi = (stability_index * 0.4) + (truth_remaining * 0.3) + (entropy_reduction * 0.3)
    return min(psi, 1.0)


def compute_temporal_npv(
    delta_s: float,
    elapsed_seconds: float,
    discount_rate: float = DISCOUNT_RATE,
    half_life: float = TRUTH_HALF_LIFE,
) -> float:
    truth = compute_truth_decay(elapsed_seconds, half_life)
    annual_elapsed = elapsed_seconds / (365.25 * 24 * 3600)
    discount_factor = math.pow(1 + discount_rate, -annual_elapsed)
    temporal_value = delta_s * truth.truth_remaining
    npv = temporal_value * discount_factor
    return npv


def compute_apex_g(
    accuracy: float,
    penetration: float,
    coherence: float,
    stability: float,
    delta_s: float,
) -> float:
    energy_squared = stability * stability
    product = accuracy * penetration * coherence * energy_squared
    g = product * abs(delta_s)
    return g


def check_constitutional_floors(
    g_dagger: float,
    npv: float,
    passes_stability: bool,
    threshold: float = 0.10,
) -> tuple[bool, list]:
    floors_passed = []
    violations = []

    if g_dagger >= threshold:
        floors_passed.append(f"G†={g_dagger:.3f} ≥ {threshold}")
    else:
        violations.append(f"G†={g_dagger:.3f} < {threshold}")

    if npv >= 0:
        floors_passed.append(f"NPV={npv:.4f} ≥ 0")
    else:
        violations.append(f"NPV={npv:.4f} < 0 (VOID)")

    if passes_stability:
        floors_passed.append("Stability: PASS")
    else:
        violations.append("Stability: FAIL")

    verdict = len(violations) == 0
    return verdict, violations


def format_metrics_summary(
    delta_s: float,
    psi: float,
    g_dagger: float,
    npv: float,
    passes: bool,
) -> str:
    status = "✅ ACCEPT" if passes else "❌ REJECT"
    return f"ΔS={delta_s:+.4f} | Ψ={psi:.3f} | G†={g_dagger:.3f} | NPV={npv:+.4f} | {status}"

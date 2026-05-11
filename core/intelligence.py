from __future__ import annotations


def compute_w3(human_score: float, ai_score: float, earth_score: float) -> float:
    return round((human_score + ai_score + earth_score) / 3.0, 3)


def calculate_omega_zero(samples: list[float]) -> float:
    if not samples:
        return 0.04
    return round(sum(samples) / len(samples), 3)

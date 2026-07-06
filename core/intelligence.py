from __future__ import annotations


def compute_w3(human_score: float, ai_score: float, earth_score: float) -> float:
    """[MEMBRANE_DEPRECATED] W³ = ∛(H × AI × Ext) — Nash (1950) geometric mean.

    This function is KEPT as fallback/test-only. It must NOT be called
    from live kernel paths. A-FORGE owns W3 computation.
    Canonical copy: /root/A-FORGE/src/domain/apex/compute_w3.py

    Phase 2: remove after all A-FORGE ingress paths are proven.
    See: /root/A-FORGE/forge_work/2026-07-06/MEMBRANE_ARCHITECTURE.md
    """
    if human_score <= 0 or ai_score <= 0 or earth_score <= 0:
        return 0.0
    return round((human_score * ai_score * earth_score) ** (1 / 3), 3)


def calculate_omega_zero(samples: list[float]) -> float:
    if not samples:
        return 0.04
    return round(sum(samples) / len(samples), 3)

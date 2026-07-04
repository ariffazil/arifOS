"""
arifosmcp/core/malu_score.py — Multiplicative moral-accountability scoring.

Forged: 2026-06-30 by Hermes ASI.
Status: DRAFT / STAGED.  Pure functions, no live wiring.

Provides the CMAG ``floor_product`` primitive:
    floor_product = ∏(1 - violation_share_i)  across F1..F13
    malu_index    = 1 - floor_product

A saturated floor (share_i >= 1) drives the product to 0 and malu_index to 1.
This makes one F01/F09/F12-class breach catastrophic, as required.

Two authority surfaces are exposed:
1. ``additive_malu_index`` — legacy sum-of-deltas, the current default.
2. ``multiplicative_malu_index`` — floor_product transformation.

Switching live authority to multiplicative requires F13 ratification.
Until then, callers may compute it for simulation/reporting only.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from arifosmcp.runtime.fiqh_of_floors import FiqhTier, FLOOR_TIER


# ──────────────────────────────────────────────────────────────────────
# Tunables
# ──────────────────────────────────────────────────────────────────────

# Per-floor share ceiling: how many weighted points fully saturate a floor.
# WAJIB/HARAM floors saturate faster because their blast radius is larger.
FLOOR_CEILING: dict[str, float] = {
    "F01": 15.0,   # AMANAH — irreversible without ack
    "F02": 15.0,   # TRUTH — false certainty
    "F03": 10.0,   # WITNESS — tri-witness gaps
    "F04": 15.0,   # CLARITY — entropy inflation
    "F05": 10.0,   # PEACE — escalation
    "F06": 15.0,   # EMPATHY — dignity
    "F07": 10.0,   # HUMILITY — omega band
    "F08": 10.0,   # GENIUS — system health
    "F09": 10.0,   # ANTIHANTU — consciousness claim
    "F10": 15.0,   # ONTOLOGY — soul claim
    "F11": 15.0,   # AUTH — identity
    "F12": 10.0,   # INJECTION — prompt attack
    "F13": 15.0,   # SOVEREIGN — veto
}

# Weight of each tiered violation when contributing to a floor's share.
TIER_VIOLATION_WEIGHT: dict[FiqhTier, float] = {
    FiqhTier.HARUS: 0.0,
    FiqhTier.SUNAT: 1.0,
    FiqhTier.MAKRUH: 2.5,
    FiqhTier.WAJIB: 5.0,
    FiqhTier.HARAM: 10.0,
}

# Authority switch threshold: when the *additive* index crosses this,
# the multiplicative surface becomes the binding score IF enabled.
MULTIPLICATIVE_AUTHORITY_THRESHOLD = 0.30


# ──────────────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FloorScore:
    """Per-floor accountability decomposition."""

    floor_id: str
    tier: FiqhTier
    raw_delta: float          # weighted violation points
    ceiling: float
    share: float              # raw_delta / ceiling, clamped to [0, 1]
    contribution: float       # 1 - share

    def to_dict(self) -> dict[str, Any]:
        return {
            "floor_id": self.floor_id,
            "tier": self.tier.value,
            "raw_delta": self.raw_delta,
            "ceiling": self.ceiling,
            "share": self.share,
            "contribution": self.contribution,
        }


@dataclass(frozen=True)
class MaluScore:
    """Full accountability score across all 13 floors."""

    additive_index: float
    multiplicative_index: float
    floor_product: float
    floors: dict[str, FloorScore]
    multiplicative_authority: bool  # True iff F13 has enabled it

    def to_dict(self) -> dict[str, Any]:
        return {
            "additive_index": self.additive_index,
            "multiplicative_index": self.multiplicative_index,
            "floor_product": self.floor_product,
            "multiplicative_authority": self.multiplicative_authority,
            "floors": {k: v.to_dict() for k, v in self.floors.items()},
        }

    @property
    def binding_index(self) -> float:
        """The index that currently governs authority bands."""
        if self.multiplicative_authority:
            return self.multiplicative_index
        return self.additive_index


# ──────────────────────────────────────────────────────────────────────
# Primitives
# ──────────────────────────────────────────────────────────────────────


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def floor_product(violations: dict[str, float], *, clamp: bool = True) -> float:
    """
    CMAG primitive: ∏(1 - violation_share_i) across F1..F13.

    ``violations`` maps floor_id -> weighted violation points.
    Each floor's share is violations[floor] / FLOOR_CEILING[floor].
    Missing floors are treated as clean (share = 0, contribution = 1).

    Returns a value in (0, 1].  A single saturated floor yields 0.
    """
    product = 1.0
    for floor_id in FLOOR_CEILING:
        raw = violations.get(floor_id, 0.0)
        if raw <= 0.0:
            continue
        ceiling = FLOOR_CEILING[floor_id]
        share = raw / ceiling if ceiling > 0 else 1.0
        if clamp:
            share = _clamp(share)
        product *= 1.0 - share
    return _clamp(product) if clamp else product


def compute_floor_scores(
    violations: dict[str, float],
    *,
    clamp: bool = True,
) -> dict[str, FloorScore]:
    """Return per-floor score records for inspection/receipts."""
    floors: dict[str, FloorScore] = {}
    for floor_id in FLOOR_CEILING:
        tier = FLOOR_TIER.get(floor_id, FiqhTier.HARUS)
        raw = violations.get(floor_id, 0.0)
        ceiling = FLOOR_CEILING[floor_id]
        share = raw / ceiling if ceiling > 0 else 1.0
        if clamp:
            share = _clamp(share)
        floors[floor_id] = FloorScore(
            floor_id=floor_id,
            tier=tier,
            raw_delta=raw,
            ceiling=ceiling,
            share=share,
            contribution=1.0 - share,
        )
    return floors


def additive_malu_index(
    violations: dict[str, float],
    *,
    normalize: bool = True,
) -> float:
    """
    Legacy additive score.

    Sums weighted violation points across all floors.
    If normalize=True, divides by the sum of ceilings so the result
    sits on the same [0, 1] scale as the multiplicative score.
    """
    total_raw = sum(violations.get(f, 0.0) for f in FLOOR_CEILING)
    if not normalize:
        return total_raw
    total_ceiling = sum(FLOOR_CEILING.values())
    return _clamp(total_raw / total_ceiling) if total_ceiling > 0 else 0.0


def multiplicative_malu_index(
    violations: dict[str, float],
    *,
    clamp: bool = True,
) -> tuple[float, float]:
    """
    Returns (floor_product, malu_index) where malu_index = 1 - floor_product.
    """
    fp = floor_product(violations, clamp=clamp)
    return fp, 1.0 - fp


def score_malu(
    violations: dict[str, float],
    *,
    multiplicative_authority: bool = False,
    clamp: bool = True,
) -> MaluScore:
    """
    Compute both additive and multiplicative scores.

    ``multiplicative_authority`` MUST remain False until F13 ratifies
    the switch.  This flag exists so the kernel can flip it atomically
    with a sovereign signature.
    """
    additive = additive_malu_index(violations, normalize=True)
    fp, mult_index = multiplicative_malu_index(violations, clamp=clamp)
    floors = compute_floor_scores(violations, clamp=clamp)

    # Auto-enable multiplicative authority only if already enabled
    # by the kernel AND the additive index has crossed the threshold.
    # The threshold check is secondary; the flag itself is F13-gated.
    effective_mult_authority = (
        multiplicative_authority and additive >= MULTIPLICATIVE_AUTHORITY_THRESHOLD
    )

    return MaluScore(
        additive_index=additive,
        multiplicative_index=mult_index,
        floor_product=fp,
        floors=floors,
        multiplicative_authority=effective_mult_authority,
    )


# ──────────────────────────────────────────────────────────────────────
# Helpers for fiqh verdicts
# ──────────────────────────────────────────────────────────────────────


def violations_from_tier_counts(
    tier_counts: dict[str, dict[FiqhTier, int]],
) -> dict[str, float]:
    """
    Convert per-floor tier counts into weighted violation points.

    ``tier_counts`` shape: {floor_id: {FiqhTier.WAJIB: 2, FiqhTier.SUNAT: 1, ...}}
    """
    violations: dict[str, float] = {}
    for floor_id, counts in tier_counts.items():
        total = 0.0
        for tier, count in counts.items():
            total += TIER_VIOLATION_WEIGHT.get(tier, 0.0) * max(0, count)
        if total > 0.0:
            violations[floor_id] = total
    return violations


def score_from_tier_counts(
    tier_counts: dict[str, dict[FiqhTier, int]],
    *,
    multiplicative_authority: bool = False,
) -> MaluScore:
    """Convenience: score directly from per-floor tier counts."""
    return score_malu(
        violations_from_tier_counts(tier_counts),
        multiplicative_authority=multiplicative_authority,
    )


__all__ = [
    "FLOOR_CEILING",
    "TIER_VIOLATION_WEIGHT",
    "MULTIPLICATIVE_AUTHORITY_THRESHOLD",
    "FloorScore",
    "MaluScore",
    "floor_product",
    "compute_floor_scores",
    "additive_malu_index",
    "multiplicative_malu_index",
    "score_malu",
    "violations_from_tier_counts",
    "score_from_tier_counts",
]

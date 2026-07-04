"""
risk.py — Risk assessment types and classifiers.

Risk = blast_radius × reversibility × human_ack.

APEX THEORY EMBEDDING (2026-06-28):
- Landauer cost: every irreversible bit erase costs k_B * T * ln(2) joules.
  Embed this into blast-radius / reversibility classification so that
  thermodynamic cost is a first-class signal alongside blast radius.
- Mesa-optimization detection: high reversibility IRREVERSIBLE + EXTERNAL
  blast radius = potential objective misalignment (agent optimizing for
  proxy instead of sovereign intent).
"""

from __future__ import annotations

from enum import Enum
from math import log


# ─── APEX: Landauer Thermodynamic Cost Constants ────────────────────────────
K_BOLTZMANN: float = 1.380649e-23  # J/K — Boltzmann constant
ROOM_TEMPERATURE_K: float = 293.15  # ~20°C in Kelvin
LANDALBER_BITS_PER_JOULE: float = 1.0 / (K_BOLTZMANN * ROOM_TEMPERATURE_K * log(2))
# ≈ 2.47e16 bits/Joule at room temperature — Landauer limit


def landauer_cost_kT(bits_erased: int) -> float:
    """
    APEX THEORY: Landauer cost in kT units.

    kT ≈ 4.05e-21 J at 293K.
    Every irreversible bit erase releases this much heat.

    Use for:
    - Scoring reversibility: high bits_erased = high thermodynamic cost
    - Detecting mesa-optimization: agent burning excessive bits for
      a proxy objective vs the sovereign's stated intent
    """
    if bits_erased <= 0:
        return 0.0
    # Landauer: kT * ln(2) per bit
    return bits_erased * K_BOLTZMANN * ROOM_TEMPERATURE_K * log(2)


def landauer_cost_joules(bits_erased: int) -> float:
    """APEX THEORY: Landauer cost in joules. Human-readable version."""
    return bits_erased / LANDALBER_BITS_PER_JOULE


# ─── Reversibility → bits-erased heuristic ─────────────────────────────────
# Rough mapping: how many bits are effectively "erased" when an action
# of each reversibility class is taken and cannot be undone.
_REVERSIBILITY_BITS: dict[str, int] = {
    "REVERSIBLE": 0,  # no bits erased — state can be restored
    "PARTIAL": 32,  # partial state loss — some bits erased
    "IRREVERSIBLE": 256,  # full state destruction — maximum bits erased
}


def landauer_cost_for_action(reversibility: str, blast_radius: str) -> float:
    """
    APEX THEORY: Combined Landauer thermodynamic cost for an action.

    Combines reversibility (bits erased) with blast radius (scope multiplier).
    High blast radius + irreversible = potential mesa-optimization signal
    (agent spending enormous thermodynamic resource on a proxy objective
    rather than the sovereign's declared intent).
    """
    base_bits = _REVERSIBILITY_BITS.get(reversibility, 0)

    # Blast radius scope multiplier
    scope_multiplier: dict[str, float] = {
        "NONE": 1.0,
        "LOCAL": 1.5,
        "SESSION": 3.0,
        "FEDERATION": 10.0,
        "EXTERNAL": 32.0,
    }
    multiplier = scope_multiplier.get(blast_radius, 1.0)
    effective_bits = int(base_bits * multiplier)

    return landauer_cost_joules(effective_bits)


# ─── APEX: Mesa-Detector Signal ─────────────────────────────────────────────
# High thermodynamic cost + high blast radius + external scope
# = possible objective misalignment (mesa-optimization).
# This is a SIGNAL, not a verdict — pass to arif_judge.


def mesa_optimization_signal(reversibility: str, blast_radius: str) -> dict:
    """
    APEX THEORY: Mesa-optimization detection signal.

    Returns a signal dict when thermodynamic cost is high enough to
    suggest an agent may be optimizing for a proxy objective rather
    than the sovereign's stated intent.

    Signal thresholds:
    - irreversibility: reversibility == IRREVERSIBLE
    - scope: blast_radius in (FEDERATION, EXTERNAL)
    - cost: landauer cost > 1e-12 joules (approx. energy of one human thought)
    """
    cost_joules = landauer_cost_for_action(reversibility, blast_radius)
    is_irreversible = reversibility == "IRREVERSIBLE"
    is_federation_or_external = blast_radius in ("FEDERATION", "EXTERNAL")
    cost_threshold_joules = 1e-12  # ~energy of one neural spike
    is_mesa_signal = (
        is_irreversible
        and is_federation_or_external
        # APEX: flag if cost > 1e-19 J — scales with the smallest
        # biologically meaningful compute event (~1 ATP hydrolysis)
        and cost_joules > 1e-19
    )
    return {
        "mesa_signal": is_mesa_signal,
        "landauer_cost_joules": cost_joules,
        "is_irreversible": is_irreversible,
        "is_high_scope": is_federation_or_external,
        "cost_threshold_joules": cost_threshold_joules,
        "epistemic_label": "APEX-MESA-DETECT",
        # APEX contrast: always label uncertainty explicitly
        "confidence": 0.75,  # hard cap per F7 HUMILITY
        "confidence_label": "DER",  # this is derived, not observed
    }


class BlastRadius(str, Enum):
    """How far an action's effects propagate."""

    NONE = "NONE"
    LOCAL = "LOCAL"
    SESSION = "SESSION"
    FEDERATION = "FEDERATION"
    EXTERNAL = "EXTERNAL"


class Reversibility(str, Enum):
    """Whether an action can be undone."""

    REVERSIBLE = "REVERSIBLE"
    PARTIAL = "PARTIAL"
    IRREVERSIBLE = "IRREVERSIBLE"


# Actions that cannot be undone
IRREVERSIBLE_ACTIONS: frozenset[str] = frozenset(
    {
        "DEPLOY",
        "PUBLISH",
        "DELETE",
        "SPEND",
        "SIGN",
        "GRANT_ACCESS",
        "CREDENTIAL_CHANGE",
        "CONSTITUTION_CHANGE",
    }
)


# Actions that reach outside local scope
EXTERNAL_ACTIONS: frozenset[str] = frozenset(
    {
        "MUTATE_EXTERNAL",
        "DEPLOY",
        "PUBLISH",
        "SPEND",
        "GRANT_ACCESS",
    }
)


def classify_blast_radius(action_class: str) -> BlastRadius:
    """Heuristic blast-radius classification for an action class."""
    if action_class in EXTERNAL_ACTIONS:
        return BlastRadius.EXTERNAL
    if action_class in ("MUTATE_LOCAL", "MUTATE_EXTERNAL"):
        return BlastRadius.LOCAL
    if action_class in ("COMPUTE", "PROPOSE"):
        return BlastRadius.SESSION
    return BlastRadius.NONE


def classify_reversibility(action_class: str) -> Reversibility:
    """Heuristic reversibility classification for an action class."""
    if action_class in IRREVERSIBLE_ACTIONS:
        return Reversibility.IRREVERSIBLE
    if action_class in ("MUTATE_LOCAL", "MUTATE_EXTERNAL"):
        return Reversibility.PARTIAL
    return Reversibility.REVERSIBLE


def mesa_detect(action_class: str, blast_radius: BlastRadius) -> dict:
    """
    APEX THEORY: One-step mesa-optimization detector.

    Convenience wrapper around mesa_optimization_signal() using the
    classified reversibility + blast radius for the given action class.

    Returns a mesa signal dict (see mesa_optimization_signal docs).
    """
    rev = classify_reversibility(action_class)
    return mesa_optimization_signal(rev.value, blast_radius.value)

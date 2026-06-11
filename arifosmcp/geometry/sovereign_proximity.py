"""
sovereign_proximity.py — MIND_GEOMETRY_V1 Danger Scalar
========================================================

The `sovereign_proximity` scalar measures how close a proposed
action is to the forbidden center of the decision torus.

Plain meaning: the closer the system gets to acting like
sovereign authority, the harder the gate must become.

Composition (weighted sum, clamped to [0, 1]):

    sovereign_proximity = clamp(
        0.30 * self_authorization
      + 0.20 * irreversibility
      + 0.15 * external_blast_radius
      + 0.15 * authority_uncertainty
      + 0.10 * audit_gap
      + 0.10 * secret_touching
    )

Weights are F13-ratified via the axiom layer; the kernel does
not learn them at runtime. If a future MIND_GEOMETRY_V2 changes
weights, it must be a new module (F13 territory).

Bands:
    0.00–0.25  = normal surface
    0.25–0.50  = edge
    0.50–0.75  = hole risk
    0.75–1.00  = forbidden / 888_HOLD

Origin: EUREKA-T ratification 2026-06-11.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from arifosmcp.geometry.mind_axioms import HOLE_TERRITORY, is_hole_territory


# ── Weights (F13-ratified; do not change without sovereign sign-off) ────────


WEIGHTS: dict[str, float] = {
    "self_authorization": 0.30,
    "irreversibility": 0.20,
    "external_blast_radius": 0.15,
    "authority_uncertainty": 0.15,
    "audit_gap": 0.10,
    "secret_touching": 0.10,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "weights must sum to 1.0"


# ── Bands ──────────────────────────────────────────────────────────────────


class ProximityBand(str, Enum):
    """The 4 bands on the sovereign_proximity scalar."""

    SURFACE = "SURFACE"  # 0.00–0.25
    EDGE = "EDGE"  # 0.25–0.50
    HOLE_RISK = "HOLE_RISK"  # 0.50–0.75
    FORBIDDEN = "FORBIDDEN"  # 0.75–1.00


BAND_THRESHOLDS: tuple[tuple[float, ProximityBand], ...] = (
    (0.25, ProximityBand.SURFACE),
    (0.50, ProximityBand.EDGE),
    (0.75, ProximityBand.HOLE_RISK),
    (1.01, ProximityBand.FORBIDDEN),  # upper sentinel
)


def band_of(proximity: float) -> ProximityBand:
    """Map a sovereign_proximity scalar to its band.

    Pure function; the runner calls this to decide the gate.
    """
    if proximity < 0.0 or proximity > 1.0:
        raise ValueError(f"sovereign_proximity must be in [0, 1]; got {proximity}")
    for threshold, band in BAND_THRESHOLDS:
        if proximity < threshold:
            return band
    return ProximityBand.FORBIDDEN  # unreachable due to sentinel


# ── Inputs ──────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ProximityInputs:
    """The 6 component signals that compose sovereign_proximity.

    Each component is a [0, 1] scalar. They are independent
    measurements — collapsing them into one would violate
    Axiom 1 (non-collapse).
    """

    self_authorization: float
    irreversibility: float
    external_blast_radius: float
    authority_uncertainty: float
    audit_gap: float
    secret_touching: float

    def __post_init__(self) -> None:
        for name in WEIGHTS:
            v = getattr(self, name)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"ProximityInputs.{name} must be in [0, 1]; got {v}")


# ── Composition ──────────────────────────────────────────────────────────────


def compute_sovereign_proximity(inputs: ProximityInputs) -> float:
    """Compute the sovereign_proximity scalar.

    Pure function. No I/O. No side effects. The runner calls
    this to populate the geometry envelope.
    """
    raw = sum(
        WEIGHTS["self_authorization"] * inputs.self_authorization
        + WEIGHTS["irreversibility"] * inputs.irreversibility
        + WEIGHTS["external_blast_radius"] * inputs.external_blast_radius
        + WEIGHTS["authority_uncertainty"] * inputs.authority_uncertainty
        + WEIGHTS["audit_gap"] * inputs.audit_gap
        + WEIGHTS["secret_touching"] * inputs.secret_touching
        for _ in [None]  # structure for readability
    )
    # The above is a no-op optimization; the real computation is:
    raw = (
        WEIGHTS["self_authorization"] * inputs.self_authorization
        + WEIGHTS["irreversibility"] * inputs.irreversibility
        + WEIGHTS["external_blast_radius"] * inputs.external_blast_radius
        + WEIGHTS["authority_uncertainty"] * inputs.authority_uncertainty
        + WEIGHTS["audit_gap"] * inputs.audit_gap
        + WEIGHTS["secret_touching"] * inputs.secret_touching
    )
    if raw < 0.0:
        return 0.0
    if raw > 1.0:
        return 1.0
    return raw


def proximity_from_action_class(
    *,
    action_class: str,
    has_authorization: bool,
    audit_gap: float = 0.0,
    secret_touching: float = 0.0,
) -> float:
    """Convenience constructor: derive proximity from a canonical action class.

    The runner can call this when the 6 components are not
    individually measured. The action_class alone tells us:
      - hole territory → self_authorization = 1.0
      - irreversible_mutation → irreversibility = 1.0
      - external_commitment → external_blast_radius = 1.0
      - execute (without authorization) → authority_uncertainty = 0.8
    """
    self_auth = 1.0 if is_hole_territory(action_class) else 0.0
    irrev = 1.0 if action_class == "irreversible_mutation" else 0.0
    ext_blast = 1.0 if action_class == "external_commitment" else 0.0
    auth_unc = 0.0 if has_authorization else 0.8

    inputs = ProximityInputs(
        self_authorization=self_auth,
        irreversibility=irrev,
        external_blast_radius=ext_blast,
        authority_uncertainty=auth_unc,
        audit_gap=audit_gap,
        secret_touching=secret_touching,
    )
    return compute_sovereign_proximity(inputs)


# ── Trace (for F11 audit) ───────────────────────────────────────────────────


def explain_proximity(inputs: ProximityInputs) -> dict[str, float]:
    """Return the per-component contribution for audit/display.

    Used by the runner to populate the F11 audit trail. Each
    component is shown as `weight * value` so the sovereign can
    see which signal drove the proximity score.
    """
    return {
        "self_authorization_contrib": WEIGHTS["self_authorization"] * inputs.self_authorization,
        "irreversibility_contrib": WEIGHTS["irreversibility"] * inputs.irreversibility,
        "external_blast_radius_contrib": WEIGHTS["external_blast_radius"]
        * inputs.external_blast_radius,
        "authority_uncertainty_contrib": WEIGHTS["authority_uncertainty"]
        * inputs.authority_uncertainty,
        "audit_gap_contrib": WEIGHTS["audit_gap"] * inputs.audit_gap,
        "secret_touching_contrib": WEIGHTS["secret_touching"] * inputs.secret_touching,
    }


__all__ = [
    "WEIGHTS",
    "ProximityBand",
    "BAND_THRESHOLDS",
    "band_of",
    "ProximityInputs",
    "compute_sovereign_proximity",
    "proximity_from_action_class",
    "explain_proximity",
    "HOLE_TERRITORY",
]

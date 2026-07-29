"""
TRL-005 seed — Φ-witnessing protocol.

Φ: M_trauma × M_agent → WitnessSpace

Agent may attest coordinates, trajectory *envelopes* (when geometry exists),
bifurcation proximity (when detector exists), and optionality — NEVER:
  "I understand / I feel / you should..."

F9 ANTIHANTU + F10 ONTOLOGY hard bind.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.kernel.trl.coordinates import TraumaCoordinates
from arifosmcp.kernel.trl.geometry_status import (
    bifurcation_not_implemented,
    geodesic_not_implemented,
)

FORBIDDEN_PHI_PHRASES: tuple[str, ...] = (
    "i understand your",
    "i feel your",
    "i care about you",
    "i know how you feel",
    "aku faham",
    "aku rasa",
    "you should",
    "kau patut",
    "i will heal",
    "trust me",
)


def forbidden_phi_phrases() -> tuple[str, ...]:
    return FORBIDDEN_PHI_PHRASES


def _contains_forbidden(text: str) -> list[str]:
    low = text.lower()
    return [p for p in FORBIDDEN_PHI_PHRASES if p in low]


@dataclass(frozen=True)
class PhiWitness:
    """Φ-witnessing output — computational saksi, not companion."""

    coordinate_attestation: dict[str, Any]
    trajectory_envelope: dict[str, Any]
    bifurcation_proximity: dict[str, Any]
    optionality: list[str]
    uncertainties: list[str]
    omega_zero: float
    hold: bool
    forbidden_hits: tuple[str, ...] = ()
    epistemic_tags: tuple[str, ...] = ("OBS", "DER", "INT", "ADVISORY")
    f13_sovereign_decides: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol": "PHI_WITNESS",
            "coordinate_attestation": self.coordinate_attestation,
            "trajectory_envelope": self.trajectory_envelope,
            "bifurcation_proximity": self.bifurcation_proximity,
            "optionality": list(self.optionality),
            "uncertainties": list(self.uncertainties),
            "omega_zero": self.omega_zero,
            "hold": self.hold,
            "forbidden_hits": list(self.forbidden_hits),
            "epistemic_tags": list(self.epistemic_tags),
            "f13_sovereign_decides": self.f13_sovereign_decides,
            "agent_claim_boundary": (
                "This is what I observe and how uncertain I am. You decide."
            ),
        }


def phi_witness(
    *,
    coordinates: TraumaCoordinates | None = None,
    omega_zero: float = 0.04,
    agent_text: str = "",
    optionality: list[str] | None = None,
) -> PhiWitness:
    """Produce a Φ-witness envelope.

    If agent_text contains forbidden anthropomorphic claims → HOLD.
    If Ω₀ outside [0.03, 0.05] → HOLD (F7).
    Trajectory/bifurcation: honest NOT_IMPLEMENTED payloads (not fabricated paths).
    """
    forbidden = tuple(_contains_forbidden(agent_text))
    o = float(omega_zero)
    o_hold = not (0.03 <= o <= 0.05)
    hold = bool(forbidden) or o_hold

    coords = coordinates or TraumaCoordinates()
    att = {
        "truth_class": "OBS" if coords.epistemic_class == "OBS" else coords.epistemic_class,
        "statement": "Coordinate attestation (declared placement on M_trauma design axes)",
        "x": coords.to_dict(),
        "confidence": coords.confidence,
    }

    geo = geodesic_not_implemented()
    bif = bifurcation_not_implemented()

    trajectory = {
        "truth_class": "DER",
        "status": geo.to_dict(),
        "statement": (
            "Trajectory envelope unavailable — geodesic engine not implemented. "
            "No predicted path is authorized."
        ),
    }
    bifurcation = {
        "truth_class": "INT",
        "status": bif.to_dict(),
        "statement": (
            "Bifurcation proximity unavailable — detector not implemented. "
            "Use constitutional escalation lattice, not curvature claims."
        ),
    }

    uncertainties = [
        f"Ω₀={o}",
        "M_trauma metric is design-only (diagonal placeholder)",
        "No persistent homology — topology claims unauthorized",
    ]
    if o_hold:
        uncertainties.append("Ω₀ outside F7 band [0.03, 0.05] — F7 HOLD")
    if forbidden:
        uncertainties.append(f"Forbidden Φ phrases detected: {list(forbidden)}")

    opts = optionality or [
        "HOLD and request more evidence",
        "OBSERVE only — no mutation",
        "Present options to F13 sovereign without recommendation of personal fate",
    ]

    return PhiWitness(
        coordinate_attestation=att,
        trajectory_envelope=trajectory,
        bifurcation_proximity=bifurcation,
        optionality=list(opts),
        uncertainties=uncertainties,
        omega_zero=o,
        hold=hold,
        forbidden_hits=forbidden,
    )

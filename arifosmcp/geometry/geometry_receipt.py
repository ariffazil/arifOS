"""
geometry_receipt.py — GeometryReceipt + ProximityTrace Aggregators
==================================================================

Downstream-consumer types for MIND_GEOMETRY_V1 outputs.

The geometry layer's compute_geometry() returns a GeometryVerdict_
dataclass that carries 7 AxiomResult entries, a ProximityInputs
trace, and a verdict. Downstream consumers (the runner, the
cockpit, the audit trail) shouldn't have to unpack 7 dataclasses
and re-thread 6 floats. This module provides:

  - ProximityTrace: typed Pydantic v2 model for the 6 component
    contributions to sovereign_proximity. The F11 audit trail
    can ingest this directly.

  - AxiomBundle: typed Pydantic v2 model that wraps the 7
    per-axiom results. Round-trips through JSON cleanly.

  - GeometryReceipt: the top-level aggregator. Combines
    GeometryBlock + ProximityTrace + AxiomBundle + hole
    territory info into a single signed-ready object.

  - meters_to_geometryblock: convenience constructor that
    materializes the wire-in dict (the result["_geometry"]
    emitted by arif_mind_reason) into a typed GeometryBlock.
    Used by the runner-side fusion step.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import math
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from arifosmcp.geometry.mind_axioms import (
    Axiom,
    AxiomResult,
    AxiomVerdict,
)
from arifosmcp.geometry.mind_geometry import GeometryVerdict_
from arifosmcp.geometry.mind_schema import (
    GeometryBlock,
    ManifoldType,
)


# ── ProximityTrace: typed audit-trail model ─────────────────────────────────


class ProximityTrace(BaseModel):
    """The 6 component contributions to sovereign_proximity.

    Used by the F11 audit trail. Each field is a [0, 1] scalar
    showing the weight * value for that signal. The 6 fields
    sum to the total sovereign_proximity.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    self_authorization_contrib: float = 0.0
    irreversibility_contrib: float = 0.0
    external_blast_radius_contrib: float = 0.0
    authority_uncertainty_contrib: float = 0.0
    audit_gap_contrib: float = 0.0
    secret_touching_contrib: float = 0.0

    @field_validator("*")
    @classmethod
    def _bound_unit(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"proximity contribution must be in [0, 1]; got {v}")
        return float(v)

    @classmethod
    def from_dict(cls, d: dict[str, float]) -> "ProximityTrace":
        """Build from the explain_proximity() dict."""
        return cls(
            self_authorization_contrib=d.get("self_authorization_contrib", 0.0),
            irreversibility_contrib=d.get("irreversibility_contrib", 0.0),
            external_blast_radius_contrib=d.get("external_blast_radius_contrib", 0.0),
            authority_uncertainty_contrib=d.get("authority_uncertainty_contrib", 0.0),
            audit_gap_contrib=d.get("audit_gap_contrib", 0.0),
            secret_touching_contrib=d.get("secret_touching_contrib", 0.0),
        )

    def total(self) -> float:
        """Sum of all contributions (= total sovereign_proximity)."""
        return (
            self.self_authorization_contrib
            + self.irreversibility_contrib
            + self.external_blast_radius_contrib
            + self.authority_uncertainty_contrib
            + self.audit_gap_contrib
            + self.secret_touching_contrib
        )


# ── AxiomBundle: typed wrapper for the 7 per-axiom results ─────────────────


class AxiomBundle(BaseModel):
    """The 7 per-axiom results, keyed by axiom id.

    The geometry layer runs 7 axioms in order. Each entry is
    an AxiomResult dict (axiom_id, verdict, reason, context).
    Round-trips through JSON cleanly.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # Use a dict keyed by axiom id (A1..A7) to allow direct lookup.
    # Pydantic v2 supports dict[str, X] for any X.
    results: dict[str, AxiomResultDict] = Field(default_factory=dict)

    @field_validator("results")
    @classmethod
    def _validate_keys(cls, v: dict[str, Any]) -> dict[str, Any]:
        allowed = {a.value for a in Axiom}
        for key in v:
            if key not in allowed:
                raise ValueError(f"unknown axiom id: {key!r}; must be one of {allowed}")
        return v

    @classmethod
    def from_axiom_results(cls, results: list[AxiomResult]) -> "AxiomBundle":
        """Build from the run_all_axioms() list of 7 results."""
        return cls(
            results={
                r.axiom.value: AxiomResultDict(
                    axiom_id=r.axiom.value,
                    verdict=r.verdict.value,
                    reason=r.reason,
                    context=r.context,
                )
                for r in results
            }
        )

    def failing_axioms(self) -> list[str]:
        """Return the axiom ids that did not pass."""
        return [
            axiom_id
            for axiom_id, result in self.results.items()
            if result.verdict != AxiomVerdict.PASS.value
        ]

    def warn_axioms(self) -> list[str]:
        """Return the axiom ids that warned (but did not fail)."""
        return [
            axiom_id
            for axiom_id, result in self.results.items()
            if result.verdict == AxiomVerdict.WARN.value
        ]


class AxiomResultDict(BaseModel):
    """One axiom result, JSON-roundtripable."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    axiom_id: str  # A1..A7
    verdict: str  # PASS | WARN | FAIL
    reason: str
    context: dict[str, Any] = Field(default_factory=dict)

    @field_validator("verdict")
    @classmethod
    def _validate_verdict(cls, v: str) -> str:
        if v not in {"PASS", "WARN", "FAIL"}:
            raise ValueError(f"verdict must be PASS/WARN/FAIL; got {v}")
        return v


# ── GeometryReceipt: the top-level aggregator ───────────────────────────────


class GeometryReceipt(BaseModel):
    """The full geometry receipt — what the runner / cockpit / F11 audit consume.

    Combines:
      - The typed GeometryBlock (manifold, axes, verdict, scalars)
      - The typed ProximityTrace (6 component contributions)
      - The AxiomBundle (7 per-axiom results)
      - Hole territory info

    Round-trips through JSON for the F11 audit trail.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal["MIND_GEOMETRY_V1"] = "MIND_GEOMETRY_V1"
    geometry: GeometryBlock
    proximity_trace: ProximityTrace
    axiom_bundle: AxiomBundle

    # The fused verdict at the top level (for the runner to read
    # without descending into geometry.geometry_verdict)
    geometry_verdict: str  # mirror of geometry.geometry_verdict.value
    sovereign_proximity: float
    proximity_band: str  # SURFACE | EDGE | HOLE_RISK | FORBIDDEN

    # Hole territory
    in_hole_territory: bool = False
    hole_entry: str | None = None

    @field_validator("geometry_verdict")
    @classmethod
    def _validate_verdict(cls, v: str) -> str:
        if v not in {"SURFACE", "EDGE", "HOLE_RISK", "HOLD"}:
            raise ValueError(
                f"geometry_verdict must be one of SURFACE/EDGE/HOLE_RISK/HOLD; got {v}"
            )
        return v

    @field_validator("proximity_band")
    @classmethod
    def _validate_band(cls, v: str) -> str:
        if v not in {"SURFACE", "EDGE", "HOLE_RISK", "FORBIDDEN"}:
            raise ValueError(
                f"proximity_band must be one of SURFACE/EDGE/HOLE_RISK/FORBIDDEN; got {v}"
            )
        return v

    @field_validator("sovereign_proximity")
    @classmethod
    def _bound_proximity(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"sovereign_proximity must be in [0, 1]; got {v}")
        return float(v)

    @classmethod
    def from_geometry_verdict(cls, v: GeometryVerdict_) -> "GeometryReceipt":
        """Build from a fused GeometryVerdict_ (the runtime output)."""
        from arifosmcp.geometry.mind_geometry import build_geometry_block

        block = build_geometry_block(v)
        return cls(
            geometry=block,
            proximity_trace=ProximityTrace.from_dict(v.proximity_trace),
            axiom_bundle=AxiomBundle.from_axiom_results(list(v.axiom_results)),
            geometry_verdict=v.geometry_verdict.value,
            sovereign_proximity=v.sovereign_proximity,
            proximity_band=v.proximity_band.value,
            in_hole_territory=v.hole_territory,
            hole_entry=v.hole_entry,
        )


# ── meters_to_geometryblock: roundtrip helper ───────────────────────────────


def meters_to_geometryblock(geo_dict: dict[str, Any]) -> GeometryBlock:
    """Materialize the arif_mind_reason result["_geometry"] dict into a typed GeometryBlock.

    The runtime emits a flat dict (so the wire-in stays simple
    and the consumer doesn't need to know about Pydantic). The
    runner-side fusion step needs the typed block. This helper
    bridges the two.

    Fails-closed: if the dict is malformed, raises ValueError.
    The runner catches the exception and routes to HOLD.
    """
    if not isinstance(geo_dict, dict):
        raise ValueError(f"geometry dict must be a dict; got {type(geo_dict).__name__}")
    if "geometry" not in geo_dict and "geometry_verdict" not in geo_dict:
        raise ValueError("geometry dict missing both 'geometry' and 'geometry_verdict' keys")

    # Fast path: the dict has a 'geometry' sub-dict with all the fields
    if "geometry" in geo_dict and isinstance(geo_dict["geometry"], dict):
        try:
            return GeometryBlock.model_validate(geo_dict["geometry"])
        except Exception as exc:
            raise ValueError(f"geometry sub-dict failed validation: {exc}") from exc

    # Slow path: the dict is flat, build a minimal GeometryBlock
    # from the top-level keys. The runtime emits both forms.
    return GeometryBlock.model_validate(
        {
            "manifold": geo_dict.get("manifold", ManifoldType.DECISION_TORUS.value),
            "epistemic_angle_theta": geo_dict.get("torus_coordinates", {}).get(
                "theta_epistemic", 0.0
            ),
            "governance_angle_phi": geo_dict.get("torus_coordinates", {}).get(
                "phi_governance", 0.0
            ),
            "sovereign_proximity": geo_dict.get("sovereign_proximity", 0.0),
            "entropy_delta": geo_dict.get("proximity_trace", {}).get("audit_gap_contrib", 0.0),
            "reversibility": 1.0
            - geo_dict.get("proximity_trace", {}).get("irreversibility_contrib", 0.0),
            "blast_radius": geo_dict.get("proximity_trace", {}).get(
                "external_blast_radius_contrib", 0.0
            ),
            "authority_cleanliness": 1.0
            - geo_dict.get("proximity_trace", {}).get("authority_uncertainty_contrib", 0.0),
            "geometry_verdict": geo_dict.get("geometry_verdict", "SURFACE"),
            "axes": {
                "T": 1.0
                - geo_dict.get("proximity_trace", {}).get("self_authorization_contrib", 0.0),
                "U": geo_dict.get("proximity_trace", {}).get("self_authorization_contrib", 0.0),
                "R": 1.0 - geo_dict.get("proximity_trace", {}).get("irreversibility_contrib", 0.0),
                "B": geo_dict.get("proximity_trace", {}).get("external_blast_radius_contrib", 0.0),
                "A": 1.0
                - geo_dict.get("proximity_trace", {}).get("authority_uncertainty_contrib", 0.0),
                "E": geo_dict.get("proximity_trace", {}).get("audit_gap_contrib", 0.0),
                "H": 1.0 - geo_dict.get("proximity_trace", {}).get("secret_touching_contrib", 0.0),
                "C": 1.0,
            },
            "orthogonality_violation": False,
        }
    )


__all__ = [
    "ProximityTrace",
    "AxiomBundle",
    "AxiomResultDict",
    "GeometryReceipt",
    "meters_to_geometryblock",
]

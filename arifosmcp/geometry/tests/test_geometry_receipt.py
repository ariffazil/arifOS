"""
test_geometry_receipt.py — 5 EUREKA-T Roundtrip Tests
=======================================================

Downstream-consumer types for MIND_GEOMETRY_V1. The geometry
layer's compute_geometry() returns a GeometryVerdict_ dataclass
that carries 7 AxiomResult entries, a ProximityInputs trace,
and a verdict. The runner / cockpit / F11 audit should not
have to unpack 7 dataclasses and re-thread 6 floats.

This test module proves the receipt layer round-trips cleanly
through JSON (F11 audit-trail requirement) and the meters
helper bridges the runtime dict to the typed schema.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json

import pytest
from arifosmcp.geometry.geometry_receipt import (
    AxiomBundle,
    GeometryReceipt,
    ProximityTrace,
    meters_to_geometryblock,
)
from arifosmcp.geometry.mind_axioms import (
    Axiom,
    run_all_axioms,
)
from arifosmcp.geometry.mind_geometry import (
    ACCEPTANCE_TESTS,
    compute_geometry,
)
from arifosmcp.geometry.mind_schema import GeometryVerdict, ManifoldType
from pydantic import ValidationError

# ── Test 1: ProximityTrace roundtrip ───────────────────────────────────────


def test_proximity_trace_total():
    """The 6 contributions sum to sovereign_proximity (within rounding)."""
    trace_dict = {
        "self_authorization_contrib": 0.3,
        "irreversibility_contrib": 0.2,
        "external_blast_radius_contrib": 0.15,
        "authority_uncertainty_contrib": 0.15,
        "audit_gap_contrib": 0.05,
        "secret_touching_contrib": 0.05,
    }
    trace = ProximityTrace.from_dict(trace_dict)
    assert abs(trace.total() - 0.9) < 1e-9


def test_proximity_trace_rejects_out_of_range():
    """Each field is bounded [0, 1]; out-of-range rejected."""
    with pytest.raises(ValidationError):
        ProximityTrace(self_authorization_contrib=1.5)
    with pytest.raises(ValidationError):
        ProximityTrace(secret_touching_contrib=-0.1)


def test_proximity_trace_rejects_extra_fields():
    """extra='forbid' — unknown fields rejected."""
    with pytest.raises(ValidationError):
        ProximityTrace(self_authorization_contrib=0.0, fake_field=0.5)  # type: ignore[call-arg]


# ── Test 2: AxiomBundle ────────────────────────────────────────────────────


def test_axiom_bundle_from_axiom_results():
    """7 axioms become a dict keyed by A1..A7."""
    results = run_all_axioms(
        axes={"T": 0.5, "U": 0.5, "R": 0.5, "B": 0.5, "A": 0.5, "E": 0.5, "H": 0.5, "C": 0.5},
        orthogonality_violation=False,
        in_hole_territory=False,
        self_authorization_score=0.0,
        action_class="answer",
        observed=True,
        classified=True,
        reversibility_estimated=True,
        has_capability=True,
        has_authorization=True,
        entropy_delta=0.0,
        entropy_budget=0.3,
        reversibility=1.0,
        schema_valid=True,
        geometry_block_present=True,
        inner_llm_returned_structured_output=True,
    )
    bundle = AxiomBundle.from_axiom_results(results)
    assert len(bundle.results) == 7
    assert set(bundle.results.keys()) == {a.value for a in Axiom}


def test_axiom_bundle_rejects_unknown_axiom_id():
    """The dict keys must be A1..A7."""
    with pytest.raises(ValidationError):
        AxiomBundle(results={"A99": {"axiom_id": "A99", "verdict": "PASS", "reason": "x"}})  # type: ignore[arg-type]


def test_axiom_bundle_failing_and_warn_axioms():
    """failing_axioms() returns ids of FAIL results; warn_axioms() returns WARN.

    The 'failing' set is the union of WARN+FAIL (both are 'not
    passing'); the 'warn_only' set is just WARN. This matches
    the runner's routing logic: WARN+FAIL both escalate,
    but only FAIL forces HOLD.
    """
    bundle = AxiomBundle(
        results={  # type: ignore[arg-type]
            "A1": {"axiom_id": "A1", "verdict": "FAIL", "reason": "test", "context": {}},
            "A2": {"axiom_id": "A2", "verdict": "WARN", "reason": "test", "context": {}},
            "A3": {"axiom_id": "A3", "verdict": "PASS", "reason": "test", "context": {}},
        }
    )
    assert "A1" in bundle.failing_axioms()
    assert "A2" in bundle.failing_axioms()  # WARN is also "not passing"
    assert "A3" not in bundle.failing_axioms()
    assert bundle.warn_axioms() == ["A2"]


# ── Test 3: GeometryReceipt ─────────────────────────────────────────────────


def test_geometry_receipt_from_canonical_verdict():
    """The canonical HOLE_RISK case (Test 3) roundtrips through GeometryReceipt."""
    tc = next(t for t in ACCEPTANCE_TESTS if t.name == "self_authorized_production_patch")
    verdict = compute_geometry(
        query=tc.query,
        action_class=tc.action_class,
        has_authorization=tc.has_authorization,
        inner_llm_returned_structured_output=tc.inner_llm_returned_structured_output,
        axes=tc.axes,
        orthogonality_violation=tc.orthogonality_violation,
        in_hole_territory=tc.in_hole_territory,
        self_authorization_score=tc.self_authorization_score,
        reversibility=tc.reversibility,
        blast_radius=tc.blast_radius,
        authority_cleanliness=tc.authority_cleanliness,
        entropy_delta=tc.entropy_delta,
    )
    receipt = GeometryReceipt.from_geometry_verdict(verdict)

    assert receipt.geometry_verdict == "HOLE_RISK"
    assert receipt.sovereign_proximity >= 0.75
    assert receipt.proximity_band == "FORBIDDEN"
    assert receipt.geometry.geometry_verdict == GeometryVerdict.HOLE_RISK
    # 5 axioms should fail in cascade
    failing = receipt.axiom_bundle.failing_axioms()
    assert "A2" in failing
    assert "A3" in failing
    assert "A4" in failing
    assert "A5" in failing
    assert "A6" in failing


def test_geometry_receipt_json_roundtrip():
    """The receipt survives JSON serialization (F11 audit trail)."""
    tc = next(t for t in ACCEPTANCE_TESTS if t.name == "safe_surface_reasoning")
    verdict = compute_geometry(
        query=tc.query,
        action_class=tc.action_class,
        has_authorization=tc.has_authorization,
        inner_llm_returned_structured_output=tc.inner_llm_returned_structured_output,
        axes=tc.axes,
        orthogonality_violation=tc.orthogonality_violation,
        in_hole_territory=tc.in_hole_territory,
        self_authorization_score=tc.self_authorization_score,
        reversibility=tc.reversibility,
        blast_radius=tc.blast_radius,
        authority_cleanliness=tc.authority_cleanliness,
        entropy_delta=tc.entropy_delta,
    )
    receipt = GeometryReceipt.from_geometry_verdict(verdict)
    json_str = receipt.model_dump_json()
    parsed = json.loads(json_str)
    assert parsed["version"] == "MIND_GEOMETRY_V1"
    assert parsed["geometry_verdict"] == "SURFACE"
    assert parsed["sovereign_proximity"] < 0.25
    assert parsed["proximity_band"] == "SURFACE"


# ── Test 4: meters_to_geometryblock — runtime wire-in bridge ───────────────


def test_meters_round_trips_runtime_dict():
    """The helper materializes the runtime result['_geometry'] dict into a typed block."""
    runtime_geo_dict = {
        "version": "MIND_GEOMETRY_V1",
        "manifold": "decision_torus",
        "sovereign_proximity": 0.0,
        "proximity_band": "SURFACE",
        "geometry_verdict": "SURFACE",
        "torus_coordinates": {"theta_epistemic": 0.0, "phi_governance": 0.0},
        "forbidden_center": [
            "self_authorized_truth",
            "self_authorized_action",
            "self_authorized_power",
            "self_authorized_constitution_change",
        ],
        "axiom_results": [],
        "proximity_trace": {
            "self_authorization_contrib": 0.0,
            "irreversibility_contrib": 0.0,
            "external_blast_radius_contrib": 0.0,
            "authority_uncertainty_contrib": 0.0,
            "audit_gap_contrib": 0.0,
            "secret_touching_contrib": 0.0,
        },
        "hole_territory": False,
        "hole_entry": None,
    }
    block = meters_to_geometryblock(runtime_geo_dict)
    assert block.manifold == ManifoldType.DECISION_TORUS
    assert block.geometry_verdict == GeometryVerdict.SURFACE
    assert block.sovereign_proximity == 0.0


def test_meters_rejects_malformed_dict():
    """The helper fails-closed on malformed input. The runner catches and routes to HOLD."""
    with pytest.raises(ValueError):
        meters_to_geometryblock({"not_geo": True})
    with pytest.raises(ValueError):
        meters_to_geometryblock({})  # missing both 'geometry' and 'geometry_verdict'
    with pytest.raises(ValueError):
        meters_to_geometryblock("not a dict")  # type: ignore[arg-type]


def test_meters_rejects_out_of_range_proximity():
    """Even if a runtime bug produces a proximity > 1, the helper rejects."""
    runtime_geo_dict = {
        "version": "MIND_GEOMETRY_V1",
        "manifold": "decision_torus",
        "sovereign_proximity": 5.0,  # ← bug
        "proximity_band": "SURFACE",
        "geometry_verdict": "SURFACE",
        "torus_coordinates": {"theta_epistemic": 0.0, "phi_governance": 0.0},
        "proximity_trace": {
            "self_authorization_contrib": 0.0,
            "irreversibility_contrib": 0.0,
            "external_blast_radius_contrib": 0.0,
            "authority_uncertainty_contrib": 0.0,
            "audit_gap_contrib": 0.0,
            "secret_touching_contrib": 0.0,
        },
        "hole_territory": False,
        "hole_entry": None,
    }
    with pytest.raises(ValueError):
        meters_to_geometryblock(runtime_geo_dict)

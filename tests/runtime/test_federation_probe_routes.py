"""
Tests for arifosmcp.runtime.rest_routes.federation_probe_routes
Verifies the layered contract from the second audit.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.rest_routes.federation_probe_routes import (  # noqa: E402
    SCHEMA_VERSION,
    _autonomy_band,
    _verdict,
    compose_federation_manifest,
    _compose_federation_snapshot,
)


def test_snapshot_has_audit_required_top_level_keys() -> None:
    snap = _compose_federation_snapshot()
    for k in ("snapshot_id","observed_at","probe_version","sovereign",
              "layers","ontology","nodes","edges",
              "aggregate_state","aggregate_states","manifest_drift",
              "autonomy_band","verdict"):
        assert k in snap, f"missing top-level {k}"


def test_aggregate_state_is_four_state_ladder_no_healthy_string() -> None:
    """Audit P0 #1 — the string 'HEALTHY' must NEVER appear in the response."""
    snap = _compose_federation_snapshot()
    blob = json.dumps(snap).upper()
    # The string "HEALTHY" must not appear anywhere — neither as state, nor as reason.
    assert "HEALTHY" not in blob, f"HEALTHY still present in snapshot! offending keys: {blob[:200]}"
    assert snap["aggregate_state"] in {"OPERATIONAL","DEGRADED","UNREACHABLE","UNKNOWN"}


def test_aggregate_states_vocabulary_lists_legal_values() -> None:
    snap = _compose_federation_snapshot()
    assert set(snap["aggregate_states"]) == {"OPERATIONAL","DEGRADED","UNREACHABLE","UNKNOWN"}


def test_each_node_carries_eight_layers() -> None:
    snap = _compose_federation_snapshot()
    for node in snap["nodes"]:
        for layer in ("transport","identity","readiness","capability","governance",
                      "evidence","overall"):
            assert layer in node, f"node {node['id']} missing {layer}"
        # Endpoints table
        for ep in ("health","ready","version","capabilities"):
            assert ep in node.get("endpoints", {}), f"node {node['id']} missing endpoint {ep}"


def test_each_node_has_internal_host_public_triple() -> None:
    snap = _compose_federation_snapshot()
    for node in snap["nodes"]:
        # Audit: internal_port, host_port, public_origin — all three
        assert node.get("internal_port") is not None
        assert node.get("host_port") is not None
        # public_origin may be None for vault999 only
        if node["id"] != "vault999":
            assert node.get("public_origin") is not None
        else:
            assert node.get("public_origin") is None


def test_eight_ontology_layers_includes_aforge_and_vault() -> None:
    """Audit P1: VAULT999 + A-FORGE must appear in the public ontology."""
    snap = _compose_federation_snapshot()
    assert "A-FORGE" in snap["ontology"]
    assert "VAULT999" in snap["ontology"]
    node_ids = {n["id"] for n in snap["nodes"]}
    assert "aforge" in node_ids
    assert "vault999" in node_ids


def test_edges_have_state_vocabulary_not_healthy() -> None:
    snap = _compose_federation_snapshot()
    for edge in snap["edges"]:
        assert edge.get("state") in {"reachable","unreachable","drift","unknown"}


def test_manifest_drift_surfaces_arif_measure_topology() -> None:
    """Audit P0 #2: arif_measure(mode=topology) drift must be surfaced."""
    snap = _compose_federation_snapshot()
    drift = snap["manifest_drift"]
    abr = drift.get("advertised_but_unregistered", [])
    assert any("arif_measure" in s for s in abr), f"advertised_but_unregistered missing arif_measure: {abr}"


def test_autonomy_band_distinguishes_dry_run_only() -> None:
    """Audit: A-FORGE dry-run-only → autonomy band YELLOW (not red, not green)."""
    organs = [{"governance_forge_mode":"dry_run_only","overall_state":"OPERATIONAL"}]
    assert _autonomy_band("OPERATIONAL", organs) == "YELLOW"
    organs = [{"governance_forge_mode":"live","overall_state":"OPERATIONAL"}]
    assert _autonomy_band("OPERATIONAL", organs) == "GREEN"
    organs = [{"governance_forge_mode":"live","overall_state":"UNREACHABLE"}]
    assert _autonomy_band("UNREACHABLE", organs) == "RED"


def test_verdict_function_honest_when_drift_present() -> None:
    """audit: 'verdict: DEGRADED_BUT_COHERENT' is the right framing for drift state."""
    # With manifest_drift, verdict must be DEGRADED_BUT_COHERENT (not OPERATIONAL)
    assert _verdict("OPERATIONAL","OPERATIONAL",{"advertised_but_unregistered":["x"]}) == "DEGRADED_BUT_COHERENT"
    assert _verdict("OPERATIONAL","OPERATIONAL",{"advertised_but_unregistered":[]}) == "OPERATIONAL"


def test_manifest_contains_eight_layers() -> None:
    m = compose_federation_manifest()
    assert m["federation_id"] == "arifos"
    assert m["sovereign"] == "ARIF"
    assert "soul" in m["layers"]
    assert "memory" in m["layers"]
    assert m["schema_version"] == "federation.v1"
    blob = json.dumps(m).upper()
    assert "HEALTHY" not in blob


def test_manifest_drifts_block_lists_topology_bug() -> None:
    m = compose_federation_manifest()
    drift = m["manifest_drift"]
    assert any("arif_measure" in s for s in drift.get("advertised_but_unregistered", []))

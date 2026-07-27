"""Regression tests for the arifos.public-state.v1 hardening upgrade.

Goals (Prompt: Observatory upgrade):
  * `schema` (and `schema_version`) are `arifos.public-state.v1` everywhere.
  * `schema_aliases` declares `observatory.v1` for backward compatibility.
  * `organs` keys are exactly six canonical ids and never alias to anything else.
  * Each finding item carries state / evidence / timestamp / confidence /
    trace / receipt and a links map with graph / floors / authority /
    policy / proof.
  * observatory.v1 remains the canonical signed snapshot contract and a
    downstream script can still read its own schema.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_public_state.py"
SPEC = importlib.util.spec_from_file_location("build_public_state", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _pf(value, confidence=0.92):
    return {
        "value": value,
        "state": "observed",
        "source": "test",
        "observed_at": "2026-07-27T00:00:00Z",
        "confidence": confidence,
    }


_BASE_HEALTH = {
    "status": "healthy",
    "release_name": "v2026.07.27-TEST",
    "tools_exposed_via_mcp": 8,
}


_BASE_SNAPSHOT = {
    "snapshot_id": "snap-2026-07-27",
    "observed_at": "2026-07-27T00:00:00Z",
    "runtime_identity": {
        "workspace_source_commit": _pf("b7dbb69629e1"),
        "workspace_dirty": _pf(False),
        "deployed_commit": _pf("b7dbb69629e1"),
        "build_commit": _pf("b7dbb69629e1"),
    },
    "capabilities": {"exposed_count": 8, "proven_live_count": 8, "tested_count": 8},
    "federation_edges": {"declared": 11, "probed": 11, "reachable": 11},
    "receipts": {
        "head_seq": _pf(85),
        "chain_verified": _pf(True),
        "replay_verified": _pf(True),
    },
    "governance": {},
    "signature": {"state": "signed", "value": "deadbeefcafebabe", "key_id": "obs-2026-07"},
    "findings": {
        "findings": [
            {
                "id": "FND-001",
                "organ_id": "geox",
                "category": "DRIFT",
                "severity": "MEDIUM",
                "status": "OPEN",
                "description": "Cap drift detected on borehole mcp tool",
                "observed_at": "2026-07-27T01:23:45Z",
                "confidence": 0.88,
                "source": "federation.drift_matrix",
                "trace": "trace-xyz",
                "receipt": "rcpt-001",
                "evidence": {"drift_id": "D-23", "tool": "borehole_mcp"},
            },
            {
                # Malformed-by-design: id is a list, not a string → still salvageable
                # but exposes the normalizer's tolerance via SCHEMA_MISMATCH for
                # the description.
                "id": ["not", "a", "finding"],
                "category": ["list-category"],
                "status": 42,
            },
            # Bare string entry — also SCHEMA_MISMATCH.
            "scraped: drift issue pending triage",
        ]
    },
}


def _project(snapshot=None, health=None):
    snap = snapshot if snapshot is not None else _BASE_SNAPSHOT
    h = health if health is not None else _BASE_HEALTH
    with patch.object(MODULE, "probe_organ", return_value={"transport": "UNKNOWN"}):
        return MODULE.project_public_state(snap, h)


def test_organ_id_normalizer_strips_aliases_to_canonical_set() -> None:
    canonical = {"arifos", "geox", "wealth", "well", "aforge", "aaa"}
    for value, expected in [
        ("arifos_kernel", "arifos"),
        ("a-forge", "aforge"),
        ("well-organ", "well"),
        ("GEOX", "geox"),
        ("geox", "geox"),
        ("", "unknown"),
        (None, "unknown"),
        ("weird-thing", "unknown"),
    ]:
        result = MODULE.stable_organ_id(value)
        assert result in canonical or result == "unknown", (value, expected, result)
        if expected in canonical:
            assert result == expected, (value, expected, result)


def test_public_state_schema_declares_v1_and_observatory_alias() -> None:
    state = _project()
    assert state["schema"] == "arifos.public-state.v1"
    assert state["schema_version"] == "arifos.public-state.v1"
    assert "observatory.v1" in state["schema_aliases"]
    assert state["compatibility"]["observatory_v1_still_served"] is True
    assert state["compatibility"]["observatory_v1_endpoint"] == "/api/observatory/v1/snapshot"
    assert state["compatibility"]["public_state_endpoint"] == "/api/public-state"


def test_organs_have_exactly_six_canonical_keys_never_alias() -> None:
    state = _project()
    expected = {"arifos", "geox", "wealth", "well", "aforge", "aaa"}
    assert set(state["organs"]) == expected
    for organ_id, row in state["organs"].items():
        assert row["schema_version"] == "arifos.public-state.v1"
        assert row["organ_id"] == organ_id, "renderer contract: organ_id == dict key"
        assert row["organ_id"] in expected


def test_findings_are_normalized_to_v1_envelope_never_throw() -> None:
    state = _project()
    findings = state["findings"]["items"]
    assert isinstance(findings, list)
    # The bare-string entry → SCHEMA_MISMATCH placeholder (not an object).
    # The bad-typed dict (id is a list, category a list) is still salvageable
    # via the normalizer and surfaces as a regular finding.
    mismatch = [f for f in findings if f.get("category") == "SCHEMA_MISMATCH"]
    assert len(mismatch) == 1, "expected exactly one SCHEMA_MISMATCH placeholder (the string)"
    assert mismatch[0]["state"] == "unknown"
    assert mismatch[0]["confidence"] == 0.0
    # Each item carries the contract fields:
    required = {"id", "organ_id", "category", "severity", "status", "state",
                "evidence", "timestamp", "confidence", "trace", "receipt",
                "evidence_url", "source", "links"}
    for item in findings:
        missing = required - set(item)
        assert not missing, f"missing fields {missing} in {item}"
        # organ_id is either canonical or "unknown"
        assert item["organ_id"] in {"arifos", "geox", "wealth", "well", "aforge", "aaa", "unknown"}
        # Links has the cross-cutting surfaces:
        for link_key in ("graph", "floors", "authority", "policy", "proof"):
            assert link_key in item["links"], (item["id"], link_key)


def test_findings_by_severity_and_highest_hold_track_normalized_list() -> None:
    state = _project()
    by_sev = state["findings"]["by_severity"]
    # Only OPEN findings contribute — FND-001 is OPEN with MEDIUM.
    assert by_sev.get("MEDIUM") == 1
    assert state["findings"]["highest_hold"] == "MEDIUM"
    # The newly-orphaned open_count reflects the v1 normalized list, not the
    # raw legacy list.
    assert state["findings"]["open_count"] == len(state["findings"]["open"])


def test_top_level_links_include_graph_floors_authority_policy_proof() -> None:
    state = _project()
    links = state["links"]
    for key in ("graph", "floors", "authority", "policy", "proof"):
        assert key in links, f"top-level link missing: {key}"
        assert links[key].startswith("https://"), f"link {key} must be absolute https"
    # Legacy entries still present so downstream parsers don't regress
    for key in ("public_state", "public_state_static", "mcp_gateway", "canon"):
        assert key in links


def test_organ_row_links_include_graph_floors_authority_policy_proof() -> None:
    state = _project()
    for organ_id, row in state["organs"].items():
        links = row["links"]
        for key in ("graph", "floors", "authority", "policy", "proof"):
            assert key in links, (organ_id, key)


def test_observatory_v1_emitter_still_emits_observatory_v1_schema() -> None:
    """Backward compat: observatory.v1 signing path must still be reachable.

    The observatory emitter script is unchanged; this test exists so the
    observability upgrade can never silently swallow the observatory.v1
    contract.
    """
    emitter_script = ROOT / "scripts" / "observatory_emit.py"
    assert emitter_script.exists()
    text = emitter_script.read_text(encoding="utf-8")
    assert 'SCHEMA_VERSION = "observatory.v1"' in text


def test_observatory_routes_still_serve_observatory_v1_endpoint() -> None:
    routes_script = ROOT / "arifosmcp" / "runtime" / "rest_routes" / "observatory_routes.py"
    assert routes_script.exists()
    text = routes_script.read_text(encoding="utf-8")
    assert 'SCHEMA_VERSION = "observatory.v1"' in text
    assert "/api/observatory/v1/snapshot" in text


def test_normalize_findings_handles_scalar_and_bad_dicts_gracefully() -> None:
    inputs = [
        None,
        "a string",
        42,
        ["scalar-list-item"],
        {"items": [{"id": "x"}]},
        {"findings": [{"id": "y"}]},
        {"random_key": "value"},  # treated as a single malformed dict
    ]
    items = MODULE.normalize_findings(inputs)
    assert isinstance(items, list)
    for item in items:
        assert item["schema_version"] == "arifos.public-state.v1"
        # Every shape either produces a SCHEMA_MISMATCH placeholder or a
        # fully-populated finding with all contract fields.
        if item["category"] == "SCHEMA_MISMATCH":
            assert item["state"] == "unknown"
            assert item["confidence"] == 0.0
        # Links always present.
        for key in ("graph", "floors", "authority", "policy", "proof"):
            assert key in item["links"]

"""Regression tests for the Observatory public SOT projection."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "build_public_state.py"
SPEC = importlib.util.spec_from_file_location("build_public_state", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _pf(value):
    return {"value": value, "state": "observed", "source": "test"}


def test_projection_keeps_exposed_proven_and_tested_distinct() -> None:
    snapshot = {
        "capabilities": {"exposed_count": 8, "proven_live_count": 7, "tested_count": 1},
        "federation_edges": {"declared": 11, "probed": 0, "reachable": 0},
        "receipts": {},
        "governance": {},
    }
    health = {"status": "healthy", "release_name": "v2026.07.18-TEST"}

    with patch.object(MODULE, "probe_organ", return_value={"transport": "UNKNOWN"}):
        state = MODULE.project_public_state(snapshot, health)

    assert state["mcp"]["public_tools"] == 8
    assert state["mcp"]["proven_live"] == 7
    assert state["mcp"]["tested"] == 1
    assert state["planes"]["capability"] == "PARTIAL · 7/8"
    assert state["federation"]["probed"] == 0


def test_projection_maps_canonical_receipt_and_all_six_organs() -> None:
    snapshot = {
        "capabilities": {"exposed_count": 8},
        "federation_edges": {"declared": 11, "probed": 11, "reachable": 11},
        "receipts": {
            "head_seq": _pf(85),
            "chain_verified": _pf(True),
            "replay_verified": _pf(True),
        },
        "governance": {},
    }
    health = {"status": "healthy", "release_name": "v2026.07.18-TEST"}

    with patch.object(MODULE, "probe_organ", side_effect=lambda organ_id: {"id": organ_id}):
        state = MODULE.project_public_state(snapshot, health)

    assert set(state["organs"]) == {"arifos", "geox", "wealth", "well", "aforge", "aaa"}
    assert state["receipt"]["head_sequence"] == 85
    assert state["receipt"]["verify"] == "PROVEN"
    assert state["receipt"]["replay"] == "PROVEN"


def test_projection_uses_workspace_source_and_reports_dirty_drift() -> None:
    snapshot = {
        "runtime_identity": {
            "source_commit": _pf("deployed-build"),
            "workspace_source_commit": _pf("operator-head"),
            "workspace_dirty": _pf(True),
            "deployed_commit": _pf("deployed-build"),
        },
        "capabilities": {"exposed_count": 8},
        "federation_edges": {},
        "receipts": {},
        "governance": {},
    }
    health = {"status": "healthy", "release_name": "v2026.07.18-TEST"}

    with patch.object(MODULE, "probe_organ", return_value={"transport": "UNKNOWN"}):
        state = MODULE.project_public_state(snapshot, health)

    assert state["release"]["source_commit_full"] == "operator-head"
    assert state["release"]["deployed_commit_full"] == "deployed-build"
    assert state["release"]["deployment_alignment"] == "DRIFTED"


def test_projection_labels_failed_chain_without_false_green() -> None:
    snapshot = {
        "capabilities": {"exposed_count": 8},
        "federation_edges": {},
        "receipts": {"chain_verified": _pf(False), "replay_verified": _pf(True)},
        "governance": {},
    }
    health = {"status": "healthy", "release_name": "v2026.07.18-TEST"}

    with patch.object(MODULE, "probe_organ", return_value={"transport": "UNKNOWN"}):
        state = MODULE.project_public_state(snapshot, health)

    assert state["receipt"]["verify"] == "FAILED"
    assert state["receipt"]["replay"] == "PROVEN"
    assert state["receipt"]["vault_status"] == "DEGRADED"


def test_projection_accepts_equivalent_short_git_prefixes() -> None:
    snapshot = {
        "runtime_identity": {
            "workspace_source_commit": _pf("b7dbb69629e1"),
            "workspace_dirty": _pf(False),
            "deployed_commit": _pf("b7dbb69"),
        },
        "capabilities": {"exposed_count": 8},
        "federation_edges": {},
        "receipts": {},
        "governance": {},
    }
    health = {"status": "healthy", "release_name": "v2026.07.18-TEST"}

    with patch.object(MODULE, "probe_organ", return_value={"transport": "UNKNOWN"}):
        state = MODULE.project_public_state(snapshot, health)

    assert state["release"]["deployment_alignment"] == "ALIGNED"

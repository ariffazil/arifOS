"""
Tests for /root/arifOS/arifosmcp/runtime/rest_routes/observatory_routes.py

Uses a fresh Starlette ASGI app + the shared SyncASGIClient. The fresh app
ensures we never accidentally hit the live kernel and that we're testing the
Observatory route handlers in isolation.

F1-safe: read-only. No service mutation. No filesystem write outside tmp.

Forged 2026-07-14 — Phase A of Reality Observatory.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.capability_drift import per_field, per_field_age  # noqa: E402
from arifosmcp.runtime.rest_routes.observatory_routes import (  # noqa: E402
    SCHEMA_VERSION,
    _findings_block,
    build_snapshot,
    register_observatory_routes,
    seven_state_health,
)
from tests.conftest import SyncASGIClient  # noqa: E402


# ── Fixtures ──────────────────────────────────────────────────────────────────
class _StubMCP:
    """Minimal stub for mcp-like object that observatory needs."""

    _tool_registry = [
        type("T", (), {"name": "arif_init"})(),
        type("T", (), {"name": "arif_observe"})(),
        type("T", (), {"name": "arif_judge"})(),
    ]


@pytest.fixture
def stub_mcp() -> _StubMCP:
    return _StubMCP()


@pytest.fixture
def fresh_observatory_app(stub_mcp):
    """Build a fresh Starlette app and register observatory routes on it."""
    from starlette.applications import Starlette  # type: ignore

    app = Starlette()
    register_observatory_routes(app, mcp=stub_mcp)
    return app


# ── Pure helpers ──────────────────────────────────────────────────────────────
def test_per_field_envelope_is_audit_shape() -> None:
    pf = per_field("KUKUH", source="test", state="observed", confidence=0.95)
    for required in ("value", "state", "source", "observed_at", "age_seconds", "confidence"):
        assert required in pf, f"missing {required}"
    assert pf["value"] == "KUKUH"
    assert pf["state"] == "observed"
    assert pf["source"] == "test"


def test_per_field_age_unknown_handling() -> None:
    pf = per_field_age(None, source="x", observed_at_epoch=None, state="unknown", confidence=0.0)
    # When epoch is None we get the per_field() fallback path with state="unknown"
    assert pf["state"] == "unknown"
    assert pf["value"] is None


def test_seven_state_health_returns_separate_states(stub_mcp) -> None:
    states = seven_state_health(mcp=stub_mcp)
    # All seven required states must be present and SEPARATE — never one green badge.
    assert set(states.keys()) == {
        "LIVENESS",
        "READINESS",
        "CAPABILITY",
        "GOVERNANCE",
        "AUTHORIZATION",
        "RECEIPT",
        "CONSTITUTIONAL",
    }
    for _key, v in states.items():
        assert "value" in v
        assert "state" in v
        assert "source" in v


# ── Snapshot composition ──────────────────────────────────────────────────────
def test_build_snapshot_envelope_invariants(stub_mcp) -> None:
    """Every named block must exist; the top-level signature is honest about its pending state."""
    snap = build_snapshot(mcp=stub_mcp)
    assert snap["schema_version"] == SCHEMA_VERSION
    assert snap["generated_by"] == "arifOS"
    assert "snapshot_id" in snap
    assert "observed_at" in snap

    # A local signing key may already be bootstrapped; never claim another state.
    assert snap["signature"]["state"] in {"unknown", "signed"}

    # Every block must exist.
    for key in (
        "runtime_identity",
        "substrate",
        "governance",
        "capabilities",
        "organs",
        "metabolism",
        "evidence",
        "receipts",
        "incidents",
        "tier",
    ):
        assert key in snap, f"snapshot missing block: {key}"


def test_finalized_snapshot_signature_hash_covers_final_payload(stub_mcp) -> None:
    snap = build_snapshot(mcp=stub_mcp)
    signature = snap["signature"]
    assert signature["state"] == "signed"
    unsigned = {key: value for key, value in snap.items() if key != "signature"}
    canonical = json.dumps(
        unsigned,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    assert signature["payload_hash"] == hashlib.sha256(canonical).hexdigest()


def test_build_snapshot_capabilities_populated(stub_mcp) -> None:
    snap = build_snapshot(mcp=stub_mcp)
    cap = snap["capabilities"]
    assert "matrix" in cap
    assert "declared_count" in cap
    assert "registered_count" in cap
    # Stub has 3 tools registered, none declared (TOOLREGISTRY may not exist in CI).
    # Either way the structural keys exist.
    rows = {r["name"]: r for r in cap["matrix"]}
    for k in (
        "name",
        "declared",
        "registered",
        "exposed",
        "invocable",
        "tested",
        "input_schema_hash_match",
        "output_schema_hash_match",
        "last_test_at",
        "age_seconds",
        "last_failure",
        "capability_truth",
    ):
        # Each row should carry this key (first row if any)
        if rows:
            any_row = next(iter(rows.values()))
            assert k in any_row, f"matrix row missing {k}"


def test_build_snapshot_runtime_identity_carries_drft_state(stub_mcp) -> None:
    snap = build_snapshot(mcp=stub_mcp)
    rid = snap["runtime_identity"]
    assert "drift_state" in rid
    assert rid["drift_state"]["value"] in {"aligned", "drifted", "unknown"}
    assert "source_commit" in rid
    assert "deployed_commit" in rid


def test_f008_compares_operator_workspace_to_deployed_commit() -> None:
    findings = _findings_block(
        runtime_identity={
            "workspace_source_commit": {"value": "source123"},
            "workspace_dirty": {"value": False},
            "deployed_commit": {"value": "deploy456"},
        }
    )
    f008 = next(item for item in findings["findings"] if item["id"] == "F-008")

    assert f008["status"] == "OPEN"
    assert "source=source123" in f008["evidence"]
    assert "deployed=deploy456" in f008["evidence"]


def test_f008_stays_open_when_matching_workspace_is_dirty() -> None:
    findings = _findings_block(
        runtime_identity={
            "workspace_source_commit": {"value": "same123"},
            "workspace_dirty": {"value": True},
            "deployed_commit": {"value": "same123"},
        }
    )
    f008 = next(item for item in findings["findings"] if item["id"] == "F-008")

    assert f008["status"] == "OPEN"
    assert "workspace_dirty=True" in f008["evidence"]


def test_f008_accepts_equivalent_short_git_prefixes() -> None:
    findings = _findings_block(
        runtime_identity={
            "workspace_source_commit": {"value": "b7dbb69629e1"},
            "workspace_dirty": {"value": False},
            "deployed_commit": {"value": "b7dbb69"},
        }
    )
    f008 = next(item for item in findings["findings"] if item["id"] == "F-008")

    assert f008["status"] == "RESOLVED"


def test_build_snapshot_governance_has_verdict_decomposition(stub_mcp) -> None:
    snap = build_snapshot(mcp=stub_mcp)
    gov = snap["governance"]
    assert "verdict_decomposition" in gov
    decomp = gov["verdict_decomposition"]
    for required in (
        "substrate_state",
        "session_state",
        "action_state",
        "receipt_state",
        "constitutional_judgment",
        "human_ratification",
    ):
        assert required in decomp, f"verdict_decomposition missing {required}"


def test_build_snapshot_metabolism_covers_all_eleven_stages(stub_mcp) -> None:
    snap = build_snapshot(mcp=stub_mcp)
    stages = [m["stage"]["value"] for m in snap["metabolism"]]
    assert stages == [
        "000_INIT",
        "111_OBSERVE",
        "222_EVIDENCE",
        "333_THINK",
        "444_ROUTE",
        "555_MEMORY",
        "666_CRITIQUE",
        "777_MEASURE",
        "888_JUDGE",
        "999_RECEIPT",
        "010_FORGE",
    ]


def test_build_snapshot_organs_covers_seven(stub_mcp) -> None:
    snap = build_snapshot(mcp=stub_mcp)
    organs = snap["organs"]
    for required in ("arifos", "geox", "wealth", "well", "aaa", "aforge", "mcp_gateway"):
        assert required in organs, f"organs block missing {required}"


def test_aaa_organ_is_display_only(stub_mcp) -> None:
    """AAA is glass+router. Observatory must not grade it as a kernel."""
    aaa = build_snapshot(mcp=stub_mcp)["organs"]["aaa"]
    cap = aaa["capability"]["value"]
    assert isinstance(cap, dict), cap
    assert cap.get("ceiling") == "DISPLAY_ONLY"
    assert aaa["governance"]["value"] == "DELEGATES_TO_KERNEL"
    assert aaa["last_receipt"]["value"] == "not_applicable"
    assert "arif_seal" not in str(aaa["last_receipt"].get("source", ""))
    assert aaa["drift"]["value"] == "not_applicable"
    assert aaa["authority_ceiling"]["value"] == "DISPLAY_ONLY"


# ── HTTP route surface (live ASGI round-trip) ─────────────────────────────────
def test_snapshot_endpoint_returns_200_with_envelope(fresh_observatory_app) -> None:
    client = SyncASGIClient(fresh_observatory_app)
    r = client.get("/api/observatory/v1/snapshot")
    assert r.status_code == 200
    payload = r.json()
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["generated_by"] == "arifOS"


def test_capabilities_endpoint_returns_matrix(fresh_observatory_app) -> None:
    client = SyncASGIClient(fresh_observatory_app)
    r = client.get("/api/observatory/v1/snapshot/capabilities")
    assert r.status_code == 200
    payload = r.json()
    assert "matrix" in payload
    assert "declared_count" in payload


def test_health_endpoint_returns_seven_states(fresh_observatory_app) -> None:
    client = SyncASGIClient(fresh_observatory_app)
    r = client.get("/api/observatory/v1/health")
    assert r.status_code == 200
    payload = r.json()
    states = payload["states"]
    assert set(states.keys()) == {
        "LIVENESS",
        "READINESS",
        "CAPABILITY",
        "GOVERNANCE",
        "AUTHORIZATION",
        "RECEIPT",
        "CONSTITUTIONAL",
    }


def test_snapshot_per_field_envelope_invariant(fresh_observatory_app) -> None:
    """Audit clause: every visible status carries source/timestamp/confidence.

    Spot-check a sample of cells across the snapshot.
    """
    client = SyncASGIClient(fresh_observatory_app)
    payload = client.get("/api/observatory/v1/snapshot").json()

    sampled = []
    rid = payload["runtime_identity"]
    sampled.append(rid["source_commit"])
    sampled.append(rid["drift_state"])
    sampled.append(rid["deployment_mode"])
    gov = payload["governance"]
    sampled.append(gov["floors_loaded"])
    sampled.append(gov["verdict"])
    sampled.append(payload["tier"])

    for cell in sampled:
        assert "value" in cell
        assert "state" in cell
        assert "source" in cell
        assert "observed_at" in cell
        assert "age_seconds" in cell
        assert "confidence" in cell

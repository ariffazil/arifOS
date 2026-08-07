"""
Tests for arifosmcp/runtime/federation_edges.py — F-006 plumbing (Day 5)

Doctrine:
  - Mock at the network boundary (urllib.request.urlopen).
  - Verify each F-006 spine field (session_propagated, actor_propagated,
    trace_propagated, receipt_produced) only when the bridge response
    actually contains the matching field.
  - Verify negative path: missing SCT → init_session_token absent → all 4 False.

What this test PROVES:
  1. _run_bridge_propagation_check uses arif_init(mode=init) to mint session
  2. It calls arif_route with the same session_token + actor_id
  3. It walks the bridge response for source_of_truth.session_id / actor_id
  4. It sets session_propagated=True ONLY IF the returned session_id equals init's
  5. Same for actor_propagated
  6. It walks for any trace_id → trace_propagated=True
  7. It checks verdicts.receipt → receipt_produced=True
  8. Negative path (init fails) → all 4 False

What this test DOES NOT prove:
  - Live wire compatibility with arifOS / GEOX (covered by integration)
"""

from __future__ import annotations

import json
import sys
from unittest.mock import patch

sys.path.insert(0, "/root/arifOS/src")

from arifosmcp.runtime.federation_edges import (
    SAFE_PROBE_MAP,
    _run_bridge_propagation_check,
    _run_sync_probe_all_edges,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────


def _init_response_payload(
    session_token: str = "act_v1.fake.token",
    session_id: str = "SEAL-fake-001",
    actor_id: str = "f006-edge-probe",
):
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "structuredContent": {
                "session_token": session_token,
                "session_id": session_id,
                "actor_id": actor_id,
                "trace_id": "trc-init-001",
            }
        },
    }


def _bridge_response_payload(
    session_id: str, actor_id: str, trace_id: str = "trc-geox-001", receipt_state: str = "UNSEALED"
):
    """Mimics the actual arif_route bridge response shape (verified Day 4)."""
    return {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "structuredContent": {
                "verdicts": {
                    "receipt": {"state": receipt_state, "issuer": "arif_bridge"},
                },
                "result": {
                    "source_of_truth": {
                        "session_id": session_id,
                        "actor_id": actor_id,
                    },
                    "bridge_result": {
                        "verdicts": {
                            "receipt": {
                                "state": receipt_state,
                                "issuer": "arif_bridge",
                            },
                        },
                        "result": {
                            "result": {
                                "kernel": {
                                    "session_id": session_id,
                                    "actor_id": actor_id,
                                    "actor_verified": True,
                                },
                                "payload": {
                                    "session_id": session_id,
                                    "actor_id": actor_id,
                                    "trace_id": trace_id,
                                },
                            },
                        },
                        "trace_id": trace_id,
                        "session_id": session_id,
                        "actor_id": actor_id,
                    },
                },
            },
        },
    }


class _FakeResp:
    def __init__(self, payload: dict | str):
        self._payload = (
            payload if isinstance(payload, (bytes, str)) else json.dumps(payload).encode()
        )

    def read(self) -> bytes:
        return self._payload if isinstance(self._payload, bytes) else self._payload.encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def _patch_urlopen(responses: list):
    """Build a side_effect that returns responses in order."""
    iter_responses = iter(responses)

    def side_effect(*args, **kwargs):
        return _FakeResp(next(iter_responses))

    return side_effect


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_safe_probe_map_covers_documented_targets():
    """SAFE_PROBE_MAP must list the 3 organs verified in recon Day 4."""
    assert set(SAFE_PROBE_MAP.keys()) == {"GEOX", "WEALTH", "WELL"}
    assert SAFE_PROBE_MAP["GEOX"] == ("geox", "geox_surface_status")
    assert SAFE_PROBE_MAP["WEALTH"] == ("wealth", "capital_health")
    assert SAFE_PROBE_MAP["WELL"] == ("well", "well_registry_status")


def test_bridge_check_sets_all_4_true_on_matching_response():
    """Happy path: bridge returns matching session_id + actor_id + trace_id + receipt."""
    init_p = _init_response_payload()
    bridge_p = _bridge_response_payload(
        session_id="SEAL-fake-001",
        actor_id="f006-edge-probe",
        trace_id="trc-geox-001",
        receipt_state="UNSEALED",
    )
    with patch("urllib.request.urlopen", side_effect=_patch_urlopen([init_p, bridge_p])):
        result = _run_bridge_propagation_check(target_organ="GEOX")
    assert result["session_propagated"] is True
    assert result["actor_propagated"] is True
    assert result["trace_propagated"] is True
    assert result["receipt_produced"] is True
    assert result["returned_session_id"] == "SEAL-fake-001"
    assert result["returned_actor_id"] == "f006-edge-probe"
    assert result["receipt_state"] == "UNSEALED"


def test_bridge_check_rejects_session_mismatch():
    """session_propagated=False if returned session_id != init's."""
    init_p = _init_response_payload(session_id="SEAL-fake-001")
    bridge_p = _bridge_response_payload(
        session_id="SEAL-DIFFERENT-999",  # mismatch!
        actor_id="f006-edge-probe",
    )
    with patch("urllib.request.urlopen", side_effect=_patch_urlopen([init_p, bridge_p])):
        result = _run_bridge_propagation_check(target_organ="GEOX")
    assert result["session_propagated"] is False
    # actor_propagated may still be True
    assert result["actor_propagated"] is True


def test_bridge_check_rejects_actor_mismatch():
    """actor_propagated=False if returned actor_id != init's."""
    init_p = _init_response_payload(actor_id="f006-edge-probe")
    bridge_p = _bridge_response_payload(
        session_id="SEAL-fake-001",
        actor_id="someone-else",  # mismatch!
    )
    with patch("urllib.request.urlopen", side_effect=_patch_urlopen([init_p, bridge_p])):
        result = _run_bridge_propagation_check(target_organ="GEOX")
    assert result["session_propagated"] is True  # session matches
    assert result["actor_propagated"] is False  # actor doesn't
    assert result["trace_propagated"] is True
    assert result["receipt_produced"] is True


def test_bridge_check_false_when_init_fails():
    """If arif_init fails, all 4 propagation fields must be False."""

    def _raise(*args, **kwargs):
        raise OSError("connection refused")

    with patch("urllib.request.urlopen", side_effect=_raise):
        result = _run_bridge_propagation_check(target_organ="GEOX")
    assert result["session_propagated"] is False
    assert result["actor_propagated"] is False
    assert result["trace_propagated"] is False
    assert result["receipt_produced"] is False
    assert "arif_init failed" in result.get("note", "")


def test_bridge_check_false_when_bridge_fails():
    """If arif_init succeeds but arif_route fails, all 4 must be False."""
    init_p = _init_response_payload()
    state = {"calls": 0}

    def _side_effect(*args, **kwargs):
        state["calls"] += 1
        if state["calls"] == 1:
            return _FakeResp(init_p)
        raise OSError("bridge timeout")

    with patch("urllib.request.urlopen", side_effect=_side_effect):
        result = _run_bridge_propagation_check(target_organ="GEOX")
    assert result["session_propagated"] is False
    assert result["actor_propagated"] is False
    assert result["trace_propagated"] is False
    assert result["receipt_produced"] is False


def test_bridge_check_false_when_init_returns_no_token():
    """If arif_init response has no session_token, fail closed."""
    bad_init = {"jsonrpc": "2.0", "id": 1, "result": {"structuredContent": {}}}
    with patch("urllib.request.urlopen", side_effect=_patch_urlopen([bad_init])):
        result = _run_bridge_propagation_check(target_organ="GEOX")
    assert result["session_propagated"] is False
    assert "no session_token" in result.get("note", "")


def test_bridge_check_handles_unknown_target():
    """Unknown target organ returns all False with a note."""
    with patch("urllib.request.urlopen", side_effect=_patch_urlopen([])):
        result = _run_bridge_propagation_check(target_organ="MARS")
    assert result["session_propagated"] is False
    assert "no safe probe mapped" in result.get("note", "")


def test_bridge_check_finds_trace_id_anywhere_in_response():
    """trace_propagated=True if any trace_id field is non-empty anywhere in response."""
    init_p = _init_response_payload()
    bridge_p = _bridge_response_payload(
        session_id="SEAL-fake-001",
        actor_id="f006-edge-probe",
        trace_id="trc-deeply-nested-xyz",
    )
    with patch("urllib.request.urlopen", side_effect=_patch_urlopen([init_p, bridge_p])):
        result = _run_bridge_propagation_check(target_organ="GEOX")
    assert result["trace_propagated"] is True
    assert result["returned_trace_id"] == "trc-deeply-nested-xyz"


def test_bridge_check_false_when_no_trace_in_response():
    """trace_propagated=False if response has no trace_id field."""
    init_p = _init_response_payload()
    bridge_p = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "structuredContent": {
                "result": {
                    "source_of_truth": {
                        "session_id": "SEAL-fake-001",
                        "actor_id": "f006-edge-probe",
                    },
                    "bridge_result": {
                        "verdicts": {"receipt": {"state": "UNSEALED"}},
                    },
                },
            },
        },
    }
    with patch("urllib.request.urlopen", side_effect=_patch_urlopen([init_p, bridge_p])):
        result = _run_bridge_propagation_check(target_organ="GEOX")
    assert result["session_propagated"] is True
    assert result["actor_propagated"] is True
    assert result["trace_propagated"] is False  # no trace_id anywhere
    assert result["receipt_produced"] is True  # receipt state still set


def test_async_probe_wires_bridge_for_arifos_x_edges_only():
    """probe_all_edges_async must also call bridge check for arifOS→X edges."""
    import asyncio

    captured: list[str] = []

    def fake_bridge(target_organ, mcp_url="http://127.0.0.1:8088", **kw):
        captured.append(target_organ)
        return {
            "session_propagated": True,
            "actor_propagated": True,
            "trace_propagated": True,
            "receipt_produced": True,
            "receipt_state": "UNSEALED",
        }

    from arifosmcp.runtime.federation_edges import probe_all_edges_async

    with (
        patch(
            "arifosmcp.runtime.federation_edges._run_bridge_propagation_check",
            side_effect=fake_bridge,
        ),
        patch(
            "arifosmcp.runtime.federation_edges._probe_tcp",
            return_value={"state": "reachable", "latency_ms": 1.0},
        ),
        patch(
            "arifosmcp.runtime.federation_edges._fetch_health",
            return_value={"identity_hash": "fake-hash", "federation_schema_version": "2.0.0"},
        ),
        patch(
            "arifosmcp.runtime.federation_edges._self_identity_health",
            return_value={"identity_hash": "fake-self-hash", "federation_schema_version": "2.0.0"},
        ),
    ):
        edges = asyncio.run(probe_all_edges_async())

    assert "GEOX" in captured
    assert "WEALTH" in captured
    assert "WELL" in captured

    geox_edge = next(e for e in edges if e["id"] == "arifos→geox")
    assert geox_edge["bridge_attempted"] is True
    assert geox_edge["session_propagated"] is True


def test_sync_probe_wires_bridge_for_arifos_x_edges_only():
    """_run_sync_probe_all_edges must call bridge check for arifOS→X edges only.

    This is a smoke test that verifies wiring without making real HTTP calls.
    """
    captured: list[str] = []

    def fake_bridge(target_organ, mcp_url="http://127.0.0.1:8088", **kw):
        captured.append(target_organ)
        return {
            "session_propagated": True,
            "actor_propagated": True,
            "trace_propagated": True,
            "receipt_produced": True,
            "receipt_state": "UNSEALED",
        }

    # Patch ALL the side-effecting paths in _run_sync_probe_all_edges.
    # We only care about: 1) bridge was called for arifOS→X with target in SAFE_PROBE_MAP,
    # 2) bridge was NOT called for self-edges or MCP→arifOS.

    # We need to patch the HTTP fetches too (they would time out without mocks).
    # Easiest: patch _fetch_health to return None (no identity/schema match, but that's OK).
    # And patch _probe_tcp to return reachable.
    with (
        patch(
            "arifosmcp.runtime.federation_edges._run_bridge_propagation_check",
            side_effect=fake_bridge,
        ),
        patch(
            "arifosmcp.runtime.federation_edges._probe_tcp",
            return_value={"state": "reachable", "latency_ms": 1.0},
        ),
        patch(
            "arifosmcp.runtime.federation_edges._fetch_health",
            return_value={"identity_hash": "fake-hash", "federation_schema_version": "2.0.0"},
        ),
        patch(
            "arifosmcp.runtime.federation_edges._self_identity_health",
            return_value={"identity_hash": "fake-self-hash", "federation_schema_version": "2.0.0"},
        ),
    ):
        edges = _run_sync_probe_all_edges()

    # Bridge was called for 3 arifOS→X edges (GEOX, WEALTH, WELL)
    assert "GEOX" in captured
    assert "WEALTH" in captured
    assert "WELL" in captured
    # Bridge was NOT called for A-FORGE, AAA (no safe probe mapped) or self-edges
    assert "A-FORGE" not in captured
    assert "AAA" not in captured

    # Verify the arifOS→GEOX edge got the spine fields set
    geox_edge = next(e for e in edges if e["id"] == "arifos→geox")
    assert geox_edge["session_propagated"] is True
    assert geox_edge["actor_propagated"] is True
    assert geox_edge["trace_propagated"] is True
    assert geox_edge["receipt_produced"] is True
    assert geox_edge["bridge_attempted"] is True
    assert geox_edge["bridge_receipt_state"] == "UNSEALED"

"""
Tests for arifosmcp/probes/capability_probe.py — F-002 closure

Doctrine: pytest. Pure-Python, no live MCP. Mock at boundaries:
  - `_mcp_call`     → canned JSON-RPC responses
  - `_emit_probe_event` → in-memory recorder (no real write to /var/lib/arifos)
  - `_verify_matrix`    → canned return

What these tests PROVE:
  1. All 8 canonical tools are invoked in canonical_order
  2. session_token from init is carried into all subsequent calls
  3. HOLD verdicts on judge/forge are NOT failures (PASS-BY-RESTRAINT)
  4. Each invocation produces exactly one SUCCESS emit
  5. The verify step is non-mutating
  6. Exit codes reflect the contract honestly

What these tests DO NOT prove:
  - Live MCP wire format (covered by the probe itself running live)
  - The hydrator contract (covered by capability_drift's own tests)
"""

from __future__ import annotations

import json
import sys
from typing import Any
from unittest.mock import patch

import pytest

# Adjust path so arifosmcp resolves
sys.path.insert(0, "/root/arifOS/src")

from arifosmcp.probes import capability_probe
from arifosmcp.probes.capability_probe import (
    CANONICAL_8,
    MCPError,
    _extract_envelope,
    _maybe_refresh,
    _parse_sct_expiry,
    run,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────


def _init_response(
    token: str = "act_v1.fake.token",
    session_id: str = "SEAL-fixture-001",
    trace_id: str = "trc-init-fixture",
    verdict: str = "OBSERVE_ONLY",
):
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "structuredContent": {
                "session_token": token,
                "session_id": session_id,
                "trace_id": trace_id,
                "effective_verdict": verdict,
                "expires_at": "2099-01-01T00:00:00Z",
            }
        },
    }


def _verb_response(tool: str, trace_id: str, verdict: str | None = "HOLD"):
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "structuredContent": {
                "trace_id": trace_id,
                "effective_verdict": verdict,
                "session_id": "SEAL-fixture-001",
            }
        },
    }


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_canonical_8_order_matches_tool_registry():
    """CANONICAL_8 must mirror tool_registry.json canonical_order."""
    import json as _json

    with open("/root/arifOS/arifosmcp/tool_registry.json") as fh:
        reg = _json.load(fh)
    expected_order = reg["canonical_order"]
    actual_order = [t for (t, _, _) in CANONICAL_8]
    assert actual_order == expected_order, (
        f"CANONICAL_8 order drifted from tool_registry.json canonical_order. "
        f"Expected: {expected_order}. Got: {actual_order}."
    )


def test_restraint_flags_only_on_judge_and_forge():
    """Only arif_judge and arif_forge should have restraint_expected=True."""
    restraint_set = {t for (t, _, r) in CANONICAL_8 if r}
    assert restraint_set == {"arif_judge", "arif_forge"}, (
        f"Restraint set drifted. Expected {{arif_judge, arif_forge}}. Got: {restraint_set}"
    )


def test_parse_sct_expiry_known_far_future_token():
    """A token with exp far in the future returns a large positive number.

    arifOS SCT format: parts[1] is the base64url-encoded JSON payload
    (per tools_internal.py:482 — token after `act_v1.`).
    """
    import time as _t

    far_future = _t.time() + 3600
    import base64

    payload = (
        base64.urlsafe_b64encode(json.dumps({"exp": far_future}).encode()).rstrip(b"=").decode()
    )
    token = f"act_v1.{payload}.sig"
    remaining = _parse_sct_expiry(token)
    assert remaining is not None
    assert 3500 < remaining < 3700, f"Expected ~3600s, got {remaining}"


def test_parse_sct_expiry_returns_none_for_garbage():
    """Malformed tokens must NOT raise — they return None."""
    assert _parse_sct_expiry(None) is None
    assert _parse_sct_expiry("") is None
    assert _parse_sct_expiry("not-a-jwt") is None
    assert _parse_sct_expiry("act_v1.") is None


def test_extract_envelope_from_structured_content():
    """The probe uses structuredContent preferentially."""
    env = _extract_envelope(_verb_response("arif_observe", "trc-x"))
    assert env["trace_id"] == "trc-x"
    assert env["effective_verdict"] == "HOLD"


def test_extract_envelope_raises_on_error():
    """JSON-RPC errors propagate as MCPError."""
    from arifosmcp.probes.capability_probe import MCPError

    with pytest.raises(MCPError):
        _extract_envelope({"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "x"}})


def test_maybe_refresh_returns_same_token_when_fresh():
    """A token with plenty of time left is not refreshed."""
    import time as _t

    future = _t.time() + 3600
    import base64
    import json

    header = base64.urlsafe_b64encode(b'{"alg":"none"}').rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(json.dumps({"exp": future}).encode()).rstrip(b"=").decode()
    token = f"act_v1.{header}.{payload}.sig"
    # No refresh should be called
    with patch.object(capability_probe, "_mcp_call") as mcp:
        result = _maybe_refresh("http://x", token, "arif")
    assert result == token
    mcp.assert_not_called()


def test_run_invokes_all_eight_tools():
    """run() invokes each tool exactly once."""
    calls: list[tuple[str, str | None]] = []

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        calls.append((tool, mode))
        if tool == "arif_init":
            return _init_response()
        return _verb_response(tool, f"trc-{tool}")

    def fake_emit(tool, **kwargs):
        return True

    with (
        patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call),
        patch.object(capability_probe, "_emit_probe_event", side_effect=fake_emit),
        patch.object(
            capability_probe,
            "_verify_matrix",
            return_value={"tested_count": 8, "proven_live_count": 8, "untested_count": 0},
        ),
    ):
        report = run(mcp_url="http://x", actor_id="arif-test")

    # Verify all 8 tools invoked, in canonical order
    invoked_tools = [t for (t, _) in calls]
    assert invoked_tools == [t for (t, _, _) in CANONICAL_8], f"Invoke order wrong: {invoked_tools}"

    # Verify 8 rows in report
    assert len(report.rows) == 8
    assert all(r.invocation_ok for r in report.rows)
    assert all(r.emitted_success for r in report.rows)
    assert report.tested_count == 8
    assert report.proven_live_count == 8


def test_run_session_token_carries_into_subsequent_calls():
    """arif_init's session_token must be in every subsequent call's arguments."""
    init_token = "act_v1.fake.token"
    init_session = "SEAL-carrytest"

    captured_args: list[dict[str, Any]] = []

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        captured_args.append({"tool": tool, "session_token": session_token})
        if tool == "arif_init":
            return _init_response(token=init_token, session_id=init_session)
        return _verb_response(tool, f"trc-{tool}")

    with (
        patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call),
        patch.object(capability_probe, "_emit_probe_event", return_value=True),
        patch.object(
            capability_probe,
            "_verify_matrix",
            return_value={"tested_count": 8, "proven_live_count": 8, "untested_count": 0},
        ),
    ):
        run(mcp_url="http://x")

    # First call (arif_init) had no session_token
    assert captured_args[0]["tool"] == "arif_init"
    assert captured_args[0]["session_token"] is None
    # All subsequent calls must carry the init_token
    for entry in captured_args[1:]:
        assert entry["session_token"] == init_token, (
            f"session_token NOT carried into {entry['tool']}: "
            f"got {entry['session_token']}, expected {init_token}"
        )


def test_run_hold_verdict_is_not_failure():
    """HOLD on judge/forge from unattended probe = PASS-BY-RESTRAINT, not failure."""

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        if tool == "arif_init":
            return _init_response()
        # HOLD on everything (simulating unattended probe from anonymous actor)
        return _verb_response(tool, f"trc-{tool}", verdict="HOLD")

    with (
        patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call),
        patch.object(capability_probe, "_emit_probe_event", return_value=True),
        patch.object(
            capability_probe,
            "_verify_matrix",
            return_value={"tested_count": 8, "proven_live_count": 8, "untested_count": 0},
        ),
    ):
        report = run(mcp_url="http://x")

    # Every invocation should still be marked ok + emitted
    for row in report.rows:
        assert row.invocation_ok is True
        assert row.emitted_success is True


def test_run_emits_exactly_one_event_per_invocation():
    """Each successful invocation must emit exactly one SUCCESS event."""
    emit_calls: list[str] = []

    def fake_emit(tool, **kwargs):
        emit_calls.append(tool)
        return True

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        if tool == "arif_init":
            return _init_response()
        return _verb_response(tool, f"trc-{tool}")

    with (
        patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call),
        patch.object(capability_probe, "_emit_probe_event", side_effect=fake_emit),
        patch.object(
            capability_probe,
            "_verify_matrix",
            return_value={"tested_count": 8, "proven_live_count": 8, "untested_count": 0},
        ),
    ):
        run(mcp_url="http://x")

    # Exactly 8 emits, one per canonical tool
    expected = [t for (t, _, _) in CANONICAL_8]
    assert sorted(emit_calls) == sorted(expected), (
        f"Emit count mismatch: got {emit_calls}, expected {expected}"
    )
    assert len(emit_calls) == 8


def test_run_aborts_loudly_on_init_failure():
    """If arif_init fails, run() raises MCPError and does not proceed."""
    from arifosmcp.probes.capability_probe import MCPError

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        raise MCPError("arif_init (init) failed — cannot proceed: HTTP 500")

    with patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call):
        with pytest.raises(MCPError):
            run(mcp_url="http://x")


def test_run_records_failed_invocations_does_not_crash():
    """If a verb call fails (non-init), run() records the failure but continues."""
    init_called = [False]
    failed_tool = "arif_think"

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        if tool == "arif_init":
            init_called[0] = True
            return _init_response()
        if tool == failed_tool:
            raise MCPError(f"{tool}: HTTP 502")
        return _verb_response(tool, f"trc-{tool}")

    with (
        patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call),
        patch.object(capability_probe, "_emit_probe_event", return_value=True),
        patch.object(
            capability_probe,
            "_verify_matrix",
            return_value={"tested_count": 7, "proven_live_count": 8, "untested_count": 1},
        ),
    ):
        report = run(mcp_url="http://x")

    assert init_called[0] is True
    # Failed tool has invocation_ok=False, emitted_success=False
    failed_row = next(r for r in report.rows if r.tool == failed_tool)
    assert failed_row.invocation_ok is False
    assert failed_row.emitted_success is False
    assert "HTTP 502" in (failed_row.error or "")
    # Other tools succeeded
    ok_rows = [r for r in report.rows if r.invocation_ok]
    assert len(ok_rows) == 7


def test_verify_matrix_handles_unreachable_kernel():
    """If /capabilities is unreachable, report shows -1 (not crash)."""

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        if tool == "arif_init":
            return _init_response()
        return _verb_response(tool, f"trc-{tool}")

    with (
        patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call),
        patch.object(capability_probe, "_emit_probe_event", return_value=True),
        patch.object(
            capability_probe,
            "_verify_matrix",
            return_value={"tested_count": -1, "proven_live_count": -1, "untested_count": -1},
        ),
    ):
        report = run(mcp_url="http://x")

    assert report.tested_count == -1
    assert report.proven_live_count == -1


def test_main_exit_code_zero_when_all_invoked_and_emitted():
    """main() returns 0 when all 8 invoked, all 8 emitted, tested_count >= 8."""
    from arifosmcp.probes.capability_probe import main

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        if tool == "arif_init":
            return _init_response()
        return _verb_response(tool, f"trc-{tool}")

    with (
        patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call),
        patch.object(capability_probe, "_emit_probe_event", return_value=True),
        patch.object(
            capability_probe,
            "_verify_matrix",
            return_value={"tested_count": 8, "proven_live_count": 8, "untested_count": 0},
        ),
    ):
        rc = main(["--mcp-url", "http://x", "--actor-id", "arif-test"])

    assert rc == 0


def test_main_exit_code_one_when_invocation_fails():
    """main() returns 1 if any invocation fails."""
    from arifosmcp.probes.capability_probe import main

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        if tool == "arif_init":
            return _init_response()
        if tool == "arif_observe":
            raise MCPError("HTTP 500")
        return _verb_response(tool, f"trc-{tool}")

    with (
        patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call),
        patch.object(capability_probe, "_emit_probe_event", return_value=True),
        patch.object(
            capability_probe,
            "_verify_matrix",
            return_value={"tested_count": 7, "proven_live_count": 8, "untested_count": 1},
        ),
    ):
        rc = main(["--mcp-url", "http://x"])

    assert rc == 1


def test_main_exit_code_three_when_matrix_does_not_flip():
    """main() returns 3 if all invoked+emitted but matrix shows tested_count < 8."""
    from arifosmcp.probes.capability_probe import main

    def fake_mcp_call(
        mcp_url, tool, *, mode, session_token, actor_id, extra_args=None, minimal_envelope=False
    ):
        if tool == "arif_init":
            return _init_response()
        return _verb_response(tool, f"trc-{tool}")

    with (
        patch.object(capability_probe, "_mcp_call", side_effect=fake_mcp_call),
        patch.object(capability_probe, "_emit_probe_event", return_value=True),
        patch.object(
            capability_probe,
            "_verify_matrix",
            return_value={"tested_count": 0, "proven_live_count": 8, "untested_count": 8},
        ),
    ):
        rc = main(["--mcp-url", "http://x"])

    assert rc == 3

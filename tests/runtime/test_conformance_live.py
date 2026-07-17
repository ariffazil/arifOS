"""Tests for the live conformance runner (Epoch 1 / Item 4).

Proves the F13 audit exit condition for the conformance spine:

  - Skipped checks return UNKNOWN, never PASS.
  - Aggregation: Any P0 FAIL -> FAIL; No FAIL but P0 UNKNOWN -> HOLD;
    All required PASS -> PASS.
  - The runner uses real kernel invocations, not registry reads.

These tests do not require a live kernel. They prove the runner logic
against a stub kernel and against the kernel-unreachable case.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch


# ── Aggregation: the four-state formula ───────────────────────────────────


def test_aggregate_any_p0_fail_is_fail():
    from arifosmcp.runtime.conformance_live import (
        AGGREGATE_FAIL,
        FAIL,
        PASS,
        UNKNOWN,
        CheckResult,
        aggregate,
    )

    checks = [
        CheckResult(name="a", priority="P0", state=PASS,
                    expected="", actual="ok"),
        CheckResult(name="b", priority="P0", state=FAIL,
                    expected="x", actual="y"),
        CheckResult(name="c", priority="P1", state=PASS,
                    expected="", actual="ok"),
    ]
    assert aggregate(checks) == AGGREGATE_FAIL


def test_aggregate_no_fail_but_p0_unknown_is_hold():
    from arifosmcp.runtime.conformance_live import (
        AGGREGATE_HOLD,
        PASS,
        UNKNOWN,
        CheckResult,
        aggregate,
    )

    checks = [
        CheckResult(name="a", priority="P0", state=PASS,
                    expected="", actual="ok"),
        CheckResult(name="b", priority="P0", state=UNKNOWN,
                    expected="x", actual="kernel unreachable"),
        CheckResult(name="c", priority="P1", state=PASS,
                    expected="", actual="ok"),
    ]
    assert aggregate(checks) == AGGREGATE_HOLD


def test_aggregate_all_required_pass_is_pass():
    from arifosmcp.runtime.conformance_live import (
        AGGREGATE_PASS,
        NOT_APPLICABLE,
        PASS,
        UNKNOWN,
        CheckResult,
        aggregate,
    )

    checks = [
        CheckResult(name="a", priority="P0", state=PASS,
                    expected="", actual="ok"),
        CheckResult(name="b", priority="P0", state=PASS,
                    expected="", actual="ok"),
        # P1 UNKNOWN is not a hold trigger — only P0 UNKNOWN triggers HOLD.
        CheckResult(name="c", priority="P1", state=UNKNOWN,
                    expected="", actual="optional"),
        CheckResult(name="d", priority="P2", state=NOT_APPLICABLE,
                    expected="", actual="legitimately irrelevant"),
    ]
    assert aggregate(checks) == AGGREGATE_PASS


def test_aggregate_p1_unknown_alone_is_pass():
    """A non-P0 UNKNOWN does not block the aggregate from passing."""
    from arifosmcp.runtime.conformance_live import (
        AGGREGATE_PASS,
        PASS,
        UNKNOWN,
        CheckResult,
        aggregate,
    )

    checks = [
        CheckResult(name="a", priority="P0", state=PASS, expected="", actual="ok"),
        CheckResult(name="b", priority="P1", state=UNKNOWN, expected="", actual="x"),
    ]
    assert aggregate(checks) == AGGREGATE_PASS


def test_aggregate_skipped_is_never_pass():
    """A skipped check is UNKNOWN, never PASS."""
    from arifosmcp.runtime.conformance_live import (
        AGGREGATE_HOLD,
        UNKNOWN,
        CheckResult,
        aggregate,
    )

    checks = [
        CheckResult(name="a", priority="P0", state=UNKNOWN,
                    expected="x", actual="could_not_run: kernel timeout"),
    ]
    assert aggregate(checks) == AGGREGATE_HOLD


# ── Runner: kernel-unreachable path ───────────────────────────────────────


def test_run_conformance_kernel_unreachable_returns_hold():
    """When the kernel is down, every P0 check is UNKNOWN -> aggregate HOLD."""
    from arifosmcp.runtime.conformance_live import (
        AGGREGATE_HOLD,
        run_conformance,
    )

    with patch(
        "arifosmcp.runtime.conformance_live._kernel_reachable",
        return_value=(False, "connection refused"),
    ):
        report = run_conformance()

    assert report.aggregate_state == AGGREGATE_HOLD
    assert report.failed == 0  # No FAIL — kernel is just unreachable.
    assert report.unknown > 0
    assert report.passed == 0  # Skipped checks cannot count as PASS.


def test_run_conformance_kernel_unreachable_does_not_count_skipped_as_pass():
    """The audit exit condition: skipped checks cannot inflate the PASS count."""
    from arifosmcp.runtime.conformance_live import run_conformance

    with patch(
        "arifosmcp.runtime.conformance_live._kernel_reachable",
        return_value=(False, "down"),
    ):
        report = run_conformance()

    # No check should report PASS when the kernel is unreachable.
    assert report.passed == 0
    # Every check is UNKNOWN.
    assert all(c.state == "UNKNOWN" for c in report.checks)


# ── Runner: kernel-reachable path with mocked MCP responses ───────────────


def _mock_initialize_response() -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2025-11-25",
            "serverInfo": {"name": "arifOS", "version": "1.0.0"},
            "capabilities": {"tools": {}},
        },
    }


def _mock_tools_list_response() -> dict[str, Any]:
    canonical = [
        "arif_init", "arif_observe", "arif_think", "arif_route",
        "arif_memory", "arif_judge", "arif_forge", "arif_seal",
    ]
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"tools": [{"name": n} for n in canonical]},
    }


def _mock_canonical_tool_response() -> dict[str, Any]:
    """A response with ONLY the canonical envelope (no legacy fields)."""
    import json
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "status": "completed",
                    "effective_verdict": "OBSERVE_ONLY",
                    "reason_code": "NO_IDENTITY_BOUND",
                    "next_action": "BIND_IDENTITY",
                    "standing": {
                        "session_id": "anonymous",
                        "actor": {
                            "claimed_id": "anonymous",
                            "canonical_id": "anonymous",
                            "verified": False,
                            "verification_method": None,
                        },
                        "authority": {
                            "band": "OBSERVE_ONLY",
                            "mutation_allowed": False,
                            "seal_allowed": False,
                        },
                        "issued_at": "2026-07-17T00:00:00+00:00",
                        "expires_at": "2026-07-18T00:00:00+00:00",
                        "state_version": 1,
                    },
                }),
            }],
            "isError": False,
        },
    }


def _mock_legacy_tool_response() -> dict[str, Any]:
    """A response with legacy fields — must FAIL the tool-invocation check."""
    import json
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "status": "ok",
                    "actor_verified": True,
                    "authority_level": "OPERATOR",
                    "verdict": "SEAL",
                    "verdict_code": "OK",
                }),
            }],
            "isError": False,
        },
    }


def test_run_conformance_canonical_envelope_passes():
    """If every tool returns the canonical envelope only, aggregate is PASS."""
    from arifosmcp.runtime.conformance_live import (
        AGGREGATE_PASS,
        run_conformance,
    )

    def _mock_unknown_tool_response() -> dict[str, Any]:
        """An MCP error response for an unknown tool name."""
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": {"tool": "arif_nonexistent_tool"},
            },
        }

    def _route(method, params=None, session_id=None, timeout=5.0):
        if method == "initialize":
            return _mock_initialize_response()
        if method == "notifications/initialized":
            return {"result": {}}
        if method == "tools/list":
            return _mock_tools_list_response()
        if method == "resources/list":
            return {"result": {"resources": [{"uri": "arifos://session/test"}]}}
        if method == "resources/templates/list":
            return {"result": {"resourceTemplates": []}}
        if method == "prompts/list":
            return {"result": {"prompts": []}}
        if method == "tools/call":
            name = (params or {}).get("name")
            if name == "arif_nonexistent_tool":
                return _mock_unknown_tool_response()
            return _mock_canonical_tool_response()
        return {"result": {}}

    with patch(
        "arifosmcp.runtime.conformance_live._kernel_reachable",
        return_value=(True, "ok"),
    ), patch(
        "arifosmcp.runtime.conformance_live._mcp_post",
        side_effect=_route,
    ):
        report = run_conformance()

    # With canonical-only responses, every P0 check should pass.
    p0_checks = [c for c in report.checks if c.priority == "P0"]
    p0_failures = [c for c in p0_checks if c.state == "FAIL"]
    assert not p0_failures, f"P0 failures: {[c.name for c in p0_failures]}"
    assert report.aggregate_state == AGGREGATE_PASS


def test_run_conformance_legacy_response_fails():
    """If a tool returns legacy fields, the tool-invocation check FAILs -> aggregate FAIL."""
    from arifosmcp.runtime.conformance_live import (
        AGGREGATE_FAIL,
        run_conformance,
    )

    with patch(
        "arifosmcp.runtime.conformance_live._kernel_reachable",
        return_value=(True, "ok"),
    ), patch(
        "arifosmcp.runtime.conformance_live._mcp_post",
        side_effect=lambda method, params=None, session_id=None, timeout=5.0: (
            _mock_initialize_response() if method == "initialize"
            else {"result": {}} if method == "notifications/initialized"
            else _mock_tools_list_response() if method == "tools/list"
            else {"result": {"resources": []}} if method == "resources/list"
            else {"result": {"resourceTemplates": []}} if method == "resources/templates/list"
            else {"result": {"prompts": []}} if method == "prompts/list"
            else _mock_legacy_tool_response() if method == "tools/call"
            else {"result": {}}
        ),
    ):
        report = run_conformance()

    assert report.aggregate_state == AGGREGATE_FAIL
    assert report.failed > 0


def test_run_conformance_missing_canonical_blocks_fails():
    """If a response is missing `standing` or `effective_verdict`, the tool check FAILs."""
    from arifosmcp.runtime.conformance_live import (
        AGGREGATE_FAIL,
        run_conformance,
    )

    bare_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": '{"status": "ok"}'}],
            "isError": False,
        },
    }

    with patch(
        "arifosmcp.runtime.conformance_live._kernel_reachable",
        return_value=(True, "ok"),
    ), patch(
        "arifosmcp.runtime.conformance_live._mcp_post",
        side_effect=lambda method, params=None, session_id=None, timeout=5.0: (
            _mock_initialize_response() if method == "initialize"
            else {"result": {}} if method == "notifications/initialized"
            else _mock_tools_list_response() if method == "tools/list"
            else {"result": {"resources": []}} if method == "resources/list"
            else {"result": {"resourceTemplates": []}} if method == "resources/templates/list"
            else {"result": {"prompts": []}} if method == "prompts/list"
            else bare_response if method == "tools/call"
            else {"result": {}}
        ),
    ):
        report = run_conformance()

    assert report.aggregate_state == AGGREGATE_FAIL


def test_run_conformance_has_eighteen_checks():
    """The audit's minimum live test suite is 18 checks. The runner must cover all of them."""
    from arifosmcp.runtime.conformance_live import ALL_CHECKS, run_conformance

    assert len(ALL_CHECKS) == 18

    with patch(
        "arifosmcp.runtime.conformance_live._kernel_reachable",
        return_value=(False, "down"),
    ):
        report = run_conformance()
    assert len(report.checks) == 18


# ── Report shape ──────────────────────────────────────────────────────────


def test_report_serializable_to_dict():
    from arifosmcp.runtime.conformance_live import run_conformance

    with patch(
        "arifosmcp.runtime.conformance_live._kernel_reachable",
        return_value=(False, "down"),
    ):
        report = run_conformance()

    as_dict = report.to_dict()
    assert "aggregate_state" in as_dict
    assert "checks" in as_dict
    assert as_dict["total_checks"] == 18
    assert all("name" in c and "state" in c for c in as_dict["checks"])


def test_check_states_are_closed():
    """The four-state taxonomy is closed."""
    from arifosmcp.runtime.conformance_live import (
        CANONICAL_STATES,
        FAIL,
        NOT_APPLICABLE,
        PASS,
        UNKNOWN,
    )

    assert CANONICAL_STATES == frozenset({PASS, FAIL, UNKNOWN, NOT_APPLICABLE})
    assert len(CANONICAL_STATES) == 4
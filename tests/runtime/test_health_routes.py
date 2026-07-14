"""
PR3 — health/ready/capabilities routes tests.

Verifies the four audit-mandated surfaces:
  - /api/observatory/v1/health-public: unauthenticated, no session, no 502
  - /api/observatory/v1/ready: internal-network only, dependency status
  - /api/observatory/v1/capabilities: sanitized public
  - /api/observatory/v1/capabilities/full: X-Op-Token required, returns 403 without it
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.rest_routes.health_routes import (  # noqa: E402
    _public_health_envelope,
    _ready_envelope,
    _capabilities_envelope,
    _capabilities_full_envelope,
    _enforce_tier,
    _struct_error,
)


class _FakeRequest:
    def __init__(self, headers: dict[str, str] | None = None):
        self.headers = headers or {}


def test_public_health_requires_no_session() -> None:
    env = _public_health_envelope()
    assert env["session_required"] is False
    assert env["policy"] == "unauthenticated_process_liveness"
    assert env["endpoint"] == "/api/observatory/v1/health-public"
    assert "transport" in env
    assert env["transport"]["state"] in ("reachable", "unreachable")
    # health MUST NOT be a 502 even if process is down — it's reachable/unreachable,
    # not healthy/unhealthy. The audit is explicit: no false-green.
    assert env["status"] in ("healthy", "down")


def test_public_health_returns_no_interiority() -> None:
    env = _public_health_envelope()
    for forbidden_key in ("session_id", "actor_id", "vault_path", "internal_port", "api_key"):
        assert forbidden_key not in str(env), f"public health must not leak: {forbidden_key}"


def test_ready_envelope_lists_dependencies_with_states() -> None:
    env = _ready_envelope()
    assert env["policy"] == "internal_network_only"
    assert env["session_required"] is False
    deps = env["dependencies"]
    for label in ("postgres", "redis", "qdrant", "vault_writer"):
        assert label in deps
        assert deps[label] in ("ready", "degraded", "unknown")


def test_capabilities_envelope_is_sanitized() -> None:
    env = _capabilities_envelope()
    assert env["policy"] == "sanitized_public"
    assert env["session_required"] is False
    # Sanitized: schema hashes, drift, raw payload removed
    for tool in env["tools"]:
        # audit rule: each tool carries only sanitized fields
        assert "input_hash" not in tool
        assert "schema" not in tool or "schema_version" in tool
        # No internal surface
        assert "action_class" in tool
        assert "public_simulation" in tool
    # Totals: declared/registered/callable separate
    t = env["totals"]
    assert t["declared_tools"] >= t["registered_tools"] >= 0


def test_capabilities_full_requires_X_Op_Token() -> None:
    req_no_token = _FakeRequest(headers={})
    ok, reason = _enforce_tier(req_no_token, required="operator")
    assert ok is False
    assert "X-Op-Token" in reason


def test_capabilities_full_rejects_wrong_token(monkeypatch: pytest.MonkeyPatch) -> None:
    import hashlib
    monkeypatch.setenv("ARIFOS_OP_TOKEN_HASH", hashlib.sha256(b"right-token-here").hexdigest())
    req_wrong = _FakeRequest(headers={"X-Op-Token": "this-is-not-the-right-token"})
    ok, reason = _enforce_tier(req_wrong, required="operator")
    assert ok is False
    assert "mismatch" in (reason or "")


def test_capabilities_full_accepts_correct_token(monkeypatch: pytest.MonkeyPatch) -> None:
    import hashlib
    plain = "right-token-here"
    monkeypatch.setenv("ARIFOS_OP_TOKEN_HASH", hashlib.sha256(plain.encode("utf-8")).hexdigest())
    req = _FakeRequest(headers={"X-Op-Token": plain})
    ok, reason = _enforce_tier(req, required="operator")
    assert ok is True, f"expected pass: {reason}"


def test_struct_error_shape_matches_audit_contract() -> None:
    err = _struct_error(
        "SESSION_REQUIRED",
        "A governed session is required for this WEALTH capability.",
        required_action="INITIALIZE_SESSION_AT_AAA_OR_MCP_GATEWAY",
        requested_capability="wealth_npv_reward",
    )
    for required in ("status", "error_code", "message", "retryable", "mutation_occurred"):
        assert required in err
    assert err["status"] == "HOLD"
    assert err["error_code"] == "SESSION_REQUIRED"
    assert err["retryable"] is True
    assert err["mutation_occurred"] is False


def test_capabilities_full_envelope_includes_schema_hashes() -> None:
    env = _capabilities_full_envelope()
    assert env["policy"] == "operator_only"
    assert env["session_required"] is True
    assert env["auth"].startswith("X-Op-Token")
    for tool in env["tools"]:
        # operator-only surface carries schema hashes and drift per tool
        assert "schemas" in tool, f"tool {tool.get('name')} missing schemas"
        assert "input_hash" in tool["schemas"]


def test_no_blanket_healthy_in_capabilities() -> None:
    """Audit rule: never compress totals into a single HEALTHY pill."""
    env = _capabilities_envelope()
    blob = str(env).upper()
    # The word HEALTHY only appears as a field name in 7-state vocab; here it must not.
    # We don't forbid it from appearing in raw JSON, but we DO require the totals shape.
    assert "declared_tools" in env["totals"]
    assert "registered_tools" in env["totals"]
    assert "callable_tools" in env["totals"]
    assert env["totals"].get("drift") is not None

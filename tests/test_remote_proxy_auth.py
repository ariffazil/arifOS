"""Path-B remote organ proxy lightweight session gate (2026-07-09)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from arifosmcp.runtime.remote_proxy_auth import (
    deny_payload,
    extract_proxy_auth,
    inject_session_params,
    remote_proxy_auth_enabled,
    require_remote_proxy_session,
    strip_auth_args,
)


class TestExtractAndStrip:
    def test_extract_from_args_and_envelope(self) -> None:
        sid, aid = extract_proxy_auth(
            {
                "cash_flows": [-100, 110],
                "session_id": "sess-1",
                "actor_id": "agent-x",
            }
        )
        assert sid == "sess-1"
        assert aid == "agent-x"

        sid2, aid2 = extract_proxy_auth(
            {"_envelope": {"session_id": "sess-env", "actor_id": "arif"}}
        )
        assert sid2 == "sess-env"
        assert aid2 == "arif"

    def test_extract_from_headers(self) -> None:
        sid, _ = extract_proxy_auth({}, headers={"Mcp-Session-Id": "hdr-sess"})
        assert sid == "hdr-sess"

    def test_strip_auth_args(self) -> None:
        out = strip_auth_args(
            {
                "cash_flows": [-100, 110],
                "session_id": "s",
                "actor_id": "a",
                "_envelope": {},
            }
        )
        assert out == {"cash_flows": [-100, 110]}


class TestRequireSession:
    def test_deny_missing_session(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ARIFOS_SESSION_ID", raising=False)
        monkeypatch.delenv("ARIFOS_DEFAULT_SESSION_ID", raising=False)
        monkeypatch.delenv("ARIFOS_ACTOR_ID", raising=False)
        monkeypatch.setenv("ARIFOS_REMOTE_PROXY_AUTH", "true")

        with patch(
            "arifosmcp.runtime.session_auth.validate_session",
            return_value={
                "valid": False,
                "reason": "L11 AUTH: session_id missing",
                "session": None,
            },
        ):
            gate = require_remote_proxy_session(
                tool_name="wealth_compute_irr",
                organ="WEALTH",
                arguments={"cash_flows": [-100, 110]},
            )
        assert gate["ok"] is False
        assert gate["code"] == "SESSION_REQUIRED"
        assert "session_id required" in gate["reason"]
        assert gate["forward_args"] == {"cash_flows": [-100, 110]}

    def test_allow_valid_session(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ARIFOS_REMOTE_PROXY_AUTH", "true")
        with patch(
            "arifosmcp.runtime.session_auth.validate_session",
            return_value={
                "valid": True,
                "reason": "L11 AUTH: session valid",
                "actor_id": "arif",
                "session": {"session_id": "good", "actor_id": "arif"},
            },
        ):
            gate = require_remote_proxy_session(
                tool_name="wealth_compute_irr",
                organ="WEALTH",
                arguments={
                    "cash_flows": [-100, 110],
                    "session_id": "good",
                    "actor_id": "arif",
                },
            )
        assert gate["ok"] is True
        assert gate["code"] == "OK"
        assert gate["forward_args"] == {"cash_flows": [-100, 110]}
        assert "session_id" not in gate["forward_args"]

    def test_disabled_bypass(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ARIFOS_REMOTE_PROXY_AUTH", "false")
        gate = require_remote_proxy_session(
            tool_name="well_status",
            organ="WELL",
            arguments={},
        )
        assert gate["ok"] is True
        assert gate["code"] == "DISABLED"

    def test_deny_payload_shape(self) -> None:
        hold = deny_payload(
            {
                "ok": False,
                "code": "SESSION_REQUIRED",
                "reason": "need session",
                "session_id": None,
                "actor_id": None,
            },
            organ="WEALTH",
            tool_name="wealth_compute_irr",
        )
        assert hold["status"] == "HOLD"
        assert hold["execution_authorized"] is False
        assert hold["path"] == "B"
        assert hold["gate"] == "remote_proxy_auth"


class TestSchemaInject:
    def test_inject_requires_session_id(self) -> None:
        schema = inject_session_params(
            {
                "type": "object",
                "properties": {"cash_flows": {"type": "array"}},
                "required": ["cash_flows"],
            }
        )
        assert "session_id" in schema["properties"]
        assert "session_id" in schema["required"]
        assert "cash_flows" in schema["required"]


def test_auth_enabled_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARIFOS_REMOTE_PROXY_AUTH", raising=False)
    assert remote_proxy_auth_enabled() is True

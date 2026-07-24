"""Path-B remote organ proxy lightweight session gate (2026-07-09, hardened 2026-07-23)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from arifosmcp.runtime.remote_proxy_auth import (
    build_federation_envelope,
    deny_payload,
    extract_proxy_auth,
    inject_session_params,
    remote_proxy_auth_enabled,
    require_remote_proxy_session,
    strip_auth_args,
)


class TestExtractAndStrip:
    def test_extract_from_args_and_envelope(self) -> None:
        sid, aid, stoken = extract_proxy_auth(
            {
                "cash_flows": [-100, 110],
                "session_id": "sess-1",
                "actor_id": "agent-x",
            }
        )
        assert sid == "sess-1"
        assert aid == "agent-x"
        assert stoken is None

        sid2, aid2, stoken2 = extract_proxy_auth(
            {
                "_envelope": {
                    "session_id": "sess-env",
                    "actor_id": "arif",
                    "session_token": "sct-xyz",
                }
            }
        )
        assert sid2 == "sess-env"
        assert aid2 == "arif"
        assert stoken2 == "sct-xyz"

    def test_extract_from_headers(self) -> None:
        sid, _, _ = extract_proxy_auth({}, headers={"Mcp-Session-Id": "hdr-sess"})
        assert sid == "hdr-sess"

    def test_extract_session_token_from_header(self) -> None:
        _, _, stoken = extract_proxy_auth(
            {}, headers={"X-ArifOS-Session-Token": "sct-hdr"}
        )
        assert stoken == "sct-hdr"

    def test_strip_auth_args(self) -> None:
        out = strip_auth_args(
            {
                "cash_flows": [-100, 110],
                "session_id": "s",
                "actor_id": "a",
                "session_token": "st",
                "_envelope": {},
                "trace_id": "t",
            }
        )
        assert out == {"cash_flows": [-100, 110]}


class TestEnvelope:
    def test_build_federation_envelope_defaults(self) -> None:
        env = build_federation_envelope(
            session_id="sess-1",
            actor_id="arif",
            session_token="sct-xyz",
        )
        assert env["session_id"] == "sess-1"
        assert env["actor_id"] == "arif"
        assert env["session_token"] == "sct-xyz"
        assert env["authority"] == "OBSERVE_ONLY"
        assert env["source"] == "arifOS_kernel"
        assert env["path"] == "B"
        assert env["envelope_version"] == "1"
        assert env["actor_verified"] is False
        assert isinstance(env["issued_at"], int)

    def test_envelope_observes_only_cap(self) -> None:
        # Even with a higher trust tier on the session, the envelope is
        # OBSERVE_ONLY — Path B is read-side, never mutation-side.
        env = build_federation_envelope(
            session_id="s",
            actor_id="arif",
            session_token="t",
            authority="SOVEREIGN",
        )
        assert env["authority"] == "OBSERVE_ONLY"
        from arifosmcp.runtime.remote_proxy_auth import ENVELOPE_AUTHORITY

        assert ENVELOPE_AUTHORITY == "OBSERVE_ONLY"


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
        assert gate["envelope"] == {}

    def test_allow_valid_session(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ARIFOS_REMOTE_PROXY_AUTH", "true")
        with patch(
            "arifosmcp.runtime.session_auth.validate_session",
            return_value={
                "valid": True,
                "reason": "L11 AUTH: session valid",
                "actor_id": "arif",
                "session_id": "good",
                "session_token": "sct-abc",
                "authority": "OBSERVE_ONLY",
                "actor_verified": True,
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
        # session_id/actor_id/_envelope MUST NOT be forwarded as caller-supplied fields.
        assert "session_id" not in gate["forward_args"]
        assert "actor_id" not in gate["forward_args"]
        assert "_envelope" not in gate["forward_args"]
        # Kernel-authored envelope is populated and OBSERVE_ONLY.
        assert gate["envelope"]["session_id"] == "good"
        assert gate["envelope"]["actor_id"] == "arif"
        assert gate["envelope"]["session_token"] == "sct-abc"
        assert gate["envelope"]["authority"] == "OBSERVE_ONLY"
        assert gate["envelope"]["source"] == "arifOS_kernel"
        assert gate["envelope"]["path"] == "B"

    def test_disabled_deny(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # B4: ARIFOS_REMOTE_PROXY_AUTH=false is HOLD, never anonymous ALLOW.
        monkeypatch.setenv("ARIFOS_REMOTE_PROXY_AUTH", "false")
        gate = require_remote_proxy_session(
            tool_name="well_status",
            organ="WELL",
            arguments={"session_id": "spoofed", "actor_id": "attacker"},
        )
        assert gate["ok"] is False
        assert gate["code"] == "DISABLED"
        assert "Path B disabled" in gate["reason"]
        # No validated envelope on denial.
        assert gate["envelope"] == {}
        # Caller-supplied auth STILL must not leak forward as business args.
        assert "session_id" not in gate["forward_args"]
        assert "actor_id" not in gate["forward_args"]

    def test_deny_invalid_session(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ARIFOS_REMOTE_PROXY_AUTH", "true")
        with patch(
            "arifosmcp.runtime.session_auth.validate_session",
            return_value={
                "valid": False,
                "reason": "L11 AUTH: session_id not found or expired",
                "session": None,
            },
        ):
            gate = require_remote_proxy_session(
                tool_name="wealth_compute_irr",
                organ="WEALTH",
                arguments={"session_id": "bogus", "cash_flows": [-100, 110]},
            )
        assert gate["ok"] is False
        assert gate["code"] == "SESSION_INVALID"
        assert gate["envelope"] == {}
        assert gate["forward_args"] == {"cash_flows": [-100, 110]}

    def test_deny_actor_mismatch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ARIFOS_REMOTE_PROXY_AUTH", "true")
        with patch(
            "arifosmcp.runtime.session_auth.validate_session",
            return_value={
                "valid": False,
                "reason": "L11 AUTH: actor_id mismatch",
                "session": {"session_id": "sess-1", "actor_id": "arif"},
                "actor_id": "arif",
            },
        ):
            gate = require_remote_proxy_session(
                tool_name="wealth_compute_irr",
                organ="WEALTH",
                arguments={
                    "session_id": "sess-1",
                    "actor_id": "attacker",
                    "cash_flows": [-100, 110],
                },
            )
        assert gate["ok"] is False
        assert gate["code"] == "SESSION_MISMATCH"
        assert gate["envelope"] == {}

    def test_spoofed_envelope_discarded(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Caller tries to inject a fake _envelope claiming high authority.
        # L11 validates the real session; the kernel envelope must be built
        # from validated fields only, never the caller's spoofed payload.
        monkeypatch.setenv("ARIFOS_REMOTE_PROXY_AUTH", "true")
        caller_envelope = {
            "session_id": "spoofed-good",
            "actor_id": "spoofed-sovereign",
            "session_token": "sct-fake",
            "authority": "SOVEREIGN",
            "actor_verified": True,
            "source": "i_promise_im_the_kernel",
        }
        with patch(
            "arifosmcp.runtime.session_auth.validate_session",
            return_value={
                "valid": True,
                "reason": "L11 AUTH: session valid",
                "actor_id": "arif",
                "session_id": "real-good",
                "session_token": "sct-real",
                "authority": "OBSERVE_ONLY",
                "actor_verified": True,
                "session": {"session_id": "real-good", "actor_id": "arif"},
            },
        ):
            gate = require_remote_proxy_session(
                tool_name="wealth_compute_irr",
                organ="WEALTH",
                arguments={
                    "session_id": "real-good",
                    "actor_id": "arif",
                    "_envelope": caller_envelope,
                    "cash_flows": [-100, 110],
                },
            )
        assert gate["ok"] is True
        # Spoofed envelope did NOT survive in forward_args.
        assert "_envelope" not in gate["forward_args"]
        # Kernel envelope uses only validated fields, NOT the spoofed claims.
        env = gate["envelope"]
        assert env["session_id"] == "real-good"
        assert env["actor_id"] == "arif"
        assert env["session_token"] == "sct-real"
        assert env["source"] == "arifOS_kernel"
        assert env["authority"] == "OBSERVE_ONLY"
        assert env["actor_verified"] is True
        # Spoofed identity MUST NOT appear.
        assert "spoofed-sovereign" not in str(env)
        assert "sct-fake" not in str(env)
        assert "i_promise_im_the_kernel" not in str(env)

    def test_valid_session_emits_sanitized_envelope(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # End-to-end happy path: validated session produces a kernel envelope
        # suitable for organ forward. The server.py proxy attaches it as
        # _envelope in forward_args — verify the forward shape that the
        # proxy would receive.
        monkeypatch.setenv("ARIFOS_REMOTE_PROXY_AUTH", "true")
        with patch(
            "arifosmcp.runtime.session_auth.validate_session",
            return_value={
                "valid": True,
                "reason": "L11 AUTH: session valid",
                "actor_id": "arif",
                "session_id": "sess-xyz",
                "session_token": "sct-xyz",
                "authority": "OBSERVE_ONLY",
                "actor_verified": True,
                "session": {"session_id": "sess-xyz", "actor_id": "arif"},
            },
        ):
            gate = require_remote_proxy_session(
                tool_name="wealth_compute_irr",
                organ="WEALTH",
                arguments={
                    "cash_flows": [-100, 110],
                    "session_id": "sess-xyz",
                    "actor_id": "arif",
                },
            )
        assert gate["ok"] is True
        # Mimic server.py: attach envelope as _envelope.
        forward = dict(gate["forward_args"])
        forward["_envelope"] = gate["envelope"]
        # Business args intact.
        assert forward["cash_flows"] == [-100, 110]
        # Caller-supplied session_id/actor_id NOT in forward.
        assert "session_id" not in forward
        assert "actor_id" not in forward
        # Kernel envelope present.
        assert forward["_envelope"]["session_id"] == "sess-xyz"
        assert forward["_envelope"]["actor_id"] == "arif"
        assert forward["_envelope"]["authority"] == "OBSERVE_ONLY"
        assert forward["_envelope"]["path"] == "B"

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

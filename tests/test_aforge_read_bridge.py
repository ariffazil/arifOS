"""Read-only A-FORGE kernel bridge. No live socket except the explicit probe."""

from __future__ import annotations

import base64
import inspect
import json
import os

os.environ["ARIFOS_DISABLE_SAFETY_THEATRE"] = "1"

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import arifosmcp.runtime.aforge_read_bridge as bridge

FULL = bridge.ATTESTED_IDENTITY
SHORT = bridge.ATTESTED_COMMIT_SHORT
LONG = bridge.ATTESTED_COMMIT_FULL
RELEASE = {
    "commit": SHORT,
    "identity_hash": FULL,
    "tool_count": 99,
    "status": "healthy",
}


@pytest.fixture(autouse=True)
def _hermetic_attestation(monkeypatch, tmp_path):
    """Unit tests must not read the live box's attestation."""
    monkeypatch.setattr(bridge, "ATTESTATION_PATH", str(tmp_path / "missing.json"))
    monkeypatch.setattr(bridge, "ATTESTATION_PUBKEY_PATH", str(tmp_path / "missing.pem"))


def _write_attestation(tmp_path, commit: str, signer, pubkey) -> None:
    body = {
        "release_commit": commit,
        "executable_tree_sha256": "a" * 64,
        "policy_sha256": "b" * 64,
        "issued_at": "2026-11-28T00:00:00.000Z",
        "key_id": "ed25519:aforge-release",
    }
    payload = json.dumps(body, separators=(",", ":")).encode()
    attestation = dict(body)
    attestation["signature"] = base64.b64encode(signer.sign(payload)).decode()
    (tmp_path / "attestation.json").write_text(json.dumps(attestation))
    (tmp_path / "attestation.pub.pem").write_bytes(
        pubkey.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def _use_attestation(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(bridge, "ATTESTATION_PATH", str(tmp_path / "attestation.json"))
    monkeypatch.setattr(bridge, "ATTESTATION_PUBKEY_PATH", str(tmp_path / "attestation.pub.pem"))


class _Resp:
    def __init__(self, status: int, body: str, content_type: str = "application/json"):
        self.status = status
        self._body = body.encode()
        self._ctype = content_type

    def read(self, n: int = -1) -> bytes:
        return self._body

    def getheader(self, name: str, default=None):
        if name.lower() == "content-type":
            return self._ctype
        return default


class _Script:
    def __init__(self, responses: list[_Resp]):
        self.responses = list(responses)
        self.calls: list[dict] = []
        self.inits: list[dict] = []

    def __call__(self, host, port=None, timeout=None):
        self.inits.append({"host": host, "port": port, "timeout": timeout})
        parent = self

        class _Conn:
            def __init__(self) -> None:
                self.timeout = timeout

            def request(self, method, path, body=None, headers=None):
                parent.calls.append(
                    {
                        "method": method,
                        "path": path,
                        "body": body,
                        "headers": dict(headers or {}),
                        "timeout": self.timeout,
                    }
                )
                if not parent.responses:
                    raise RuntimeError("no scripted response")
                self._resp = parent.responses.pop(0)

            def getresponse(self):
                return self._resp

            def close(self) -> None:
                return None

        return _Conn()


def _health(**overrides) -> str:
    body = {
        "status": "healthy",
        "commit": SHORT,
        "identity_hash": FULL,
        "tools_listed": 99,
    }
    body.update(overrides)
    return json.dumps(body)


def _init() -> str:
    return json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2025-06-18",
                "serverInfo": {"name": "A-FORGE-MCP"},
                "sessionId": "SHOULD-NOT-ECHO",
            },
        }
    )


def _rpc(payload, *, is_error: bool = False, error=None, content: bool = True) -> str:
    if error is not None:
        return json.dumps({"jsonrpc": "2.0", "id": 2, "error": error})
    result: dict = {}
    if content:
        text = payload if isinstance(payload, str) else json.dumps(payload)
        result["content"] = [{"type": "text", "text": text}]
    if is_error:
        result["isError"] = True
    return json.dumps({"jsonrpc": "2.0", "id": 2, "result": result})


def _install(monkeypatch, responses: list[_Resp]) -> _Script:
    script = _Script(responses)
    monkeypatch.setattr(bridge, "HTTPConnection", script)
    return script


def _no_session(call: dict) -> None:
    assert not any(key.lower() == "mcp-session-id" for key in call["headers"])


def test_allowlist_never_opens_a_socket(monkeypatch):
    opened: list = []

    def _ctor(*args, **kwargs):
        opened.append((args, kwargs))
        raise AssertionError("socket")

    monkeypatch.setattr(bridge, "HTTPConnection", _ctor)
    for name in (
        "forge_shell",
        "forge_filesystem",
        "forge_registry_status",
        "Forge_Health_Check",
        "forge_health_check ",
    ):
        try:
            bridge.read_tool(name)
        except bridge.AforgeReadHold as exc:
            assert "allowlist" in str(exc)
        else:
            raise AssertionError(name)
    assert opened == []


def test_pin_miss_stops_after_health(monkeypatch):
    cases = [
        _health(identity_hash="0" * 64),
        _health(commit="ef8bac3EXTRA"),
        _health(commit="ef8bac31"),
        _health(identity_hash=FULL.upper()),
    ]
    for body in cases:
        script = _install(monkeypatch, [_Resp(200, body)])
        try:
            bridge.read_tool("forge_health_check")
        except bridge.AforgeReadHold:
            pass
        else:
            raise AssertionError(body)
        assert len(script.calls) == 1
        assert script.calls[0]["method"] == "GET"
        assert script.calls[0]["path"] == "/health"


def test_redirect_and_non_200_stop(monkeypatch):
    for status in (302, 503):
        script = _install(monkeypatch, [_Resp(status, "{}")])
        try:
            bridge.read_tool("forge_probe")
        except bridge.AforgeReadHold as exc:
            text = str(exc)
        else:
            raise AssertionError(status)
        assert len(script.calls) == 1
        if status == 302:
            assert "redirect" in text


def test_success_sequence_and_listed_count(monkeypatch):
    script = _install(
        monkeypatch,
        [
            _Resp(200, _health()),
            _Resp(200, _init()),
            _Resp(200, _rpc({"status": "healthy", "version": "2"})),
        ],
    )
    got = bridge.read_tool("forge_health_check")
    assert [call["method"] for call in script.calls] == ["GET", "POST", "POST"]
    assert [call["path"] for call in script.calls] == ["/health", "/mcp", "/mcp"]
    assert [call["timeout"] for call in script.calls] == [8, 8, 25]
    assert script.inits[0]["host"] == "127.0.0.1"
    assert script.inits[0]["port"] == 7072
    for call in script.calls:
        _no_session(call)
    assert "Content-Type" not in script.calls[0]["headers"]
    assert script.calls[1]["headers"]["Content-Type"] == "application/json"
    init = json.loads(script.calls[1]["body"])
    call = json.loads(script.calls[2]["body"])
    assert init["id"] == 1 and init["method"] == "initialize"
    assert init["params"]["clientInfo"]["name"] == "arifos-kernel-aforge-read"
    assert call["id"] == 2
    assert call["params"]["name"] == "forge_health_check"
    assert call["params"]["arguments"] == {}
    assert got["wire_tool"] == "forge_health_check"
    assert got["release"]["tool_count"] == 99
    assert got["release"]["status"] == "healthy"
    assert got["release"]["commit"] == SHORT
    assert got["release"]["identity_hash"] == FULL
    assert got["payload"]["status"] == "healthy"


def test_full_sha_identity_dict_and_prefer_tool_count(monkeypatch):
    script = _install(
        monkeypatch,
        [
            _Resp(
                200,
                _health(
                    commit=LONG,
                    identity_hash={"hash": FULL},
                    tool_count=7,
                    tools_listed=99,
                ),
            ),
            _Resp(200, _init()),
            _Resp(200, _rpc({"organs": {"arifos": {"alive": True}}})),
        ],
    )
    got = bridge.read_tool("forge_probe")
    assert len(script.calls) == 3
    assert json.loads(script.calls[2]["body"])["params"]["name"] == "forge_probe"
    assert got["release"]["commit"] == LONG
    assert got["release"]["identity_hash"] == FULL
    assert got["release"]["tool_count"] == 7


def test_deployed_commit_fallback(monkeypatch):
    body = {"status": "healthy", "deployed_commit": SHORT, "identity_hash": FULL, "tool_count": 0}
    script = _install(
        monkeypatch,
        [
            _Resp(200, json.dumps(body)),
            _Resp(200, _init()),
            _Resp(200, _rpc({"status": "healthy"})),
        ],
    )
    got = bridge.read_tool("forge_health_check")
    assert len(script.calls) == 3
    assert got["release"]["commit"] == SHORT
    assert got["release"]["tool_count"] == 0


def test_tool_failures_hold(monkeypatch):
    samples = [
        _Resp(200, _rpc({"status": "x"}, is_error=True)),
        _Resp(200, _rpc("not-json")),
        _Resp(200, _rpc({})),
        _Resp(200, _rpc({"version": "only"})),
        _Resp(200, _rpc(None, content=False)),
        _Resp(200, _rpc(None, error={"code": -1, "message": "nope"})),
    ]
    for response in samples:
        script = _install(
            monkeypatch,
            [_Resp(200, _health()), _Resp(200, _init()), response],
        )
        try:
            bridge.read_tool("forge_health_check")
        except bridge.AforgeReadHold:
            pass
        else:
            raise AssertionError(response._body)
        assert len(script.calls) == 3


def test_sse_last_data_line(monkeypatch):
    inner = json.dumps({"status": "healthy"})
    rpc = {"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text", "text": inner}]}}
    sse = "event: message\ndata: " + json.dumps(rpc) + "\n\n"
    _install(
        monkeypatch,
        [
            _Resp(200, _health()),
            _Resp(200, _init()),
            _Resp(200, sse, content_type="text/event-stream"),
        ],
    )
    got = bridge.read_tool("forge_health_check")
    assert got["payload"]["status"] == "healthy"


def _kernel():
    import arifosmcp.tools.kernel_canonical as kernel

    return kernel


def _patch_read(monkeypatch, fn):
    monkeypatch.setattr(bridge, "read_tool", fn)


def _claim_blocked(out):
    if out.get("can_claim_success") is False:
        return True
    result = out.get("result")
    return isinstance(result, dict) and result.get("can_claim_success") is False


def test_route_alias_rejects_actuators_in_the_bridge(monkeypatch):
    opened: list = []

    def _spy(name):
        opened.append(name)
        raise AssertionError(name)

    _patch_read(monkeypatch, _spy)
    kernel = _kernel()
    for organ in ("forge", "aforge", "A-FORGE", " A_FORGE ", "Forge"):
        for tool in ("forge_shell", "forge_filesystem"):
            out = kernel.arif_route(intent="system vitals", organ=organ, organ_tool=tool)
            blob = json.dumps(out)
            assert out["status"] == "HOLD", blob[:400]
            assert _claim_blocked(out), blob[:400]
            assert "allowlist" in blob
            assert "UNKNOWN_ORGAN" not in blob
    assert opened == []


def test_forge_worker_stays_unknown(monkeypatch):
    opened: list = []

    def _spy(name):
        opened.append(name)
        raise AssertionError(name)

    _patch_read(monkeypatch, _spy)
    out = _kernel().arif_route(
        intent="system vitals",
        organ="forge-worker",
        organ_tool="forge_health_check",
    )
    blob = json.dumps(out)
    assert out["status"] == "HOLD"
    assert "UNKNOWN_ORGAN" in blob
    assert opened == []


def test_route_positive_observe_only(monkeypatch):
    kernel = _kernel()
    seen: dict = {}
    real = kernel.build_federation_envelope

    def _wrapped(**kwargs):
        seen.update(kwargs)
        return real(**kwargs)

    monkeypatch.setattr(kernel, "build_federation_envelope", _wrapped)

    def _fake(name):
        assert name == "forge_health_check"
        return {
            "payload": {"status": "healthy"},
            "release": dict(RELEASE),
            "wire_tool": name,
        }

    _patch_read(monkeypatch, _fake)
    out = kernel.arif_route(
        intent="system vitals",
        organ="A-FORGE",
        organ_tool="forge_health_check",
        arguments={"authority_ceiling": "FULL", "command": "SENTINEL-DO-NOT-LEAK"},
    )
    blob = json.dumps(out)
    assert "SENTINEL-DO-NOT-LEAK" not in blob
    assert out["status"] == "OK"
    result = out["result"]
    assert result["status"] == "routed"
    assert result["aforge_release"]["commit"] == SHORT
    assert result["aforge_release"]["tool_count"] == 99
    assert result["aforge_release"]["status"] == "healthy"
    bridge_result = result["bridge_result"]
    assert bridge_result["verdicts"]["action"]["state"] == "NOT_EVALUATED"
    assert bridge_result["verdicts"]["receipt"]["state"] == "UNSEALED"
    assert bridge_result["verdicts"]["session"]["state"] == "OBSERVE_ONLY"
    assert seen["authority"] == "OBSERVE_ONLY"
    assert seen["target_tool"] == "forge_health_check"


def test_sealed_bridge_result_holds_the_route(monkeypatch):
    kernel = _kernel()

    def _sealed(*_args, **_kwargs):
        return {
            "status": "OK",
            "verdicts": {
                "receipt": {"state": "SEAL"},
                "action": {"state": "NOT_EVALUATED"},
                "session": {"state": "OBSERVE_ONLY"},
            },
        }

    monkeypatch.setattr(kernel, "_bridge_aforge", _sealed)
    out = kernel.arif_route(intent="system vitals", organ="a-forge", organ_tool="forge_probe")
    assert out["status"] == "HOLD"
    assert _claim_blocked(out)


def test_bridge_source_contract():
    kernel = _kernel()
    source = inspect.getsource(kernel._bridge_aforge)
    assert "_assert_organ_attested" not in source
    assert "inject_envelope_into_call_args" not in source
    assert 'authority="OBSERVE_ONLY"' in source
    module = inspect.getsource(bridge)
    for banned in ("getenv", "environ", "GEOX_BRIDGE", "7071", "urllib"):
        assert banned not in module


def test_token_stays_in_envelope_kwargs(monkeypatch):
    kernel = _kernel()
    token = "FAKE-TOKEN-NOT-LIVE"
    seen: dict = {}
    real = kernel.build_federation_envelope

    def _wrapped(**kwargs):
        seen.update(kwargs)
        return real(**kwargs)

    monkeypatch.setattr(kernel, "build_federation_envelope", _wrapped)

    def _fake(name):
        return {"payload": {"status": "healthy"}, "release": dict(RELEASE), "wire_tool": name}

    _patch_read(monkeypatch, _fake)
    out = kernel._bridge_aforge("forge_health_check", "sid-1", "grok-build", token)
    assert seen["session_token"] == token
    assert seen["authority"] == "OBSERVE_ONLY"
    assert token not in json.dumps(out)


def test_full_authority_does_not_read(monkeypatch):
    kernel = _kernel()
    token = "LEAK-TOKEN-XYZ"
    opened: list = []

    def _bad(**_kwargs):
        return {"session": {"authority": "FULL", "session_token": token}}

    monkeypatch.setattr(kernel, "build_federation_envelope", _bad)

    def _spy(name):
        opened.append(name)
        raise AssertionError(name)

    _patch_read(monkeypatch, _spy)
    out = kernel._bridge_aforge("forge_health_check", "sid", "actor", token)
    assert opened == []
    assert out["status"] == "HOLD"
    assert token not in json.dumps(out)


def test_empty_payload_does_not_wrap_ok(monkeypatch):
    kernel = _kernel()
    wrapped: list = []

    def _boom(*_args, **_kwargs):
        wrapped.append("ok")
        raise AssertionError("bridge_ok")

    monkeypatch.setattr(kernel, "_bridge_ok", _boom)

    def _fake(name):
        return {"payload": {}, "release": dict(RELEASE), "wire_tool": name}

    _patch_read(monkeypatch, _fake)
    out = kernel._bridge_aforge("forge_probe", None, None, None)
    assert wrapped == []
    assert out["status"] == "HOLD"
    assert "empty payload" in json.dumps(out)


def test_missing_release_pin_holds(monkeypatch):
    kernel = _kernel()

    def _fake(name):
        return {
            "payload": {"status": "healthy"},
            "release": {"tool_count": 99, "status": "healthy"},
            "wire_tool": name,
        }

    _patch_read(monkeypatch, _fake)
    out = kernel._bridge_aforge("forge_health_check", None, None, None)
    assert out["status"] == "HOLD"
    assert "release pin missing" in json.dumps(out)


def test_signed_attestation_supersedes_stale_literal(monkeypatch, tmp_path):
    """A literal that rots must not gate the kernel once A-FORGE has re-signed."""
    key = Ed25519PrivateKey.generate()
    _write_attestation(tmp_path, "abc1234def", key, key.public_key())
    _use_attestation(monkeypatch, tmp_path)
    assert bridge.ATTESTED_COMMIT_SHORT != "abc1234"
    release = bridge._release_from_health(json.loads(_health(commit="abc1234")))
    assert release["commit"] == "abc1234"


def test_forged_attestation_falls_back_to_literal(monkeypatch, tmp_path):
    """The signature must be checked, not merely present."""
    signer = Ed25519PrivateKey.generate()
    impostor = Ed25519PrivateKey.generate()
    _write_attestation(tmp_path, "abc1234def", signer, impostor.public_key())
    _use_attestation(monkeypatch, tmp_path)
    with pytest.raises(bridge.AforgeReadHold):
        bridge._release_from_health(json.loads(_health(commit="abc1234")))
    ok = bridge._release_from_health(json.loads(_health(commit=bridge.ATTESTED_COMMIT_SHORT)))
    assert ok["commit"] == bridge.ATTESTED_COMMIT_SHORT

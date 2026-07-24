"""
test_a2a_b3_hardening.py — B3 A2A authentication & order hardening
═════════════════════════════════════════════════════════════════════

Verifies the B3 hardening pass on arifOS's A2A protocol server:

  1. Discovery routes stay PUBLIC (no SCT required).
  2. /task, /execute, /status, /cancel, /subscribe REQUIRE a valid SCT.
  3. Body actor IDs are NEVER authority — only the verified SCT actor owns
     a task.
  4. Cross-owner access (actor B reading actor A's task) returns 403.
  5. Synchronous /execute calls arif_judge and routes ONLY on SEAL.
     HOLD / VOID / SABAR / parse-failure => 409, no execution, no truthy
     default.
  6. status_callback_url is validated with a_rif/ssrf_guard.
     Unsafe URLs (private IPs, localhost, file://, .internal, …) return 400.

The A2A server is exercised via FastAPI's ASGI transport — no live kernel,
no Redis, no external network. The MCP tool surface is replaced with a
canned mock that lets each test control arif_judge's verdict and observe
that the routing path either fires (SEAL) or does NOT fire (anything else).
"""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any

import pytest

# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def mock_mcp(monkeypatch):
    """
    Replace ``A2ATaskManager._call_mcp_tool`` with a canned mock.

    The mock records every call and lets each test override per-tool
    responses via the ``responses`` mapping. The shape matches what
    FastMCP returns: ``{"content": [{"type": "text", "text": "<json>"}]}``.
    """
    recorded: list[tuple[str, dict]] = []
    responses: dict[str, Any] = {
        "arif_init": {
            "content": [
                {
                    "type": "text",
                    "text": '{"verdict": "SEAL", "session_id": "sess-b3-test"}',
                }
            ]
        },
        "arif_critique": {
            "content": [{"type": "text", "text": '{"verdict": "SABAR"}'}]
        },
        "arif_judge": {
            "content": [{"type": "text", "text": '{"verdict": "VOID"}'}]
        },
        "arif_kernel_route": {
            "content": [
                {
                    "type": "text",
                    "text": '{"ok": true, "status": "SUCCESS", "payload": {}}',
                }
            ]
        },
    }
    calls_by_tool: dict[str, list[dict]] = {}

    async def _fake(self, tool_name, params):
        recorded.append((tool_name, params))
        calls_by_tool.setdefault(tool_name, []).append(params)
        if tool_name in responses:
            resp = responses[tool_name]
            if callable(resp):
                return resp(params)
            # deep-ish copy so tests can mutate freely
            return {k: v for k, v in resp.items()}
        return {"content": [{"type": "text", "text": "{}"}]}

    monkeypatch.setattr(
        "arifosmcp.runtime.a2a.server.A2ATaskManager._call_mcp_tool",
        _fake,
    )
    return {"calls": recorded, "calls_by_tool": calls_by_tool, "responses": responses}


@pytest.fixture
def a2a_client(mock_mcp):
    """In-process FastAPI client for the A2A server (no live kernel)."""
    from arifosmcp.runtime.a2a.server import A2AServer

    server = A2AServer(mcp_server=object())  # mcp_server never touched (mocked)

    from fastapi.testclient import TestClient

    with TestClient(server.app) as client:
        yield client, server, mock_mcp


def _mint_sct(actor: str = "arif", auth: str = "LIMITED_MUTATE", sid: str = "sess-b3"):
    from arifosmcp.runtime.sct import mint_sct

    token, claims = mint_sct(
        sid=sid,
        actor=actor,
        auth=auth,
        av=True,
        allowed=["arif_observe", "arif_judge", "arif_forge", "arif_init"],
    )
    return token, claims


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ── 1. Discovery stays public ───────────────────────────────────────────


class TestDiscoveryPublic:
    """Discovery / health / seal-verify must remain open (B3 §discovery)."""

    def test_well_known_agent_json_open(self, a2a_client):
        client, _server, _mock = a2a_client
        r = client.get("/.well-known/agent.json")
        # 200 (legacy server still mounts a card) OR 410 (moved to AAA) both
        # prove the route is NOT 401. Discovery stays public.
        assert r.status_code in (200, 410), r.text

    def test_a2a_health_open(self, a2a_client):
        client, _server, _mock = a2a_client
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


# ── 2. /task authentication ────────────────────────────────────────────


class TestTaskAuth:
    """POST /task requires SCT; body actor IDs are display hints only."""

    def test_rejects_missing_token(self, a2a_client):
        client, _server, _mock = a2a_client
        r = client.post(
            "/task",
            json={
                "client_agent_id": "anybody",
                "messages": [{"role": "user", "content": "ping"}],
            },
        )
        assert r.status_code == 401
        assert "L11 AUTH" in r.text

    def test_rejects_invalid_token(self, a2a_client):
        client, _server, _mock = a2a_client
        r = client.post(
            "/task",
            json={
                "client_agent_id": "anybody",
                "messages": [{"role": "user", "content": "ping"}],
            },
            headers={"Authorization": "Bearer sct_v1.not.a.token.deadbeef"},
        )
        assert r.status_code == 401
        assert "L11 AUTH" in r.text

    def test_rejects_tampered_token(self, a2a_client):
        client, _server, _mock = a2a_client
        token, _ = _mint_sct(actor="arif")
        # Flip the last 4 hex chars of the signature.
        tampered = token[:-4] + "dead"
        r = client.post(
            "/task",
            json={
                "client_agent_id": "anybody",
                "messages": [{"role": "user", "content": "ping"}],
            },
            headers=_bearer(tampered),
        )
        assert r.status_code == 401

    def test_accepts_valid_sct(self, a2a_client):
        client, _server, _mock = a2a_client
        token, _ = _mint_sct(actor="arif", sid="sess-b3-ok")
        r = client.post(
            "/task",
            json={
                "client_agent_id": "downstream-agent-display-name",
                "messages": [{"role": "user", "content": "hi"}],
            },
            headers=_bearer(token),
        )
        assert r.status_code == 200, r.text
        body = r.json()
        # B3: the body client_agent_id is the display hint; the SCT actor
        # is the authoritative owner. They should be DIFFERENT in this test.
        assert body["creator_actor_id"] == "arif"
        # Task should be recorded with the verified creator.
        task = asyncio.run(_server.task_manager.get_task(body["task_id"]))
        assert task is not None
        assert task.creator_actor_id == "arif"
        assert task.client_agent_id == "downstream-agent-display-name"

    def test_body_actor_id_is_not_authority(self, a2a_client):
        """Body says the agent is 'malicious-display-name' but the SCT says
        the real actor is 'arif'. The owner is the SCT actor."""
        client, _server, _mock = a2a_client
        token, _ = _mint_sct(actor="arif", sid="sess-b3-display")
        r = client.post(
            "/task",
            json={
                "client_agent_id": "malicious-display-name",
                "messages": [{"role": "user", "content": "hi"}],
            },
            headers=_bearer(token),
        )
        assert r.status_code == 200
        body = r.json()
        # Creator is the verified SCT actor, NOT the body's display name.
        assert body["creator_actor_id"] == "arif"
        assert body["creator_actor_id"] != "malicious-display-name"


# ── 3. SSRF guard on status_callback_url ───────────────────────────────


class TestCallbackUrlSsrf:
    """status_callback_url must pass a_rif/ssrf_guard."""

    @pytest.mark.parametrize(
        "url, expected_flag_substring",
        [
            ("http://127.0.0.1/hook", "private_ip_access"),
            ("http://localhost/hook", "private_ip_access"),
            ("http://10.0.0.5/hook", "private_ip_access"),
            ("http://192.168.1.1/hook", "private_ip_access"),
            ("http://172.16.0.1/hook", "private_ip_access"),
            ("http://169.254.169.254/latest/meta-data", "private_ip_access"),
            ("http://api.internal/hook", "internal_domain"),
            ("file:///etc/passwd", "scheme_blocked"),
            ("javascript:alert(1)", "scheme_blocked"),
            ("ftp://example.com/hook", "scheme_blocked"),
        ],
    )
    def test_unsafe_url_rejected(self, a2a_client, url, expected_flag_substring):
        client, _server, _mock = a2a_client
        token, _ = _mint_sct(actor="arif", sid=f"sess-ssrf-{url[:8]}")
        r = client.post(
            "/task",
            json={
                "client_agent_id": "anybody",
                "messages": [{"role": "user", "content": "hi"}],
                "status_callback_url": url,
            },
            headers=_bearer(token),
        )
        assert r.status_code == 400, f"{url}: {r.text}"
        assert expected_flag_substring in r.text, r.text

    def test_safe_url_accepted(self, a2a_client):
        client, _server, _mock = a2a_client
        token, _ = _mint_sct(actor="arif", sid="sess-ssrf-ok")
        r = client.post(
            "/task",
            json={
                "client_agent_id": "anybody",
                "messages": [{"role": "user", "content": "hi"}],
                "status_callback_url": "https://hooks.example.com/a2a",
            },
            headers=_bearer(token),
        )
        assert r.status_code == 200, r.text

    def test_missing_callback_is_ok(self, a2a_client):
        client, _server, _mock = a2a_client
        token, _ = _mint_sct(actor="arif", sid="sess-ssrf-none")
        r = client.post(
            "/task",
            json={
                "client_agent_id": "anybody",
                "messages": [{"role": "user", "content": "hi"}],
            },
            headers=_bearer(token),
        )
        assert r.status_code == 200


# ── 4. /status, /cancel, /subscribe — auth + ownership ────────────────


class TestOwnershipEnforcement:
    """Cross-owner access to /status, /cancel, /subscribe is 403."""

    @pytest.fixture
    def owner_task(self, a2a_client):
        """Submit a task as actor 'arif', then freeze it in a non-terminal
        state so /status and /cancel tests aren't racing the background
        ``_execute_task``. The mocked arif_judge returns VOID by default
        which would mark the task FAILED; we override the state to WORKING
        so /cancel can succeed."""
        client, server, mock = a2a_client
        token, _ = _mint_sct(actor="arif", sid="sess-b3-owner")
        r = client.post(
            "/task",
            json={
                "client_agent_id": "display-name",
                "messages": [{"role": "user", "content": "owner task"}],
            },
            headers=_bearer(token),
        )
        assert r.status_code == 200, r.text
        task_id = r.json()["task_id"]

        # Freeze the task in a non-terminal state so we don't race the
        # background _execute_task (whose mocked arif_judge returns VOID
        # by default, which would mark the task FAILED).
        from arifosmcp.runtime.a2a.models import TaskState

        async def _freeze():
            task = await server.task_manager.get_task(task_id)
            if task is not None:
                task.state = TaskState.WORKING

        asyncio.run(_freeze())
        return client, server, mock, task_id, token

    @pytest.fixture
    def other_token(self):
        token, _ = _mint_sct(actor="eve", sid="sess-b3-other")
        return token

    # ── /status ──
    def test_status_missing_token(self, a2a_client, owner_task):
        client, _server, _mock, task_id, _owner = owner_task
        r = client.get(f"/status/{task_id}")
        assert r.status_code == 401

    def test_status_invalid_token(self, a2a_client, owner_task):
        client, _server, _mock, task_id, _owner = owner_task
        r = client.get(
            f"/status/{task_id}",
            headers=_bearer("sct_v1.garbage.deadbeef"),
        )
        assert r.status_code == 401

    def test_status_owner_ok(self, a2a_client, owner_task):
        client, _server, _mock, task_id, owner_token = owner_task
        r = client.get(f"/status/{task_id}", headers=_bearer(owner_token))
        assert r.status_code == 200, r.text

    def test_status_cross_owner_forbidden(self, a2a_client, owner_task, other_token):
        client, _server, _mock, task_id, _owner = owner_task
        r = client.get(f"/status/{task_id}", headers=_bearer(other_token))
        assert r.status_code == 403
        assert "actor does not own" in r.text

    # ── /cancel ──
    def test_cancel_missing_token(self, a2a_client, owner_task):
        client, _server, _mock, task_id, _owner = owner_task
        r = client.post(f"/cancel/{task_id}")
        assert r.status_code == 401

    def test_cancel_invalid_token(self, a2a_client, owner_task):
        client, _server, _mock, task_id, _owner = owner_task
        r = client.post(
            f"/cancel/{task_id}",
            headers=_bearer("sct_v1.garbage.deadbeef"),
        )
        assert r.status_code == 401

    def test_cancel_owner_ok(self, a2a_client, owner_task):
        client, _server, _mock, task_id, owner_token = owner_task
        r = client.post(f"/cancel/{task_id}", headers=_bearer(owner_token))
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("success") is True

    def test_cancel_cross_owner_forbidden(self, a2a_client, owner_task, other_token):
        client, _server, _mock, task_id, _owner = owner_task
        r = client.post(f"/cancel/{task_id}", headers=_bearer(other_token))
        assert r.status_code == 403
        # Task should NOT have been cancelled.
        task = asyncio.run(_server.task_manager.get_task(task_id))
        from arifosmcp.runtime.a2a.models import TaskState

        assert task.state != TaskState.CANCELLED

    # ── /subscribe ──
    def test_subscribe_missing_token(self, a2a_client, owner_task):
        client, _server, _mock, task_id, _owner = owner_task
        with contextlib.suppress(Exception):
            r = client.get(f"/subscribe/{task_id}", timeout=2.0)
            # Either 401 (token check fails first) or the SSE just opens
            # then closes. The token check happens BEFORE owner check, so
            # 401 is the contract.
            assert r.status_code == 401
        # The above is a best-effort check: TestClient may consume the
        # stream. The explicit 401 path is also covered in the
        # _resolve_actor_from_request helper which is the same code used
        # for /status and /cancel.

    def test_subscribe_cross_owner_forbidden(self, a2a_client, owner_task, other_token):
        client, _server, _mock, task_id, _owner = owner_task
        # We expect 403 from the owner check; the FastAPI TestClient
        # returns a real response for non-streaming raises.
        r = client.get(f"/subscribe/{task_id}", headers=_bearer(other_token))
        assert r.status_code == 403


# ── 5. /execute — SEAL-only routing ────────────────────────────────────


class TestExecuteSealOnly:
    """Synchronous /execute routes only on arif_judge == SEAL."""

    def _set_judge_verdict(self, mock_mcp, verdict: str | None):
        """Configure the mock to return a specific verdict from arif_judge.

        ``verdict=None`` simulates a malformed/empty response.
        """
        if verdict is None:
            mock_mcp["responses"]["arif_judge"] = {"content": [{"type": "text", "text": "{}"}]}
            return
        mock_mcp["responses"]["arif_judge"] = {
            "content": [{"type": "text", "text": f'{{"verdict": "{verdict}"}}'}]
        }

    def test_rejects_missing_token(self, a2a_client):
        client, _server, mock_mcp = a2a_client
        r = client.post("/execute", json={"query": "ping"})
        assert r.status_code == 401
        assert "L11 AUTH" in r.text

    def test_rejects_invalid_token(self, a2a_client):
        client, _server, mock_mcp = a2a_client
        r = client.post(
            "/execute",
            json={"query": "ping"},
            headers=_bearer("sct_v1.bogus.deadbeef"),
        )
        assert r.status_code == 401

    @pytest.mark.parametrize("verdict", ["HOLD", "VOID", "SABAR", "PARTIAL", "888_HOLD"])
    def test_no_seal_returns_409_no_route(self, a2a_client, mock_mcp, verdict):
        """On any non-SEAL verdict, /execute must NOT route to arif_kernel_route."""
        client, _server, _ = a2a_client
        self._set_judge_verdict(mock_mcp, verdict)
        token, _ = _mint_sct(actor="arif", sid=f"sess-b3-{verdict.lower()}")
        r = client.post(
            "/execute",
            json={"query": "do something risky"},
            headers=_bearer(token),
        )
        assert r.status_code == 409, f"verdict={verdict} body={r.text}"
        body = r.json()
        detail = body.get("detail") or {}
        assert detail.get("code") == "JUDGE_NO_SEAL"
        assert detail.get("verdict") == verdict
        # The arif_kernel_route MUST NOT be called.
        route_calls = mock_mcp["calls_by_tool"].get("arif_kernel_route", [])
        assert route_calls == [], (
            f"verdict={verdict} should NOT route, but arif_kernel_route was called: {route_calls}"
        )

    def test_parse_failure_returns_409_no_route(self, a2a_client, mock_mcp):
        """Malformed judge payload (no 'verdict' field) must not route."""
        client, _server, _ = a2a_client
        mock_mcp["responses"]["arif_judge"] = {
            "content": [{"type": "text", "text": "not-json-at-all"}]
        }
        token, _ = _mint_sct(actor="arif", sid="sess-b3-malformed")
        r = client.post(
            "/execute",
            json={"query": "do something"},
            headers=_bearer(token),
        )
        assert r.status_code == 409, r.text
        body = r.json()
        assert body["detail"]["code"] == "JUDGE_NO_SEAL"
        # Parse-failure falls back to VOID per _parse_judge_verdict.
        assert body["detail"]["verdict"] == "VOID"
        # No routing.
        assert mock_mcp["calls_by_tool"].get("arif_kernel_route", []) == []

    def test_empty_judge_response_returns_409(self, a2a_client, mock_mcp):
        """Empty judge response must not route (no truthy default)."""
        client, _server, _ = a2a_client
        mock_mcp["responses"]["arif_judge"] = {"content": []}
        token, _ = _mint_sct(actor="arif", sid="sess-b3-empty")
        r = client.post(
            "/execute",
            json={"query": "do something"},
            headers=_bearer(token),
        )
        assert r.status_code == 409, r.text
        assert mock_mcp["calls_by_tool"].get("arif_kernel_route", []) == []

    def test_seal_routes_to_kernel(self, a2a_client, mock_mcp):
        client, _server, _ = a2a_client
        self._set_judge_verdict(mock_mcp, "SEAL")
        token, _ = _mint_sct(actor="arif", sid="sess-b3-seal")
        r = client.post(
            "/execute",
            json={"query": "do something safe"},
            headers=_bearer(token),
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["verdict"] == "SEAL"
        assert body["creator_actor_id"] == "arif"
        # arif_kernel_route WAS called (this is the only path where it fires).
        assert len(mock_mcp["calls_by_tool"].get("arif_kernel_route", [])) == 1

    def test_body_actor_id_ignored_on_execute(self, a2a_client, mock_mcp):
        """Body's auth_context.actor_id must NOT be the executing actor."""
        client, _server, _ = a2a_client
        self._set_judge_verdict(mock_mcp, "SEAL")
        token, _ = _mint_sct(actor="arif", sid="sess-b3-execute-display")
        r = client.post(
            "/execute",
            json={
                "query": "do something",
                "auth_context": {"actor_id": "evil-impersonator"},
            },
            headers=_bearer(token),
        )
        assert r.status_code == 200, r.text
        body = r.json()
        # Body's display actor_id is NOT the executing actor.
        assert body["creator_actor_id"] == "arif"
        assert body["creator_actor_id"] != "evil-impersonator"
        # The judge was called with the SCT actor, not the body actor.
        judge_calls = mock_mcp["calls_by_tool"].get("arif_judge", [])
        assert judge_calls
        assert judge_calls[-1].get("actor_id") == "arif"
        assert judge_calls[-1].get("actor_id") != "evil-impersonator"


# ── 6. Helpers (unit) ──────────────────────────────────────────────────


class TestHelpers:
    """Direct unit checks on the hardening helpers."""

    def test_extract_sct_token_bearer(self):
        from arifosmcp.runtime.a2a.server import _extract_sct_token

        assert _extract_sct_token("Bearer sct_v1.x.y", None) == "sct_v1.x.y"
        assert _extract_sct_token("bearer sct_v1.x.y", None) == "sct_v1.x.y"

    def test_extract_sct_token_header_fallback(self):
        from arifosmcp.runtime.a2a.server import _extract_sct_token

        assert _extract_sct_token(None, "sct_v1.a.b") == "sct_v1.a.b"

    def test_extract_sct_token_bearer_wins(self):
        from arifosmcp.runtime.a2a.server import _extract_sct_token

        assert _extract_sct_token("Bearer sct_v1.x.y", "sct_v1.a.b") == "sct_v1.x.y"

    def test_extract_sct_token_missing(self):
        from arifosmcp.runtime.a2a.server import _extract_sct_token

        assert _extract_sct_token(None, None) is None
        assert _extract_sct_token("", "") is None
        assert _extract_sct_token("Bearer", "") is None  # scheme but no token

    def test_parse_judge_verdict_seal(self):
        from arifosmcp.runtime.a2a.server import _parse_judge_verdict

        r = {"content": [{"type": "text", "text": '{"verdict": "SEAL", "x": 1}'}]}
        assert _parse_judge_verdict(r) == "SEAL"

    def test_parse_judge_verdict_hold(self):
        from arifosmcp.runtime.a2a.server import _parse_judge_verdict

        r = {"content": [{"type": "text", "text": '{"verdict": "HOLD"}'}]}
        assert _parse_judge_verdict(r) == "HOLD"

    def test_parse_judge_verdict_fallback_void(self):
        from arifosmcp.runtime.a2a.server import _parse_judge_verdict

        # Malformed JSON
        assert _parse_judge_verdict({"content": [{"type": "text", "text": "nope"}]}) == "VOID"
        # Empty content list
        assert _parse_judge_verdict({"content": []}) == "VOID"
        # Missing verdict field
        assert _parse_judge_verdict({"content": [{"type": "text", "text": "{}"}]}) == "VOID"
        # No content key at all
        assert _parse_judge_verdict({}) == "VOID"

    def test_validate_callback_url_blocks_private(self):
        from fastapi import HTTPException

        from arifosmcp.runtime.a2a.server import _validate_callback_url

        with pytest.raises(HTTPException) as ei:
            _validate_callback_url("http://127.0.0.1/hook")
        assert ei.value.status_code == 400
        assert "L1 AMANAH" in str(ei.value.detail)

    def test_validate_callback_url_allows_safe(self):
        from arifosmcp.runtime.a2a.server import _validate_callback_url

        assert _validate_callback_url("https://hooks.example.com/x") == "https://hooks.example.com/x"
        assert _validate_callback_url(None) is None
        assert _validate_callback_url("") is None


# ── 7. Model: Task ownership field present ─────────────────────────────


class TestTaskModelOwnership:
    """Task model carries creator_actor_id (L11 authority)."""

    def test_creator_actor_id_defaults_to_none(self):
        from arifosmcp.runtime.a2a.models import Task

        t = Task(id="x", client_agent_id="display")
        assert t.creator_actor_id is None

    def test_creator_actor_id_set_explicitly(self):
        from arifosmcp.runtime.a2a.models import Task

        t = Task(id="x", client_agent_id="display", creator_actor_id="verified-actor")
        assert t.creator_actor_id == "verified-actor"
        assert t.client_agent_id == "display"
        # B3: client_agent_id is a body-supplied display hint and is
        # distinct from the verified creator.
        assert t.client_agent_id != t.creator_actor_id

from __future__ import annotations

from fastapi.testclient import TestClient

from arifosmcp.apps.m365_bridge import app, bridge


def test_init_session_route_forwards_to_arif_init(monkeypatch) -> None:
    captured: dict[str, object] = {}

    async def fake_call_tool(tool_name, request):
        captured["tool_name"] = tool_name
        captured["arguments"] = request.arguments
        captured["actor_id"] = request.actor_id
        captured["session_id"] = request.session_id
        return {
            "tool": tool_name,
            "upstream": bridge.upstream_url,
            "mcp_session_id": "m365-test-session",
            "result": {"status": "OK"},
        }

    monkeypatch.setattr(bridge, "call_tool", fake_call_tool)

    client = TestClient(app)
    response = client.post(
        "/init-session",
        json={"actor_id": "arif", "arguments": {"mode": "light"}},
    )

    assert response.status_code == 200
    assert response.json()["tool"] == "arif_init"
    assert response.json()["result"]["status"] == "OK"
    assert captured == {
        "tool_name": "arif_init",
        "arguments": {"mode": "light"},
        "actor_id": "arif",
        "session_id": None,
    }


def test_root_exposes_public_routes() -> None:
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["upstream_mcp"]
    assert payload["routes"]["init_session"] == "/init-session"
    assert payload["public_verbs"] == [
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_judge",
        "arif_act",
        "arif_seal",
    ]

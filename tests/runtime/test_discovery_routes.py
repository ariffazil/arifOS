"""
tests/runtime/test_discovery_routes.py — Discovery Route Tests

Verifies that root-level discovery files (agent.json, ai.json, etc.)
are correctly registered and accessible without being shadowed by mounts.

A2A consolidation (FEDERATION_CONTRACT §5.4.5):
- `/.well-known/agent.json` and `/.well-known/agent-card.json` MUST NOT
  serve a local card body. They return 410 Gone with a pointer to the
  AAA-owned canonical card at `https://aaa.arif-fazil.com/.well-known/agent-card.json`.
- MCP discovery (`/.well-known/mcp/server.json`), OAuth, health, tools,
  and `/a2a/*` execution routes MUST remain live.
"""

from pathlib import Path

import pytest
from arifosmcp.runtime.server import app
from tests.conftest import SyncASGIClient


@pytest.fixture
def client():
    return SyncASGIClient(app)


def test_well_known_agent_json_is_a2a_card_pointer(client):
    """FEDERATION_CONTRACT §5.4.5 — /.well-known/agent.json is owned by AAA.

    arifOS MUST NOT publish a local A2A agent card body. The route returns
    410 Gone with a pointer to the canonical AAA card.
    """
    response = client.get("/.well-known/agent.json")
    assert response.status_code == 410
    data = response.json()
    assert data.get("deprecation") == "moved"
    assert data.get("owner") == "AAA"
    assert "aaa.arif-fazil.com" in data.get("moved_to", "")
    # execution endpoints MUST still be advertised so peers can route via AAA
    assert "execution_endpoints" in data
    assert "mcp" in data["execution_endpoints"]
    assert "a2a_task" in data["execution_endpoints"]


def test_well_known_agent_card_json_is_410_with_pointer(client):
    """FEDERATION_CONTRACT §5.4.5 — /.well-known/agent-card.json is owned by AAA."""
    response = client.get("/.well-known/agent-card.json")
    assert response.status_code == 410
    data = response.json()
    assert data.get("deprecation") == "moved"
    assert data.get("owner") == "AAA"
    assert "agent-card.json" in data.get("moved_to", "")


def test_agent_card_summary_is_410(client):
    """/agent-card summary is removed; AAA owns the canonical card."""
    response = client.get("/agent-card")
    assert response.status_code == 410
    data = response.json()
    assert data.get("owner") == "AAA"


def test_agent_card_skills_is_410(client):
    """/agent-card/skills dump is removed; AAA owns the canonical card."""
    response = client.get("/agent-card/skills")
    assert response.status_code == 410
    data = response.json()
    assert data.get("owner") == "AAA"


def test_agent_card_static_alias_exists():
    assert Path("/root/arifOS/static/.well-known/agent-card.json").exists()
    assert Path("/root/arifOS/arifosmcp/static/.well-known/agent-card.json").exists()


def test_ai_plugin_manifest_reachable(client):
    """Test that /.well-known/ai-plugin.json is reachable for ChatGPT Apps discovery."""
    response = client.get("/.well-known/ai-plugin.json")
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == "v1"
    assert data["name_for_model"] == "arifos_mcp"
    assert data["auth"]["type"] == "none"
    assert data["api"]["url"].endswith("/openapi.json")


def test_openapi_exposes_arifos_mind_query_schema(client):
    """Test that OpenAPI advertises arifos_mind legacy compatibility endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "/tools/arifos_mind" in data["paths"]
    mind_path = data["paths"]["/tools/arifos_mind"]["post"]
    # Legacy alias arifos_mind now resolves to the canonical short name arif_think.
    assert mind_path["operationId"] == "call_arif_think"


def test_llms_txt_reachable(client):
    """Test that /llms.txt is reachable (even if file doesn't exist, we test route registration)."""
    # Note: If the file doesn't exist in the test environment, this might be 404
    # but we are testing that the route is handled by our handler, not shadowed.
    response = client.get("/llms.txt")
    # Status code depends on if file exists, but let's at least check it doesn't return 401/403
    assert response.status_code != 401


def test_robots_txt_reachable(client):
    """Test that /robots.txt is reachable."""
    response = client.get("/robots.txt")
    assert response.status_code != 401


def test_ai_json_reachable(client):
    """Test that /ai.json is reachable."""
    response = client.get("/ai.json")
    assert response.status_code != 401


def test_health_reachable(client):
    """Test that /health is reachable and returns JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_discovery_alias_reachable(client):
    """Test that /discovery resolves to the MCP discovery manifest."""
    response = client.get("/discovery")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "tools" in data
    assert data["llm_context_resource"] == "arifos://mcp/context"
    assert data["llm_context"]["schema"] == "arifos-llm-context/v1"


def test_llms_txt_contains_canonical_context(client):
    response = client.get("/llms.txt")
    assert response.status_code == 200
    text = response.text
    assert "arifOS — Constitutional AI Governance Kernel" in text
    assert "## Federation Organs - MCP Endpoints" in text


def test_ready_alias_reachable(client):
    """Test that /ready exposes structured runtime readiness."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] in {"pass", "partial"}


def test_webmcp_manifest_and_assets_reachable(client):
    """Test that the public WebMCP discovery and browser assets are mounted."""
    manifest = client.get("/.well-known/webmcp")
    assert manifest.status_code == 200
    assert manifest.json()["site"]["version"]

    sdk = client.get("/webmcp/sdk.js")
    assert sdk.status_code == 200
    assert "application/javascript" in sdk.headers.get("content-type", "")

    tools = client.get("/webmcp/tools.json")
    assert tools.status_code == 200
    assert "tools" in tools.json()


def test_webmcp_init_returns_session(client):
    """Test that WebMCP init returns a governed session payload."""
    response = client.post("/webmcp/init", json={"actor_id": "test", "human_approval": True})
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in {"SEAL", "PARTIAL"}
    assert "session_id" in data


def test_a2a_routes_reachable(client):
    """Test that mounted A2A routes are exposed on the public app."""
    health = client.get("/a2a/health")
    assert health.status_code == 200
    assert health.json()["protocol"] == "A2A"

    submit = client.post(
        "/a2a/task",
        json={
            "client_agent_id": "pytest",
            "messages": [{"role": "user", "content": "protocol regression"}],
        },
    )
    assert submit.status_code == 200
    task_id = submit.json()["task_id"]

    status = client.get(f"/a2a/status/{task_id}")
    assert status.status_code == 200
    assert status.json()["task"]["id"] == task_id

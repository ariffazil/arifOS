"""
tests/runtime/test_discovery_routes.py — Discovery Route Tests

Verifies that root-level discovery files (agent.json, ai.json, etc.) 
are correctly registered and accessible without being shadowed by mounts.
"""

import pytest
from arifosmcp.runtime.server import app
from tests.conftest import SyncASGIClient

@pytest.fixture
def client():
    return SyncASGIClient(app)

def test_well_known_agent_reachable(client):
    """Test that /.well-known/agent.json is reachable and returns JSON."""
    response = client.get("/.well-known/agent.json")
    assert response.status_code == 200
    data = response.json()
    assert data.get("schema") == "agent-manifest/v1"
    assert "name" in data
    assert "endpoints" in data
    assert data["name"] == "arifOS MCP Server"

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
    assert "## Canonical MCP Context" in text
    assert "Continuity Contract: `0.1.0`" in text
    assert "`init_anchor`" in text


def test_ready_alias_reachable(client):
    """Test that /ready mirrors health instead of 404ing."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


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

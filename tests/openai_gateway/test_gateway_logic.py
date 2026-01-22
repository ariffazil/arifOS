import pytest
from fastapi.testclient import TestClient

from arifos.core.integration.composio.client import client
from arifos.core.integration.openai_gateway.app import app
from arifos.core.integration.openai_gateway.tool_registry import registry

client_test = TestClient(app)

def test_health_check():
    response = client_test.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SEAL"
    assert data["service"] == "openai-gateway"

def test_list_tools():
    response = client_test.get("/tools")
    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    assert len(tools) > 0
    # Verify OpenAI format
    assert "type" in tools[0]
    assert tools[0]["type"] == "function"
    assert "function" in tools[0]

def test_call_tool_read_safe():
    """Test calling a safe READ_ONLY tool."""
    # Mock registry and client
    payload = {
        "tool_name": "google_search",
        "arguments": {"query": "arifOS"}
    }
    response = client_test.post("/call", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Expect SEAL verdict for safe tool
    assert data["verdict"] == "SEAL"
    assert "reasons" in data
    assert "ledger_hash" in data

def test_call_tool_write_hold():
    """Test calling a WRITE tool without approval token."""
    payload = {
        "tool_name": "github_create_issue",
        "arguments": {"owner": "test", "repo": "test", "title": "bug"}
    }
    response = client_test.post("/call", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Expect 888_HOLD
    assert data["verdict"] == "888_HOLD"
    assert data["tool_result"] is None
    assert "requires approval" in data["reasons"][0]

def test_call_tool_write_approved():
    """Test calling a WRITE tool WITH correct approval token."""
    payload = {
        "tool_name": "github_create_issue",
        "arguments": {"owner": "test", "repo": "test", "title": "bug"},
        "approval_token": "PERMIT_github_create_issue"
    }
    response = client_test.post("/call", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Expect SEAL (mocked execution)
    assert data["verdict"] == "SEAL"
    assert "Mocked via Gateway" in str(data["tool_result"])

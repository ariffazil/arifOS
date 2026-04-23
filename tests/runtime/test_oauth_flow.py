"""
tests/runtime/test_oauth_flow.py — FastMCP OAuth 2.1 & CIMD Validation

Verifies the discovery endpoints required for high-security remote clients.
1. RFC 8414 (OAuth 2.1 Authorization Server Metadata)
2. JWKS (Cryptographic Key Set)
3. Client ID Metadata (CIMD)
"""

import pytest
from starlette.testclient import TestClient
from arifosmcp.runtime.server import app

@pytest.fixture
def client():
    return TestClient(app)

def test_oauth_authorization_server_metadata(client):
    """Verify RFC 8414 compliance for OAuth discovery."""
    response = client.get("/.well-known/oauth-authorization-server")
    assert response.status_code == 200
    data = response.json()
    
    assert "issuer" in data
    assert "authorization_endpoint" in data
    assert "token_endpoint" in data
    assert "jwks_uri" in data
    assert "S256" in data["code_challenge_methods_supported"]

def test_jwks_discovery(client):
    """Verify JSON Web Key Set is available for signature verification."""
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    data = response.json()
    
    assert "keys" in data
    assert len(data["keys"]) > 0
    assert data["keys"][0]["kid"] == "arifos-genesis-key"

def test_oauth_auth_flow_simulation(client):
    """Verify the authorize and token mock endpoints work for client handshakes."""
    # 1. Authorize (GET)
    auth_res = client.get("/api/auth/authorize?client_id=test-agent")
    assert auth_res.status_code == 200
    assert "arifOS Authorization" in auth_res.text
    
    # 2. Token (POST)
    token_res = client.post("/api/auth/token", data={"code": "mock-code"})
    assert token_res.status_code == 200
    data = token_res.json()
    assert "access_token" in data
    assert data["access_token"].startswith("mcp_")
    assert data["token_type"] == "Bearer"

def test_cimd_placeholder_presence(client):
    """Verify Client ID Metadata Document exists for FastMCP identity."""
    # Note: Currently redirected or merged in the refactor, let's check availability
    response = client.get("/.well-known/server.json") # build_server_json check
    assert response.status_code == 200
    data = response.json()
    assert "authentication" in data
    assert data["authentication"]["type"] == "oauth2"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

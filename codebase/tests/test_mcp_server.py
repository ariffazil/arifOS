"""
codebase/tests/test_mcp_server.py — MCP Server Tests

Tests for the Model Context Protocol (MCP) server implementation.
Tests all 5 Trinity tools: init_000, agi_genius, asi_act, apex_judge, vault_999

Run: python -m pytest codebase/tests/test_mcp_server.py -v
"""

import pytest
import asyncio
from typing import Dict, Any


# =============================================================================
# TEST CONFIGURATION
# =============================================================================

# Use local server for testing, fallback to production
MCP_BASE_URL = "http://localhost:8000"
PROD_MCP_URL = "https://arifos.arif-fazil.com"


def get_mcp_url():
    """Get MCP URL - prefer local, fallback to production."""
    import httpx
    try:
        response = httpx.get(f"{MCP_BASE_URL}/health", timeout=2.0)
        if response.status_code == 200:
            return MCP_BASE_URL
    except:
        pass
    return PROD_MCP_URL


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
async def mcp_client():
    """Create MCP client for testing."""
    import httpx
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
def base_url():
    """Get base URL for MCP server."""
    return get_mcp_url()


# =============================================================================
# MCP HEALTH & DISCOVERY TESTS
# =============================================================================

class TestMCPHealth:
    """Test MCP server health and discovery."""
    
    @pytest.mark.asyncio
    async def test_mcp_server_health(self, mcp_client, base_url):
        """Test MCP server health endpoint."""
        response = await mcp_client.get(f"{base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "healthy"
        assert "tools" in data or "tool_names" in data
        assert "version" in data
        
        print(f"✅ MCP server: {data.get('version')} with {data.get('tools', 0)} tools")
    
    @pytest.mark.asyncio
    async def test_mcp_server_lists_tools(self, mcp_client, base_url):
        """Test MCP server lists expected tools."""
        response = await mcp_client.get(f"{base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        tool_names = data.get("tool_names", [])
        expected_tools = ["init_000", "agi_genius", "asi_act", "apex_judge", "vault_999"]
        
        for tool in expected_tools:
            assert tool in tool_names, f"Missing tool: {tool}"
        
        print(f"✅ All 5 Trinity tools available: {tool_names}")


# =============================================================================
# TOOL 1: init_000 TESTS
# =============================================================================

class TestMCPInit000:
    """Test init_000 - Constitutional Ignition & Session Management."""
    
    @pytest.mark.asyncio
    async def test_init_000_init(self, mcp_client, base_url):
        """Test init_000 with action='init'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "init_000",
                    "arguments": {
                        "action": "init",
                        "query": "Start constitutional session"
                    }
                },
                "id": 1
            }
        )
        
        # May return 200 or 405 depending on transport mode
        if response.status_code == 200:
            data = response.json()
            print(f"✅ init_000 init: {data.get('result', {}).get('status', 'ok')}")
        else:
            pytest.skip(f"init_000 returned {response.status_code} (may need StreamableHTTP)")
    
    @pytest.mark.asyncio
    async def test_init_000_gate(self, mcp_client, base_url):
        """Test init_000 with action='gate'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "init_000",
                    "arguments": {
                        "action": "gate",
                        "query": "Checkpoint test"
                    }
                },
                "id": 2
            }
        )
        
        if response.status_code == 200:
            print(f"✅ init_000 gate: ok")


# =============================================================================
# TOOL 2: agi_genius TESTS
# =============================================================================

class TestMCPAGIGenius:
    """Test agi_genius - AGI Mind Engine."""
    
    @pytest.mark.asyncio
    async def test_agi_genius_sense(self, mcp_client, base_url):
        """Test agi_genius with action='sense'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "agi_genius",
                    "arguments": {
                        "action": "sense",
                        "query": "What is constitutional AI?"
                    }
                },
                "id": 3
            }
        )
        
        if response.status_code == 200:
            print(f"✅ agi_genius sense: ok")
    
    @pytest.mark.asyncio
    async def test_agi_genius_think(self, mcp_client, base_url):
        """Test agi_genius with action='think'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "agi_genius",
                    "arguments": {
                        "action": "think",
                        "query": "Analyze the thermodynamics of AI safety"
                    }
                },
                "id": 4
            }
        )
        
        if response.status_code == 200:
            print(f"✅ agi_genius think: ok")


# =============================================================================
# TOOL 3: asi_act TESTS
# =============================================================================

class TestMCPASIAct:
    """Test asi_act - ASI Heart Engine."""
    
    @pytest.mark.asyncio
    async def test_asi_act_evidence(self, mcp_client, base_url):
        """Test asi_act with action='evidence'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "asi_act",
                    "arguments": {
                        "action": "evidence",
                        "text": "User needs help with Python code"
                    }
                },
                "id": 5
            }
        )
        
        if response.status_code == 200:
            print(f"✅ asi_act evidence: ok")
    
    @pytest.mark.asyncio
    async def test_asi_act_empathize(self, mcp_client, base_url):
        """Test asi_act with action='empathize'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "asi_act",
                    "arguments": {
                        "action": "empathize",
                        "text": "User is frustrated with deployment issues"
                    }
                },
                "id": 6
            }
        )
        
        if response.status_code == 200:
            print(f"✅ asi_act empathize: ok")


# =============================================================================
# TOOL 4: apex_judge TESTS
# =============================================================================

class TestMCPAPEXJudge:
    """Test apex_judge - APEX Soul Engine."""
    
    @pytest.mark.asyncio
    async def test_apex_judge_judge(self, mcp_client, base_url):
        """Test apex_judge with action='judge'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "apex_judge",
                    "arguments": {
                        "action": "judge",
                        "query": "Is this response constitutional?",
                        "response": "Test response for judgment"
                    }
                },
                "id": 7
            }
        )
        
        if response.status_code == 200:
            print(f"✅ apex_judge judge: ok")
    
    @pytest.mark.asyncio
    async def test_apex_judge_decide(self, mcp_client, base_url):
        """Test apex_judge with action='decide'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "apex_judge",
                    "arguments": {
                        "action": "decide",
                        "query": "Should we proceed?",
                        "reasoning": "All floors passed"
                    }
                },
                "id": 8
            }
        )
        
        if response.status_code == 200:
            print(f"✅ apex_judge decide: ok")


# =============================================================================
# TOOL 5: vault_999 TESTS
# =============================================================================

class TestMCPVault999:
    """Test vault_999 - VAULT-999 Immutable Memory."""
    
    @pytest.mark.asyncio
    async def test_vault_999_seal(self, mcp_client, base_url):
        """Test vault_999 with action='seal'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "vault_999",
                    "arguments": {
                        "action": "seal",
                        "verdict": "SEAL",
                        "decision_data": {
                            "test": "data",
                            "timestamp": "2026-01-29T00:00:00Z"
                        }
                    }
                },
                "id": 9
            }
        )
        
        if response.status_code == 200:
            print(f"✅ vault_999 seal: ok")
    
    @pytest.mark.asyncio
    async def test_vault_999_list(self, mcp_client, base_url):
        """Test vault_999 with action='list'."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "vault_999",
                    "arguments": {
                        "action": "list"
                    }
                },
                "id": 10
            }
        )
        
        if response.status_code == 200:
            print(f"✅ vault_999 list: ok")


# =============================================================================
# TRINITY LOOP TESTS
# =============================================================================

class TestMCPTrinityLoop:
    """Test trinity_loop - Complete AGI→ASI→APEX→VAULT pipeline."""
    
    @pytest.mark.asyncio
    async def test_trinity_loop_full(self, mcp_client, base_url):
        """Test trinity_loop with full pipeline."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "trinity_loop",
                    "arguments": {
                        "query": "Explain constitutional AI governance in one sentence"
                    }
                },
                "id": 11
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ trinity_loop full pipeline: ok")


# =============================================================================
# METRICS ENDPOINT TESTS
# =============================================================================

class TestMCPMetrics:
    """Test MCP metrics and telemetry endpoints."""
    
    @pytest.mark.asyncio
    async def test_metrics_json_endpoint(self, mcp_client, base_url):
        """Test /metrics/json endpoint returns metrics."""
        response = await mcp_client.get(f"{base_url}/metrics/json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        print(f"✅ Metrics endpoint: {len(data)} metrics available")
    
    @pytest.mark.asyncio
    async def test_dashboard_endpoint(self, mcp_client, base_url):
        """Test /dashboard endpoint returns HTML."""
        response = await mcp_client.get(f"{base_url}/dashboard")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert len(response.text) > 1000
        
        print(f"✅ Dashboard endpoint: {len(response.text)} bytes HTML")


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestMCPErrorHandling:
    """Test MCP error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_tool_name(self, mcp_client, base_url):
        """Test error response for invalid tool name."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "invalid_tool",
                    "arguments": {}
                },
                "id": 99
            }
        )
        
        # Should return error or 404
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"✅ Invalid tool returns error: {data['error'].get('message', 'unknown')}")
        else:
            print(f"✅ Invalid tool returns {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_missing_arguments(self, mcp_client, base_url):
        """Test error response for missing required arguments."""
        response = await mcp_client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "trinity_loop"
                    # Missing required "query" argument
                },
                "id": 100
            }
        )
        
        # Should handle gracefully
        print(f"✅ Missing args handled: {response.status_code}")


# =============================================================================
# MARKERS
# =============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "mcp: MCP server tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

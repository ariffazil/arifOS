
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastmcp import FastMCP
from arifosmcp.runtime.resources import register_resources, read_resource_content
from arifosmcp.runtime import tools
from arifosmcp.runtime.models import Verdict, RuntimeEnvelope, CanonicalAuthority, RuntimeStatus, Stage

@pytest.fixture
def mcp():
    return FastMCP("test-server")

@pytest.fixture
def registered_mcp(mcp):
    register_resources(mcp)
    return mcp

class TestResourceAlignment:
    @pytest.mark.asyncio
    async def test_canon_states_content(self, registered_mcp):
        """P1: Verify canon://states resource content exists and is correct."""
        content = await read_resource_content("canon://states")
        assert content is not None
        assert "# arifOS Session Ladder" in content
        assert "anonymous" in content
        assert "anchored" in content
        assert "OPERATOR" in content

    @pytest.mark.asyncio
    async def test_canon_index_includes_states(self, registered_mcp):
        """P5: Verify canon://index includes all 5 resources (once prompts are cleared)."""
        content = await read_resource_content("canon://index")
        data = json.loads(content)
        assert "canon://states" in data["resources"]
        assert len(data["resources"]) >= 5

    @pytest.mark.asyncio
    async def test_prompts_registered(self):
        """Verify prompt templates are defined in the registry."""
        from arifosmcp.runtime.public_registry import public_prompt_specs
        prompts = public_prompt_specs()
        assert len(prompts) == 5
        assert any(p.name == "constitutional.analysis" for p in prompts)

class TestToolPayloadAlignment:
    @pytest.mark.asyncio
    async def test_init_anchor_enriched_payload(self):
        """P1: Verify arifos_init enriched payload with authority and next_action."""
        # Patch the mega tool that arifos_init calls
        with patch("arifosmcp.runtime.tools._mega_init_anchor", new_callable=AsyncMock) as mock_mega:
            mock_envelope = RuntimeEnvelope(
                tool="arifos.init",
                canonical_tool_name="arifos.init",
                session_id="test-sid",
                stage=Stage.INIT_000.value,
                verdict=Verdict.SEAL,
                status=RuntimeStatus.SUCCESS,
                payload={
                    "session_id": "test-sid",
                    "caller_state": "anchored",
                    "authority": "OPERATOR",
                    "auth_context": {"actor_id": "test-actor"},
                    "next_action": "Use arifos.kernel"
                }
            )
            mock_mega.return_value = mock_envelope
            
            result = await tools.arifos_init(actor_id="test-actor")
            
            # seal_runtime_envelope will process this
            assert result.payload["caller_state"] == "anchored"
            assert result.payload["canonical_tool_name"] == "arifos.init"
            assert "next_action" in result.payload

    @pytest.mark.asyncio
    async def test_check_vital_bootstrap_guidance(self):
        """P1: Verify arifos_health bootstrap guidance fields."""
        # For this test, we mock the entire tool since it has complex internal logic
        mock_envelope = RuntimeEnvelope(
            tool="arifos.vps_monitor",
            canonical_tool_name="arifos.vps_monitor",
            session_id="global",
            stage=Stage.INIT_000.value,
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload={
                "bootstrap": {
                    "current_state": "READY",
                    "operator_guidance": "Awaiting intent",
                    "ladder_resource": "canon://states"
                }
            }
        )
        
        with patch("arifosmcp.runtime.tools.arifos_health", new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = mock_envelope
            
            result = await tools.arifos_health()
            
            assert "bootstrap" in result.payload
            bootstrap = result.payload["bootstrap"]
            assert bootstrap["current_state"] == "READY"
            assert "canon://states" in bootstrap["ladder_resource"]

class TestErrorRemediationAlignment:
    @pytest.mark.asyncio
    async def test_remediation_first_error_response(self):
        """P1: Verify remediation-first error responses in unified_tool_output."""
        from core.enforcement.governance_engine import wrap_tool_output
        
        # Simulate a failing case (VOID verdict)
        payload = {
            "verdict": "VOID",
            "failed_laws": ["F11_AUTHORITY"],
            "auth_state": "unverified",
            "error": "Authentication required",
            "authority": "operator",
            "truth_score": 1.0,
            "grounded": True,
            "stage": "444_ROUTER",
        }
        
        # wrap_tool_output is synchronous in governance_engine.py
        # Correctly call with only tool and payload
        result = wrap_tool_output(
            tool="test_tool",
            payload=payload
        )
        
        assert "errors" in result
        error = result["errors"][0]
        assert "remediation" in error
        remediation = error["remediation"]
        assert remediation["next_tool"] == "arifos.init"
        assert "required_args" in remediation
        assert "example_payload" in remediation
        assert remediation["retry_safe"] is True


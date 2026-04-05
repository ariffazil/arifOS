
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastmcp import FastMCP
from arifosmcp.runtime.resources import register_resources, read_resource_content
from arifosmcp.runtime.tools import init_anchor, check_vital
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
        assert len(prompts) == 4
        assert any(p.name == "bootstrap_session" for p in prompts)

class TestToolPayloadAlignment:
    @pytest.mark.asyncio
    async def test_init_anchor_enriched_payload(self):
        """P1: Verify init_anchor enriched payload with authority and next_action."""
        # We need to mock _wrap_call because init_anchor calls it
        # and _wrap_call calls call_kernel which requires a running server/engine
        with patch("arifosmcp.runtime.tools._wrap_call", new_callable=AsyncMock) as mock_wrap:
            mock_envelope = RuntimeEnvelope(
                tool="init_anchor",
                session_id="test-sid",
                stage=Stage.INIT_000.value,
                verdict=Verdict.SEAL,
                status=RuntimeStatus.SUCCESS,
                payload={
                    "session_id": "test-sid",
                    "caller_state": "anchored",
                    "authority": "OPERATOR",
                    "auth_context": {"actor_id": "test-actor"},
                    "next_action": "Use arifOS_kernel"
                }
            )
            mock_wrap.return_value = mock_envelope
            
            result = await init_anchor(actor_id="test-actor")
            
            # Since we mock _wrap_call, we just need to verify it returns what we expect
            assert result.payload["authority"]["claim_status"] == "anchored"
            assert "next_action" in result.payload
            assert result.payload["caller_state"] == "anchored"

    @pytest.mark.asyncio
    async def test_check_vital_bootstrap_guidance(self):
        """P1: Verify check_vital bootstrap guidance fields."""
        with patch("arifosmcp.runtime.tools._wrap_call", new_callable=AsyncMock) as mock_wrap:
            mock_envelope = RuntimeEnvelope(
                tool="check_vital",
                session_id="global",
                stage=Stage.INIT_000.value,
                verdict=Verdict.SEAL,
                status=RuntimeStatus.SUCCESS,
                payload={}
            )
            mock_wrap.return_value = mock_envelope
            
            with patch("arifosmcp.runtime.tools._normalize_session_id", return_value="global"):
                # GovernanceKernel mock removed as it's no longer used in check_vital
                with patch("core.state.session_manager.session_manager.get_session", return_value=None):
                    result = await check_vital()
                    
                    assert "bootstrap" in result.payload
                    bootstrap = result.payload["bootstrap"]
                    assert "current_state" in bootstrap
                    assert "operator_guidance" in bootstrap
                    assert "canon://states" in bootstrap["ladder_resource"]

class TestErrorRemediationAlignment:
    @pytest.mark.asyncio
    async def test_remediation_first_error_response(self):
        """P1: Verify remediation-first error responses in unified_tool_output."""
        from arifosmcp.core.enforcement.governance_engine import wrap_tool_output
        
        # Simulate a failing case (VOID verdict)
        payload = {
            "verdict": "VOID",
            "failed_laws": ["F11_AUTHORITY"],
            "auth_state": "unverified",
            "error": "Authentication required",
            "stage": "444_ROUTER",
            "session_id": "test-session"
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
        assert remediation["next_tool"] == "init_anchor"
        assert "required_args" in remediation
        assert "example_payload" in remediation
        assert remediation["retry_safe"] is True


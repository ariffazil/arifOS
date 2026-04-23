"""
Tests for MODEL_SOUL verification and three-layer identity binding in init_anchor.
"""
import pytest
from arifosmcp.runtime.tools import init_anchor
from arifosmcp.runtime.models import RuntimeStatus


@pytest.mark.asyncio
async def test_init_anchor_v2_function_returns_flat_payload():
    """Test init_anchor function directly to verify flat V2 payload with three-layer binding."""
    payload = {
        "actor_id": "Antigravity",
        "intent": "Verify model soul",
        "model_soul": {
            "base_identity": {
                "provider": "google",
                "model_family": "gemini",
                "model_variant": "gemini-2.0-flash",
                "runtime_class": "flash"
            }
        }
    }
    
    envelope = await init_anchor(mode="init", **payload)
    
    # Check RuntimeEnvelope
    assert envelope.status == RuntimeStatus.SUCCESS
    
    # Check flattened payload content
    res = envelope.payload
    assert res["ok"] is True
    assert res["tool"] == "init_anchor"
    assert res["result_type"] == "init_anchor_result@v2"
    
    result = res["result"]
    # Google/Gemini matches provider soul via models lookup -> verified
    assert result["base_identity"]["verification_status"] in ("verified", "mood_matched")
    # Self-claim boundary should be present
    assert result["self_claim_boundary"] is not None
    
    # Check Phase 2 Identity Split
    assert result["declared_actor_id"] == "Antigravity"
    assert result["auth_state"] == "claimed_only"
    
    # Check bound session exists
    assert "bound_session" in result
    assert result["bound_session"]["bound_role"] is not None


@pytest.mark.asyncio
async def test_init_anchor_v2_with_deployment_id():
    """Test init_anchor V2 with explicit deployment_id for runtime profile lookup."""
    payload = {
        "actor_id": "TestUser",
        "intent": "Test deployment lookup",
        "deployment_id": "vps_main_arifos",
        "model_soul": {
            "base_identity": {
                "provider": "minimax",
                "model_family": "minimax",
                "model_variant": "MiniMax-M2.7",
                "runtime_class": "M2.7"
            }
        }
    }
    
    envelope = await init_anchor(mode="init", **payload)
    res = envelope.payload
    
    # With deployment_id, should find runtime profile -> runtime_attested
    assert res["result"]["base_identity"]["verification_status"] == "runtime_attested"
    assert res["result"]["bound_session"]["runtime"] is not None


@pytest.mark.asyncio
async def test_init_anchor_v2_no_soul():
    """Test init_anchor V2 without model_soul."""
    envelope = await init_anchor(mode="init", actor_id="BasicUser", intent="No soul test")
    res = envelope.payload
    
    assert res["result_type"] == "init_anchor_result@v2"
    # No model_soul should be "unverified"
    assert res["result"]["base_identity"]["verification_status"] == "unverified"


@pytest.mark.asyncio
async def test_init_anchor_v2_claimed_only():
    """Test init_anchor V2 with an unknown model (not in registry)."""
    payload = {
        "intent": "Claimed only test",
        "model_soul": {
            "base_identity": {
                "provider": "unknown",
                "model_family": "alien",
                "model_variant": "alien-model-v9"
            }
        }
    }
    
    envelope = await init_anchor(mode="init", **payload)
    res = envelope.payload
    
    # Unknown model should be "unverified" (no registry match)
    assert res["result"]["base_identity"]["verification_status"] == "unverified"
    # Bound role should be untrusted_guest for unverified models
    assert res["result"]["bound_session"]["bound_role"] == "untrusted_guest"

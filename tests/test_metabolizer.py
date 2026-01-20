
"""
Test Component 4: Metabolizer
============================
Verifies the Encoder -> Metabolizer -> Decoder pipeline.

Canonical Location: arifos.orchestrator.metabolizer (v49 single-body)
"""
import pytest

from arifos.core.orchestrator.metabolizer import (AAAMetabolizer,
                                             PresentationStrategy, UserProfile)


@pytest.fixture
def metabolizer():
    return AAAMetabolizer()

def test_encoder_standard_json(metabolizer):
    """Test standard JSON parsing"""
    raw_output = {
        "result": {
            "verdict": "SEAL",
            "summary": "Operation Successful",
            "entropy_delta": -1.5
        }
    }
    semantics = metabolizer.encoder.encode(raw_output)
    assert semantics.status == "SEAL"
    assert semantics.metrics["delta_s"] == -1.5
    assert not semantics.is_emergency

def test_encoder_error_handling(metabolizer):
    """Test error wrapping"""
    raw_error = {
        "error": {
            "code": 500,
            "message": "Database Timeout"
        }
    }
    semantics = metabolizer.encoder.encode(raw_error)
    assert semantics.status == "ERROR"
    assert semantics.is_emergency == True

def test_metabolizer_strategy_expert(metabolizer):
    """Test expert profile strategy"""
    # Mock environment variable if possible, or just inject profile
    metabolizer.metabolizer.current_profile = UserProfile.EXPERT

    semantics = metabolizer.encoder.encode({"result": {"verdict": "SEAL"}})
    strategy = metabolizer.metabolizer.metabolize(semantics)

    assert strategy.style == "technical"
    assert strategy.language_mix == True
    assert strategy.show_metrics == True

def test_metabolizer_strategy_emergency(metabolizer):
    """Test emergency override"""
    semantics = metabolizer.encoder.encode({"result": {"verdict": "VOID"}})
    strategy = metabolizer.metabolizer.metabolize(semantics)

    assert strategy.style == "alert"
    assert strategy.tone == "urgent"

def test_decoder_rendering(metabolizer):
    """Test text rendering"""
    raw_output = {
        "result": {
            "verdict": "SEAL",
            "summary": "System Ready",
            "entropy_delta": -0.5,
            "humility": 0.04
        }
    }
    # Force Expert Strategy
    metabolizer.metabolizer.current_profile = UserProfile.EXPERT

    output = metabolizer.process(raw_output)

    assert "🟢 SEAL" in output
    assert "System Ready" in output
    assert "Ω₀" in output
    assert "Ditempa Bukan Diberi" in output


# Phase 9 Feature Tests

def test_phase9_phoenix72_cooling(metabolizer):
    """Test Phoenix-72 cooling metadata rendering."""
    raw_output = {
        "verdict": "SABAR",
        "session_id": "session_cooling_test",
        "stage": "888_JUDGE",
        "output": {
            "phoenix72_cooling": {
                "tier": 2,
                "tier_label": "SABAR",
                "cooling_hours": 72,
                "cooled_until": "2026-01-20T12:00:00Z",
                "status": "COOLING",
            },
        },
    }

    output = metabolizer.process(raw_output)

    assert "Phoenix-72 Cooling" in output
    assert "Tier 2" in output
    assert "SABAR" in output
    assert "72h" in output


def test_phase9_eureka_sieve_memory(metabolizer):
    """Test EUREKA sieve memory band rendering."""
    raw_output = {
        "verdict": "SEAL",
        "session_id": "session_memory_test",
        "stage": "999_VAULT",
        "output": {
            "memory_band": "L2_WITNESS",
            "eureka_sieve": {
                "ttl_days": 90,
                "expiry": "2026-04-18T00:00:00Z",
                "description": "Verified Facts (90 days)",
            },
        },
    }

    output = metabolizer.process(raw_output)

    assert "L2_WITNESS" in output
    assert "90 days" in output


def test_phase9_zkpc_receipt(metabolizer):
    """Test zkPC receipt rendering."""
    raw_output = {
        "verdict": "SEAL",
        "session_id": "session_zkpc_test",
        "stage": "889_PROOF",
        "output": {
            "zkpc_receipt_id": "receipt_test_123",
            "zkpc_hash": "sha256_abcd1234efgh5678",
            "merkle_root": "merkle_root_xyz",
            "vault_ledger": "L1_cooling_ledger.jsonl",
        },
    }

    # Force expert profile to show zkPC
    metabolizer.metabolizer.current_profile = UserProfile.EXPERT

    output = metabolizer.process(raw_output)

    assert "zkPC Receipt" in output
    assert "receipt_test_123" in output


def test_phase9_full_stack(metabolizer):
    """Test full Phase 9 stack with all features."""
    raw_output = {
        "verdict": "SEAL",
        "session_id": "session_full_phase9",
        "stage": "999_VAULT",  # Canonical name
        "latency_ms": 67.3,
        "floor_scores": {
            "F1_Amanah": {"pass": True, "score": 1.0},
            "F2_Truth": {"pass": True, "score": 0.99},
            "F8_Genius": {"pass": True, "score": 0.85},
        },
        "output": {
            "phoenix72_cooling": {
                "tier": 1,
                "tier_label": "WARM",
                "cooling_hours": 42,
                "cooled_until": "2026-01-20T06:00:00Z",
                "status": "COOLING",
            },
            "memory_band": "L2_WITNESS",
            "eureka_sieve": {
                "ttl_days": 90,
                "expiry": "2026-04-18T00:00:00Z",
                "description": "Verified Facts (90 days)",
            },
            "zkpc_receipt_id": "receipt_full_test",
            "zkpc_hash": "sha256_full_hash",
            "merkle_root": "merkle_full_root",
        },
    }

    # Force expert profile
    metabolizer.metabolizer.current_profile = UserProfile.EXPERT

    output = metabolizer.process(raw_output)

    # Verify all Phase 9 features appear
    assert "Phoenix-72 Cooling" in output
    assert "Tier 1" in output
    assert "L2_WITNESS" in output
    assert "zkPC Receipt" in output
    assert "session_full_phase9" in output
    assert "999_VAULT" in output


def test_aclip_stage_inference():
    """Test aCLIP Protocol v49 stage inference from tool names."""
    from arifos.core.orchestrator.mcp_gateway import MCPGateway

    gateway = MCPGateway()

    # Test all 10 canonical aCLIP stages
    assert gateway._infer_stage_from_tool("vault/init") == "000_INIT"
    assert gateway._infer_stage_from_tool("sense_patterns") == "111_SENSE"
    assert gateway._infer_stage_from_tool("agi/think") == "222_THINK"
    assert gateway._infer_stage_from_tool("reason_about") == "333_ATLAS"
    assert gateway._infer_stage_from_tool("align_values") == "444_ALIGN"
    assert gateway._infer_stage_from_tool("asi/empathy") == "555_EMPATHY"
    assert gateway._infer_stage_from_tool("bridge_neuro") == "666_BRIDGE"
    assert gateway._infer_stage_from_tool("reflect_verdict") == "777_EUREKA"
    assert gateway._infer_stage_from_tool("apex/seal") == "888_JUDGE"
    assert gateway._infer_stage_from_tool("vault/store") == "999_VAULT"

    # Test numeric code fallback
    assert gateway._infer_stage_from_tool("tool_111") == "111_SENSE"
    assert gateway._infer_stage_from_tool("tool_999") == "999_VAULT"

    # Test unknown tools
    assert gateway._infer_stage_from_tool("random_tool") == "unknown"

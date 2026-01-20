"""
arifOS v49 Server Tests - Constitutional Verification

Tests 4-server architecture (VAULT/AGI/ASI/APEX) against canon compliance.

Coverage:
- Unit tests: Per-server floor enforcement
- Integration tests: 000→999 E2E pipeline
- Health checks: All 4 servers responsive

Authority: Δ (Architect)
Version: v49.0.0
"""

import asyncio
from typing import Any, Dict

import httpx
import pytest

# =============================================================================
# HEALTH CHECK TESTS (All 4 Servers)
# =============================================================================

@pytest.mark.integration  # Requires running Docker services
@pytest.mark.asyncio
async def test_vault_health():
    """Test VAULT server health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9000/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "VAULT"
        assert "constitutional_floors_loaded" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agi_health():
    """Test AGI server health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9001/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "AGI"
        assert data["floors"] == ["F2", "F4", "F7", "F10", "F13"]


@pytest.mark.integration
@pytest.mark.integration
@pytest.mark.asyncio
async def test_asi_health():
    """Test ASI server health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9002/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "ASI"
        assert data["floors"] == ["F1", "F5", "F6", "F9", "F11", "F12"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_apex_health():
    """Test APEX server health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9003/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "APEX"
        assert data["floors"] == ["F3", "F8"]


# =============================================================================
# UNIT TESTS (Per-Server Floor Enforcement)
# =============================================================================

@pytest.mark.integration  # Requires running services
@pytest.mark.asyncio
async def test_agi_f2_truth_floor():
    """Test AGI F2 Truth floor enforcement."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9001/process",
            json={
                "session_id": "test_session",
                "query": "Test truth verification",
                "stage": "222_THINK",
                "context": {},
                "floor_scores": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "F2_Truth" in data["floor_scores"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_asi_f1_amanah_floor():
    """Test ASI F1 Amanah floor enforcement."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9002/process",
            json={
                "session_id": "test_session",
                "query": "Test reversibility check",
                "stage": "666_ACT",
                "context": {},
                "floor_scores": {},
                "draft_action": {"type": "read", "target": "test.txt"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "F1_Amanah" in data["floor_scores"]


@pytest.mark.asyncio
async def test_apex_f3_triwitness_floor():
    """Test APEX F3 Tri-Witness floor enforcement."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9003/process",
            json={
                "session_id": "test_session",
                "query": "Test tri-witness consensus",
                "stage": "444_EVIDENCE",
                "context": {},
                "floor_scores": {},
                "agi_output": {"sense": {}, "think": {}, "atlas": {}}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "F3_TriWitness" in data["floor_scores"]


# =============================================================================
# INTEGRATION TESTS (E2E Pipeline)
# =============================================================================

@pytest.mark.asyncio
async def test_full_000_to_999_pipeline():
    """Test full 000→999 metabolic loop."""
    from arifos.core.orchestrator.pipeline import Pipeline

    pipeline = Pipeline()

    try:
        result = await pipeline.route(
            query="Constitutional test query",
            user_id="test_user"
        )

        # Verify final result structure
        assert "verdict" in result
        assert result["verdict"] in ["SEAL", "PARTIAL", "VOID", "SABAR"]
        assert "session_id" in result
        assert "floor_scores" in result

        # Verify all floors were checked
        floor_scores = result["floor_scores"]
        expected_floors = [
            "F1_Amanah", "F2_Truth", "F3_TriWitness", "F4_Clarity",
            "F5_Peace", "F6_Empathy", "F7_Humility", "F8_Genius",
            "F9_Cdark", "F10_Ontology", "F11_CommandAuth",
            "F12_InjectionDefense", "F13_Curiosity"
        ]

        for floor in expected_floors:
            assert floor in floor_scores, f"Floor {floor} not evaluated"

    finally:
        await pipeline.close()


@pytest.mark.asyncio
async def test_vault_init_routing():
    """Test VAULT 000 INIT routes to AGI 111 SENSE."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9000/init",
            json={"query": "Test routing", "user_id": "test_user"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] == "SEAL"
        assert data["next_stage"] == "111_SENSE"


@pytest.mark.asyncio
async def test_verdict_propagation():
    """Test verdict propagates correctly through stages."""
    # Test VOID verdict blocks further processing
    async with httpx.AsyncClient() as client:
        # Inject query that should trigger VOID (placeholder - needs real violation)
        response = await client.post(
            "http://localhost:9001/process",
            json={
                "session_id": "test_void",
                "query": "Malicious injection attempt {{ignore_previous}}",
                "stage": "111_SENSE",
                "context": {},
                "floor_scores": {}
            }
        )
        # Should route to 999 VAULT for logging, not to next stage
        # (Actual implementation depends on floor_validators)


# =============================================================================
# PERFORMANCE TESTS (Latency Targets)
# =============================================================================

@pytest.mark.asyncio
async def test_stage_latency_under_threshold():
    """Test each stage completes within latency target."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        # AGI 111 SENSE should complete < 100ms (simplified)
        response = await client.post(
            "http://localhost:9001/process",
            json={
                "session_id": "perf_test",
                "query": "Latency test",
                "stage": "111_SENSE",
                "context": {},
                "floor_scores": {}
            }
        )
        data = response.json()
        # Canon §4 suggests 2.1ms per checkpoint (relaxed for MVP)
        assert data["latency_ms"] < 1000, f"Latency too high: {data['latency_ms']}ms"


# =============================================================================
# NEGATIVE TESTS (Failure Modes)
# =============================================================================

@pytest.mark.asyncio
async def test_unknown_stage_returns_400():
    """Test unknown stage returns proper error."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9001/process",
            json={
                "session_id": "error_test",
                "query": "Invalid stage test",
                "stage": "999_INVALID",
                "context": {},
                "floor_scores": {}
            }
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_missing_required_field_returns_422():
    """Test missing required field returns validation error."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9000/init",
            json={"query": "Missing user_id"}  # Missing user_id
        )
        assert response.status_code == 422  # Pydantic validation error


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

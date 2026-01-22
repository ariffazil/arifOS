"""
arifOS API Unit Tests - Test FastAPI app and routes.

Tests the API endpoints using FastAPI TestClient.
All tests are independent and use mocks where appropriate.

Run with:
    pytest tests/unit/test_api_app.py -v
"""

from __future__ import annotations

import pytest

# Guard import for when FastAPI is not installed
try:
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    TestClient = None


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def client():
    """Create a test client for the API."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not installed")

    from arifos.core.integration.api import create_app
    app = create_app()
    return TestClient(app)


# =============================================================================
# TEST CLASS: APP CREATION
# =============================================================================

class TestAppCreation:
    """Test that the FastAPI app can be created."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_create_app_returns_fastapi_instance(self):
        """App factory should return a FastAPI instance."""
        from fastapi import FastAPI
        from arifos.core.integration.api import create_app

        app = create_app()
        assert isinstance(app, FastAPI)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_app_has_correct_title(self):
        """App should have correct title."""
        from arifos.core.integration.api import create_app

        app = create_app()
        assert "arifOS" in app.title

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_app_has_routes_registered(self):
        """App should have routes registered."""
        from arifos.core.integration.api import create_app

        app = create_app()
        routes = [r.path for r in app.routes]

        # Check key routes exist
        assert "/health" in routes
        assert "/ready" in routes
        assert "/live" in routes
        assert "/pipeline/run" in routes
        assert "/memory/recall" in routes


# =============================================================================
# TEST CLASS: HEALTH ENDPOINTS
# =============================================================================

class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_health_returns_200(self, client):
        """GET /health should return 200."""
        response = client.get("/health")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_health_returns_healthy_status(self, client):
        """GET /health should return healthy status."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_health_includes_version(self, client):
        """GET /health should include version."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_ready_returns_200(self, client):
        """GET /ready should return 200."""
        response = client.get("/ready")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_ready_includes_pipeline_status(self, client):
        """GET /ready should include pipeline availability."""
        response = client.get("/ready")
        data = response.json()
        assert "pipeline_available" in data

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_live_returns_200(self, client):
        """GET /live should return 200."""
        response = client.get("/live")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_live_returns_live_true(self, client):
        """GET /live should return live: true."""
        response = client.get("/live")
        data = response.json()
        assert data["live"] is True


# =============================================================================
# TEST CLASS: PIPELINE ENDPOINTS
# =============================================================================

class TestPipelineEndpoints:
    """Test pipeline execution endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_pipeline_run_returns_200(self, client):
        """POST /pipeline/run should return 200 on valid input."""
        response = client.post(
            "/pipeline/run",
            json={"query": "What is 2 + 2?"}
        )
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_pipeline_run_returns_verdict(self, client):
        """POST /pipeline/run should return a verdict."""
        response = client.post(
            "/pipeline/run",
            json={"query": "What is the capital of Malaysia?"}
        )
        data = response.json()
        assert "verdict" in data
        assert data["verdict"] in ["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD", "UNKNOWN", "ERROR"]

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_pipeline_run_returns_response_text(self, client):
        """POST /pipeline/run should return response text."""
        response = client.post(
            "/pipeline/run",
            json={"query": "Hello world"}
        )
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_pipeline_run_returns_apex_prime_contract(self, client):
        """POST /pipeline/run should return APEX PRIME public contract (v41.0.1)."""
        response = client.post(
            "/pipeline/run",
            json={"query": "Test query"}
        )
        data = response.json()
        # v41.0.1 APEX PRIME contract: {verdict, apex_pulse, response, reason_code?}
        assert "verdict" in data, "Contract should include verdict"
        assert data["verdict"] in ["SEAL", "SABAR", "VOID"], f"Invalid verdict: {data['verdict']}"
        assert "apex_pulse" in data, "Contract should include apex_pulse"
        assert "response" in data, "Contract should include response"
        # reason_code is optional (only present for non-SEAL)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_pipeline_run_with_empty_query_fails(self, client):
        """POST /pipeline/run should fail with empty query."""
        response = client.post(
            "/pipeline/run",
            json={"query": ""}
        )
        # Should return 422 (validation error)
        assert response.status_code == 422

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_pipeline_status_returns_200(self, client):
        """GET /pipeline/status should return 200."""
        response = client.get("/pipeline/status")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_pipeline_status_includes_verdicts(self, client):
        """GET /pipeline/status should include verdict list."""
        response = client.get("/pipeline/status")
        data = response.json()
        assert "verdicts" in data
        assert "SEAL" in data["verdicts"]


# =============================================================================
# TEST CLASS: MEMORY ENDPOINTS
# =============================================================================

class TestMemoryEndpoints:
    """Test L7 memory endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_memory_recall_returns_200(self, client):
        """GET /memory/recall should return 200."""
        response = client.get(
            "/memory/recall",
            params={"user_id": "test_user", "prompt": "What is Amanah?"}
        )
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_memory_recall_includes_memories_list(self, client):
        """GET /memory/recall should include memories list."""
        response = client.get(
            "/memory/recall",
            params={"user_id": "test_user", "prompt": "test query"}
        )
        data = response.json()
        assert "memories" in data
        assert isinstance(data["memories"], list)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_memory_recall_includes_l7_available_flag(self, client):
        """GET /memory/recall should include l7_available flag."""
        response = client.get(
            "/memory/recall",
            params={"user_id": "test_user", "prompt": "test"}
        )
        data = response.json()
        assert "l7_available" in data
        assert isinstance(data["l7_available"], bool)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_memory_recall_includes_confidence_ceiling(self, client):
        """GET /memory/recall should include confidence ceiling (0.85)."""
        response = client.get(
            "/memory/recall",
            params={"user_id": "test_user", "prompt": "test"}
        )
        data = response.json()
        assert "confidence_ceiling" in data
        assert data["confidence_ceiling"] == 0.85

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_memory_status_returns_200(self, client):
        """GET /memory/status should return 200."""
        response = client.get("/memory/status")
        assert response.status_code == 200


# =============================================================================
# TEST CLASS: LEDGER ENDPOINTS
# =============================================================================

class TestLedgerEndpoints:
    """Test ledger access endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_ledger_entry_returns_200(self, client):
        """GET /ledger/{entry_id} should return 200."""
        response = client.get("/ledger/test_entry_123")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_ledger_entry_returns_stub_status(self, client):
        """GET /ledger/{entry_id} should return stub status."""
        response = client.get("/ledger/test_entry")
        data = response.json()
        assert data["status"] == "not_implemented"

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_ledger_search_returns_200(self, client):
        """GET /ledger/ should return 200."""
        response = client.get("/ledger/")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_ledger_stats_returns_200(self, client):
        """GET /ledger/stats should return 200."""
        response = client.get("/ledger/stats")
        assert response.status_code == 200


# =============================================================================
# TEST CLASS: METRICS ENDPOINTS
# =============================================================================

class TestMetricsEndpoints:
    """Test metrics and floor information endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_metrics_returns_200(self, client):
        """GET /metrics should return 200."""
        response = client.get("/metrics/")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_metrics_includes_floors(self, client):
        """GET /metrics should include floors list."""
        response = client.get("/metrics/")
        data = response.json()
        assert "floors" in data
        assert len(data["floors"]) == 9  # 9 constitutional floors

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_metrics_includes_verdicts(self, client):
        """GET /metrics should include verdicts list."""
        response = client.get("/metrics/")
        data = response.json()
        assert "verdicts" in data
        assert "SEAL" in data["verdicts"]
        assert "VOID" in data["verdicts"]

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_floors_endpoint_returns_200(self, client):
        """GET /metrics/floors should return 200."""
        response = client.get("/metrics/floors")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_verdicts_endpoint_returns_200(self, client):
        """GET /metrics/verdicts should return 200."""
        response = client.get("/metrics/verdicts")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_genius_endpoint_returns_200(self, client):
        """GET /metrics/genius should return 200."""
        response = client.get("/metrics/genius")
        assert response.status_code == 200


# =============================================================================
# TEST CLASS: ROOT ENDPOINT
# =============================================================================

class TestRootEndpoint:
    """Test root endpoint."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_root_returns_200(self, client):
        """GET / should return 200."""
        response = client.get("/")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_root_includes_name(self, client):
        """GET / should include API name."""
        response = client.get("/")
        data = response.json()
        assert "name" in data
        assert "arifOS" in data["name"]

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_root_includes_version(self, client):
        """GET / should include version."""
        response = client.get("/")
        data = response.json()
        assert "version" in data

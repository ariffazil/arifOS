"""tests/test_hybrid_discovery.py — Smoke tests for arif_sense_observe hybrid_discovery."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from arifosmcp.tools.sense import arif_sense_observe


@pytest.fixture
def mock_reality_handler():
    with patch("arifosmcp.tools.sense.reality_handler") as mock:
        mock.search_brave = AsyncMock()
        yield mock

@pytest.fixture
def mock_search_index():
    with patch("arifos_wiki_tools.search.search_index") as mock:
        yield mock

def test_hybrid_discovery_format(mock_reality_handler, mock_search_index):
    """Verify the hybrid_discovery result format and basic coordination."""
    # Mock web search to return results
    mock_s_res = MagicMock()
    mock_s_res.results = [{"title": "Web Result", "url": "https://exa.ai", "snippet": "current reality"}]
    mock_s_res.engine = "exa"
    mock_reality_handler.search_brave.return_value = mock_s_res
    
    # Mock wiki search to return results
    mock_search_index.return_value = [{"rel_path": "AAA/wiki/F11.md", "excerpt": "F11 is AUDIT", "score": 1.0}]
    
    # Execute hybrid_discovery (using actor_id to trigger ephemeral session fallback)
    result = arif_sense_observe(
        mode="hybrid_discovery", 
        query="F11 floor", 
        actor_id="arif"
    )
    
    assert result["status"] == "OK"
    data = result["result"]
    assert data["mode"] == "hybrid_discovery"
    assert data["evidence_state"] == "FOUND"
    
    layers = data["knowledge_layers"]
    assert layers["local_wiki"]["status"] == "FOUND"
    assert layers["web_reality"]["status"] == "FOUND"
    assert layers["web_reality"]["source"] == "exa"
    
    reconciliation = data["reconciliation"]
    assert "state" in reconciliation
    assert isinstance(reconciliation["contradictions"], list)
    assert isinstance(reconciliation["unknowns"], list)

    physics = data["physics_kernel"]
    assert "claim_state" in physics
    assert "evidence_level" in physics
    assert "w4" in physics
    assert "delta_s" in physics

def test_hybrid_discovery_web_failure_resilience(mock_reality_handler, mock_search_index):
    """Verify local discovery works even if web search throws an error."""
    # Mock web search to throw
    mock_reality_handler.search_brave.side_effect = Exception("API Key Missing")
    
    # Mock wiki search to return results
    mock_search_index.return_value = [{"rel_path": "AAA/wiki/F11.md", "excerpt": "F11 is AUDIT", "score": 1.0}]
    
    # Execute
    result = arif_sense_observe(
        mode="hybrid_discovery", 
        query="F11 floor", 
        actor_id="arif"
    )
    
    assert result["status"] == "OK"
    data = result["result"]
    
    # Web should be unavailable
    assert data["knowledge_layers"]["web_reality"]["status"] == "UNAVAILABLE"
    assert "API Key Missing" in data["knowledge_layers"]["web_reality"]["error"]
    
    # Local should still be found
    assert data["knowledge_layers"]["local_wiki"]["status"] == "FOUND"
    
    # Evidence state should be PARTIAL (local only)
    assert data["evidence_state"] == "PARTIAL"
    assert data["verdict"] == "SABAR"
    
    # Unknowns should capture web failure
    assert any("Web source unavailable" in u for u in data["reconciliation"]["unknowns"])

def test_hybrid_discovery_no_results(mock_reality_handler, mock_search_index):
    """Verify handling when no results are found anywhere."""
    mock_s_res = MagicMock()
    mock_s_res.results = []
    mock_reality_handler.search_brave.return_value = mock_s_res
    mock_search_index.return_value = []
    
    result = arif_sense_observe(
        mode="hybrid_discovery", 
        query="nonexistent search term", 
        actor_id="arif"
    )
    
    data = result["result"]
    assert data["evidence_state"] == "EMPTY"
    assert data["verdict"] == "HOLD"
    assert data["knowledge_layers"]["local_wiki"]["status"] == "EMPTY"
    assert data["knowledge_layers"]["web_reality"]["status"] == "EMPTY"

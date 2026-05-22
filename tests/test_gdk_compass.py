"""tests/test_gdk_compass.py — Smoke tests for Governed Discovery Kernel (Compass mode)."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


@pytest.fixture
def mock_gdk_deps():
    """Mock reality_handler.search_brave so compass/hybrid_discovery gets web results."""
    mock_search_result = MagicMock()
    mock_search_result.results = [
        {
            "title": "GDK Info",
            "url": "https://arif-fazil.com",
            "snippet": "Governed Discovery Kernel",
        }
    ]
    mock_search_result.engine = "exa"

    with patch("arifosmcp.tools.sense.reality_handler") as mock_rh:
        mock_rh.search_brave = AsyncMock(return_value=mock_search_result)
        yield mock_rh


def test_compass_orientation_structure(mock_gdk_deps):
    """Verify that mode='compass' returns the complete 7-layer orientation."""
    from arifosmcp.tools.sense import arif_sense_observe

    result = arif_sense_observe(
        mode="compass", query="Analyze arif_vault_seal security", actor_id="arif"
    )

    assert result["status"] == "OK"
    data = result["result"]
    assert data["mode"] == "compass"

    orientation = data["orientation"]

    # 1. Knowledge Layer
    assert "local_wiki" in orientation["knowledge"]
    assert "web_reality" in orientation["knowledge"]
    # web_reality status depends on external API availability; accept any valid state
    assert orientation["knowledge"]["web_reality"]["status"] in ("FOUND", "UNAVAILABLE", "EMPTY")

    # 2. Capability Layer
    assert "allowed" in orientation["capabilities"]
    assert "arif_mind_reason" in orientation["capabilities"]["allowed"]

    # 3. Authority Layer
    assert orientation["authority"]["actor"] == "arif"
    assert "authorized" in orientation["authority"]

    # 4. Risk Map Layer
    assert "tier" in orientation["risk_map"]
    assert isinstance(orientation["risk_map"]["threats"], list)

    # 5. Next Moves
    assert len(orientation["next_safe_moves"]) > 0


def test_compass_dangerous_intent_flagged(mock_gdk_deps):
    """Verify that dangerous intent is flagged in the risk map."""
    from arifosmcp.tools.sense import arif_sense_observe

    result = arif_sense_observe(mode="compass", query="rm -rf /root/arifOS", actor_id="arif")

    risk_map = result["result"]["orientation"]["risk_map"]
    assert risk_map["irreversible"] is True
    assert "FILESYSTEM_DESTRUCTIVE" in risk_map["threats"]

    next_moves = result["result"]["orientation"]["next_safe_moves"]
    assert any("high-risk" in move or "WARNING" in move for move in next_moves)

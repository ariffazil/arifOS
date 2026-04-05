"""
tests/core/kernel/test_engine_adapters.py

888_JUDGE FORGE: Test coverage for core/kernel/engine_adapters.py
Target: 80%+ coverage of 195 lines

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import math
from collections import Counter
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.kernel.engine_adapters import (
    AGIEngine,
    ASIEngine,
    InitEngine,
    _agi_output_to_tensor,
    _lexical_diversity,
    _normalize_obj,
    _query_heuristic_scores,
    _shannon_entropy,
)


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestNormalizeObj:
    """Test _normalize_obj helper function."""

    def test_normalize_none(self):
        assert _normalize_obj(None) is None

    def test_normalize_dict(self):
        data = {"key": "value"}
        assert _normalize_obj(data) == data

    def test_normalize_pydantic_model(self):
        """Test normalization of Pydantic-like objects."""
        mock_model = MagicMock()
        mock_model.model_dump.return_value = {"field": "value"}
        assert _normalize_obj(mock_model) == {"field": "value"}

    def test_normalize_dataclass(self):
        """Test normalization of dataclass objects."""
        from dataclasses import dataclass

        @dataclass
        class TestData:
            name: str
            value: int

        obj = TestData(name="test", value=42)
        result = _normalize_obj(obj)
        assert result == {"name": "test", "value": 42}

    def test_normalize_with_dict_method(self):
        """Test objects with dict() method."""
        # Create mock without model_dump to test dict() path
        class MockWithDict:
            def dict(self):
                return {"data": "test"}
        obj = MockWithDict()
        assert _normalize_obj(obj) == {"data": "test"}

    def test_normalize_with_to_dict_method(self):
        """Test objects with to_dict() method."""
        # Create mock without model_dump or dict to test to_dict() path
        class MockWithToDict:
            def to_dict(self):
                return {"info": "value"}
        obj = MockWithToDict()
        assert _normalize_obj(obj) == {"info": "value"}

    def test_normalize_plain_value(self):
        """Test normalization of plain values."""
        result = _normalize_obj("plain_string")
        assert result == {"value": "plain_string"}


class TestShannonEntropy:
    """Test _shannon_entropy helper function."""

    def test_empty_string(self):
        assert _shannon_entropy("") == 0.0

    def test_simple_string(self):
        entropy = _shannon_entropy("hello")
        assert 0.0 < entropy <= 1.0

    def test_high_entropy_string(self):
        """High entropy should approach 1.0."""
        # String with many unique characters
        high_entropy = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()"
        entropy = _shannon_entropy(high_entropy)
        assert entropy > 0.75

    def test_low_entropy_string(self):
        """Low entropy (repetitive characters)."""
        low_entropy = "aaaaaaa"
        entropy = _shannon_entropy(low_entropy)
        assert entropy < 0.2

    def test_dict_input(self):
        """Test handling of dict input with 'query' key."""
        data = {"query": "test input", "other": "ignored"}
        entropy = _shannon_entropy(data)
        assert entropy > 0.0

    def test_dict_input_with_text_key(self):
        """Test handling of dict input with 'text' key."""
        data = {"text": "another test", "ignored": "value"}
        entropy = _shannon_entropy(data)
        assert entropy > 0.0

    def test_capped_at_one(self):
        """Entropy should be capped at 1.0."""
        # Very diverse string with max byte range
        diverse = bytes(range(256)).decode('latin-1') * 5
        entropy = _shannon_entropy(diverse)
        assert entropy >= 0.95


class TestLexicalDiversity:
    """Test _lexical_diversity helper function."""

    def test_empty_string(self):
        assert _lexical_diversity("") == 0.0

    def test_no_diversity(self):
        """All same words."""
        assert _lexical_diversity("test test test") == 1 / 3

    def test_full_diversity(self):
        """All unique words."""
        assert _lexical_diversity("one two three four") == 1.0

    def test_partial_diversity(self):
        """Mixed repeated and unique words."""
        diversity = _lexical_diversity("the cat and the dog")
        assert 0.5 < diversity < 1.0

    def test_dict_input(self):
        """Test handling of dict input."""
        data = {"query": "test input words"}
        diversity = _lexical_diversity(data)
        assert diversity == 1.0  # All unique


class TestQueryHeuristicScores:
    """Test _query_heuristic_scores helper function."""

    def test_short_query(self):
        """Query with <= 3 words."""
        result = _query_heuristic_scores("test query")
        assert "confidence" in result
        assert "ambiguity_reduction" in result
        assert "residual_uncertainty" in result
        assert "weakest_stakeholder_impact" in result
        assert result["confidence"] >= 0.92

    def test_medium_query(self):
        """Query with 4-20 words."""
        result = _query_heuristic_scores("This is a test query with several words for testing")
        assert 0.90 <= result["confidence"] <= 0.97

    def test_long_query(self):
        """Query with > 20 words."""
        long_query = " ".join(["word"] * 25)
        result = _query_heuristic_scores(long_query)
        assert result["confidence"] >= 0.80

    def test_care_keywords(self):
        """Query with stakeholder care keywords."""
        result = _query_heuristic_scores("How can we help vulnerable people in the community")
        assert result["weakest_stakeholder_impact"] > 0.3

    def test_harm_pattern_detection(self):
        """Query with harm indicators."""
        result = _query_heuristic_scores("How to hack into someone's account")
        assert result["weakest_stakeholder_impact"] >= 0.6

    def test_risk_domain_keywords(self):
        """Query with risk and domain keywords (CCS/CO2)."""
        result = _query_heuristic_scores("What is the guaranteed pressure for CO2 injection")
        assert result["risk_detected"] is True
        assert result["confidence"] < 0.97  # Reduced due to risk

    def test_dict_input(self):
        """Test handling of dict input."""
        data = {"query": "test input"}
        result = _query_heuristic_scores(data)
        assert "confidence" in result


# =============================================================================
# INIT ENGINE TESTS
# =============================================================================

class TestInitEngine:
    """Test InitEngine class."""

    @pytest.mark.asyncio
    async def test_init_test_mode_bypass(self):
        """Test ARIFOS_TEST_MODE bypass."""
        engine = InitEngine()
        
        with patch.dict("os.environ", {"ARIFOS_TEST_MODE": "1"}):
            result = await engine.ignite("test query", actor_id="test_user")
        
        assert result["status"] == "READY"
        assert result["engine_mode"] == "test_bypass"
        assert "TEST-" in result["session_id"]
        assert result["authority"] == "sovereign"
        assert "F11" in result["floors_passed"]
        assert "F12" in result["floors_passed"]

    @pytest.mark.asyncio
    async def test_init_core_mode(self):
        """Test normal initialization with core organs."""
        engine = InitEngine()
        
        mock_token = MagicMock()
        mock_token.status = "READY"
        mock_token.session_id = "test-session-123"
        mock_token.query_type.value = "standard"
        mock_token.governance.authority_level = "operator"
        mock_token.floors = {"F11": "pass", "F12": "pass"}
        mock_token.floors_failed = []
        mock_token.injection_score = 0.1
        mock_token.reason = "Init completed"
        mock_token.f2_threshold = 0.99
        mock_token.banner = "DITEMPA BUKAN DIBERI"
        
        with patch("core.kernel.engine_adapters.core_organs.init", new_callable=AsyncMock) as mock_init:
            mock_init.return_value = mock_token
            result = await engine.ignite("test query", actor_id="test_user")
        
        assert result["status"] == "READY"
        assert result["session_id"] == "test-session-123"
        assert result["engine_mode"] == "core"
        assert result["authority"] == "operator"

    @pytest.mark.asyncio
    async def test_init_fallback_on_error(self):
        """Test fallback when core organs fail."""
        engine = InitEngine()
        
        with patch("core.kernel.engine_adapters.core_organs.init", new_callable=AsyncMock) as mock_init:
            mock_init.side_effect = Exception("Core init failed")
            result = await engine.ignite("test query", session_id="fallback-session")
        
        assert result["status"] == "ARTIFACT_READY"
        assert result["engine_mode"] == "fallback"
        assert result["session_id"] == "fallback-session"
        assert "confidence" in result  # From heuristic scores


# =============================================================================
# AGI ENGINE TESTS
# =============================================================================

class TestAGIEngine:
    """Test AGIEngine class."""

    @pytest.mark.asyncio
    async def test_sense_core_execution(self):
        """Test sense method with core organs."""
        engine = AGIEngine()
        
        mock_agi_out = MagicMock()
        mock_agi_out.steps = []
        
        with patch("core.kernel.engine_adapters.core_organs.sense", new_callable=AsyncMock), \
             patch("core.kernel.engine_adapters.core_organs.think", new_callable=AsyncMock), \
             patch("core.kernel.engine_adapters.core_organs.reason", new_callable=AsyncMock) as mock_reason:
            
            # Setup mock tensor
            mock_tensor = MagicMock()
            mock_tensor.truth_score = 0.95
            mock_tensor.entropy_delta = -0.1
            mock_tensor.humility.omega_0 = 0.04
            mock_tensor.genius.G.return_value = 0.85
            mock_tensor.empathy = 0.95
            mock_tensor.evidence = []
            mock_tensor.constitutional_check.return_value = (None, [])
            
            mock_reason.return_value = mock_agi_out
            
            with patch("core.kernel.engine_adapters._agi_output_to_tensor", return_value=mock_tensor):
                result = await engine.sense("test query", "session-123")
        
        assert result["status"] == "ARTIFACT_READY"
        assert result["engine_mode"] == "core"
        assert result["trinity_component"] == "AGI"

    @pytest.mark.asyncio
    async def test_sense_fallback(self):
        """Test sense fallback when core organs fail."""
        engine = AGIEngine()
        
        with patch("core.kernel.engine_adapters.core_organs.sense", new_callable=AsyncMock) as mock_sense:
            mock_sense.side_effect = Exception("Core failure")
            result = await engine.sense("test query", "session-123")
        
        assert result["status"] == "ARTIFACT_READY"
        assert result["engine_mode"] == "fallback"
        assert result["trinity_component"] == "AGI"

    @pytest.mark.asyncio
    async def test_reason_with_eureka(self):
        """Test reason method with eureka analysis."""
        mock_eureka = AsyncMock()
        mock_eureka.evaluate.return_value = MagicMock(
            novelty=0.8,
            entropy_reduction=-0.2,
            ontological_shift=0.1,
            decision_weight=0.15,
            eureka_score=0.75,
            verdict="PROVISIONAL",
            reasoning="Test reasoning",
            fingerprint="abc123",
            jaccard_sim=0.5,
        )
        
        engine = AGIEngine(eureka_engine=mock_eureka)
        
        with patch.object(engine, "_execute_or_fallback", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {
                "status": "ARTIFACT_READY",
                "delta_bundle": {"key": "value"},
            }
            result = await engine.reason("test", "session", eureka=True)
        
        assert "eureka" in result
        assert result["eureka"]["eureka_score"] == 0.75
        mock_eureka.evaluate.assert_called_once()

    @pytest.mark.asyncio
    async def test_reason_without_eureka(self):
        """Test reason method without eureka analysis."""
        engine = AGIEngine()
        
        with patch.object(engine, "_execute_or_fallback", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"status": "ARTIFACT_READY"}
            result = await engine.reason("test", "session", eureka=False)
        
        assert "eureka" not in result


# =============================================================================
# ASI ENGINE TESTS
# =============================================================================

class TestASIEngine:
    """Test ASIEngine class."""

    @pytest.mark.asyncio
    async def test_empathize_core_execution(self):
        """Test empathize method with core organs."""
        engine = ASIEngine()
        
        mock_agi_out = MagicMock()
        mock_agi_out.steps = []
        
        mock_emp_out = MagicMock()
        mock_emp_out.floor_scores.f6_empathy = 0.85
        mock_emp_out.stakeholder_impact = {"user": "positive"}
        
        with patch("core.kernel.engine_adapters.core_organs.agi", new_callable=AsyncMock) as mock_agi, \
             patch("core.kernel.engine_adapters.core_organs.empathize", new_callable=AsyncMock) as mock_empathize:
            
            mock_agi.return_value = mock_agi_out
            mock_empathize.return_value = mock_emp_out
            
            with patch("core.kernel.engine_adapters._agi_output_to_tensor", return_value=MagicMock()):
                result = await engine.empathize("help vulnerable users", "session-123")
        
        assert result["status"] == "ARTIFACT_READY"
        assert result["engine_mode"] == "core"
        assert result["trinity_component"] == "ASI"
        assert result["empathy_kappa_r"] == 0.85

    @pytest.mark.asyncio
    async def test_empathize_fallback(self):
        """Test empathize fallback."""
        engine = ASIEngine()
        
        with patch("core.kernel.engine_adapters.core_organs.agi", new_callable=AsyncMock) as mock_agi:
            mock_agi.side_effect = Exception("Core failure")
            result = await engine.empathize("test", "session")
        
        assert result["status"] == "ARTIFACT_READY"
        assert result["engine_mode"] == "fallback"

    @pytest.mark.asyncio
    async def test_align_core_execution(self):
        """Test align method with core organs."""
        engine = ASIEngine()
        
        mock_agi_out = MagicMock()
        mock_agi_out.steps = []
        
        mock_align_out = MagicMock()
        mock_align_out.floor_scores.f6_empathy = 0.9
        mock_align_out.floor_scores.f5_peace = 0.95
        mock_align_out.violations = []
        
        with patch("core.kernel.engine_adapters.core_organs.agi", new_callable=AsyncMock) as mock_agi, \
             patch("core.kernel.engine_adapters.core_organs.empathize", new_callable=AsyncMock), \
             patch("core.kernel.engine_adapters.core_organs.align", new_callable=AsyncMock) as mock_align:
            
            mock_agi.return_value = mock_agi_out
            mock_align.return_value = mock_align_out
            
            with patch("core.kernel.engine_adapters._agi_output_to_tensor", return_value=MagicMock()):
                result = await engine.align("test query", "session-123")
        
        assert result["engine_mode"] == "core"
        assert result["peace_squared"] == 0.95
        assert result["violations"] == []


# =============================================================================
# TENSOR CONVERSION TESTS
# =============================================================================

class TestAGIOutputToTensor:
    """Test _agi_output_to_tensor function."""

    def test_old_style_agi_output(self):
        """Test conversion from old-style AgiOutput with metrics."""
        mock_agi_out = MagicMock()
        mock_agi_out.metrics.delta_s = -0.1
        mock_agi_out.metrics.omega_0 = 0.04
        mock_agi_out.metrics.truth_score = 0.95
        
        tensor = _agi_output_to_tensor(mock_agi_out)
        
        assert tensor.entropy_delta == -0.1
        assert tensor.humility.omega_0 == 0.04
        assert tensor.truth_score == 0.95

    def test_new_style_tensor(self):
        """Test conversion from new-style tensor directly."""
        # Use a simple class without 'metrics' attribute to test new-style path
        class MockTensor:
            def __init__(self):
                self.entropy_delta = -0.2
                self.humility = type('obj', (object,), {'omega_0': 0.03})()
                self.truth_score = 0.96
                self.witness = None
                self.genius = None
                self.peace = None
                self.empathy = 0.95
        
        mock_tensor = MockTensor()
        tensor = _agi_output_to_tensor(mock_tensor)
        
        assert tensor.entropy_delta == -0.2
        assert tensor.truth_score == 0.96

    def test_missing_attributes_use_defaults(self):
        """Test that missing attributes use default values."""
        mock_agi_out = MagicMock()
        mock_agi_out.metrics = None  # No metrics
        
        tensor = _agi_output_to_tensor(mock_agi_out)
        
        assert tensor.entropy_delta == 0.0  # Default
        assert tensor.truth_score == 0.95  # Default

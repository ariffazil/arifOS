"""
tests/core/organs/test_trinity_organs.py — Trinity Organ Test Suite (V6 - Working with Lazy Imports)

Tests for:
- _1_agi.py (AGI Mind - Delta)
- _2_asi.py (ASI Heart - Omega)
- _3_apex.py (APEX Soul - Psi)

Target: 90%+ coverage for Trinity architecture
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
from types import ModuleType


# =============================================================================
# AGI MIND (_1_agi.py) TESTS
# =============================================================================


class TestAgiMind:
    """Test AGI Mind organ - Stage 111-333 Reasoning Pipeline."""

    @pytest.fixture
    def mock_ollama_response(self):
        """Mock successful Ollama response."""
        mock_env = Mock()
        mock_env.ok = True
        mock_env.payload = {
            "response": "Test analysis result with insight",
            "usage": {"completion_tokens": 100},
            "truncated": False,
        }
        return mock_env

    @pytest.fixture
    def mock_ollama_failure(self):
        """Mock failed Ollama response."""
        mock_env = Mock()
        mock_env.ok = False
        mock_env.payload = {"error": "OLLAMA_UNREACHABLE"}
        return mock_env

    @pytest.mark.asyncio
    async def test_agi_basic_reasoning(self, mock_ollama_response):
        """Test AGI completes 111→222→333 pipeline successfully."""
        # The import is lazy (inside function), so we need to patch the module before import
        mock_ollama_module = ModuleType("arifosmcp.intelligence.tools.ollama_local")
        mock_ollama_module.ollama_local_generate = AsyncMock(return_value=mock_ollama_response)
        sys.modules["arifosmcp.intelligence.tools.ollama_local"] = mock_ollama_module

        try:
            from core.organs._1_agi import agi

            result = await agi(
                query="Analyze this test query", session_id="test-session-001", action="full"
            )

            # Result is a dict
            assert result["session_id"] == "test-session-001"
            assert result["stage"] == "333"
            assert "steps" in result
            assert len(result["steps"]) == 3
            assert result["steps"][0]["phase"] == "111_search"
            assert result["steps"][1]["phase"] == "222_analyze"
            assert result["steps"][2]["phase"] == "333_synthesis"
        finally:
            # Cleanup
            if "arifosmcp.intelligence.tools.ollama_local" in sys.modules:
                del sys.modules["arifosmcp.intelligence.tools.ollama_local"]
            if "core.organs._1_agi" in sys.modules:
                del sys.modules["core.organs._1_agi"]

    @pytest.mark.asyncio
    async def test_agi_phase_111_failure(self, mock_ollama_failure):
        """Test AGI handles Phase 111 failure gracefully."""
        mock_ollama_module = ModuleType("arifosmcp.intelligence.tools.ollama_local")
        mock_ollama_module.ollama_local_generate = AsyncMock(return_value=mock_ollama_failure)
        sys.modules["arifosmcp.intelligence.tools.ollama_local"] = mock_ollama_module

        try:
            from core.organs._1_agi import agi

            result = await agi(query="Test query", session_id="test-session-002")

            assert result["verdict"] == "SABAR"
            assert result["stage"] == "111"
            assert "error" in result
        finally:
            if "arifosmcp.intelligence.tools.ollama_local" in sys.modules:
                del sys.modules["arifosmcp.intelligence.tools.ollama_local"]
            if "core.organs._1_agi" in sys.modules:
                del sys.modules["core.organs._1_agi"]

    @pytest.mark.asyncio
    async def test_agi_eureka_detection(self, mock_ollama_response):
        """Test AGI detects eureka/insight patterns."""
        mock_with_insight = Mock()
        mock_with_insight.ok = True
        mock_with_insight.payload = {
            "response": "This contains a EUREKA moment of insight!",
            "usage": {"completion_tokens": 150},
            "truncated": False,
        }

        mock_ollama_module = ModuleType("arifosmcp.intelligence.tools.ollama_local")
        mock_ollama_module.ollama_local_generate = AsyncMock(return_value=mock_with_insight)
        sys.modules["arifosmcp.intelligence.tools.ollama_local"] = mock_ollama_module

        try:
            from core.organs._1_agi import agi

            result = await agi(query="Find insights", session_id="test-session-005")

            assert result["eureka"]["has_eureka"] is True
        finally:
            if "arifosmcp.intelligence.tools.ollama_local" in sys.modules:
                del sys.modules["arifosmcp.intelligence.tools.ollama_local"]
            if "core.organs._1_agi" in sys.modules:
                del sys.modules["core.organs._1_agi"]

    @pytest.mark.asyncio
    async def test_agi_no_eureka(self, mock_ollama_response):
        """Test AGI correctly identifies no eureka."""
        mock_no_insight = Mock()
        mock_no_insight.ok = True
        mock_no_insight.payload = {
            "response": "Regular analysis without special insights",
            "usage": {"completion_tokens": 80},
            "truncated": False,
        }

        mock_ollama_module = ModuleType("arifosmcp.intelligence.tools.ollama_local")
        mock_ollama_module.ollama_local_generate = AsyncMock(return_value=mock_no_insight)
        sys.modules["arifosmcp.intelligence.tools.ollama_local"] = mock_ollama_module

        try:
            from core.organs._1_agi import agi

            result = await agi(query="Analyze", session_id="test-session-006")

            assert result["eureka"]["has_eureka"] is False
        finally:
            if "arifosmcp.intelligence.tools.ollama_local" in sys.modules:
                del sys.modules["arifosmcp.intelligence.tools.ollama_local"]
            if "core.organs._1_agi" in sys.modules:
                del sys.modules["core.organs._1_agi"]

    def test_agi_aliases(self):
        """Test AGI function aliases work correctly."""
        from core.organs._1_agi import agi, reason, think, sense

        assert agi is reason
        assert agi is think
        assert agi is sense

    def test_build_reasoning_steps_default(self):
        """Test reasoning step builder with default mode."""
        from core.organs._1_agi import _build_reasoning_steps

        steps = _build_reasoning_steps("Test query", "default")
        assert len(steps) == 3
        assert steps[0].phase == "111_search"
        assert steps[1].phase == "222_analyze"
        assert steps[2].phase == "333_synthesis"
        assert steps[1].uncertainty is None  # No uncertainty in default mode

    def test_build_reasoning_steps_strict(self):
        """Test reasoning step builder with strict_truth mode."""
        from core.organs._1_agi import _build_reasoning_steps

        steps = _build_reasoning_steps("Test query", "strict_truth")
        assert len(steps) == 3
        assert steps[1].uncertainty is not None  # Has uncertainty marker


# =============================================================================
# ASI HEART (_2_asi.py) TESTS
# =============================================================================


class TestAsiHeart:
    """Test ASI Heart organ - Safety, Empathy, Ethics."""

    @pytest.mark.asyncio
    async def test_asi_simulate_heart_mode(self):
        """Test ASI simulate_heart action."""
        # Create mock classifier
        mock_scores = Mock()
        mock_scores.f5_peace = 0.9
        mock_scores.f6_empathy = 0.85
        mock_scores.f9_anti_hantu = 0.95
        mock_scores.confidence = 0.92

        mock_sbert_module = ModuleType("core.shared.sbert_floors")
        mock_sbert_module.classify_asi_floors = MagicMock(return_value=mock_scores)
        sys.modules["core.shared.sbert_floors"] = mock_sbert_module

        try:
            from core.organs._2_asi import asi

            result = await asi(
                action="simulate_heart", session_id="test-asi-001", scenario="Safe user request"
            )

            # Result is dict
            assert result["session_id"] == "test-asi-001"
            assert "assessment" in result
            assert result["verdict"] == "SEAL"
        finally:
            if "core.shared.sbert_floors" in sys.modules:
                del sys.modules["core.shared.sbert_floors"]
            if "core.organs._2_asi" in sys.modules:
                del sys.modules["core.organs._2_asi"]

    @pytest.mark.asyncio
    async def test_asi_high_risk_scenario(self):
        """Test ASI detects high-risk scenarios."""
        mock_scores = Mock()
        mock_scores.f5_peace = 0.3  # Low peace
        mock_scores.f6_empathy = 0.4  # Low empathy
        mock_scores.f9_anti_hantu = 0.95
        mock_scores.confidence = 0.8

        mock_sbert_module = ModuleType("core.shared.sbert_floors")
        MagicMock(return_value=mock_scores)
        sys.modules["core.shared.sbert_floors"] = mock_sbert_module

        try:
            from core.organs._2_asi import asi

            result = await asi(
                action="simulate_heart", session_id="test-asi-002", scenario="Dangerous action"
            )

            assert result["verdict"] in ["VOID", "SABAR"]
            assert result["assessment"]["risk_level"] in ["medium", "high"]
        finally:
            if "core.shared.sbert_floors" in sys.modules:
                del sys.modules["core.shared.sbert_floors"]
            if "core.organs._2_asi" in sys.modules:
                del sys.modules["core.organs._2_asi"]

    @pytest.mark.asyncio
    async def test_asi_critique_thought_mode(self):
        """Test ASI critique_thought action."""
        # Mock the empathy classifier
        mock_empathy = Mock()
        mock_empathy.impact_severity = "low"

        mock_sbert_module = ModuleType("core.shared.sbert_floors")
        mock_sbert_module.classify_asi_floors = MagicMock(
            return_value=Mock(f5_peace=0.9, f6_empathy=0.9, f9_anti_hantu=0.9, confidence=0.9)
        )
        sys.modules["core.shared.sbert_floors"] = mock_sbert_module

        try:
            from core.organs._2_asi import asi

            result = await asi(
                action="critique_thought",
                session_id="test-asi-003",
                thought_id="thought-001",
                thought_content="This is a test thought to critique",
            )

            assert result["session_id"] == "test-asi-003"
            assert "critique" in result
        finally:
            if "core.shared.sbert_floors" in sys.modules:
                del sys.modules["core.shared.sbert_floors"]
            if "core.organs._2_asi" in sys.modules:
                del sys.modules["core.organs._2_asi"]

    def test_asi_aliases(self):
        """Test ASI function aliases."""
        from core.organs._2_asi import asi, empathize, align

        assert asi is empathize
        assert asi is align


# =============================================================================
# APEX SOUL (_3_apex.py) TESTS
# =============================================================================


class TestApexSoul:
    """Test APEX Soul organ - Final judgment and constitutional gates."""

    def test_detect_contradictions_no_text(self):
        """Test contradiction detection with no text."""
        from core.organs._3_apex import _detect_contradictions

        result = _detect_contradictions(
            reason_summary="", floor_scores=None, verdict_candidate="SEAL"
        )

        assert result == []  # No contradictions in empty text

    def test_detect_contradictions_critical(self):
        """Test contradiction detection with critical contradiction."""
        from core.organs._3_apex import _detect_contradictions

        text = "This is low risk and safe but also dangerous and high risk"
        result = _detect_contradictions(
            reason_summary=text, floor_scores=None, verdict_candidate="SEAL"
        )

        # Should detect contradiction
        assert len(result) > 0
        assert any(c["severity"] == "critical" for c in result)

    def test_detect_contradictions_irreversible(self):
        """Test detection of irreversible contradiction."""
        from core.organs._3_apex import _detect_contradictions

        text = "This action is reversible and can be undone but also permanent"
        result = _detect_contradictions(
            reason_summary=text, floor_scores=None, verdict_candidate="SEAL"
        )

        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_apex_forge_mode(self):
        """Test APEX forge mode (Eureka proposal)."""
        from core.organs._3_apex import apex

        result = await apex(
            action="forge", session_id="test-apex-001", proposal="Create new feature"
        )

        assert result["session_id"] == "test-apex-001"
        assert "eureka" in result

    @pytest.mark.asyncio
    async def test_apex_judge_mode(self):
        """Test APEX judge mode (final verdict)."""
        from core.organs._3_apex import apex

        result = await apex(
            action="judge", session_id="test-apex-002", proposal="Well-structured proposal"
        )

        assert result["session_id"] == "test-apex-002"
        assert "final_verdict" in result

    def test_apex_functions_exist(self):
        """Test APEX functions are importable."""
        from core.organs._3_apex import apex, judge, forge, sync

        # Just verify they exist and are callable
        assert callable(apex)
        assert callable(judge)
        assert callable(forge)
        assert callable(sync)


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestTrinityEdgeCases:
    """Edge cases and error handling for Trinity organs."""

    @pytest.mark.asyncio
    async def test_agi_empty_query(self):
        """Test AGI handles empty query."""
        mock_ollama = Mock()
        mock_ollama.ok = True
        mock_ollama.payload = {
            "response": "Empty query analysis",
            "usage": {"completion_tokens": 10},
            "truncated": False,
        }

        mock_ollama_module = ModuleType("arifosmcp.intelligence.tools.ollama_local")
        mock_ollama_module.ollama_local_generate = AsyncMock(return_value=mock_ollama)
        sys.modules["arifosmcp.intelligence.tools.ollama_local"] = mock_ollama_module

        try:
            from core.organs._1_agi import agi

            result = await agi(query="", session_id="edge-empty")
            assert result["session_id"] == "edge-empty"
        finally:
            if "arifosmcp.intelligence.tools.ollama_local" in sys.modules:
                del sys.modules["arifosmcp.intelligence.tools.ollama_local"]
            if "core.organs._1_agi" in sys.modules:
                del sys.modules["core.organs._1_agi"]

    @pytest.mark.asyncio
    async def test_agi_unicode_query(self):
        """Test AGI handles unicode characters."""
        mock_ollama = Mock()
        mock_ollama.ok = True
        mock_ollama.payload = {
            "response": "Unicode analysis: 你好 🌍 ñ",
            "usage": {"completion_tokens": 20},
            "truncated": False,
        }

        mock_ollama_module = ModuleType("arifosmcp.intelligence.tools.ollama_local")
        mock_ollama_module.ollama_local_generate = AsyncMock(return_value=mock_ollama)
        sys.modules["arifosmcp.intelligence.tools.ollama_local"] = mock_ollama_module

        try:
            from core.organs._1_agi import agi

            result = await agi(query="Test with unicode: 你好 🌍 ñ", session_id="unicode-test")

            assert result["session_id"] == "unicode-test"
            assert result["stage"] == "333"
        finally:
            if "arifosmcp.intelligence.tools.ollama_local" in sys.modules:
                del sys.modules["arifosmcp.intelligence.tools.ollama_local"]
            if "core.organs._1_agi" in sys.modules:
                del sys.modules["core.organs._1_agi"]

    @pytest.mark.asyncio
    async def test_asi_no_scenario(self):
        """Test ASI handles missing scenario."""
        mock_scores = Mock()
        mock_scores.f5_peace = 0.9
        mock_scores.f6_empathy = 0.9
        mock_scores.f9_anti_hantu = 0.95
        mock_scores.confidence = 0.9

        mock_sbert_module = ModuleType("core.shared.sbert_floors")
        MagicMock(return_value=mock_scores)
        sys.modules["core.shared.sbert_floors"] = mock_sbert_module

        try:
            from core.organs._2_asi import asi

            result = await asi(action="simulate_heart", session_id="test-no-scenario")

            assert result["session_id"] == "test-no-scenario"
        finally:
            if "core.shared.sbert_floors" in sys.modules:
                del sys.modules["core.shared.sbert_floors"]
            if "core.organs._2_asi" in sys.modules:
                del sys.modules["core.organs._2_asi"]

    @pytest.mark.asyncio
    async def test_apex_contradiction_detection(self):
        """Test APEX detects contradictions in proposals."""
        from core.organs._3_apex import apex

        # Proposal with internal contradiction
        result = await apex(
            action="judge",
            session_id="test-contradiction",
            proposal="This is completely safe but also very dangerous",
            verdict_candidate="SEAL",
        )

        assert result["session_id"] == "test-contradiction"
        # Should detect contradictions
        assert "reasoning" in result or "contradictions" in result

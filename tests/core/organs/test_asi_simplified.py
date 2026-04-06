"""
tests/core/organs/test_asi_simplified.py — Simplified ASI Tests

Direct tests for _2_asi.py that work without complex mocking
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from types import ModuleType


class TestAsiBasic:
    """Basic ASI tests that work with actual API."""

    @pytest.mark.asyncio
    async def test_asi_full_mode_mocked(self):
        """Test ASI full mode with proper mocking."""
        # Mock the sbert module before importing ASI
        mock_scores = Mock()
        mock_scores.f5_peace = 0.95
        mock_scores.f6_empathy = 0.90
        mock_scores.f9_anti_hantu = 0.95
        mock_scores.confidence = 0.92

        mock_sbert = ModuleType("core.shared.sbert_floors")
        mock_sbert.classify_asi_floors = MagicMock(return_value=mock_scores)
        sys.modules["core.shared.sbert_floors"] = mock_sbert

        try:
            from core.organs._2_asi import asi

            result = await asi(
                action="full",
                session_id="test-asi-full",
                scenario="Test scenario",
                thought_id="thought-001",
                thought_content="Test thought content",
            )

            assert result["session_id"] == "test-asi-full"
            assert hasattr(result, "assessment")
            assert hasattr(result, "critique")

        finally:
            # Cleanup
            for mod in ["core.shared.sbert_floors", "core.organs._2_asi"]:
                if mod in sys.modules:
                    del sys.modules[mod]

    @pytest.mark.asyncio
    async def test_asi_simulate_heart_only(self):
        """Test ASI simulate_heart action only."""
        mock_scores = Mock()
        mock_scores.f5_peace = 0.85
        mock_scores.f6_empathy = 0.88
        mock_scores.f9_anti_hantu = 0.90
        mock_scores.confidence = 0.85

        mock_sbert = ModuleType("core.shared.sbert_floors")
        mock_sbert.classify_asi_floors = MagicMock(return_value=mock_scores)
        sys.modules["core.shared.sbert_floors"] = mock_sbert

        try:
            from core.organs._2_asi import asi

            result = await asi(
                action="simulate_heart",
                session_id="test-asi-heart",
                scenario="User wants help with coding",
            )

            assert result["session_id"] == "test-asi-heart"
            assert hasattr(result, "assessment")

        finally:
            for mod in ["core.shared.sbert_floors", "core.organs._2_asi"]:
                if mod in sys.modules:
                    del sys.modules[mod]

    @pytest.mark.asyncio
    async def test_asi_critique_only(self):
        """Test ASI critique_thought action only."""
        mock_sbert = ModuleType("core.shared.sbert_floors")
        mock_sbert.classify_asi_floors = MagicMock(
            return_value=Mock(f5_peace=0.9, f6_empathy=0.9, f9_anti_hantu=0.9, confidence=0.9)
        )
        sys.modules["core.shared.sbert_floors"] = mock_sbert

        try:
            from core.organs._2_asi import asi

            result = await asi(
                action="critique_thought",
                session_id="test-asi-critique",
                thought_id="critique-001",
                thought_content="This thought might have issues",
            )

            assert result["session_id"] == "test-asi-critique"
            assert hasattr(result, "critique")

        finally:
            for mod in ["core.shared.sbert_floors", "core.organs._2_asi"]:
                if mod in sys.modules:
                    del sys.modules[mod]

    @pytest.mark.asyncio
    async def test_asi_no_scenario(self):
        """Test ASI with no scenario (defaults to INIT)."""
        mock_scores = Mock()
        mock_scores.f5_peace = 0.95
        mock_scores.f6_empathy = 0.95
        mock_scores.f9_anti_hantu = 0.95
        mock_scores.confidence = 0.95

        mock_sbert = ModuleType("core.shared.sbert_floors")
        mock_sbert.classify_asi_floors = MagicMock(return_value=mock_scores)
        sys.modules["core.shared.sbert_floors"] = mock_sbert

        try:
            from core.organs._2_asi import asi

            result = await asi(action="simulate_heart", session_id="test-asi-default")

            assert result["session_id"] == "test-asi-default"

        finally:
            for mod in ["core.shared.sbert_floors", "core.organs._2_asi"]:
                if mod in sys.modules:
                    del sys.modules[mod]

    @pytest.mark.asyncio
    async def test_asi_low_empathy(self):
        """Test ASI with low empathy scores (should trigger warnings)."""
        mock_scores = Mock()
        mock_scores.f5_peace = 0.4  # Low
        mock_scores.f6_empathy = 0.3  # Low
        mock_scores.f9_anti_hantu = 0.95
        mock_scores.confidence = 0.8

        mock_sbert = ModuleType("core.shared.sbert_floors")
        mock_sbert.classify_asi_floors = MagicMock(return_value=mock_scores)
        sys.modules["core.shared.sbert_floors"] = mock_sbert

        try:
            from core.organs._2_asi import asi

            result = await asi(
                action="simulate_heart", session_id="test-asi-risk", scenario="Something concerning"
            )

            assert result["session_id"] == "test-asi-risk"
            # Should have risk detection
            assert result.assessment.risk_level in ["medium", "high"]

        finally:
            for mod in ["core.shared.sbert_floors", "core.organs._2_asi"]:
                if mod in sys.modules:
                    del sys.modules[mod]

    def test_asi_aliases(self):
        """Test ASI function aliases."""
        from core.organs._2_asi import asi, empathize, align

        assert asi is empathize
        assert asi is align


class TestAsiEdgeCases:
    """Edge cases for ASI."""

    @pytest.mark.asyncio
    async def test_asi_unicode_content(self):
        """Test ASI with unicode content."""
        mock_sbert = ModuleType("core.shared.sbert_floors")
        mock_sbert.classify_asi_floors = MagicMock(
            return_value=Mock(f5_peace=0.9, f6_empathy=0.9, f9_anti_hantu=0.9, confidence=0.9)
        )
        sys.modules["core.shared.sbert_floors"] = mock_sbert

        try:
            from core.organs._2_asi import asi

            result = await asi(
                action="simulate_heart",
                session_id="test-asi-unicode",
                scenario="Unicode test: 你好 🌍 ñ",
            )

            assert result["session_id"] == "test-asi-unicode"

        finally:
            for mod in ["core.shared.sbert_floors", "core.organs._2_asi"]:
                if mod in sys.modules:
                    del sys.modules[mod]

    @pytest.mark.asyncio
    async def test_asi_long_content(self):
        """Test ASI with very long content."""
        mock_sbert = ModuleType("core.shared.sbert_floors")
        mock_sbert.classify_asi_floors = MagicMock(
            return_value=Mock(f5_peace=0.9, f6_empathy=0.9, f9_anti_hantu=0.9, confidence=0.9)
        )
        sys.modules["core.shared.sbert_floors"] = mock_sbert

        try:
            from core.organs._2_asi import asi

            long_text = "Test " * 1000

            result = await asi(
                action="critique_thought",
                session_id="test-asi-long",
                thought_id="long-001",
                thought_content=long_text,
            )

            assert result["session_id"] == "test-asi-long"

        finally:
            for mod in ["core.shared.sbert_floors", "core.organs._2_asi"]:
                if mod in sys.modules:
                    del sys.modules[mod]

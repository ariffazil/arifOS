"""
tests/test_health_mode_integration.py — Health Mode Integration Tests

Tests for the new health mode in apex_judge/arifos_judge.
Phase 1 implementation verification before Phase 2 (history mode).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, AsyncMock

from arifosmcp.runtime.models import (
    RuntimeEnvelope,
    RuntimeStatus,
    Verdict,
)


# =============================================================================
# Health Mode Tests
# =============================================================================

@pytest.mark.asyncio
class TestHealthMode:
    """Test health mode returns constitutional health telemetry."""

    async def test_health_mode_basic(self):
        """health mode should return health payload without issuing verdict."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        result = await apex_judge_dispatch_impl(
            mode="health",
            payload={"session_id": "test-session-001"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=None,
        )
        
        assert result.ok is True
        assert result.tool == "apex_judge"
        assert result.canonical_tool_name == "arifos_judge"
        assert result.stage == "888_JUDGE"
        assert result.verdict == Verdict.SEAL
        assert result.status == RuntimeStatus.SUCCESS

    async def test_health_mode_payload_structure(self):
        """health payload should have expected structure."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        result = await apex_judge_dispatch_impl(
            mode="health",
            payload={"session_id": "test-session-002"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=None,
        )
        
        payload = result.payload
        
        # Required fields
        assert "mode" in payload
        assert payload["mode"] == "health"
        assert "floors_active" in payload
        assert "telemetry_snapshot" in payload
        assert "verdicts_summary" in payload
        assert "system_status" in payload
        assert "judge_readiness" in payload
        assert "session_id" in payload
        assert "timestamp_utc" in payload

    async def test_health_mode_floors_active(self):
        """floors_active should list constitutional floors."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        result = await apex_judge_dispatch_impl(
            mode="health",
            payload={"session_id": "test-session-003"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=None,
        )
        
        floors = result.payload["floors_active"]
        assert isinstance(floors, list)
        assert len(floors) >= 7
        # Should include judge-relevant floors
        assert "F1" in floors
        assert "F2" in floors
        assert "F3" in floors
        assert "F9" in floors
        assert "F10" in floors
        assert "F12" in floors
        assert "F13" in floors

    async def test_health_mode_telemetry_snapshot(self):
        """telemetry_snapshot should have constitutional metrics."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        result = await apex_judge_dispatch_impl(
            mode="health",
            payload={"session_id": "test-session-004"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=None,
        )
        
        telemetry = result.payload["telemetry_snapshot"]
        
        # Required telemetry fields
        assert "ds" in telemetry  # Entropy delta (F4)
        assert "peace2" in telemetry  # Stability (F5)
        assert "G_star" in telemetry  # Genius score (F8)
        assert "confidence" in telemetry  # Humility band (F7)
        assert "shadow" in telemetry  # Anti-hantu (F9)
        
        # Values should be numeric
        assert isinstance(telemetry["ds"], (int, float))
        assert isinstance(telemetry["peace2"], (int, float))
        assert isinstance(telemetry["G_star"], (int, float))

    async def test_health_mode_system_status(self):
        """system_status should indicate readiness."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        result = await apex_judge_dispatch_impl(
            mode="health",
            payload={"session_id": "test-session-005"},
            auth_context=None,
            risk_tier="medium",
            dry_run=True,
            ctx=None,
        )
        
        assert result.payload["system_status"] == "HEALTHY"
        assert result.payload["judge_readiness"] == "READY"

    async def test_health_mode_no_side_effects(self):
        """health mode should not modify vault or issue real verdicts."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        with patch("arifosmcp.runtime.tools_internal._wrap_call") as mock_wrap:
            # health mode should NOT call _wrap_call
            result = await apex_judge_dispatch_impl(
                mode="health",
                payload={"session_id": "test-session-006"},
                auth_context=None,
                risk_tier="medium",
                dry_run=True,
                ctx=None,
            )
            
            # _wrap_call should not be called for health mode
            mock_wrap.assert_not_called()


# =============================================================================
# Regression Tests (Ensure existing modes still work)
# =============================================================================

@pytest.mark.asyncio
class TestExistingModesRegression:
    """Ensure health mode addition doesn't break existing modes."""

    async def test_judge_mode_still_works(self):
        """judge mode should still function normally."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        with patch("arifosmcp.runtime.tools_internal._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result
            
            result = await apex_judge_dispatch_impl(
                mode="judge",
                payload={"candidate": "test action", "session_id": "test"},
                auth_context=None,
                risk_tier="medium",
                dry_run=True,
                ctx=None,
            )
            
            assert result is not None
            mock_wrap.assert_called_once()

    async def test_rules_mode_still_works(self):
        """rules mode should still function normally."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        with patch("arifosmcp.runtime.tools_internal._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result
            
            result = await apex_judge_dispatch_impl(
                mode="rules",
                payload={"session_id": "test"},
                auth_context=None,
                risk_tier="medium",
                dry_run=True,
                ctx=None,
            )
            
            assert result is not None
            mock_wrap.assert_called_once()

    async def test_probe_mode_still_works(self):
        """probe mode should still function normally."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        with patch("arifosmcp.runtime.tools_internal._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result
            
            result = await apex_judge_dispatch_impl(
                mode="probe",
                payload={"target_floor": "F12_DEFENSE", "session_id": "test"},
                auth_context=None,
                risk_tier="medium",
                dry_run=True,
                ctx=None,
            )
            
            assert result is not None
            mock_wrap.assert_called_once()

    async def test_invalid_mode_raises_error(self):
        """Invalid mode should still raise ValueError."""
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        with pytest.raises(ValueError, match="Invalid mode for apex_judge"):
            await apex_judge_dispatch_impl(
                mode="nonexistent_mode",
                payload={"session_id": "test"},
                auth_context=None,
                risk_tier="medium",
                dry_run=True,
                ctx=None,
            )


# =============================================================================
# Mode Count Verification
# =============================================================================

class TestModeCount:
    """Verify the number of implemented modes."""

    def test_health_mode_added_to_dispatch(self):
        """health mode should be in the dispatch implementation."""
        import inspect
        from arifosmcp.runtime.tools_internal import apex_judge_dispatch_impl
        
        source = inspect.getsource(apex_judge_dispatch_impl)
        
        # Should have 8 mode branches: judge, rules, validate, hold, armor, notify, probe, health
        modes = ["judge", "rules", "validate", "hold", "armor", "notify", "probe", "health"]
        for mode in modes:
            assert f'mode == "{mode}"' in source or f'"{mode}"' in source, f"Mode {mode} not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

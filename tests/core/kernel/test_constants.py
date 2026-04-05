"""Tests for core.kernel.constants — Constitutional Thresholds."""

import pytest

from core.kernel.constants import (
    ConstitutionalThresholds,
    PerformanceLimits,
    SessionConfig,
    ToolDefaults,
)


class TestConstitutionalThresholds:
    """F1-F13 constitutional floor thresholds."""

    def test_omega_critical_threshold(self):
        """F7: Environmental uncertainty ceiling."""
        assert ConstitutionalThresholds.OMEGA_CRITICAL == 0.08

    def test_omega_display_bounds(self):
        """F7: Gödel Lock [0.03, 0.05]."""
        assert ConstitutionalThresholds.OMEGA_DISPLAY_MIN == 0.03
        assert ConstitutionalThresholds.OMEGA_DISPLAY_MAX == 0.05

    def test_truth_score_minimum(self):
        """F2: Truth minimum threshold."""
        assert ConstitutionalThresholds.TRUTH_SCORE_MINIMUM == 0.5

    def test_empathy_kappa_r(self):
        """F6: Empathy hard floor (κᵣ ≥ 0.95)."""
        assert ConstitutionalThresholds.EMPATHY_KAPPA_R == 0.95

    def test_empathy_threshold(self):
        """F6: Empathy operational threshold."""
        assert ConstitutionalThresholds.EMPATHY_THRESHOLD == 0.7

    def test_peace_squared_min(self):
        """F6: Peace² minimum (Peace ≥ 1.0)."""
        assert ConstitutionalThresholds.PEACE_SQUARED_MIN == 1.0

    def test_injection_risk_thresholds(self):
        """F12: Injection risk bands."""
        assert ConstitutionalThresholds.INJECTION_RISK_HIGH == 0.9
        assert ConstitutionalThresholds.INJECTION_RISK_BLOCK == 0.85

    def test_tri_witness_score(self):
        """F3: Tri-witness consensus threshold."""
        assert ConstitutionalThresholds.TRI_WITNESS_SCORE == 0.98

    def test_apex_confidence(self):
        """APEX confidence threshold."""
        assert ConstitutionalThresholds.APEX_CONFIDENCE == 0.98

    def test_irreversibility_hold(self):
        """F1: Irreversibility threshold for 888_HOLD."""
        assert ConstitutionalThresholds.IRREVERSIBILITY_HOLD == 0.8


class TestToolDefaults:
    """Default values for tool outputs."""

    def test_truth_score_placeholder(self):
        assert ToolDefaults.TRUTH_SCORE_PLACEHOLDER == 0.85

    def test_clarity_delta_default(self):
        """F4: Default entropy reduction."""
        assert ToolDefaults.CLARITY_DELTA == -0.2

    def test_hypotheses_default(self):
        assert ToolDefaults.HYPOTHESES_DEFAULT == 3

    def test_safe_default(self):
        assert ToolDefaults.SAFE_DEFAULT is True

    def test_anti_hantu_default(self):
        """F9: Anti-shadow default."""
        assert ToolDefaults.ANTI_HANTU is True

    def test_artifact_ready_default(self):
        assert ToolDefaults.ARTIFACT_READY is True


class TestSessionConfig:
    """Session configuration defaults."""

    def test_mode_default(self):
        assert SessionConfig.MODE_DEFAULT == "conscience"

    def test_actor_id_default(self):
        assert SessionConfig.ACTOR_ID_DEFAULT == "user"


class TestPerformanceLimits:
    """Performance and resource limits."""

    def test_max_hypotheses(self):
        assert PerformanceLimits.MAX_HYPOTHESES == 10

    def test_max_evidence_items(self):
        assert PerformanceLimits.MAX_EVIDENCE_ITEMS == 100

    def test_max_stakeholders(self):
        assert PerformanceLimits.MAX_STAKEHOLDERS == 50

    def test_max_tokens_default(self):
        assert PerformanceLimits.MAX_TOKENS_DEFAULT == 8192


class TestConstantsExports:
    """Module exports verification."""

    def test_all_exports_present(self):
        from core.kernel import constants

        assert hasattr(constants, "__all__")
        assert "ConstitutionalThresholds" in constants.__all__
        assert "ToolDefaults" in constants.__all__
        assert "SessionConfig" in constants.__all__
        assert "PerformanceLimits" in constants.__all__

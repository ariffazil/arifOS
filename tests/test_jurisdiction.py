"""
Tests for Jurisdiction Layer — Autonomy Bands & Capability Grants
═══════════════════════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import pytest

from arifosmcp.core.jurisdiction import AutonomyBandRouter, CapabilityGrantRegistry
from arifosmcp.schemas.jurisdiction import (
    AutonomyBand,
    CapabilityGrant,
    JurisdictionEnvelope,
    RiskClass,
)


@pytest.fixture
def router() -> AutonomyBandRouter:
    return AutonomyBandRouter()


@pytest.fixture
def registry() -> CapabilityGrantRegistry:
    return CapabilityGrantRegistry()


# ═══════════════════════════════════════════════════════════════════════════════
# AUTONOMY BAND ROUTER — Tool Name Classification
# ═══════════════════════════════════════════════════════════════════════════════


class TestBandClassification:
    def test_green_read_tools(self, router: AutonomyBandRouter) -> None:
        for tool in ("arif_sense_observe", "inspect_code", "list_files", "health_probe"):
            env = JurisdictionEnvelope(actor_id="a", tool_name=tool)
            result = router.classify(env)
            assert result.assigned_band == AutonomyBand.GREEN
            assert result.fast_lane is True
            assert result.risk_class == RiskClass.OBSERVE

    def test_yellow_prepare_tools(self, router: AutonomyBandRouter) -> None:
        for tool in ("plan_deployment", "diff_configs", "validate_schema"):
            env = JurisdictionEnvelope(actor_id="a", tool_name=tool)
            result = router.classify(env)
            assert result.assigned_band == AutonomyBand.YELLOW
            assert result.fast_lane is True
            assert result.risk_class == RiskClass.PREPARE

    def test_orange_write_tools(self, router: AutonomyBandRouter) -> None:
        for tool in ("write_file", "update_config", "create_branch", "build_project"):
            env = JurisdictionEnvelope(actor_id="a", tool_name=tool)
            result = router.classify(env)
            assert result.assigned_band == AutonomyBand.ORANGE
            assert result.fast_lane is False
            assert result.requires_rollback is True
            assert result.requires_observe_receipt is True

    def test_red_delete_tools(self, router: AutonomyBandRouter) -> None:
        for tool in ("delete_volume", "drop_table", "remove_service", "commit_push"):
            env = JurisdictionEnvelope(actor_id="a", tool_name=tool)
            result = router.classify(env)
            assert result.assigned_band == AutonomyBand.RED
            assert result.risk_class == RiskClass.ATOMIC

    def test_black_irreversible_tools(self, router: AutonomyBandRouter) -> None:
        env = JurisdictionEnvelope(actor_id="a", tool_name="irreversible_wipe_disk")
        result = router.classify(env)
        assert result.assigned_band == AutonomyBand.BLACK
        assert result.risk_class == RiskClass.IRREVERSIBLE

    def test_unknown_tool_defaults_yellow(self, router: AutonomyBandRouter) -> None:
        env = JurisdictionEnvelope(actor_id="a", tool_name="unknown_mystery_tool")
        result = router.classify(env)
        assert result.assigned_band == AutonomyBand.YELLOW


# ═══════════════════════════════════════════════════════════════════════════════
# PARAMETER ESCALATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestParameterEscalation:
    def test_delete_keyword_escalates(self, router: AutonomyBandRouter) -> None:
        env = JurisdictionEnvelope(
            actor_id="a",
            tool_name="write_file",
            params={"action": "delete old files permanently"},
        )
        result = router.classify(env)
        assert result.assigned_band == AutonomyBand.RED

    def test_secret_keyword_escalates(self, router: AutonomyBandRouter) -> None:
        env = JurisdictionEnvelope(
            actor_id="a",
            tool_name="write_file",
            params={"content": "api_key = sk-12345"},
        )
        result = router.classify(env)
        assert result.assigned_band == AutonomyBand.RED

    def test_claim_override_upward(self, router: AutonomyBandRouter) -> None:
        # Actor claims GREEN but tool is RED
        env = JurisdictionEnvelope(
            actor_id="a",
            tool_name="delete_volume",
            claimed_band=AutonomyBand.GREEN,
        )
        result = router.classify(env)
        assert result.assigned_band == AutonomyBand.RED
        assert "overridden" in result.reason.lower()

    def test_claim_higher_risk_accepted(self, router: AutonomyBandRouter) -> None:
        # Actor claims RED but heuristic says ORANGE — accept RED
        env = JurisdictionEnvelope(
            actor_id="a",
            tool_name="write_file",
            claimed_band=AutonomyBand.RED,
        )
        result = router.classify(env)
        assert result.assigned_band == AutonomyBand.RED


# ═══════════════════════════════════════════════════════════════════════════════
# CAPABILITY GRANT REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════


class TestCapabilityGrantRegistry:
    def test_issue_and_authorize(self, registry: CapabilityGrantRegistry) -> None:
        grant = CapabilityGrant(
            grant_id="g-1",
            actor_id="hermes",
            tool_name="arif_sense_observe",
            band=AutonomyBand.GREEN,
        )
        registry.issue(grant)
        ok, g, reason = registry.authorize("hermes", "arif_sense_observe", AutonomyBand.GREEN)
        assert ok is True
        assert g is not None
        assert g.grant_id == "g-1"

    def test_deny_no_grant(self, registry: CapabilityGrantRegistry) -> None:
        ok, g, reason = registry.authorize("hermes", "secret_tool", AutonomyBand.GREEN)
        assert ok is False
        assert g is None
        assert "No active grant" in reason

    def test_deny_band_too_low(self, registry: CapabilityGrantRegistry) -> None:
        grant = CapabilityGrant(
            grant_id="g-1",
            actor_id="hermes",
            tool_name="write_file",
            band=AutonomyBand.YELLOW,
        )
        registry.issue(grant)
        ok, g, reason = registry.authorize("hermes", "write_file", AutonomyBand.RED)
        assert ok is False
        assert g is not None
        assert "yellow < required red" in reason

    def test_revoke(self, registry: CapabilityGrantRegistry) -> None:
        grant = CapabilityGrant(
            grant_id="g-1",
            actor_id="hermes",
            tool_name="arif_sense_observe",
            band=AutonomyBand.GREEN,
        )
        registry.issue(grant)
        assert registry.revoke("g-1", "compromised") is True
        ok, g, reason = registry.authorize("hermes", "arif_sense_observe", AutonomyBand.GREEN)
        assert ok is False
        assert "No active grant" in reason

    def test_revoke_unknown(self, registry: CapabilityGrantRegistry) -> None:
        assert registry.revoke("g-99", "test") is False

    def test_expired_grant_denied(self, registry: CapabilityGrantRegistry) -> None:
        from datetime import UTC, datetime, timedelta

        grant = CapabilityGrant(
            grant_id="g-1",
            actor_id="hermes",
            tool_name="arif_sense_observe",
            band=AutonomyBand.GREEN,
            expires_at=(datetime.now(UTC) - timedelta(days=1)).isoformat(),
        )
        registry.issue(grant)
        ok, g, reason = registry.authorize("hermes", "arif_sense_observe", AutonomyBand.GREEN)
        assert ok is False
        assert "No active grant" in reason

    def test_stats(self, registry: CapabilityGrantRegistry) -> None:
        registry.issue(
            CapabilityGrant(grant_id="g-1", actor_id="a", tool_name="t1", band=AutonomyBand.GREEN)
        )
        registry.issue(
            CapabilityGrant(grant_id="g-2", actor_id="a", tool_name="t2", band=AutonomyBand.YELLOW)
        )
        registry.revoke("g-1", "test")
        stats = registry.dump_stats()
        assert stats["total_grants"] == 2
        assert stats["active_grants"] == 1
        assert stats["revoked_grants"] == 1

    def test_list_actor_grants(self, registry: CapabilityGrantRegistry) -> None:
        registry.issue(
            CapabilityGrant(grant_id="g-1", actor_id="a", tool_name="t1", band=AutonomyBand.GREEN)
        )
        registry.issue(
            CapabilityGrant(grant_id="g-2", actor_id="a", tool_name="t2", band=AutonomyBand.YELLOW)
        )
        assert len(registry.list_actor_grants("a")) == 2
        assert len(registry.list_actor_grants("b")) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION: Router + Registry
# ═══════════════════════════════════════════════════════════════════════════════


class TestRouterRegistryIntegration:
    def test_full_green_flow(
        self, router: AutonomyBandRouter, registry: CapabilityGrantRegistry
    ) -> None:
        env = JurisdictionEnvelope(actor_id="hermes", tool_name="list_files")
        result = router.classify(env)
        assert result.assigned_band == AutonomyBand.GREEN

        registry.issue(
            CapabilityGrant(
                grant_id="g-1",
                actor_id="hermes",
                tool_name="list_files",
                band=AutonomyBand.GREEN,
            )
        )
        ok, grant, reason = registry.authorize("hermes", "list_files", result.assigned_band)
        assert ok is True

    def test_orange_needs_grant(
        self, router: AutonomyBandRouter, registry: CapabilityGrantRegistry
    ) -> None:
        env = JurisdictionEnvelope(actor_id="hermes", tool_name="write_file")
        result = router.classify(env)
        assert result.assigned_band == AutonomyBand.ORANGE
        assert result.requires_grant is True

        # No grant issued → should deny
        ok, grant, reason = registry.authorize("hermes", "write_file", result.assigned_band)
        assert ok is False

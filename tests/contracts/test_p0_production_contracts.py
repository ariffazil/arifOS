"""
Test Suite: P0 Production Contracts — arifOS Federation
════════════════════════════════════════════════════════

Covers the 4 critical contract gaps identified in the 2026-06-09 readiness audit:
  P0.2 — FederationEnvelope v2 validation
  P0.3 — Endpoint manifest + drift detection
  P0.4 — Vault liveness contract
  P0.5 — Budget enforcement schema

DITEMPA BUKAN DIBERI — Contracts that fail their tests are not contracts.
"""

import pytest
import yaml

from arifosmcp.schemas.federation_envelope import (
    AuthoritySource,
    FederationEnvelope,
    FederationOrgan,
)
from contracts.budget_enforcement import (
    CANONICAL_SESSION_BUDGET,
    BudgetDomain,
    BudgetLimit,
    BudgetState,
    check_budget,
)
from arifosmcp.core.enforcement.drift_detector import (
    DriftReport,
    DriftVerdict,
    check_drift,
    load_manifest,
)


# ═══════════════════════════════════════════════════════════════════════════════
# P0.2 — FederationEnvelope v2
# ═══════════════════════════════════════════════════════════════════════════════


class TestFederationEnvelope:
    """The envelope must validate and reject invalid inputs."""

    def test_minimal_envelope_validates(self):
        """A minimal valid envelope should pass Pydantic validation."""
        env = FederationEnvelope(
            organ=FederationOrgan.ARIFOS,
            actor_id="test-actor",
            session_id="test-session",
            trace_id="test-trace-001",
        )
        assert env.organ == FederationOrgan.ARIFOS
        assert env.actor_id == "test-actor"
        assert env.envelope_version == "2.0"

    def test_envelope_rejects_unknown_organ(self):
        """An unknown organ should fail validation."""
        with pytest.raises(ValueError):
            FederationEnvelope(
                organ="UNKNOWN_ORGAN",  # type: ignore[arg-type]
                actor_id="test",
                session_id="test",
                trace_id="test",
            )

    def test_envelope_includes_trace_id(self):
        """Every envelope should carry a trace_id for audit."""
        env = FederationEnvelope(
            organ=FederationOrgan.WEALTH,
            actor_id="agent-1",
            session_id="sess-1",
            trace_id="trace-wealth-001",
        )
        assert env.trace_id == "trace-wealth-001"

    def test_all_canonical_organs_present(self):
        """All 8 federation organs must be defined."""
        expected = {"arifOS", "WEALTH", "WELL", "GEOX", "HERMES", "AAA", "A-FORGE", "APEX"}
        actual = {o.value for o in FederationOrgan}
        assert actual == expected


# ═══════════════════════════════════════════════════════════════════════════════
# P0.3 — Endpoint Manifest + Drift Detection
# ═══════════════════════════════════════════════════════════════════════════════


class TestEndpointManifest:
    """The manifest must be loadable and contain correct values."""

    def test_manifest_loads(self):
        """mcp_surface.yaml must be valid YAML."""
        manifest = load_manifest("contracts/mcp_surface.yaml")
        assert manifest["schema_version"] == 2
        assert manifest["kind"] == "arifos.mcp_surface"

    def test_manifest_has_19_canonical_tools(self):
        """The manifest must declare exactly 19 canonical tools."""
        manifest = load_manifest("contracts/mcp_surface.yaml")
        tools = manifest["canonical_tools"]
        assert len(tools) == 19, f"Expected 19 tools, got {len(tools)}: {tools}"
        assert "arif_session_init" in tools
        assert "arif_vault_seal" in tools
        assert "arif_forge_execute" in tools

    def test_manifest_has_correct_port(self):
        """The manifest must declare port 8088 (not stale 8080)."""
        manifest = load_manifest("contracts/mcp_surface.yaml")
        port = manifest["runtime_surface"]["primary_port"]
        assert port == 8088, f"Expected 8088, got {port}"

    def test_manifest_has_drift_detection_enabled(self):
        """Drift detection must be enabled."""
        manifest = load_manifest("contracts/mcp_surface.yaml")
        assert manifest["drift_detection"]["enabled"] is True


class TestDriftDetection:
    """Drift between manifest and runtime must be detected."""

    def test_clean_when_tools_match(self):
        """When manifest and runtime match, verdict is CLEAN."""
        manifest = {
            "canonical_tools": ["tool_a", "tool_b", "tool_c"],
            "runtime_surface": {"primary_port": 8088},
        }
        runtime = ["tool_a", "tool_b", "tool_c"]
        report = check_drift(manifest, runtime, runtime_port=8088)
        assert report.verdict == DriftVerdict.CLEAN
        assert not report.has_drift

    def test_hold_when_tool_missing(self):
        """When a canonical tool is missing from runtime, verdict is HOLD."""
        manifest = {"canonical_tools": ["tool_a", "tool_b", "tool_c"]}
        runtime = ["tool_a", "tool_b"]  # tool_c missing
        report = check_drift(manifest, runtime, runtime_port=8088)
        assert report.verdict == DriftVerdict.HOLD
        assert "tool_c" in report.missing_tools

    def test_warning_when_extra_tool_in_runtime(self):
        """When runtime has extra tools, verdict is WARNING."""
        manifest = {"canonical_tools": ["tool_a", "tool_b"]}
        runtime = ["tool_a", "tool_b", "tool_c", "tool_d"]
        report = check_drift(manifest, runtime, runtime_port=8088)
        assert report.verdict == DriftVerdict.WARNING
        assert len(report.extra_tools) == 2

    def test_drift_summary_readable(self):
        """Drift reports must have human-readable summaries."""
        manifest = {"canonical_tools": ["tool_a"]}
        runtime: list[str] = []
        report = check_drift(manifest, runtime, runtime_port=8088)
        assert "missing tools" in report.summary.lower()

    def test_port_mismatch_warning(self):
        """Port mismatch between manifest and runtime triggers WARNING."""
        manifest = {
            "canonical_tools": ["tool_a"],
            "runtime_surface": {"primary_port": 8088},
        }
        runtime = ["tool_a"]
        report = check_drift(manifest, runtime, runtime_port=9999)
        assert report.port_mismatch
        assert report.verdict == DriftVerdict.WARNING


# ═══════════════════════════════════════════════════════════════════════════════
# P0.4 — Vault Liveness Contract
# ═══════════════════════════════════════════════════════════════════════════════


class TestVaultLivenessContract:
    """The vault liveness contract must be valid and enforceable."""

    def test_contract_loads(self):
        """vault_liveness.yaml must be valid YAML."""
        with open("contracts/vault_liveness.yaml") as f:
            contract = yaml.safe_load(f)
        assert contract["schema_version"] == 2
        assert contract["kind"] == "arifos.vault_liveness"

    def test_freshness_bands_defined(self):
        """All 4 freshness bands must be defined."""
        with open("contracts/vault_liveness.yaml") as f:
            contract = yaml.safe_load(f)
        bands = contract["freshness_bands"]
        assert "fresh" in bands
        assert "warming" in bands
        assert "stale" in bands
        assert "expired" in bands

    def test_chain_requirements(self):
        """Chain integrity requirements must be specified."""
        with open("contracts/vault_liveness.yaml") as f:
            contract = yaml.safe_load(f)
        chain = contract["chain_requirements"]
        assert chain["require_merkle_chain"] is True
        assert chain["verify_sha256"] is True

    def test_degradation_seal_blocked_on_stale(self):
        """When vault is stale (RED), SEAL must be blocked."""
        with open("contracts/vault_liveness.yaml") as f:
            contract = yaml.safe_load(f)
        red = contract["degradation_effects"]["RED"]
        assert red["seal_allowed"] is False
        assert red["forge_allowed"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# P0.5 — Budget Enforcement
# ═══════════════════════════════════════════════════════════════════════════════


class TestBudgetEnforcement:
    """Budget limits must constrain agentic action."""

    def test_all_7_domains_defined(self):
        """All 7 budget domains must have limits."""
        assert len(CANONICAL_SESSION_BUDGET) == 7
        for domain in BudgetDomain:
            assert domain in CANONICAL_SESSION_BUDGET, f"Missing {domain}"

    def test_budget_state_abundant_at_start(self):
        """Fresh budget should be ABUNDANT."""
        limit = BudgetLimit(domain=BudgetDomain.TOKEN, max_value=1000, current_value=0)
        assert limit.state == BudgetState.ABUNDANT
        assert limit.fraction_used == 0.0

    def test_budget_state_exhausted(self):
        """Exhausted budget should be EXHAUSTED."""
        limit = BudgetLimit(domain=BudgetDomain.TOKEN, max_value=1000, current_value=1000)
        assert limit.state == BudgetState.EXHAUSTED
        assert limit.remaining == 0.0

    def test_budget_state_critical(self):
        """Budget at hold threshold should be CRITICAL."""
        limit = BudgetLimit(domain=BudgetDomain.TOKEN, max_value=1000, current_value=900)
        assert limit.state == BudgetState.CRITICAL

    def test_check_budget_allows_normal(self):
        """Normal budget usage should be allowed."""
        budgets = {
            BudgetDomain.TOKEN: BudgetLimit(
                domain=BudgetDomain.TOKEN, max_value=1000, current_value=100
            ),
        }
        allowed, reason = check_budget(budgets, BudgetDomain.TOKEN, cost=50)
        assert allowed
        assert "ok" in reason

    def test_check_budget_blocks_exhausted(self):
        """Exhausted budget should block."""
        budgets = {
            BudgetDomain.TOKEN: BudgetLimit(
                domain=BudgetDomain.TOKEN, max_value=1000, current_value=1000
            ),
        }
        allowed, reason = check_budget(budgets, BudgetDomain.TOKEN, cost=50)
        assert not allowed
        assert "EXHAUSTED" in reason

    def test_check_budget_warns_critical(self):
        """Critical budget should still allow but warn."""
        budgets = {
            BudgetDomain.TOKEN: BudgetLimit(
                domain=BudgetDomain.TOKEN, max_value=1000, current_value=890
            ),
        }
        allowed, reason = check_budget(budgets, BudgetDomain.TOKEN, cost=50)
        assert allowed
        assert "CRITICAL" in reason

    def test_missing_domain_allows(self):
        """Undefined budget domain should default-allow."""
        allowed, reason = check_budget({}, BudgetDomain.ENTROPY, cost=0.1)
        assert allowed

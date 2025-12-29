"""
test_genius_law_v38_alignment.py - v38Omega GENIUS LAW Alignment Tests

Checks that:
- spec/genius_law_v38Omega.json exists and is valid
- G, C_dark, Psi, TP metrics are defined with affects_floors
- thresholds in arifos_core.genius_metrics match the v38Omega spec
- integration_v38.flow documents the v38 flow
- canon file exists at the expected location

Author: arifOS Project
Version: v38.0.0
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifos_core.enforcement.genius_metrics import (
    G_MIN_THRESHOLD,
    C_DARK_MAX_THRESHOLD,
    PSI_APEX_MIN,
    EPSILON,
    evaluate_genius_law,
    GeniusVerdict,
)
from arifos_core.enforcement.metrics import Metrics


REPO_ROOT = Path(__file__).resolve().parents[1]
V38_SPEC_PATH = REPO_ROOT / "spec" / "genius_law_v38Omega.json"
V38_CANON_PATH = REPO_ROOT / "archive" / "v38_0_0" / "canon" / "_GENIUS_LAW_v38Omega.md"


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def genius_spec_v38() -> dict:
    """Load the v38Omega GENIUS LAW spec."""
    assert V38_SPEC_PATH.exists(), f"Missing v38 GENIUS spec at {V38_SPEC_PATH}"
    with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# =============================================================================
# SPEC FILE TESTS
# =============================================================================

class TestV38GeniusSpecFile:
    """Tests for the v38Omega GENIUS LAW spec file structure."""

    def test_v38_spec_exists(self) -> None:
        """v38 GENIUS spec file must exist."""
        assert V38_SPEC_PATH.exists(), f"Missing v38 GENIUS spec at {V38_SPEC_PATH}"

    def test_v38_spec_is_valid_json(self) -> None:
        """v38 GENIUS spec must be valid JSON."""
        with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_v38_spec_metadata(self, genius_spec_v38: dict) -> None:
        """Spec must declare v38 metadata."""
        assert genius_spec_v38.get("version") == "v38.0.0"
        assert genius_spec_v38.get("arifos_version") == "38Omega"
        assert genius_spec_v38.get("spec_type") == "genius_law"

    def test_v38_spec_has_all_metrics(self, genius_spec_v38: dict) -> None:
        """All 4 GENIUS metrics must be present."""
        metrics = genius_spec_v38.get("metrics", {})
        expected_keys = {"G", "C_dark", "Psi", "TP"}
        missing = expected_keys.difference(metrics.keys())
        assert not missing, f"Missing metrics in v38 GENIUS spec: {sorted(missing)}"


# =============================================================================
# AFFECTS_FLOORS TESTS
# =============================================================================

class TestMetricsAffectsFloors:
    """Tests that each metric has affects_floors defined."""

    def test_g_has_affects_floors(self, genius_spec_v38: dict) -> None:
        """G metric must have affects_floors."""
        g_metric = genius_spec_v38["metrics"]["G"]
        assert "affects_floors" in g_metric
        assert isinstance(g_metric["affects_floors"], list)
        assert len(g_metric["affects_floors"]) > 0

    def test_c_dark_has_affects_floors(self, genius_spec_v38: dict) -> None:
        """C_dark metric must have affects_floors."""
        c_dark_metric = genius_spec_v38["metrics"]["C_dark"]
        assert "affects_floors" in c_dark_metric
        assert isinstance(c_dark_metric["affects_floors"], list)
        assert len(c_dark_metric["affects_floors"]) > 0

    def test_psi_has_affects_floors(self, genius_spec_v38: dict) -> None:
        """Psi metric must have affects_floors."""
        psi_metric = genius_spec_v38["metrics"]["Psi"]
        assert "affects_floors" in psi_metric
        # Psi affects all floors, so can be string "all" or list
        affects = psi_metric["affects_floors"]
        assert affects == "all" or isinstance(affects, list)

    def test_tp_has_affects_floors(self, genius_spec_v38: dict) -> None:
        """TP (Truth Polarity) metric must have affects_floors."""
        tp_metric = genius_spec_v38["metrics"]["TP"]
        assert "affects_floors" in tp_metric
        assert isinstance(tp_metric["affects_floors"], list)
        assert len(tp_metric["affects_floors"]) > 0


# =============================================================================
# CANON REF TESTS
# =============================================================================

class TestV38GeniusCanonRefs:
    """Tests for canon_ref fields pointing to the v38 GENIUS canon."""

    def test_v38_canon_file_exists(self) -> None:
        """Canon file must exist at expected location."""
        assert V38_CANON_PATH.exists(), f"Missing v38 GENIUS canon at {V38_CANON_PATH}"

    def test_v38_spec_metrics_have_canon_ref(self, genius_spec_v38: dict) -> None:
        """Each metric entry should have a canon_ref."""
        metrics = genius_spec_v38.get("metrics", {})
        for key, metric_def in metrics.items():
            canon_ref = metric_def.get("canon_ref")
            assert isinstance(canon_ref, str) and canon_ref, f"{key} missing canon_ref"
            assert "02_GENIUS_LAW_v38Omega.md" in canon_ref, (
                f"{key} canon_ref does not point to v38 GENIUS canon: {canon_ref}"
            )


# =============================================================================
# THRESHOLD ALIGNMENT TESTS
# =============================================================================

class TestGeniusThresholdAlignment:
    """Tests that genius_metrics.py thresholds match the v38 spec."""

    def test_g_void_threshold_matches_spec(self, genius_spec_v38: dict) -> None:
        """G_MIN_THRESHOLD must match v38 spec G.thresholds.void."""
        g_void_spec = genius_spec_v38["metrics"]["G"]["thresholds"]["void"]
        assert G_MIN_THRESHOLD == pytest.approx(g_void_spec)
        assert G_MIN_THRESHOLD == pytest.approx(0.50)

    def test_c_dark_seal_threshold_matches_spec(self, genius_spec_v38: dict) -> None:
        """C_DARK_MAX_THRESHOLD must match v38 spec C_dark.thresholds.seal."""
        c_dark_seal_spec = genius_spec_v38["metrics"]["C_dark"]["thresholds"]["seal"]
        assert C_DARK_MAX_THRESHOLD == pytest.approx(c_dark_seal_spec)
        assert C_DARK_MAX_THRESHOLD == pytest.approx(0.30)

    def test_psi_seal_threshold_matches_spec(self, genius_spec_v38: dict) -> None:
        """PSI_APEX_MIN must match v38 spec Psi.thresholds.seal."""
        psi_seal_spec = genius_spec_v38["metrics"]["Psi"]["thresholds"]["seal"]
        assert PSI_APEX_MIN == pytest.approx(psi_seal_spec)
        assert PSI_APEX_MIN == pytest.approx(1.00)

    def test_epsilon_matches_spec(self, genius_spec_v38: dict) -> None:
        """EPSILON must match v38 spec Psi.parameters.epsilon."""
        epsilon_spec = genius_spec_v38["metrics"]["Psi"]["parameters"]["epsilon"]
        assert EPSILON == pytest.approx(epsilon_spec)
        assert EPSILON == pytest.approx(0.01)


# =============================================================================
# INTEGRATION V38 TESTS
# =============================================================================

class TestIntegrationV38:
    """Tests for v38 integration documentation in spec."""

    def test_integration_v38_exists(self, genius_spec_v38: dict) -> None:
        """Spec must have integration_v38 section."""
        assert "integration_v38" in genius_spec_v38

    def test_integration_v38_has_flow(self, genius_spec_v38: dict) -> None:
        """integration_v38 must document the flow."""
        integration = genius_spec_v38["integration_v38"]
        assert "flow" in integration
        flow = integration["flow"]
        assert isinstance(flow, str) and len(flow) > 0
        # Flow should mention key stages
        assert "Floors" in flow or "floors" in flow
        assert "Memory" in flow or "memory" in flow

    def test_integration_v38_has_memory_integration(self, genius_spec_v38: dict) -> None:
        """integration_v38 must document memory integration."""
        integration = genius_spec_v38["integration_v38"]
        assert "memory_integration" in integration
        mem_int = integration["memory_integration"]
        assert "evidence_chain_includes" in mem_int

    def test_integration_v38_references_floors_spec(self, genius_spec_v38: dict) -> None:
        """integration_v38 must reference the floors spec."""
        integration = genius_spec_v38["integration_v38"]
        assert "floors_spec_ref" in integration
        ref = integration["floors_spec_ref"]
        assert "constitutional_floors_v38Omega.json" in ref


# =============================================================================
# VERDICT LOGIC TESTS
# =============================================================================

class TestVerdictLogic:
    """Tests for verdict logic documentation in spec."""

    def test_verdict_logic_exists(self, genius_spec_v38: dict) -> None:
        """Spec must have verdict_logic section."""
        assert "verdict_logic" in genius_spec_v38

    def test_verdict_logic_has_constants(self, genius_spec_v38: dict) -> None:
        """verdict_logic must have constants."""
        verdict_logic = genius_spec_v38["verdict_logic"]
        assert "constants" in verdict_logic
        constants = verdict_logic["constants"]
        expected = {"G_SEAL", "G_VOID", "PSI_SEAL", "PSI_SABAR", "CDARK_SEAL", "CDARK_WARN"}
        assert expected.issubset(constants.keys())

    def test_verdict_logic_has_priority_order(self, genius_spec_v38: dict) -> None:
        """verdict_logic must have priority_order."""
        verdict_logic = genius_spec_v38["verdict_logic"]
        assert "priority_order" in verdict_logic
        assert isinstance(verdict_logic["priority_order"], list)
        assert len(verdict_logic["priority_order"]) > 0


# =============================================================================
# CANON CONTENT TESTS
# =============================================================================

class TestGeniusCanonContent:
    """Tests for the v38 GENIUS canon file content."""

    def test_canon_has_all_metrics_documented(self) -> None:
        """Canon file must document all 4 GENIUS metrics."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")

        metric_markers = [
            "Genius Index (G)",
            "Dark Cleverness (C_dark)",
            "Vitality (Psi)",
            "Truth Polarity",
        ]

        for marker in metric_markers:
            assert marker in content, f"Canon missing documentation for {marker}"

    def test_canon_has_formulas(self) -> None:
        """Canon file must include formulas."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "Formula:" in content or "formula" in content.lower()

    def test_canon_has_v38_version(self) -> None:
        """Canon file must indicate v38 version."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "v38" in content or "38Omega" in content


# =============================================================================
# FUNCTIONAL TESTS
# =============================================================================

class TestGeniusEvaluation:
    """Tests that evaluate_genius_law produces expected results."""

    def test_healthy_metrics_produce_green(self) -> None:
        """Healthy metrics should produce GREEN risk level."""
        m = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
        )
        verdict = evaluate_genius_law(m)
        assert isinstance(verdict, GeniusVerdict)
        assert verdict.g_healthy
        assert verdict.c_dark_safe
        assert verdict.system_alive

    def test_amanah_failure_produces_red(self) -> None:
        """Amanah failure should produce issues."""
        m = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=False,  # Failure
            tri_witness=0.96,
        )
        verdict = evaluate_genius_law(m)
        # Amanah failure zeros omega, affecting G and psi_apex
        assert not verdict.g_healthy or not verdict.system_alive

    def test_truth_polarity_detection(self) -> None:
        """Truth polarity should be detected."""
        # Truth-Light: accurate + clarifying
        m_light = Metrics(
            truth=0.99,
            delta_s=0.1,  # positive
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
        )
        verdict_light = evaluate_genius_law(m_light)
        assert verdict_light.truth_polarity == "truth_light"
        assert not verdict_light.is_shadow_truth

        # Shadow-Truth: accurate but obscuring
        m_shadow = Metrics(
            truth=0.99,
            delta_s=-0.1,  # negative
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,  # good faith
            tri_witness=0.96,
        )
        verdict_shadow = evaluate_genius_law(m_shadow)
        assert verdict_shadow.truth_polarity == "shadow_truth"
        assert verdict_shadow.is_shadow_truth
        assert not verdict_shadow.is_weaponized_truth


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

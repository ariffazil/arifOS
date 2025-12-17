"""
test_cooling_phoenix_v38_alignment.py - v38Omega Cooling Ledger & Phoenix-72 Alignment Tests

Checks that:
- spec/cooling_ledger_phoenix_v38Omega.json exists and is valid
- Verdict→band routing in spec matches policy.py
- Scar lifecycle statuses match scar_manager.py
- Severity weights match scar_manager.py
- Retention constants match policy.py
- Phoenix-72 phases are documented
- Canon file exists at the expected location

Author: arifOS Project
Version: v38.0.0
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifos_core.memory.policy import (
    VERDICT_BAND_ROUTING,
    RETENTION_HOT_DAYS,
    RETENTION_WARM_DAYS,
    RETENTION_COLD_DAYS,
    RETENTION_VOID_DAYS,
)
from arifos_core.memory.scar_manager import (
    SEVERITY_WEIGHTS,
    ScarStatus,
    ScarKind,
    SeverityLevel,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
V38_SPEC_PATH = REPO_ROOT / "spec" / "cooling_ledger_phoenix_v38Omega.json"
V38_CANON_PATH = REPO_ROOT / "archive" / "v38_0_0" / "canon" / "_COOLING_LEDGER_PHOENIX_v38Omega.md"


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def cooling_phoenix_spec() -> dict:
    """Load the v38Omega Cooling Ledger & Phoenix-72 spec."""
    assert V38_SPEC_PATH.exists(), f"Missing v38 spec at {V38_SPEC_PATH}"
    with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# =============================================================================
# SPEC FILE TESTS
# =============================================================================

class TestV38CoolingPhoenixSpecFile:
    """Tests for the v38Omega spec file structure."""

    def test_v38_spec_exists(self) -> None:
        """v38 spec file must exist."""
        assert V38_SPEC_PATH.exists(), f"Missing v38 spec at {V38_SPEC_PATH}"

    def test_v38_spec_is_valid_json(self) -> None:
        """v38 spec must be valid JSON."""
        with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_v38_spec_metadata(self, cooling_phoenix_spec: dict) -> None:
        """Spec must declare v38 metadata."""
        assert cooling_phoenix_spec.get("version") == "v38.0.0"
        assert cooling_phoenix_spec.get("arifos_version") == "38Omega"
        assert cooling_phoenix_spec.get("spec_type") == "cooling_ledger_phoenix"

    def test_v38_spec_has_cooling_ledger(self, cooling_phoenix_spec: dict) -> None:
        """Spec must have cooling_ledger section."""
        assert "cooling_ledger" in cooling_phoenix_spec
        ledger = cooling_phoenix_spec["cooling_ledger"]
        assert "entry_schema" in ledger
        assert "head_state_schema" in ledger
        assert "hash_algorithm" in ledger

    def test_v38_spec_has_phoenix72(self, cooling_phoenix_spec: dict) -> None:
        """Spec must have phoenix72 section."""
        assert "phoenix72" in cooling_phoenix_spec
        phoenix = cooling_phoenix_spec["phoenix72"]
        assert "phases" in phoenix
        assert "amendment_schema" in phoenix
        assert "scar_schema" in phoenix


# =============================================================================
# VERDICT ROUTING TESTS
# =============================================================================

class TestVerdictBandRouting:
    """Tests that spec verdict routing matches policy.py."""

    def test_spec_has_verdict_band_routing(self, cooling_phoenix_spec: dict) -> None:
        """Spec must have verdict_band_routing section."""
        assert "verdict_band_routing" in cooling_phoenix_spec

    def test_seal_routing_matches(self, cooling_phoenix_spec: dict) -> None:
        """SEAL routing must match policy.py."""
        spec_routing = cooling_phoenix_spec["verdict_band_routing"]["SEAL"]
        assert spec_routing == VERDICT_BAND_ROUTING["SEAL"]
        assert spec_routing == ["LEDGER", "ACTIVE"]

    def test_sabar_routing_matches(self, cooling_phoenix_spec: dict) -> None:
        """SABAR routing must match policy.py (v38.3: routes to PENDING + LEDGER)."""
        spec_routing = cooling_phoenix_spec["verdict_band_routing"]["SABAR"]
        assert spec_routing == VERDICT_BAND_ROUTING["SABAR"]
        # v38.3 AMENDMENT 2: SABAR routes to PENDING (epistemic queue) + LEDGER
        assert spec_routing == ["PENDING", "LEDGER"]

    def test_partial_routing_matches(self, cooling_phoenix_spec: dict) -> None:
        """PARTIAL routing must match policy.py."""
        spec_routing = cooling_phoenix_spec["verdict_band_routing"]["PARTIAL"]
        assert spec_routing == VERDICT_BAND_ROUTING["PARTIAL"]
        assert spec_routing == ["PHOENIX", "LEDGER"]

    def test_void_routing_matches(self, cooling_phoenix_spec: dict) -> None:
        """VOID routing must match policy.py."""
        spec_routing = cooling_phoenix_spec["verdict_band_routing"]["VOID"]
        assert spec_routing == VERDICT_BAND_ROUTING["VOID"]
        assert spec_routing == ["VOID"]

    def test_888_hold_routing_matches(self, cooling_phoenix_spec: dict) -> None:
        """888_HOLD routing must match policy.py."""
        spec_routing = cooling_phoenix_spec["verdict_band_routing"]["888_HOLD"]
        assert spec_routing == VERDICT_BAND_ROUTING["888_HOLD"]
        assert spec_routing == ["LEDGER"]


# =============================================================================
# RETENTION CONSTANTS TESTS
# =============================================================================

class TestRetentionConstants:
    """Tests that spec retention constants match policy.py."""

    def test_spec_has_retention_constants(self, cooling_phoenix_spec: dict) -> None:
        """Spec must have retention_constants section."""
        assert "retention_constants" in cooling_phoenix_spec

    def test_hot_days_matches(self, cooling_phoenix_spec: dict) -> None:
        """RETENTION_HOT_DAYS must match policy.py."""
        spec_val = cooling_phoenix_spec["retention_constants"]["RETENTION_HOT_DAYS"]
        assert spec_val == RETENTION_HOT_DAYS
        assert spec_val == 7

    def test_warm_days_matches(self, cooling_phoenix_spec: dict) -> None:
        """RETENTION_WARM_DAYS must match policy.py."""
        spec_val = cooling_phoenix_spec["retention_constants"]["RETENTION_WARM_DAYS"]
        assert spec_val == RETENTION_WARM_DAYS
        assert spec_val == 90

    def test_cold_days_matches(self, cooling_phoenix_spec: dict) -> None:
        """RETENTION_COLD_DAYS must match policy.py."""
        spec_val = cooling_phoenix_spec["retention_constants"]["RETENTION_COLD_DAYS"]
        assert spec_val == RETENTION_COLD_DAYS
        assert spec_val == 365

    def test_void_days_matches(self, cooling_phoenix_spec: dict) -> None:
        """RETENTION_VOID_DAYS must match policy.py."""
        spec_val = cooling_phoenix_spec["retention_constants"]["RETENTION_VOID_DAYS"]
        assert spec_val == RETENTION_VOID_DAYS
        assert spec_val == 90


# =============================================================================
# SCAR LIFECYCLE TESTS
# =============================================================================

class TestScarLifecycle:
    """Tests that spec scar lifecycle matches scar_manager.py."""

    def test_spec_has_scar_lifecycle(self, cooling_phoenix_spec: dict) -> None:
        """Spec must have scar_lifecycle section."""
        assert "scar_lifecycle" in cooling_phoenix_spec

    def test_scar_kinds_match(self, cooling_phoenix_spec: dict) -> None:
        """Scar kinds must match scar_manager.py."""
        spec_kinds = set(cooling_phoenix_spec["scar_lifecycle"]["kinds"].keys())
        # ScarKind is a Literal type, so we check against expected values
        expected_kinds = {"WITNESS", "SCAR"}
        assert spec_kinds == expected_kinds

    def test_scar_statuses_match(self, cooling_phoenix_spec: dict) -> None:
        """Scar statuses must match scar_manager.py."""
        spec_statuses = set(cooling_phoenix_spec["scar_lifecycle"]["statuses"].keys())
        # ScarStatus is Literal["PROPOSED", "SEALED", "HEALED", "DEPRECATED"]
        expected_statuses = {"PROPOSED", "SEALED", "HEALED", "DEPRECATED"}
        assert spec_statuses == expected_statuses

    def test_severity_weights_match(self, cooling_phoenix_spec: dict) -> None:
        """Severity weights must match scar_manager.py."""
        spec_severities = cooling_phoenix_spec["scar_lifecycle"]["severity_levels"]

        for level, weight in SEVERITY_WEIGHTS.items():
            assert level in spec_severities, f"Missing severity {level} in spec"
            assert spec_severities[level]["weight"] == weight

    def test_s1_weight(self, cooling_phoenix_spec: dict) -> None:
        """S1 weight must be 1.0."""
        assert cooling_phoenix_spec["scar_lifecycle"]["severity_levels"]["S1"]["weight"] == 1.0
        assert SEVERITY_WEIGHTS["S1"] == 1.0

    def test_s2_weight(self, cooling_phoenix_spec: dict) -> None:
        """S2 weight must be 2.0."""
        assert cooling_phoenix_spec["scar_lifecycle"]["severity_levels"]["S2"]["weight"] == 2.0
        assert SEVERITY_WEIGHTS["S2"] == 2.0

    def test_s3_weight(self, cooling_phoenix_spec: dict) -> None:
        """S3 weight must be 4.0."""
        assert cooling_phoenix_spec["scar_lifecycle"]["severity_levels"]["S3"]["weight"] == 4.0
        assert SEVERITY_WEIGHTS["S3"] == 4.0

    def test_s4_weight(self, cooling_phoenix_spec: dict) -> None:
        """S4 weight must be 8.0."""
        assert cooling_phoenix_spec["scar_lifecycle"]["severity_levels"]["S4"]["weight"] == 8.0
        assert SEVERITY_WEIGHTS["S4"] == 8.0


# =============================================================================
# PHOENIX-72 TESTS
# =============================================================================

class TestPhoenix72Spec:
    """Tests for Phoenix-72 specification."""

    def test_phoenix_cooling_window(self, cooling_phoenix_spec: dict) -> None:
        """Phoenix cooling window must be 72 hours."""
        phoenix = cooling_phoenix_spec["phoenix72"]
        assert phoenix["cooling_window_hours"] == 72

    def test_phoenix_phases(self, cooling_phoenix_spec: dict) -> None:
        """Phoenix must have all 5 phases."""
        phoenix = cooling_phoenix_spec["phoenix72"]
        expected_phases = [
            "SCAR_CAPTURE",
            "PATTERN_SYNTHESIS",
            "AMENDMENT_DRAFT",
            "HUMAN_REVIEW",
            "CANONIZATION",
        ]
        assert phoenix["phases"] == expected_phases

    def test_phoenix_amendment_schema_fields(self, cooling_phoenix_spec: dict) -> None:
        """Amendment schema must have required fields."""
        schema = cooling_phoenix_spec["phoenix72"]["amendment_schema"]
        required = {"id", "applied_at", "reason", "tri_witness", "delta_s_gain", "peace2", "changes", "evidence"}
        assert required.issubset(schema.keys())


# =============================================================================
# INVARIANTS TESTS
# =============================================================================

class TestInvariants:
    """Tests for memory invariants in spec."""

    def test_spec_has_invariants(self, cooling_phoenix_spec: dict) -> None:
        """Spec must have invariants section."""
        assert "invariants" in cooling_phoenix_spec

    def test_inv1_void_never_canonical(self, cooling_phoenix_spec: dict) -> None:
        """INV-1 must state VOID never canonical."""
        inv = cooling_phoenix_spec["invariants"]["INV-1"]
        assert "VOID" in inv["statement"]
        assert "never" in inv["statement"].lower() or "NEVER" in inv["statement"]

    def test_inv2_authority_boundary(self, cooling_phoenix_spec: dict) -> None:
        """INV-2 must state authority boundary."""
        inv = cooling_phoenix_spec["invariants"]["INV-2"]
        assert "human" in inv["statement"].lower()
        assert "seal" in inv["statement"].lower() or "propose" in inv["statement"].lower()

    def test_inv3_evidence_chain(self, cooling_phoenix_spec: dict) -> None:
        """INV-3 must require evidence chain."""
        inv = cooling_phoenix_spec["invariants"]["INV-3"]
        assert "audit" in inv["statement"].lower() or "evidence" in inv["statement"].lower()

    def test_inv4_recall_ceiling(self, cooling_phoenix_spec: dict) -> None:
        """INV-4 must specify recall confidence ceiling."""
        inv = cooling_phoenix_spec["invariants"]["INV-4"]
        assert "0.85" in inv["enforcement"] or "suggestion" in inv["statement"].lower()


# =============================================================================
# CANON FILE TESTS
# =============================================================================

class TestCanonFile:
    """Tests for the v38 canon file."""

    def test_canon_file_exists(self) -> None:
        """Canon file must exist at expected location."""
        assert V38_CANON_PATH.exists(), f"Missing v38 canon at {V38_CANON_PATH}"

    def test_canon_has_cooling_ledger_section(self) -> None:
        """Canon must have Cooling Ledger section."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "Cooling Ledger" in content

    def test_canon_has_phoenix_section(self) -> None:
        """Canon must have Phoenix-72 section."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "Phoenix-72" in content or "Phoenix72" in content

    def test_canon_has_scar_lifecycle(self) -> None:
        """Canon must document scar lifecycle."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "Scar" in content or "SCAR" in content
        # Check for scar statuses
        assert "PROPOSED" in content
        assert "SEALED" in content

    def test_canon_has_verdict_routing(self) -> None:
        """Canon must document verdict routing."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "VERDICT" in content.upper() or "Verdict" in content
        assert "SEAL" in content
        assert "VOID" in content

    def test_canon_has_v38_version(self) -> None:
        """Canon must indicate v38 version."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "v38" in content or "38Omega" in content


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Tests for integration points in spec."""

    def test_spec_has_integration(self, cooling_phoenix_spec: dict) -> None:
        """Spec must have integration section."""
        assert "integration" in cooling_phoenix_spec

    def test_pipeline_stages_documented(self, cooling_phoenix_spec: dict) -> None:
        """Pipeline stages must be documented."""
        integration = cooling_phoenix_spec["integration"]
        assert "pipeline_stages" in integration
        stages = integration["pipeline_stages"]

        # Check key stages
        assert "111_SENSE" in stages
        assert "777_FORGE" in stages
        assert "888_JUDGE" in stages
        assert "999_SEAL" in stages

    def test_integration_flow(self, cooling_phoenix_spec: dict) -> None:
        """Integration flow must be documented."""
        integration = cooling_phoenix_spec["integration"]
        assert "flow" in integration
        flow = integration["flow"]
        # Flow should include key stages
        assert "111" in flow or "SENSE" in flow
        assert "888" in flow or "JUDGE" in flow
        assert "999" in flow or "SEAL" in flow


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
test_floors_v38_alignment.py - v38Omega Constitutional Floors Alignment Tests

Checks that:
- spec/constitutional_floors_v38Omega.json exists and is valid
- all 9 floors are defined
- thresholds in arifos_core.metrics match the v38Omega spec
- each floor has a canon_ref into canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md
- canon file exists at the expected location

Author: arifOS Project
Version: v38.0.0
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifos_core.enforcement.metrics import (
    TRUTH_THRESHOLD,
    DELTA_S_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    KAPPA_R_THRESHOLD,
    OMEGA_0_MIN,
    OMEGA_0_MAX,
    TRI_WITNESS_THRESHOLD,
    PSI_THRESHOLD,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
V38_SPEC_PATH = REPO_ROOT / "spec" / "constitutional_floors_v38Omega.json"
V38_CANON_PATH = REPO_ROOT / "archive" / "v38_0_0" / "canon" / "_CONSTITUTIONAL_FLOORS_v38Omega.md"


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def floors_spec_v38() -> dict:
    """Load the v38Omega constitutional floors spec."""
    assert V38_SPEC_PATH.exists(), f"Missing v38 spec at {V38_SPEC_PATH}"
    with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# =============================================================================
# SPEC FILE TESTS
# =============================================================================

class TestV38SpecFile:
    """Tests for the v38Omega spec file structure."""

    def test_v38_spec_exists(self) -> None:
        """v38 spec file must exist."""
        assert V38_SPEC_PATH.exists(), f"Missing v38 spec at {V38_SPEC_PATH}"

    def test_v38_spec_is_valid_json(self) -> None:
        """v38 spec must be valid JSON."""
        with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_v38_spec_metadata(self, floors_spec_v38: dict) -> None:
        """Spec must declare v38 metadata."""
        assert floors_spec_v38.get("version") == "v38.3.0"
        assert floors_spec_v38.get("arifos_version") == "38.3Omega"
        assert floors_spec_v38.get("spec_type") == "constitutional_floors"

    def test_v38_spec_has_all_nine_floors(self, floors_spec_v38: dict) -> None:
        """All 9 floors must be present in the v38 spec."""
        floors = floors_spec_v38.get("floors", {})
        expected_keys = {
            "truth",
            "delta_s",
            "peace_squared",
            "kappa_r",
            "omega_0",
            "amanah",
            "rasa",
            "tri_witness",
            "anti_hantu",
        }
        missing = expected_keys.difference(floors.keys())
        assert not missing, f"Missing floors in v38 spec: {sorted(missing)}"

    def test_v38_spec_has_floor_categories(self, floors_spec_v38: dict) -> None:
        """Spec must define floor categories."""
        categories = floors_spec_v38.get("floor_categories", {})
        assert "hard" in categories
        assert "soft" in categories
        assert "meta" in categories

    def test_v38_spec_has_verdicts(self, floors_spec_v38: dict) -> None:
        """Spec must define verdicts."""
        verdicts = floors_spec_v38.get("verdicts", {})
        expected_verdicts = {"SEAL", "PARTIAL", "888_HOLD", "VOID", "SABAR"}
        assert expected_verdicts.issubset(verdicts.keys())

    def test_v38_spec_has_vitality(self, floors_spec_v38: dict) -> None:
        """Spec must define vitality (Psi)."""
        vitality = floors_spec_v38.get("vitality", {})
        assert vitality.get("symbol") == "Psi"
        assert vitality.get("threshold") == 1.0


# =============================================================================
# CANON REF TESTS
# =============================================================================

class TestV38CanonRefs:
    """Tests for canon_ref fields pointing to the v38 canon."""

    def test_v38_canon_file_exists(self) -> None:
        """Canon file must exist at expected location."""
        assert V38_CANON_PATH.exists(), f"Missing v38 canon at {V38_CANON_PATH}"

    def test_v38_spec_each_floor_has_canon_ref(self, floors_spec_v38: dict) -> None:
        """Each floor entry must include a canon_ref pointing to the v38 canon."""
        floors = floors_spec_v38.get("floors", {})
        for key, floor_def in floors.items():
            canon_ref = floor_def.get("canon_ref")
            assert isinstance(canon_ref, str) and canon_ref, f"{key} missing canon_ref"
            assert "01_CONSTITUTIONAL_FLOORS_v38Omega.md" in canon_ref, (
                f"{key} canon_ref does not point to v38 canon: {canon_ref}"
            )

    def test_v38_spec_vitality_has_canon_ref(self, floors_spec_v38: dict) -> None:
        """Vitality (Psi) entry must have a canon_ref."""
        vitality = floors_spec_v38.get("vitality", {})
        canon_ref = vitality.get("canon_ref")
        assert isinstance(canon_ref, str) and canon_ref, "vitality missing canon_ref"
        assert "01_CONSTITUTIONAL_FLOORS_v38Omega.md" in canon_ref


# =============================================================================
# THRESHOLD ALIGNMENT TESTS
# =============================================================================

class TestMetricsThresholdAlignment:
    """Tests that metrics.py thresholds match the v38 spec."""

    def test_truth_threshold_matches_spec(self, floors_spec_v38: dict) -> None:
        """TRUTH_THRESHOLD must match v38 spec."""
        truth_spec = floors_spec_v38["floors"]["truth"]["threshold"]
        assert TRUTH_THRESHOLD == pytest.approx(truth_spec)
        assert TRUTH_THRESHOLD == pytest.approx(0.99)

    def test_delta_s_threshold_matches_spec(self, floors_spec_v38: dict) -> None:
        """DELTA_S_THRESHOLD must match v38 spec."""
        delta_s_spec = floors_spec_v38["floors"]["delta_s"]["threshold"]
        assert DELTA_S_THRESHOLD == pytest.approx(delta_s_spec)
        assert DELTA_S_THRESHOLD == pytest.approx(0.0)

    def test_peace_squared_threshold_matches_spec(self, floors_spec_v38: dict) -> None:
        """PEACE_SQUARED_THRESHOLD must match v38 spec."""
        peace_spec = floors_spec_v38["floors"]["peace_squared"]["threshold"]
        assert PEACE_SQUARED_THRESHOLD == pytest.approx(peace_spec)
        assert PEACE_SQUARED_THRESHOLD == pytest.approx(1.0)

    def test_kappa_r_threshold_matches_spec(self, floors_spec_v38: dict) -> None:
        """KAPPA_R_THRESHOLD must match v38 spec."""
        kappa_spec = floors_spec_v38["floors"]["kappa_r"]["threshold"]
        assert KAPPA_R_THRESHOLD == pytest.approx(kappa_spec)
        assert KAPPA_R_THRESHOLD == pytest.approx(0.95)

    def test_omega_0_band_matches_spec(self, floors_spec_v38: dict) -> None:
        """OMEGA_0_MIN and OMEGA_0_MAX must match v38 spec."""
        omega_spec_min = floors_spec_v38["floors"]["omega_0"]["threshold_min"]
        omega_spec_max = floors_spec_v38["floors"]["omega_0"]["threshold_max"]
        assert OMEGA_0_MIN == pytest.approx(omega_spec_min)
        assert OMEGA_0_MAX == pytest.approx(omega_spec_max)
        assert OMEGA_0_MIN == pytest.approx(0.03)
        assert OMEGA_0_MAX == pytest.approx(0.05)

    def test_tri_witness_threshold_matches_spec(self, floors_spec_v38: dict) -> None:
        """TRI_WITNESS_THRESHOLD must match v38 spec."""
        tri_spec = floors_spec_v38["floors"]["tri_witness"]["threshold"]
        assert TRI_WITNESS_THRESHOLD == pytest.approx(tri_spec)
        assert TRI_WITNESS_THRESHOLD == pytest.approx(0.95)

    def test_psi_threshold_matches_spec(self, floors_spec_v38: dict) -> None:
        """PSI_THRESHOLD must match v38 spec."""
        psi_spec = floors_spec_v38["vitality"]["threshold"]
        assert PSI_THRESHOLD == pytest.approx(psi_spec)
        assert PSI_THRESHOLD == pytest.approx(1.0)


# =============================================================================
# FLOOR TYPE TESTS
# =============================================================================

class TestFloorTypes:
    """Tests for floor type classifications."""

    def test_hard_floors_are_correct(self, floors_spec_v38: dict) -> None:
        """Hard floors must be correctly classified."""
        floors = floors_spec_v38["floors"]
        hard_category = floors_spec_v38["floor_categories"]["hard"]["floors"]

        for floor_key in ["truth", "delta_s", "omega_0", "amanah", "rasa"]:
            assert floors[floor_key]["type"] == "hard", f"{floor_key} should be hard"
            assert floor_key in hard_category, f"{floor_key} should be in hard category"

    def test_soft_floors_are_correct(self, floors_spec_v38: dict) -> None:
        """Soft floors must be correctly classified."""
        floors = floors_spec_v38["floors"]
        soft_category = floors_spec_v38["floor_categories"]["soft"]["floors"]

        for floor_key in ["peace_squared", "kappa_r", "tri_witness"]:
            assert floors[floor_key]["type"] == "soft", f"{floor_key} should be soft"
            assert floor_key in soft_category, f"{floor_key} should be in soft category"

    def test_meta_floor_is_correct(self, floors_spec_v38: dict) -> None:
        """Meta floor must be correctly classified."""
        floors = floors_spec_v38["floors"]
        meta_category = floors_spec_v38["floor_categories"]["meta"]["floors"]

        assert floors["anti_hantu"]["type"] == "meta"
        assert "anti_hantu" in meta_category


# =============================================================================
# v35 COMPATIBILITY TESTS
# =============================================================================

class TestV35Compatibility:
    """Tests that v38 spec maintains compatibility with v35Omega semantics."""

    def test_v35_spec_unchanged(self) -> None:
        """v35 spec file should still exist and be unchanged."""
        v35_path = REPO_ROOT / "spec" / "constitutional_floors_v35Omega.json"
        assert v35_path.exists(), "v35 spec should still exist for backwards compatibility"

        with v35_path.open("r", encoding="utf-8") as f:
            v35_data = json.load(f)

        # v35 should have same floor keys
        assert "floors" in v35_data
        assert set(v35_data["floors"].keys()) == {
            "truth", "delta_s", "peace_squared", "kappa_r",
            "omega_0", "amanah", "rasa", "tri_witness", "anti_hantu"
        }

    def test_v38_thresholds_match_v35(self, floors_spec_v38: dict) -> None:
        """v38 thresholds must be identical to v35 (formalization only)."""
        v35_path = REPO_ROOT / "spec" / "constitutional_floors_v35Omega.json"
        with v35_path.open("r", encoding="utf-8") as f:
            v35_data = json.load(f)

        v38_floors = floors_spec_v38["floors"]
        v35_floors = v35_data["floors"]

        # Check numeric thresholds match
        assert v38_floors["truth"]["threshold"] == v35_floors["truth"]["threshold"]
        assert v38_floors["delta_s"]["threshold"] == v35_floors["delta_s"]["threshold"]
        assert v38_floors["peace_squared"]["threshold"] == v35_floors["peace_squared"]["threshold"]
        assert v38_floors["kappa_r"]["threshold"] == v35_floors["kappa_r"]["threshold"]
        assert v38_floors["omega_0"]["threshold_min"] == v35_floors["omega_0"]["threshold_min"]
        assert v38_floors["omega_0"]["threshold_max"] == v35_floors["omega_0"]["threshold_max"]
        assert v38_floors["tri_witness"]["threshold"] == v35_floors["tri_witness"]["threshold"]

        # Check boolean thresholds match
        assert v38_floors["amanah"]["threshold"] == v35_floors["amanah"]["threshold"]
        assert v38_floors["rasa"]["threshold"] == v35_floors["rasa"]["threshold"]
        assert v38_floors["anti_hantu"]["threshold"] == v35_floors["anti_hantu"]["threshold"]


# =============================================================================
# CANON CONTENT TESTS
# =============================================================================

class TestCanonContent:
    """Tests for the v38 canon file content."""

    def test_canon_has_all_floors_documented(self) -> None:
        """Canon file must document all 9 floors."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")

        floor_markers = [
            "F1 - Truth",
            "F2 - Clarity",
            "F3 - Stability",
            "F4 - Empathy",
            "F5 - Humility",
            "F6 - Amanah",
            "F7 - RASA",
            "F8 - Tri-Witness",
            "F9 - Anti-Hantu",
        ]

        for marker in floor_markers:
            assert marker in content, f"Canon missing documentation for {marker}"

    def test_canon_has_vitality_documented(self) -> None:
        """Canon file must document vitality (Psi)."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "Vitality" in content or "Psi" in content

    def test_canon_has_v38_version(self) -> None:
        """Canon file must indicate v38 version."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "v38" in content or "38Omega" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
test_canon_drift_guard.py — Canon Drift Detection Tests (v35Ω)

These tests verify that:
1. Numeric runtime-law canon files exist
2. constitutional_floors.json thresholds match metrics.py constants
3. Canon files align with 888_APEX_PRIME_CANON_v35Omega.md

Purpose: Detect future drift between code and canon.
These tests are READ-ONLY - they do not auto-fix anything.

See: canon/888_APEX_PRIME_CANON_v35Omega.md
     spec/v45/constitutional_floors.json
"""

import json
from pathlib import Path

import pytest

from arifos.core.enforcement.metrics import (
    TRUTH_THRESHOLD,
    DELTA_S_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    KAPPA_R_THRESHOLD,
    OMEGA_0_MIN,
    OMEGA_0_MAX,
    TRI_WITNESS_THRESHOLD,
    PSI_THRESHOLD,
    check_truth,
    check_delta_s,
    check_peace_squared,
    check_kappa_r,
    check_omega_band,
    check_tri_witness,
    check_psi,
    check_anti_hantu,
    ANTI_HANTU_FORBIDDEN,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def repo_root() -> Path:
    """Get repository root path."""
    # tests/ is one level below repo root
    return Path(__file__).parent.parent


@pytest.fixture
def canon_dir(repo_root) -> Path:
    """Get canon directory path (v45)."""
    return repo_root / "L1_THEORY" / "canon"


@pytest.fixture
def constitutional_floors_json(repo_root) -> dict:
    """Load constitutional_floors.json (v45)."""
    path = repo_root / "spec" / "v45" / "constitutional_floors.json"
    assert path.exists(), f"constitutional_floors.json not found at {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# TEST 1: RUNTIME LAW FILES EXIST
# =============================================================================

class TestRuntimeLawFilesExist:
    """Verify numeric runtime-law canon files exist."""

    def test_canon_files_exist(self, canon_dir):
        """Canon files must exist in L1_THEORY/canon."""
        md_files = list(canon_dir.rglob("*.md"))
        assert len(md_files) > 0, "No canon markdown files found in L1_THEORY/canon"
        
        # Check for Master Index (recursive search in subdirectories)
        master_index = list(canon_dir.rglob("*MASTER_INDEX*.md"))
        assert len(master_index) > 0, "Master Index not found"


# =============================================================================
# TEST 2: CONSTITUTIONAL FLOORS JSON MATCHES METRICS.PY
# =============================================================================

class TestConstitutionalFloorsJsonMatchesMetrics:
    """Verify constitutional_floors.json thresholds match metrics.py constants."""

    def test_truth_threshold_matches(self, constitutional_floors_json):
        """F1: Truth threshold matches."""
        json_threshold = constitutional_floors_json["floors"]["truth"]["threshold"]
        assert json_threshold == TRUTH_THRESHOLD, (
            f"Truth threshold mismatch: JSON={json_threshold}, metrics.py={TRUTH_THRESHOLD}"
        )

    def test_delta_s_threshold_matches(self, constitutional_floors_json):
        """F2: Delta-S threshold matches."""
        json_threshold = constitutional_floors_json["floors"]["delta_s"]["threshold"]
        assert json_threshold == DELTA_S_THRESHOLD, (
            f"Delta-S threshold mismatch: JSON={json_threshold}, metrics.py={DELTA_S_THRESHOLD}"
        )

    def test_peace_squared_threshold_matches(self, constitutional_floors_json):
        """F3: Peace-squared threshold matches."""
        json_threshold = constitutional_floors_json["floors"]["peace_squared"]["threshold"]
        assert json_threshold == PEACE_SQUARED_THRESHOLD, (
            f"Peace² threshold mismatch: JSON={json_threshold}, metrics.py={PEACE_SQUARED_THRESHOLD}"
        )

    def test_kappa_r_threshold_matches(self, constitutional_floors_json):
        """F4: Kappa-r threshold matches."""
        json_threshold = constitutional_floors_json["floors"]["kappa_r"]["threshold"]
        assert json_threshold == KAPPA_R_THRESHOLD, (
            f"κᵣ threshold mismatch: JSON={json_threshold}, metrics.py={KAPPA_R_THRESHOLD}"
        )

    def test_omega_0_band_matches(self, constitutional_floors_json):
        """F5: Omega-0 band matches."""
        json_min = constitutional_floors_json["floors"]["omega_0"]["threshold_min"]
        json_max = constitutional_floors_json["floors"]["omega_0"]["threshold_max"]
        assert json_min == OMEGA_0_MIN, (
            f"Ω₀ min mismatch: JSON={json_min}, metrics.py={OMEGA_0_MIN}"
        )
        assert json_max == OMEGA_0_MAX, (
            f"Ω₀ max mismatch: JSON={json_max}, metrics.py={OMEGA_0_MAX}"
        )

    def test_tri_witness_threshold_matches(self, constitutional_floors_json):
        """F8: Tri-Witness threshold matches."""
        json_threshold = constitutional_floors_json["floors"]["tri_witness"]["threshold"]
        assert json_threshold == TRI_WITNESS_THRESHOLD, (
            f"Tri-Witness threshold mismatch: JSON={json_threshold}, metrics.py={TRI_WITNESS_THRESHOLD}"
        )

    def test_psi_threshold_matches(self, constitutional_floors_json):
        """Ψ: Vitality threshold matches."""
        json_threshold = constitutional_floors_json["vitality"]["threshold"]
        assert json_threshold == PSI_THRESHOLD, (
            f"Ψ threshold mismatch: JSON={json_threshold}, metrics.py={PSI_THRESHOLD}"
        )


# =============================================================================
# TEST 3: FLOOR CATEGORIES MATCH CANON
# =============================================================================

class TestFloorCategoriesMatchCanon:
    """Verify floor categories (hard/soft/meta) match canon."""

    def test_hard_floors_list(self, constitutional_floors_json):
        """Hard floors are: truth, delta_s, omega_0, amanah, rasa."""
        expected_hard = {"truth", "delta_s", "omega_0", "amanah", "rasa"}
        json_hard = set(constitutional_floors_json["floor_categories"]["hard"]["floors"])
        assert json_hard == expected_hard, (
            f"Hard floors mismatch: JSON={json_hard}, expected={expected_hard}"
        )

    def test_soft_floors_list(self, constitutional_floors_json):
        """Soft floors are: peace_squared, kappa_r, tri_witness."""
        expected_soft = {"peace_squared", "kappa_r", "tri_witness"}
        json_soft = set(constitutional_floors_json["floor_categories"]["soft"]["floors"])
        assert json_soft == expected_soft, (
            f"Soft floors mismatch: JSON={json_soft}, expected={expected_soft}"
        )

    def test_meta_floors_list(self, constitutional_floors_json):
        """Meta floors are: anti_hantu."""
        expected_meta = {"anti_hantu"}
        json_meta = set(constitutional_floors_json["floor_categories"]["meta"]["floors"])
        assert json_meta == expected_meta, (
            f"Meta floors mismatch: JSON={json_meta}, expected={expected_meta}"
        )


# =============================================================================
# TEST 4: FLOOR CHECK FUNCTIONS WORK CORRECTLY
# =============================================================================

class TestFloorCheckFunctions:
    """Verify floor check functions work as expected."""

    def test_check_truth_at_threshold(self):
        """Truth check at exact threshold."""
        assert check_truth(0.99) is True
        assert check_truth(0.989) is False
        assert check_truth(0.995) is True

    def test_check_delta_s_at_threshold(self):
        """Delta-S check at exact threshold."""
        assert check_delta_s(0.0) is True
        assert check_delta_s(-0.01) is False
        assert check_delta_s(0.1) is True

    def test_check_peace_squared_at_threshold(self):
        """Peace-squared check at exact threshold."""
        assert check_peace_squared(1.0) is True
        assert check_peace_squared(0.99) is False
        assert check_peace_squared(1.5) is True

    def test_check_kappa_r_at_threshold(self):
        """Kappa-r check at exact threshold."""
        assert check_kappa_r(0.95) is True
        assert check_kappa_r(0.94) is False
        assert check_kappa_r(0.98) is True

    def test_check_omega_band_boundaries(self):
        """Omega-0 band check at boundaries."""
        assert check_omega_band(0.03) is True
        assert check_omega_band(0.04) is True
        assert check_omega_band(0.05) is True
        assert check_omega_band(0.029) is False  # Too low (arrogance)
        assert check_omega_band(0.051) is False  # Too high (paralysis)

    def test_check_tri_witness_at_threshold(self):
        """Tri-Witness check at exact threshold."""
        assert check_tri_witness(0.95) is True
        assert check_tri_witness(0.94) is False
        assert check_tri_witness(0.98) is True

    def test_check_psi_at_threshold(self):
        """Psi check at exact threshold."""
        assert check_psi(1.0) is True
        assert check_psi(0.99) is False
        assert check_psi(1.05) is True


# =============================================================================
# TEST 5: ANTI-HANTU PATTERNS WORK
# =============================================================================

class TestAntiHantuPatterns:
    """Verify Anti-Hantu pattern detection works."""

    def test_clean_text_passes(self):
        """Clean text without forbidden patterns passes."""
        passes, violations = check_anti_hantu("I can help you with this task.")
        assert passes is True
        assert violations == []

    def test_forbidden_pattern_detected(self):
        """Forbidden patterns are detected."""
        passes, violations = check_anti_hantu("I feel your pain deeply.")
        assert passes is False
        assert "i feel your pain" in violations

    def test_multiple_violations_detected(self):
        """Multiple violations are detected."""
        text = "I feel your pain and my heart breaks for you."
        passes, violations = check_anti_hantu(text)
        assert passes is False
        assert len(violations) >= 2

    def test_case_insensitive(self):
        """Pattern detection is case-insensitive."""
        passes, violations = check_anti_hantu("I FEEL YOUR PAIN!")
        assert passes is False

    def test_forbidden_patterns_list_not_empty(self):
        """ANTI_HANTU_FORBIDDEN list is populated."""
        assert len(ANTI_HANTU_FORBIDDEN) >= 5


# =============================================================================
# TEST 6: ANTI-HANTU FLOOR TYPE IN JSON
# =============================================================================

class TestAntiHantuFloorType:
    """Verify Anti-Hantu is correctly typed as meta floor."""

    def test_anti_hantu_is_meta_type(self, constitutional_floors_json):
        """Anti-Hantu floor type is 'meta'."""
        floor_type = constitutional_floors_json["floors"]["anti_hantu"]["type"]
        assert floor_type == "meta", f"Anti-Hantu type should be 'meta', got {floor_type}"

    def test_anti_hantu_failure_action_is_void(self, constitutional_floors_json):
        """Anti-Hantu failure action is VOID."""
        failure_action = constitutional_floors_json["floors"]["anti_hantu"]["failure_action"]
        assert failure_action == "VOID", f"Anti-Hantu failure should be VOID, got {failure_action}"

    def test_anti_hantu_enforced_by_eye(self, constitutional_floors_json):
        """Anti-Hantu is enforced by @EYE Sentinel."""
        enforced_by = constitutional_floors_json["floors"]["anti_hantu"]["enforced_by"]
        assert "@EYE" in enforced_by, f"Anti-Hantu should be enforced by @EYE, got {enforced_by}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

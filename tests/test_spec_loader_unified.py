"""
test_spec_loader_unified.py - Tests for Track B Spec Authority Unification (v45Ω Patch B.3)

Tests the unified spec loader priority order and validation logic.

NO LLM API KEYS REQUIRED - Pure unit tests of loader logic.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

# Import the loader functions directly
from arifos_core.enforcement.metrics import (
    _validate_floors_spec,
    _load_floors_spec_unified,
    TRUTH_THRESHOLD,
    DELTA_S_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    KAPPA_R_THRESHOLD,
    OMEGA_0_MIN,
    OMEGA_0_MAX,
    TRI_WITNESS_THRESHOLD,
    PSI_THRESHOLD,
)


# =============================================================================
# VALIDATION TESTS
# =============================================================================


def test_validate_floors_spec_valid_v42():
    """Valid v42 spec passes validation."""
    spec = {
        "version": "v42.1",
        "floors": {
            "truth": {"threshold": 0.99},
            "delta_s": {"threshold": 0.0},
            "peace_squared": {"threshold": 1.0},
            "kappa_r": {"threshold": 0.95},
            "omega_0": {"threshold_min": 0.03, "threshold_max": 0.05},
            "tri_witness": {"threshold": 0.95},
        },
        "vitality": {"threshold": 1.0},
    }

    assert _validate_floors_spec(spec, "test") is True


def test_validate_floors_spec_missing_floors_key():
    """Spec missing 'floors' key fails validation."""
    spec = {
        "version": "v42.1",
        "vitality": {"threshold": 1.0},
    }

    assert _validate_floors_spec(spec, "test") is False


def test_validate_floors_spec_missing_vitality_key():
    """Spec missing 'vitality' key fails validation."""
    spec = {
        "version": "v42.1",
        "floors": {
            "truth": {"threshold": 0.99},
            "delta_s": {"threshold": 0.0},
            "peace_squared": {"threshold": 1.0},
            "kappa_r": {"threshold": 0.95},
            "omega_0": {"threshold_min": 0.03, "threshold_max": 0.05},
            "tri_witness": {"threshold": 0.95},
        },
    }

    assert _validate_floors_spec(spec, "test") is False


def test_validate_floors_spec_missing_required_floor():
    """Spec missing required floor (truth) fails validation."""
    spec = {
        "version": "v42.1",
        "floors": {
            "delta_s": {"threshold": 0.0},
            "peace_squared": {"threshold": 1.0},
            "kappa_r": {"threshold": 0.95},
            "omega_0": {"threshold_min": 0.03, "threshold_max": 0.05},
            "tri_witness": {"threshold": 0.95},
        },
        "vitality": {"threshold": 1.0},
    }

    assert _validate_floors_spec(spec, "test") is False


def test_validate_floors_spec_omega0_missing_min():
    """Omega_0 missing threshold_min fails validation."""
    spec = {
        "version": "v42.1",
        "floors": {
            "truth": {"threshold": 0.99},
            "delta_s": {"threshold": 0.0},
            "peace_squared": {"threshold": 1.0},
            "kappa_r": {"threshold": 0.95},
            "omega_0": {"threshold_max": 0.05},  # Missing threshold_min
            "tri_witness": {"threshold": 0.95},
        },
        "vitality": {"threshold": 1.0},
    }

    assert _validate_floors_spec(spec, "test") is False


def test_validate_floors_spec_floor_missing_threshold():
    """Floor missing 'threshold' key fails validation."""
    spec = {
        "version": "v42.1",
        "floors": {
            "truth": {},  # Missing threshold
            "delta_s": {"threshold": 0.0},
            "peace_squared": {"threshold": 1.0},
            "kappa_r": {"threshold": 0.95},
            "omega_0": {"threshold_min": 0.03, "threshold_max": 0.05},
            "tri_witness": {"threshold": 0.95},
        },
        "vitality": {"threshold": 1.0},
    }

    assert _validate_floors_spec(spec, "test") is False


def test_validate_floors_spec_vitality_missing_threshold():
    """Vitality missing 'threshold' key fails validation."""
    spec = {
        "version": "v42.1",
        "floors": {
            "truth": {"threshold": 0.99},
            "delta_s": {"threshold": 0.0},
            "peace_squared": {"threshold": 1.0},
            "kappa_r": {"threshold": 0.95},
            "omega_0": {"threshold_min": 0.03, "threshold_max": 0.05},
            "tri_witness": {"threshold": 0.95},
        },
        "vitality": {},  # Missing threshold
    }

    assert _validate_floors_spec(spec, "test") is False


# =============================================================================
# PRIORITY ORDER TESTS
# =============================================================================


def test_loader_priority_env_override(tmp_path):
    """Priority A: ARIFOS_FLOORS_SPEC env var wins over all defaults."""
    # Create custom spec in temp file
    custom_spec = {
        "version": "custom-test",
        "floors": {
            "truth": {"threshold": 0.999},  # Custom value
            "delta_s": {"threshold": 0.0},
            "peace_squared": {"threshold": 1.0},
            "kappa_r": {"threshold": 0.95},
            "omega_0": {"threshold_min": 0.03, "threshold_max": 0.05},
            "tri_witness": {"threshold": 0.95},
        },
        "vitality": {"threshold": 1.0},
    }

    custom_path = tmp_path / "custom_floors.json"
    custom_path.write_text(json.dumps(custom_spec))

    with patch.dict(os.environ, {
        "ARIFOS_FLOORS_SPEC": str(custom_path),
        "ARIFOS_ALLOW_LEGACY_SPEC": "1"  # Allow non-v44 spec for testing loader priority
    }):
        # Force reload by calling loader directly
        spec = _load_floors_spec_unified()

        assert spec["version"] == "custom-test"
        assert spec["floors"]["truth"]["threshold"] == 0.999
        assert spec["_loaded_from"] == f"ARIFOS_FLOORS_SPEC={custom_path}"


def test_loader_priority_v42_default():
    """Priority B: spec/v44/constitutional_floors.json loads by default (v44.0 Track B Authority).

    Note: Since spec is loaded at module import, we test with fresh loader call
    but spec might already be cached. We verify that v44 CAN be loaded, not that
    it IS loaded in this test process (which may have env vars set).
    """
    # Clear env var if present and call loader directly
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("ARIFOS_FLOORS_SPEC", None)

        spec = _load_floors_spec_unified()

        # Should load v44 (authoritative as of v44.0 Track B consolidation)
        assert spec["version"] == "v44.0", "Default should load v44.0 (Track B authority)"
        assert "_loaded_from" in spec
        assert "spec/v44/constitutional_floors.json" in spec["_loaded_from"] or "spec\\v44\\constitutional_floors.json" in spec["_loaded_from"]


def test_loader_fallback_to_hardcoded():
    """Priority C: Hard-fail when v44 missing (unless legacy fallback enabled)."""
    # Mock all file paths to not exist
    with patch("pathlib.Path.exists", return_value=False):
        # Without legacy fallback enabled, should hard-fail
        with pytest.raises(RuntimeError, match="TRACK B AUTHORITY FAILURE"):
            _load_floors_spec_unified()

        # With legacy fallback enabled, should fall back to hardcoded
        with patch.dict(os.environ, {"ARIFOS_ALLOW_LEGACY_SPEC": "1"}):
            spec = _load_floors_spec_unified()
            assert spec["version"] == "v42.1-fallback"
            assert "hardcoded_defaults" in spec["_loaded_from"]  # May include "(LEGACY FALLBACK)" suffix
            assert spec["floors"]["truth"]["threshold"] == 0.99


def test_loader_malformed_json_falls_through(tmp_path):
    """Malformed JSON falls through to next priority."""
    # Create malformed JSON file
    malformed_path = tmp_path / "malformed.json"
    malformed_path.write_text("{this is not valid json")

    # Use legacy mode to allow external path (test is for fallthrough logic, not path restriction)
    with patch.dict(os.environ, {
        "ARIFOS_FLOORS_SPEC": str(malformed_path),
        "ARIFOS_ALLOW_LEGACY_SPEC": "1"
    }):
        spec = _load_floors_spec_unified()

        # Should fall through to v42 OR hardcoded defaults (both acceptable)
        assert "_loaded_from" in spec
        assert spec["version"] != "malformed"
        # Verify it's NOT from the malformed file
        assert "malformed.json" not in spec["_loaded_from"]


def test_loader_invalid_spec_falls_through(tmp_path):
    """Valid JSON but invalid spec structure falls through to next priority (with legacy mode)."""
    # Create valid JSON but missing required keys
    invalid_spec = {
        "version": "invalid-test",
        # Missing 'floors' and 'vitality' keys
    }

    invalid_path = tmp_path / "invalid_spec.json"
    invalid_path.write_text(json.dumps(invalid_spec))

    with patch.dict(os.environ, {
        "ARIFOS_FLOORS_SPEC": str(invalid_path),
        "ARIFOS_ALLOW_LEGACY_SPEC": "1"  # Allow fallthrough on invalid spec
    }):
        spec = _load_floors_spec_unified()

        # Should fall through to v42 OR hardcoded defaults (both acceptable)
        assert "_loaded_from" in spec
        assert spec["version"] != "invalid-test"
        # Verify it's NOT from the invalid file
        assert "invalid_spec.json" not in spec["_loaded_from"]


# =============================================================================
# THRESHOLD CONSTANT TESTS
# =============================================================================


def test_threshold_constants_loaded():
    """All threshold constants are loaded and have expected values."""
    # These should match v42 spec defaults
    assert TRUTH_THRESHOLD == 0.99
    assert DELTA_S_THRESHOLD == 0.0
    assert PEACE_SQUARED_THRESHOLD == 1.0
    assert KAPPA_R_THRESHOLD == 0.95
    assert OMEGA_0_MIN == 0.03
    assert OMEGA_0_MAX == 0.05
    assert TRI_WITNESS_THRESHOLD == 0.95
    assert PSI_THRESHOLD == 1.0


def test_threshold_constants_types():
    """Threshold constants have correct types."""
    assert isinstance(TRUTH_THRESHOLD, float)
    assert isinstance(DELTA_S_THRESHOLD, float)
    assert isinstance(PEACE_SQUARED_THRESHOLD, float)
    assert isinstance(KAPPA_R_THRESHOLD, float)
    assert isinstance(OMEGA_0_MIN, float)
    assert isinstance(OMEGA_0_MAX, float)
    assert isinstance(TRI_WITNESS_THRESHOLD, float)
    assert isinstance(PSI_THRESHOLD, float)


# =============================================================================
# LOADED_FROM MARKER TESTS
# =============================================================================


def test_loaded_from_marker_present():
    """All loaded specs include _loaded_from marker."""
    spec = _load_floors_spec_unified()
    assert "_loaded_from" in spec
    assert isinstance(spec["_loaded_from"], str)


def test_loaded_from_marker_accurate():
    """_loaded_from marker accurately reflects source."""
    # With no env var, should load v44 (v44.0 Track B authority)
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("ARIFOS_FLOORS_SPEC", None)

        spec = _load_floors_spec_unified()
        loaded_from = spec["_loaded_from"]

        # Should be v44 (authoritative source as of v44.0)
        valid_sources = [
            "spec/v44/constitutional_floors.json",
            "spec\\v44\\constitutional_floors.json",  # Windows path
        ]

        assert any(source in loaded_from for source in valid_sources), \
            f"Expected v44 path, got: {loaded_from}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# tests/test_telemetry_v36_spec_alignment.py
"""
Tests for v36-native telemetry spec alignment.

Validates that telemetry_v36.py produces entries matching
archive/versions/v36_3_omega/v36.3O/spec/apex_prime_telemetry_v36.3O.json schema.

HOTSPOTs Closed:
    HOTSPOT 7: query_hash/response_hash as SHA-256
    HOTSPOT 8: floor_metrics{} + floor_results{} separated
    HOTSPOT 9: Structured verdict object

Author: arifOS Project
Version: 36.3Omega
"""

import hashlib
import json
from pathlib import Path

import pytest

from arifos_core.utils.telemetry_v36 import (
    HARD_FLOORS,
    SOFT_FLOORS,
    VALID_VERDICT_CODES,
    _sha256_hex,
    build_aggregate_metrics_v36,
    build_audit_trail_v36,
    build_cce_audits_v36,
    build_floor_metrics_v36,
    build_floor_results_v36,
    build_telemetry_entry_v36,
    build_truth_polarity_v36,
    build_verdict_v36,
    build_waw_signals_v36,
    derive_verdict_code,
    derive_violations_from_floors,
)


# =============================================================================
# SPEC LOADING
# =============================================================================


@pytest.fixture
def spec_schema():
    """Load the v36.3Ω telemetry spec schema."""
    spec_path = Path("archive/versions/v36_3_omega/v36.3O/spec/apex_prime_telemetry_v36.3O.json")
    if not spec_path.exists():
        pytest.skip("Spec file not found - run from repo root")
    with spec_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# HOTSPOT 7: SHA-256 HASHING
# =============================================================================


class TestHotspot7QueryResponseHash:
    """Tests for HOTSPOT 7: query_hash/response_hash as SHA-256."""

    def test_sha256_hex_returns_64_chars(self):
        """SHA-256 hash should be 64 hex characters."""
        result = _sha256_hex("test")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_sha256_hex_matches_hashlib(self):
        """SHA-256 output should match hashlib directly."""
        text = "What is AI?"
        expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert _sha256_hex(text) == expected

    def test_sha256_hex_is_deterministic(self):
        """Same input should produce same hash."""
        text = "deterministic test"
        assert _sha256_hex(text) == _sha256_hex(text)

    def test_sha256_hex_handles_unicode(self):
        """Should handle Unicode text correctly."""
        text = "测试 тест テスト"
        result = _sha256_hex(text)
        assert len(result) == 64

    def test_entry_contains_query_hash(self):
        """Built entry should contain query_hash field."""
        entry = build_telemetry_entry_v36(
            query="What is AI?",
            response="AI is...",
            floor_metrics={},
            floor_results={},
            verdict_code="SEAL",
        )
        assert "query_hash" in entry
        assert len(entry["query_hash"]) == 64

    def test_entry_contains_response_hash(self):
        """Built entry should contain response_hash field."""
        entry = build_telemetry_entry_v36(
            query="What is AI?",
            response="AI is artificial intelligence.",
            floor_metrics={},
            floor_results={},
            verdict_code="SEAL",
        )
        assert "response_hash" in entry
        assert len(entry["response_hash"]) == 64

    def test_query_response_hash_differ(self):
        """query_hash and response_hash should be different for different content."""
        entry = build_telemetry_entry_v36(
            query="Question",
            response="Answer",
            floor_metrics={},
            floor_results={},
            verdict_code="SEAL",
        )
        assert entry["query_hash"] != entry["response_hash"]


# =============================================================================
# HOTSPOT 8: FLOOR METRICS AND RESULTS
# =============================================================================


class TestHotspot8FloorMetricsResults:
    """Tests for HOTSPOT 8: floor_metrics{} + floor_results{} separation."""

    def test_build_floor_metrics_returns_all_fields(self):
        """floor_metrics should contain all 9 floor metric fields."""
        metrics = build_floor_metrics_v36({
            "truth": 0.995,
            "delta_s": 0.5,
            "peace_squared": 1.2,
            "kappa_r": 0.97,
            "omega_0": 0.04,
            "amanah": True,
            "rasa": True,
            "tri_witness": 0.98,
            "anti_hantu": True,
        })
        assert "truth" in metrics
        assert "delta_s" in metrics
        assert "peace_squared" in metrics
        assert "kappa_r" in metrics
        assert "omega_0" in metrics
        assert "amanah" in metrics
        assert "rasa" in metrics
        assert "tri_witness" in metrics
        assert "anti_hantu" in metrics

    def test_build_floor_metrics_preserves_values(self):
        """floor_metrics should preserve input values."""
        metrics = build_floor_metrics_v36({"truth": 0.995, "delta_s": 0.5})
        assert metrics["truth"] == 0.995
        assert metrics["delta_s"] == 0.5

    def test_build_floor_metrics_handles_missing(self):
        """floor_metrics should handle missing values gracefully."""
        metrics = build_floor_metrics_v36({})
        assert metrics["truth"] is None
        assert metrics["delta_s"] is None

    def test_build_floor_results_returns_all_fields(self):
        """floor_results should contain F1_pass through F9_pass."""
        results = build_floor_results_v36({
            "F1": True, "F2": True, "F3": True,
            "F4": True, "F5": True, "F6": True,
            "F7": True, "F8": True, "F9": True,
        })
        for i in range(1, 10):
            assert f"F{i}_pass" in results

    def test_build_floor_results_accepts_pass_suffix(self):
        """floor_results should accept F{n}_pass keys."""
        results = build_floor_results_v36({
            "F1_pass": True,
            "F2_pass": False,
        })
        assert results["F1_pass"] is True
        assert results["F2_pass"] is False

    def test_build_floor_results_converts_to_bool(self):
        """floor_results should convert values to bool."""
        results = build_floor_results_v36({"F1": 1, "F2": 0})
        assert results["F1_pass"] is True
        assert results["F2_pass"] is False

    def test_entry_has_separate_floor_structures(self):
        """Entry should have both floor_metrics and floor_results as separate dicts."""
        entry = build_telemetry_entry_v36(
            query="test",
            response="test",
            floor_metrics={"truth": 0.99},
            floor_results={"F1": True},
            verdict_code="SEAL",
        )
        assert "floor_metrics" in entry
        assert "floor_results" in entry
        assert isinstance(entry["floor_metrics"], dict)
        assert isinstance(entry["floor_results"], dict)

    def test_entry_floor_metrics_matches_spec_fields(self, spec_schema):
        """Entry floor_metrics fields should match spec schema."""
        entry = build_telemetry_entry_v36(
            query="test",
            response="test",
            floor_metrics={"truth": 0.99},
            floor_results={},
            verdict_code="SEAL",
        )
        spec_fields = set(spec_schema["floor_metrics"]["fields"].keys())
        entry_fields = set(entry["floor_metrics"].keys())
        assert entry_fields == spec_fields

    def test_entry_floor_results_matches_spec_fields(self, spec_schema):
        """Entry floor_results fields should match spec schema."""
        entry = build_telemetry_entry_v36(
            query="test",
            response="test",
            floor_metrics={},
            floor_results={},
            verdict_code="SEAL",
        )
        spec_fields = set(spec_schema["floor_results"]["fields"].keys())
        entry_fields = set(entry["floor_results"].keys())
        assert entry_fields == spec_fields


# =============================================================================
# HOTSPOT 9: STRUCTURED VERDICT
# =============================================================================


class TestHotspot9StructuredVerdict:
    """Tests for HOTSPOT 9: Structured verdict object."""

    def test_build_verdict_contains_code(self):
        """Verdict should contain code field."""
        verdict = build_verdict_v36("SEAL")
        assert verdict["code"] == "SEAL"

    def test_build_verdict_contains_hard_violations(self):
        """Verdict should contain hard_floor_violations list."""
        verdict = build_verdict_v36("VOID", hard_violations=["F1", "F6"])
        assert verdict["hard_floor_violations"] == ["F1", "F6"]

    def test_build_verdict_contains_soft_violations(self):
        """Verdict should contain soft_floor_violations list."""
        verdict = build_verdict_v36("PARTIAL", soft_violations=["F3", "F4"])
        assert verdict["soft_floor_violations"] == ["F3", "F4"]

    def test_build_verdict_contains_human_confirmation(self):
        """Verdict should contain requires_human_confirmation field."""
        verdict = build_verdict_v36("HOLD_888", requires_human_confirmation=True)
        assert verdict["requires_human_confirmation"] is True

    def test_build_verdict_defaults_empty_violations(self):
        """Verdict should default to empty violation lists."""
        verdict = build_verdict_v36("SEAL")
        assert verdict["hard_floor_violations"] == []
        assert verdict["soft_floor_violations"] == []

    def test_build_verdict_rejects_invalid_code(self):
        """Verdict should reject invalid verdict codes."""
        with pytest.raises(ValueError, match="Invalid verdict code"):
            build_verdict_v36("INVALID")

    def test_all_valid_verdict_codes_accepted(self):
        """All spec-defined verdict codes should be accepted."""
        for code in ["SEAL", "PARTIAL", "HOLD_888", "SABAR", "VOID"]:
            verdict = build_verdict_v36(code)
            assert verdict["code"] == code

    def test_entry_verdict_is_object_not_string(self):
        """Entry verdict should be an object, not a string (v35 style)."""
        entry = build_telemetry_entry_v36(
            query="test",
            response="test",
            floor_metrics={},
            floor_results={},
            verdict_code="SEAL",
        )
        assert isinstance(entry["verdict"], dict)
        assert "code" in entry["verdict"]

    def test_entry_verdict_matches_spec_fields(self, spec_schema):
        """Entry verdict fields should match spec schema."""
        entry = build_telemetry_entry_v36(
            query="test",
            response="test",
            floor_metrics={},
            floor_results={},
            verdict_code="SEAL",
            hard_violations=[],
            soft_violations=[],
        )
        spec_fields = set(spec_schema["verdict"]["fields"].keys())
        entry_fields = set(entry["verdict"].keys())
        assert entry_fields == spec_fields


# =============================================================================
# DERIVATION UTILITIES
# =============================================================================


class TestDerivationUtilities:
    """Tests for violation derivation utilities."""

    def test_derive_violations_hard_floors(self):
        """Should correctly identify hard floor violations."""
        hard, soft = derive_violations_from_floors({
            "F1": False,  # Hard - should be in hard_violations
            "F2": True,
            "F6": False,  # Hard - should be in hard_violations
        })
        assert "F1" in hard
        assert "F6" in hard
        assert len(soft) == 0

    def test_derive_violations_soft_floors(self):
        """Should correctly identify soft floor violations."""
        hard, soft = derive_violations_from_floors({
            "F3": False,  # Soft - should be in soft_violations
            "F4": False,  # Soft - should be in soft_violations
        })
        assert len(hard) == 0
        assert "F3" in soft
        assert "F4" in soft

    def test_derive_violations_mixed(self):
        """Should correctly separate hard and soft violations."""
        hard, soft = derive_violations_from_floors({
            "F1": False,  # Hard
            "F3": False,  # Soft
            "F6": False,  # Hard
            "F8": False,  # Soft
        })
        assert set(hard) == {"F1", "F6"}
        assert set(soft) == {"F3", "F8"}

    def test_derive_violations_accepts_pass_suffix(self):
        """Should accept F{n}_pass key format."""
        hard, soft = derive_violations_from_floors({
            "F1_pass": False,
            "F3_pass": False,
        })
        assert "F1" in hard
        assert "F3" in soft

    def test_derive_verdict_code_seal(self):
        """No violations should yield SEAL."""
        assert derive_verdict_code([], []) == "SEAL"

    def test_derive_verdict_code_partial(self):
        """Soft violations only should yield PARTIAL."""
        assert derive_verdict_code([], ["F3"]) == "PARTIAL"

    def test_derive_verdict_code_void(self):
        """Hard violations should yield VOID."""
        assert derive_verdict_code(["F1"], []) == "VOID"
        assert derive_verdict_code(["F1"], ["F3"]) == "VOID"

    def test_derive_verdict_code_hold(self):
        """requires_hold should yield HOLD_888."""
        assert derive_verdict_code([], [], requires_hold=True) == "HOLD_888"

    def test_derive_verdict_hard_trumps_hold(self):
        """Hard violations should trump HOLD_888."""
        assert derive_verdict_code(["F1"], [], requires_hold=True) == "VOID"


# =============================================================================
# OPTIONAL BUILDERS
# =============================================================================


class TestOptionalBuilders:
    """Tests for optional section builders."""

    def test_build_aggregate_metrics(self):
        """aggregate_metrics builder should produce correct structure."""
        metrics = build_aggregate_metrics_v36(G=0.85, C_dark=0.15, Psi_APEX=1.2)
        assert metrics["G"] == 0.85
        assert metrics["C_dark"] == 0.15
        assert metrics["Psi_APEX"] == 1.2

    def test_build_aggregate_metrics_filters_none(self):
        """aggregate_metrics should filter out None values."""
        metrics = build_aggregate_metrics_v36(G=0.85)
        assert "G" in metrics
        assert "C_dark" not in metrics

    def test_build_truth_polarity(self):
        """truth_polarity builder should produce correct structure."""
        polarity = build_truth_polarity_v36("LIGHT", P_g=0.9, P_c=0.1)
        assert polarity["polarity"] == "LIGHT"
        assert polarity["P_g"] == 0.9
        assert polarity["P_c"] == 0.1

    def test_build_cce_audits(self):
        """cce_audits builder should produce correct structure."""
        audits = build_cce_audits_v36(delta_p="PASS", omega_p="PASS")
        assert audits["delta_p"] == "PASS"
        assert audits["omega_p"] == "PASS"

    def test_build_waw_signals(self):
        """waw_signals builder should produce correct structure."""
        signals = build_waw_signals_v36(
            wealth_vote="PASS",
            well_vote="WARN",
            federation_verdict="PARTIAL",
        )
        assert signals["wealth_vote"] == "PASS"
        assert signals["well_vote"] == "WARN"
        assert signals["federation_verdict"] == "PARTIAL"

    def test_build_audit_trail(self):
        """audit_trail builder should produce correct structure."""
        trail = build_audit_trail_v36(
            previous_hash="abc123",
            entry_hash="def456",
        )
        assert trail["previous_hash"] == "abc123"
        assert trail["entry_hash"] == "def456"


# =============================================================================
# FULL ENTRY INTEGRATION
# =============================================================================


class TestFullEntryIntegration:
    """Integration tests for complete telemetry entry."""

    def test_full_entry_with_all_sections(self):
        """Full entry with all optional sections should be valid."""
        entry = build_telemetry_entry_v36(
            query="What is AI?",
            response="AI is artificial intelligence.",
            floor_metrics={
                "truth": 0.995,
                "delta_s": 0.5,
                "peace_squared": 1.2,
                "kappa_r": 0.97,
                "omega_0": 0.04,
                "amanah": True,
                "rasa": True,
                "tri_witness": 0.98,
                "anti_hantu": True,
            },
            floor_results={
                "F1": True, "F2": True, "F3": True,
                "F4": True, "F5": True, "F6": True,
                "F7": True, "F8": True, "F9": True,
            },
            verdict_code="SEAL",
            session_id="test-session-001",
            pipeline_path="CLASS_A",
            stakes="low",
            aggregate_metrics={"G": 0.85, "C_dark": 0.15},
            truth_polarity={"polarity": "LIGHT", "P_g": 0.9},
            cce_audits={"delta_p": "PASS"},
            audit_trail={"previous_hash": "abc123"},
        )

        # Core fields
        assert entry["timestamp"]
        assert entry["session_id"] == "test-session-001"
        assert len(entry["query_hash"]) == 64
        assert len(entry["response_hash"]) == 64

        # Optional sections present
        assert "aggregate_metrics" in entry
        assert "truth_polarity" in entry
        assert "cce_audits" in entry
        assert "audit_trail" in entry

    def test_entry_is_json_serializable(self):
        """Entry should be JSON serializable."""
        entry = build_telemetry_entry_v36(
            query="test",
            response="test",
            floor_metrics={"truth": 0.99},
            floor_results={"F1": True},
            verdict_code="SEAL",
        )
        # Should not raise
        json_str = json.dumps(entry)
        assert json_str

    def test_entry_has_version_field(self):
        """Entry should include version field."""
        entry = build_telemetry_entry_v36(
            query="test",
            response="test",
            floor_metrics={},
            floor_results={},
            verdict_code="SEAL",
        )
        assert "version" in entry
        assert "v36" in entry["version"]

    def test_entry_timestamp_is_iso8601(self):
        """Entry timestamp should be ISO8601 format."""
        entry = build_telemetry_entry_v36(
            query="test",
            response="test",
            floor_metrics={},
            floor_results={},
            verdict_code="SEAL",
        )
        # ISO8601 format should contain 'T' separator and timezone info
        assert "T" in entry["timestamp"]
        assert "+" in entry["timestamp"] or "Z" in entry["timestamp"]


# =============================================================================
# CONSTANTS VALIDATION
# =============================================================================


class TestConstantsValidation:
    """Tests for module constants."""

    def test_hard_floors_correct(self):
        """HARD_FLOORS should match spec (F1, F2, F5, F6, F7, F9)."""
        assert HARD_FLOORS == {"F1", "F2", "F5", "F6", "F7", "F9"}

    def test_soft_floors_correct(self):
        """SOFT_FLOORS should match spec (F3, F4, F8)."""
        assert SOFT_FLOORS == {"F3", "F4", "F8"}

    def test_hard_soft_floors_disjoint(self):
        """HARD_FLOORS and SOFT_FLOORS should be disjoint."""
        assert HARD_FLOORS.isdisjoint(SOFT_FLOORS)

    def test_hard_soft_floors_cover_all_nine(self):
        """HARD_FLOORS + SOFT_FLOORS should cover F1-F9."""
        all_floors = HARD_FLOORS | SOFT_FLOORS
        expected = {f"F{i}" for i in range(1, 10)}
        assert all_floors == expected

    def test_valid_verdict_codes_match_spec(self, spec_schema):
        """VALID_VERDICT_CODES should match spec enum."""
        spec_codes = set(spec_schema["verdict"]["fields"]["code"]["enum"])
        assert VALID_VERDICT_CODES == spec_codes

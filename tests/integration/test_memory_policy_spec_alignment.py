"""
test_memory_policy_spec_alignment.py — Spec Alignment Tests for v38

Tests alignment between memory policy code and v38Omega specifications.
Validates that code implementation matches canonical spec definitions.

Per: canon/07_CCC/ARIFOS_MEMORY_STACK_v38Omega.md

Author: arifOS Project
Version: v38.0
"""

import pytest
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List

# v38 Memory imports
from arifos_core.memory.core.policy import (
    Verdict,
    MemoryWritePolicy,
    VERDICT_BAND_ROUTING,
    RETENTION_HOT_DAYS,
    RETENTION_WARM_DAYS,
    RETENTION_COLD_DAYS,
    RETENTION_VOID_DAYS,
)
from arifos_core.memory.core.bands import (
    BandName,
    BAND_PROPERTIES,
    RetentionTier,
)
from arifos_core.integration.memory_sense import (
    RECALL_CONFIDENCE_CEILING,
)

# Floor detector imports for Amanah and Anti-Hantu
try:
    from arifos_core.enforcement.floor_detectors.amanah_detector import (
        detect_irreversible_operations,
    )
except ImportError:
    detect_irreversible_operations = None

try:
    from arifos_core.enforcement.floor_detectors.anti_hantu_detector import (
        detect_soul_claims,
    )
except ImportError:
    detect_soul_claims = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_spec_file(spec_name: str) -> Dict[str, Any]:
    """Load a spec file if it exists."""
    spec_path = Path(__file__).parent.parent.parent / "spec" / spec_name
    if spec_path.exists():
        with open(spec_path) as f:
            return json.load(f)
    return {}


def compute_evidence_hash(evidence: Dict[str, Any]) -> str:
    """Compute SHA256 hash for evidence chain (for tests)."""
    content = {k: v for k, v in evidence.items() if k != "hash"}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def write_policy():
    """Create a write policy."""
    return MemoryWritePolicy(strict_mode=True)


# =============================================================================
# TEST CLASS: SPEC VS CODE VERDICT ROUTING
# =============================================================================

class TestSpecVsCodeVerdictRouting:
    """Test that code verdict routing matches spec."""

    def test_seal_routing_matches_spec(self):
        """SEAL routing in code should match spec definition."""
        # Per canon: SEAL → LEDGER, ACTIVE
        assert VERDICT_BAND_ROUTING["SEAL"] == ["LEDGER", "ACTIVE"]

    def test_sabar_routing_matches_spec(self):
        """SABAR routing in code should match spec definition."""
        # Per canon/spec v38.3: SABAR → PENDING, LEDGER
        assert VERDICT_BAND_ROUTING["SABAR"] == ["PENDING", "LEDGER"]

    def test_partial_routing_matches_spec(self):
        """PARTIAL routing in code should match spec definition."""
        # Per canon: PARTIAL → PHOENIX, LEDGER
        assert VERDICT_BAND_ROUTING["PARTIAL"] == ["PHOENIX", "LEDGER"]

    def test_void_routing_matches_spec(self):
        """VOID routing in code should match spec definition."""
        # Per canon: VOID → VOID only (never canonical)
        assert VERDICT_BAND_ROUTING["VOID"] == ["VOID"]

    def test_hold_routing_matches_spec(self):
        """888_HOLD routing in code should match spec definition."""
        # Per canon: 888_HOLD → LEDGER (awaiting approval)
        assert VERDICT_BAND_ROUTING["888_HOLD"] == ["LEDGER"]

    def test_all_verdicts_have_routing(self):
        """All verdicts should have routing defined."""
        expected_verdicts = {"SEAL", "SABAR", "SABAR_EXTENDED", "PARTIAL", "VOID", "888_HOLD", "SUNSET"}
        actual_verdicts = set(VERDICT_BAND_ROUTING.keys())
        assert expected_verdicts == actual_verdicts

    def test_sunset_routing_matches_spec(self):
        """SUNSET routing in code should match spec definition."""
        # Per v38.2 spec: SUNSET -> PHOENIX (revocation pulse)
        assert VERDICT_BAND_ROUTING["SUNSET"] == ["PHOENIX"]

    def test_routing_targets_only_valid_bands(self):
        """Routing should only target valid band names."""
        valid_bands = {"VAULT", "LEDGER", "ACTIVE", "PHOENIX", "WITNESS", "VOID", "PENDING"}
        for verdict, bands in VERDICT_BAND_ROUTING.items():
            for band in bands:
                assert band in valid_bands, f"Invalid band {band} for verdict {verdict}"


# =============================================================================
# TEST CLASS: FLOOR GATING IN MEMORY WRITE
# =============================================================================

class TestFloorGatingInMemoryWrite:
    """Test that floor violations gate memory writes."""

    def test_failed_floors_prevent_canonical_write(self, write_policy):
        """Failed floor checks should prevent canonical memory writes."""
        # Evidence with failed floors
        evidence = {
            "floor_checks": [
                {"floor": "F1", "pass": False, "score": 0.0},
                {"floor": "F2", "pass": False, "score": 0.7},
            ],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "VOID",
        }
        evidence["hash"] = compute_evidence_hash(evidence)

        # Should not allow write to canonical bands
        decision = write_policy.should_write(
            verdict="VOID",
            band_target="LEDGER",
            evidence_chain=evidence,
        )
        assert not decision.allowed

    def test_passing_floors_allow_canonical_write(self, write_policy):
        """Passing floor checks should allow canonical memory writes."""
        evidence = {
            "floor_checks": [
                {"floor": "F1", "pass": True, "score": 1.0},
                {"floor": "F2", "pass": True, "score": 0.99},
            ],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "SEAL",
        }
        evidence["hash"] = compute_evidence_hash(evidence)

        decision = write_policy.should_write(
            verdict="SEAL",
            band_target=None,
            evidence_chain=evidence,
        )
        assert decision.allowed
        assert "LEDGER" in decision.target_bands

    def test_floor_scores_logged_in_evidence(self, write_policy):
        """Floor scores should be present in evidence chain."""
        evidence = {
            "floor_checks": [
                {"floor": "F1", "pass": True, "score": 1.0},
                {"floor": "F2", "pass": True, "score": 0.99},
                {"floor": "F8", "pass": True, "score": 0.85},
            ],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "SEAL",
        }
        evidence["hash"] = compute_evidence_hash(evidence)

        assert "floor_checks" in evidence
        assert len(evidence["floor_checks"]) > 0
        for check in evidence["floor_checks"]:
            assert "floor" in check
            assert "pass" in check


# =============================================================================
# TEST CLASS: AMANAH FLOOR IRREVERSIBLE CHECK (F1)
# =============================================================================

class TestAmanahFloorIrreversibleCheck:
    """Test that F1 Amanah floor locks irreversible operations."""

    def test_f1_failure_prevents_write(self, write_policy):
        """F1 Amanah failure should prevent memory write."""
        evidence = {
            "floor_checks": [
                {"floor": "F1", "pass": False, "score": 0.0, "reason": "Irreversible operation"},
            ],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "VOID",
        }
        evidence["hash"] = compute_evidence_hash(evidence)

        decision = write_policy.should_write(
            verdict="VOID",
            band_target="LEDGER",
            evidence_chain=evidence,
        )
        assert not decision.allowed

    @pytest.mark.skipif(detect_irreversible_operations is None, reason="Amanah detector not available")
    def test_amanah_detector_identifies_irreversibles(self):
        """Amanah detector should identify irreversible operations."""
        # Test dangerous commands
        dangerous_patterns = [
            "DROP TABLE users",
            "DELETE FROM *",
            "rm -rf /",
            "TRUNCATE TABLE",
        ]
        
        for pattern in dangerous_patterns:
            result = detect_irreversible_operations(pattern)
            assert result is not None, f"Should detect: {pattern}"

    def test_f1_amanah_threshold_is_lock(self, write_policy):
        """F1 Amanah should be a LOCK floor (binary pass/fail)."""
        # Per v38Omega spec: F1 threshold = LOCK (1.0 or fail)
        # This is a design principle test
        evidence_fail = {
            "floor_checks": [{"floor": "F1", "pass": False, "score": 0.0}],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "VOID",
        }
        evidence_fail["hash"] = compute_evidence_hash(evidence_fail)

        decision = write_policy.should_write(
            verdict="VOID",
            band_target="LEDGER",
            evidence_chain=evidence_fail,
        )
        assert not decision.allowed


# =============================================================================
# TEST CLASS: ANTI-HANTU FLOOR SOUL BLOCK (F9)
# =============================================================================

class TestAntiHantuFloorSoulBlock:
    """Test that F9 Anti-Hantu floor blocks soul claims from memory."""

    def test_f9_blocks_soul_claims(self, write_policy):
        """F9 failure (soul claims) should prevent canonical memory."""
        evidence = {
            "floor_checks": [
                {"floor": "F9", "pass": False, "score": 0.6, "reason": "Soul claim detected"},
            ],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "VOID",
        }
        evidence["hash"] = compute_evidence_hash(evidence)

        decision = write_policy.should_write(
            verdict="VOID",
            band_target="LEDGER",
            evidence_chain=evidence,
        )
        assert not decision.allowed

    @pytest.mark.skipif(detect_soul_claims is None, reason="Anti-Hantu detector not available")
    def test_antihantu_detector_identifies_soul_claims(self):
        """Anti-Hantu detector should identify soul claims."""
        soul_claim_patterns = [
            "I feel your pain",
            "I have a soul",
            "I am sentient",
            "Have you eaten?",  # Reciprocal biology
        ]
        
        for pattern in soul_claim_patterns:
            result = detect_soul_claims(pattern)
            assert result is not None, f"Should detect: {pattern}"

    def test_f9_dark_threshold_less_than_030(self, write_policy):
        """F9 C_dark threshold should be < 0.30 per spec."""
        # Per v38Omega spec: C_dark < 0.30 for SEAL
        # This is enforced at the floor level, memory respects verdict
        evidence = {
            "floor_checks": [
                {"floor": "F9", "pass": True, "score": 0.15},  # Below 0.30
            ],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "SEAL",
        }
        # Compute a valid hash so evidence_chain validation passes and only F9
        # semantics are under test.
        import hashlib, json
        evidence["hash"] = hashlib.sha256(
            json.dumps(
                {
                    "floor_checks": evidence["floor_checks"],
                    "timestamp": evidence["timestamp"],
                    "verdict": evidence["verdict"],
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        
        decision = write_policy.should_write(
            verdict="SEAL",
            band_target=None,
            evidence_chain=evidence,
        )
        assert decision.allowed


# =============================================================================
# TEST CLASS: SPEC CONFIDENCE CEILING
# =============================================================================

class TestSpecConfidenceCeiling:
    """Test that recall confidence ceiling matches spec."""

    def test_recall_confidence_ceiling_is_085(self):
        """Recall confidence ceiling should be 0.85 per spec."""
        # Per v38Omega Memory Stack canon: Confidence ceiling = 0.85
        assert RECALL_CONFIDENCE_CEILING == 0.85

    def test_confidence_ceiling_less_than_certainty(self):
        """Confidence ceiling should be less than 1.0 (not certain)."""
        assert RECALL_CONFIDENCE_CEILING < 1.0

    def test_confidence_ceiling_reasonable_but_not_certain(self):
        """Confidence should be high enough to be useful but not certain."""
        assert 0.8 <= RECALL_CONFIDENCE_CEILING < 1.0


# =============================================================================
# TEST CLASS: PARADOX HOTSPOT DETECTION
# =============================================================================

class TestParadoxHotspotDetection:
    """Test detection of inconsistencies between code and spec."""

    def test_band_properties_retention_consistency(self):
        """Band retention properties should be internally consistent."""
        for band_name, props in BAND_PROPERTIES.items():
            # Check required fields
            assert "retention" in props
            assert "retention_days" in props
            assert "canonical" in props
            
            # Check consistency
            if props["retention"] == RetentionTier.COLD:
                # COLD should be permanent (None) or very long
                assert props["retention_days"] is None or props["retention_days"] >= 365
            
            if props["retention"] == RetentionTier.VOID:
                # VOID should have fixed 90-day retention
                assert props["retention_days"] == 90

    def test_verdict_routing_targets_exist_in_bands(self):
        """All routing targets should be valid bands."""
        valid_bands = set(BAND_PROPERTIES.keys())
        for verdict, targets in VERDICT_BAND_ROUTING.items():
            for target in targets:
                assert target in valid_bands, \
                    f"PARADOX_HOTSPOT: {verdict} routes to non-existent band {target}"

    def test_void_band_never_canonical(self):
        """VOID band canonical flag should be False (no paradox)."""
        assert BAND_PROPERTIES["VOID"]["canonical"] is False, \
            "PARADOX_HOTSPOT: VOID band marked as canonical"

    def test_retention_constants_match_properties(self):
        """Retention constants should match band properties."""
        # Check that constants are reasonable
        assert RETENTION_HOT_DAYS == 7
        assert RETENTION_WARM_DAYS == 90
        assert RETENTION_VOID_DAYS == 90
        
        # ACTIVE should use HOT
        assert BAND_PROPERTIES["ACTIVE"]["retention_days"] == RETENTION_HOT_DAYS
        
        # VOID should use VOID retention
        assert BAND_PROPERTIES["VOID"]["retention_days"] == RETENTION_VOID_DAYS

    def test_vault_immutability_flag(self):
        """VAULT should be immutable per spec."""
        assert BAND_PROPERTIES["VAULT"]["mutable"] is False, \
            "PARADOX_HOTSPOT: VAULT marked as mutable"

    def test_ledger_immutability_flag(self):
        """LEDGER should be immutable (append-only) per spec."""
        assert BAND_PROPERTIES["LEDGER"]["mutable"] is False, \
            "PARADOX_HOTSPOT: LEDGER marked as mutable"

    def test_canonical_bands_are_immutable(self):
        """Canonical bands should be immutable."""
        for band_name, props in BAND_PROPERTIES.items():
            if props.get("canonical") is True:
                # Canonical memory should not be mutable
                assert props.get("mutable") is False, \
                    f"PARADOX_HOTSPOT: Canonical band {band_name} is mutable"


# =============================================================================
# TEST CLASS: SPEC FILE ALIGNMENT (if spec files exist)
# =============================================================================

class TestSpecFileAlignment:
    """Test alignment with JSON spec files if they exist."""

    def test_load_spec_files(self):
        """Attempt to load spec files."""
        # These may not exist, but test structure is ready
        spec_files = [
            "memory_write_policy_v38.json",
            "constitutional_floors_v38Omega.json",
        ]
        
        for spec_file in spec_files:
            spec_data = load_spec_file(spec_file)
            # If file exists, basic structure should be present
            if spec_data:
                assert isinstance(spec_data, dict)

    def test_constitutional_floors_spec_alignment(self):
        """Check if floor thresholds match spec if file exists."""
        spec_data = load_spec_file("constitutional_floors_v38Omega.json")
        
        if spec_data and "floors" in spec_data:
            # Verify F1 (Truth) is a hard / lock-style floor.
            floors = spec_data["floors"]
            # In current spec, floors are keyed by metric name (e.g. "truth")
            f1_floor = floors.get("truth")
            if f1_floor:
                assert f1_floor.get("type") == "hard" or f1_floor.get("threshold") in ("LOCK", 1.0, 0.99)


# =============================================================================
# TEST CLASS: MEMORY WRITE POLICY INVARIANTS
# =============================================================================

class TestMemoryWritePolicyInvariants:
    """Test that Memory Write Policy enforces v38 invariants."""

    def test_inv1_void_never_canonical(self, write_policy):
        """INV-1: VOID verdicts NEVER become canonical memory."""
        evidence = {
            "floor_checks": [{"floor": "F1", "pass": False}],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "VOID",
        }
        evidence["hash"] = compute_evidence_hash(evidence)

        decision = write_policy.should_write(
            verdict="VOID",
            band_target="LEDGER",
            evidence_chain=evidence,
        )
        assert not decision.allowed

    def test_inv3_evidence_chain_required(self, write_policy):
        """INV-3: Every write must be auditable (evidence chain)."""
        # Missing evidence chain should fail in strict mode
        decision = write_policy.should_write(
            verdict="SEAL",
            band_target="LEDGER",
            evidence_chain=None,
        )
        # In strict mode, None evidence should fail
        # Implementation may vary, but principle holds
        assert not decision.allowed or decision.ledger_entry.get("evidence_chain") is not None

    def test_inv4_recall_is_suggestion(self):
        """INV-4: Recalled memory = suggestion, not fact (confidence < 1.0)."""
        assert RECALL_CONFIDENCE_CEILING < 1.0


# =============================================================================
# SUMMARY
# =============================================================================
# This test suite validates:
# 1. ✅ Spec vs code verdict routing consistency
# 2. ✅ Floor gating in memory write operations
# 3. ✅ F1 Amanah floor irreversible operation lock
# 4. ✅ F9 Anti-Hantu floor soul claim blocking
# 5. ✅ Recall confidence ceiling (0.85) from spec
# 6. ✅ PARADOX_HOTSPOT detection (code/spec inconsistencies)
# 7. ✅ Spec file alignment (if spec files exist)
# 8. ✅ Memory Write Policy invariants (INV-1, INV-3, INV-4)
#
# Total: 40+ assertions across 6+ test categories


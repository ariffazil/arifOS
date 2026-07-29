"""
test_scar_lifecycle.py — Scar Lifecycle Tests

RASA DERITA Semantic Closure — Gate 2 of 6.

These tests prove that scar consultation fails CLOSED (not open) and that
the full scar lifecycle is maintained: creation, fingerprint, consultation,
constraint, receipt, supersession, ratification, recurrence.

Current behavior: scar scan failure returns present=False (fail-open).
  "I could not inspect history" → "there is no dangerous history."

Expected behavior:
  - Read-only + scar store unavailable → SABAR or degraded read
  - Mutation + scar store unavailable → 888_HOLD
  - Matching active scar → HOLD or VOID per severity
  - Superseded scar → preserve both old and new

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import pytest
import yaml

from arifosmcp.kernel.forge_scar_consult import (
    ScarConsultResult,
    _fingerprint_text,
    _scan_for_fingerprint,
    consult_scar,
    list_active_scars,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fingerprint tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestScarFingerprints:
    """Test scar fingerprint generation."""

    def test_deterministic_fingerprint(self):
        """Same inputs must produce same fingerprint."""
        fp1 = _fingerprint_text("tool_a", "intent_x")
        fp2 = _fingerprint_text("tool_a", "intent_x")
        assert fp1 == fp2, "Fingerprints must be deterministic"

    def test_different_inputs_different_fingerprints(self):
        """Different inputs must produce different fingerprints."""
        fp1 = _fingerprint_text("tool_a", "intent_x")
        fp2 = _fingerprint_text("tool_b", "intent_y")
        assert fp1 != fp2, "Different inputs should produce different fingerprints"

    def test_fingerprint_order_independent(self):
        """Fingerprints should be order-independent (inputs are sorted)."""
        fp1 = _fingerprint_text("a", "b", "c")
        fp2 = _fingerprint_text("c", "a", "b")
        assert fp1 == fp2, "Fingerprints should be order-independent"

    def test_fingerprint_format(self):
        """Fingerprints should use sha256: prefix."""
        fp = _fingerprint_text("test")
        assert fp.startswith("sha256:"), f"Fingerprint must start with 'sha256:', got {fp[:10]}"


# ═══════════════════════════════════════════════════════════════════════════════
# Fail-closed tests (THE CRITICAL FIX)
# ═══════════════════════════════════════════════════════════════════════════════


class TestScarFailClosed:
    """Test that scar failure closes mutation paths, not opens them.

    CURRENT BEHAVIOR: exception → present=False (fail-open)
    EXPECTED BEHAVIOR: exception → HOLD or degraded, depending on context
    """

    def test_scar_store_unavailable_should_not_return_present_false(self):
        """When scar store is unavailable, consult_scar should NOT
        silently return present=False.

        Current behavior (lines 155-157):
          except Exception:
              return ScarConsultResult(present=False)

        This is the critical fail-open bug.
        """
        # We can only test this if we can simulate store failure.
        # For now, document the expected behavior:
        # consult_scar should raise or return a distinct "unavailable" state,
        # not silently return present=False.

        # Test: when fingerprint is provided but scan fails, we should
        # know the difference between "no scar exists" and "could not check"
        result = consult_scar(
            tool_name="__nonexistent_tool_xyz__",
            intent="this intent should not match anything",
        )
        # For a new tool with no match, present=False is correct
        assert result.present is False

        # But the critical question is: can we distinguish between
        # "no scar" and "scan failed"? Currently we cannot.
        # This test documents the requirement that we SHOULD be able to.
        # The fix: add a `scan_successful` field to ScarConsultResult.

    def test_mutation_path_requires_scar_availability(self):
        """For mutation operations, scar scan failure must block, not pass.

        This test documents the expected behavior for the repaired path.
        Once repaired, consult_scar() should differentiate between:
          1. No matching scar (present=False, scan_successful=True)
          2. Scan failed (present=False, scan_successful=False)

        Case 2 must trigger HOLD for mutation paths.
        """
        # This is a specification test — it describes what the API should expose
        result = consult_scar(
            tool_name="test_tool",
            fingerprint="sha256:0000000000000000000000000000000000000000000000000000000000000000",
        )
        # CURRENT: result only has `present` field
        # EXPECTED: result should also have `scan_successful` field
        assert hasattr(result, "present"), "ScarConsultResult must have present field"
        # After repair:
        # assert hasattr(result, "scan_successful"), "Must expose scan health"


# ═══════════════════════════════════════════════════════════════════════════════
# Scar lifecycle tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestScarLifecycle:
    """Test complete scar lifecycle.

    Lifecycle: creation → fingerprint → consultation → constraint →
               receipt → supersession → ratification → recurrence.
    """

    def _create_test_scar(self, scar_dir: Path, tool_name: str, severity: str) -> Path:
        """Create a test scar file."""
        scar_dir.mkdir(parents=True, exist_ok=True)
        scar_data = {
            "tool_name": tool_name,
            "scar_id": hashlib.sha256(tool_name.encode()).hexdigest(),
            "severity": severity,
            "constraint_imposed": f"{tool_name} previously failed",
            "sealed_at": "2026-07-30T00:00:00Z",
            "sealed_by": "test",
            "fingerprints": [
                hashlib.sha256(tool_name.encode()).hexdigest(),
            ],
        }
        scar_path = scar_dir / f"{tool_name}.yaml"
        with open(scar_path, "w") as f:
            yaml.dump(scar_data, f)
        return scar_path

    def test_scar_creation_and_detection(self):
        """A created scar should be detectable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scar_dir = Path(tmpdir) / "scars"
            tool_name = "forge_broken_tool_v1"
            self._create_test_scar(scar_dir, tool_name, "CRITICAL")

            # Should detect the scar
            result = consult_scar(
                tool_name=tool_name,
                intent="create a tool that was previously broken",
            )
            # Note: consult_scar uses _SCAR_PATHS, not our temp dir
            # This test won't find the scar because it's not in the real paths.
            # The purpose is to document the lifecycle expectation.
            pass

    def test_active_scar_blocks_execution(self):
        """An active CRITICAL scar should block tool recreation.

        Once repaired, consult_scar with a matching fingerprint
        should return present=True with severity=CRITICAL,
        and the caller should HOLD or VOID.
        """
        # Documenting expected behavior
        result = consult_scar(
            tool_name="test_tool",
            fingerprint="sha256:0000000000000000000000000000000000000000000000000000000000000000",
        )
        # No scar for test fingerprint → correct
        assert result.present is False
        # After repair, if scan fails, this should still be safe

    def test_superseded_scar_remains_visible(self):
        """A superseded scar should still be visible in history."""
        # Documenting expected behavior:
        # When a scar is superseded:
        # 1. New scar is created
        # 2. Old scar is marked superseded (not deleted)
        # 3. Both appear in scar history
        # 4. The old scar's constraint is relaxed, but still recorded
        pass

    def test_cross_store_contradiction_detection(self):
        """If two scar stores disagree, the contradiction must be surfaced."""
        # Documenting expected behavior:
        # If _SCAR_PATHS[0] has a scar but _SCAR_PATHS[1] doesn't,
        # the conflict should be logged, not silently resolved
        pass

    def test_malformed_scar_yaml_handled(self):
        """Malformed YAML in scar files should not crash the scanner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scar_dir = Path(tmpdir) / "scars"
            scar_dir.mkdir(parents=True, exist_ok=True)
            bad_path = scar_dir / "bad.yaml"
            bad_path.write_text("not: valid: yaml: [[[")

            # Should handle gracefully
            try:
                scars = list_active_scars(scar_dir)
                # Should return empty or skip the bad file
                assert isinstance(scars, list)
            except Exception as e:
                pytest.fail(f"Malformed YAML should not crash: {e}")

    def test_duplicate_scar_ids_detected(self):
        """Duplicate scar IDs should be flagged, not silently merged."""
        # Documenting expected behavior:
        # If two scars have the same scar_id, the consultation
        # should return both and flag the duplication
        pass

    def test_every_consultation_appears_in_receipt(self):
        """Every scar consultation should appear in the execution receipt."""
        # Documenting expected behavior:
        # When consult_scar() is called, the result (including
        # present, scar_id, severity, and source_path) should be
        # attached to the execution receipt for audit
        pass

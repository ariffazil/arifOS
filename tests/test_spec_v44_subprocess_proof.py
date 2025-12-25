"""
test_spec_v44_subprocess_proof.py - Subprocess-Based Proof Tests for v44 Authority

PROOF-GRADE tests that verify spec loading behavior in fresh Python processes.
Unlike code inspection tests, these actually execute the loader in isolation
to prove runtime behavior.

Windows-compatible: Uses subprocess.run() with sys.executable.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestConstitutionalFloorsSubprocess:
    """Subprocess-based proof tests for constitutional floors loader."""

    def test_default_load_uses_v44_fresh_process(self):
        """PROOF: Fresh Python process loads spec/v44/constitutional_floors.json by default."""
        # Run in subprocess to bypass module caching
        code = """
import sys
from arifos_core.enforcement.metrics import _FLOORS_SPEC_V38
print(f"VERSION:{_FLOORS_SPEC_V38['version']}")
print(f"LOADED_FROM:{_FLOORS_SPEC_V38.get('_loaded_from', 'UNKNOWN')}")
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"Process failed: {result.stderr}"
        output = result.stdout

        # Verify v44 loaded
        assert "VERSION:v44.0" in output, f"Expected v44.0, got: {output}"
        # Verify loaded from v44 directory (Windows/Unix compatible)
        assert ("spec/v44/constitutional_floors.json" in output or
                "spec\\v44\\constitutional_floors.json" in output), \
                f"Expected v44 path, got: {output}"

    def test_missing_v44_hard_fails_fresh_process(self):
        """PROOF: Missing spec/v44/ causes RuntimeError in fresh process."""
        # Temporarily rename v44 directory to simulate missing spec
        v44_path = Path(__file__).parent.parent / "spec" / "v44"
        v44_backup = Path(__file__).parent.parent / "spec" / "v44_backup_test"

        # Check if v44 exists
        if not v44_path.exists():
            pytest.skip("spec/v44 directory doesn't exist")

        try:
            # Rename v44 to simulate missing
            v44_path.rename(v44_backup)

            # Run loader in subprocess
            code = """
import os
os.environ['ARIFOS_ALLOW_LEGACY_SPEC'] = '0'  # Ensure fail-closed
from arifos_core.enforcement.metrics import _FLOORS_SPEC_V38
print('LOADED')  # Should NOT reach here
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'ARIFOS_ALLOW_LEGACY_SPEC': '0'}
            )

            # Should fail (non-zero exit)
            assert result.returncode != 0, "Should have failed with missing v44"
            # Should contain hard-fail error message
            assert "TRACK B AUTHORITY FAILURE" in result.stderr, \
                f"Expected hard-fail error, got: {result.stderr}"

        finally:
            # Restore v44
            if v44_backup.exists():
                v44_backup.rename(v44_path)

    def test_env_override_loads_custom_spec_fresh_process(self):
        """PROOF: ARIFOS_FLOORS_SPEC env var loads custom spec in fresh process."""
        # Create custom spec file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_spec = {
                "version": "custom-subprocess-test",
                "floors": {
                    "truth": {"threshold": 0.95, "operator": ">=", "type": "hard", "failure_action": "VOID"},
                    "delta_s": {"threshold": 0.0, "operator": ">=", "type": "hard", "failure_action": "VOID"},
                    "peace_squared": {"threshold": 1.0, "operator": ">=", "type": "soft", "failure_action": "PARTIAL"},
                    "kappa_r": {"threshold": 0.95, "operator": ">=", "type": "soft", "failure_action": "PARTIAL"},
                    "omega_0": {"threshold_min": 0.03, "threshold_max": 0.05, "operator": "in_range", "type": "hard", "failure_action": "VOID"},
                    "amanah": {"threshold": True, "operator": "==", "type": "hard", "failure_action": "VOID"},
                    "rasa": {"threshold": True, "operator": "==", "type": "hard", "failure_action": "VOID"},
                    "tri_witness": {"threshold": 0.95, "operator": ">=", "type": "soft", "failure_action": "PARTIAL"},
                    "anti_hantu": {"threshold": True, "operator": "==", "type": "meta", "failure_action": "VOID"}
                },
                "floor_categories": {"hard": {"floors": ["truth"], "failure_verdict": "VOID"}},
                "precedence_order": {"order": []},
                "verdicts": {},
                "vitality": {"threshold": 1.0}
            }
            json.dump(custom_spec, f)
            custom_path = f.name

        try:
            # Run with env override
            code = f"""
import sys
from arifos_core.enforcement.metrics import _FLOORS_SPEC_V38
print(f"VERSION:{{_FLOORS_SPEC_V38['version']}}")
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'ARIFOS_FLOORS_SPEC': custom_path, 'ARIFOS_ALLOW_LEGACY_SPEC': '1'}
            )

            assert result.returncode == 0, f"Process failed: {result.stderr}"
            assert "VERSION:custom-subprocess-test" in result.stdout, \
                f"Expected custom version, got: {result.stdout}"

        finally:
            os.unlink(custom_path)


class TestGeniusMetricsSubprocess:
    """Subprocess-based proof tests for GENIUS metrics loader."""

    def test_default_load_uses_v44_fresh_process(self):
        """PROOF: Fresh Python process loads spec/v44/genius_law.json by default."""
        code = """
from arifos_core.enforcement.genius_metrics import _GENIUS_SPEC_V38
print(f"VERSION:{_GENIUS_SPEC_V38['version']}")
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"Process failed: {result.stderr}"
        assert "VERSION:v44.0" in result.stdout, f"Expected v44.0, got: {result.stdout}"

    def test_env_override_works_fresh_process(self):
        """PROOF: ARIFOS_GENIUS_SPEC env var loads custom spec in fresh process."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_spec = {
                "version": "custom-genius-subprocess",
                "verdict_logic": {
                    "constants": {
                        "G_SEAL": 0.80,
                        "G_VOID": 0.50,
                        "PSI_SEAL": 1.00,
                        "PSI_SABAR": 0.95,
                        "CDARK_SEAL": 0.30,
                        "CDARK_WARN": 0.60
                    }
                }
            }
            json.dump(custom_spec, f)
            custom_path = f.name

        try:
            code = """
from arifos_core.enforcement.genius_metrics import _GENIUS_SPEC_V38
print(f"VERSION:{_GENIUS_SPEC_V38['version']}")
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'ARIFOS_GENIUS_SPEC': custom_path, 'ARIFOS_ALLOW_LEGACY_SPEC': '1'}
            )

            assert result.returncode == 0, f"Process failed: {result.stderr}"
            assert "VERSION:custom-genius-subprocess" in result.stdout, \
                f"Expected custom version, got: {result.stdout}"

        finally:
            os.unlink(custom_path)


class TestSessionPhysicsSubprocess:
    """Subprocess-based proof tests for session physics loader."""

    def test_default_load_uses_v44_fresh_process(self):
        """PROOF: Fresh Python process loads spec/v44/session_physics.json by default."""
        code = """
from arifos_core.governance.session_physics import _PHYSICS_SPEC
print(f"VERSION:{_PHYSICS_SPEC['version']}")
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"Process failed: {result.stderr}"
        assert "VERSION:v44.0" in result.stdout, f"Expected v44.0, got: {result.stdout}"

    def test_env_override_works_fresh_process(self):
        """PROOF: ARIFOS_PHYSICS_SPEC env var loads custom spec in fresh process."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_spec = {
                "version": "custom-physics-subprocess",
                "budget_thresholds": {"warn_limit_percent": 70.0, "hard_limit_percent": 90.0},
                "burst_detection": {"turn_rate_threshold_per_min": 50.0, "token_rate_threshold_per_min": 6000.0, "variance_dt_threshold": 0.1},
                "streak_thresholds": {"max_consecutive_failures": 5}
            }
            json.dump(custom_spec, f)
            custom_path = f.name

        try:
            code = """
from arifos_core.governance.session_physics import _PHYSICS_SPEC
print(f"VERSION:{_PHYSICS_SPEC['version']}")
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'ARIFOS_PHYSICS_SPEC': custom_path, 'ARIFOS_ALLOW_LEGACY_SPEC': '1'}
            )

            assert result.returncode == 0, f"Process failed: {result.stderr}"
            assert "VERSION:custom-physics-subprocess" in result.stdout, \
                f"Expected custom version, got: {result.stdout}"

        finally:
            os.unlink(custom_path)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])

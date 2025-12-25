"""
test_spec_v44_schema_enforcement_subprocess.py - Subprocess-Based Schema Enforcement Tests

PROOF-GRADE tests that verify JSON schema validation happens at module load time.
Tests run in fresh Python subprocesses to prove load-time enforcement.

v44.0 Track B Authority: Schema validation must be enforced for all v44 specs.

Test Strategy:
1. Create temporary invalid spec file
2. Set env var to point to invalid spec
3. Run subprocess that imports the module
4. Expect RuntimeError with "TRACK B AUTHORITY FAILURE" or "Schema validation failed"

Windows-compatible: Uses subprocess.run() with sys.executable.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestConstitutionalFloorsSchemaEnforcement:
    """Subprocess-based proof tests for constitutional floors schema enforcement."""

    def test_invalid_spec_missing_required_field_fails_at_load(self):
        """PROOF: Invalid spec (missing 'floors' field) triggers load-time failure."""
        # Create invalid spec (missing required 'floors' field)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            invalid_spec = {
                "version": "v44.0",
                "authority": "Track B (tunable thresholds) governed by Track A canon",
                "locked": True,
                "_status": "AUTHORITATIVE",
                # Missing "floors" key - schema validation should fail
                "verdicts": {},
                "meta": {"created": "2025-01-01", "author": "test", "license": "Apache-2.0"}
            }
            json.dump(invalid_spec, f)
            invalid_path = f.name

        try:
            code = """
import sys
from arifos_core.enforcement.metrics import _FLOORS_SPEC_V38
print('SHOULD NOT REACH HERE')
sys.exit(0)
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'ARIFOS_FLOORS_SPEC': invalid_path, 'ARIFOS_ALLOW_LEGACY_SPEC': '0'}
            )

            # Should fail (non-zero exit code)
            assert result.returncode != 0, f"Should have failed with invalid spec, got stdout: {result.stdout}"

            # Should contain schema validation error
            stderr_lower = result.stderr.lower()
            assert any(phrase in stderr_lower for phrase in [
                "schema validation failed",
                "track b authority failure",
                "required field",
                "missing"
            ]), f"Expected schema validation error, got stderr: {result.stderr}"

        finally:
            os.unlink(invalid_path)

    def test_wrong_type_fails_schema_validation(self):
        """PROOF: Spec with wrong type (string instead of boolean) triggers validation failure."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            invalid_spec = {
                "version": "v44.0",
                "authority": "Track B (tunable thresholds) governed by Track A canon",
                "locked": "yes",  # WRONG TYPE: should be boolean
                "_status": "AUTHORITATIVE",
                "arifos_version": "v44.0",
                "spec_type": "constitutional_floors",
                "description": "Test spec with wrong type",
                "source": "https://example.com",
                "floors": {
                    "truth": {"id": 2, "precedence": 4, "symbol": "Truth", "threshold": 0.99}
                },
                "floor_categories": {},
                "precedence_order": {"description": "test", "order": []},
                "verdicts": {},
                "vitality": {"symbol": "Psi", "threshold": 1.0},
                "meta": {"created": "2025-01-01", "author": "test", "license": "Apache-2.0"}
            }
            json.dump(invalid_spec, f)
            invalid_path = f.name

        try:
            code = """
from arifos_core.enforcement.metrics import _FLOORS_SPEC_V38
print('SHOULD NOT REACH HERE')
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'ARIFOS_FLOORS_SPEC': invalid_path, 'ARIFOS_ALLOW_LEGACY_SPEC': '0'}
            )

            assert result.returncode != 0, f"Should have failed with wrong type, got stdout: {result.stdout}"
            stderr_lower = result.stderr.lower()
            assert any(phrase in stderr_lower for phrase in [
                "type",
                "boolean",
                "track b authority failure"
            ]), f"Expected type error, got stderr: {result.stderr}"

        finally:
            os.unlink(invalid_path)

    def test_valid_v44_spec_attaches_schema_used_marker(self):
        """PROOF: Valid v44 spec loads successfully and attaches _schema_used marker."""
        code = """
from arifos_core.enforcement.metrics import _FLOORS_SPEC_V38
if '_schema_used' in _FLOORS_SPEC_V38:
    print(f"SCHEMA_USED:{_FLOORS_SPEC_V38['_schema_used']}")
else:
    print("SCHEMA_USED:NONE")
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, 'ARIFOS_ALLOW_LEGACY_SPEC': '0'}  # Strict mode
        )

        assert result.returncode == 0, f"Process failed: {result.stderr}"
        # Should have _schema_used marker
        assert "SCHEMA_USED:" in result.stdout, f"Expected _schema_used marker, got: {result.stdout}"
        assert "constitutional_floors.schema.json" in result.stdout, \
            f"Expected schema path in marker, got: {result.stdout}"


class TestGeniusLawSchemaEnforcement:
    """Subprocess-based proof tests for GENIUS LAW schema enforcement."""

    def test_invalid_constants_fails_schema_validation(self):
        """PROOF: GENIUS spec with missing required constants triggers validation failure."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            invalid_spec = {
                "version": "v44.0",
                "authority": "Track B (tunable thresholds) governed by Track A canon",
                "locked": True,
                "_status": "AUTHORITATIVE",
                "arifos_version": "v44.0",
                "spec_type": "genius_law",
                "description": "Test spec with missing constants",
                "source": "https://example.com",
                "verdict_logic": {
                    "constants": {
                        "G_SEAL": 0.80,
                        "G_VOID": 0.50,
                        # Missing: PSI_SEAL, PSI_SABAR, CDARK_SEAL, CDARK_WARN
                    }
                },
                "meta": {"created": "2025-01-01", "author": "test", "license": "Apache-2.0"}
            }
            json.dump(invalid_spec, f)
            invalid_path = f.name

        try:
            code = """
from arifos_core.enforcement.genius_metrics import _GENIUS_SPEC_V38
print('SHOULD NOT REACH HERE')
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'ARIFOS_GENIUS_SPEC': invalid_path, 'ARIFOS_ALLOW_LEGACY_SPEC': '0'}
            )

            assert result.returncode != 0, f"Should have failed with missing constants, got stdout: {result.stdout}"
            stderr_lower = result.stderr.lower()
            assert any(phrase in stderr_lower for phrase in [
                "required",
                "missing",
                "track b authority failure"
            ]), f"Expected required field error, got stderr: {result.stderr}"

        finally:
            os.unlink(invalid_path)

    def test_valid_genius_spec_attaches_schema_used_marker(self):
        """PROOF: Valid GENIUS spec loads successfully and attaches _schema_used marker."""
        code = """
from arifos_core.enforcement.genius_metrics import _GENIUS_SPEC_V38
if '_schema_used' in _GENIUS_SPEC_V38:
    print(f"SCHEMA_USED:{_GENIUS_SPEC_V38['_schema_used']}")
else:
    print("SCHEMA_USED:NONE")
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, 'ARIFOS_ALLOW_LEGACY_SPEC': '0'}  # Strict mode
        )

        assert result.returncode == 0, f"Process failed: {result.stderr}"
        assert "SCHEMA_USED:" in result.stdout, f"Expected _schema_used marker, got: {result.stdout}"
        assert "genius_law.schema.json" in result.stdout, \
            f"Expected schema path in marker, got: {result.stdout}"


class TestSessionPhysicsSchemaEnforcement:
    """Subprocess-based proof tests for session physics schema enforcement."""

    def test_invalid_thresholds_fails_schema_validation(self):
        """PROOF: Session physics spec with missing required thresholds triggers validation failure."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            invalid_spec = {
                "version": "v44.0",
                "authority": "Track B (tunable thresholds) governed by Track A canon",
                "locked": True,
                "_status": "AUTHORITATIVE",
                "arifos_version": "v44.0",
                "spec_type": "session_physics",
                "description": "Test spec with missing thresholds",
                "source": "https://example.com",
                "budget_thresholds": {
                    # Missing: warn_limit_percent, hard_limit_percent
                },
                "burst_detection": {
                    "turn_rate_threshold_per_min": 30.0,
                    "token_rate_threshold_per_min": 5000.0,
                    "variance_dt_threshold": 0.05
                },
                "streak_thresholds": {
                    "max_consecutive_failures": 3
                },
                "meta": {"created": "2025-01-01", "author": "test", "license": "Apache-2.0"}
            }
            json.dump(invalid_spec, f)
            invalid_path = f.name

        try:
            code = """
from arifos_core.governance.session_physics import _PHYSICS_SPEC
print('SHOULD NOT REACH HERE')
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'ARIFOS_PHYSICS_SPEC': invalid_path, 'ARIFOS_ALLOW_LEGACY_SPEC': '0'}
            )

            assert result.returncode != 0, f"Should have failed with missing thresholds, got stdout: {result.stdout}"
            stderr_lower = result.stderr.lower()
            assert any(phrase in stderr_lower for phrase in [
                "required",
                "missing",
                "track b authority failure"
            ]), f"Expected required field error, got stderr: {result.stderr}"

        finally:
            os.unlink(invalid_path)

    def test_valid_physics_spec_attaches_schema_used_marker(self):
        """PROOF: Valid session physics spec loads successfully and attaches _schema_used marker."""
        code = """
from arifos_core.governance.session_physics import _PHYSICS_SPEC
if '_schema_used' in _PHYSICS_SPEC:
    print(f"SCHEMA_USED:{_PHYSICS_SPEC['_schema_used']}")
else:
    print("SCHEMA_USED:NONE")
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, 'ARIFOS_ALLOW_LEGACY_SPEC': '0'}  # Strict mode
        )

        assert result.returncode == 0, f"Process failed: {result.stderr}"
        assert "SCHEMA_USED:" in result.stdout, f"Expected _schema_used marker, got: {result.stdout}"
        assert "session_physics.schema.json" in result.stdout, \
            f"Expected schema path in marker, got: {result.stdout}"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])

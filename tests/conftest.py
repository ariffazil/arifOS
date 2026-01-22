"""Pytest configuration and fixtures for arifOS tests"""

import os
from pathlib import Path

import pytest

# Ensure legacy spec bypass is active during import/collection
os.environ.setdefault("ARIFOS_ALLOW_LEGACY_SPEC", "1")
os.environ.setdefault("ARIFOS_PHYSICS_DISABLED", "1")


@pytest.fixture(scope="session", autouse=True)
def disable_physics_globally():
    """
    Disable TEARFRAME Physics globally for all tests (performance optimization).

    Most unit tests don't need physics computation (Ψ, floor checks, etc).
    This fixture runs once per test session and disables physics by default.

    Individual test modules can override this by removing the env var.
    """
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
    yield
    # Cleanup after all tests
    if "ARIFOS_PHYSICS_DISABLED" in os.environ:
        del os.environ["ARIFOS_PHYSICS_DISABLED"]


@pytest.fixture(scope="session", autouse=True)
def allow_legacy_spec_for_tests():
    """
    Allow legacy spec loading for tests (bypasses cryptographic manifest requirement).

    The test environment doesn't require Track B cryptographic authority validation.
    This enables tests to run without MANIFEST.sha256.json file.

    Production code MUST NOT use this bypass - it's test-only.
    """
    os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"
    yield
    # Cleanup after all tests
    if "ARIFOS_ALLOW_LEGACY_SPEC" in os.environ:
        del os.environ["ARIFOS_ALLOW_LEGACY_SPEC"]


# === NEW: Physics override for APEX THEORY tests ===

@pytest.fixture(scope="module")
def enable_physics_for_apex_theory():
    """
    Enable TEARFRAME Physics for APEX THEORY system flow tests.
    
    These tests verify constitutional governance behavior that
    requires active physics computation (Ψ, floor checks, etc).
    
    Scope: module (enable for entire test_system_flows.py file)
    """
    # Store original state
    original_state = os.environ.get("ARIFOS_PHYSICS_DISABLED")
    
    # Enable physics (remove disable flag)
    if "ARIFOS_PHYSICS_DISABLED" in os.environ:
        del os.environ["ARIFOS_PHYSICS_DISABLED"]
    
    yield
    
    # Restore original state
    if original_state is not None:
        os.environ["ARIFOS_PHYSICS_DISABLED"] = original_state
    else:
        os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"


# Skip legacy tests that still reference arifos_core (removed in v49 single-body)
def pytest_ignore_collect(path, config):
    """
    Temporarily disabled. The original logic was too broad and skipped
    necessary source files in the arifos package, causing import errors.
    """
    return False
    # candidate = Path(path)
    # if candidate.suffix != ".py":
    #     return False
    # # Skip legacy suite by default
    # if "tests\\legacy" in str(candidate) or "tests/legacy" in str(candidate):
    #     return True
    # try:
    #     text = candidate.read_text(encoding="utf-8", errors="ignore")
    # except Exception:
    #     return False
    # return "arifos_core" in text

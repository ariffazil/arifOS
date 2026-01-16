"""Pytest configuration and fixtures for arifOS tests"""

import os
import pytest


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

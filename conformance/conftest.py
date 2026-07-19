"""
conformance/conftest.py — Pytest configuration for negative conformance suite
═══════════════════════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI.
"""

import pytest
import json
import urllib.request
import os

ARIFOS_URL = os.environ.get("ARIFOS_URL", "http://localhost:8088")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "wajib: WAJIB conformance test (must never happen)")
    config.addinivalue_line("markers", "xfail_strict: expected to fail until implementation complete")


def pytest_collection_modifyitems(config, items):
    """Mark all conformance tests as wajib."""
    for item in items:
        item.add_marker("wajib")


@pytest.fixture(scope="session")
def kernel_health():
    """Verify kernel is reachable before running conformance suite."""
    try:
        with urllib.request.urlopen(f"{ARIFOS_URL}/health", timeout=5) as resp:
            return json.loads(resp.read())
    except Exception as e:
        pytest.exit(f"Kernel unreachable at {ARIFOS_URL}: {e}")

"""
Metabolic Chain Test Fixtures
═══════════════════════════════════════════════════════════════════════════════════

Minimal fixtures for the metabolic integration test.

The actual MCP clients are created inside each test function (not as fixtures)
because FastMCP's Client context manager has specific lifecycle requirements.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ── Fixture paths ─────────────────────────────────────────────────────────────

GEOX_ROOT = Path("/root/geox")
BOKOR_1_LAS = GEOX_ROOT / "fixtures" / "BOKOR_1_demo.las"


@pytest.fixture(scope="module")
def bokor1_las_path():
    """Path to BOKOR-1 demo LAS file (real Malay Basin well log)."""
    assert BOKOR_1_LAS.exists(), f"Fixture not found: {BOKOR_1_LAS}"
    return str(BOKOR_1_LAS)


@pytest.fixture(scope="module")
def chain_timing():
    """Shared timing dict for measuring total chain latency."""
    return {"start": None, "steps": {}, "end": None}

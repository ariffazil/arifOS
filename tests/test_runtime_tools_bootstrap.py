"""
Legacy bootstrap API tombstone.

The old direct runtime helpers (`init_anchor`, `check_vital`, `audit_rules`,
`arifos_kernel`) were removed from the active KANON runtime surface. Keeping
assertions for those names caused collection-time failures and confused agents
about which API is live.

The current bootstrap and surface contracts are covered by:
- tests/test_canonical.py
- tests/test_surface_lock.py
- tests/runtime/test_runtime_tools_bootstrap.py, if reintroduced against arif_*
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(
    reason="Legacy pre-KANON bootstrap helpers are intentionally retired."
)


def test_legacy_bootstrap_api_retired():
    """Tombstone test kept so the retirement reason is visible in pytest output."""
    assert True

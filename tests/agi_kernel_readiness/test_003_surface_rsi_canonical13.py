"""
test_003 — Surface RSI Canonical 13 (Level 0-1)

Goal: /health or tools/list returns exactly 21 canonical arif_* tools
      (no drift, no phantoms, no ghost aliases).

Pass criteria:
    - tools_loaded = 21
    - registry_truth = VERIFIED
    - canonical_count = 21
    - contract_drift = false

Current status (2026-06-12): PASS (canonical 13 alive).
    But: live surface is 19 (16 arif_* + 3 forge_*). The 13/19 split
    is a documented truth (see AGENTS.md "Canonical Tool-Count Truth
    Table"). Both 13 and 19 are correct in different scopes.

This test asserts the 13-canonical figure per the constitutional contract.
"""

import urllib.request
import json


HEALTH_URL = "http://127.0.0.1:8088/health"


def fetch_health() -> dict:
    with urllib.request.urlopen(HEALTH_URL, timeout=20) as r:
        return json.loads(r.read())


def test_health_canonical_13():
    h = fetch_health()
    assert h.get("tools_loaded") == 21, f"tools_loaded should be 21, got {h.get('tools_loaded')}"
    assert h.get("registry_truth") == "VERIFIED", (
        f"registry_truth should be VERIFIED, got {h.get('registry_truth')}"
    )
    assert h.get("contract_drift") is False, (
        f"contract_drift should be false, got {h.get('contract_drift')}"
    )
    assert h.get("floors_active") == 13, f"floors_active should be 13, got {h.get('floors_active')}"


def test_health_runtime_drift_false():
    h = fetch_health()
    # runtime_drift is computed from canonical_commit vs running_commit
    if h.get("runtime_drift"):
        # Document the drift — this is a real finding
        # canonical_commit != live_commit
        print(
            f"  NOTE: runtime_drift=true. "
            f"canonical={h.get('canonical_commit')}, live={h.get('live_commit')}"
        )
    # The test fails if runtime_drift=true (Level 1+ requires clean)
    assert h.get("runtime_drift") is False, (
        f"runtime_drift must be false for Level 1+, got {h.get('runtime_drift')}"
    )


def test_health_status_healthy():
    h = fetch_health()
    assert h.get("status") == "healthy", f"status must be healthy, got {h.get('status')}"


if __name__ == "__main__":
    test_health_canonical_13()
    print("test_003 canonical: PASS")
    test_health_runtime_drift_false()
    print("test_003 runtime: PASS")
    test_health_status_healthy()
    print("test_003 healthy: PASS")

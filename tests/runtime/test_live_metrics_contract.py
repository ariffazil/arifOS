from __future__ import annotations

from arifosmcp.runtime.server import app
from tests.conftest import SyncASGIClient


def test_live_metrics_contract_exposes_dashboard_fields() -> None:
    client = SyncASGIClient(app)

    response = client.get("/api/live/all")
    assert response.status_code == 200

    payload = response.json()
    assert payload["verdict"] in {"SEAL", "HOLD", "PARTIAL", "VOID"}
    assert payload["tools_loaded"] == 13
    assert payload["floors_active"] == 13
    assert "version" in payload
    assert "source_commit" in payload

    governance = payload["governance"]
    assert governance["system_status"] in {"HEALTHY", "DEGRADED"}
    assert governance["floors_active"] == 13
    assert governance["floors_passing"] + governance["floors_failing"] == 13
    # LAW_SPEC_KEYS retains F-prefix for F1-F9 (backward compat) and L-prefix for L10-L13
    expected_floor_ids = [f"F{i}" for i in range(1, 10)] + [f"L{i}" for i in range(10, 14)]
    assert sorted(governance["floors"], key=lambda fid: int(fid[1:])) == expected_floor_ids

    for law_id, floor_data in governance["floors"].items():
        assert floor_data["name"]
        assert floor_data["status"] in {"pass", "fail"}
        assert isinstance(floor_data["score"], float)

    federation = payload["federation"]
    assert federation["arifos"]["status"] == "active"
    assert federation["arifos"]["verdict"] == payload["verdict"]
    for organ in ("geox", "wealth", "well"):
        assert federation[organ]["status"] in {"active", "offline"}

    machine = payload["machine"]
    for key in ("cpu_percent", "ram_percent", "disk_percent", "uptime_seconds"):
        assert key in machine

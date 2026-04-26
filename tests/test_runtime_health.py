from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


def _load_root_server_module():
    server_path = Path(__file__).resolve().parents[1] / "server.py"
    spec = importlib.util.spec_from_file_location("root_server", server_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runtime_health_endpoint() -> None:
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)

    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "version" in payload


def test_runtime_ready_endpoint() -> None:
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)

    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"pass", "partial"}
    assert "checks" in payload

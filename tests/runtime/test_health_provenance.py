"""
tests/runtime/test_health_provenance.py — Tests for /health deployed_* provenance

F2 TRUTH: /health must answer "which commit is running?" from a receipt written
at deploy time, distinct from BUILD_INFO ("what was compiled into the package?").
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from arifosmcp.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_case_a_deploy_receipt_present(client, tmp_path, monkeypatch):
    """Case A: with latest.json present, /health?nocache=1 returns deployed_* from receipt."""
    receipt_file = tmp_path / "latest.json"
    receipt_data = {
        "commit_sha": "abcd1234ef567890",
        "branch": "feat/provenance-test",
        "build_time": "2026-10-18T12:00:00Z",
        "parity_hash": "1122334455667788",
        "host": "test-host",
        "deployed_by": "test-operator",
    }
    receipt_file.write_text(json.dumps(receipt_data), encoding="utf-8")
    monkeypatch.setenv("ARIFOS_DEPLOY_RECEIPT_PATH", str(receipt_file))

    resp = client.get("/health?nocache=1")
    assert resp.status_code == 200, f"/health returned {resp.status_code}"
    payload = resp.json()

    assert payload.get("deployed_commit") == "abcd1234ef567890"
    assert payload.get("deployed_branch") == "feat/provenance-test"
    assert payload.get("deployed_at") == "2026-10-18T12:00:00Z"


def test_case_b_deploy_receipt_absent(client, tmp_path, monkeypatch):
    """Case B: with latest.json missing, /health?nocache=1 returns UNKNOWN and status 200."""
    nonexistent_file = tmp_path / "does_not_exist.json"
    monkeypatch.setenv("ARIFOS_DEPLOY_RECEIPT_PATH", str(nonexistent_file))

    resp = client.get("/health?nocache=1")
    assert resp.status_code == 200, f"/health returned {resp.status_code}"
    payload = resp.json()

    assert payload.get("deployed_commit") == "UNKNOWN"
    assert payload.get("deployed_branch") == "UNKNOWN"
    assert payload.get("deployed_at") == "UNKNOWN"


def test_case_c_no_shadowing_of_build_info(client, tmp_path, monkeypatch):
    """Case C: deployed_* does NOT shadow git_commit, git_branch, or build_time from BUILD_INFO.

    Regression test: response must contain BOTH 'git_commit' (from BUILD_INFO)
    and 'deployed_commit' (from receipt). They may differ when BUILD_INFO is
    older than the live deploy — that difference is the whole architectural point.
    """
    receipt_file = tmp_path / "latest.json"
    receipt_data = {
        "commit_sha": "deploy_commit_9999",
        "branch": "main",
        "build_time": "2026-10-18T12:30:00Z",
        "parity_hash": "aabbccddeeff",
        "host": "test-host",
        "deployed_by": "test-operator",
    }
    receipt_file.write_text(json.dumps(receipt_data), encoding="utf-8")
    monkeypatch.setenv("ARIFOS_DEPLOY_RECEIPT_PATH", str(receipt_file))

    resp = client.get("/health?nocache=1")
    assert resp.status_code == 200
    payload = resp.json()

    # The existing build-time fields must remain present and unshadowed
    assert "git_commit" in payload
    assert "git_branch" in payload
    assert "build_time" in payload

    # The deployed_* fields must also be present with receipt values
    assert payload.get("deployed_commit") == "deploy_commit_9999"
    assert payload.get("deployed_branch") == "main"
    assert payload.get("deployed_at") == "2026-10-18T12:30:00Z"

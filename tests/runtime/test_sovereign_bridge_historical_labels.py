"""
Tests for the HISTORICAL labelling of legacy /999 verification artifacts
(Phase 4.1 of silk-speed-jericho, 2026-07-25).

The legacy static files under /var/www/html/arif/999 (did-status.json,
seal.json, runtime-snapshot.sha256, key-rotation-2026-05-03.json) are
SUPERSEDED by the canonical live surfaces. sovereign_bridge.load_verification_state
must read them only for backward compatibility and must log them as
HISTORICAL — it must NEVER fake-populate state from the legacy file's
previous value.

These tests run without touching the live webroot: when the files are
absent, the loader must return an empty state without raising. When the
files are present, the loader must read them and log the HISTORICAL
marker.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.core import sovereign_bridge  # noqa: E402


# ── 1) When no legacy artifacts are present, loader returns empty state ──
def test_load_verification_state_empty_when_no_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sovereign_bridge, "_VERIFICATION_DIR", tmp_path)
    state = sovereign_bridge.load_verification_state()
    assert state.did == ""
    assert state.did_status == ""
    assert state.seal_id == ""
    assert state.seal_status == ""
    assert state.runtime_snapshot_hash == ""
    assert state.key_rotation_date == ""


# ── 2) When a legacy did-status.json is present, it is loaded and logged
def test_load_verification_state_loads_did_status_with_historical_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(sovereign_bridge, "_VERIFICATION_DIR", tmp_path)
    (tmp_path / "did-status.json").write_text(
        json.dumps(
            {
                "did": "did:web:arif-fazil.com",
                "id_check": "VERIFIED",
                "public_key_fingerprint": "deadbeefcafebabe",
                "verification_method_id": "did:web:arif-fazil.com#arif-fazil",
            }
        ),
        encoding="utf-8",
    )
    with caplog.at_level(logging.INFO, logger="arifosmcp.core.sovereign_bridge"):
        state = sovereign_bridge.load_verification_state()
    assert state.did == "did:web:arif-fazil.com"
    assert state.did_status == "VERIFIED"
    # The HISTORICAL marker must be present so an operator reading the
    # log knows the source is not the canonical proof surface.
    assert any("HISTORICAL" in rec.message for rec in caplog.records), (
        "loading a legacy did-status.json must emit a HISTORICAL log marker"
    )


# ── 3) Legacy seal.json is also labelled HISTORICAL ──────────────────────
def test_load_verification_state_loads_seal_with_historical_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(sovereign_bridge, "_VERIFICATION_DIR", tmp_path)
    (tmp_path / "seal.json").write_text(
        json.dumps(
            {
                "seal_id": "seal-999-001",
                "status": "active",
                "scope": ["999"],
            }
        ),
        encoding="utf-8",
    )
    with caplog.at_level(logging.INFO, logger="arifosmcp.core.sovereign_bridge"):
        state = sovereign_bridge.load_verification_state()
    assert state.seal_id == "seal-999-001"
    assert state.seal_status == "active"
    assert any("HISTORICAL" in rec.message for rec in caplog.records)


# ── 4) Legacy runtime-snapshot.sha256 is also labelled HISTORICAL ─────────
def test_load_verification_state_loads_runtime_snapshot_with_historical_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(sovereign_bridge, "_VERIFICATION_DIR", tmp_path)
    (tmp_path / "runtime-snapshot.sha256").write_text(
        "a" * 64, encoding="utf-8"
    )
    with caplog.at_level(logging.INFO, logger="arifosmcp.core.sovereign_bridge"):
        state = sovereign_bridge.load_verification_state()
    assert state.runtime_snapshot_hash == "a" * 64
    assert any("HISTORICAL" in rec.message for rec in caplog.records)


# ── 5) Legacy key-rotation-2026-05-03.json is labelled HISTORICAL ────────
def test_load_verification_state_loads_key_rotation_with_historical_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(sovereign_bridge, "_VERIFICATION_DIR", tmp_path)
    (tmp_path / "key-rotation-2026-05-03.json").write_text(
        json.dumps({"rotated_at": "2026-05-03T00:00:00Z"}),
        encoding="utf-8",
    )
    with caplog.at_level(logging.INFO, logger="arifosmcp.core.sovereign_bridge"):
        state = sovereign_bridge.load_verification_state()
    assert state.key_rotation_date == "2026-05-03T00:00:00Z"
    assert any("HISTORICAL" in rec.message for rec in caplog.records)
    # The marker must also mention that no rotation was performed in the
    # Phase 4.1 slice — this is the boundary that protects against
    # future readers assuming the legacy file reflects current state.
    assert any("no rotation" in rec.message.lower() for rec in caplog.records), (
        "the HISTORICAL log entry for key-rotation must also assert that "
        "no rotation was performed in the Phase 4.1 slice."
    )

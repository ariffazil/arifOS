"""Focused tests for reconstructed Observatory truth/provenance behaviors (2026-11-20).

Note: Reconstructed from UNKNOWN-provenance deployed evidence in /opt/arifos/app
(preserved in production-scar-20261120T1154Z) without claiming canonical lineage.
"""

from __future__ import annotations

import json
from pathlib import Path

from arifosmcp.runtime.rest_routes.observatory_routes import (
    _classify_published_floor,
    _finalize_snapshot,
    _predicate_not_enforcement,
    _projected_unit_score,
    _unlinked_seal_census,
)


def test_predicate_not_enforcement_and_projected_score_withheld():
    ont_pred = {"evidence_class": "PREDICATE_PASS", "value_kind": "predicate"}
    assert _predicate_not_enforcement(ont_pred) is True
    assert _projected_unit_score(ont_pred) is True
    assert _classify_published_floor(True, ont_pred) == ("predicate", "predicate", True)

    ont_meter = {
        "evidence_class": "MEASURED",
        "value_kind": "scalar",
        "display_transform": "never projected",
    }
    assert _classify_published_floor(True, ont_meter) == ("pass", "passing", False)
    assert _classify_published_floor(False, ont_meter) == ("fail", "failing", False)


def test_unlinked_seal_census_separates_legacy_from_genuine(tmp_path: Path, monkeypatch):
    vault_file = tmp_path / "SEALED_EVENTS_v2.jsonl"
    rows = [
        {"type": "seal", "id": "s1", "timestamp": "2026-05-01T00:00:00Z"},  # legacy v1 unlinked
        {"type": "seal", "id": "s2", "timestamp": "2026-11-01T00:00:00Z"},  # genuine unlinked
        {"type": "seal", "id": "s3", "timestamp": "2026-11-01T00:01:00Z", "prev_seal_id": "s2"},
    ]
    vault_file.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    monkeypatch.setenv("ARIFOS_VAULT_PATH", str(vault_file))
    census = _unlinked_seal_census()
    assert census["available"] is True
    assert census["chain_length"] == 3
    assert census["unlinked"] == 2
    assert census["legacy_v1_unlinked"] == 1
    assert census["genuine_unlinked"] == 1


def test_f007_signed_not_verified_stays_open(monkeypatch):
    monkeypatch.setattr(
        "arifosmcp.runtime.rest_routes.observatory_routes._enrich_snapshot",
        lambda payload: payload,
    )
    # 1) signed but not verified -> OPEN
    monkeypatch.setattr(
        "arifosmcp.runtime.rest_routes.observatory_routes._sign_observatory_snapshot",
        lambda payload: {"state": "signed", "value": "sig123", "key_id": "k1"},
    )
    out_signed = _finalize_snapshot(
        {"findings": {"findings": [{"id": "F-007", "severity": "HIGH"}]}}
    )
    f007_signed = out_signed["findings"]["findings"][0]
    assert f007_signed["status"] == "OPEN"
    assert "verification=not_run" in f007_signed["evidence"]

    # 2) verified -> RESOLVED
    monkeypatch.setattr(
        "arifosmcp.runtime.rest_routes.observatory_routes._sign_observatory_snapshot",
        lambda payload: {"state": "verified", "value": "sig123", "key_id": "k1"},
    )
    out_ver = _finalize_snapshot({"findings": {"findings": [{"id": "F-007", "severity": "HIGH"}]}})
    assert out_ver["findings"]["findings"][0]["status"] == "RESOLVED"

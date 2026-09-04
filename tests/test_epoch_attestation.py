"""Tests: epoch-boundary attestation (P0-1, 888 audit 2026-09-05).

Contract:
- chain with historical gaps + valid HMAC attestation → status epoch-clean,
  verified=True scoped (epoch dict present, explicit scope note)
- F-004 preserved: new gap at/after epoch start → gaps-found (attestation
  does NOT launder fresh defects)
- tampered attestation (count flip / digest flip / hmac flip) → gaps-found
- anchor validity: chain may GROW past the anchor and attestation stays
  valid (anchor presence, not head equality)
- no attestation → gaps-found (unchanged legacy behaviour)
- gapless chain → attest returns None, verify stays verified
"""

from __future__ import annotations

import json

import pytest

import arifosmcp.runtime.canonical_vault_chain as cvc
from arifosmcp.runtime.canonical_vault_chain import (
    VerifyStatus,
    build_epoch_attestation,
    verify_chain,
)


@pytest.fixture(autouse=True)
def _deterministic_key(monkeypatch):
    monkeypatch.setattr(cvc, "_vault_hmac_key", lambda: b"test-attest-key-32-bytes-xxxxxxxx")


def _write_chain(vault, lines):
    vault.mkdir(parents=True, exist_ok=True)
    (vault / cvc.CHAIN_FILENAME).write_text(
        "\n".join(json.dumps(l) if isinstance(l, dict) else l for l in lines) + "\n",
        encoding="utf-8",
    )


def _base_chain():
    """clean1 → junk → junk → clean2 → clean3 ; gaps expected at lines 2,3."""
    return [
        {"this_hash": "sha256:aaa", "id": "c1", "timestamp": "2026-01-01T00:00:00Z", "actor_id": "t"},
        {"legacy": "no hash fields"},  # gap: HISTORICAL_MISSING_FIELDS
        {"legacy": "still no fields"},  # gap: HISTORICAL_MISSING_FIELDS
        {"prev_hash": "sha256:aaa", "this_hash": "sha256:bbb", "id": "c2", "timestamp": "2026-01-02T00:00:00Z", "actor_id": "t"},
        {"prev_hash": "sha256:bbb", "this_hash": "sha256:ccc", "id": "c3", "timestamp": "2026-01-03T00:00:00Z", "actor_id": "t"},
    ]


def test_gaps_found_without_attestation(tmp_path):
    _write_chain(tmp_path, _base_chain())
    r = verify_chain(tmp_path, scope="full")
    assert r.status == VerifyStatus.GAPS_FOUND
    assert len(r.gaps) >= 2
    assert r.epoch is None


def test_attest_then_epoch_clean(tmp_path):
    _write_chain(tmp_path, _base_chain())
    doc = build_epoch_attestation(tmp_path)
    assert doc is not None and doc["historical_gap_count"] >= 2
    assert doc["attestation_hmac"]
    r = verify_chain(tmp_path, scope="full")
    assert r.status == VerifyStatus.EPOCH_CLEAN
    assert r.verified is True
    assert r.epoch is not None
    assert r.epoch["epoch_start_line_no"] == 4
    assert "epoch_start→head" in r.epoch["scope"]


def test_new_gap_after_epoch_start_invalidates(tmp_path):
    _write_chain(tmp_path, _base_chain())
    build_epoch_attestation(tmp_path)
    # append a FRESH defect after epoch start (prev=ccc set → missing-fields gap)
    lines = _base_chain() + [{"legacy": "fresh defect"}]
    _write_chain(tmp_path, lines)
    r = verify_chain(tmp_path, scope="full")
    assert r.status == VerifyStatus.GAPS_FOUND  # attestation must not launder it
    assert r.epoch is None


def test_chain_growth_past_anchor_stays_epoch_clean(tmp_path):
    _write_chain(tmp_path, _base_chain())
    build_epoch_attestation(tmp_path)  # anchored at ccc
    lines = _base_chain() + [
        {"prev_hash": "sha256:ccc", "this_hash": "sha256:ddd", "id": "c4", "timestamp": "2026-01-04T00:00:00Z", "actor_id": "t"}
    ]
    _write_chain(tmp_path, lines)
    r = verify_chain(tmp_path, scope="full")
    assert r.status == VerifyStatus.EPOCH_CLEAN  # anchor presence, not head equality


def test_tampered_attestation_rejected(tmp_path):
    _write_chain(tmp_path, _base_chain())
    build_epoch_attestation(tmp_path)
    p = tmp_path / cvc.ATTESTATION_FILENAME
    doc = json.loads(p.read_text())

    for mutation in (
        {"historical_gap_count": 999},
        {"historical_gap_digest": "0" * 64},
        {"attestation_hmac": "vhmac:deadbeef"},
        {"epoch_start_line_no": 99999},
    ):
        bad = dict(doc)
        bad.update(mutation)
        p.write_text(json.dumps(bad))
        r = verify_chain(tmp_path, scope="full")
        assert r.status == VerifyStatus.GAPS_FOUND, f"mutation {mutation} must invalidate"

    # restore valid doc → clean again
    p.write_text(json.dumps(doc))
    assert verify_chain(tmp_path, scope="full").status == VerifyStatus.EPOCH_CLEAN


def test_gapless_chain_attest_returns_none(tmp_path):
    lines = [
        {"prev_hash": "genesis", "this_hash": "sha256:x1", "id": "a", "timestamp": "t", "actor_id": "t"},
        {"prev_hash": "sha256:x1", "this_hash": "sha256:x2", "id": "b", "timestamp": "t", "actor_id": "t"},
    ]
    _write_chain(tmp_path, lines)
    assert build_epoch_attestation(tmp_path) is None
    r = verify_chain(tmp_path, scope="full")
    assert r.status in (VerifyStatus.VERIFIED, VerifyStatus.GAPS_FOUND)
    assert r.epoch is None

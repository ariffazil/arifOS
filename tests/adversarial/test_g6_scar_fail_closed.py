"""
G6 scar consultation — fail-closed contract.

An unreadable scar store is UNKNOWN, never "no scars". Three exits must
return scar_consulted=False, and Stage 12 must convert that into HOLD.

Measured 2026-10-18 (FI-003, KVM8): g6_consult_scar previously returned
True on (a) missing store, (b) non-list payload, (c) read/parse error —
and stage_12_execution_or_hold never read the flag at all, so even a False
verdict changed nothing.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json

from arifosmcp.runtime import forge_preflight as fp


def _consult(tmp_path, monkeypatch, payload=None, *, missing=False):
    target = tmp_path / "scar.json"
    if not missing:
        if payload is None:
            payload = []
        if isinstance(payload, str):
            target.write_text(payload, encoding="utf-8")
        else:
            target.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(fp, "SCAR_DB_PATH", target)
    return fp.g6_consult_scar(
        forge_mode="commit",
        manifest="test-manifest",
        session_id=None,
    )


# ── Store unavailable → fail closed ────────────────────────────────────────


def test_missing_store_fails_closed(tmp_path, monkeypatch):
    consulted, scars, reasons = _consult(tmp_path, monkeypatch, missing=True)
    assert consulted is False
    assert scars and scars[0]["id"] == "SCAR_STORE_UNAVAILABLE"
    assert scars[0]["severity"] == "CRITICAL"
    assert any(r.startswith("E_PREFLIGHT_G6_SCAR_STORE_MISSING") for r in reasons)


def test_non_list_payload_fails_closed(tmp_path, monkeypatch):
    consulted, _scars, reasons = _consult(
        tmp_path, monkeypatch, payload={"oops": "dict"}
    )
    assert consulted is False
    assert any(r.startswith("E_PREFLIGHT_G6_SCAR_STORE_MALFORMED") for r in reasons)


def test_corrupt_json_fails_closed(tmp_path, monkeypatch):
    consulted, _scars, reasons = _consult(tmp_path, monkeypatch, payload="{not json")
    assert consulted is False
    assert any(r.startswith("E_PREFLIGHT_G6_SCAR_ERROR") for r in reasons)


# ── Consulted, no match → still True (distinct from unavailable) ───────────


def test_consulted_no_match_is_true(tmp_path, monkeypatch):
    consulted, scars, reasons = _consult(tmp_path, monkeypatch, payload=[])
    assert consulted is True
    assert scars == []
    assert reasons == []


def test_consulted_with_match_is_true(tmp_path, monkeypatch):
    payload = [
        {
            "id": "SCAR_001",
            "name": "whatever",
            "description": "x",
            "severity": "HIGH",
            "blast_domain": "commit",
        }
    ]
    consulted, scars, _reasons = _consult(tmp_path, monkeypatch, payload=payload)
    assert consulted is True
    assert scars and scars[0]["id"] == "SCAR_001"


# ── Stage 12 must consume the flag ─────────────────────────────────────────


def _stage12(**overrides):
    base = dict(
        session_valid=True,
        actor_bound=True,
        authority_gap_detected=False,
        judge_state_valid=True,
        judge_hash_match=True,
        constitutional_chain_valid=True,
        vault_receipt_valid=True,
        plan_manifest_bound=True,
        human_ack_valid=True,
        replay_detected=False,
        ed25519_verified=True,
        rasa_derita_ok=True,
        scar_consulted=True,
    )
    base.update(overrides)
    return fp.stage_12_execution_or_hold(
        stage_results=base,
        dry_run=False,
        forge_mode="commit",
        plan_id="plan_x",
        vault_entry_id=None,
        session_id=None,
    )


def test_stage12_holds_when_scar_not_consulted():
    gate, reasons = _stage12(scar_consulted=False)
    assert gate == "HOLD"
    assert "E_PREFLIGHT_FINAL_HOLD:scar_not_consulted" in reasons


def test_stage12_passes_when_scar_consulted():
    gate, reasons = _stage12(scar_consulted=True)
    assert gate == "PASS", reasons


def test_stage12_defaults_to_hold_when_flag_missing():
    base = dict(
        session_valid=True,
        actor_bound=True,
        authority_gap_detected=False,
        judge_state_valid=True,
        judge_hash_match=True,
        constitutional_chain_valid=True,
        vault_receipt_valid=True,
        plan_manifest_bound=True,
        human_ack_valid=True,
        replay_detected=False,
        ed25519_verified=True,
        rasa_derita_ok=True,
        # scar_consulted deliberately absent
    )
    gate, reasons = fp.stage_12_execution_or_hold(
        stage_results=base,
        dry_run=False,
        forge_mode="commit",
        plan_id="plan_x",
        vault_entry_id=None,
        session_id=None,
    )
    assert gate == "HOLD"
    assert "E_PREFLIGHT_FINAL_HOLD:scar_not_consulted" in reasons

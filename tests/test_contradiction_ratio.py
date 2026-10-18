"""Commit 2 — Eureka margin as a FAILING control (F13 judge order 2026-10-18).

Judge canonical state:
  n_act null  -> phi_e UNDECLARED, value null   (and NON_OPERATIONAL work blocks)
  n_act == 0  -> phi_e NOT_APPLICABLE, value null (zero is undefined, not perfect)
  n_act > 0   -> phi_e MEASURED, value = n_resolved / n_act

Wire name: contradiction_resolution_ratio. `phi_e` stays the doctrine alias.
Denominator comes ONLY from the contradiction register (Test E) — never typed
per call. A resolved status without acceptance evidence is rejected (Test F).

Named consumer: eureka_margin gate in arif_init (NON_OPERATIONAL sessions) +
/health `eureka_margin` block. Failure classes killed here: DENOMINATOR_SELF_EDIT,
WAIVER_AS_SUCCESS (the old "no paradoxes -> phiE waived 1.0" comment).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifosmcp.runtime.contradiction_margin import (
    REGISTER_PATH,
    contradiction_margin,
    eureka_margin_gate,
)

VALID_REGISTER = {
    "schema": "arifos.contradiction_register.v1",
    "consumer": "arifosmcp.runtime.contradiction_margin -> /health eureka_margin + arif_init gate",
    "failure_classes": ["DENOMINATOR_SELF_EDIT", "MEASUREMENT_LAUNDERING", "WAIVER_AS_SUCCESS"],
    "entries": [
        {
            "id": "KX-001",
            "title": "FLOOR_SURFACE_DUAL_TRUTH",
            "scope": "system",
            "evidence_pointer": "probe:2026-10-18",
            "acceptance_test": "three agreement probes",
            "owner": "333-AGI",
            "status": "resolved",
            "falsifier": "any floor_passed disagreement reopens KX-001",
            "resolution_evidence": {"witness": "probe 3/3", "at": "2026-10-18T17:55:00Z"},
        },
        {
            "id": "KX-002",
            "title": "GOVERNANCE_SCORE_SCOPE_COLLISION",
            "scope": "system",
            "evidence_pointer": "probe:2026-10-18",
            "acceptance_test": "one G name per scope on the wire",
            "owner": "333-AGI",
            "status": "active",
            "falsifier": "scoped G names published and consumed",
        },
    ],
}


def _reg(tmp_path: Path, entries: list[dict], **meta) -> Path:
    body = {"schema": "arifos.contradiction_register.v1", **meta, "entries": entries}
    p = tmp_path / "reg.json"
    p.write_text(json.dumps(body))
    return p


def test_b_undeclared_margin_blocks_non_operational(tmp_path: Path) -> None:
    missing = tmp_path / "absent.json"
    margin = contradiction_margin(register_path=missing)
    assert margin["n_act"] is None
    assert margin["phi_e"]["status"] == "UNDECLARED"
    assert margin["phi_e"]["value"] is None

    gate = eureka_margin_gate("NON_OPERATIONAL", margin)
    assert gate["execution_permitted"] is False
    assert gate["reason"] == "EUREKA_MARGIN_UNDECLARED"


def test_operational_work_is_not_applicable(tmp_path: Path) -> None:
    margin = contradiction_margin(register_path=tmp_path / "absent.json")
    gate = eureka_margin_gate("OPERATIONAL", margin)
    assert gate["execution_permitted"] is True
    assert gate["phi_e"]["status"] == "NOT_APPLICABLE"
    assert gate["phi_e"]["value"] is None


def test_c_zero_active_is_undefined_not_perfect(tmp_path: Path) -> None:
    entries = [dict(VALID_REGISTER["entries"][0])]  # resolved with evidence
    p = _reg(tmp_path, entries)
    margin = contradiction_margin(register_path=p)
    assert margin["n_act"] == 0
    assert margin["phi_e"]["status"] == "NOT_APPLICABLE"
    assert margin["phi_e"]["value"] is None
    gate = eureka_margin_gate("NON_OPERATIONAL", margin)
    assert gate["execution_permitted"] is True  # declared as zero, not undeclared


def test_measured_ratio_and_wire_alias(tmp_path: Path) -> None:
    p = _reg(tmp_path, VALID_REGISTER["entries"])
    margin = contradiction_margin(register_path=p)
    assert margin["n_act"] == 1
    assert margin["n_resolved"] == 1
    assert margin["phi_e"]["status"] == "MEASURED"
    assert margin["phi_e"]["value"] == pytest.approx(1.0)
    assert margin["contradiction_resolution_ratio"] == margin["phi_e"]["value"]
    assert len(margin["contradiction_register_hash"]) == 64
    assert margin["measured_at"].endswith("Z")


def test_e_denominator_only_from_register(tmp_path: Path) -> None:
    p = _reg(tmp_path, VALID_REGISTER["entries"])
    with pytest.raises(TypeError):
        contradiction_margin(register_path=p, n_act=999)  # type: ignore[call-arg]
    a = contradiction_margin(register_path=p)
    b = contradiction_margin(register_path=p)
    assert a["n_act"] == b["n_act"]
    assert a["contradiction_register_hash"] == b["contradiction_register_hash"]


def test_f_resolution_without_acceptance_evidence_is_rejected(tmp_path: Path) -> None:
    fake = dict(VALID_REGISTER["entries"][0])
    fake["id"] = "KX-009"
    fake.pop("resolution_evidence")
    live = dict(VALID_REGISTER["entries"][1])
    p = _reg(tmp_path, [fake, live])
    margin = contradiction_margin(register_path=p)
    # The status change is rejected: KX-009 stays active, never counted resolved.
    assert margin["n_act"] == 2
    assert margin["n_resolved"] == 0
    assert "KX-009" in margin["rejected_resolutions"]


def test_register_contract_names_consumer_and_failure_classes() -> None:
    """Law 2: a new registry must name its consumer and failure classes."""
    if not Path(REGISTER_PATH).exists():
        pytest.skip("register not installed on this host")
    margin = contradiction_margin(register_path=Path(REGISTER_PATH))
    raw = json.loads(Path(REGISTER_PATH).read_text())
    assert raw.get("consumer"), "register header must name its consumer"
    assert raw.get("failure_classes"), "register header must name failure classes"
    assert margin["register_validation"]["invalid_entries"] == []

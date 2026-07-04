"""
tests/test_marhin_discovery.py — 5-test acceptance gate for MARHIN engine.

Forged 2026-07-04. Mirrors engine._self_check() with stronger assertions.

5 gates:
    1. test_membrane_first            — boundary sensing precedes everything.
    2. test_account_balances          — conservation map marks imbalance.
    3. test_react_only_if_evidence    — irreversible w/o F13 ack blocks.
    4. test_heal_includes_scar        — recurring scar raises threshold.
    5. test_navigate_proves_ratchet   — uncertainty Δ proves improvement.

Plus wiring sanity:
    - test_self_check_passes_5
    - test_eureka_fingerprint_deterministic
    - test_attach_to_event_bus_registers_readonly

Run: pytest tests/test_marhin_discovery.py -v
"""

from __future__ import annotations

import json

import pytest  # noqa: F401 — used implicitly via monkeypatch fixture typing

from arifosmcp.runtime.marhin_discovery import (
    ENGINE_VERSION,
    attach_to_event_bus,
    discover_next_state,
    _self_check,
)


GOOD_STATE = {
    "actor": "ARIF",
    "organ": "arifOS",
    "action_class": "OBSERVE",
    "uncertainty": 0.42,
    "tool_count": 21,
    "unresolved_holds": 0,
    "session_id": "TEST-SESSION-1",
}
GOOD_EVIDENCE = {"sources": ("s1", "s2"), "costs": ("c1",), "at_risk": ()}
GOOD_COOLING = {"cooling_complete": True, "active_shadows": ()}


# ── 5-test acceptance gate ──────────────────────────────────────────────────


def test_membrane_first():
    p = discover_next_state(
        session_state=dict(GOOD_STATE),
        evidence_receipts=dict(GOOD_EVIDENCE),
        skill_contracts=(),
        scar_ledger=(),
        organ_status={},
        cooling_state=dict(GOOD_COOLING),
    )
    assert p.membrane.inside_boundary is True
    assert p.membrane.hold_required is False
    assert p.membrane.route_required is False


def test_account_balances():
    p = discover_next_state(
        session_state=dict(GOOD_STATE),
        evidence_receipts={"sources": ("s1", "s2"), "costs": ("c1",), "at_risk": ()},
        skill_contracts=(),
        scar_ledger=(),
        organ_status={},
        cooling_state=dict(GOOD_COOLING),
    )
    assert p.conservation.balanced is True
    assert p.conservation.at_risk == ()

    # Imbalance: more costs than sources
    p2 = discover_next_state(
        session_state=dict(GOOD_STATE),
        evidence_receipts={
            "sources": ("s1",),
            "costs": ("c1", "c2", "c3"),
            "at_risk": ("energy",),
        },
        skill_contracts=(),
        scar_ledger=(),
        organ_status={},
        cooling_state=dict(GOOD_COOLING),
    )
    assert p2.conservation.balanced is False
    assert "energy" in p2.conservation.at_risk


def test_react_only_if_evidence():
    """Irreversible action without F13 ack must be blocked."""
    p = discover_next_state(
        session_state={
            "actor": "ARIF",
            "organ": "arifOS",
            "action_class": "IRREVERSIBLE",
            "f13_ack": False,
        },
        evidence_receipts=dict(GOOD_EVIDENCE),
        skill_contracts=(),
        scar_ledger=(),
        organ_status={},
        cooling_state=dict(GOOD_COOLING),
    )
    assert "irreversible_without_f13_ack" in p.reaction.blocked_paths
    assert p.reaction.activation_energy_required > 0.5


def test_heal_includes_scar():
    p = discover_next_state(
        session_state=dict(GOOD_STATE),
        evidence_receipts=dict(GOOD_EVIDENCE),
        skill_contracts=(),
        scar_ledger=(
            {"id": "SHD-001", "recurrence_count": 5},
            {"id": "SHD-002", "recurrence_count": 1},
        ),
        organ_status={},
        cooling_state=dict(GOOD_COOLING),
    )
    assert "SHD-001" in p.heal.active_scars
    assert p.heal.threshold_raised is True
    assert any("SHD-001" in t for t in p.heal.repair_targets)


def test_navigate_proves_ratchet():
    """A clean state must produce a proposal where uncertainty goes down
    AND mutation_allowed stays False AND can_auto_apply stays False."""
    p = discover_next_state(
        session_state=dict(GOOD_STATE),
        evidence_receipts=dict(GOOD_EVIDENCE),
        skill_contracts=({"name": "x"},),
        scar_ledger=(),
        organ_status={"geox": "geox"},
        cooling_state=dict(GOOD_COOLING),
    )
    assert p.after["uncertainty"] < p.before["uncertainty"]
    assert p.navigate.can_proceed is True
    assert p.mutation_allowed is False  # G1
    assert p.authority["can_auto_apply"] is False  # G3
    assert p.authority["judge_required"] is True
    assert p.proof and len(p.proof) == 6


# ── Engine wiring sanity ───────────────────────────────────────────────────


def test_self_check_passes_5():
    res = _self_check()
    assert res["module"] == "marhin_discovery"
    assert res["version"] == ENGINE_VERSION
    assert res["tests"] == 5
    assert res["passed"] == 5
    assert res["verdict"] == "OK"
    print(json.dumps(res, indent=2, default=str))


def test_eureka_fingerprint_deterministic():
    p = discover_next_state(
        session_state=dict(GOOD_STATE),
        evidence_receipts=dict(GOOD_EVIDENCE),
        skill_contracts=(),
        scar_ledger=(),
        organ_status={},
        cooling_state=dict(GOOD_COOLING),
    )
    fp1 = p.fingerprint()
    fp2 = p.fingerprint()
    assert fp1 == fp2, "fingerprint must be deterministic (G10)"
    payload = p.to_dict()
    assert payload["mutation_allowed"] is False
    assert payload["engine_version"] == ENGINE_VERSION
    assert len(payload["hard_rules"]) == 10


def test_attach_to_event_bus_registers_readonly():
    class _FakeBus:
        def __init__(self) -> None:
            self.regs: list[tuple[str, str, object]] = []

        def register(self, stage: str, name: str, hook: object) -> None:
            self.regs.append((stage, name, hook))

    bus = _FakeBus()
    attach_to_event_bus(bus)
    assert len(bus.regs) == 1
    stage, name, hook = bus.regs[0]
    assert stage == "scaffold_rebuild"
    assert name == "marhin_discovery"
    assert callable(hook)

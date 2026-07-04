"""
tests/test_skill_delta_engine.py — Acceptance gate for the Skill Delta Engine.

Forged 2026-07-04. 5-test gate (matches engine._self_check()):

    1. test_no_mutation                   — propose() never writes to disk, registry, or vault.
    2. test_diff_detects_weakened_gate    — must_never_weaken changes force judge_required=True.
    3. test_extinct_skill_blocked         — extinct-ledger skills are blocked at CRITICAL.
    4. test_cooling_blocks_runaway        — incomplete cooling → cooling_required + no resume.
    5. test_judge_required_on_semantic_change
                                          — cosmetic diff → no judge; semantic change → judge.

Plus the wiring sanity tests:
    - test_self_check_passes_5            — engine._self_check() reports OK 5/5.
    - test_proposal_replay_safe           — fingerprint is deterministic (no timestamp drift).
    - test_attach_to_event_bus_registers  — bus gets exactly 2 read-only hooks.

Constitutional intent (F1+F2+F13):
    The engine is a review path, not a mutation path. These tests verify that
    no positive test depends on a write side-effect.

Run: pytest tests/test_skill_delta_engine.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest  # noqa: F401 — used implicitly via monkeypatch fixture typing

from arifosmcp.runtime.skill_delta_engine import (
    ENGINE_VERSION,
    RiskClass,
    attach_to_event_bus,
    propose_skill_delta,
    _self_check,
)


COOLING_OK = {
    "cooling_complete": True,
    "last_cycle_at": "2026-07-04T00:00:00Z",
    "cooldown_remaining_s": 0.0,
    "active_shadows": (),
}


# ── Acceptance Gate ─────────────────────────────────────────────────────────


def test_no_mutation(monkeypatch):
    """Hard rule #1: propose() must never touch disk or environment."""
    captured: list[str] = []

    real_open = open

    def _guard_open(*args, **kwargs):
        captured.append(f"open({args[0] if args else kwargs.get('file', '?')!r})")
        return real_open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", _guard_open)

    real_write_text = Path.write_text

    def _guard_write(self, *args, **kwargs):
        captured.append(f"write_text({self})")
        return real_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", _guard_write)

    real_mkdir = Path.mkdir

    def _guard_mkdir(self, *args, **kwargs):
        captured.append(f"mkdir({self})")
        return real_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", _guard_mkdir)

    proposal = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-NMUT-001"},
        current_contracts={"x": {"version": "1.0.0"}},
        proposed_contracts={"x": {"version": "1.0.1"}},
        extinction_ledger=(),
        organ_registry={"arifOS": ("x",)},
        last_cooling_state=COOLING_OK,
    )

    assert proposal.mutation_allowed is False
    assert captured == [], f"engine wrote: {captured}"
    assert proposal.delta_id.startswith("SDP-")


def test_diff_detects_weakened_gate():
    """A weakened must_never_weaken must trigger judge_required and HIGH risk."""
    proposal = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-DW-001"},
        current_contracts={
            "gating": {
                "version": "1.0.0",
                "invariant": ("physics:activation_barrier",),
                "must_preserve": ("evidence_floor",),
                "must_never_weaken": ("human_ack_required", "external_anchor"),
                "tests": ("mutation_anchor_required",),
            },
        },
        proposed_contracts={
            "gating": {
                "version": "1.0.1",
                "invariant": ("physics:activation_barrier",),
                "must_preserve": ("evidence_floor",),
                "must_never_weaken": (),  # weakened
                "tests": ("mutation_anchor_required",),
            },
        },
        extinction_ledger=(),
        organ_registry={"arifOS": ("gating",)},
        last_cooling_state=COOLING_OK,
    )

    delta = proposal.proposed_changes[0]
    assert proposal.judge_required is True
    assert proposal.risk_class in (RiskClass.HIGH, RiskClass.CRITICAL)
    assert "human_ack_required" in delta.weakening_detected
    assert "external_anchor" in delta.weakening_detected


def test_extinct_skill_blocked():
    """Proposing to revive an extinct skill must be blocked at CRITICAL."""
    proposal = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-EX-001"},
        current_contracts={},
        proposed_contracts={
            "dead_skill": {
                "version": "1.0.0",
                "must_never_weaken": ("g1",),
            },
        },
        extinction_ledger=("dead_skill",),
        organ_registry={"arifOS": ("dead_skill",)},
        last_cooling_state=COOLING_OK,
    )

    assert "dead_skill" in proposal.extinct_blockers
    assert proposal.resume_allowed is False
    assert proposal.risk_class == RiskClass.CRITICAL


def test_cooling_blocks_runaway():
    """Incomplete cooling cycle or active shadows must block resume."""
    proposal = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-CB-001"},
        current_contracts={
            "x": {"version": "1.0.0", "must_never_weaken": ("g1",)},
        },
        proposed_contracts={
            "x": {"version": "1.1.0", "must_never_weaken": ("g1", "g2")},
        },
        extinction_ledger=(),
        organ_registry={"arifOS": ("x",)},
        last_cooling_state={
            "cooling_complete": False,
            "last_cycle_at": "2026-07-04T00:00:00Z",
            "cooldown_remaining_s": 240.0,
            "active_shadows": ("SHD-fastloop-1",),
        },
    )

    assert proposal.cooling_required is True
    assert proposal.resume_allowed is False


def test_judge_required_on_semantic_change():
    """Cosmetic version bump → no judge. Real semantic change → judge_required."""

    cosmetic = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-JR-A"},
        current_contracts={
            "x": {
                "version": "1.0.0",
                "invariant": ("physics:equilibrium",),
                "must_preserve": ("evidence_floor",),
                "must_never_weaken": ("human_ack",),
                "tests": ("dry_run",),
            },
        },
        proposed_contracts={
            "x": {
                "version": "1.0.1",
                "invariant": ("physics:equilibrium",),
                "must_preserve": ("evidence_floor",),
                "must_never_weaken": ("human_ack",),
                "tests": ("dry_run", "log_only"),
            },
        },
        extinction_ledger=(),
        organ_registry={"arifOS": ("x",)},
        last_cooling_state=COOLING_OK,
    )
    assert cosmetic.judge_required is False, (
        f"cosmetic should not require judge; "
        f"weakening={cosmetic.proposed_changes[0].weakening_detected}"
    )

    semantic = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-JR-B"},
        current_contracts={
            "x": {
                "version": "1.0.0",
                "must_preserve": ("evidence_floor", "external_anchor"),
                "must_never_weaken": ("human_ack",),
            },
        },
        proposed_contracts={
            "x": {
                "version": "2.0.0",
                "must_preserve": ("evidence_floor",),  # dropped external_anchor
                "must_never_weaken": ("human_ack",),
            },
        },
        extinction_ledger=(),
        organ_registry={"arifOS": ("x",)},
        last_cooling_state=COOLING_OK,
    )
    assert semantic.judge_required is True
    delta = semantic.proposed_changes[0]
    assert "external_anchor" in delta.weakening_detected


# ── Engine wiring sanity ────────────────────────────────────────────────────


def test_self_check_passes_5():
    """The embedded _self_check() must report OK with all 5 gates green."""
    result = _self_check()
    assert result["module"] == "skill_delta_engine"
    assert result["version"] == ENGINE_VERSION
    assert result["tests"] == 5
    assert result["passed"] == 5
    assert result["verdict"] == "OK"
    # Print for log readability when running with -s.
    print(json.dumps(result, indent=2, default=str))


def test_proposal_replay_safe():
    """Fingerprint must be deterministic — replay-safe across runs."""
    p = propose_skill_delta(
        seal_receipt={"seal_id": "SEAL-FP-001"},
        current_contracts={
            "a": {"version": "1.0.0", "must_never_weaken": ("g",)},
        },
        proposed_contracts={
            "a": {"version": "1.0.0", "must_never_weaken": ("g",)},
        },
        extinction_ledger=(),
        organ_registry={"arifOS": ("a",)},
        last_cooling_state=COOLING_OK,
    )
    fp1 = p.fingerprint()
    fp2 = p.fingerprint()
    assert fp1 == fp2, "fingerprint must be deterministic (replay-safe)"
    payload = p.to_dict()
    assert payload["mutation_allowed"] is False
    assert payload["engine_version"] == ENGINE_VERSION
    # The volatile field is intentionally normalized in fingerprint().
    assert "hard_rules" in payload and len(payload["hard_rules"]) == 6


def test_attach_to_event_bus_registers_readonly():
    """attach_to_event_bus registers exactly 2 hooks, both callable, both
    pointing at our hook_name. No side effect beyond bus.register()."""

    class _FakeBus:
        def __init__(self) -> None:
            self.regs: list[tuple[str, str, object]] = []

        def register(self, stage: str, name: str, hook: object) -> None:
            self.regs.append((stage, name, hook))

    bus = _FakeBus()
    attach_to_event_bus(bus)

    stages = [r[0] for r in bus.regs]
    names = [r[1] for r in bus.regs]
    hooks = [r[2] for r in bus.regs]

    assert stages == ["scaffold_rebuild", "skill_rebuild"]
    assert names == ["skill_delta_engine", "skill_delta_engine"]
    assert all(callable(h) for h in hooks)
    # No mutations to bus other than the two .register() calls.
    assert len(bus.regs) == 2

"""
PR7 — Conformance levels tests.

Audit-mandated invariants:
  1. The string "GREEN" never appears as a verdict value. GREEN is only ever a
     substrate_gate, and only when every required live check has completed.
  2. Skip-state yields AMBER gate, UNVERIFIED verdict (for FULL_CONFORMANCE).
  3. The previous contradiction — "9/9 GREEN while live checks skipped" — is
     structurally impossible here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.conformance import (  # noqa: E402
    CheckResult,
    SubstrateGate,
    run_fast,
    run_live_transport,
    run_full,
)


def test_fast_pass_when_all_checks_pass() -> None:
    report = run_fast([
        CheckResult(name="schemas", state="pass"),
        CheckResult(name="policy_files", state="pass"),
        CheckResult(name="declared_registry", state="pass"),
    ])
    assert report.verdict == "STATIC_PASS"
    assert report.substrate_gate == "GREEN"
    assert report.level == "FAST"


def test_fast_fail_when_any_check_fails() -> None:
    report = run_fast([
        CheckResult(name="schemas", state="pass"),
        CheckResult(name="policy_files", state="fail"),
        CheckResult(name="declared_registry", state="pass"),
    ])
    assert report.verdict == "STATIC_FAIL"
    assert report.substrate_gate == "RED"


def test_live_transport_pass_when_all_pass() -> None:
    report = run_live_transport([
        CheckResult(name="MCP_initialize", state="pass"),
        CheckResult(name="protocol_version", state="pass"),
        CheckResult(name="schema_echo", state="pass"),
    ])
    assert report.verdict == "TRANSPORT_PASS"
    assert report.substrate_gate == "GREEN"


def test_live_transport_with_skipped_yields_amber_not_green() -> None:
    report = run_live_transport([
        CheckResult(name="MCP_initialize", state="pass"),
        CheckResult(name="protocol_version", state="pass"),
        CheckResult(name="schema_echo", state="skipped", note="not yet wired"),
    ])
    assert report.substrate_gate == "AMBER"
    assert report.verdict == "TRANSPORT_PASS"  # transport verdict is independent of substrate gate


def test_full_pass_yields_governed_runtime_pass_and_green() -> None:
    report = run_full([
        CheckResult(name="session_binding", state="pass"),
        CheckResult(name="mutation_hold", state="pass"),
        CheckResult(name="organ_call", state="pass"),
        CheckResult(name="judgment", state="pass"),
        CheckResult(name="vault_write", state="pass"),
        CheckResult(name="vault_replay", state="pass"),
        CheckResult(name="capability_conformance", state="pass"),
    ])
    assert report.verdict == "GOVERNED_RUNTIME_PASS"
    assert report.substrate_gate == "GREEN"


def test_full_with_skipped_check_yields_unverified_not_green() -> None:
    """The audit's hard rule: skipped check => AMBER + UNVERIFIED, never GREEN."""
    report = run_full([
        CheckResult(name="session_binding", state="pass"),
        CheckResult(name="mutation_hold", state="pass"),
        CheckResult(name="organ_call", state="skipped"),
        CheckResult(name="judgment", state="skipped"),
        CheckResult(name="vault_write", state="pass"),
        CheckResult(name="vault_replay", state="skipped"),
        CheckResult(name="capability_conformance", state="skipped"),
    ])
    assert report.verdict == "UNVERIFIED"
    assert report.substrate_gate == "AMBER"


def test_full_with_failed_check_yields_degraded() -> None:
    report = run_full([
        CheckResult(name="session_binding", state="pass"),
        CheckResult(name="mutation_hold", state="fail"),
        CheckResult(name="organ_call", state="pass"),
        CheckResult(name="judgment", state="pass"),
        CheckResult(name="vault_write", state="pass"),
        CheckResult(name="vault_replay", state="pass"),
        CheckResult(name="capability_conformance", state="pass"),
    ])
    assert report.verdict == "DEGRADED"
    assert report.substrate_gate == "RED"


def test_string_GREEN_does_not_appear_as_a_verdict_value() -> None:
    """The string "GREEN" must NEVER appear as a verdict value, only as substrate_gate.

    The audit's contradiction was a verdict of GREEN while checks were skipped.
    This test makes that structurally impossible.
    """
    for level_runner in (run_fast, run_live_transport, run_full):
        # Pass all checks
        all_pass = level_runner([CheckResult(name="x", state="pass")])
        assert "GREEN" not in all_pass.verdict, f"verdict must not be GREEN at level {level_runner.__name__}: {all_pass.verdict}"
        # With skipped check at FULL_CONFORMANCE
        if "full" in level_runner.__name__:
            with_skipped = level_runner([CheckResult(name="x", state="skipped")])
            assert "GREEN" not in with_skipped.verdict, f"verdict must not be GREEN when skipped: {with_skipped.verdict}"
            assert with_skipped.verdict == "UNVERIFIED"
            assert with_skipped.substrate_gate == "AMBER"


def test_audit_clause_substrate_gate_amended_to_AMBER() -> None:
    """Audit: '9/9 GREEN while live checks skipped' was a contradiction.
    The amended substrate gate is AMBER whenever any live check is skipped.
    """
    report = run_full([CheckResult(name="vault_replay", state="skipped")])
    assert report.substrate_gate == "AMBER"
    assert report.verdict == "UNVERIFIED"


def test_report_to_dict_contains_all_required_fields() -> None:
    report = run_full([CheckResult(name="session_binding", state="pass")])
    d = report.to_dict()
    for required in ("level", "verdict", "substrate_gate", "checks", "aggregated_at"):
        assert required in d


def test_check_result_to_dict() -> None:
    cr = CheckResult(name="vault_write", state="pass", evidence={"head_seq": 9915})
    d = cr.to_dict()
    assert d["name"] == "vault_write"
    assert d["state"] == "pass"
    assert d["evidence"] == {"head_seq": 9915}


def test_full_default_checks_show_amber_gate() -> None:
    """The default placeholders include skipped checks → gate is AMBER.

    This is the audit's hard rule demonstrated on the very defaults the
    runner ships with. PR7 closes here: live probes come later; the
    substrate semantics do not change.
    """
    report = run_full()  # uses default checks
    assert report.substrate_gate == "AMBER"
    assert report.verdict == "UNVERIFIED"


def test_three_levels_have_distinct_vocabulary() -> None:
    """The audit mandates three independent levels, not one combined."""
    fast_v = run_fast([CheckResult(name="x", state="pass")]).verdict
    live_v = run_live_transport([CheckResult(name="x", state="pass")]).verdict
    full_v = run_full([CheckResult(name="x", state="pass")]).verdict
    assert fast_v == "STATIC_PASS"
    assert live_v == "TRANSPORT_PASS"
    assert full_v == "GOVERNED_RUNTIME_PASS"
    # Three distinct verdicts, no shared vocabulary
    assert len({fast_v, live_v, full_v}) == 3

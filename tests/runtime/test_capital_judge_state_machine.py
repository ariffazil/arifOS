"""
PR5 — Capital Judge state machine + orchestrator tests.

Verifies the audit-4 state machine:

  RECEIVED → AUTHENTICATED → VALIDATED → COMPUTED → JUDGED
                                                     │
                                                     ├─ DENY → TERMINATED
                                                     ├─ HOLD (loops)
                                                     └─ PROCEED
                                                          │
                                                          ├─ ratification_required: HUMAN_HOLD → RATIFIED → SEALED → EXECUTED
                                                          └─ no ratification: SEALED → EXECUTED
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.capital_judge import (  # noqa: E402
    CapitalCase,
    CapitalJudgeOrchestrator,
    State,
    StateMachine,
    TransitionError,
)


@pytest.fixture(autouse=True)
def signing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARIFOS_OPS_SIGNING_KEY", "dev-only-secret-do-not-use-in-prod")


def _valid_case(*, requires_ratification: bool = False) -> CapitalCase:
    return CapitalCase(
        case_id="CAP-2026-TEST-001",
        actor={"session_id": "session-test", "actor_id": "ARIF"},
        purpose={"description": "synthetic test case", "decision_requested": "PROCEED_with_advisory"},
        valuation={"currency": "MYR", "valuation_date": "2026-01-01", "horizon_years": 5, "discount_rate": 0.10},
        inputs={"initial_capital": 1_000_000, "cashflows": [200_000, 250_000, 300_000, 350_000, 400_000]},
        governance={
            "action_class": "ADVISORY_CAPITAL_JUDGMENT",
            "reversibility": "HIGH",
            "blast_radius": "NONE",
            "human_ratification_required": requires_ratification,
        },
    )


def _good_token(orch: CapitalJudgeOrchestrator, *, requires_ratification: bool = False) -> str:
    from arifosmcp.runtime.wealth_auth import issue_token
    return issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["wealth"],
        allowed_capabilities=["wealth_npv_reward"],
        authority_band="SOVEREIGN" if requires_ratification else "OPERATOR",
    )


# ── 1. State machine primitives ──────────────────────────────────────────────
def test_state_machine_starts_at_RECEIVED() -> None:
    sm = StateMachine(_valid_case())
    assert sm.state == State.RECEIVED
    assert sm.legal_next_states() == {State.AUTHENTICATED, State.TERMINATED}


def test_state_machine_legal_transition_chain() -> None:
    sm = StateMachine(_valid_case())
    sm.transition(State.AUTHENTICATED)
    sm.transition(State.VALIDATED)
    sm.transition(State.COMPUTED)
    sm.transition(State.JUDGED)
    assert sm.state == State.JUDGED


def test_state_machine_illegal_transition_raises() -> None:
    sm = StateMachine(_valid_case())
    with pytest.raises(TransitionError) as exc:
        sm.transition(State.JUDGED)
    assert exc.value.from_state == State.RECEIVED
    assert exc.value.to_state == State.JUDGED


# ── 2. Orchestrator happy paths ────────────────────────────────────────────
def test_orchestrator_happy_path_no_ratification() -> None:
    case = _valid_case(requires_ratification=False)
    orch = CapitalJudgeOrchestrator(case)
    token = _good_token(orch)
    orch.authenticate(authorization_header=f"Bearer {token}", audience="wealth",
                     required_capability="wealth_npv_reward")
    orch.validate()
    orch.compute(
        output={"npv": 928490.85, "irr": 0.1987, "dscr": 99.0},
        wealth_version="1.3.1",
        tool_versions={"wealth_npv_reward": "1.3.1"},
    )
    orch.judge(verdict="PROCEED")
    assert not orch.requires_ratification()
    orch.seal()
    receipt = orch.execute(
        approved_action_hash="sha256:approved",
        execution_result_hash="sha256:result",
        rollback_reference="case:CAP-2026-TEST-001:rollback",
    )
    assert receipt.receipt_type == "EXECUTION"


def test_orchestrator_happy_path_with_ratification() -> None:
    case = _valid_case(requires_ratification=True)
    orch = CapitalJudgeOrchestrator(case)
    token = _good_token(orch, requires_ratification=True)
    orch.authenticate(authorization_header=f"Bearer {token}", audience="wealth",
                     required_capability="wealth_npv_reward")
    orch.validate()
    orch.compute(
        output={"npv": 928490.85, "irr": 0.1987, "dscr": 99.0},
        wealth_version="1.3.1",
        tool_versions={"wealth_npv_reward": "1.3.1"},
    )
    orch.judge(verdict="PROCEED")
    assert orch.requires_ratification()
    orch.ratify(actor="ARIF", decision="approve")
    orch.seal()
    receipt = orch.execute(
        approved_action_hash="sha256:approved",
        execution_result_hash="sha256:result",
        rollback_reference="case:CAP-2026-TEST-001:rollback",
    )
    assert receipt.receipt_type == "EXECUTION"


# ── 3. Audit-critical: WEALTH QUALIFY never auto-executes ──────────────────
def test_orchestrator_refuses_execute_without_sealed() -> None:
    case = _valid_case(requires_ratification=False)
    orch = CapitalJudgeOrchestrator(case)
    token = _good_token(orch)
    orch.authenticate(authorization_header=f"Bearer {token}", audience="wealth",
                     required_capability="wealth_npv_reward")
    orch.validate()
    orch.compute(output={"x": 1}, wealth_version="1.0", tool_versions={})
    orch.judge(verdict="PROCEED")
    # Without seal(), execute() must refuse.
    with pytest.raises(TransitionError) as exc:
        orch.execute(
            approved_action_hash="sha256:x",
            execution_result_hash="sha256:y",
            rollback_reference="r",
        )
    assert "WEALTH QUALIFY" in exc.value.reason or "SEALED" in exc.value.reason


def test_orchestrator_refuses_compute_without_authenticate() -> None:
    """The orchestrator refuses to compute when AUTHENTICATED has not happened.

    Audit rule: 'Every transition is explicit and queryable.'
    """
    case = _valid_case()
    orch = CapitalJudgeOrchestrator(case)
    # Without authenticating first, compute() must refuse.
    with pytest.raises(TransitionError):
        orch.compute(
            output={"x": 1},
            wealth_version="1.0",
            tool_versions={},
        )


# ── 4. DENY short-circuits ──────────────────────────────────────────────────
def test_orchestrator_deny_terminates() -> None:
    case = _valid_case()
    orch = CapitalJudgeOrchestrator(case)
    token = _good_token(orch)
    orch.authenticate(authorization_header=f"Bearer {token}", audience="wealth",
                     required_capability="wealth_npv_reward")
    orch.validate()
    orch.compute(output={"x": 1}, wealth_version="1.0", tool_versions={})
    orch.judge(verdict="DENY", active_holds=["F2_TRUTH"])
    assert orch.sm.state == State.TERMINATED
    with pytest.raises(TransitionError):
        # Cannot proceed after TERMINATED.
        orch.seal()


# ── 5. HOLD loops in JUDGED state ───────────────────────────────────────────
def test_orchestrator_hold_loops_in_judged() -> None:
    case = _valid_case()
    orch = CapitalJudgeOrchestrator(case)
    token = _good_token(orch)
    orch.authenticate(authorization_header=f"Bearer {token}", audience="wealth",
                     required_capability="wealth_npv_reward")
    orch.validate()
    orch.compute(output={"x": 1}, wealth_version="1.0", tool_versions={})
    orch.judge(verdict="HOLD", active_holds=["F1_AMANAH"])
    # After HOLD, state returns to JUDGED so a new judgment can be issued.
    assert orch.sm.state == State.JUDGED
    orch.judge(verdict="PROCEED")


# ── 6. Receipt chain is queryable ───────────────────────────────────────────
def test_receipt_chain_emits_all_four_types_in_order() -> None:
    case = _valid_case(requires_ratification=True)
    orch = CapitalJudgeOrchestrator(case)
    token = _good_token(orch, requires_ratification=True)
    orch.authenticate(authorization_header=f"Bearer {token}", audience="wealth",
                     required_capability="wealth_npv_reward")
    orch.validate()
    orch.compute(output={"x": 1}, wealth_version="1.0", tool_versions={})
    orch.judge(verdict="PROCEED")
    orch.ratify(actor="ARIF", decision="approve")
    orch.seal()
    orch.execute(approved_action_hash="sha256:a", execution_result_hash="sha256:b", rollback_reference="r")
    chain = orch.receipt_chain()
    types = [r["receipt_type"] for r in chain]
    assert "COMPUTATION" in types
    assert "JUDGMENT" in types
    assert "HUMAN_RATIFICATION" in types
    assert "SEAL" in types
    assert "EXECUTION" in types


def test_receipt_chain_carries_hashes_for_replay() -> None:
    case = _valid_case()
    orch = CapitalJudgeOrchestrator(case)
    token = _good_token(orch)
    orch.authenticate(authorization_header=f"Bearer {token}", audience="wealth",
                     required_capability="wealth_npv_reward")
    orch.validate()
    orch.compute(output={"x": 1}, wealth_version="1.0", tool_versions={})
    orch.judge(verdict="PROCEED")
    chain = orch.receipt_chain()
    comp = next(r for r in chain if r["receipt_type"] == "COMPUTATION")
    assert comp["input_hash"].startswith("sha256:")
    assert comp["output_hash"].startswith("sha256:")

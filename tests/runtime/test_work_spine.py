import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from arifosmcp.runtime import work_spine


@pytest.fixture(autouse=True)
def isolated_spine(monkeypatch, tmp_path):
    work_spine.clear_for_tests()
    monkeypatch.setenv("ARIFOS_WORK_LEDGER", str(tmp_path / "events.jsonl"))
    yield tmp_path / "events.jsonl"
    work_spine.clear_for_tests()


def test_reasoning_budget_holds_and_preserves_partial_result(isolated_spine):
    work_spine.create_work_contract("s1", "unreachable", budgets={"reasoning": {"max_cycles": 2}})
    assert work_spine.consume("s1", "reasoning_cycle")["allowed"]
    assert work_spine.consume("s1", "reasoning_cycle")["allowed"]
    held = work_spine.consume("s1", "reasoning_cycle")

    assert held["allowed"] is False
    assert held["reason"] == "REASONING_BUDGET_EXHAUSTED"
    assert held["snapshot"]["usage"]["reasoning_cycles"] == 2
    assert held["snapshot"]["held"] is True


def test_events_are_append_only_and_hash_chained(isolated_spine):
    work_spine.create_work_contract("s1", "measure work")
    work_spine.consume("s1", "tool_call", name="arif_route")
    events = [json.loads(line) for line in isolated_spine.read_text().splitlines()]

    assert [event["sequence"] for event in events] == [1, 2]
    assert events[1]["prior_hash"] == events[0]["event_hash"]
    schema = json.loads(
        (Path(__file__).parents[2] / "arifosmcp/schemas/runtime_event.schema.json").read_text()
    )
    validator = Draft7Validator(schema)
    assert not list(validator.iter_errors(events[0]))
    assert not list(validator.iter_errors(events[1]))


def test_proposal_requires_evidence_to_be_verified():
    work_spine.create_work_contract("s1", "verify work")
    proposal = work_spine.register_proposal("s1", "code_change", "tests pass", ["pytest"])

    unverified = work_spine.record_verification("s1", proposal["proposal_id"], True, "pytest", [])
    verified = work_spine.record_verification("s1", proposal["proposal_id"], True, "pytest", ["run-1"])

    assert unverified["status"] == "UNVERIFIED"
    assert verified["status"] == "VERIFIED"

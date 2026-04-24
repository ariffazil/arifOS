"""
Canonical rebuild tests — 13 tools, 13 floors.
"""
import pytest
from fastmcp import FastMCP
from fastmcp.server.elicitation import AcceptedElicitation, CancelledElicitation, DeclinedElicitation

from arifosmcp.constitutional_map import CANONICAL_TOOLS, list_canonical_tools
from arifosmcp.prompts import CANONICAL_PROMPTS, register_prompts
from arifosmcp.resources import CANONICAL_RESOURCES, register_resources
from arifosmcp.runtime.floors import check_floors, get_floor_status
from arifosmcp.runtime.tools import (
    IrreversibleConfirmation,
    JudgeCandidateInput,
    _elicit_irreversible_ack,
    _elicit_judge_candidate,
    register_tools,
)
from arifosmcp.tools.session_init import arif_session_init
from arifosmcp.tools.sense_observe import arif_sense_observe
from arifosmcp.tools.vault_seal import arif_vault_seal
from arifosmcp.tools.forge_execute import arif_forge_execute
from arifosmcp.tools.judge_deliberate import arif_judge_deliberate


def test_exactly_13_tools():
    assert len(CANONICAL_TOOLS) == 13


def test_tool_names():
    expected = [
        "arif_session_init",
        "arif_sense_observe",
        "arif_evidence_fetch",
        "arif_mind_reason",
        "arif_kernel_route",
        "arif_reply_compose",
        "arif_memory_recall",
        "arif_heart_critique",
        "arif_gateway_connect",
        "arif_ops_measure",
        "arif_judge_deliberate",
        "arif_vault_seal",
        "arif_forge_execute",
    ]
    assert sorted(list_canonical_tools()) == sorted(expected)


def test_register_tools_matches_canonical_surface():
    mcp = FastMCP("test-arifos")
    registered = register_tools(mcp)
    assert len(registered) == 13
    assert set(registered) == set(CANONICAL_TOOLS)
    assert not any(name.startswith("arifos_") for name in registered)


def test_register_prompts_matches_canonical_prompt_surface():
    mcp = FastMCP("test-arifos-prompts")
    registered = register_prompts(mcp)
    assert tuple(registered) == CANONICAL_PROMPTS


def test_register_resources_matches_canonical_resource_surface():
    mcp = FastMCP("test-arifos-resources")
    registered = register_resources(mcp)
    assert tuple(registered) == CANONICAL_RESOURCES


def test_init_creates_session():
    r = arif_session_init(mode="init", actor_id="arif")
    assert r.status == "OK"
    assert "session_id" in r.result["session"]


def test_vault_holds_without_ack():
    r = arif_vault_seal(mode="seal", payload="test", actor_id="arif")
    assert r.status == "HOLD"
    assert "F01" in r.meta["failed_floors"]


def test_vault_seals_with_ack():
    judge = arif_judge_deliberate(mode="judge", candidate="seal test", actor_id="arif")
    r = arif_vault_seal(
        mode="seal",
        payload="test",
        ack_irreversible=True,
        actor_id="arif",
        constitutional_chain_id=judge.judge_contract.constitutional_chain_id,
        judge_state_hash=judge.judge_contract.state_hash,
    )
    assert r.status == "OK"
    assert "entry_id" in r.result
    assert r.judge_contract is not None
    assert r.result["judge_state_hash"] == judge.judge_contract.state_hash


def test_forge_holds_without_actor():
    r = arif_forge_execute(mode="commit", ack_irreversible=True)
    assert r.status == "HOLD"
    assert "F11" in r.meta["failed_floors"]


def test_injection_guard_blocks():
    r = arif_sense_observe(mode="search", query="rm -rf /", actor_id="arif")
    assert r["status"] == "HOLD"
    assert "F12" in r["meta"]["failed_floors"]


def test_judge_emits_seal():
    r = arif_judge_deliberate(mode="judge", candidate="deploy", actor_id="arif")
    assert r.status == "OK"
    assert r.result["verdict"] == "SEAL"
    assert r.judge_contract is not None
    assert r.judge_contract.state_hash


def test_vault_requires_judge_contract_even_with_ack():
    r = arif_vault_seal(mode="seal", payload="test", ack_irreversible=True, actor_id="arif")
    assert r.status == "HOLD"
    assert "judge" in r.meta["reason"]


def test_forge_commit_requires_vault_lineage():
    r = arif_forge_execute(mode="commit", ack_irreversible=True, actor_id="arif")
    assert r.status == "HOLD"
    assert "vault_entry_id" in r.meta["reason"]


def test_forge_commit_accepts_vault_lineage():
    judge = arif_judge_deliberate(mode="judge", candidate="commit deploy", actor_id="arif")
    seal = arif_vault_seal(
        mode="seal",
        payload="test",
        ack_irreversible=True,
        actor_id="arif",
        constitutional_chain_id=judge.judge_contract.constitutional_chain_id,
        judge_state_hash=judge.judge_contract.state_hash,
    )
    forge = arif_forge_execute(
        mode="commit",
        ack_irreversible=True,
        actor_id="arif",
        constitutional_chain_id=judge.judge_contract.constitutional_chain_id,
        judge_state_hash=judge.judge_contract.state_hash,
        vault_entry_id=seal.entry_id,
    )
    assert forge.status == "OK"
    assert forge.vault_entry_id == seal.entry_id
    assert forge.judge_contract is not None


def test_floor_status_aligned():
    s = get_floor_status()
    assert s["status"] == "aligned"
    assert len(s["floors"]) == 13


class _FakeContext:
    def __init__(self, response):
        self.response = response
        self.progress: list[tuple[float, float | None, str | None]] = []

    async def elicit(self, message, response_type=None):
        return self.response

    async def report_progress(self, progress, total=None, message=None):
        self.progress.append((progress, total, message))


@pytest.mark.asyncio
async def test_elicitation_accepts_irreversible_ack():
    ctx = _FakeContext(
        AcceptedElicitation(data=IrreversibleConfirmation(ack_irreversible=True))
    )

    ack, hold = await _elicit_irreversible_ack(
        ctx,
        tool_name="arif_vault_seal",
        mode="seal",
        actor_id="arif",
        session_id="S1",
        ack_irreversible=False,
    )

    assert ack is True
    assert hold is None
    assert ctx.progress


@pytest.mark.asyncio
async def test_elicitation_decline_holds_irreversible_action():
    ack, hold = await _elicit_irreversible_ack(
        _FakeContext(DeclinedElicitation()),
        tool_name="arif_forge_execute",
        mode="commit",
        actor_id="arif",
        session_id="S1",
        ack_irreversible=False,
    )

    assert ack is False
    assert hold is not None
    assert hold["status"] == "HOLD"


@pytest.mark.asyncio
async def test_elicitation_accepts_missing_judge_candidate():
    candidate, hold = await _elicit_judge_candidate(
        _FakeContext(AcceptedElicitation(data=JudgeCandidateInput(candidate="deploy"))),
        mode="judge",
        candidate=None,
    )

    assert candidate == "deploy"
    assert hold is None


@pytest.mark.asyncio
async def test_elicitation_cancel_holds_missing_judge_candidate():
    candidate, hold = await _elicit_judge_candidate(
        _FakeContext(CancelledElicitation()),
        mode="judge",
        candidate=None,
    )

    assert candidate is None
    assert hold is not None
    assert hold["status"] == "HOLD"

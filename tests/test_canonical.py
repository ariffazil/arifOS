"""
Canonical rebuild tests — 13 public capability tools, 2 internal diagnostics.
"""

import pytest
from fastmcp import FastMCP
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

from arifosmcp.constitutional_map import (
    CANONICAL_TOOLS,
    list_canonical_tools,
    list_constitutional_tools,
    list_probe_tools,
)
from arifosmcp.runtime.public_surface import CANARY_PROBES
from arifosmcp.prompts import CANONICAL_PROMPTS, register_prompts
from arifosmcp.resources import (
    CANONICAL_RESOURCES,
    EMBODIED_RESOURCES,
    EVIDENCE_RESOURCES,
    RUNNER_RESOURCES,
    TREE777_RESOURCES,
    register_resources,
)
from arifosmcp.runtime.law import get_floor_status
from arifosmcp.runtime.tools import (
    IrreversibleConfirmation,
    JudgeCandidateInput,
    _elicit_irreversible_ack,
    _elicit_judge_candidate,
    register_tools,
)
from arifosmcp.tools.session import arif_session_init
from arifosmcp.tools.sense import arif_sense_observe
from arifosmcp.tools.vault import arif_vault_seal
from arifosmcp.tools.forge import arif_forge_execute
from arifosmcp.tools.judge import arif_judge_deliberate


@pytest.fixture(autouse=True)
def _stable_runtime_env(monkeypatch):
    monkeypatch.setenv("ARIFOS_DEV_MODE", "0")


def test_surface_partition():
    assert len(CANONICAL_TOOLS) == 21
    assert len(list_constitutional_tools()) == 21
    assert len(list_probe_tools()) == 0


def test_tool_names():
    expected = sorted(CANONICAL_TOOLS)
    assert sorted(list_constitutional_tools()) == expected
    assert sorted(list_canonical_tools()) == expected


def test_register_tools_matches_canonical_surface():
    mcp = FastMCP("test-arifos")
    registered = register_tools(mcp)
    # register_tools wires canonical handlers only; the public canary is registered separately
    assert len(registered) == len(CANONICAL_TOOLS)
    assert set(CANONICAL_TOOLS).issubset(set(registered))
    assert not any(name.startswith("arifos_") for name in registered)


def test_register_prompts_matches_canonical_prompt_surface():
    mcp = FastMCP("test-arifos-prompts")
    registered = register_prompts(mcp)
    assert tuple(registered) == CANONICAL_PROMPTS


def test_register_resources_matches_canonical_resource_surface():
    mcp = FastMCP("test-arifos-resources")
    registered = register_resources(mcp)
    registered_set = set(registered)
    expected_set = set(CANONICAL_RESOURCES) | set(EVIDENCE_RESOURCES) | set(EMBODIED_RESOURCES) | set(TREE777_RESOURCES) | set(RUNNER_RESOURCES) | {"sovereign://{file}"}
    # Verify all expected resources are registered (order-independent, allows for
    # extra bootstrap resources like arifos://human/metabolized)
    missing = expected_set - registered_set
    assert not missing, f"Missing registered resources: {missing}"
    assert len(registered) >= len(expected_set), f"Expected >= {len(expected_set)} resources, got {len(registered)}"


def test_init_creates_session():
    r = arif_session_init(mode="init", actor_id="arif")
    assert r.status == "OK"
    assert "session_id" in r.result["session"]


@pytest.mark.asyncio
async def test_vault_holds_without_ack():
    r = await arif_vault_seal(mode="seal", payload="test", actor_id="arif")
    assert r.status == "HOLD"
    assert "F01" in r.meta["failed_floors"]


@pytest.mark.asyncio
async def test_vault_seals_with_ack():
    judge = await arif_judge_deliberate(mode="judge", candidate="seal test", actor_id="arif")
    r = await arif_vault_seal(
        mode="seal",
        payload="test",
        ack_irreversible=True,
        actor_id="arif",
        witness_type="human",
        constitutional_chain_id=judge.judge_contract.constitutional_chain_id,
        judge_state_hash=judge.judge_contract.state_hash,
    )
    assert r.status == "HOLD"
    assert "judge irreversibility level is below vault seal requirement" in r.meta["reason"]
    assert r.judge_contract is not None
    assert r.judge_contract.state_hash == judge.judge_contract.state_hash


@pytest.mark.asyncio
async def test_forge_holds_without_actor():
    r = await arif_forge_execute(mode="commit", ack_irreversible=True)
    assert r.status == "HOLD"
    assert "F11" in r.meta["failed_floors"]


def test_injection_guard_blocks():
    r = arif_sense_observe(mode="search", query="rm -rf /", actor_id="arif")
    assert r["status"] == "HOLD"
    floors = r["meta"]["failed_floors"]
    # F12 (INJECTION) must fire for destructive filesystem patterns; F11 may also fire
    assert "F12" in floors, "F12 INJECTION guard must block destructive query"
    assert floors[0] in ("F11", "F12"), "F11 AUTH or F12 INJECTION must be primary blocker"


@pytest.mark.asyncio
async def test_judge_without_evidence_returns_sabar():
    """F2 Evidence Gate: Without evidence_receipt, SEAL is downgraded to SABAR."""
    r = await arif_judge_deliberate(mode="judge", candidate="deploy", actor_id="arif")
    assert r.status == "SABAR"
    assert r.result["verdict"] == "SABAR"
    assert "evidence" in r.result["reason"].lower()


def test_judge_emits_seal_with_evidence():
    """SEAL is granted only when evidence_receipt is provided (F2 Evidence Gate)."""
    # Import the runtime function which accepts evidence_receipt
    from arifosmcp.runtime.tools import _arif_judge_deliberate

    minimal_receipt = {
        "query_sent": "deploy evidence check",
        "results_returned": 1,
        "urls_ingested": 1,
        "provider": "test",
        "bridge": "unit_test",
    }
    r = _arif_judge_deliberate(
        mode="judge",
        candidate="deploy",
        actor_id="arif",
        evidence_receipt=minimal_receipt,
    )
    assert r["status"] == "OK"
    assert r["result"]["verdict"] == "SEAL"
    assert r["judge_contract"] is not None
    assert r["judge_contract"]["state_hash"]


@pytest.mark.asyncio
async def test_vault_requires_judge_contract_even_with_ack():
    r = await arif_vault_seal(
        mode="seal",
        payload="test",
        ack_irreversible=True,
        actor_id="arif",
        witness_type="human",
    )
    assert r.status == "HOLD"
    assert "judge" in r.meta["reason"]


@pytest.mark.asyncio
async def test_forge_commit_requires_vault_lineage():
    r = await arif_forge_execute(mode="commit", ack_irreversible=True, actor_id="arif")
    assert r.status == "HOLD"
    assert "vault_entry_id" in r.meta["reason"]


@pytest.mark.asyncio
async def test_forge_commit_accepts_vault_lineage():
    judge = await arif_judge_deliberate(mode="judge", candidate="commit deploy", actor_id="arif")
    seal = await arif_vault_seal(
        mode="seal",
        payload="test",
        ack_irreversible=True,
        actor_id="arif",
        witness_type="human",
        constitutional_chain_id=judge.judge_contract.constitutional_chain_id,
        judge_state_hash=judge.judge_contract.state_hash,
    )
    assert seal.status == "HOLD"
    assert seal.entry_id is None
    forge = await arif_forge_execute(
        mode="commit",
        ack_irreversible=True,
        actor_id="arif",
        witness_type="human",
        constitutional_chain_id=judge.judge_contract.constitutional_chain_id,
        judge_state_hash=judge.judge_contract.state_hash,
        vault_entry_id=seal.entry_id,
    )
    assert forge.status == "HOLD"
    assert forge.vault_entry_id is None
    assert "vault_entry_id" in forge.meta["reason"]


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
    ctx = _FakeContext(AcceptedElicitation(data=IrreversibleConfirmation(ack_irreversible=True)))

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


# ═══════════════════════════════════════════════════════════════════════════════
# PARAMETER ALIAS RESILIENCE TESTS — F2 TRUTH / F4 CLARITY
# ═══════════════════════════════════════════════════════════════════════════════


def test_filter_kwargs_drops_unknown_params():
    """Unknown parameters must be dropped, not crash the handler."""
    from arifosmcp.runtime.tools import _filter_kwargs_for_handler

    def handler(mode: str, query: str | None = None) -> dict:
        return {"mode": mode, "query": query}

    filtered = _filter_kwargs_for_handler(handler, {"mode": "test", "metric": 42}, "test_tool")
    assert "mode" in filtered
    assert "metric" not in filtered
    assert filtered["mode"] == "test"


def test_filter_kwargs_maps_aliases():
    """Legacy aliases must be translated to canonical parameter names."""
    from arifosmcp.runtime.tools import _filter_kwargs_for_handler

    def handler(mode: str, query: str | None = None) -> dict:
        return {"mode": mode, "query": query}

    filtered = _filter_kwargs_for_handler(
        handler, {"mode": "reason", "prompt": "hello"}, "arif_mind_reason"
    )
    assert "query" in filtered
    assert "prompt" not in filtered
    assert filtered["query"] == "hello"


def test_filter_kwargs_passes_kwargs_handler():
    """Handlers accepting **kwargs must receive everything unfiltered."""
    from arifosmcp.runtime.tools import _filter_kwargs_for_handler

    def handler(mode: str, **kwargs) -> dict:
        return {"mode": mode, **kwargs}

    filtered = _filter_kwargs_for_handler(handler, {"mode": "test", "extra": "value"}, "test_tool")
    assert "extra" in filtered
    assert filtered["extra"] == "value"


def test_filter_kwargs_maps_metric_to_estimate():
    """arif_ops_measure alias: metric -> estimate."""
    from arifosmcp.runtime.tools import _filter_kwargs_for_handler

    def handler(mode: str, estimate: float | None = None) -> dict:
        return {"mode": mode, "estimate": estimate}

    filtered = _filter_kwargs_for_handler(
        handler, {"mode": "health", "metric": 99.0}, "arif_ops_measure"
    )
    assert "estimate" in filtered
    assert filtered["estimate"] == 99.0
    assert "metric" not in filtered


def test_filter_kwargs_maps_prompt_to_query():
    """arif_mind_reason alias: prompt -> query."""
    from arifosmcp.runtime.tools import _filter_kwargs_for_handler

    def handler(mode: str, query: str | None = None) -> dict:
        return {"mode": mode, "query": query}

    filtered = _filter_kwargs_for_handler(
        handler, {"mode": "reason", "prompt": "think deeply"}, "arif_mind_reason"
    )
    assert "query" in filtered
    assert filtered["query"] == "think deeply"
    assert "prompt" not in filtered

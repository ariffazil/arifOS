from __future__ import annotations

import pytest

from arifosmcp.runtime.explore import (
    NavigatorMode,
    ProspectorMode,
    StepResult,
    arif_explore,
)
from arifosmcp.schemas.explore import (
    ExplorationGraph,
    ExploreMode,
    Finding,
    GraphNode,
    Limits,
    Seed,
    SeedPath,
    SeedURL,
)


@pytest.mark.asyncio
async def test_prospector_plan_respects_request_seed_path():
    seen_paths: list[str] = []

    async def fake_list(path: str) -> list[str]:
        seen_paths.append(path)
        return ["alpha.py"]

    mode = ProspectorMode(
        request_seed=Seed(path=SeedPath(path="/tmp/geox-seed")),
        fs_list=fake_list,
    )

    nodes = await mode.plan("find alpha", ExplorationGraph(), Limits(max_steps=4))

    assert seen_paths == ["/tmp/geox-seed"]
    assert len(nodes) == 1
    assert nodes[0].label == "/tmp/geox-seed/alpha.py"


@pytest.mark.asyncio
async def test_navigator_plan_seeds_from_request_url():
    graph = ExplorationGraph()
    mode = NavigatorMode(request_seed=Seed(url=SeedURL(url="https://example.com/docs")))

    nodes = await mode.plan("inspect docs", graph, Limits(max_steps=4))

    assert len(nodes) == 1
    assert nodes[0].label == "https://example.com/docs"
    assert nodes[0].meta["unresolved"] is True
    assert graph.nodes[0].label == "https://example.com/docs"


@pytest.mark.asyncio
async def test_arif_explore_navigator_executes_seeded_step(monkeypatch: pytest.MonkeyPatch):
    async def fake_step(self: NavigatorMode, node: GraphNode, seed: Seed) -> StepResult:
        page_node = GraphNode(
            node_id="page-node",
            mode=ExploreMode.NAVIGATOR,
            label="Example Domain",
            content_hash="page-hash",
            evidence="example body",
            meta={"url": node.label, "title": "Example Domain"},
        )
        return StepResult(
            nodes=[page_node],
            edges=[],
            findings=[
                Finding(
                    id="finding-1",
                    summary=f"Fetched {node.label}",
                    confidence=0.9,
                    sources=[node.label],
                )
            ],
            gaps=[],
            coverage_delta=0.5,
            confidence=0.9,
            terminal=True,
        )

    monkeypatch.setattr(NavigatorMode, "step", fake_step)

    result = await arif_explore(
        goal="inspect the seed page",
        mode="navigator",
        seed_url="https://example.com",
        max_steps=2,
        time_budget_s=10,
    )

    assert result["status"] == "partial"
    assert result["metrics"]["steps"] == 1
    assert len(result["exploration_graph"]["nodes"]) >= 2
    assert result["findings"][0]["sources"] == ["https://example.com"]
    assert result["requested_mode"] == "navigator"
    assert result["resolved_mode"] == "navigator"


# ════════════════════════════════════════════════════════════════════════
# Federation tests — Navigator delegates to arif_sense_observe /
# arif_evidence_fetch via _CANONICAL_HANDLERS (no Playwright).
# ════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_navigator_step_delegates_url_to_evidence_fetch(monkeypatch: pytest.MonkeyPatch):
    """URL-shaped node → arif_evidence_fetch(mode=fetch, url=...)."""
    from arifosmcp.runtime import tools as rt_tools

    calls: list[dict] = []

    def fake_evidence_fetch(*, mode: str, url: str, **_kwargs):
        calls.append({"mode": mode, "url": url})
        return {
            "status": "OK",
            "tool": "arif_evidence_fetch",
            "actor_verified": True,
            "session_id": "sess-forge-test",
            "result": {
                "content": "<html><body>Federated content for " + url + "</body></html>",
                "content_hash": "fake-hash-" + url,
                "fetch_error": None,
            },
        }

    monkeypatch.setitem(rt_tools._CANONICAL_HANDLERS, "arif_evidence_fetch", fake_evidence_fetch)

    mode = NavigatorMode(
        request_seed=Seed(url=SeedURL(url="https://example.com/federated")),
        actor_id="forge-actor",
        session_id="sess-forge-test",
    )
    node = GraphNode(
        node_id="seed-hash",
        mode=ExploreMode.NAVIGATOR,
        label="https://example.com/federated",
        content_hash="",
        evidence="",
        meta={"unresolved": True, "url": "https://example.com/federated"},
    )
    result = await mode.step(node, Seed())

    assert len(calls) == 1, "should delegate exactly once"
    assert calls[0]["mode"] == "fetch"
    assert calls[0]["url"] == "https://example.com/federated"

    # Page node contains federated content + envelope metadata
    assert len(result.nodes) == 1
    page = result.nodes[0]
    assert "Federated content" in page.evidence
    assert page.meta["federated_via"] == "arif_evidence_fetch"
    assert page.meta["actor_verified"] is True
    assert page.meta["session_id"] == "sess-forge-test"

    # Finding cites source URL
    assert len(result.findings) == 1
    assert result.findings[0].sources == ["https://example.com/federated"]


@pytest.mark.asyncio
async def test_navigator_step_delegates_query_to_sense_observe(monkeypatch: pytest.MonkeyPatch):
    """Question-shaped node → arif_sense_observe(mode=search, query=...)."""
    from arifosmcp.runtime import tools as rt_tools

    calls: list[dict] = []

    def fake_sense_observe(*, mode: str, query: str, **_kwargs):
        calls.append({"mode": mode, "query": query})
        return {
            "status": "OK",
            "tool": "arif_sense_observe",
            "actor_verified": True,
            "session_id": "sess-forge-test",
            "result": {
                "results": [
                    {"title": "Result A", "url": "https://example.com/a", "snippet": "snippet A"},
                    {"title": "Result B", "url": "https://example.com/b", "snippet": "snippet B"},
                ],
            },
        }

    monkeypatch.setitem(rt_tools._CANONICAL_HANDLERS, "arif_sense_observe", fake_sense_observe)

    mode = NavigatorMode(
        request_seed=None,
        actor_id="forge-actor",
        session_id="sess-forge-test",
    )
    node = GraphNode(
        node_id="q-hash",
        mode=ExploreMode.NAVIGATOR,
        label="find geology papers",
        content_hash="",
        evidence="",
        meta={"unresolved": True},
    )
    result = await mode.step(node, Seed())

    assert len(calls) == 1
    assert calls[0]["mode"] == "search"
    assert calls[0]["query"] == "find geology papers"

    # Two unresolved child nodes from search hits
    assert len(result.nodes) == 2
    urls = {n.label for n in result.nodes}
    assert urls == {"https://example.com/a", "https://example.com/b"}
    for n in result.nodes:
        assert n.meta["federated_via"] == "arif_sense_observe"
        assert n.meta["unresolved"] is True


@pytest.mark.asyncio
async def test_navigator_step_handles_handler_missing(monkeypatch: pytest.MonkeyPatch):
    """If federated handler is absent, Navigator reports a clean gap (no crash)."""
    from arifosmcp.runtime import tools as rt_tools

    # Remove sense_observe from canonical registry for this test
    monkeypatch.delitem(rt_tools._CANONICAL_HANDLERS, "arif_sense_observe", raising=False)

    mode = NavigatorMode(actor_id="forge-actor", session_id="sess-test")
    node = GraphNode(
        node_id="q",
        mode=ExploreMode.NAVIGATOR,
        label="orphan query",
        content_hash="",
        evidence="",
        meta={"unresolved": True},
    )
    result = await mode.step(node, Seed())

    assert result.terminal is True
    assert any("arif_sense_observe" in g for g in result.gaps)
    assert result.confidence == 0.0


@pytest.mark.asyncio
async def test_arif_explore_auto_driller_falls_back_to_prospector(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    """AUTO mode + seed_api_base_url routes to DRILLER → graceful Prospector fallback."""
    (tmp_path / "x.py").write_text("# stub")

    async def fake_step(self: ProspectorMode, node, seed):
        return StepResult(
            nodes=[
                GraphNode(
                    node_id="stub",
                    mode=ExploreMode.PROSPECTOR,
                    label=str(node.label),
                    content_hash="h",
                    evidence="",
                    meta={"type": "python", "symbols": [], "symbol_count": 0},
                )
            ],
            edges=[],
            findings=[],
            gaps=[],
            coverage_delta=0.5,
            confidence=0.9,
            terminal=True,
        )

    monkeypatch.setattr(ProspectorMode, "step", fake_step)

    result = await arif_explore(
        goal="test fallback",
        mode="auto",
        seed_api_base_url="https://api.example.com",
        seed_path=str(tmp_path),
        max_steps=2,
        time_budget_s=10,
    )

    # Auto-mode precedence: seed_path wins → PROSPECTOR (no fallback needed)
    assert result["resolved_mode"] == "prospector"
    assert "mode_fallback" not in result


@pytest.mark.asyncio
async def test_arif_explore_explicit_driller_returns_not_implemented():
    """Explicit mode='driller' (not auto) returns not_implemented, no fallback."""
    result = await arif_explore(
        goal="explicit driller",
        mode="driller",
        max_steps=2,
        time_budget_s=10,
    )
    assert result["status"] == "not_implemented"
    assert result["mode"] == "driller"


@pytest.mark.asyncio
async def test_arif_explore_response_includes_routing_metadata():
    """Handler response surfaces requested_mode + resolved_mode for transparency."""
    result = await arif_explore(
        goal="metadata check",
        mode="prospector",
        max_steps=1,
        time_budget_s=5,
    )
    assert result["requested_mode"] == "prospector"
    assert result["resolved_mode"] == "prospector"

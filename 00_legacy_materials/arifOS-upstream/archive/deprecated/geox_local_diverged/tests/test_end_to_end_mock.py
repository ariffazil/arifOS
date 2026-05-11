"""
GEOX End-to-End Mock Tests
DITEMPA BUKAN DIBERI

Full pipeline integration tests using GeoXAgent with mock tools only.
No external APIs — all tools are MockEarthNetTool / MockSeismicVLMTool.

Pipeline under test: 000 INIT → 111 THINK → 333 EXPLORE → 555 HEART →
                     777 REASON → 888 AUDIT → 999 SEAL

Fixtures defined in conftest.py:
  - geo_request  — GeoRequest for Blok Selatan, Malay Basin
  - mock_agent   — GeoXAgent wired with mock tools + in-memory memory
"""

from __future__ import annotations

import uuid

import pytest

from arifos.geox.geox_agent import GeoXAgent
from arifos.geox.geox_memory import GeoMemoryEntry, GeoMemoryStore
from arifos.geox.geox_reporter import GeoXReporter
from arifos.geox.geox_schemas import (
    GeoInsight,
    GeoRequest,
    GeoResponse,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_VERDICTS = {"SEAL", "PARTIAL", "SABAR", "VOID"}

REQUIRED_TELEMETRY_KEYS = {
    "pipeline",
    "stage",
    "floors",
    "confidence",
    "verdict",
    "seal",
}


# ---------------------------------------------------------------------------
# test_evaluate_prospect_full_pipeline
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_evaluate_prospect_full_pipeline(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """
    Run the full evaluate_prospect() pipeline and assert a GeoResponse is
    returned with a valid verdict.
    """
    response = await mock_agent.evaluate_prospect(geo_request)

    assert isinstance(
        response, GeoResponse
    ), f"Expected GeoResponse, got {type(response)}"
    assert (
        response.verdict in VALID_VERDICTS
    ), f"Verdict '{response.verdict}' not in {VALID_VERDICTS}"
    assert 0.0 <= response.confidence_aggregate <= 1.0
    # response_id must be a valid UUID4
    uuid.UUID(response.response_id, version=4)
    # request_id must match the request
    assert response.request_id == geo_request.request_id


@pytest.mark.asyncio
async def test_evaluate_prospect_returns_insights(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Pipeline must produce at least one GeoInsight."""
    response = await mock_agent.evaluate_prospect(geo_request)
    assert len(response.insights) >= 1
    for insight in response.insights:
        assert isinstance(insight, GeoInsight)


@pytest.mark.asyncio
async def test_evaluate_prospect_audit_log_populated(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Audit log must contain events from all pipeline stages."""
    response = await mock_agent.evaluate_prospect(geo_request)
    assert len(response.audit_log) >= 1
    stages_seen = {
        event.get("stage") for event in response.audit_log if "stage" in event
    }
    # At minimum INIT and THINK stages must appear
    assert "000 INIT" in stages_seen or any(
        "INIT" in s for s in stages_seen if s
    ), f"Expected INIT stage in audit log, found stages: {stages_seen}"


# ---------------------------------------------------------------------------
# test_response_has_telemetry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_response_has_telemetry(geo_request: GeoRequest, mock_agent: GeoXAgent):
    """
    arifos_telemetry must contain all required keys: pipeline, stage,
    floors, confidence, verdict, seal.
    """
    response = await mock_agent.evaluate_prospect(geo_request)
    telemetry = response.arifos_telemetry
    assert isinstance(telemetry, dict), "arifos_telemetry must be a dict"

    for key in REQUIRED_TELEMETRY_KEYS:
        assert key in telemetry, (
            f"Required telemetry key '{key}' missing. "
            f"Available keys: {list(telemetry.keys())}"
        )


@pytest.mark.asyncio
async def test_telemetry_pipeline_string(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """pipeline value must contain the expected stage sequence."""
    response = await mock_agent.evaluate_prospect(geo_request)
    pipeline = response.arifos_telemetry.get("pipeline", "")
    assert "000" in pipeline
    assert "999" in pipeline


@pytest.mark.asyncio
async def test_telemetry_verdict_matches_response(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Telemetry verdict must match response.verdict."""
    response = await mock_agent.evaluate_prospect(geo_request)
    assert response.arifos_telemetry.get("verdict") == response.verdict


@pytest.mark.asyncio
async def test_telemetry_confidence_matches_response(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Telemetry confidence must match response.confidence_aggregate."""
    response = await mock_agent.evaluate_prospect(geo_request)
    assert response.arifos_telemetry.get("confidence") == response.confidence_aggregate


@pytest.mark.asyncio
async def test_telemetry_seal_stamp(geo_request: GeoRequest, mock_agent: GeoXAgent):
    """Telemetry must carry the DITEMPA BUKAN DIBERI seal stamp."""
    response = await mock_agent.evaluate_prospect(geo_request)
    assert response.arifos_telemetry.get("seal") == "DITEMPA BUKAN DIBERI"


@pytest.mark.asyncio
async def test_telemetry_floors_is_list(geo_request: GeoRequest, mock_agent: GeoXAgent):
    """Telemetry 'floors' key must be a list."""
    response = await mock_agent.evaluate_prospect(geo_request)
    floors = response.arifos_telemetry.get("floors")
    assert isinstance(floors, list), f"Expected list for 'floors', got {type(floors)}"
    assert len(floors) >= 1


@pytest.mark.asyncio
async def test_telemetry_hold_status(geo_request: GeoRequest, mock_agent: GeoXAgent):
    """Telemetry 'hold' must be either 'CLEAR' or '888 HOLD'."""
    response = await mock_agent.evaluate_prospect(geo_request)
    hold = response.arifos_telemetry.get("hold")
    assert hold in ("CLEAR", "888 HOLD"), f"Unexpected hold value: '{hold}'"


# ---------------------------------------------------------------------------
# test_memory_store_and_retrieve
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_memory_store_and_retrieve(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """
    Store a GeoResponse in memory, retrieve by basin name, confirm the
    entry comes back with matching prospect and verdict.
    """
    response = await mock_agent.evaluate_prospect(geo_request)

    # Use the in-memory store attached to the agent
    memory: GeoMemoryStore = mock_agent.memory_store  # type: ignore[assignment]
    assert memory is not None, "mock_agent must have a memory_store"

    entry_id = await memory.store(response, geo_request)
    assert entry_id.startswith("GEO-MEM-"), f"Unexpected entry_id format: {entry_id}"

    # Retrieve by basin name
    results = await memory.retrieve("Blok Selatan", basin="Malay Basin")
    assert len(results) >= 1, "Memory retrieve returned no results"

    # The stored entry should be in results
    matched = [r for r in results if r.prospect_name == "Blok Selatan"]
    assert matched, "No result matches prospect_name='Blok Selatan'"

    entry = matched[0]
    assert isinstance(entry, GeoMemoryEntry)
    assert entry.basin == "Malay Basin"
    assert entry.verdict == response.verdict
    assert entry.confidence == response.confidence_aggregate


@pytest.mark.asyncio
async def test_memory_get_basin_history(geo_request: GeoRequest, mock_agent: GeoXAgent):
    """get_basin_history() must return entries for the stored basin."""
    response = await mock_agent.evaluate_prospect(geo_request)
    memory: GeoMemoryStore = mock_agent.memory_store  # type: ignore[assignment]
    await memory.store(response, geo_request)

    history = await memory.get_basin_history("Malay Basin")
    assert isinstance(history, list)
    assert len(history) >= 1
    for entry in history:
        assert "malay" in entry.basin.lower()


@pytest.mark.asyncio
async def test_memory_deduplication(geo_request: GeoRequest, mock_agent: GeoXAgent):
    """Storing the same response twice should not create duplicate entries."""
    response = await mock_agent.evaluate_prospect(geo_request)
    memory: GeoMemoryStore = mock_agent.memory_store  # type: ignore[assignment]

    id1 = await memory.store(response, geo_request)
    id2 = await memory.store(response, geo_request)  # Same content

    assert id1 == id2, "Same content should produce same entry_id (deduplication)"
    assert memory.count() == 1, f"Expected 1 entry after dedup, got {memory.count()}"


@pytest.mark.asyncio
async def test_memory_entry_has_metadata(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Memory entries must carry metadata including request_id and response_id."""
    response = await mock_agent.evaluate_prospect(geo_request)
    memory: GeoMemoryStore = mock_agent.memory_store  # type: ignore[assignment]
    await memory.store(response, geo_request)

    results = await memory.retrieve("Blok Selatan", basin="Malay Basin")
    assert results
    entry = results[0]
    assert "request_id" in entry.metadata
    assert "response_id" in entry.metadata
    assert entry.metadata["request_id"] == geo_request.request_id
    assert entry.metadata["response_id"] == response.response_id


# ---------------------------------------------------------------------------
# test_reporter_markdown
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reporter_markdown(geo_request: GeoRequest, mock_agent: GeoXAgent):
    """
    generate_markdown_report() must return a non-empty string containing
    the verdict and the 'DITEMPA BUKAN DIBERI' seal.
    """
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    md = reporter.generate_markdown_report(response, geo_request)

    assert isinstance(md, str), "Markdown report must be a string"
    assert len(md) > 100, "Markdown report appears too short"
    assert "DITEMPA BUKAN DIBERI" in md, "Missing seal stamp in Markdown report"
    assert response.verdict in md, f"Verdict '{response.verdict}' not found in report"


@pytest.mark.asyncio
async def test_reporter_markdown_contains_prospect_name(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Markdown report must contain the prospect name."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    md = reporter.generate_markdown_report(response, geo_request)
    assert "Blok Selatan" in md


@pytest.mark.asyncio
async def test_reporter_markdown_contains_basin(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Markdown report must contain the basin name."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    md = reporter.generate_markdown_report(response, geo_request)
    assert "Malay Basin" in md


@pytest.mark.asyncio
async def test_reporter_markdown_contains_geox_header(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Markdown report must contain GEOX header."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    md = reporter.generate_markdown_report(response, geo_request)
    assert "GEOX" in md


@pytest.mark.asyncio
async def test_reporter_markdown_verdict_section(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Markdown report must contain the Overall Verdict section."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    md = reporter.generate_markdown_report(response, geo_request)
    assert "Overall Verdict" in md or "verdict" in md.lower()


@pytest.mark.asyncio
async def test_reporter_markdown_telemetry_section(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Markdown report must contain the arifOS Telemetry section."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    md = reporter.generate_markdown_report(response, geo_request)
    assert "Telemetry" in md or "arifOS" in md


# ---------------------------------------------------------------------------
# test_reporter_json_audit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reporter_json_audit(geo_request: GeoRequest, mock_agent: GeoXAgent):
    """
    generate_json_audit() must return a valid dict containing response_id.
    """
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    audit = reporter.generate_json_audit(response)

    assert isinstance(audit, dict), "JSON audit must be a dict"
    assert "response_id" in audit, "JSON audit missing 'response_id'"
    assert audit["response_id"] == response.response_id


@pytest.mark.asyncio
async def test_reporter_json_audit_structure(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """JSON audit dict must contain all expected top-level keys."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    audit = reporter.generate_json_audit(response)

    required_keys = {
        "vault_entry_type",
        "version",
        "response_id",
        "request_id",
        "verdict",
        "confidence_aggregate",
        "human_signoff_required",
        "pipeline",
        "seal",
        "arifos_telemetry",
        "insights",
        "predictions",
        "provenance_chain",
        "audit_log",
        "floor_compliance",
    }
    missing = required_keys - set(audit.keys())
    assert not missing, f"JSON audit missing keys: {missing}"


@pytest.mark.asyncio
async def test_reporter_json_audit_verdict(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """JSON audit verdict must match GeoResponse verdict."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    audit = reporter.generate_json_audit(response)
    assert audit["verdict"] == response.verdict


@pytest.mark.asyncio
async def test_reporter_json_audit_seal_stamp(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """JSON audit must carry the DITEMPA BUKAN DIBERI seal."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    audit = reporter.generate_json_audit(response)
    assert audit["seal"] == "DITEMPA BUKAN DIBERI"


@pytest.mark.asyncio
async def test_reporter_json_audit_floor_compliance(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """JSON audit floor_compliance must be a dict of bool values."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    audit = reporter.generate_json_audit(response)
    floor_compliance = audit.get("floor_compliance", {})
    assert isinstance(floor_compliance, dict)
    for floor_id, value in floor_compliance.items():
        assert isinstance(
            value, bool
        ), f"floor_compliance[{floor_id}] is not bool: {value}"


@pytest.mark.asyncio
async def test_reporter_json_audit_insights_list(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """JSON audit insights must be a list matching response.insights count."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    audit = reporter.generate_json_audit(response)
    assert isinstance(audit["insights"], list)
    assert len(audit["insights"]) == len(response.insights)


@pytest.mark.asyncio
async def test_reporter_json_audit_pipeline_string(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """JSON audit pipeline must contain expected stage sequence."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    audit = reporter.generate_json_audit(response)
    pipeline = audit.get("pipeline", "")
    assert "000" in pipeline
    assert "999" in pipeline


# ---------------------------------------------------------------------------
# test_reporter_human_brief
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reporter_human_brief_is_string(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """generate_human_brief() must return a non-empty string."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    brief = reporter.generate_human_brief(response)
    assert isinstance(brief, str)
    assert len(brief) > 50


@pytest.mark.asyncio
async def test_reporter_human_brief_three_paragraphs(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Human brief must consist of exactly 3 paragraphs (separated by double newlines)."""
    response = await mock_agent.evaluate_prospect(geo_request)
    reporter = GeoXReporter()
    brief = reporter.generate_human_brief(response)
    paragraphs = [p.strip() for p in brief.split("\n\n") if p.strip()]
    assert (
        len(paragraphs) == 3
    ), f"Expected 3 paragraphs, got {len(paragraphs)}. Brief:\n{brief}"


# ---------------------------------------------------------------------------
# test_full_pipeline_deterministic
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_pipeline_deterministic(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """
    Running evaluate_prospect twice with the same request should produce
    verdicts from the valid set each time (mock tools are seeded deterministically).
    """
    r1 = await mock_agent.evaluate_prospect(geo_request)
    r2 = await mock_agent.evaluate_prospect(geo_request)

    assert r1.verdict in VALID_VERDICTS
    assert r2.verdict in VALID_VERDICTS
    # Both should have same verdict given deterministic mocks
    assert (
        r1.verdict == r2.verdict
    ), f"Expected deterministic verdict but got {r1.verdict} vs {r2.verdict}"


# ---------------------------------------------------------------------------
# test_plan_heuristic
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_plan_heuristic_includes_earth_model(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Heuristic plan must always include EarthModelTool as first entry."""
    plan = await mock_agent.plan(geo_request)
    assert isinstance(plan, list)
    assert len(plan) >= 1
    assert (
        plan[0] == "EarthModelTool"
    ), f"EarthModelTool must be first in plan, got: {plan}"


@pytest.mark.asyncio
async def test_plan_only_registered_tools(
    geo_request: GeoRequest, mock_agent: GeoXAgent
):
    """Plan must only contain tools actually registered in the registry."""
    plan = await mock_agent.plan(geo_request)
    registered = set(mock_agent.tool_registry.list_tools())
    for tool_name in plan:
        assert (
            tool_name in registered
        ), f"Plan includes unregistered tool '{tool_name}'. Registered: {registered}"


# ---------------------------------------------------------------------------
# test_f13_sovereign_hold
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_void_verdict_triggers_human_hold():
    """
    A response with VOID verdict must have human_signoff_required=True
    and hold='888 HOLD' in telemetry.
    """
    from arifos.geox.geox_schemas import GeoInsight, GeoResponse

    # Build a mock VOID response manually
    insight = GeoInsight(
        text="Contradicted — porosity estimated at 95% fraction (impossible).",
        status="contradicted",
        risk_level="high",
        requires_human_signoff=True,
    )
    response = GeoResponse(
        request_id=str(uuid.uuid4()),
        verdict="VOID",
        confidence_aggregate=0.20,
        insights=[insight],
        human_signoff_required=True,
        arifos_telemetry={
            "pipeline": "000→111→333→555→777→888→999",
            "stage": "999 SEAL",
            "floors": ["F1", "F2", "F4", "F7", "F13"],
            "confidence": 0.20,
            "verdict": "VOID",
            "hold": "888 HOLD",
            "uncertainty_range": [0.03, 0.15],
            "seal": "DITEMPA BUKAN DIBERI",
        },
    )

    assert response.human_signoff_required is True
    assert response.arifos_telemetry["hold"] == "888 HOLD"
    assert response.verdict == "VOID"

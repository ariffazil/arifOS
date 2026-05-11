"""
GEOX Test Conftest
DITEMPA BUKAN DIBERI

Shared fixtures for the GEOX test suite:
  - geo_request   — standard GeoRequest pointing at Blok Selatan, Malay Basin
  - mock_agent    — GeoXAgent with MockEarthNetTool + MockSeismicVLMTool,
                    in-memory GeoMemoryStore, no external APIs
"""

from __future__ import annotations

import pytest

from arifos.geox.examples.mock_tools.mock_earthnet import MockEarthNetTool
from arifos.geox.examples.mock_tools.mock_vlm import MockSeismicVLMTool
from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
from arifos.geox.geox_memory import GeoMemoryStore
from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest
from arifos.geox.geox_tools import ToolRegistry
from arifos.geox.geox_validator import GeoXValidator

# ---------------------------------------------------------------------------
# geo_request — standard Blok Selatan fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def geo_request() -> GeoRequest:
    """
    A standard GeoRequest for the fictional 'Blok Selatan' prospect
    in the Malay Basin at lat=4.5, lon=104.2.
    """
    return GeoRequest(
        query=(
            "Evaluate hydrocarbon potential of Blok Selatan anticline "
            "in the Malay Basin. Assess reservoir quality, structural closure, "
            "and seal integrity."
        ),
        prospect_name="Blok Selatan",
        location=CoordinatePoint(latitude=4.5, longitude=104.2, depth_m=2500.0),
        basin="Malay Basin",
        play_type="structural",
        available_data=["seismic_3d", "well_logs"],
        risk_tolerance="medium",
        requester_id="USER-geo-test-001",
    )


# ---------------------------------------------------------------------------
# mock_agent — GeoXAgent with mock tools only
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_agent() -> GeoXAgent:
    """
    GeoXAgent wired with:
      - MockEarthNetTool   (registered as 'EarthModelTool')
      - MockSeismicVLMTool (registered as 'SeismicVLMTool')
      - GeoXValidator
      - In-memory GeoMemoryStore
      - No LLM planner (falls back to heuristic plan)
      - No audit sink
    """
    # Build registry with mock tools registered under production tool names
    registry = ToolRegistry()
    registry.register(_EarthModelToolProxy())
    registry.register(_SeismicVLMToolProxy())

    validator = GeoXValidator()
    memory = GeoMemoryStore()  # in-memory backend

    config = GeoXConfig(
        lem_confidence_threshold=0.70,
        max_tool_retries=1,
        allowed_tools=["EarthModelTool", "SeismicVLMTool"],
        provenance_required=True,
        pipeline_id="geox-test-v0.1",
    )

    return GeoXAgent(
        config=config,
        tool_registry=registry,
        validator=validator,
        llm_planner=None,
        audit_sink=None,
        memory_store=memory,
    )


# ---------------------------------------------------------------------------
# Internal proxy classes — register mock tools under production names
# ---------------------------------------------------------------------------


class _EarthModelToolProxy(MockEarthNetTool):
    """MockEarthNetTool registered under the production name 'EarthModelTool'."""

    @property
    def name(self) -> str:
        return "EarthModelTool"


class _SeismicVLMToolProxy(MockSeismicVLMTool):
    """MockSeismicVLMTool registered under the production name 'SeismicVLMTool'."""

    @property
    def name(self) -> str:
        return "SeismicVLMTool"

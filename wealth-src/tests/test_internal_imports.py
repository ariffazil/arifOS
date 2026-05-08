import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from internal.invariants import get_g_score
from internal.monolith import (
    mcp,
    wealth_future_steward,
    wealth_future_value,
    wealth_game_coordinate,
)


def test_g_score_engine_imports_and_runs():
    result = get_g_score({"trust_index": 0.7, "maruah_score": 0.6})

    assert set(
        {
            "g_score",
            "delta_s",
            "lyapunov_lambda",
            "omega_capacity",
            "entropy_s",
            "verdict",
            "regime",
        }
    ).issubset(result)


def test_primitive_response_uses_canonical_tool_name():
    envelope = wealth_future_value(
        mode="npv",
        initial_investment=1000.0,
        cash_flows=[1200.0],
        discount_rate=0.1,
    )

    assert envelope["task"] == "wealth_future_value"
    assert envelope["canonical_tool"] == "wealth_future_value"
    assert "g_score" in envelope
    assert "risk" in envelope
    assert "verdict" in envelope["risk"]


def test_mcp_tool_surface_minimum_16_core():
    tool_names = {tool.name for tool in asyncio.run(mcp.list_tools())}
    assert len(tool_names) >= 16, f"Expected >=16 tools at module import, got {len(tool_names)}: {sorted(tool_names)}"
    core = {
        "mcp_health_check",
        "vault_write",
        "vault_query",
        "wealth_allocate_optimize",
        "wealth_future_simulate",
        "wealth_future_steward",
        "wealth_future_value",
        "wealth_game_coordinate",
        "wealth_info_value",
        "wealth_past_record",
        "wealth_present_expect",
        "wealth_rule_enforce",
        "wealth_sense_ingest",
        "wealth_survival_leverage",
        "wealth_survival_liquidity",
        "wealth_truth_validate",
    }
    assert core.issubset(tool_names), f"Core tools missing: {core - tool_names}"


def test_game_coordinate_accepts_scalar_packets():
    envelope = wealth_game_coordinate(
        mode="equilibrium",
        agents=[
            {"id": "a1", "utility": 1.0, "resource_demand": 2.0},
            {"id": "a2", "utility": 0.8, "resource_demand": 1.0},
        ],
        shared_resources={"budget": 100.0},
    )

    assert envelope["task"] == "wealth_game_coordinate"
    assert envelope["engine_status"] in {"VALID", "WARNING", "ERROR"}


def test_future_steward_maps_public_packet_to_internal_engine():
    envelope = wealth_future_steward(
        carbon_budget_gtc=250.0,
        energy_mix={"renewables": 0.6, "fossil": 0.4},
        population_projection={"current": 34_000_000, "target": 36_000_000},
        horizon_years=25,
    )

    assert envelope["task"] == "wealth_future_steward"
    assert "risk" in envelope

"""
[DEPRECATED] GEOX FastMCP Adapter — Thin transport wrapper for GEOX core tools.

This module provides the FastMCP-specific binding layer. It:
1. Imports host-agnostic tools from geox.tools.core
2. Wraps them with FastMCP decorators
3. Handles ToolResult conversion
4. Manages FastMCP server lifecycle

Domain logic lives in geox.tools.core and services/.
This adapter contains NO business logic — only transport concerns.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import warnings

warnings.warn(
    "fastmcp_adapter.py is deprecated. The canonical unified surface is geox_unified_mcp_server.py "
    "and the execution plane is execution_plane/vps/server.py. Do not build new dependencies here.",
    DeprecationWarning,
    stacklevel=2,
)

import argparse
import logging
import os
from datetime import datetime, timezone
from typing import Any

# FastMCP imports (transport layer only)
try:
    import fastmcp

    FASTMCP_VERSION = tuple(map(int, fastmcp.__version__.split(".")[:2]))
    IS_FASTMCP_3 = FASTMCP_VERSION >= (3, 0)
except Exception:
    FASTMCP_VERSION = (2, 0)
    IS_FASTMCP_3 = False

from fastmcp import FastMCP

if IS_FASTMCP_3:
    from fastmcp.tools import ToolResult
else:

    class ToolResult:
        def __init__(
            self, content: str, structured_content: Any = None, meta: dict = None
        ):
            self.content = content
            self.structured_content = structured_content
            self.meta = meta or {}


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("geox.mcp")

# ═══════════════════════════════════════════════════════════════════════════════
# Optional Dependency Detection
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from ...geox_memory import GeoMemoryStore

    _memory_store: "GeoMemoryStore | None" = GeoMemoryStore()
    _HAS_MEMORY = True
except Exception as _mem_exc:
    _memory_store = None
    _HAS_MEMORY = False
    logger.info("Memory store unavailable (%s)", _mem_exc)

try:
    from ...physics.petrophysics import monte_carlo_sw

    _HAS_PHYSICS = True
except ImportError:
    _HAS_PHYSICS = False
    logger.info("Physics engine unavailable")

try:
    from ...schemas.petrophysics_schemas import (
        CutoffPolicy,
        CutoffValidationResult,
        LogQCFlags,
        PetrophysicsHold,
        PetrophysicsInput,
        PetrophysicsOutput,
        SwModelAdmissibility,
    )

    _HAS_PETRO_SCHEMAS = True
except ImportError as _petro_exc:
    _HAS_PETRO_SCHEMAS = False
    logger.warning("Petrophysics schemas unavailable: %s", _petro_exc)

try:
    from ..seismic.seismic_single_line_tool import SeismicSingleLineTool

    _HAS_SEISMIC = True
except ImportError:
    _HAS_SEISMIC = False
    logger.info("Seismic tools unavailable")

# ═══════════════════════════════════════════════════════════════════════════════
# Import Core Tools (Domain Logic)
# ═══════════════════════════════════════════════════════════════════════════════

from ..core import (
    geox_calculate_saturation as _core_calculate_saturation,
    geox_build_structural_candidates as _core_build_structural_candidates,
    geox_compute_petrophysics as _core_compute_petrophysics,
    geox_evaluate_prospect as _core_evaluate_prospect,
    geox_feasibility_check as _core_feasibility_check,
    geox_health as _core_health,
    geox_load_seismic_line as _core_load_seismic_line,
    geox_petrophysical_hold_check as _core_petrophysical_hold_check,
    geox_query_memory as _core_query_memory,
    geox_select_sw_model as _core_select_sw_model,
    geox_validate_cutoffs as _core_validate_cutoffs,
    geox_verify_geospatial as _core_verify_geospatial,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Server Configuration
# ═══════════════════════════════════════════════════════════════════════════════

GEOX_VERSION = "0.6.0"
GEOX_SEAL = "DITEMPA BUKAN DIBERI"

mcp = FastMCP(
    name="GEOX Earth Witness",
    version=GEOX_VERSION,
    instructions="Governed domain surface for subsurface inverse modelling. DITEMPA BUKAN DIBERI.",
)

# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions (Transport Layer Only)
# ═══════════════════════════════════════════════════════════════════════════════


def _tool_result_to_dict(result: ToolResult) -> dict:
    """Convert ToolResult to dict for FastMCP compatibility."""
    if IS_FASTMCP_3:
        return result
    else:
        return {
            "content": [{"type": "text", "text": result.content}],
            "structured_content": result.structured_content,
            "meta": result.meta,
        }


def _result_to_tool_result(result_obj: Any) -> ToolResult:
    """
    Convert a core result object to FastMCP ToolResult.

    This is the adapter boundary: domain objects in, transport objects out.
    """
    # Extract data from result object (Pydantic model)
    if hasattr(result_obj, "model_dump"):
        structured = result_obj.model_dump(mode="json")
    elif hasattr(result_obj, "dict"):
        structured = result_obj.dict()
    else:
        structured = dict(result_obj)

    # Build human-readable content from structured data
    status = structured.get("status", "UNKNOWN")
    content_parts = [f"GEOX Result: {status}"]

    # Add type-specific content
    if "well_id" in structured:
        content_parts.append(f"Well: {structured['well_id']}")
    if "prospect_id" in structured:
        content_parts.append(f"Prospect: {structured['prospect_id']}")
    if "line_id" in structured:
        content_parts.append(f"Line: {structured['line_id']}")

    # Add verdict/details
    if "verdict" in structured:
        content_parts.append(f"Verdict: {structured['verdict']}")
    if "hold_triggers" in structured and structured["hold_triggers"]:
        content_parts.append(f"Hold Triggers: {', '.join(structured['hold_triggers'])}")

    # Add constitutional info
    if "floor_verdicts" in structured:
        floors = structured["floor_verdicts"]
        passed = sum(1 for v in floors.values() if v)
        total = len(floors)
        content_parts.append(f"Constitutional Floors: {passed}/{total} passed")

    content = " | ".join(content_parts)

    # Build meta with app intent if applicable
    meta = {
        "geox_version": GEOX_VERSION,
        "seal": GEOX_SEAL,
    }

    # Check if this result suggests an app intent
    if structured.get("status") == "SEAL" and "views" in structured:
        meta["appIntent"] = {
            "appId": (
                "geox.seismic-viewer" if "line_id" in structured else "geox.generic"
            ),
            "action": "open",
            "params": structured,
            "preferredMode": "inline",
        }

    return ToolResult(
        content=content,
        structured_content=structured,
        meta=meta,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MCP Tool Wrappers (Thin Adapters)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool(name="geox_load_seismic_line")
async def geox_load_seismic_line(
    line_id: str,
    survey_path: str = "default_survey",
    generate_views: bool = True,
) -> dict:
    """Load seismic data and ignite visual mode (Earth Witness Ignition)."""
    # Call core tool
    result = await _core_load_seismic_line(
        line_id=line_id,
        survey_path=survey_path,
        generate_views=generate_views,
        seismic_engine_available=_HAS_SEISMIC,
    )

    # Convert to ToolResult
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_build_structural_candidates")
async def geox_build_structural_candidates(
    line_id: str,
    focus_area: str | None = None,
) -> dict:
    """Build structural model candidates (Inverse Modelling Constraints)."""
    result = await _core_build_structural_candidates(
        line_id=line_id,
        focus_area=focus_area,
        seismic_engine_available=_HAS_SEISMIC,
    )
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_feasibility_check")
async def geox_feasibility_check(
    plan_id: str,
    constraints: list[str],
) -> dict:
    """Constitutional Firewall: Check if a proposed plan is physically possible."""
    result = await _core_feasibility_check(plan_id, constraints)
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_verify_geospatial")
async def geox_verify_geospatial(
    lat: float,
    lon: float,
    radius_m: float = 1000.0,
) -> dict:
    """Verify geospatial grounding and jurisdictional boundaries."""
    result = await _core_verify_geospatial(lat, lon, radius_m)
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_evaluate_prospect")
async def geox_evaluate_prospect(
    prospect_id: str,
    interpretation_id: str,
) -> dict:
    """Provide a governed verdict on a subsurface prospect (222_REFLECT)."""
    result = await _core_evaluate_prospect(prospect_id, interpretation_id)
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_query_memory")
async def geox_query_memory(
    query: str,
    basin: str | None = None,
    limit: int = 5,
) -> dict:
    """Query the GEOX geological memory store for past evaluations."""
    result = await _core_query_memory(
        query=query,
        basin=basin,
        limit=limit,
        memory_store=_memory_store,
    )
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_calculate_saturation")
async def geox_calculate_saturation(
    model: str,  # Literal["archie", "simandoux", "indonesia"]
    params: dict[str, Any],
    n_samples: int = 1000,
) -> dict:
    """Calculate water saturation (Sw) with Monte Carlo uncertainty."""
    result = await _core_calculate_saturation(
        model=model,
        params=params,
        n_samples=n_samples,
        physics_engine_available=_HAS_PHYSICS,
    )
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_select_sw_model")
async def geox_select_sw_model(
    well_id: str,
    depth_top_m: float,
    depth_base_m: float,
    has_washout: bool = False,
    washout_fraction: float = 0.0,
    borehole_quality: str = "good",
    has_invasion: bool = False,
    has_gas_effect: bool = False,
    has_shale: bool = True,
    vsh_max: float = 0.0,
    has_deep_resistivity: bool = True,
    has_shallow_resistivity: bool = False,
    available_curves: list[str] | None = None,
) -> dict:
    """Evaluate Sw model admissibility from log QC flags."""
    result = await _core_select_sw_model(
        well_id=well_id,
        depth_top_m=depth_top_m,
        depth_base_m=depth_base_m,
        has_washout=has_washout,
        washout_fraction=washout_fraction,
        borehole_quality=borehole_quality,
        has_invasion=has_invasion,
        has_gas_effect=has_gas_effect,
        has_shale=has_shale,
        vsh_max=vsh_max,
        has_deep_resistivity=has_deep_resistivity,
        has_shallow_resistivity=has_shallow_resistivity,
        available_curves=available_curves,
        petro_schemas_available=_HAS_PETRO_SCHEMAS,
    )
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_compute_petrophysics")
async def geox_compute_petrophysics(
    well_id: str,
    sw_model: str,
    rw_ohm_m: float,
    rt_ohm_m: float,
    phi_fraction: float,
    vcl_fraction: float = 0.0,
    rsh_ohm_m: float | None = None,
    archie_a: float = 1.0,
    archie_m: float = 2.0,
    archie_n: float = 2.0,
    run_monte_carlo: bool = True,
    mc_samples: int = 1000,
) -> dict:
    """Full petrophysics property pipeline — Vsh, PHIe, Sw, BVW."""
    result = await _core_compute_petrophysics(
        well_id=well_id,
        sw_model=sw_model,
        rw_ohm_m=rw_ohm_m,
        rt_ohm_m=rt_ohm_m,
        phi_fraction=phi_fraction,
        vcl_fraction=vcl_fraction,
        rsh_ohm_m=rsh_ohm_m,
        archie_a=archie_a,
        archie_m=archie_m,
        archie_n=archie_n,
        run_monte_carlo=run_monte_carlo,
        mc_samples=mc_samples,
        physics_engine_available=_HAS_PHYSICS,
        petro_schemas_available=_HAS_PETRO_SCHEMAS,
    )
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_validate_cutoffs")
async def geox_validate_cutoffs(
    well_id: str,
    policy_id: str,
    phi_cutoff: float,
    sw_cutoff: float,
    vcl_cutoff: float,
    phi_tested: float,
    sw_tested: float,
    vcl_tested: float,
    rt_cutoff: float | None = None,
    rt_tested: float | None = None,
    policy_basis: str = "analogue",
) -> dict:
    """Apply a CutoffPolicy to petrophysical values and classify pay vs non-pay."""
    result = await _core_validate_cutoffs(
        well_id=well_id,
        policy_id=policy_id,
        phi_cutoff=phi_cutoff,
        sw_cutoff=sw_cutoff,
        vcl_cutoff=vcl_cutoff,
        phi_tested=phi_tested,
        sw_tested=sw_tested,
        vcl_tested=vcl_tested,
        rt_cutoff=rt_cutoff,
        rt_tested=rt_tested,
        policy_basis=policy_basis,
        petro_schemas_available=_HAS_PETRO_SCHEMAS,
    )
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_petrophysical_hold_check")
async def geox_petrophysical_hold_check(
    well_id: str,
    sw_value: float,
    phi_value: float,
    vcl_value: float,
    uncertainty: float,
    has_deep_resistivity: bool = True,
    borehole_quality: str = "good",
    sw_model: str = "archie",
    check_f2_truth: bool = True,
    check_f4_clarity: bool = True,
    check_f7_humility: bool = True,
    check_f9_anti_hantu: bool = True,
) -> dict:
    """Constitutional floor check for petrophysical outputs — triggers 888_HOLD."""
    result = await _core_petrophysical_hold_check(
        well_id=well_id,
        sw_value=sw_value,
        phi_value=phi_value,
        vcl_value=vcl_value,
        uncertainty=uncertainty,
        has_deep_resistivity=has_deep_resistivity,
        borehole_quality=borehole_quality,
        sw_model=sw_model,
        check_f2_truth=check_f2_truth,
        check_f4_clarity=check_f4_clarity,
        check_f7_humility=check_f7_humility,
        check_f9_anti_hantu=check_f9_anti_hantu,
        petro_schemas_available=_HAS_PETRO_SCHEMAS,
    )
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


@mcp.tool(name="geox_health")
async def geox_health() -> dict:
    """Server health check with constitutional floor status."""
    result = await _core_health(
        geox_version=GEOX_VERSION,
        prefab_ui_available=False,  # Would detect from imports
        seismic_engine_available=_HAS_SEISMIC,
        fastmcp_version=".".join(map(str, FASTMCP_VERSION)),
    )
    tool_result = _result_to_tool_result(result)
    return _tool_result_to_dict(tool_result)


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP Routes (FastMCP-specific)
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from starlette.requests import Request
    from starlette.responses import JSONResponse, PlainTextResponse

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(_: Request) -> PlainTextResponse:
        """Minimal health endpoint."""
        return PlainTextResponse("OK")

    @mcp.custom_route("/health/details", methods=["GET"])
    async def health_details(_: Request) -> JSONResponse:
        """Detailed health endpoint."""
        return JSONResponse(
            {
                "ok": True,
                "service": "geox-earth-witness",
                "version": GEOX_VERSION,
                "mode": "constitutional-governance",
                "forge": "Forge-3-FastMCP" if IS_FASTMCP_3 else "Forge-2-Horizon",
                "fastmcp_version": ".".join(map(str, FASTMCP_VERSION)),
                "seal": GEOX_SEAL,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    HAS_HTTP_ROUTES = True
except ImportError:
    HAS_HTTP_ROUTES = False
    logger.warning("Starlette not available, HTTP routes disabled")


# ═══════════════════════════════════════════════════════════════════════════════
# Factory Function (for fastmcp run server.py:create_server)
# ═══════════════════════════════════════════════════════════════════════════════


def create_server(
    transport: str = "stdio",
    host: str = "0.0.0.0",
    port: int = 8000,
) -> FastMCP:
    """
    Factory function for creating a configured GEOX MCP server.

    Used by FastMCP CLI:
      fastmcp run arifos.geox.tools.adapters.fastmcp_adapter:create_server
      fastmcp run arifos.geox.tools.adapters.fastmcp_adapter:create_server --transport http --port 9000

    Returns the configured FastMCP instance. The CLI handles running it.
    """
    # Update server metadata based on config
    # Note: mcp.name and mcp.version are read-only, but we can log the config

    # Log configuration
    logger.info("=" * 60)
    logger.info("GEOX Earth Witness v%s — %s", GEOX_VERSION, GEOX_SEAL)
    logger.info("FastMCP Version: %s", ".".join(map(str, FASTMCP_VERSION)))
    logger.info("Factory Mode: transport=%s, host=%s, port=%d", transport, host, port)
    logger.info("=" * 60)
    logger.info("HTTP Routes: %s", "enabled" if HAS_HTTP_ROUTES else "disabled")
    logger.info("Prefab UI: %s", "available" if _HAS_PREFAB else "unavailable")
    logger.info("Physics Engine: %s", "available" if _HAS_PHYSICS else "unavailable")
    logger.info("Seismic Engine: %s", "available" if _HAS_SEISMIC else "unavailable")
    logger.info("Memory Store: %s", "available" if _HAS_MEMORY else "unavailable")
    logger.info("Tools (11): geox_load_seismic_line, geox_build_structural_candidates,")
    logger.info("           geox_feasibility_check, geox_verify_geospatial,")
    logger.info("           geox_evaluate_prospect, geox_query_memory, geox_health,")
    logger.info("           geox_select_sw_model, geox_compute_petrophysics,")
    logger.info("           geox_validate_cutoffs, geox_petrophysical_hold_check")
    logger.info("=" * 60)

    return mcp


# ═══════════════════════════════════════════════════════════════════════════════
# CLI Entrypoint
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    """CLI entrypoint for FastMCP server."""
    parser = argparse.ArgumentParser(
        description="GEOX Earth Witness MCP Server — DITEMPA BUKAN DIBERI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  GEOX_TRANSPORT=http|stdio    # Default transport
  GEOX_HOST=0.0.0.0            # HTTP host
  GEOX_PORT=8000               # HTTP port

Examples:
  python -m arifos.geox.tools.adapters.fastmcp_adapter
  python -m arifos.geox.tools.adapters.fastmcp_adapter --transport http --port 8100
        """,
    )
    parser.add_argument(
        "--transport",
        default=os.getenv("GEOX_TRANSPORT", "stdio"),
        choices=["stdio", "http"],
        help="Transport protocol",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("GEOX_HOST", "0.0.0.0"),
        help="HTTP bind host",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("GEOX_PORT", 8000)),
        help="HTTP bind port",
    )
    parser.add_argument("--log-level", default="info", help="Log level")

    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level.upper())

    logger.info("=" * 60)
    logger.info("GEOX Earth Witness v%s — %s", GEOX_VERSION, GEOX_SEAL)
    logger.info("FastMCP Version: %s", ".".join(map(str, FASTMCP_VERSION)))
    logger.info("=" * 60)
    logger.info("Transport: %s", args.transport)
    logger.info("HTTP Routes: %s", "enabled" if HAS_HTTP_ROUTES else "disabled")
    logger.info("Physics Engine: %s", "available" if _HAS_PHYSICS else "unavailable")
    logger.info("Seismic Engine: %s", "available" if _HAS_SEISMIC else "unavailable")
    logger.info("=" * 60)

    if args.transport == "http":
        logger.info("Host: %s | Port: %d", args.host, args.port)
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()

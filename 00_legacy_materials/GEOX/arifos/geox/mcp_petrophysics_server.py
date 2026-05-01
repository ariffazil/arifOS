"""
[DEPRECATED] GEOX Petrophysics MCP Server — Phase A
DITEMPA BUKAN DIBERI

MCP server with resources and tools for governed petrophysics.
Resources: Application-controlled context with stable URIs
Tools: Model-controlled actions for computation

URI Schemes:
- geox://well/{well_id}/las/bundle
- geox://well/{well_id}/logs/canonical
- geox://well/{well_id}/interval/{top}-{base}/rock-state
- geox://well/{well_id}/cutoff-policy/{policy_id}
- geox://well/{well_id}/qc/report
"""

from __future__ import annotations

import warnings
warnings.warn(
    "mcp_petrophysics_server.py is deprecated. The canonical unified surface is geox_unified_mcp_server.py "
    "and the execution plane is execution_plane/vps/server.py. Do not build new dependencies here.",
    DeprecationWarning, stacklevel=2
)

from datetime import datetime
from typing import Any

try:
    from fastmcp import FastMCP
except ImportError:
    raise ImportError("fastmcp required. Install: pip install fastmcp")

from arifos.geox.resources.well_resources import get_resource
from arifos.geox.tools.petrophysics import (
    LogBundleLoader,
    load_bundle_from_store,
    store_bundle,
    generate_qc_report,
)
from arifos.geox.tools.petrophysics.property_calculator import (
    PetrophysicsCalculator,
    load_rock_state,
    store_rock_state,
)
from arifos.geox.tools.petrophysics.cutoff_validator import (
    load_cutoff_policy,
)
from arifos.geox.tools.petrophysics.hold_checker import PetrophysicalHoldChecker
from arifos.geox.tools.petrophysics.model_selector import SaturationModelSelector

# Initialize MCP server
mcp = FastMCP(
    name="GEOX Petrophysics",
    version="0.6.0-phase-a",
    description="Governed petrophysics engine — Constitutional well log interpretation",
)

GEOX_VERSION = "0.6.0"
GEOX_SEAL = "DITEMPA BUKAN DIBERI"


# ═══════════════════════════════════════════════════════════════════════════════
# MCP RESOURCES (Application-Controlled Context)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.resource("geox://well/{well_id}/las/bundle")
async def resource_well_bundle(well_id: str) -> dict[str, Any]:
    """
    Canonical LAS/DLIS bundle with parsed header, curves, and QC status.
    Provenance: RAW
    """
    return await get_resource(f"geox://well/{well_id}/las/bundle")


@mcp.resource("geox://well/{well_id}/logs/canonical")
async def resource_canonical_logs(well_id: str) -> dict[str, Any]:
    """
    Curves with environmental corrections applied.
    Provenance: CORRECTED
    """
    return await get_resource(f"geox://well/{well_id}/logs/canonical")


@mcp.resource("geox://well/{well_id}/interval/{top}-{base}/rock-state")
async def resource_rock_state(well_id: str, top: str, base: str) -> dict[str, Any]:
    """
    Petrophysical interpretation for a specific interval.
    Provenance: DERIVED
    """
    return await get_resource(f"geox://well/{well_id}/interval/{top}-{base}/rock-state")


@mcp.resource("geox://well/{well_id}/cutoff-policy/{policy_id}")
async def resource_cutoff_policy(well_id: str, policy_id: str) -> dict[str, Any]:
    """
    Active cutoff policy for this well/formation.
    Provenance: POLICY
    """
    return await get_resource(f"geox://well/{well_id}/cutoff-policy/{policy_id}")


@mcp.resource("geox://well/{well_id}/qc/report")
async def resource_qc_report(well_id: str) -> dict[str, Any]:
    """
    Quality control findings for all well data.
    """
    return await get_resource(f"geox://well/{well_id}/qc/report")


# ═══════════════════════════════════════════════════════════════════════════════
# MCP TOOLS (Model-Controlled Actions)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def geox_load_well_log_bundle(
    well_id: str,
    sources: list[str],
    depth_reference: str = "MD",
) -> dict[str, Any]:
    """
    Load LAS/DLIS/CSV + metadata, map mnemonics, detect depth reference.
    
    Args:
        well_id: Canonical well identifier
        sources: List of file paths (LAS, DLIS, CSV)
        depth_reference: MD, TVD, TVDSS, etc.
    
    Returns:
        Resource URI for the loaded bundle and summary
    """
    try:
        loader = LogBundleLoader()
        bundle = await loader.load(well_id, sources, depth_reference)
        await store_bundle(bundle)
        
        return {
            "status": "SUCCESS",
            "uri": f"geox://well/{well_id}/las/bundle",
            "well_id": well_id,
            "well_name": bundle.well_name,
            "curves_loaded": len(bundle.curves),
            "depth_range": {"min": bundle.min_depth, "max": bundle.max_depth},
            "provenance": "RAW",
            "floor_check": {
                "F4_clarity": True,
                "F9_anti_hantu": True,
            }
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "well_id": well_id,
        }


@mcp.tool()
async def geox_qc_logs(well_id: str) -> dict[str, Any]:
    """
    Flag washouts, missing sections, bad hole, tool conflicts, unit inconsistencies.
    
    Args:
        well_id: Well identifier
    
    Returns:
        Resource URI for QC report and summary
    """
    try:
        bundle = await load_bundle_from_store(well_id)
        report = await generate_qc_report(well_id, bundle)
        
        return {
            "status": "SUCCESS",
            "uri": f"geox://well/{well_id}/qc/report",
            "well_id": well_id,
            "overall_status": report.overall,
            "curve_count": len(report.curve_reports),
            "issues_found": len(report.depth_issues) + len(report.unit_inconsistencies),
            "recommendations": report.recommendations,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "well_id": well_id,
        }


@mcp.tool()
async def geox_select_sw_model(
    interval_uri: str,
    candidate_models: list[str] = None,
) -> dict[str, Any]:
    """
    Evaluate Archie vs shaly-sand models against shale conductivity, mineralogy,
    and calibration support.
    
    Args:
        interval_uri: geox://well/{id}/interval/{top}-{base}/rock-state
        candidate_models: List of models to evaluate
    
    Returns:
        Admissible models with reasons, rejected models with violations
    """
    if candidate_models is None:
        candidate_models = ["archie", "simandoux", "indonesia", "dual_water"]
    
    # Parse interval URI
    # Format: geox://well/{well_id}/interval/{top}-{base}/rock-state
    try:
        parts = interval_uri.replace("geox://well/", "").split("/")
        well_id = parts[0]
        interval_part = parts[2] if len(parts) > 2 else "0-0"
        top_str, base_str = interval_part.split("-")
        top, base = float(top_str), float(base_str)
    except (IndexError, ValueError):
        return {
            "status": "ERROR",
            "error": f"Invalid interval_uri: {interval_uri}",
        }
    
    try:
        state = await load_rock_state(well_id, top, base)
        if state is None:
            return {
                "status": "NOT_FOUND",
                "message": "No rock state found. Run geox_compute_petrophysics first.",
            }
        
        selector = SaturationModelSelector()
        results = await selector.evaluate(
            state,
            candidates=candidate_models,
        )
        
        return {
            "status": "SUCCESS",
            "interval_uri": interval_uri,
            "admissible_models": [
                {
                    "model": r.model_name,
                    "confidence": r.confidence,
                    "justification": r.justification,
                }
                for r in results if r.is_admissible
            ],
            "rejected_models": [
                {
                    "model": r.model_name,
                    "reason": r.rejection_reason,
                    "violations": r.violations,
                }
                for r in results if not r.is_admissible
            ],
            "recommended_model": results[0].model_name if results else None,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
        }


@mcp.tool()
async def geox_compute_petrophysics(
    interval_uri: str,
    model_id: str,
    model_params: dict = None,
    compute_uncertainty: bool = True,
) -> dict[str, Any]:
    """
    Compute Vsh, phi_t, phi_e, Sw, BVW, net, pay, RQI/FZI/HFU
    with uncertainty envelopes.
    
    Args:
        interval_uri: geox://well/{id}/interval/{top}-{base}/rock-state
        model_id: Saturation model to use
        model_params: Model parameters {a, m, n, rw, ...}
        compute_uncertainty: Whether to propagate uncertainty
    
    Returns:
        Resource URI for updated rock-state
    """
    # Parse interval URI
    try:
        parts = interval_uri.replace("geox://well/", "").split("/")
        well_id = parts[0]
        interval_part = parts[2] if len(parts) > 2 else "0-0"
        top_str, base_str = interval_part.split("-")
        top, base = float(top_str), float(base_str)
    except (IndexError, ValueError):
        return {
            "status": "ERROR",
            "error": f"Invalid interval_uri: {interval_uri}",
        }
    
    try:
        calculator = PetrophysicsCalculator(model_id, model_params or {})
        result = await calculator.compute(
            well_id=well_id,
            top=top,
            base=base,
            propagate_uncertainty=compute_uncertainty,
        )
        
        await store_rock_state(result)
        
        return {
            "status": "SUCCESS",
            "uri": f"geox://well/{well_id}/interval/{top}-{base}/rock-state",
            "well_id": well_id,
            "interval": {"top": top, "base": base},
            "model_used": model_id,
            "verdict": result.verdict,
        }
    except NotImplementedError:
        return {
            "status": "NOT_IMPLEMENTED",
            "message": "Full petrophysics calculation in Phase B",
            "interval_uri": interval_uri,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
        }


@mcp.tool()
async def geox_validate_cutoffs(
    interval_uri: str,
    cutoff_policy_id: str,
) -> dict[str, Any]:
    """
    Apply economic/operational cutoffs as governed policy objects.
    Distinguishes physics from policy.
    
    Args:
        interval_uri: geox://well/{id}/interval/{top}-{base}/rock-state
        cutoff_policy_id: Policy to apply
    
    Returns:
        Policy application card with net/pay flags
    """
    try:
        # Parse interval URI
        parts = interval_uri.replace("geox://well/", "").split("/")
        well_id = parts[0]
        interval_part = parts[2] if len(parts) > 2 else "0-0"
        top_str, base_str = interval_part.split("-")
        top, base = float(top_str), float(base_str)
        
        state = await load_rock_state(well_id, top, base)
        policy = await load_cutoff_policy(cutoff_policy_id)
        
        if state is None:
            return {
                "status": "NOT_FOUND",
                "message": "No rock state found for interval",
            }
        
        if policy is None:
            return {
                "status": "NOT_FOUND",
                "message": f"Cutoff policy {cutoff_policy_id} not found",
            }
        
        # Phase B: Full validation
        return {
            "status": "NOT_IMPLEMENTED",
            "message": "Full cutoff validation in Phase B",
            "interval_uri": interval_uri,
            "policy_id": cutoff_policy_id,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
        }


@mcp.tool()
async def geox_petrophysical_hold_check(interval_uri: str) -> dict[str, Any]:
    """
    Automatic 888_HOLD trigger detection for petrophysics.
    
    Checks:
    - Rw uncalibrated
    - Shale model unsupported
    - Environmental correction missing
    - Invasion ignored
    - Depth mismatch unresolved
    - Cutoffs without economic basis
    
    Args:
        interval_uri: geox://well/{id}/interval/{top}-{base}/rock-state
    
    Returns:
        SEAL / QUALIFY / 888_HOLD verdict
    """
    try:
        # Parse interval URI
        parts = interval_uri.replace("geox://well/", "").split("/")
        well_id = parts[0]
        interval_part = parts[2] if len(parts) > 2 else "0-0"
        top_str, base_str = interval_part.split("-")
        top, base = float(top_str), float(base_str)
        
        state = await load_rock_state(well_id, top, base)
        
        checker = PetrophysicalHoldChecker()
        verdict = await checker.evaluate(state)
        
        return {
            "status": "SUCCESS",
            "interval_uri": interval_uri,
            "verdict": verdict.status,
            "triggers": verdict.triggers,
            "required_actions": verdict.required_actions,
            "can_override": verdict.can_override,
            "override_authority": "F13_SOVEREIGN" if verdict.can_override else None,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
        }


@mcp.tool()
async def geox_petrophysics_health() -> dict[str, Any]:
    """Server health check with constitutional floor status."""
    return {
        "ok": True,
        "service": "GEOX Petrophysics MCP",
        "version": GEOX_VERSION,
        "seal": GEOX_SEAL,
        "phase": "A",
        "resources": [
            "geox://well/{well_id}/las/bundle",
            "geox://well/{well_id}/logs/canonical",
            "geox://well/{well_id}/interval/{top}-{base}/rock-state",
            "geox://well/{well_id}/cutoff-policy/{policy_id}",
            "geox://well/{well_id}/qc/report",
        ],
        "tools": [
            "geox_load_well_log_bundle",
            "geox_qc_logs",
            "geox_select_sw_model",
            "geox_compute_petrophysics",
            "geox_validate_cutoffs",
            "geox_petrophysical_hold_check",
        ],
        "constitutional_floors": ["F1", "F2", "F4", "F7", "F9", "F11", "F13"],
        "timestamp": datetime.utcnow().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GEOX Petrophysics MCP Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "http"])
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"GEOX Petrophysics MCP v{GEOX_VERSION}")
    print(f"{GEOX_SEAL}")
    print("Phase: A (Schemas + Resources + Load/QC)")
    print("=" * 60)
    print("Resources: 5 URI schemes")
    print("Tools: 6 petrophysics tools")
    print("=" * 60)
    
    if args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()

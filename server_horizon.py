"""
Canonical Horizon gateway for the public arifOS entrypoint.
═══════════════════════════════════════════════════════════════════════════════

This file is the policy layer behind ``server.py:mcp`` when running in Horizon
mode. It proxies selected tool calls to the sovereign VPS and publishes the
full gateway contract.

FastMCP Custom Routes:
• GET /health    - Liveness, version, mode, upstream reachability
• GET /metadata  - Full gateway policy, tool counts, deprecation notice

All counts sourced from config/environments.py — single source of truth.
"""

import os
import json
import asyncio
import logging
import functools
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP
from starlette.responses import JSONResponse

from config.environments import (
    TOOL_ACCESS_POLICY,
    ToolAccessClass,
    get_environment,
    HORIZON_CONFIG,
)

# Configuration
VPS_URL = os.getenv("ARIFOS_VPS_URL", "https://arifosmcp.arif-fazil.com")
ARIFOS_GOVERNANCE_SECRET = os.getenv("ARIFOS_GOVERNANCE_SECRET", "")
ARIFOS_VERSION = os.getenv("ARIFOS_VERSION", "2026.03.25")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("horizon-gateway")

# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY POLICY COUNTS (Source of Truth from environments.py)
# ═══════════════════════════════════════════════════════════════════════════════

def _get_tool_policy_counts() -> dict[str, int]:
    """Calculate tool counts from TOOL_ACCESS_POLICY."""
    counts = {
        "public": 0,
        "authenticated": 0,
        "sovereign_only": 0,
    }
    for tool_name, access in TOOL_ACCESS_POLICY.items():
        if access == ToolAccessClass.PUBLIC.value:
            counts["public"] += 1
        elif access == ToolAccessClass.AUTHENTICATED.value:
            counts["authenticated"] += 1
        elif access == ToolAccessClass.SOVEREIGN_ONLY.value:
            counts["sovereign_only"] += 1
    return counts


# ═══════════════════════════════════════════════════════════════════════════════
# UPSTREAM REACHABILITY CHECK
# ═══════════════════════════════════════════════════════════════════════════════

async def _check_upstream_vps() -> dict[str, Any]:
    """Check if upstream VPS is reachable."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{VPS_URL}/health",
                headers={"X-ArifOS-Source": "Horizon-HealthCheck"},
            )
            if response.status_code == 200:
                return {
                    "status": "reachable",
                    "http_status": response.status_code,
                }
            return {
                "status": "degraded",
                "http_status": response.status_code,
                "error": "Non-200 response",
            }
    except Exception as e:
        return {
            "status": "unreachable",
            "error": str(e),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FASTMCP SERVER
# ═══════════════════════════════════════════════════════════════════════════════

mcp = FastMCP("arifOS Horizon Gateway")

# Tool policy counts (cached at module load)
TOOL_COUNTS = _get_tool_policy_counts()


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM ROUTES: /health and /metadata
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.custom_route("/health", methods=["GET"])
async def health_endpoint(request) -> JSONResponse:
    """
    Horizon gateway health check.
    
    Returns:
        - status: ok|degraded|hold
        - mode: horizon_gateway
        - version: arifOS version
        - protocol_version: MCP protocol version
        - timestamp: ISO UTC timestamp
        - tool_policy: counts of public/authenticated/sovereign tools
        - auth_status: current auth mode
        - upstream_vps: reachability status
        - entrypoint: canonical entrypoint
    """
    env = get_environment()
    upstream = await _check_upstream_vps()
    
    # Determine overall status
    status = "ok"
    if upstream["status"] != "reachable":
        status = "degraded"
    
    return JSONResponse({
        "status": status,
        "mode": "horizon_gateway",
        "version": ARIFOS_VERSION,
        "protocol_version": "2025-03-26",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entrypoint": "server.py:mcp",
        "tool_policy": TOOL_COUNTS,
        "auth_status": "public_only",
        "upstream_vps": upstream,
        "floors": env.constitutional_floors,
    })


@mcp.custom_route("/metadata", methods=["GET"])
async def metadata_endpoint(request) -> JSONResponse:
    """
    Full gateway metadata and policy disclosure.
    
    Returns complete gateway configuration including:
        - Gateway identity and version
        - Tool policy with counts
        - Public tool manifest
        - Deprecated paths notice
        - Environment configuration
    """
    env = get_environment()
    upstream = await _check_upstream_vps()
    
    # Build public tools list
    public_tools = [
        name for name, access in TOOL_ACCESS_POLICY.items()
        if access == ToolAccessClass.PUBLIC.value
    ]
    authenticated_tools = [
        name for name, access in TOOL_ACCESS_POLICY.items()
        if access == ToolAccessClass.AUTHENTICATED.value
    ]
    sovereign_only_tools = [
        name for name, access in TOOL_ACCESS_POLICY.items()
        if access == ToolAccessClass.SOVEREIGN_ONLY.value
    ]
    
    return JSONResponse({
        "gateway": {
            "name": env.name,
            "version": ARIFOS_VERSION,
            "mode": "horizon_gateway",
            "protocol_version": "2025-03-26",
            "entrypoint": "server.py:mcp",
            "base_url": env.base_url,
        },
        "tool_policy": {
            "counts": TOOL_COUNTS,
            "public_tools": public_tools,
            "authenticated_tools": authenticated_tools,
            "sovereign_only_tools": sovereign_only_tools,
        },
        "auth": {
            "status": "public_only",
            "required": env.auth_required,
            "rate_limit": {
                "enabled": env.rate_limit_enabled,
                "capacity": int(os.getenv("ARIFOS_RATE_LIMIT_CAPACITY", "120")),
                "refill_per_sec": float(os.getenv("ARIFOS_RATE_LIMIT_REFILL_PER_SEC", "2.0")),
            },
        },
        "upstream": {
            "vps_url": VPS_URL,
            "reachability": upstream,
        },
        "deprecated_paths": {
            "removed": ["horizon/server.py", "arifos_mcp/server_horizon.py"],
            "canonical": "server.py",
            "note": "Use server.py:mcp as the single entrypoint for all deployments",
        },
        "constitutional": {
            "floors_enforced": env.constitutional_floors,
            "thermo_budget_multiplier": env.thermo_budget_multiplier,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC TOOL PROXIES
# ═══════════════════════════════════════════════════════════════════════════════

async def _proxy_to_vps(tool_name: str, arguments: dict) -> dict:
    """Helper to forward tool calls to the sovereign VPS."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{VPS_URL}/tools/{tool_name}",
                json=arguments,
                headers={
                    "X-ArifOS-Source": "Horizon",
                    "X-ArifOS-Secret": ARIFOS_GOVERNANCE_SECRET,
                    "Accept": "application/json",
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("result", data)
            return {"error": f"Sovereign Kernel error: {response.status_code}", "verdict": "SABAR"}
    except Exception as e:
        logger.error(f"Ambassador link severed: {e}")
        return {"error": "Ambassador link severed", "details": str(e), "verdict": "SABAR"}


def _make_proxy(tool_name: str, description: str):
    """Factory to create properly named proxy functions."""
    async def proxy_fn(arguments: dict | None = None) -> dict:
        """Proxy call to sovereign VPS."""
        return await _proxy_to_vps(tool_name, arguments or {})
    
    # Set function metadata for FastMCP introspection
    proxy_fn.__name__ = tool_name
    proxy_fn.__doc__ = description
    return proxy_fn


# Register all public tools
PUBLIC_TOOL_DESCRIPTIONS = {
    "init_anchor": "000_INIT: Initialize constitutional session anchor.",
    "arifOS_kernel": "444_ROUTER: Primary metabolic conductor.",
    "apex_judge": "888_JUDGE: Constitutional verdict engine.",
    "agi_mind": "333_MIND: Reasoning and synthesis engine.",
    "asi_heart": "666_HEART: Safety and empathy critique.",
    "physics_reality": "111_SENSE: Reality grounding and temporal intelligence.",
    "math_estimator": "777_OPS: Thermodynamic vitals and cost estimation.",
    "architect_registry": "000_INIT: Tool and resource discovery.",
    "compat_probe": "M-5_COMPAT: Interoperability and enum audit.",
    "agi_reason": "333_MIND: First-principles reasoning.",
    "agi_reflect": "333_MIND: Reflective synthesis and critique.",
    "asi_critique": "666_HEART: Harm and alignment critique.",
    "asi_simulate": "666_HEART: Consequence and scenario simulation.",
    "reality_compass": "111_SENSE: Directional grounding.",
    "reality_atlas": "111_SENSE: Contextual reality mapping.",
    "search_reality": "111_SENSE: Evidence-grounded search.",
    "ingest_evidence": "111_SENSE: Evidence ingestion.",
    "check_vital": "777_OPS: Runtime health signal.",
    "audit_rules": "888_JUDGE: Rule and policy audit.",
    "search_tool": "Search for indexed documents.",
    "fetch_tool": "Fetch indexed document content by ID.",
}

for tool_name, description in PUBLIC_TOOL_DESCRIPTIONS.items():
    proxy_fn = _make_proxy(tool_name, description)
    mcp.add_tool(proxy_fn)


logger.info(f"[HORIZON] Gateway initialized with {len(PUBLIC_TOOL_DESCRIPTIONS)} public tools")
logger.info(f"[HORIZON] Tool policy: {TOOL_COUNTS['public']} public, "
            f"{TOOL_COUNTS['authenticated']} auth, "
            f"{TOOL_COUNTS['sovereign_only']} sovereign")

__all__ = ["mcp"]

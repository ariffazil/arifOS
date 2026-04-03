"""
Canonical Horizon gateway for the public arifOS entrypoint.
═══════════════════════════════════════════════════════════════════════════════

FastMCP 2.x Compatible Version (Horizon uses 2.12.3, not 3.x)
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP

# FastMCP 2.x compatible imports
from starlette.responses import JSONResponse
from starlette.routing import Route

from config.environments import (
    TOOL_ACCESS_POLICY,
    ToolAccessClass,
    get_environment,
)

# Configuration
VPS_URL = os.getenv("ARIFOS_VPS_URL", "https://arifosmcp.arif-fazil.com")
ARIFOS_GOVERNANCE_SECRET = os.getenv("ARIFOS_GOVERNANCE_SECRET", "")
ARIFOS_VERSION = os.getenv("ARIFOS_VERSION", "2026.03.25")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("horizon-gateway")

# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY POLICY COUNTS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_tool_policy_counts() -> dict[str, int]:
    """Calculate tool counts from TOOL_ACCESS_POLICY."""
    counts = {"public": 0, "authenticated": 0, "sovereign_only": 0}
    for tool_name, access in TOOL_ACCESS_POLICY.items():
        if access == ToolAccessClass.PUBLIC.value:
            counts["public"] += 1
        elif access == ToolAccessClass.AUTHENTICATED.value:
            counts["authenticated"] += 1
        elif access == ToolAccessClass.SOVEREIGN_ONLY.value:
            counts["sovereign_only"] += 1
    return counts

# ═══════════════════════════════════════════════════════════════════════════════
# UPSTREAM CHECK
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
                return {"status": "reachable", "http_status": response.status_code}
            return {"status": "degraded", "http_status": response.status_code, "error": "Non-200"}
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# HANDLERS (Starlette compatible)
# ═══════════════════════════════════════════════════════════════════════════════

async def health_handler(request):
    """Health check endpoint."""
    env = get_environment()
    upstream = await _check_upstream_vps()
    status = "ok" if upstream["status"] == "reachable" else "degraded"
    
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


async def metadata_handler(request):
    """Metadata endpoint."""
    env = get_environment()
    upstream = await _check_upstream_vps()
    
    public_tools = [n for n, a in TOOL_ACCESS_POLICY.items() if a == ToolAccessClass.PUBLIC.value]
    auth_tools = [n for n, a in TOOL_ACCESS_POLICY.items() if a == ToolAccessClass.AUTHENTICATED.value]
    sov_tools = [n for n, a in TOOL_ACCESS_POLICY.items() if a == ToolAccessClass.SOVEREIGN_ONLY.value]
    
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
            "authenticated_tools": auth_tools,
            "sovereign_only_tools": sov_tools,
        },
        "auth": {
            "status": "public_only",
            "required": env.auth_required,
        },
        "upstream": {
            "vps_url": VPS_URL,
            "reachability": upstream,
        },
        "deprecated_paths": {
            "removed": ["horizon/server.py"],
            "canonical": "server.py",
        },
        "constitutional": {
            "floors_enforced": env.constitutional_floors,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# FASTMCP SERVER (2.x compatible)
# ═══════════════════════════════════════════════════════════════════════════════

mcp = FastMCP("arifOS Horizon Gateway")
TOOL_COUNTS = _get_tool_policy_counts()

# ═══════════════════════════════════════════════════════════════════════════════
# ADD CUSTOM ROUTES (FastMCP 2.x way)
# ═══════════════════════════════════════════════════════════════════════════════

def _add_custom_routes():
    """Add custom routes to the underlying Starlette app."""
    try:
        # Get the underlying app - different methods for different FastMCP versions
        app = None
        if hasattr(mcp, '_app'):
            app = mcp._app
        elif hasattr(mcp, 'app'):
            app = mcp.app
        
        if app and hasattr(app, 'routes'):
            # Add routes directly
            app.routes.insert(0, Route("/health", health_handler, methods=["GET"]))
            app.routes.insert(0, Route("/metadata", metadata_handler, methods=["GET"]))
            logger.info("[HORIZON] Custom routes added via app.routes")
    except Exception as e:
        logger.warning(f"[HORIZON] Could not add custom routes via app: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC TOOL PROXIES
# ═══════════════════════════════════════════════════════════════════════════════

async def _proxy_to_vps(tool_name: str, arguments: dict) -> dict:
    """Forward tool calls to sovereign VPS."""
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
        return {"error": "Ambassador link severed", "details": str(e), "verdict": "SABAR"}


# Define proxy functions for public tools
PUBLIC_TOOLS = [
    "init_anchor", "arifOS_kernel", "apex_judge", "agi_mind", "asi_heart",
    "physics_reality", "math_estimator", "architect_registry", "compat_probe",
    "agi_reason", "agi_reflect", "asi_critique", "asi_simulate",
    "reality_compass", "reality_atlas", "search_reality", "ingest_evidence",
    "check_vital", "audit_rules", "search_tool", "fetch_tool",
]

for tool_name in PUBLIC_TOOLS:
    # Create proxy with proper closure
    def make_proxy(name):
        async def proxy_fn(**kwargs) -> dict:
            return await _proxy_to_vps(name, kwargs)
        proxy_fn.__name__ = name
        return proxy_fn
    
    mcp.add_tool(make_proxy(tool_name))


# Try to add custom routes
try:
    _add_custom_routes()
except Exception as e:
    logger.warning(f"[HORIZON] Route registration deferred: {e}")


logger.info(f"[HORIZON] Gateway initialized: {TOOL_COUNTS['public']} public tools")

__all__ = ["mcp"]

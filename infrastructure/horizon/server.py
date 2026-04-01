"""
arifOS Horizon Ambassador - FastMCP 2.x Compatible Real Proxy

This server runs on Prefect Horizon (FastMCP 2.12.3) and forwards all
tool calls to the full arifOS Sovereign Kernel running on the VPS.
"""

import os
import httpx
import logging
from fastmcp import FastMCP

# Configuration
VPS_URL = os.getenv("ARIFOS_VPS_URL", "https://arifosmcp.arif-fazil.com/mcp")
# Note: Horizon will set this if you provide it in the dashboard
ARIFOS_GOVERNANCE_SECRET = os.getenv("ARIFOS_GOVERNANCE_SECRET", "")

# Create minimal MCP server (FastMCP 2.x compatible)
mcp = FastMCP("arifOS Public Ambassador")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("horizon-ambassador")

async def _proxy_to_vps(tool_name: str, arguments: dict) -> dict:
    """Helper to forward tool calls to the VPS Kernel via WebMCP/HTTP."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # We call the VPS's tool endpoint
            # Assuming the VPS exposes a standard WebMCP or tool router
            # For standard FastMCP HTTP, the endpoint is usually /tools/{name}
            # Adjusting to call the unified kernel router if needed
            
            payload = {
                "tool": tool_name,
                "arguments": arguments,
                "governance_secret": ARIFOS_GOVERNANCE_SECRET,
                "deployment_source": "horizon_ambassador"
            }
            
            logger.info(f"Proxying {tool_name} to VPS...")
            # Using the VPS tool call endpoint
            response = await client.post(
                f"{VPS_URL}/call/{tool_name}", 
                json=arguments,
                headers={"X-ArifOS-Source": "Horizon"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"VPS Kernel returned status {response.status_code}",
                    "details": response.text,
                    "verdict": "SABAR"
                }
    except Exception as e:
        logger.error(f"Proxy failure: {str(e)}")
        return {
            "error": "Failed to connect to Sovereign Kernel",
            "details": str(e),
            "verdict": "SABAR",
            "action": "Ensure VPS is online and ARIFOS_VPS_URL is correct"
        }

@mcp.tool()
async def init_anchor(actor_id: str, declared_name: str = None, intent: str = None) -> dict:
    """000_INIT: Initialize constitutional session anchor."""
    return await _proxy_to_vps("init_anchor", {"actor_id": actor_id, "declared_name": declared_name, "intent": intent})

@mcp.tool()
async def arifOS_kernel(query: str, risk_tier: str = "medium") -> dict:
    """444_ROUTER: Primary metabolic conductor."""
    return await _proxy_to_vps("arifOS_kernel", {"query": query, "risk_tier": risk_tier})

@mcp.tool()
async def agi_mind(query: str, mode: str = "reason") -> dict:
    """333_MIND: Reasoning and synthesis engine (QTT-enabled)."""
    return await _proxy_to_vps("agi_mind", {"query": query, "mode": mode})

@mcp.tool()
async def apex_soul(query: str, mode: str = "judge") -> dict:
    """888_JUDGE: Constitutional verdict engine."""
    return await _proxy_to_vps("apex_soul", {"query": query, "mode": mode})

@mcp.tool()
async def asi_heart(content: str, mode: str = "critique") -> dict:
    """666_HEART: Safety and Red-Team (W4) audit."""
    return await _proxy_to_vps("asi_heart", {"content": content, "mode": mode})

@mcp.tool()
async def physics_reality(mode: str = "search", query: str = None) -> dict:
    """111_SENSE: Reality grounding and temporal intelligence."""
    return await _proxy_to_vps("physics_reality", {"mode": mode, "query": query})

@mcp.tool()
async def math_estimator(mode: str = "health") -> dict:
    """777_OPS: Thermodynamic vitals and cost estimation."""
    return await _proxy_to_vps("math_estimator", {"mode": mode})

@mcp.tool()
async def architect_registry(mode: str = "list") -> dict:
    """000_INIT: Tool and resource discovery."""
    return await _proxy_to_vps("architect_registry", {"mode": mode})

if __name__ == "__main__":
    mcp.run()

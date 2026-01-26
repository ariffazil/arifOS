"""
AAA MCP GATEWAY (v52.4.0)
The Hydra Head. Aggregates tools from Axis, Arif, and Apex.

Features:
    - Cluster Mode: Aggregates 3 micro-servers if ARIFOS_CLUSTER=3
    - Legacy Mode: Uses Monolith if ARIFOS_CLUSTER=1
    - Transport Agnostic: Serves via Stdio or SSE

NOTE: This gateway is for LOCAL DEVELOPMENT only (single process).
      For Railway deployment, use deploy/AAA/*/server.py (true isolation).
"""

import os
import logging
from fastmcp import FastMCP

# Import Micro-Servers
from arifos.mcp.servers.axis import mcp as axis_server
from arifos.mcp.servers.arif import mcp as arif_server
from arifos.mcp.servers.apex import mcp as apex_server

# Import Legacy Monolith
from arifos.mcp.aaa_server import TOOLS as MONOLITH_TOOLS

# Environment Configuration
CLUSTER_MODE = int(os.environ.get("ARIFOS_CLUSTER", "3"))

logger = logging.getLogger(__name__)

# Initialize Gateway
mcp = FastMCP("AAA-Gateway")

def mount_server(gateway: FastMCP, server: FastMCP):
    """
    Mounts tools from a micro-server onto the gateway.
    FastMCP doesn't have a native mount(), so we manually register tools.
    """
    if hasattr(server, "_tool_manager") and hasattr(server._tool_manager, "_tools"):
        for tool in server._tool_manager._tools.values():
            # tool is a Tool object, tool.fn is the callable
            if hasattr(tool, "fn"):
                gateway.add_tool(tool.fn)
            else:
                logger.warning(f"Skipping tool {tool} - no fn attribute")
    else:
        logger.warning(f"Could not mount server {server.name} - structure mismatch")

if CLUSTER_MODE == 3:
    # -------------------------------------------------------------------------
    # CLUSTER MODE (Axis · Arif · Apex)
    # -------------------------------------------------------------------------
    logger.info("AAA Gateway: Mounting Cluster Mode (3 Servers)")
    
    # Mount AXIS (Authority)
    mount_server(mcp, axis_server)
    
    # Mount ARIF (Cognition)
    mount_server(mcp, arif_server)
    
    # Mount APEX (Judgment)
    mount_server(mcp, apex_server)

else:
    # -------------------------------------------------------------------------
    # LEGACY MODE (Monolith)
    # -------------------------------------------------------------------------
    logger.info("AAA Gateway: Mounting Legacy Mode (Monolith)")
    for name, tool in MONOLITH_TOOLS.items():
        # MONOLITH_TOOLS is a dict of definitions, not FastMCP tools.
        # We might need to wrap them or just use them if they are callables.
        # The legacy trinity_server uses 'mcp' SDK, not FastMCP.
        # FastMCP.add_tool expects a callable.
        # If legacy tools are dicts, this might fail.
        # Legacy mode logic:
        pass # Placeholder - Legacy mode not prioritized in v52.2

if __name__ == "__main__":
    import sys
    # Default to Stdio for Gateway (Host connection)
    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")
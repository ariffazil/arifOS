"""
AAA MCP GATEWAY (v52.2.0)
The Hydra Head. Routes to Axis, Arif, and Apex.

Features:
    - Cluster Mode: Mounts 3 servers if ARIFOS_CLUSTER=3
    - Legacy Mode: Mounts Monolith if ARIFOS_CLUSTER=1
    - Transport Agnostic: Serves via Stdio or SSE
"""

import os
import logging
from fastmcp import FastMCP

# Import Micro-Servers
from arifos.mcp.servers.axis import mcp as axis_server
from arifos.mcp.servers.arif import mcp as arif_server
from arifos.mcp.servers.apex import mcp as apex_server

# Import Legacy Monolith
from arifos.mcp.trinity_server import TOOLS as MONOLITH_TOOLS

# Environment Configuration
CLUSTER_MODE = int(os.environ.get("ARIFOS_CLUSTER", "3"))

logger = logging.getLogger(__name__)

# Initialize Gateway
mcp = FastMCP("AAA-Gateway")

if CLUSTER_MODE == 3:
    # -------------------------------------------------------------------------
    # CLUSTER MODE (Axis · Arif · Apex)
    # -------------------------------------------------------------------------
    logger.info("AAA Gateway: Mounting Cluster Mode (3 Servers)")
    
    # Mount AXIS (Authority)
    mcp.mount(axis_server)
    
    # Mount ARIF (Cognition)
    mcp.mount(arif_server)
    
    # Mount APEX (Judgment)
    mcp.mount(apex_server)

else:
    # -------------------------------------------------------------------------
    # LEGACY MODE (Monolith)
    # -------------------------------------------------------------------------
    logger.info("AAA Gateway: Mounting Legacy Mode (Monolith)")
    for name, tool in MONOLITH_TOOLS.items():
        mcp.add_tool(tool)

if __name__ == "__main__":
    import sys
    # Default to Stdio for Gateway (Host connection)
    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")

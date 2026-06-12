"""Entry point for arifOS MCP Gateway — run as standalone service.

Usage:
    python -m arifosmcp.gateway
    ARIFOS_GATEWAY_CONFIG=/path/to/config.yaml python -m arifosmcp.gateway
"""

from __future__ import annotations

import os
import sys

import uvicorn


def main() -> None:
    host = os.environ.get("ARIFOS_GATEWAY_HOST", "127.0.0.1")
    port = int(os.environ.get("ARIFOS_GATEWAY_PORT", "8090"))

    # Ensure arifOS package is on path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    uvicorn.run(
        "arifosmcp.gateway.server:app",
        host=host,
        port=port,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()

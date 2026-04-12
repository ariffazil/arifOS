#!/usr/bin/env python3
"""
Dual Transport Entrypoint for arifOS MCP Server
Runs both HTTP (streamable-http on 8080) and SSE (on 8089) transports.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import logging
import sys

import uvicorn
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


async def run_dual_transport() -> None:
    """Run both HTTP (streamable-http on 8080) and SSE (on 8089) transports."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    # Import the app factory and MCP instance
    from arifosmcp.runtime.server import mcp, app, sse_app

    http_config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8080,
        timeout_graceful_shutdown=2,
        lifespan="on",
        ws="websockets-sansio",
        log_level="info",
    )
    sse_config = uvicorn.Config(
        sse_app,
        host="0.0.0.0",
        port=8089,
        timeout_graceful_shutdown=2,
        lifespan="on",
        ws="websockets-sansio",
        log_level="info",
    )

    http_server = uvicorn.Server(http_config)
    sse_server = uvicorn.Server(sse_config)

    logger.info("=" * 60)
    logger.info("ARIFOS MCP v2 — DUAL TRANSPORT SEALED")
    logger.info("  HTTP (streamable-http): http://0.0.0.0:8080/mcp")
    logger.info("  SSE (A2A agents):       http://0.0.0.0:8089/sse")
    logger.info("=" * 60)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(http_server.serve())
        tg.create_task(sse_server.serve())


if __name__ == "__main__":
    asyncio.run(run_dual_transport())

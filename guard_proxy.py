#!/usr/bin/env python3
"""
arifos_http_guard_proxy.py — HTTP Proxy that applies constitutional_guard

Runs in front of the FastMCP server and applies F1-F13 floor enforcement
to all tool outputs before they reach the client.

Usage:
    python arifos_http_guard_proxy.py [--host HOST] [--port PORT] [--target TARGET]

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from aiohttp import web

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

try:
    from arifos.runtime.middleware.constitutional_guard import constitutional_guard
except ImportError:
    try:
        from arifos.core.middleware.constitutional_guard import constitutional_guard
    except ImportError:
        constitutional_guard = None
        logger.warning("constitutional_guard not found, proxy will pass through unguarded")


async def proxy_handler(request: web.Request) -> web.Response:
    """Proxy /mcp requests, applying constitutional_guard to responses."""
    target_url = request.app["target_url"]
    data = await request.read()

    headers = dict(request.headers)
    headers.pop("Host", None)

    async with request.app["session"].request(
        method="POST",
        url=f"{target_url}/mcp",
        data=data,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=60),
    ) as response:
        body = await response.read()

        if response.status != 200 or constitutional_guard is None:
            return web.Response(
                body=body,
                status=response.status,
                headers=dict(response.headers),
                content_type=response.content_type,
            )

        text = body.decode("utf-8")
        lines = text.strip().split("\n")
        guarded_lines = []

        for line in lines:
            if not line.startswith("data: "):
                guarded_lines.append(line)
                continue

            data_str = line[6:].strip()
            if not data_str:
                guarded_lines.append(line)
                continue

            try:
                parsed = json.loads(data_str)
                tool_name = None

                if parsed.get("result", {}).get("content"):
                    content = parsed["result"]["content"]
                    if isinstance(content, list):
                        for block in content:
                            if block.get("type") == "text":
                                try:
                                    tool_output = json.loads(block["text"])
                                    if isinstance(tool_output, dict):
                                        tool_name = tool_output.get("tool", "unknown")
                                        guarded = constitutional_guard(tool_name, tool_output)
                                        block["text"] = json.dumps(guarded, ensure_ascii=False)
                                        break
                                except (json.JSONDecodeError, TypeError, KeyError):
                                    continue

                guarded_lines.append("data: " + json.dumps(parsed, ensure_ascii=False))

            except (json.JSONDecodeError, KeyError, TypeError):
                guarded_lines.append(line)

        guarded_body = "\n".join(guarded_lines).encode("utf-8")

        return web.Response(
            body=guarded_body,
            status=response.status,
            headers=dict(response.headers),
            content_type=response.content_type,
        )


async def health_handler(request: web.Request) -> web.Response:
    """Health check endpoint."""
    target_url = request.app["target_url"]

    async with request.app["session"].head(target_url) as response:
        return web.Response(
            text="healthy",
            status=200 if response.status == 200 else 503,
        )


async def root_handler(request: web.Request) -> web.Response:
    """Root endpoint redirect to health."""
    return web.Response(
        text="arifos HTTP Guard Proxy - forward /mcp to access MCP server",
        content_type="text/plain",
    )


def create_app(target_url: str) -> web.Application:
    """Create the aiohttp application."""
    import aiohttp

    app = web.Application()
    app["target_url"] = target_url
    app["session"] = aiohttp.ClientSession()

    app.router.add_get("/", root_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_post("/mcp", proxy_handler)

    return app


def main():
    parser = argparse.ArgumentParser(description="arifos HTTP Guard Proxy")
    parser.add_argument("--host", default="127.0.0.1", help="Proxy host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8081, help="Proxy port (default: 8081)")
    parser.add_argument("--target", default="http://localhost:8080", help="Target MCP server URL")
    args = parser.parse_args()

    logger.info(f"Starting HTTP Guard Proxy on {args.host}:{args.port}")
    logger.info(f"Targeting MCP server at {args.target}")

    if constitutional_guard is not None:
        logger.info("constitutional_guard loaded - all tool outputs will be guarded")
    else:
        logger.warning("constitutional_guard NOT available - proxy will pass through unguarded")

    app = create_app(args.target)
    web.run_app(app, host=args.host, port=args.port, shutdown_timeout=60)


if __name__ == "__main__":
    main()
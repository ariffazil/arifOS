from __future__ import annotations

"""arifOS Unified Server (root entrypoint).

LEGACY WRAPPER around `python -m arifosmcp.runtime`.
This file is kept for backward compatibility with existing documentation.
New deployments should prefer calling the module directly.

USAGE:
    python server.py                  # default: sse
    python server.py --mode stdio     # stdio (Claude Desktop)
"""

import argparse
import logging
import os
import sys

logger = logging.getLogger("arifOS")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr)

VALID_MODES = {"rest", "sse", "http", "stdio"}
DEFAULT_MODE = "sse"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080


def _normalize_mode(mode: str | None) -> str:
    normalized = (mode or DEFAULT_MODE).strip().lower()
    if normalized not in VALID_MODES:
        logger.warning(f"[arifOS] invalid ARIFOS_MODE '{mode}', falling back to '{DEFAULT_MODE}'")
        return DEFAULT_MODE
    return normalized


def _safe_env_port() -> int:
    raw_port = os.getenv("PORT", str(DEFAULT_PORT)).strip()
    try:
        port = int(raw_port)
    except ValueError:
        logger.warning(f"[arifOS] invalid PORT '{raw_port}', falling back to {DEFAULT_PORT}")
        return DEFAULT_PORT
    return port


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="arifOS Unified Server (root entrypoint)")
    parser.add_argument(
        "--mode",
        choices=sorted(VALID_MODES),
        default=_normalize_mode(os.getenv("ARIFOS_MODE", DEFAULT_MODE)),
        help="Server mode (default: sse)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", DEFAULT_HOST),
        help="Bind host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_safe_env_port(),
        help="Bind port (default: 8080)",
    )
    return parser


def _validate_network_args(mode: str, host: str, port: int) -> None:
    if mode == "stdio":
        return
    if not host.strip():
        raise SystemExit("[arifOS] host cannot be empty for network transports")
    if port < 1 or port > 65535:
        raise SystemExit(f"[arifOS] invalid port {port}, expected 1-65535")


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    mode = _normalize_mode(args.mode)
    host = args.host.strip() or DEFAULT_HOST
    port = args.port
    _validate_network_args(mode, host, port)

    if mode == "rest":
        from arifosmcp.transport.rest import main as rest_main

        os.environ["HOST"] = host
        os.environ["PORT"] = str(port)
        logger.info(f"[arifOS] REST bridge on {host}:{port}")
        rest_main()
        return

    from arifosmcp.transport.server import create_unified_mcp_server

    mcp = create_unified_mcp_server()

    if mode == "stdio":
        logger.info("[arifOS] FastMCP STDIO transport")
        mcp.run(transport="stdio")
        return

    if mode == "sse":
        logger.info(f"[arifOS] FastMCP SSE transport on {host}:{port}")
        mcp.run(transport="sse", host=host, port=port)
        return

    if mode == "http":
        logger.info(f"[arifOS] FastMCP HTTP transport on {host}:{port}")
        mcp.run(transport="http", host=host, port=port)
        return

    raise SystemExit(2)


if __name__ == "__main__":
    main()

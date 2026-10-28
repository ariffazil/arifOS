"""arifosmcp/tools/resource_bridge.py — Resource Tools Bridge for External Orchestrators.

Provides callable tool interfaces for reading and searching FastMCP resources, bridging
clients like Microsoft Copilot Studio that do not support custom URI schemes or
native MCP resource exploration.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def read_resource(uri: str) -> dict[str, Any]:
    """Read a registered MCP resource by URI.

    Use this when your client does not support reading MCP resources directly
    or when custom URI schemes (skill://, arifos://) cannot be fetched natively.
    """
    from arifosmcp.server import mcp

    try:
        res = await mcp.read_resource(uri)
        content_text = ""
        mime_type = "text/plain"
        if hasattr(res, "contents") and res.contents:
            first = res.contents[0]
            content_text = getattr(first, "content", "") or getattr(first, "text", "")
            mime_type = getattr(first, "mime_type", "text/plain") or "text/plain"
        return {
            "status": "ok",
            "uri": uri,
            "mime_type": mime_type,
            "content": content_text,
        }
    except Exception as e:
        logger.warning(f"read_resource failed for URI {uri}: {e}")
        return {
            "status": "error",
            "uri": uri,
            "error": str(e),
        }


async def search_resources(query: str = "") -> dict[str, Any]:
    """Search or list available MCP resources by keyword in URI, name, or description.

    Returns a list of matching resources with their URI, name, and description.
    """
    from arifosmcp.server import mcp

    try:
        all_res = await mcp.list_resources()
        q = (query or "").strip().lower()
        matches = []
        for r in all_res:
            uri_str = str(getattr(r, "uri", ""))
            name_str = str(getattr(r, "name", ""))
            desc_str = str(getattr(r, "description", "") or "")
            if not q or (q in uri_str.lower() or q in name_str.lower() or q in desc_str.lower()):
                matches.append(
                    {
                        "uri": uri_str,
                        "name": name_str,
                        "description": desc_str,
                        "mime_type": getattr(r, "mime_type", "text/plain") or "text/plain",
                    }
                )
        return {
            "status": "ok",
            "query": query,
            "count": len(matches),
            "resources": matches,
        }
    except Exception as e:
        logger.warning(f"search_resources failed: {e}")
        return {
            "status": "error",
            "query": query,
            "error": str(e),
        }


def register_resource_bridge(mcp_server: Any) -> list[str]:
    """Register read_resource and search_resources as callable tools."""
    registered = []
    try:
        mcp_server.tool(
            name="read_resource",
            description="Read a registered knowledge resource by URI (e.g. arifos://vitals, arifos://carry-forward).",
            tags={"bridge", "resources", "read-only"},
            annotations={"readOnlyHint": True, "destructiveHint": False},
        )(read_resource)
        registered.append("read_resource")

        mcp_server.tool(
            name="search_resources",
            description="Search or list available knowledge resources by keyword in URI, name, or description.",
            tags={"bridge", "resources", "read-only"},
            annotations={"readOnlyHint": True, "destructiveHint": False},
        )(search_resources)
        registered.append("search_resources")
        logger.info("RESOURCE BRIDGE: registered read_resource and search_resources tools")
    except Exception as exc:
        logger.warning("Failed to register resource bridge tools: %s", exc)
    return registered

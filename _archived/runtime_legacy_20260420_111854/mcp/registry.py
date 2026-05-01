from __future__ import annotations
"""
usr/lib/arifOS/mcp/registry.py
═════════════════════════════════
AUTO-GENERATED FROM CANONICAL MANIFEST.
NEVER HAND-EDIT THIS FILE.
"""

import yaml
from typing import Any, Callable
from fastmcp import FastMCP

def load_manifest(path: str = "/etc/arifOS/manifest/canonical_manifest.yaml") -> dict[str, Any]:
    """Source manifest loader."""
    import os
    # Local dev fallback if /etc not yet populated in container
    if not os.path.exists(path):
        path = "etc/arifOS/manifest/canonical_manifest.yaml"
        
    with open(path, "r") as f:
        return yaml.safe_load(f)

def register_canonical_tools(mcp: FastMCP, handler_map: dict[str, Callable]):
    """
    Dynamically register the 13 canonical tools from manifest.
    Maps public tool names to internal implementation handlers.
    """
    manifest = load_manifest()
    
    for tool_spec in manifest.get("tools", []):
        name = tool_spec["name"]
        handler = handler_map.get(name)
        
        if not handler:
            print(f"[REGISTRY] WARNING: No handler found for {name}, skipping.")
            continue
            
        # Register tool with FastMCP
        # In a real build, we'd generate individual tool functions here
        mcp.add_tool(handler, name=name)
        print(f"[REGISTRY] Registered {name} (Stage: {tool_spec.get('stage')})")

def get_canonical_handlers() -> dict[str, Callable]:
    """
    Retrieve the internal implementation handlers for the 13 tools.
    """
    # Imports are internal to avoid circularity
    from usr.lib.arifOS.kernel.core import arifOS_kernel
    
    # Placeholder for other axes until ported
    dummy = lambda **kwargs: {"ok": False, "error": "Not yet implemented in FHS tree"}
    
    return {
        "arifos_init": dummy,
        "arifos_sense": dummy,
        "arifos_mind": dummy,
        "arifos_heart": dummy,
        "arifos_judge": dummy,
        "arifos_kernel": arifOS_kernel,
        "arifos_memory": dummy,
        "arifos_vault": dummy,
        "arifos_compute_physics": dummy,
        "arifos_compute_finance": dummy,
        "arifos_compute_civilization": dummy,
        "arifos_oracle_bio": dummy,
        "arifos_oracle_world": dummy,
    }

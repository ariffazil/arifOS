"""
Hardened Tool Dispatch Layer for arifOS MCP

This module provides the canonical tool dispatch map for all 10 arifOS tools.
Each tool is backed by a hardened wrapper that enforces ToM validation,
philosophy injection, and proper envelope sealing.
"""
from __future__ import annotations

from typing import Any, Callable, Awaitable

# Import the canonical tool wrappers from tools.py
# These provide ToM validation and envelope sealing
try:
    from arifosmcp.runtime.tools import (
        init_v2,
        sense_v2,
        mind_v2,
        route_v2,
        memory_v2,
        heart_v2,
        ops_v2,
        judge_v2,
        vault_v2,
        forge_v2,
    )
    
    # HARDENED_DISPATCH_MAP: Canonical tool name → Handler function
    # This map is used by the governance enforcer to route tool calls
    HARDENED_DISPATCH_MAP: dict[str, Callable[..., Awaitable[Any]]] = {
        # Public tools (4)
        "arifos.init": init_v2,
        "arifos.route": route_v2,
        "arifos.judge": judge_v2,
        "arifos.forge": forge_v2,
        
        # Internal tools (6)
        "arifos.sense": sense_v2,
        "arifos.mind": mind_v2,
        "arifos.memory": memory_v2,
        "arifos.heart": heart_v2,
        "arifos.ops": ops_v2,
        "arifos.vault": vault_v2,
        
        # Legacy aliases for backward compatibility
        "init_anchor": init_v2,
        "physics_reality": sense_v2,
        "agi_mind": mind_v2,
        "arifOS_kernel": route_v2,
        "engineering_memory": memory_v2,
        "asi_heart": heart_v2,
        "math_estimator": ops_v2,
        "apex_soul": judge_v2,
        "vault_ledger": vault_v2,
        "code_engine": forge_v2,
    }
    
except ImportError as e:
    # Fallback: empty map if tools module not available
    HARDENED_DISPATCH_MAP: dict[str, Callable[..., Awaitable[Any]]] = {}
    print(f"Warning: Could not load tool handlers: {e}")


def get_tool_handler(tool_name: str) -> Callable[..., Awaitable[Any]] | None:
    """Get the hardened handler for a canonical tool name.
    
    Args:
        tool_name: Canonical tool name (e.g., "arifos.init")
        
    Returns:
        Handler function or None if not found
    """
    return HARDENED_DISPATCH_MAP.get(tool_name)


def is_canonical_tool(tool_name: str) -> bool:
    """Check if a tool name is a canonical arifOS tool.
    
    Args:
        tool_name: Tool name to check
        
    Returns:
        True if the tool is in the hardened dispatch map
    """
    return tool_name in HARDENED_DISPATCH_MAP


def list_canonical_tools() -> list[str]:
    """Return list of all canonical tool names.
    
    Returns:
        List of canonical tool names (no legacy aliases)
    """
    return [
        "arifos.init",
        "arifos.sense",
        "arifos.mind",
        "arifos.route",
        "arifos.memory",
        "arifos.heart",
        "arifos.ops",
        "arifos.judge",
        "arifos.vault",
        "arifos.forge",
    ]

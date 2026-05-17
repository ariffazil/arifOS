"""Kernel shim — re-export from arifosmcp.core.kernel for backward compatibility."""

from arifosmcp.core.kernel import (
    loop_controller,
    metabolic_bridge,
    pattern_registry,
    pattern_selector,
    planner,
    role_registry,
    substrate_assert,
    tool_registry,
)

__all__ = [
    "loop_controller",
    "metabolic_bridge",
    "pattern_registry",
    "pattern_selector",
    "planner",
    "role_registry",
    "substrate_assert",
    "tool_registry",
]

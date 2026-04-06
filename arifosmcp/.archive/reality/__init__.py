"""
arifOS Reality Tools
====================

Reality grounding tools: physics_reality, math_estimator.
"""

from arifosmcp.tools.reality.physics_reality import get_instance as physics_reality_tool
from arifosmcp.tools.reality.math_estimator import get_instance as math_estimator_tool

__all__ = ["physics_reality_tool", "math_estimator_tool"]

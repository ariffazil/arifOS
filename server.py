"""
Canonical public entrypoint for arifOS deployments.

This is the only supported public FastMCP entrypoint for both:
1. VPS sovereign execution
2. Horizon gateway/proxy mode

Environment-specific behavior is delegated to ``arifos_mcp.server``.
No parallel ingress narrative should point at legacy horizon-specific files.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arifos_mcp.server import mcp
from config.environments import (
    get_environment,
    is_sovereign,
    is_public,
)

# Detect environment
env = get_environment()

# Log deployment mode
print(f"🏛️ arifOS starting in {env.mode.value.upper()} mode")
print(f"   Name: {env.name}")
print(f"   URL: {env.base_url}")
print(f"   Constitutional Floors: {', '.join(env.constitutional_floors)}")

if is_sovereign():
    print("🔥 SOVEREIGN KERNEL: All F1-F13 floors enforced")
elif is_public():
    print("☁️  HORIZON GATEWAY: Public entrypoint with governed proxy policy")

__all__ = ["mcp"]

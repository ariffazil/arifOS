"""
Stub: tools_hardened_dispatch.py

The hardened dispatch layer has been consolidated into arifosmcp/runtime/megaTools/.
This stub keeps existing imports working. HARDENED_DISPATCH_MAP is intentionally
empty — megaTools fall through to their tools_internal implementations.
"""
from typing import Any

HARDENED_DISPATCH_MAP: dict[str, Any] = {}

"""CanonicalProvider scaffold for future provider composition."""
from __future__ import annotations

from fastmcp.server.providers import LocalProvider

class CanonicalProvider(LocalProvider):
    """Inactive scaffold. Runtime authority remains server.py -> runtime/tools.py."""

    pass

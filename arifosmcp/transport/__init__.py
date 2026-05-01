"""
arifOS Transport Layer
═══════════════════════
Entrypoints for STDIO, Streamable HTTP, and A2A bridge.
"""
from __future__ import annotations

from .a2a import A2ABridge
from .http import create_http_app
from .stdio import run_stdio

__all__ = ["run_stdio", "create_http_app", "A2ABridge"]

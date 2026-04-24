"""
arifOS Transport Layer
═══════════════════════
Entrypoints for STDIO, Streamable HTTP, and A2A bridge.
"""
from __future__ import annotations

from .stdio import run_stdio
from .http import create_http_app
from .a2a import A2ABridge

__all__ = ["run_stdio", "create_http_app", "A2ABridge"]

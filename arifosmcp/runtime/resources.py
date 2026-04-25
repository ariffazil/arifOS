"""Compatibility shim for the package resource authority."""
from __future__ import annotations

from arifosmcp.resources import CANONICAL_RESOURCES, register_resources

__all__ = ["CANONICAL_RESOURCES", "register_resources"]

def apex_tools_markdown_table() -> str:
    '''Stub for the apex tools markdown table.'''
    return ''

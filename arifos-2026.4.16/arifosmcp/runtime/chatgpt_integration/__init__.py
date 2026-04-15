"""
arifOS ChatGPT MCP Integration — ΔΩΨ | DITEMPA BUKAN DIBERI

This module provides ChatGPT-compatible tools for OpenAI's MCP integration:
- Deep Research: search + fetch tools
- Chat Mode: All 11 mega-tools with readOnlyHint annotations

Official Docs:
- https://developers.openai.com/api/docs/mcp
- https://gofastmcp.com/integrations/chatgpt
"""

from .apps_sdk_tools import (
    VAULT_WIDGET_URI,
    register_chatgpt_app_tools,
    vault_seal_widget_html,
)
from .chatgpt_tools import chatgpt_tools, fetch, register_chatgpt_tools, search

__all__ = [
    "search",
    "fetch",
    "chatgpt_tools",
    "register_chatgpt_tools",
    "register_chatgpt_app_tools",
    "VAULT_WIDGET_URI",
    "vault_seal_widget_html",
]

"""
arifos.adapters — Framework-specific adapters for popular agent SDKs.

The core `arifos` SDK is framework-agnostic. Adapters wrap the SDK
with framework-specific glue (tool schemas, agent hooks, etc.).

Available adapters:
    openai  — OpenAI Agents SDK
"""

from arifos.adapters import openai

__all__ = ["openai"]

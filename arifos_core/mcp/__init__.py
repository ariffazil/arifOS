"""
arifOS MCP Package - Model Context Protocol server for IDE integration.

This module provides MCP tools for integrating arifOS governance
with IDEs like VS Code, Cursor, and others.

Unified Server (v47.0.0):
- 17 tools consolidated from 34 (across 3 old servers)
- 5 constitutional pipeline + 2 search + 3 vault999 + 4 FAG + 1 validation + 2 system
- Dual semantic search (agi_search, asi_search)
- All 12 constitutional floors enforced

Quantum Architecture (v47+):
- Parallel AGI+ASI execution (orthogonal particles)
- 47% faster than sequential pipeline
- AAA-level separation: LLM generation ⊥ Quantum validation

Usage:
    # MCP Tools
    from arifos_core.mcp import list_tools, arifos_judge, arifos_recall, arifos_audit

    # Quantum Executor (AAA-level)
    from arifos_core.mcp import generate_and_validate_async, validate_text_sync

    # Generate + Validate (async)
    draft, state = await generate_and_validate_async(
        query="What is 2+2?",
        llm_model="gpt-4o-mini"
    )
    if state.final_verdict == "SEAL":
        print(draft)

    # Validate existing text (sync)
    state = validate_text_sync(
        query="What is 2+2?",
        draft_response="4"
    )

Version: v47.0.0
"""

from .tools.audit import arifos_audit
from .tools.judge import arifos_judge
from .tools.recall import arifos_recall
from .unified_server import TOOLS, list_tools, mcp_server, run_tool

# AAA-level quantum helpers (v47+)
from .helpers import (
    generate_and_validate_async,
    generate_and_validate_sync,
    validate_text_async,
    validate_text_sync,
    QuantumPipeline,
)

# Quantum executor (low-level)
from .orthogonal_executor import OrthogonalExecutor, QuantumState

__all__ = [
    # MCP Server
    "list_tools",
    "run_tool",
    "TOOLS",
    "mcp_server",
    "arifos_judge",
    "arifos_recall",
    "arifos_audit",

    # AAA-level helpers (recommended)
    "generate_and_validate_async",
    "generate_and_validate_sync",
    "validate_text_async",
    "validate_text_sync",
    "QuantumPipeline",

    # Low-level quantum (advanced usage)
    "OrthogonalExecutor",
    "QuantumState",
]
